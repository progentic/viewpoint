import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HASH_TARGETS = (
    "contracts/openapi.json",
    "taskpane/src/generated/client.ts",
    "package-lock.json",
    "companion/requirements.lock",
    "manifest/word-researcher.xml",
    "installers/macos/install.sh",
    "installers/macos/repair.sh",
    "installers/macos/uninstall.sh",
    "installers/macos/word_manifest.applescript",
    "installers/windows/common.ps1",
    "installers/windows/platform.ps1",
    "installers/windows/policy.ps1",
    "installers/windows/install.ps1",
    "installers/windows/repair.ps1",
    "installers/windows/tests/phase1.tests.ps1",
    "installers/windows/uninstall.ps1",
)


def main() -> None:
    print(json.dumps(compute_hashes(), indent=2, sort_keys=True))


def compute_hashes() -> dict[str, str]:
    return {target: sha256(PROJECT_ROOT / target) for target in HASH_TARGETS}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    main()
