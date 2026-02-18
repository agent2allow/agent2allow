#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Agent2Allow OpenAPI schema to a file")
    parser.add_argument(
        "--out",
        default="sdk/openapi/agent2allow.openapi.json",
        help="output file path",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    gateway_root = repo_root / "gateway"
    sys.path.insert(0, str(gateway_root))

    from src.main import app  # pylint: disable=import-outside-toplevel

    target = repo_root / args.out
    target.parent.mkdir(parents=True, exist_ok=True)
    schema = app.openapi()
    target.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote OpenAPI schema to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
