# Chinese handwriting input helper

- Input handwritten Chinese characters.
- OCR returns ranked candidate characters.
- Select by number key or button.
- Selected character is inserted into the active external app.
- `q` to estimate, `e` to erase.

## Linux packaging: Option B (quick `.deb` with bundled venv)

This repo uses a Debian package flow.

### Build quick `.deb`

Run on Ubuntu/Debian:

1. Install packaging prerequisites:
   - `sudo apt-get update`
   - `sudo apt-get install -y dpkg-dev python3 python3-venv`

2. Build package:
   - `chmod +x scripts/build_deb_quick.sh`
   - `./scripts/build_deb_quick.sh 0.1.0 amd64`

3. Install package:
   - `sudo dpkg -i build-deb/hw-chinese_0.1.0_amd64.deb`

4. Launch app:
   - `hw-chinese`

### What gets installed

- App source: `/opt/hw-chinese/app`
- Bundled virtualenv: `/opt/hw-chinese/venv`
- Launcher: `/usr/bin/hw-chinese`
- Desktop entry: `/usr/share/applications/hw-chinese.desktop`

### Runtime Linux dependencies

Install if missing:

- `xdotool`
- `x11-utils`
- `xclip` or `xsel`

Example:

- `sudo apt-get install -y xdotool x11-utils xclip`

### CI

GitHub Actions now builds Debian artifacts with `.github/workflows/build-deb.yml` and uploads `build-deb/*.deb`.
