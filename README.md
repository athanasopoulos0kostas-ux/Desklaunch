# DeskLaunch

DeskLaunch is a Linux launcher workspace for publishing local scripts, binaries, AppImages, and file handoff entries as polished desktop launchers.

It is designed to feel like a proper desktop product. The app gives you a controlled discovery workflow, a review step for the selected asset, and a clean publishing path into the Linux application menu.

## Core workflow

- scan a folder for `.sh` scripts, executables, AppImages, Python files, or any file
- pick a target and choose how it should launch
- generate a proper `.desktop` shortcut so it behaves like a normal app
- optionally drop a copy of that shortcut on the desktop

It is built with Python and PySide6 so the UI can feel like a current desktop app instead of a wrapped utility.

## What it supports

- Shell scripts: launch with `bash`
- Executables and AppImages: run directly
- Python scripts: launch with `python3`
- Any file: open with the default app through `xdg-open`

You can also override the launch mode manually inside the UI.

## Install on Linux

Requirements:

- `python3`
- `PySide6`

Install `PySide6` with your distro package manager or with pip:

```bash
python3 -m pip install --user PySide6
```

Install steps:

```bash
chmod +x install.sh
./install.sh
```

If you want the app itself copied to the desktop too:

```bash
./install.sh --desktop-icon
```

That installs:

- the app under `~/.local/share/desklaunch`
- a launcher command at `~/.local/bin/desklaunch`
- an app menu entry at `~/.local/share/applications/desklaunch.desktop`

## Build an AppImage

The project includes a Linux packaging script at `build-appimage.sh`.

Requirements:

- `python3`
- `python3-venv`
- either `curl` or `wget`

Build it like this:

```bash
chmod +x build-appimage.sh
./build-appimage.sh --clean --version 1.0.0
```

What the script does:

- creates a local virtual environment under `.build/venv`
- installs `PyInstaller` and `PySide6` into that environment
- builds a bundled Linux binary
- assembles an AppDir
- uses `appimagetool` to emit an `.AppImage`

Output:

- `dist-appimage/DeskLaunch-<version>-<arch>.AppImage`

Notes:

- If `appimagetool` is not already installed, the script downloads the official binary into `.build/tools`.
- To force a preinstalled `appimagetool`, use `./build-appimage.sh --no-download` or set `APPIMAGETOOL_BIN=/path/to/appimagetool`.
- Build on a Linux system that is close to your oldest supported distro if you want wider compatibility.

## Use it

1. Open `DeskLaunch` from your app menu.
2. Choose a source directory such as `/home/you`, `/opt`, or an external drive mount.
3. Filter for scripts, executables, AppImages, Python files, or any file.
4. Select the asset you want to publish.
5. Adjust the launcher name, arguments, working directory, icon, and launch mode.
6. Click `Publish launcher`.

Generated launchers are written to:

- `~/.local/share/applications`

Helper scripts are written to:

- `~/.local/share/desklaunch/launchers`

If `Add desktop icon copy` is enabled in the app, the generated `.desktop` file is also copied to your desktop directory.

## Remove it

```bash
chmod +x uninstall.sh
./uninstall.sh
```

## Notes

- Some desktop environments block launchers copied straight to the desktop until you mark them trusted. If that happens, right-click the desktop file and allow launching.
- For plain executables without the execute bit set, the app can add it for you.
- This project was created from a non-Linux environment, so the Linux packaging flow is set up but was not runtime-tested on a live Linux desktop from here.
