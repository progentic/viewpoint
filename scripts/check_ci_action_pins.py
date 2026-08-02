import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIRECTORY = PROJECT_ROOT / ".github" / "workflows"
ACTION_REFERENCE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
FULL_COMMIT = re.compile(r"^[^@]+@[0-9a-f]{40}$")


def main() -> None:
    failures = collect_unpinned_actions()
    if failures:
        raise SystemExit("Unpinned CI actions:\n" + "\n".join(failures))


def collect_unpinned_actions() -> list[str]:
    failures = []
    for workflow in sorted(WORKFLOW_DIRECTORY.glob("*.y*ml")):
        failures.extend(unpinned_references(workflow))
    return failures


def unpinned_references(workflow: Path) -> list[str]:
    references = ACTION_REFERENCE.findall(workflow.read_text(encoding="utf-8"))
    return [
        f"{workflow.relative_to(PROJECT_ROOT)}: {reference}"
        for reference in references
        if not reference.startswith("./") and FULL_COMMIT.fullmatch(reference) is None
    ]


if __name__ == "__main__":
    main()
