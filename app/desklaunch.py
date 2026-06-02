#!/usr/bin/env python3

from __future__ import annotations

import base64
import os
import shlex
import shutil
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PySide6.QtCore import Qt, QSize, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QBoxLayout,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QToolTip,
    QVBoxLayout,
    QWidget,
)


APP_NAME = "DeskLaunch"
APP_ID = "desklaunch"
APP_COMMENT = "Discover runnable assets and publish Linux desktop launchers."
PUBLISH_DIR_LABEL = "~/.local/share/applications"
SUPPORT_URL = "https://ko-fi.com/G1M820A57S"
KOFI_BUTTON_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAkQAAACSCAMAAACTxiVzAAAAAXNSR0IArs4c6QAAAARnQU1BAACx"
    "jwv8YQUAAAFoUExURQAAAP9wQP9gMP9oOP9gMP9lNf9gMP9kNP9kMP9jM/9jMP9mM/9lNf9lMv9i"
    "Mv9iMP9kNP9kMv9iMv9kMv9lM/9jM/9jMv9lM/9jMv9kM/9jMf9lM/9jMv9kM/9kM/9kMv9kM/9j"
    "Mv9lM/9jMv9jMv9kM/9jMv/////18v/18f/18PHx8f/s5v/r5f/r4v/q4v/i2f/g1OPj4//YzP/W"
    "xf/WxP/VxP/Ov//Mt//Mtv/LttXV1f/Fs//Fsv/Esv/BqP/Bp/+8pv+7pv+3mf+2mcfHx/+ymf+x"
    "mf+si/+siv+ojP+njP+ifP+ie7m5uf+egP+ef/+Ybf+Xbf+Vc/+Uc6urq/+NXv+LZv+KZv+DUP+B"
    "Wf+AWZ2dnf94Tf93Tf95Qv93TP95Qf9uQP9vM/9uM5CQkI+Pj/9kM/9kJf9kJP9aFoKCgoGBgXR0"
    "dHNzc2ZmZmVlZVhYWFdXV0pKSklJSTw8PC4uLiAgINwb3EwAAAAndFJOUwAQECAgMDBAQFBQX2Bg"
    "YGBwcHCPkJCQn5+goK+vsL/Az9Df3+Dv7+CCITYAAA9kSURBVHja7Nzxb9pGFAdwC6VttkqZaKW0"
    "WtYoEkuft5qIcp2oRuZMbpHVOgswsGAk0Ziz4c1radIU+PcXfE595ozPxkRk8D6/9YyMeXx7d74z"
    "keLJrD/Y3NrJPbXRSnia297afLCekeYl89WjHJZ1Ne083libQ4IebGMpV9t2yhytY4LQla0vZ++E"
    "cBRDntyGNIsszqJRuhitYy+E0sVo7RssGeI9XpNiu48jGUrXGWUeYrHQNA8zsYYynA2hCLk1Segu"
    "DmUoUu6OcDqERUIi96VIWawQEstihlBqWRzL0M2NaHexNiiuO3hvj9LaXZNCZDBDKIFcRuLhOjVK"
    "5KHE2cCqoGTu44QIzX1a9DXWBCW1hYMZSu2exMLBDM0ghx0RSi2LHRFKazeDHRFKK4sdEZrbrOgL"
    "rAVKe4P2BEuBZrUtudawEmh2GZxWo/lMrfEvf6AUtnE0Q6llZhzNusfNqqHrqqqWyBQlVdV0vdps"
    "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"
    "QmCC"
)
FALLBACK_SCRIPT_ICON = "utilities-terminal"
FALLBACK_EXEC_ICON = "application-x-executable"
FALLBACK_OPEN_ICON = "folder-open"
ICON_FILE_SUFFIXES = (".png", ".svg", ".xpm", ".ico", ".jpg", ".jpeg", ".bmp", ".gif")
STYLE_SHEET = """
QWidget {
    color: #122338;
    background: #f4f7fb;
    font-family: "DejaVu Sans";
    font-size: 10pt;
}
QWidget#Root {
    background: #f4f7fb;
}
QDialog,
QMessageBox,
QFileDialog {
    background: #f4f7fb;
    color: #122338;
}
QDialog QLabel,
QMessageBox QLabel,
QFileDialog QLabel {
    color: #122338;
    background: transparent;
}
QFileDialog QListView,
QFileDialog QTreeView,
QFileDialog QTableView {
    background: #ffffff;
    color: #122338;
    border: 1px solid #e6edf5;
    border-radius: 8px;
    alternate-background-color: #fbfcfe;
    selection-background-color: #e6eefc;
    selection-color: #0f172a;
}
QFileDialog QToolButton {
    background: #edf3fa;
    color: #17314b;
    border: 0;
    border-radius: 10px;
    padding: 6px 10px;
}
QFileDialog QToolButton:hover {
    background: #e6eef8;
}
QLabel {
    background: transparent;
}
QFrame#Card {
    background: #ffffff;
    border: 1px solid #e6edf5;
    border-radius: 18px;
}
QFrame#SoftCard {
    background: #f7f9fc;
    border: 0;
    border-radius: 14px;
}
QLabel#Eyebrow {
    color: #5e7288;
    font-size: 8.5pt;
    font-weight: 600;
    letter-spacing: 0.08em;
}
QLabel#HeroTitle {
    color: #0f172a;
    font-size: 20pt;
    font-weight: 700;
}
QLabel#HeroText {
    color: #5f7185;
    font-size: 9pt;
}
QLabel#CardTitle {
    color: #122338;
    font-size: 12pt;
    font-weight: 700;
}
QLabel#CardText {
    color: #67798c;
    font-size: 8.5pt;
}
QLabel#InfoText {
    color: #36516c;
    font-size: 8.5pt;
    font-weight: 600;
}
QLabel#StatusText {
    color: #4c6074;
    font-size: 8.5pt;
}
QLabel#HintText {
    color: #7a8b9b;
    font-size: 8pt;
}
QLabel#HintBadge {
    color: #5f7185;
    background: #eef3f8;
    border: 1px solid #dde6f0;
    border-radius: 9px;
    padding: 0px 7px;
    font-weight: 700;
    font-size: 9pt;
    min-width: 10px;
    min-height: 16px;
    max-height: 18px;
}
QLabel#HintBadge:hover {
    color: #122338;
    background: #e4edf7;
    border: 1px solid #cfdceb;
}
QLineEdit,
QComboBox,
QSpinBox,
QTableWidget {
    background: #f8fafc;
    border: 1px solid transparent;
    border-radius: 14px;
    padding: 8px 10px;
    color: #0f172a;
}
QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QTableWidget:focus {
    background: #ffffff;
    border: 1px solid #90b6ef;
}
QLineEdit::placeholder {
    color: #9aa8b5;
}
QPushButton {
    background: #edf3fa;
    border: 0;
    border-radius: 14px;
    padding: 8px 12px;
    color: #17314b;
    font-weight: 600;
}
QPushButton:hover {
    background: #e6eef8;
}
QPushButton:pressed {
    background: #dde8f4;
}
QPushButton:disabled {
    background: #eef2f6;
    color: #a0adba;
}
QPushButton#PrimaryButton {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #14365d,
        stop: 1 #204a76
    );
    color: #ffffff;
}
QPushButton#PrimaryButton:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #1a426b,
        stop: 1 #2a5a89
    );
}
QPushButton#GhostButton {
    background: transparent;
    color: #3f668e;
    padding-left: 0;
    padding-right: 0;
}
QPushButton#GhostButton:hover {
    background: transparent;
    color: #254f7b;
}
QPushButton#SupportButton {
    background: transparent;
    border: 0;
    padding: 0;
}
QPushButton#SupportButton:hover {
    background: transparent;
}
QPushButton#SupportButton:pressed {
    background: transparent;
}
QPushButton#ChipButton {
    background: #eef3f8;
    border: 1px solid #dde6f0;
    border-radius: 13px;
    padding: 7px 10px;
    color: #33485f;
    text-align: left;
    font-weight: 600;
}
QPushButton#ChipButton:hover {
    background: #e4edf7;
    border: 1px solid #cfdceb;
}
QPushButton#ChipButton:checked {
    background: #0f172a;
    color: #ffffff;
    border: 1px solid #0f172a;
}
QPushButton#ChipButton:checked:hover {
    background: #162036;
}
QComboBox::drop-down {
    border: 0;
    width: 28px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QSpinBox::up-button,
QSpinBox::down-button {
    width: 18px;
    border: 0;
    background: transparent;
}
QTableWidget {
    gridline-color: transparent;
    alternate-background-color: #fbfcfe;
    selection-background-color: #e6eefc;
    selection-color: #0f172a;
}
QHeaderView::section {
    background: transparent;
    color: #6b7c8f;
    border: 0;
    padding: 10px 8px;
    font-weight: 700;
}
QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 4px 0 4px 0;
}
QScrollBar::handle:vertical {
    background: #d8e1eb;
    border-radius: 6px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #c8d3df;
}
QScrollBar:horizontal {
    background: transparent;
    height: 12px;
    margin: 0 4px 0 4px;
}
QScrollBar::handle:horizontal {
    background: #d8e1eb;
    border-radius: 6px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover {
    background: #c8d3df;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical,
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
    border: 0;
}
QScrollArea {
    background: transparent;
    border: 0;
}
QTabBar#CompactTabs {
    margin-top: 4px;
    background: #f4f7fb;
    border: 0;
    border-radius: 0px;
    padding: 0px;
}
QTabBar#CompactTabs::tab {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #14365d,
        stop: 1 #204a76
    );
    color: #eef4fb;
    border: 0;
    border-radius: 0px;
    padding: 10px 14px;
    margin-right: 0px;
    font-weight: 700;
}
QTabBar#CompactTabs::tab:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #1a426b,
        stop: 1 #2a5a89
    );
}
QTabBar#CompactTabs::tab:selected {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #f59e0b,
        stop: 1 #c2410c
    );
    color: #ffffff;
}
QTabBar#CompactTabs::tab:selected:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #f8ac22,
        stop: 1 #d15212
    );
}
"""


