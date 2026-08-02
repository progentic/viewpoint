import argparse
import plistlib
import sys
from pathlib import Path

from researcher_companion.platform.credentials import (
    InstallationSecretService,
    current_credential_store,
)
from researcher_companion.platform.tls import PerInstallTlsProvisioner, TlsMaterial
from researcher_companion.settings import STABLE_HOSTNAME


def main() -> None:
    arguments = parse_arguments()
    dispatch(arguments)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Provision Phase 1 local installation material")
    commands = parser.add_subparsers(dest="command", required=True)
    provision = commands.add_parser("provision")
    provision.add_argument("--tls-directory", type=Path, required=True)
    commands.add_parser("check-secret")
    commands.add_parser("delete-secret")
    launch_agent = commands.add_parser("render-launch-agent")
    launch_agent.add_argument("--output", type=Path, required=True)
    launch_agent.add_argument("--python", type=Path, required=True)
    launch_agent.add_argument("--project-root", type=Path, required=True)
    launch_agent.add_argument("--app-data", type=Path, required=True)
    return parser.parse_args()


def dispatch(arguments: argparse.Namespace) -> None:
    if arguments.command == "provision":
        provision_installation(arguments.tls_directory)
    elif arguments.command == "check-secret":
        InstallationSecretService(current_credential_store()).load()
    elif arguments.command == "delete-secret":
        InstallationSecretService(current_credential_store()).delete()
    elif arguments.command == "render-launch-agent":
        render_launch_agent(arguments)


def provision_installation(tls_directory: Path) -> None:
    InstallationSecretService(current_credential_store()).ensure()
    material = expected_tls_material(tls_directory)
    if all_material_exists(material):
        return
    if any_material_exists(material):
        raise RuntimeError("TLS material is incomplete; run repair before changing trust state")
    PerInstallTlsProvisioner(tls_directory, STABLE_HOSTNAME).provision()


def expected_tls_material(directory: Path) -> TlsMaterial:
    return TlsMaterial(
        root_certificate=directory / "root-ca.pem",
        root_private_key=directory / "root-ca-key.pem",
        server_certificate=directory / "server-cert.pem",
        server_private_key=directory / "server-key.pem",
        metadata=directory / "tls-metadata.json",
    )


def all_material_exists(material: TlsMaterial) -> bool:
    return all(path.is_file() for path in material.__dict__.values())


def any_material_exists(material: TlsMaterial) -> bool:
    return any(path.exists() for path in material.__dict__.values())


def render_launch_agent(arguments: argparse.Namespace) -> None:
    payload = launch_agent_payload(arguments.python, arguments.project_root, arguments.app_data)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.output.open("wb") as stream:
        plistlib.dump(payload, stream, sort_keys=True)


def launch_agent_payload(python: Path, project_root: Path, app_data: Path) -> dict:
    return {
        "EnvironmentVariables": {
            "PYTHONPATH": str(project_root / "companion" / "src"),
            "WORD_RESEARCHER_DATA": str(app_data),
        },
        "KeepAlive": True,
        "Label": "local.word-researcher.companion",
        "ProgramArguments": [str(python), "-m", "researcher_companion.main"],
        "RunAtLoad": True,
        "StandardErrorPath": str(app_data / "logs" / "companion.stderr.log"),
        "StandardOutPath": str(app_data / "logs" / "companion.stdout.log"),
        "WorkingDirectory": str(project_root),
    }


if __name__ == "__main__":
    sys.exit(main())
