import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASKPANE_SOURCE = PROJECT_ROOT / "taskpane" / "src"
PRODUCTION_OFFICE_JS = "https://appsforoffice.microsoft.com/lib/1/hosted/office.js"
REQUIRED_SCRIPTS = {
    "build",
    "lint",
    "pyright",
    "test",
    "typecheck",
    "validate:manifest",
    "verify:architecture",
    "verify:generated",
    "verify:security",
}


def main() -> None:
    checks = (
        verify_package_contract,
        verify_office_contract,
        verify_generated_client_boundary,
        verify_workflow_contract,
        verify_python_dependencies,
    )
    for check in checks:
        check()
    print("architecture-verification: PASS")


def verify_package_contract() -> None:
    package = load_json(PROJECT_ROOT / "package.json")
    missing = REQUIRED_SCRIPTS - package["scripts"].keys()
    require(not missing, f"Missing required npm scripts: {sorted(missing)}")
    require("--if-present" not in json.dumps(package["scripts"]), "Silent npm fallback is forbidden")
    for section in ("dependencies", "devDependencies"):
        for name, version in package.get(section, {}).items():
            require(is_exact_version(version), f"Mutable npm dependency: {name}@{version}")


def verify_office_contract() -> None:
    html = (PROJECT_ROOT / "taskpane" / "index.html").read_text(encoding="utf-8")
    require(PRODUCTION_OFFICE_JS in html_head(html), "Production Office.js must load in head")
    require("office.js" not in browser_bundle(), "Office.js must not be bundled")
    repository_text = production_text()
    require("appsforoffice.microsoft.com/lib/beta" not in repository_text, "Preview CDN is forbidden")
    require("@types/office-js-preview" not in repository_text, "Preview Office types are forbidden")
    require('"WordApi", "1.3"' in repository_text, "WordApi 1.3 runtime gate is missing")


def verify_generated_client_boundary() -> None:
    handwritten = "\n".join(
        path.read_text(encoding="utf-8")
        for path in TASKPANE_SOURCE.rglob("*.ts*")
        if "generated" not in path.parts
    )
    require("/api/v1/" not in handwritten, "Handwritten task-pane API route detected")
    require('from "./generated/client"' in handwritten, "Task pane does not use generated client")


def verify_workflow_contract() -> None:
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "phase1.yml").read_text(
        encoding="utf-8"
    )
    require("permissions:\n  contents: read" in workflow, "Workflow permissions are too broad")
    for action in re.findall(r"uses:\s*([^\s#]+)", workflow):
        require(re.fullmatch(r"[^@]+@[0-9a-f]{40}", action) is not None, f"Unpinned action: {action}")


def verify_python_dependencies() -> None:
    requirements = (PROJECT_ROOT / "companion" / "requirements.in").read_text(encoding="utf-8")
    for line in requirements.splitlines():
        if line and not line.startswith("#"):
            require("==" in line, f"Mutable Python dependency: {line}")


def html_head(document: str) -> str:
    match = re.search(r"<head>(.*?)</head>", document, re.DOTALL)
    return match.group(1) if match else ""


def browser_bundle() -> str:
    build = PROJECT_ROOT / "taskpane" / "dist" / "assets"
    if not build.is_dir():
        return ""
    return "\n".join(path.read_text(encoding="utf-8") for path in build.glob("*.js"))


def production_text() -> str:
    targets = [PROJECT_ROOT / "taskpane", PROJECT_ROOT / "manifest", PROJECT_ROOT / "package.json"]
    files = [path for target in targets for path in target_files(target)]
    return "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in files
        if "dist" not in path.parts and "node_modules" not in path.parts
    )


def target_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return [path for path in target.rglob("*") if path.is_file()]


def is_exact_version(version: str) -> bool:
    return re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version) is not None


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    main()
