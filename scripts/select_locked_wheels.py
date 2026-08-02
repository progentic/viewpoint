import argparse
import json
from pathlib import Path

from packaging.requirements import Requirement
from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "companion" / "requirements.in"


def main() -> None:
    arguments = parse_arguments()
    supported_tags = list(sys_tags())
    for line in INPUT.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            selection = select_requirement(line, arguments.metadata_directory, supported_tags)
            if selection is not None:
                print("\t".join(selection))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select locked wheels for the active Python")
    parser.add_argument("--metadata-directory", type=Path, required=True)
    return parser.parse_args()


def select_requirement(
    line: str,
    metadata_directory: Path,
    supported_tags: list,
) -> tuple[str, str, str] | None:
    requirement = Requirement(line)
    if requirement.marker is not None and not requirement.marker.evaluate():
        return None
    metadata_path = metadata_directory / f"{requirement.name}.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    artifact = select_compatible_wheel(metadata["urls"], supported_tags)
    return requirement.name, artifact["url"], artifact["filename"]


def select_compatible_wheel(artifacts: list[dict], supported_tags: list) -> dict:
    priority = {tag: index for index, tag in enumerate(supported_tags)}
    candidates = []
    for artifact in artifacts:
        if artifact["packagetype"] == "bdist_wheel" and not artifact.get("yanked", False):
            candidates.append((wheel_priority(artifact["filename"], priority), artifact))
    compatible = [candidate for candidate in candidates if candidate[0] is not None]
    if not compatible:
        raise RuntimeError("Locked release has no wheel compatible with the active Python")
    return min(compatible, key=lambda candidate: candidate[0])[1]


def wheel_priority(filename: str, priority: dict) -> int | None:
    _name, _version, _build, tags = parse_wheel_filename(filename)
    matches = [priority[tag] for tag in tags if tag in priority]
    return min(matches) if matches else None


if __name__ == "__main__":
    main()
