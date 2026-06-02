#!/usr/bin/env bash

set -euo pipefail

APP_NAME="DeskLaunch"
APP_ID="desklaunch"
APP_COMMENT="Discover runnable assets and publish Linux desktop launchers."
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUILD_ROOT="$PROJECT_ROOT/.build"
PYTHON_VENV="$BUILD_ROOT/venv"
PYINSTALLER_BIN="$PYTHON_VENV/bin/pyinstaller"
DIST_ROOT="$PROJECT_ROOT/dist"
APPDIR_ROOT="$BUILD_ROOT/appimage/$APP_NAME.AppDir"
OUTPUT_ROOT="$PROJECT_ROOT/dist-appimage"
TOOLS_ROOT="$BUILD_ROOT/tools"
VERSION_VALUE="${VERSION:-0.1.0}"
ARCH_RAW="$(uname -m)"
DOWNLOAD_APPIMAGETOOL=1
CLEAN_BUILD=0

usage() {
  cat <<'EOF'
Usage: ./build-appimage.sh [options]

Options:
  --version <value>      Override the AppImage version label.
  --clean                Remove previous build output before packaging.
  --no-download          Require an existing appimagetool binary.
  -h, --help             Show this help text.

Environment:
  VERSION                Default version label if --version is not passed.
  APPIMAGETOOL_BIN       Use a specific appimagetool binary instead of auto-discovery.
EOF
}

require_linux() {
  if [[ "$(uname -s)" != "Linux" ]]; then
    printf 'This script must run on Linux.\n' >&2
    exit 1
  fi
}

map_arch() {
  case "$ARCH_RAW" in
    x86_64|amd64)
      printf 'x86_64\n'
      ;;
    aarch64|arm64)
      printf 'aarch64\n'
      ;;
    *)
      printf 'Unsupported architecture for AppImage packaging: %s\n' "$ARCH_RAW" >&2
      exit 1
      ;;
  esac
}

ensure_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Required command not found: %s\n' "$1" >&2
    exit 1
  fi
}

download_file() {
  local url="$1"
  local destination="$2"

  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --output "$destination" "$url"
    return
  fi

  if command -v wget >/dev/null 2>&1; then
    wget -O "$destination" "$url"
    return
  fi

  printf 'curl or wget is required to download build tools.\n' >&2
  exit 1
}

ensure_pyinstaller() {
  ensure_command python3

  if [[ ! -d "$PYTHON_VENV" ]]; then
    python3 -m venv "$PYTHON_VENV"
  fi

  "$PYTHON_VENV/bin/python" -m pip install --upgrade pip >/dev/null
  "$PYTHON_VENV/bin/python" -m pip install pyinstaller PySide6 >/dev/null
}

resolve_appimagetool() {
  local arch="$1"

  if [[ -n "${APPIMAGETOOL_BIN:-}" ]]; then
    printf '%s\n' "$APPIMAGETOOL_BIN"
    return
  fi

  if command -v appimagetool >/dev/null 2>&1; then
    command -v appimagetool
    return
  fi

  local cached="$TOOLS_ROOT/appimagetool-$arch.AppImage"
  if [[ -x "$cached" ]]; then
    printf '%s\n' "$cached"
    return
  fi

  if [[ "$DOWNLOAD_APPIMAGETOOL" -ne 1 ]]; then
    printf 'appimagetool was not found. Install it or set APPIMAGETOOL_BIN.\n' >&2
    exit 1
  fi

  mkdir -p "$TOOLS_ROOT"
  local url="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$arch.AppImage"
  printf 'Downloading appimagetool for %s ...\n' "$arch" >&2
  download_file "$url" "$cached"
  chmod +x "$cached"
  printf '%s\n' "$cached"
}

clean_previous_output() {
  rm -rf "$APPDIR_ROOT" "$OUTPUT_ROOT"
  rm -rf "$DIST_ROOT/$APP_NAME" "$BUILD_ROOT/pyinstaller"
}

build_binary_bundle() {
  mkdir -p "$BUILD_ROOT/pyinstaller"

  "$PYINSTALLER_BIN" \
    --noconfirm \
    --clean \
    --windowed \
    --name "$APP_NAME" \
    --distpath "$DIST_ROOT" \
    --workpath "$BUILD_ROOT/pyinstaller" \
    --specpath "$BUILD_ROOT/pyinstaller" \
    "$PROJECT_ROOT/app/desklaunch.py"
}

write_desktop_entry() {
  local destination="$1"
  cat > "$destination" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=$APP_NAME
Comment=$APP_COMMENT
Exec=$APP_NAME
Icon=$APP_ID
Terminal=false
Categories=Utility;System;
StartupNotify=true
EOF
}

write_apprun() {
  local destination="$1"
  cat > "$destination" <<'EOF'
#!/usr/bin/env bash

set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "$HERE/usr/bin/DeskLaunch" "$@"
EOF
  chmod +x "$destination"
}

assemble_appdir() {
  local bundle_root="$DIST_ROOT/$APP_NAME"
  if [[ ! -x "$bundle_root/$APP_NAME" ]]; then
    printf 'Expected PyInstaller bundle at %s\n' "$bundle_root/$APP_NAME" >&2
    exit 1
  fi

  mkdir -p \
    "$APPDIR_ROOT/usr/bin" \
    "$APPDIR_ROOT/usr/share/applications" \
    "$APPDIR_ROOT/usr/share/icons/hicolor/scalable/apps"

  cp -a "$bundle_root/." "$APPDIR_ROOT/usr/bin/"
  cp "$PROJECT_ROOT/assets/desklaunch.svg" "$APPDIR_ROOT/$APP_ID.svg"
  cp "$PROJECT_ROOT/assets/desklaunch.svg" "$APPDIR_ROOT/usr/share/icons/hicolor/scalable/apps/$APP_ID.svg"

  write_desktop_entry "$APPDIR_ROOT/$APP_ID.desktop"
  cp "$APPDIR_ROOT/$APP_ID.desktop" "$APPDIR_ROOT/usr/share/applications/$APP_ID.desktop"
  write_apprun "$APPDIR_ROOT/AppRun"
}

build_appimage() {
  local arch="$1"
  local appimagetool_bin="$2"
  local output_name="$APP_NAME-$VERSION_VALUE-$arch.AppImage"

  mkdir -p "$OUTPUT_ROOT"
  printf 'Creating %s ...\n' "$output_name"
  ARCH="$arch" VERSION="$VERSION_VALUE" APPIMAGE_EXTRACT_AND_RUN=1 \
    "$appimagetool_bin" "$APPDIR_ROOT" "$OUTPUT_ROOT/$output_name"
}

while (($#)); do
  case "$1" in
    --version)
      VERSION_VALUE="${2:-}"
      if [[ -z "$VERSION_VALUE" ]]; then
        printf '--version requires a value.\n' >&2
        exit 1
      fi
      shift 2
      ;;
    --clean)
      CLEAN_BUILD=1
      shift
      ;;
    --no-download)
      DOWNLOAD_APPIMAGETOOL=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

require_linux
ensure_command cp
ensure_command chmod

if [[ "$CLEAN_BUILD" -eq 1 ]]; then
  clean_previous_output
fi

ARCH_VALUE="$(map_arch)"
ensure_pyinstaller
APPIMAGETOOL_PATH="$(resolve_appimagetool "$ARCH_VALUE")"
build_binary_bundle
assemble_appdir
build_appimage "$ARCH_VALUE" "$APPIMAGETOOL_PATH"

printf '\nAppImage build complete.\n'
printf 'Output directory: %s\n' "$OUTPUT_ROOT"