@dataclass(slots=True)
class InstalledApp:
    name: str
    exec_command: str
    icon: str
    comment: str
    desktop_path: Path


def _installed_app_search_dirs() -> list[Path]:
    candidates = [
        Path("/usr/share/applications"),
        Path("/usr/local/share/applications"),
        xdg_data_home() / "applications",
        Path("/var/lib/flatpak/exports/share/applications"),
        xdg_data_home() / "flatpak" / "exports" / "share" / "applications",
        Path("/var/lib/snapd/desktop/applications"),
    ]
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in candidates:
        if path in seen or not path.exists() or not path.is_dir():
            continue
        seen.add(path)
        ordered.append(path)
    return ordered


def parse_desktop_entry(path: Path) -> InstalledApp | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    section: str | None = None
    fields: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section != "Desktop Entry" or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key in fields or "[" in key:
            continue
        fields[key] = value.strip()

    if fields.get("Type", "") != "Application":
        return None
    if fields.get("NoDisplay", "").lower() == "true":
        return None
    if fields.get("Hidden", "").lower() == "true":
        return None
    exec_cmd = fields.get("Exec", "")
    if not exec_cmd:
        return None

    return InstalledApp(
        name=fields.get("Name", path.stem),
        exec_command=exec_cmd,
        icon=fields.get("Icon", ""),
        comment=fields.get("Comment", ""),
        desktop_path=path,
    )


