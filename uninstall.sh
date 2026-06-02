#!/usr/bin/env bash

set -euo pipefail

APP_ID="desklaunch"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
INSTALL_ROOT="$XDG_DATA_HOME/$APP_ID"
BIN_PATH="$HOME/.local/bin/$APP_ID"
DESKTOP_ENTRY="$XDG_DATA_HOME/applications/$APP_ID.desktop"

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

rm -f "$BIN_PATH"
rm -f "$DESKTOP_ENTRY"
rm -f "$(desktop_dir)/$APP_ID.desktop"
rm -rf "$INSTALL_ROOT"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$XDG_DATA_HOME/applications" >/dev/null 2>&1 || true
fi

printf 'Removed DeskLaunch.\n'
