#!/usr/bin/env bash

set -euo pipefail

APP_NAME="DeskLaunch"
APP_ID="desklaunch"
APP_COMMENT="Discover runnable assets and publish Linux desktop launchers."
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
INSTALL_ROOT="$XDG_DATA_HOME/$APP_ID"
APP_DIR="$INSTALL_ROOT/app"
ASSETS_DIR="$INSTALL_ROOT/assets"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="$XDG_DATA_HOME/applications"
WRAPPER_PATH="$BIN_DIR/$APP_ID"
DESKTOP_ENTRY="$APPS_DIR/$APP_ID.desktop"
ICON_PATH="$ASSETS_DIR/$APP_ID.svg"
COPY_DESKTOP_ICON=0

desktop_dir() {
  local config_file="$HOME/.config/user-dirs.dirs"
  if [[ -f "$config_file" ]]; then
    local value
    value="$(grep '^XDG_DESKTOP_DIR=' "$config_file" | head -n 1 | cut -d= -f2- | tr -d '"')"
    if [[ -n "$value" ]]; then
      value="${value/\$HOME/$HOME}"
      printf '%s\n' "$value"
      return
    fi
  fi
  printf '%s\n' "$HOME/Desktop"
}

check_dependencies() {
  command -v python3 >/dev/null 2>&1 || {
    printf 'python3 is required.\n' >&2
    exit 1
  }

  if ! python3 - <<'PY'
import PySide6
PY
  then
    printf 'PySide6 is required for the DeskLaunch UI.\n' >&2
    printf 'Install it with your distro package manager or run: python3 -m pip install --user PySide6\n' >&2
    exit 1
  fi
}

while (($#)); do
  case "$1" in
    --desktop-icon)
      COPY_DESKTOP_ICON=1
      shift
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      printf 'Usage: ./install.sh [--desktop-icon]\n' >&2
      exit 1
      ;;
  esac
done

check_dependencies

mkdir -p "$APP_DIR" "$ASSETS_DIR" "$BIN_DIR" "$APPS_DIR"
cp "$SCRIPT_DIR/app/desklaunch.py" "$APP_DIR/desklaunch.py"
cp "$SCRIPT_DIR/assets/desklaunch.svg" "$ICON_PATH"

printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -euo pipefail' \
  "exec python3 \"$APP_DIR/desklaunch.py\" \"\$@\"" \
  > "$WRAPPER_PATH"
chmod +x "$WRAPPER_PATH"

python3 - "$SCRIPT_DIR/assets/desklaunch.desktop.in" "$DESKTOP_ENTRY" "$APP_NAME" "$APP_COMMENT" "$WRAPPER_PATH" "$ICON_PATH" <<'PY'
from pathlib import Path
import sys

def desktop_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'

template_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
replacements = {
    "@APP_NAME@": sys.argv[3],
    "@APP_COMMENT@": sys.argv[4],
    "@APP_EXEC@": desktop_quote(sys.argv[5]),
    "@APP_ICON@": sys.argv[6],
}
content = template_path.read_text(encoding="utf-8")
for key, value in replacements.items():
    content = content.replace(key, value)
output_path.write_text(content, encoding="utf-8")
PY
chmod +x "$DESKTOP_ENTRY"

if [[ "$COPY_DESKTOP_ICON" -eq 1 ]]; then
  DESKTOP_DIR="$(desktop_dir)"
  mkdir -p "$DESKTOP_DIR"
  cp "$DESKTOP_ENTRY" "$DESKTOP_DIR/$APP_ID.desktop"
  chmod +x "$DESKTOP_DIR/$APP_ID.desktop"
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
fi

printf '\nInstalled %s\n' "$APP_NAME"
printf 'Launcher command: %s\n' "$WRAPPER_PATH"
printf 'Desktop entry:    %s\n' "$DESKTOP_ENTRY"
if [[ "$COPY_DESKTOP_ICON" -eq 1 ]]; then
  printf 'Desktop icon:     %s/%s.desktop\n' "$(desktop_dir)" "$APP_ID"
fi
printf '\nIf %s is not in your app menu yet, log out and back in or run `update-desktop-database`.\n' "$APP_NAME"
