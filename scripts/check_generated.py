import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_contracts import (
    CLIENT_OUTPUT,
    OPENAPI_OUTPUT,
    generate_contracts,
)


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        generated_openapi = temporary / "openapi.json"
        generated_client = temporary / "client.ts"
        generate_contracts(generated_openapi, generated_client)
        compare(OPENAPI_OUTPUT, generated_openapi)
        compare(CLIENT_OUTPUT, generated_client)


def compare(expected: Path, generated: Path) -> None:
    if not expected.is_file():
        raise SystemExit(f"Missing generated file: {expected.relative_to(PROJECT_ROOT)}")
    if expected.read_bytes() != generated.read_bytes():
        raise SystemExit(f"Generated drift detected: {expected.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