def scan_installed_apps() -> list[InstalledApp]:
    apps: list[InstalledApp] = []
    seen_keys: set[str] = set()
    for directory in _installed_app_search_dirs():
        for desktop_file in sorted(directory.glob("*.desktop")):
            if desktop_file.name in seen_keys:
                continue
            seen_keys.add(desktop_file.name)
            app = parse_desktop_entry(desktop_file)
            if app is not None:
                apps.append(app)
    apps.sort(key=lambda a: a.name.lower())
    return apps


def parse_installed_exec(exec_command: str) -> tuple[str, str] | None:
    try:
        parts = shlex.split(exec_command)
    except ValueError:
        return None
    cleaned = [part for part in parts if not part.startswith("%")]
    if not cleaned:
        return None
    binary = cleaned[0]
    if "/" not in binary:
        resolved = shutil.which(binary)
        if resolved:
            binary = resolved
    arguments = " ".join(shlex.quote(p) for p in cleaned[1:])
    return binary, arguments


@dataclass(slots=True)
class LauncherRequest:
    name: str
    target: Path
    working_dir: Path
    arguments: str
    icon: str
    categories: str
    mode: str
    terminal: bool
    add_desktop_icon: bool
    chmod_target: bool
    sudo: bool


def xdg_data_home() -> Path:
    value = os.environ.get("XDG_DATA_HOME")
    if value:
        return Path(value).expanduser()
    return Path.home() / ".local" / "share"


def xdg_apps_dir() -> Path:
    return xdg_data_home() / "applications"


def app_support_dir() -> Path:
    return xdg_data_home() / APP_ID


def desktop_dir() -> Path:
    config_path = Path.home() / ".config" / "user-dirs.dirs"
    if config_path.exists():
        for line in config_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line.startswith("XDG_DESKTOP_DIR="):
                continue
            raw = line.split("=", 1)[1].strip().strip('"')
            raw = raw.replace("$HOME", str(Path.home()))
            return Path(raw).expanduser()
    return Path.home() / "Desktop"


def slugify(value: str) -> str:
    cleaned: list[str] = []
    last_dash = False
    for char in value.strip().lower():
        if char.isalnum():
            cleaned.append(char)
            last_dash = False
            continue
        if not last_dash:
            cleaned.append("-")
            last_dash = True
    slug = "".join(cleaned).strip("-")
    return slug or "launcher"


def title_from_path(path: Path) -> str:
    raw = path.stem.replace("_", " ").replace("-", " ").strip()
    return raw.title() if raw else path.name


