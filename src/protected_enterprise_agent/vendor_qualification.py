from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


PINNED_VENDOR_SHA = "15c113c10ba71b272e0e7515b04e2f81b8b6afe7"
MINIMUM_COMPOSE_VERSION = (2, 30, 0)


def _command(*args: str, cwd: Path | None = None, timeout: int = 120) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=timeout,
    )
    if completed.returncode:
        raise RuntimeError(f"command failed ({' '.join(args[:3])}): {completed.stdout.strip()}")
    return completed.stdout.strip()


def _version_tuple(value: str) -> tuple[int, int, int]:
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", value)
    if not match:
        raise RuntimeError(f"could not parse version: {value}")
    return tuple(int(part or 0) for part in match.groups())


def _compose_services(compose_file: Path) -> list[dict[str, object]]:
    raw = _command("docker", "compose", "-f", str(compose_file), "ps", "--format", "json")
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        rows = parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return [row for row in rows if isinstance(row, dict)]


def _resolved_compose(compose_file: Path) -> dict[str, Any]:
    parsed = json.loads(_command("docker", "compose", "-f", str(compose_file), "config", "--format", "json"))
    if not isinstance(parsed, dict):
        raise RuntimeError(f"resolved compose config is not an object: {compose_file}")
    services = parsed.get("services", {})
    return {
        "compose_file": str(compose_file),
        "project_name": parsed.get("name"),
        "networks": sorted((parsed.get("networks") or {}).keys()),
        "services": {
            name: {
                "image": value.get("image"),
                "ports": value.get("ports", []),
                "networks": sorted((value.get("networks") or {}).keys()) if isinstance(value.get("networks"), dict) else value.get("networks", []),
            }
            for name, value in services.items()
            if isinstance(value, dict)
        },
    }


def _container_receipts(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    receipts: list[dict[str, object]] = []
    for row in rows:
        container_id = str(row.get("ID") or row.get("Id") or row.get("Name") or "")
        if not container_id:
            continue
        inspected = json.loads(_command("docker", "inspect", container_id))[0]
        image_id = str(inspected.get("Image", ""))
        image_details = json.loads(_command("docker", "image", "inspect", image_id))[0] if image_id else {}
        receipts.append({
            "container_id": str(inspected.get("Id", "")),
            "name": str(inspected.get("Name", "")).lstrip("/"),
            "state": (inspected.get("State") or {}).get("Status"),
            "image_reference": (inspected.get("Config") or {}).get("Image"),
            "image_id": image_id,
            "repo_digests": image_details.get("RepoDigests") or [],
            "published_ports": row.get("Publishers") or row.get("Ports") or [],
        })
    return receipts


def observe_runtime(vendor_root: Path | None = None) -> dict[str, Any]:
    root_value = vendor_root or (Path(os.environ["PROTEGRITY_DEV_EDITION_ROOT"]) if os.environ.get("PROTEGRITY_DEV_EDITION_ROOT") else None)
    if root_value is None:
        raise RuntimeError("PROTEGRITY_DEV_EDITION_ROOT is required for vendor qualification")
    root = root_value.resolve()
    data_compose = root / "data-discovery" / "docker-compose.yml"
    semantic_compose = root / "semantic-guardrail" / "docker-compose.yml"
    if not data_compose.is_file() or not semantic_compose.is_file():
        raise RuntimeError("pinned vendor checkout is missing required compose files")

    vendor_sha = _command("git", "rev-parse", "HEAD", cwd=root)
    compose_text = _command("docker", "compose", "version", "--short")
    compose_version = _version_tuple(compose_text)
    server_os = _command("docker", "info", "--format", "{{.OSType}}")
    server_version = _command("docker", "version", "--format", "{{.Server.Version}}")
    wsl_version = _command("wsl.exe", "--version")
    _command("docker", "run", "--rm", "hello-world", timeout=180)

    data_services = _compose_services(data_compose)
    semantic_services = _compose_services(semantic_compose)
    all_services = data_services + semantic_services
    running = [row for row in all_services if str(row.get("State", "")).lower() == "running"]
    observed = {
        "pinned_vendor_runtime_observed": (
            vendor_sha == PINNED_VENDOR_SHA
            and compose_version >= MINIMUM_COMPOSE_VERSION
            and server_os.lower() == "linux"
            and len(data_services) >= 3
            and len(semantic_services) >= 1
            and len(running) == len(all_services)
        ),
        "vendor_sha": vendor_sha,
        "expected_vendor_sha": PINNED_VENDOR_SHA,
        "compose_version": compose_text,
        "minimum_compose_version": ".".join(map(str, MINIMUM_COMPOSE_VERSION)),
        "docker_server_version": server_version,
        "docker_server_os": server_os,
        "trivial_container_pass": True,
        "data_discovery_service_count": len(data_services),
        "semantic_guardrail_service_count": len(semantic_services),
        "running_service_count": len(running),
        "wsl_version": [line.strip() for line in wsl_version.replace("\x00", "").splitlines() if line.strip()],
        "resolved_compose": {
            "data_discovery": _resolved_compose(data_compose),
            "semantic_guardrails": _resolved_compose(semantic_compose),
        },
        "containers": _container_receipts(all_services),
    }
    return observed


def evaluate_vendor_qualification(
    runtime: dict[str, Any],
    events: list[dict[str, Any]],
    *,
    security_pass: bool,
    utility_pass: bool,
    adversarial_pass: bool,
    fallback_used: bool,
) -> dict[str, Any]:
    discovery_events = [
        event for event in events
        if event.get("pipeline_stage") == "ingestion"
        and event.get("provider_component") == "Protegrity Data Discovery"
        and event.get("details", {}).get("vendor_observed") is True
        and int(event.get("details", {}).get("detection_count", 0)) > 0
    ]
    semantic_events = [
        event for event in events
        if event.get("provider_component") == "Protegrity Semantic Guardrails"
        and event.get("pipeline_stage") in {"input_guardrail", "inference"}
        and event.get("details", {}).get("vendor_observed") is True
        and "risk_score" in event.get("details", {})
    ]
    vendor_blocks = [event for event in semantic_events if event.get("decision") == "BLOCK"]
    conditions = {
        "pinned_vendor_runtime_observed": runtime.get("pinned_vendor_runtime_observed") is True,
        "data_discovery_real_response_observed": bool(discovery_events),
        "semantic_guardrail_real_response_observed": bool(semantic_events),
        "application_real_vendor_path_executed": bool(discovery_events and semantic_events),
        "fallback_not_used": not fallback_used,
        "causal_effect_observed": bool(vendor_blocks),
        "leak_suite_pass": security_pass,
        "utility_suite_pass": utility_pass,
        "adversarial_suite_pass": adversarial_pass,
    }
    failed = [name for name, passed in conditions.items() if not passed]
    return {
        "vendor_available": bool(discovery_events or semantic_events),
        "vendor_qualified": not failed,
        "conditions": conditions,
        "failed_conditions": failed,
        "runtime": runtime,
        "observed_event_counts": {
            "data_discovery": len(discovery_events),
            "semantic_guardrails": len(semantic_events),
            "semantic_guardrail_blocks": len(vendor_blocks),
        },
    }
