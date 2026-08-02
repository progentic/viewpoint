import argparse
from pathlib import Path

from researcher_companion.platform.credentials import (
    InstallationSecretService,
    current_credential_store,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def main() -> None:
    arguments = parse_arguments()
    secret = InstallationSecretService(current_credential_store()).load()
    exposed = [path for path in files_to_scan(arguments.logs) if contains(path, secret)]
    if exposed:
        names = "\n".join(str(path) for path in exposed)
        raise SystemExit(f"Installation secret was exposed in:\n{names}")
    print("installed-secret-exposure-scan: PASS")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan Phase 1 browser assets and logs")
    parser.add_argument("--logs", type=Path, required=True)
    return parser.parse_args()


def files_to_scan(logs: Path) -> list[Path]:
    roots = [
        PROJECT_ROOT / "manifest",
        PROJECT_ROOT / "taskpane" / "src",
        PROJECT_ROOT / "taskpane" / "dist",
        PROJECT_ROOT / "companion" / "src",
        logs,
    ]
    return [path for root in roots for path in root.rglob("*") if path.is_file()]


def contains(path: Path, secret: bytes) -> bool:
    return secret in path.read_bytes()


if __name__ == "__main__":
    main()
