#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def schema_to_py(schema: dict) -> str:
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    if "anyOf" in schema:
        return " | ".join(schema_to_py(item) for item in schema["anyOf"])
    if "oneOf" in schema:
        return " | ".join(schema_to_py(item) for item in schema["oneOf"])

    schema_type = schema.get("type")
    if schema_type == "string":
        return "str"
    if schema_type in {"integer", "number"}:
        return "int | float" if schema_type == "number" else "int"
    if schema_type == "boolean":
        return "bool"
    if schema_type == "null":
        return "None"
    if schema_type == "array":
        return f"list[{schema_to_py(schema.get('items', {}))}]"
    if schema_type == "object" or "properties" in schema:
        additional = schema.get("additionalProperties")
        if additional is True:
            return "dict[str, object]"
        if isinstance(additional, dict):
            return f"dict[str, {schema_to_py(additional)}]"
        return "dict[str, object]"
    return "object"


def render_typed_dict(name: str, schema: dict) -> str:
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    lines = [f"class {name}(TypedDict, total=False):"]
    if not properties:
        lines.append("    pass")
        return "\n".join(lines)
    for prop_name, prop_schema in properties.items():
        annotation = schema_to_py(prop_schema)
        if prop_name in required:
            lines.append(f"    {prop_name}: {annotation}")
        else:
            lines.append(f"    {prop_name}: NotRequired[{annotation}]")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Python TypedDicts from OpenAPI schemas")
    parser.add_argument(
        "--openapi",
        default="sdk/openapi/agent2allow.openapi.json",
        help="OpenAPI schema path",
    )
    parser.add_argument(
        "--out",
        default="sdk/python/agent2allow_sdk/openapi_types.py",
        help="output module path",
    )
    args = parser.parse_args()

    openapi_path = Path(args.openapi)
    output_path = Path(args.out)
    spec = json.loads(openapi_path.read_text(encoding="utf-8"))
    schemas: dict = spec.get("components", {}).get("schemas", {})

    parts = [
        "# Generated from OpenAPI. Do not edit manually.",
        "from __future__ import annotations",
        "",
        "from typing import NotRequired, TypedDict",
        "",
    ]
    for name, schema in schemas.items():
        parts.append(render_typed_dict(name, schema))
        parts.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
