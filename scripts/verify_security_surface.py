import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = {
    "private key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "GitHub token": re.compile(r"gh[opsu]_[A-Za-z0-9_]{20,}"),
    "OpenAI-style token": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
}
FORBIDDEN_HTTP_CLIENTS = (
    "import requests",
    "import httpx",
    "import aiohttp",
    "urllib.request",
    "Invoke-WebRequest",
    "Start-BitsTransfer",
    "wget ",
)


def main() -> None:
    verify_no_committed_secret_material()
    verify_browser_storage_boundary()
    verify_generated_bundle_boundary()
    verify_no_installer_or_companion_http_client()
    print("security-surface-verification: PASS")


def verify_no_committed_secret_material() -> None:
    for path in source_controlled_files():
        content = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            require(pattern.search(content) is None, f"Potential {label} in {relative(path)}")


def verify_browser_storage_boundary() -> None:
    source = read_tree(PROJECT_ROOT / "taskpane" / "src")
    require("localStorage" not in source, "Task pane must not use localStorage")
    require("sessionStorage" not in source, "Task pane must not use sessionStorage")


def verify_generated_bundle_boundary() -> None:
    bundle = read_generated_bundle()
    forbidden = (
        "WordResearcher.Phase1",
        "installation-secret",
        private_key_marker(),
        "localStorage",
        "sessionStorage",
    )
    for marker in forbidden:
        require(marker not in bundle, f"Generated bundle exposes protected marker: {marker}")
    require_secret_not_in_url(bundle)


def verify_no_installer_or_companion_http_client() -> None:
    source = read_tree(PROJECT_ROOT / "companion" / "src") + read_tree(
        PROJECT_ROOT / "installers"
    )
    for client in FORBIDDEN_HTTP_CLIENTS:
        require(client not in source, f"Unexpected external HTTP client: {client.strip()}")
    verify_local_curl_only()


def verify_local_curl_only() -> None:
    installer = read_tree(PROJECT_ROOT / "installers")
    curl_lines = [line.strip() for line in installer.splitlines() if "curl" in line]
    for line in curl_lines:
        require("/usr/bin/curl" in line, "Installer curl must use the system client")
    require("STABLE_ORIGIN/taskpane" in installer, "Installer curl target must be exact loopback")


def source_controlled_files() -> list[Path]:
    roots = ("companion", "contracts", "installers", "manifest", "phase1", "scripts", "taskpane")
    return [
        path
        for root in roots
        for path in (PROJECT_ROOT / root).rglob("*")
        if path.is_file() and not ignored(path)
    ]


def read_generated_bundle() -> str:
    build = PROJECT_ROOT / "taskpane" / "dist"
    require(build.is_dir(), "Generated task-pane bundle is missing")
    return "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in build.rglob("*")
        if path.is_file()
    )


def require_secret_not_in_url(content: str) -> None:
    secret_query = re.compile(r"https?://[^\s\"']+[?&](?:secret|token|key)=", re.IGNORECASE)
    require(secret_query.search(content) is None, "Generated bundle places secret material in a URL")


def private_key_marker() -> str:
    return "BEGIN" + " PRIVATE KEY"


def read_tree(root: Path) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in root.rglob("*")
        if path.is_file() and not ignored(path)
    )


def ignored(path: Path) -> bool:
    return any(part in {"node_modules", "dist", "__pycache__", "runtime"} for part in path.parts)


def relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    main()
