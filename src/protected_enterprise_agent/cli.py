from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model_backends import OllamaModel
from .pipeline import deterministic_model
from .qualification import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Protected Enterprise Agent canonical qualification demo.")
    parser.add_argument("--require-vendor", action="store_true", help="Require live local Protegrity Data Discovery and Semantic Guardrails services.")
    parser.add_argument("--model-backend", choices=("deterministic", "ollama"), default="deterministic", help="Model implementation; deterministic remains the qualification default.")
    parser.add_argument("--ollama-model", default="gemma4:12b", help="Local Ollama model name when --model-backend=ollama.")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434", help="Local Ollama API base URL.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    model = OllamaModel(model=args.ollama_model, base_url=args.ollama_url) if args.model_backend == "ollama" else deterministic_model
    result = run(args.root.resolve(), args.require_vendor, model)
    print(json.dumps(result, indent=2, sort_keys=True))
    required = ("security", "utility", "adversarial", "evidence", "public_estate")
    return 0 if all(result[name] for name in required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
