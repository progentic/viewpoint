import html
from pathlib import Path

from fastapi import Response

from researcher_companion.session import BOOTSTRAP_COOKIE, BootstrapMaterial

BOOTSTRAP_PLACEHOLDER = "__BOOTSTRAP_CSRF__"


class TaskPaneRenderer:
    def __init__(self, index_path: Path) -> None:
        self._index_path = index_path

    def render(self, bootstrap: BootstrapMaterial) -> Response:
        template = self._load_template()
        csrf_token = html.escape(bootstrap.csrf_token, quote=True)
        document = template.replace(BOOTSTRAP_PLACEHOLDER, csrf_token)
        response = Response(document, media_type="text/html")
        self._set_bootstrap_cookie(response, bootstrap)
        self._set_security_headers(response)
        return response

    def _load_template(self) -> str:
        if not self._index_path.is_file():
            raise RuntimeError("Task pane assets are missing; run the locked frontend build")
        return self._index_path.read_text(encoding="utf-8")

    def _set_bootstrap_cookie(self, response: Response, bootstrap: BootstrapMaterial) -> None:
        response.set_cookie(
            BOOTSTRAP_COOKIE,
            bootstrap.cookie,
            secure=True,
            httponly=True,
            samesite="strict",
            path="/api/v1/session/bootstrap",
            expires=bootstrap.expires_at,
        )

    def _set_security_headers(self, response: Response) -> None:
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' https://appsforoffice.microsoft.com; "
            "style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
