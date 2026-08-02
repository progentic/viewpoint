#!/bin/zsh
set -euo pipefail

SCRIPT_DIRECTORY=${0:A:h}
PROJECT_ROOT=${SCRIPT_DIRECTORY:h:h}
PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE:-"$PROJECT_ROOT/.venv/bin/python"}
APP_DATA=${WORD_RESEARCHER_DATA:-"$HOME/Library/Application Support/WordResearcher"}
LAUNCH_AGENT="$HOME/Library/LaunchAgents/local.word-researcher.companion.plist"
MANIFEST_DIRECTORY="$HOME/Library/Containers/com.microsoft.Word/Data/Documents/wef"
MANIFEST_TARGET="$MANIFEST_DIRECTORY/word-researcher.xml"
WORD_DOCUMENTS="$HOME/Library/Containers/com.microsoft.Word/Data/Documents"
LOGIN_KEYCHAIN="$HOME/Library/Keychains/login.keychain-db"

require_prebuilt_runtime() {
  [[ -x "$PYTHON_EXECUTABLE" ]] || { print -u2 "Missing locked Python environment"; return 1; }
  [[ -f "$PROJECT_ROOT/taskpane/dist/index.html" ]] || { print -u2 "Missing task-pane build"; return 1; }
}

provision_private_material() {
  mkdir -p "$APP_DATA/logs"
  PYTHONPATH="$PROJECT_ROOT/companion/src" "$PYTHON_EXECUTABLE" \
    -m researcher_companion.install_cli provision --tls-directory "$APP_DATA/tls"
}

install_local_trust() {
  security add-trusted-cert -r trustRoot -k "$LOGIN_KEYCHAIN" "$APP_DATA/tls/root-ca.pem"
}

register_word_manifest() {
  if ! { mkdir -p "$MANIFEST_DIRECTORY" 2>/dev/null && cp "$PROJECT_ROOT/manifest/word-researcher.xml" "$MANIFEST_TARGET" 2>/dev/null; }; then
    osascript "$SCRIPT_DIRECTORY/word_manifest.applescript" register \
      "$PROJECT_ROOT/manifest/word-researcher.xml" "$WORD_DOCUMENTS"
  fi
}

install_launch_agent() {
  PYTHONPATH="$PROJECT_ROOT/companion/src" "$PYTHON_EXECUTABLE" \
    -m researcher_companion.install_cli render-launch-agent \
    --output "$LAUNCH_AGENT" --python "$PYTHON_EXECUTABLE" \
    --project-root "$PROJECT_ROOT" --app-data "$APP_DATA"
  launchctl bootout "gui/$UID" "$LAUNCH_AGENT" 2>/dev/null || true
  launchctl bootstrap "gui/$UID" "$LAUNCH_AGENT"
}

install_phase1_spike() {
  require_prebuilt_runtime
  provision_private_material
  install_local_trust
  register_word_manifest
  install_launch_agent
}

install_phase1_spike
