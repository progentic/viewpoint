#!/bin/zsh
set -euo pipefail

SCRIPT_DIRECTORY=${0:A:h}
PROJECT_ROOT=${SCRIPT_DIRECTORY:h:h}
PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE:-"$PROJECT_ROOT/.venv/bin/python"}
APP_DATA=${WORD_RESEARCHER_DATA:-"$HOME/Library/Application Support/WordResearcher"}
RUNTIME_ROOT="$APP_DATA/runtime"
LAUNCH_AGENT="$HOME/Library/LaunchAgents/local.word-researcher.companion.plist"
MANIFEST_DIRECTORY="$HOME/Library/Containers/com.microsoft.Word/Data/Documents/wef"
MANIFEST_TARGET="$MANIFEST_DIRECTORY/word-researcher.xml"
WORD_DOCUMENTS="$HOME/Library/Containers/com.microsoft.Word/Data/Documents"
LOGIN_KEYCHAIN="$HOME/Library/Keychains/login.keychain-db"
STABLE_ORIGIN="https://localhost:4179"

require_prebuilt_runtime() {
  [[ -x "$PYTHON_EXECUTABLE" ]] || { print -u2 "Missing locked Python environment"; return 1; }
  [[ -f "$PROJECT_ROOT/taskpane/dist/index.html" ]] || { print -u2 "Missing task-pane build"; return 1; }
  [[ -f "$PROJECT_ROOT/companion/src/researcher_companion/main.py" ]] || { print -u2 "Missing companion source"; return 1; }
  [[ -d "$PROJECT_ROOT/companion/migrations" ]] || { print -u2 "Missing migrations"; return 1; }
}

provision_private_material() {
  mkdir -p "$APP_DATA/logs"
  PYTHONPATH="$PROJECT_ROOT/companion/src" "$PYTHON_EXECUTABLE" \
    -m researcher_companion.install_cli provision --tls-directory "$APP_DATA/tls"
}

stop_installed_companion() {
  launchctl bootout "gui/$UID" "$LAUNCH_AGENT" 2>/dev/null || true
}

stage_runtime_assets() {
  rm -rf "$RUNTIME_ROOT"
  mkdir -p "$RUNTIME_ROOT/companion" "$RUNTIME_ROOT/taskpane"
  cp -R "$PROJECT_ROOT/companion/src" "$RUNTIME_ROOT/companion/src"
  cp -R "$PROJECT_ROOT/companion/migrations" "$RUNTIME_ROOT/companion/migrations"
  cp -R "$PROJECT_ROOT/taskpane/dist" "$RUNTIME_ROOT/taskpane/dist"
  find "$RUNTIME_ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
  find "$RUNTIME_ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
  chmod -R go-rwx "$RUNTIME_ROOT"
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
    --runtime-root "$RUNTIME_ROOT" --app-data "$APP_DATA"
  launchctl bootstrap "gui/$UID" "$LAUNCH_AGENT"
}

wait_for_companion() {
  repeat 40; do
    if /usr/bin/curl --fail --silent --show-error --noproxy '*' \
      --connect-timeout 1 --max-time 2 --output /dev/null "$STABLE_ORIGIN/taskpane"; then
      return
    fi
    sleep 0.25
  done
  print -u2 "The local HTTPS companion did not become ready at $STABLE_ORIGIN"
  return 1
}

install_phase1_spike() {
  require_prebuilt_runtime
  provision_private_material
  stop_installed_companion
  stage_runtime_assets
  install_local_trust
  register_word_manifest
  install_launch_agent
  wait_for_companion
}

install_phase1_spike
