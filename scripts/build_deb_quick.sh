#!/usr/bin/env bash
set -euo pipefail

APP_NAME="hw-chinese"
VERSION="${1:-0.1.0}"
ARCH="${2:-amd64}"
ACCELERATOR="${3:-none}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_ROOT="$ROOT_DIR/build-deb"
PKG_ROOT="$BUILD_ROOT/${APP_NAME}_${VERSION}_${ARCH}"
APP_INSTALL_DIR="$PKG_ROOT/opt/$APP_NAME/app"
VENV_INSTALL_DIR="$PKG_ROOT/opt/$APP_NAME/venv"
DEBIAN_DIR="$PKG_ROOT/DEBIAN"

if ! command -v dpkg-deb >/dev/null 2>&1; then
  echo "dpkg-deb is required. Install dpkg first." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required." >&2
  exit 1
fi

rm -rf "$PKG_ROOT"
mkdir -p "$APP_INSTALL_DIR" "$VENV_INSTALL_DIR" "$DEBIAN_DIR" "$PKG_ROOT/usr/bin" "$PKG_ROOT/usr/share/applications"

cd "$ROOT_DIR"

# Copy source tree while excluding build artifacts and local envs.
tar \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='.venv' \
  --exclude='build' \
  --exclude='dist' \
  --exclude='build-deb' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  -cf - . | tar -xf - -C "$APP_INSTALL_DIR"

python3 -m venv --copies "$VENV_INSTALL_DIR"
"$VENV_INSTALL_DIR/bin/pip" install --upgrade pip wheel setuptools
if [[ "$ACCELERATOR" == "gpu" ]]; then
  "$VENV_INSTALL_DIR/bin/pip" install -r "$APP_INSTALL_DIR/gpu-requirements.txt"
else
  "$VENV_INSTALL_DIR/bin/pip" install -r "$APP_INSTALL_DIR/cpu-requirements.txt"
fi
"$VENV_INSTALL_DIR/bin/pip" install -r "$APP_INSTALL_DIR/requirements.txt"

cat > "$DEBIAN_DIR/control" <<EOF
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: hw-chinese maintainers <maintainers@example.com>
Depends: xdotool, x11-utils, xclip | xsel
Description: Chinese handwriting input helper
 OCR handwriting helper with ranked candidate selection and text insertion.
EOF

cat > "$DEBIAN_DIR/postinst" <<'EOF'
#!/usr/bin/env bash
set -e

missing=0

if ! command -v xdotool >/dev/null 2>&1; then
  echo "[hw-chinese] WARNING: xdotool is missing. Install: sudo apt-get install -y xdotool" >&2
  missing=1
fi

if ! command -v xprop >/dev/null 2>&1; then
  echo "[hw-chinese] WARNING: xprop is missing. Install: sudo apt-get install -y x11-utils" >&2
  missing=1
fi

if ! command -v xclip >/dev/null 2>&1 && ! command -v xsel >/dev/null 2>&1; then
  echo "[hw-chinese] WARNING: xclip/xsel missing. Install one: sudo apt-get install -y xclip" >&2
  missing=1
fi

if [[ "$missing" -eq 1 ]]; then
  echo "[hw-chinese] Some optional runtime tools appear missing; text insertion may fail until installed." >&2
fi

exit 0
EOF

cat > "$PKG_ROOT/usr/bin/$APP_NAME" <<'EOF'
#!/usr/bin/env bash
exec /opt/hw-chinese/venv/bin/python /opt/hw-chinese/app/main.py "$@"
EOF

cat > "$PKG_ROOT/usr/share/applications/$APP_NAME.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=hw-chinese
Comment=Chinese handwriting input helper
Exec=hw-chinese
Icon=/opt/hw-chinese/app/icon.jpg
Terminal=false
Categories=Utility;
EOF

chmod 0755 "$PKG_ROOT/usr/bin/$APP_NAME"
chmod 0755 "$DEBIAN_DIR/postinst"
chmod 0644 "$DEBIAN_DIR/control" "$PKG_ROOT/usr/share/applications/$APP_NAME.desktop"

OUTPUT_DEB="$BUILD_ROOT/${APP_NAME}_${VERSION}_${ARCH}.deb"
mkdir -p "$BUILD_ROOT"
rm -f "$OUTPUT_DEB"
dpkg-deb --build "$PKG_ROOT" "$OUTPUT_DEB"

echo "Built package: $OUTPUT_DEB"
echo "Install with: sudo dpkg -i $OUTPUT_DEB"
