import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPANION_SOURCE = PROJECT_ROOT / "companion" / "src"
sys.path.insert(0, str(COMPANION_SOURCE))

from researcher_companion.api.app import create_app
from researcher_companion.settings import (
    CompanionSettings,
    LoopbackSettings,
    RuntimePaths,
    SessionSettings,
)

OPENAPI_OUTPUT = PROJECT_ROOT / "contracts" / "openapi.json"
CLIENT_OUTPUT = PROJECT_ROOT / "taskpane" / "src" / "generated" / "client.ts"
CLIENT_TEMPLATE = PROJECT_ROOT / "scripts" / "templates" / "typescript-client.template.ts"


def main() -> None:
    generate_contracts(OPENAPI_OUTPUT, CLIENT_OUTPUT)


def generate_contracts(openapi_output: Path, client_output: Path) -> None:
    contract = build_openapi_contract()
    write_text(openapi_output, serialize_contract(contract))
    write_text(client_output, render_typescript_client(contract))


def build_openapi_contract() -> dict[str, Any]:
    application = create_app(generation_settings(), b"phase1-generation-secret-material")
    return application.openapi()


def generation_settings() -> CompanionSettings:
    temporary = PROJECT_ROOT / ".generated-contract-runtime"
    paths = RuntimePaths(
        database=temporary / "state.sqlite3",
        content_store=temporary / "content",
        taskpane_index=PROJECT_ROOT / "taskpane" / "index.html",
        taskpane_assets=PROJECT_ROOT / "taskpane" / "src",
        certificate=temporary / "server-cert.pem",
        private_key=temporary / "server-key.pem",
        migrations=PROJECT_ROOT / "companion" / "migrations",
    )
    return CompanionSettings(LoopbackSettings(), SessionSettings(), paths)


def serialize_contract(contract: dict[str, Any]) -> str:
    return json.dumps(contract, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def render_typescript_client(contract: dict[str, Any]) -> str:
    template = CLIENT_TEMPLATE.read_text(encoding="utf-8")
    operations = operation_paths(contract)
    replacements = {
        "__TYPE_DEFINITIONS__": render_type_definitions(contract),
        "__BOOTSTRAP_PATH__": operations["bootstrapLocalSession"],
        "__HEALTH_PATH__": operations["getHealth"],
    }
    for marker, replacement in replacements.items():
        template = template.replace(marker, replacement)
    return template


def operation_paths(contract: dict[str, Any]) -> dict[str, str]:
    operations: dict[str, str] = {}
    for path, path_item in contract["paths"].items():
        for operation in path_item.values():
            if isinstance(operation, dict) and "operationId" in operation:
                operations[operation["operationId"]] = path
    required = {"bootstrapLocalSession", "getHealth"}
    if required - operations.keys():
        raise RuntimeError("OpenAPI contract is missing a required Phase 1 operation")
    return operations


def render_type_definitions(contract: dict[str, Any]) -> str:
    schemas = contract["components"]["schemas"]
    definitions = [render_interface(name, schemas[name]) for name in sorted(schemas)]
    return "\n\n".join(definitions)


def render_interface(name: str, schema: dict[str, Any]) -> str:
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    lines = [f"export interface {name} {{"]
    for property_name in sorted(properties):
        optional = "" if property_name in required else "?"
        lines.append(f"  {property_name}{optional}: {typescript_type(properties[property_name])};")
    lines.append("}")
    return "\n".join(lines)


def typescript_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        return schema["$ref"].rsplit("/", maxsplit=1)[-1]
    if "const" in schema:
        return json.dumps(schema["const"])
    if "enum" in schema:
        return " | ".join(json.dumps(value) for value in schema["enum"])
    if schema.get("type") == "array":
        return f"Array<{typescript_type(schema['items'])}>"
    schema_type = schema.get("type")
    if not isinstance(schema_type, str):
        return "unknown"
    types = {"boolean": "boolean", "integer": "number", "number": "number", "string": "string"}
    return types.get(schema_type, "unknown")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
