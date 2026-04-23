# MousePet Desktop Pet

A lightweight Windows desktop pet built with Python and PySide6. The cat follows the mouse cursor smoothly, plays walking and sitting animations, and stays always on top with a transparent click-through window.

## Features

- Transparent, borderless, always-on-top window
- Click-through window so it does not block desktop interaction
- Smooth eased movement toward the mouse
- State-based animation: idle, walk, sit
- Simple bounce effect when stopping
- Runtime-generated cat sprite frames stored under `assets/cat/`
- Custom app icon support via `assets/app_icon.png` and `assets/app_icon.ico`

## Requirements

- Python 3.11+
- PySide6
- PyInstaller (for packaging)

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

## Build

Run one of the build scripts to create a Windows executable:

PowerShell:

```powershell
.\build.ps1
```

Command Prompt:

```cmd
build.bat
```

This will install `pyinstaller`, generate the app icon assets if needed, and produce `dist\main.exe`.

## Custom Icon

Place a custom icon image in `assets/app_icon.png` and run `python create_assets.py` to generate `.ico` support.

For the executable, replace or copy your own icon to `assets/app_icon.ico` and then rerun the build script.

## Project Structure

- `main.py` — application entry point
- `src/pet.py` — pet behavior and window logic
- `src/animation.py` — animation playback
- `src/config.py` — tuning constants and paths
- `assets/cat/` — generated cat animation frames
