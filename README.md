handwriting input for chinese characters
- input handwritten chinese characters
- OCR and present the suggested characters in confidence rank (if theres multiple)
- user selects with 1,2,3, etc. or click the character
- selected character gets inserted into the current cursor location the user is typing into (external word processor, email, etc.)
- q to estimate; e to erase

## Build standalone binaries (macOS, Linux, Windows)

This repo includes:
- `hw-chinese.spec` for PyInstaller
- `.github/workflows/build-binaries.yml` for GitHub Actions matrix builds

### Local build

Build on each target OS natively (do not cross-compile):

1. Create and activate a virtual environment
	 - macOS/Linux:
		 - `python3 -m venv .venv`
		 - `source .venv/bin/activate`
	 - Windows (PowerShell):
		 - `py -m venv .venv`
		 - `.venv\Scripts\Activate.ps1`

2. Install dependencies
	 - `python -m pip install --upgrade pip wheel setuptools`
	 - `pip install -r cpu-requirements.txt`
	 - `pip install pyinstaller`

3. Build
	 - (macOS, optional when changing icon image) regenerate icon assets:
		 - `chmod +x scripts/generate_icons_macos.sh`
		 - `./scripts/generate_icons_macos.sh icon.jpg`
	 - `pyinstaller --noconfirm --clean hw-chinese.spec`

4. Run built app/binary
	 - Output folder: `dist/hw-chinese/`
	 - macOS/Linux:
		 - `./dist/hw-chinese/hw-chinese`
	 - Windows:
		 - `dist\hw-chinese\hw-chinese.exe`

### CI build (all 3 OSes)

Push to `main` or trigger manually via GitHub Actions (`Build standalone binaries`).
Artifacts are uploaded per OS as:
- `hw-chinese-Linux`
- `hw-chinese-macOS`
- `hw-chinese-Windows`

On macOS runners, CI regenerates `assets/icons/app_icon.icns` and `assets/icons/app_icon.jpg` from `icon.jpg` before building so the packaged app icon stays in sync with the source image.

### Platform notes

- Linux runtime requires: `xdotool`, `xprop` (from `x11-utils`), and `xclip` or `xsel`.
- macOS may require Accessibility permissions for automation/paste behavior.
- Windows binary builds, but text insertion currently returns "not implemented yet" in `src/platform/windows_actions.py`.