#!/bin/zsh
set -euo pipefail

SCRIPT_DIRECTORY=${0:A:h}
PROJECT_ROOT=${SCRIPT_DIRECTORY:h:h}
PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE:-"$PROJECT_ROOT/.venv/bin/python"}
APP_DATA=${WORD_RESEARCHER_DATA:-"$HOME/Library/Application Support/WordResearcher"}
LAUNCH_AGENT="$HOME/Library/LaunchAgents/local.word-researcher.companion.plist"
MANIFEST_TARGET="$HOME/Library/Containers/com.microsoft.Word/Data/Documents/wef/word-researcher.xml"
WORD_DOCUMENTS="$HOME/Library/Containers/com.microsoft.Word/Data/Documents"
LOGIN_KEYCHAIN="$HOME/Library/Keychains/login.keychain-db"

remove_registrations() {
  launchctl bootout "gui/$UID" "$LAUNCH_AGENT" 2>/dev/null || true
  if [[ -f "$APP_DATA/tls/root-ca.pem" ]]; then
    local fingerprint
    fingerprint=$(openssl x509 -in "$APP_DATA/tls/root-ca.pem" -noout -fingerprint -sha1 | cut -d= -f2 | tr -d :)
    security delete-certificate -Z "$fingerprint" "$LOGIN_KEYCHAIN" 2>/dev/null || true
  fi
  PYTHONPATH="$PROJECT_ROOT/companion/src" "$PYTHON_EXECUTABLE" \
    -m researcher_companion.install_cli delete-secret
  rm -f "$LAUNCH_AGENT"
  if ! rm -f "$MANIFEST_TARGET" 2>/dev/null; then
    osascript "$SCRIPT_DIRECTORY/word_manifest.applescript" unregister "" "$WORD_DOCUMENTS"
  fi
}

remove_phase1_files() {
  rm -rf "$APP_DATA/runtime/companion" "$APP_DATA/runtime/taskpane"
  rmdir "$APP_DATA/runtime" 2>/dev/null || true
  rm -f "$APP_DATA/state/companion.sqlite3"
  rm -f "$APP_DATA/tls/root-ca.pem" "$APP_DATA/tls/root-ca-key.pem"
  rm -f "$APP_DATA/tls/server-cert.pem" "$APP_DATA/tls/server-key.pem"
  rm -f "$APP_DATA/tls/tls-metadata.json"
  rm -f "$APP_DATA/logs/companion.stdout.log" "$APP_DATA/logs/companion.stderr.log"
  rmdir "$APP_DATA/content" "$APP_DATA/state" "$APP_DATA/tls" "$APP_DATA/logs" 2>/dev/null || true
  rmdir "$APP_DATA" 2>/dev/null || true
}

remove_registrations
remove_phase1_files
