#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_IMAGE="${1:-$ROOT_DIR/icon.jpg}"
ICON_DIR="$ROOT_DIR/assets/icons"
ICONSET_DIR="$ICON_DIR/icon.iconset"

if [[ ! -f "$SOURCE_IMAGE" ]]; then
  echo "Source image not found: $SOURCE_IMAGE" >&2
  exit 1
fi

mkdir -p "$ICONSET_DIR"

sips -s format png -z 16 16 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null
sips -s format png -z 32 32 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null
sips -s format png -z 32 32 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null
sips -s format png -z 64 64 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null
sips -s format png -z 128 128 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null
sips -s format png -z 256 256 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null
sips -s format png -z 256 256 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_256x256.png" >/dev/null
sips -s format png -z 512 512 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_256x256@2x.png" >/dev/null
sips -s format png -z 512 512 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null
sips -s format png -z 1024 1024 "$SOURCE_IMAGE" --out "$ICONSET_DIR/icon_512x512@2x.png" >/dev/null

iconutil -c icns "$ICONSET_DIR" -o "$ICON_DIR/app_icon.icns"
cp "$SOURCE_IMAGE" "$ICON_DIR/app_icon.jpg"

echo "Generated: $ICON_DIR/app_icon.icns"
echo "Generated: $ICON_DIR/app_icon.jpg"