def is_executable(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        mode = path.stat().st_mode
    except OSError:
        return False
    return bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def detect_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    executable = is_executable(path)
    if suffix == ".appimage":
        return "AppImage"
    if suffix == ".sh":
        return "Shell script"
    if suffix == ".py":
        return "Python script"
    if executable:
        return "Executable"
    return "File"


def default_mode_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".sh":
        return "bash"
    if suffix == ".py":
        return "python"
    if suffix == ".appimage" or is_executable(path):
        return "executable"
    return "open"


def default_icon_for_mode(mode: str) -> str:
    if mode in {"bash", "python"}:
        return FALLBACK_SCRIPT_ICON
    if mode == "open":
        return FALLBACK_OPEN_ICON
    return FALLBACK_EXEC_ICON


def quoted_command(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def desktop_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_exec_parts(target: Path, mode: str, arguments: str) -> list[str]:
    args = shlex.split(arguments)
    if mode == "bash":
        return ["/usr/bin/env", "bash", str(target), *args]
    if mode == "python":
        return ["/usr/bin/env", "python3", str(target), *args]
    if mode == "open":
        if args:
            raise ValueError("Open mode uses xdg-open and does not accept extra arguments.")
        return ["/usr/bin/env", "xdg-open", str(target)]
    return [str(target), *args]


def normalize_categories(value: str) -> str:
    categories = value.strip() or "Utility;"
    if not categories.endswith(";"):
        categories += ";"
    return categories


def ensure_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def create_launcher_files(request: LauncherRequest) -> tuple[Path, Path]:
    support_dir = app_support_dir()
    launchers_dir = support_dir / "launchers"
    xdg_dir = xdg_apps_dir()
    support_dir.mkdir(parents=True, exist_ok=True)
    launchers_dir.mkdir(parents=True, exist_ok=True)
    xdg_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(request.name)
    helper_path = launchers_dir / f"{slug}.sh"
    desktop_path = xdg_dir / f"{slug}.desktop"

    if request.chmod_target and request.mode == "executable" and not is_executable(request.target):
        ensure_executable(request.target)

    exec_parts = build_exec_parts(request.target, request.mode, request.arguments)
    helper_lines: list[str] = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"cd {shlex.quote(str(request.working_dir))}",
    ]
    if request.sudo:
        helper_lines += [
            "if command -v xhost >/dev/null 2>&1; then",
            "    xhost +SI:localuser:root >/dev/null 2>&1 || true",
            "fi",
            "exec pkexec env \\",
            '    DISPLAY="${DISPLAY:-}" \\',
            '    XAUTHORITY="${XAUTHORITY:-}" \\',
            '    WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-}" \\',
            '    XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-}" \\',
            '    XDG_SESSION_TYPE="${XDG_SESSION_TYPE:-}" \\',
            '    XDG_DATA_DIRS="${XDG_DATA_DIRS:-}" \\',
            '    DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-}" \\',
            '    HOME="${HOME:-/root}" \\',
            f"    {quoted_command(exec_parts)}",
        ]
    else:
        helper_lines.append(f"exec {quoted_command(exec_parts)}")
    helper_lines.append("")
    helper_path.write_text("\n".join(helper_lines), encoding="utf-8")
    ensure_executable(helper_path)

    icon_value = request.icon.strip() or default_icon_for_mode(request.mode)
    desktop_lines = [
        "[Desktop Entry]",
        "Type=Application",
        "Version=1.0",
        f"Name={request.name}",
        f"Comment=Published by {APP_NAME}",
        f"Exec={desktop_quote(str(helper_path))}",
        f"Path={request.working_dir}",
        f"Icon={icon_value}",
        f"Terminal={'true' if request.terminal else 'false'}",
        f"Categories={normalize_categories(request.categories)}",
        "StartupNotify=true",
        "",
    ]
    desktop_path.write_text("\n".join(desktop_lines), encoding="utf-8")
    ensure_executable(desktop_path)

    if request.add_desktop_icon:
        user_desktop_dir = desktop_dir()
        user_desktop_dir.mkdir(parents=True, exist_ok=True)
        desktop_copy = user_desktop_dir / desktop_path.name
        desktop_copy.write_text(desktop_path.read_text(encoding="utf-8"), encoding="utf-8")
        ensure_executable(desktop_copy)

    return helper_path, desktop_path


class HintBadge(QLabel):
    def __init__(self, tip: str) -> None:
        super().__init__("?")
        self._tip = tip
        self.setObjectName("HintBadge")
        self.setCursor(Qt.CursorShape.WhatsThisCursor)
        self.setToolTip(tip)

    def enterEvent(self, event) -> None:  # type: ignore[override]
        QToolTip.showText(self.mapToGlobal(self.rect().bottomLeft()), self._tip, self)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        QToolTip.hideText()
        super().leaveEvent(event)


class DeskLaunchWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1240, 780)
        self.setMinimumSize(760, 500)

        self.responsive_rows: list[tuple[str, QBoxLayout, QWidget]] = []
        self.target_path: Path | None = None
        self.args_value = ""
        self.workdir_value = str(Path.home())
        self.icon_value = ""
        self.categories_value = "Utility;"
        self.terminal_value = False
        self.desktop_icon_value = True
        self.chmod_target_value = True
        self.sudo_value = False

        self._build_ui()
        self._set_defaults()
        QTimer.singleShot(0, self._apply_responsive_layouts)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        self.main_card = QFrame()
        self.main_card.setObjectName("Card")
        self.main_card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        self.main_card.setMaximumWidth(720)
        self.main_card.setMinimumWidth(420)
        main_layout = QVBoxLayout(self.main_card)
        main_layout.setContentsMargins(28, 26, 28, 26)
        main_layout.setSpacing(14)

        eyebrow = QLabel("LINUX LAUNCHER")
        eyebrow.setObjectName("Eyebrow")
        title = QLabel(APP_NAME)
        title.setObjectName("HeroTitle")
        subtitle = QLabel("Find a runnable file and publish it as a real desktop app.")
        subtitle.setObjectName("HeroText")
        subtitle.setWordWrap(True)
        main_layout.addWidget(eyebrow)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(10)

        self._populate_launcher_form(main_layout)

        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        centerer = QHBoxLayout()
        centerer.setContentsMargins(0, 0, 0, 0)
        centerer.addStretch(1)
        centerer.addWidget(self.main_card)
        centerer.addStretch(1)

        panel_layout.addStretch(1)
        panel_layout.addLayout(centerer)
        panel_layout.addStretch(1)

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_scroll.setWidget(panel)
        self.launcher_scroll = main_scroll
        outer.addWidget(main_scroll, 1)

        status_card = QFrame()
        status_card.setObjectName("SoftCard")
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(18, 12, 18, 12)
        status_layout.setSpacing(10)
        self.status_label = QLabel("Ready.")
        self.status_label.setObjectName("StatusText")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch(1)
        self.support_button = QPushButton()
        self.support_button.setObjectName("SupportButton")
        self.support_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.support_button.setToolTip(SUPPORT_URL)
        self.support_button.clicked.connect(self._open_support_link)

        kofi_pixmap = QPixmap()
        if kofi_pixmap.loadFromData(base64.b64decode(KOFI_BUTTON_PNG_B64), "PNG"):
            self.support_button.setIcon(QIcon(kofi_pixmap))
            self.support_button.setIconSize(QSize(143, 36))
            self.support_button.setFlat(True)
        else:
            self.support_button.setText("Support me on Ko-fi")
        status_layout.addWidget(self.support_button)
        outer.addWidget(status_card)

    def _build_card(self, title: str, subtitle: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(0)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("CardText")
            subtitle_label.setWordWrap(True)
            layout.addSpacing(2)
            layout.addWidget(subtitle_label)

        layout.addSpacing(14)

        content = QVBoxLayout()
        content.setSpacing(10)
        layout.addLayout(content)
        return card, content

    def _make_chip_button(self, label: str, checked: bool = False) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName("ChipButton")
        button.setCheckable(True)
        button.setChecked(checked)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return button

    def _build_field_block(
        self,
        label_text: str,
        field: QWidget,
        *,
        trailing: QWidget | None = None,
        hint: str = "",
        scope: str = "",
        tooltip: str = "",
    ) -> QVBoxLayout:
        block = QVBoxLayout()
        block.setContentsMargins(0, 0, 0, 0)
        block.setSpacing(4)

        if tooltip:
            label_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            label_row.setContentsMargins(0, 0, 0, 0)
            label_row.setSpacing(6)
            label = QLabel(label_text)
            label_row.addWidget(label)
            label_row.addWidget(HintBadge(tooltip))
            label_row.addStretch(1)
            block.addLayout(label_row)
        else:
            label = QLabel(label_text)
            block.addWidget(label)

        row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        row.addWidget(field, 1)
        if trailing is not None:
            trailing.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            row.addWidget(trailing)
            if scope:
                self.responsive_rows.append((scope, row, trailing))
        block.addLayout(row)

        if hint:
            hint_label = QLabel(hint)
            hint_label.setObjectName("HintText")
            hint_label.setWordWrap(True)
            block.addWidget(hint_label)

        return block

    def _populate_launcher_form(self, content: QVBoxLayout) -> None:
        content.setSpacing(10)

        target_block = QVBoxLayout()
        target_block.setContentsMargins(0, 0, 0, 0)
        target_block.setSpacing(4)
        target_block.addWidget(QLabel("Target file"))

        target_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        target_row.setContentsMargins(0, 0, 0, 0)
        target_row.setSpacing(10)
        target_browse = QPushButton("Browse")
        target_browse.clicked.connect(self._browse_target)
        self.installed_apps_button = QPushButton("Pick from installed apps...")
        self.installed_apps_button.clicked.connect(self._open_installed_app_picker)
        target_row.addWidget(target_browse)
        target_row.addWidget(self.installed_apps_button)
        target_row.addStretch(1)
        target_block.addLayout(target_row)

        self.target_display = QLabel("No target selected")
        self.target_display.setObjectName("HintText")
        self.target_display.setWordWrap(True)
        target_block.addWidget(self.target_display)
        content.addLayout(target_block)

        self.launcher_name_edit = QLineEdit()
        self.launcher_name_edit.setPlaceholderText("Launcher name")
        content.addLayout(self._build_field_block("Launcher name", self.launcher_name_edit))

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Auto", "auto")
        self.mode_combo.addItem("Executable", "executable")
        self.mode_combo.addItem("Bash", "bash")
        self.mode_combo.addItem("Python", "python")
        self.mode_combo.addItem("Open", "open")
        content.addLayout(self._build_field_block("Launch mode", self.mode_combo, hint="Auto usually works."))

        self.advanced_button = QPushButton("Advanced")
        self.advanced_button.clicked.connect(self._open_advanced_dialog)
        content.addWidget(self.advanced_button)

        self.notes_label = QLabel(f"Saved to {PUBLISH_DIR_LABEL}.")
        self.notes_label.setObjectName("HintText")
        self.notes_label.setWordWrap(True)
        content.addWidget(self.notes_label)

        self.advanced_summary_label = QLabel("")
        self.advanced_summary_label.setObjectName("InfoText")
        self.advanced_summary_label.setWordWrap(True)
        content.addWidget(self.advanced_summary_label)

        actions = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        actions.setSpacing(10)
        self.launcher_actions = actions
        content.addLayout(actions)

        self.create_button = QPushButton("Create launcher")
        self.create_button.setObjectName("PrimaryButton")
        self.create_button.clicked.connect(self._create_launcher)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._reset_form)

        actions.addWidget(self.create_button)
        actions.addWidget(self.clear_button)
        actions.addStretch(1)

    def _open_support_link(self) -> None:
        if self._launch_url_clean_env(SUPPORT_URL):
            self.status_label.setText("Opening Ko-fi in your browser...")
            return

        if QDesktopServices.openUrl(QUrl(SUPPORT_URL)):
            self.status_label.setText("Opening Ko-fi in your browser...")
            return

        try:
            import webbrowser
            if webbrowser.open(SUPPORT_URL):
                self.status_label.setText("Opening Ko-fi in your browser...")
                return
        except Exception as exc:
            print(f"[support] webbrowser fallback failed: {exc}", flush=True)

        self._show_error(
            "Could not open the browser. Open this URL manually:\n" + SUPPORT_URL
        )

    @staticmethod
    def _launch_url_clean_env(url: str) -> bool:
        import subprocess
        env = os.environ.copy()
        appimage_active = bool(env.get("APPIMAGE") or env.get("APPDIR"))
        appimage_vars = (
            "LD_LIBRARY_PATH",
            "LD_PRELOAD",
            "PYTHONHOME",
            "PYTHONPATH",
            "PERLLIB",
            "GSETTINGS_SCHEMA_DIR",
            "GST_PLUGIN_SYSTEM_PATH",
            "QT_PLUGIN_PATH",
            "XDG_DATA_DIRS",
            "PATH",
        )
        for var in appimage_vars:
            original = env.get(f"APPIMAGE_ORIGINAL_{var}")
            if original is not None:
                env[var] = original
            elif appimage_active and var != "PATH":
                env.pop(var, None)
        try:
            subprocess.Popen(
                ["xdg-open", url],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except FileNotFoundError:
            print("[support] xdg-open not found on PATH", flush=True)
            return False
        except Exception as exc:
            print(f"[support] xdg-open clean-env failed: {exc}", flush=True)
            return False

    def _set_defaults(self) -> None:
        home = str(Path.home())
        self.args_value = ""
        self.workdir_value = home
        self.icon_value = ""
        self.categories_value = "Utility;"
        self.terminal_value = False
        self.desktop_icon_value = True
        self.chmod_target_value = True
        self.sudo_value = False
        self._set_mode("auto")
        self.notes_label.setText(f"Saved to {PUBLISH_DIR_LABEL}. Helper scripts go to ~/.local/share/desklaunch/launchers.")
        self._update_advanced_summary()

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, APP_NAME, message)

    def _show_info(self, message: str) -> None:
        QMessageBox.information(self, APP_NAME, message)

    def _update_advanced_summary(self) -> None:
        parts: list[str] = []
        if self.args_value.strip():
            parts.append("arguments")
        if self.icon_value.strip():
            parts.append("icon")
        if self.categories_value.strip() and self.categories_value.strip() != "Utility;":
            parts.append("categories")
        if self.terminal_value:
            parts.append("terminal")
        if not self.desktop_icon_value:
            parts.append("no desktop copy")
        if not self.chmod_target_value:
            parts.append("no chmod")
        if self.sudo_value:
            parts.append("sudo")

        if parts:
            self.advanced_summary_label.setText("Advanced: " + ", ".join(parts))
        else:
            self.advanced_summary_label.setText("Advanced: defaults only")

    def _set_box_direction(self, layout: QBoxLayout, vertical: bool) -> None:
        direction = QBoxLayout.Direction.TopToBottom if vertical else QBoxLayout.Direction.LeftToRight
        if layout.direction() != direction:
            layout.setDirection(direction)

    def _apply_responsive_layouts(self) -> None:
        launcher_width = self.main_card.width() or max(360, self.width() - 32)
        self._set_box_direction(self.launcher_actions, launcher_width < 560)

        for _scope, row, button in self.responsive_rows:
            vertical = launcher_width < 720
            self._set_box_direction(row, vertical)
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding if vertical else QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed,
            )

    def _size_browse_dialog(self, dialog: QFileDialog) -> None:
        floor_w, floor_h = 720, 520
        parent_size = self.size()
        target_w = max(int(parent_size.width() * 0.73), floor_w)
        target_h = max(int(parent_size.height() * 0.73), floor_h)
        dialog.setMinimumSize(floor_w, floor_h)
        dialog.resize(target_w, target_h)
        splitter = dialog.findChild(QSplitter)
        if splitter is not None:
            sidebar_w = int(target_w * 0.30)
            splitter.setSizes([sidebar_w, target_w - sidebar_w])

    def _pick_directory(self, title: str, start_path: Path) -> Path | None:
        dialog = QFileDialog(self, title, str(start_path.expanduser()))
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        self._size_browse_dialog(dialog)
        if dialog.exec():
            return Path(dialog.selectedFiles()[0])
        return None

    def _pick_file(self, title: str, start_path: Path, name_filter: str = "") -> Path | None:
        start_dir = start_path.expanduser()
        if start_dir.is_file():
            start_dir = start_dir.parent
        dialog = QFileDialog(self, title, str(start_dir))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        if name_filter:
            dialog.setNameFilter(name_filter)
        self._size_browse_dialog(dialog)
        if dialog.exec():
            return Path(dialog.selectedFiles()[0])
        return None

    def _browse_target(self) -> None:
        start = self.target_path or Path.home()
        selected = self._pick_file("Choose target file", start)
        if selected is not None:
            self._load_target(selected)

    def _open_installed_app_picker(self) -> None:
        apps = scan_installed_apps()
        if not apps:
            self._show_info("No installed apps were found in the standard locations.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Installed apps")
        dialog.setModal(True)
        floor_w, floor_h = 620, 520
        parent_size = self.size()
        target_w = max(int(parent_size.width() * 0.6), floor_w)
        target_h = max(int(parent_size.height() * 0.7), floor_h)
        dialog.setMinimumSize(floor_w, floor_h)
        dialog.resize(target_w, target_h)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Installed apps")
        title.setObjectName("CardTitle")
        hint = QLabel("Pick a system app (Dolphin, Kate, ...). Combine with 'Run as sudo' in Advanced for admin launchers.")
        hint.setObjectName("CardText")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        search = QLineEdit()
        search.setPlaceholderText("Filter by name or command")
        layout.addWidget(search)

        list_widget = QListWidget()
        layout.addWidget(list_widget, 1)
        for app in apps:
            label = app.name if not app.comment else f"{app.name}  —  {app.comment}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, app)
            list_widget.addItem(item)
        if list_widget.count():
            list_widget.setCurrentRow(0)

        def filter_items(text: str) -> None:
            needle = text.strip().lower()
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                app_obj = item.data(Qt.ItemDataRole.UserRole)
                visible = (
                    not needle
                    or needle in app_obj.name.lower()
                    or needle in app_obj.exec_command.lower()
                )
                item.setHidden(not visible)

        search.textChanged.connect(filter_items)
        list_widget.itemDoubleClicked.connect(lambda _item: dialog.accept())

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        search.setFocus()

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        current = list_widget.currentItem()
        if current is None or current.isHidden():
            return
        self._apply_installed_app(current.data(Qt.ItemDataRole.UserRole))

    def _apply_installed_app(self, app: InstalledApp) -> None:
        parsed = parse_installed_exec(app.exec_command)
        if parsed is None:
            self._show_error(f"Could not parse the Exec line for {app.name}.")
            return
        binary, arguments = parsed

        target = Path(binary)
        self.target_path = target
        self.target_display.setText(str(target))
        self.launcher_name_edit.setText(app.name)
        parent = target.parent
        self.workdir_value = str(parent) if parent != Path() and parent.exists() else str(Path.home())
        self.args_value = arguments
        if app.icon:
            self.icon_value = app.icon
        self._set_mode("executable")
        self.terminal_value = False
        self._update_advanced_summary()
        self.status_label.setText(f"Loaded {app.name}")

    def _set_mode(self, mode: str) -> None:
        for index in range(self.mode_combo.count()):
            if self.mode_combo.itemData(index) == mode:
                self.mode_combo.setCurrentIndex(index)
                return
        self.mode_combo.setCurrentIndex(0)

    def _selected_mode(self) -> str:
        data = self.mode_combo.currentData()
        return data if isinstance(data, str) else "auto"

    def _open_advanced_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced settings")
        dialog.setModal(True)
        dialog.resize(620, 520)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("Advanced settings")
        title.setObjectName("CardTitle")
        hint = QLabel("Optional overrides for arguments, icon, working directory, and launcher behavior.")
        hint.setObjectName("CardText")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        args_edit = QLineEdit(self.args_value)
        args_edit.setPlaceholderText("Optional arguments")
        layout.addLayout(
            self._build_field_block(
                "Arguments",
                args_edit,
                tooltip=(
                    "Extra command-line args appended to the target.\n"
                    "Parsed like a shell — quote values with spaces, e.g. --name \"Hello world\".\n"
                    "No variable / glob expansion ($HOME, *.txt are passed literally).\n"
                    "Not allowed in 'Open' mode (xdg-open takes no extra args)."
                ),
            )
        )

        workdir_edit = QLineEdit(self.workdir_value)
        workdir_edit.setPlaceholderText("Working directory")
        workdir_browse = QPushButton("Browse")
        workdir_browse.clicked.connect(
            lambda: self._dialog_pick_directory(workdir_edit, "Choose working directory")
        )
        layout.addLayout(self._build_field_block("Working directory", workdir_edit, trailing=workdir_browse))

        icon_edit = QLineEdit(self.icon_value)
        icon_edit.setPlaceholderText("Icon path or themed icon name")
        icon_browse = QPushButton("Browse")
        icon_browse.clicked.connect(lambda: self._dialog_pick_icon(icon_edit))
        layout.addLayout(self._build_field_block("Icon", icon_edit, trailing=icon_browse))

        categories_edit = QLineEdit(self.categories_value)
        categories_edit.setPlaceholderText("Utility;")
        layout.addLayout(self._build_field_block("Categories", categories_edit))

        option_shell = QFrame()
        option_shell.setObjectName("SoftCard")
        option_layout = QGridLayout(option_shell)
        option_layout.setContentsMargins(14, 14, 14, 14)
        option_layout.setHorizontalSpacing(10)
        option_layout.setVerticalSpacing(10)
        layout.addWidget(option_shell)

        terminal_button = self._make_chip_button("Run in terminal", self.terminal_value)
        desktop_button = self._make_chip_button("Copy launcher to desktop", self.desktop_icon_value)
        chmod_button = self._make_chip_button("Apply execute permission if required", self.chmod_target_value)
        sudo_button = self._make_chip_button("Run as sudo (pkexec)", self.sudo_value)
        option_layout.addWidget(terminal_button, 0, 0)
        option_layout.addWidget(desktop_button, 0, 1)
        option_layout.addWidget(chmod_button, 1, 0, 1, 2)
        option_layout.addWidget(sudo_button, 2, 0, 1, 2)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.args_value = args_edit.text().strip()
        self.workdir_value = workdir_edit.text().strip() or str(Path.home())
        self.icon_value = icon_edit.text().strip()
        self.categories_value = categories_edit.text().strip() or "Utility;"
        self.terminal_value = terminal_button.isChecked()
        self.desktop_icon_value = desktop_button.isChecked()
        self.chmod_target_value = chmod_button.isChecked()
        self.sudo_value = sudo_button.isChecked()
        self._update_advanced_summary()

    def _dialog_pick_directory(self, field: QLineEdit, title: str) -> None:
        selected = self._pick_directory(title, Path(field.text() or str(Path.home())))
        if selected is not None:
            field.setText(str(selected))

    def _dialog_pick_icon(self, field: QLineEdit) -> None:
        image_globs = " ".join(f"*{suffix}" for suffix in ICON_FILE_SUFFIXES)
        fallback = str(self.target_path) if self.target_path else str(Path.home())
        selected = self._pick_file(
            "Choose icon file",
            Path(field.text() or fallback),
            f"Images ({image_globs})",
        )
        if selected is not None:
            field.setText(str(selected))

    def _load_target(self, path: Path) -> None:
        self.target_path = path
        self.target_display.setText(str(path))
        self.launcher_name_edit.setText(title_from_path(path))
        self.workdir_value = str(path.parent)
        suggested_mode = default_mode_for_path(path)
        self._set_mode("auto")
        self.terminal_value = suggested_mode in {"bash", "python"}
        if not self.icon_value.strip():
            self.icon_value = default_icon_for_mode(suggested_mode)
        self._update_advanced_summary()
        self.status_label.setText(path.name)

    def _create_launcher(self) -> None:
        if self.target_path is None:
            self._show_error("Choose a target file with Browse or Pick from installed apps.")
            return
        target = self.target_path.expanduser()
        if not target.exists() or not target.is_file():
            self._show_error("The selected target no longer exists. Pick a new one.")
            return

        name = self.launcher_name_edit.text().strip()
        if not name:
            self._show_error("Give the launcher a name.")
            return

        workdir = Path(self.workdir_value.strip() or str(target.parent)).expanduser()
        if not workdir.exists() or not workdir.is_dir():
            self._show_error("Choose a valid working directory.")
            return

        icon_value = self.icon_value.strip()
        if icon_value:
            icon_path = Path(icon_value).expanduser()
            if "/" in icon_value or icon_value.startswith("."):
                if not icon_path.exists():
                    self._show_error("The icon file does not exist.")
                    return
                icon_value = str(icon_path)

        mode = self._selected_mode()
        if mode == "auto":
            mode = default_mode_for_path(target)

        if mode == "executable" and not is_executable(target) and not self.chmod_target_value:
            self._show_error("The target is not executable. Enable chmod or choose another launch mode.")
            return

        slug = slugify(name)
        existing_desktop = xdg_apps_dir() / f"{slug}.desktop"
        existing_helper = app_support_dir() / "launchers" / f"{slug}.sh"
        if existing_desktop.exists() or existing_helper.exists():
            replace = QMessageBox.question(
                self,
                APP_NAME,
                f"Launcher '{name}' already exists. Replace it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if replace != QMessageBox.StandardButton.Yes:
                return

        request = LauncherRequest(
            name=name,
            target=target,
            working_dir=workdir,
            arguments=self.args_value.strip(),
            icon=icon_value,
            categories=self.categories_value.strip(),
            mode=mode,
            terminal=self.terminal_value,
            add_desktop_icon=self.desktop_icon_value,
            chmod_target=self.chmod_target_value,
            sudo=self.sudo_value,
        )

        try:
            helper_path, desktop_path = create_launcher_files(request)
        except ValueError as exc:
            self._show_error(str(exc))
            return
        except Exception as exc:
            self._show_error(f"Failed to create launcher:\n{exc}")
            return

        self.status_label.setText("Launcher created.")
        self._show_info(
            "Launcher created.\n\n"
            f"Desktop entry: {desktop_path}\n"
            f"Helper script: {helper_path}"
        )

    def _reset_form(self) -> None:
        self.launcher_name_edit.clear()
        self.target_path = None
        self.target_display.setText("No target selected")
        self.args_value = ""
        self.workdir_value = str(Path.home())
        self.icon_value = ""
        self.categories_value = "Utility;"
        self._set_mode("auto")
        self.terminal_value = False
        self.desktop_icon_value = True
        self.chmod_target_value = True
        self.sudo_value = False
        self._update_advanced_summary()
        self.status_label.setText("Cleared.")

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._apply_responsive_layouts()


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE_SHEET)
    app.setFont(QFont("DejaVu Sans", 10))

    window = DeskLaunchWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
