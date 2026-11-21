#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 2 ]]; then
  echo "usage: build-apk.sh [YouTube.apk|apk_url] [output.apk]" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MORPHE_CLI_VERSION="${MORPHE_CLI_VERSION:-2.3.0}"
RVX_PATCHES_VERSION="${RVX_PATCHES_VERSION:-4.3.0}"
DEFAULT_APK_URL="https://archive.org/download/jhc-apks/apks/com.google.android.youtube/com.google.android.youtube-21.13.164-all.apk"
GOOGLE_YT_CERT_SHA256="3d7a1223019aa39d9ea0e3436ab7c0896bfb4fb679f4de5fe7c23f326c8f994a"

INPUT_SOURCE="${1:-${APK_URL:-$DEFAULT_APK_URL}}"
OUTPUT_ARG="${2:-}"
APK_ARCHS="${APK_ARCHS:-arm64-v8a,armeabi-v7a}"
CACHE_DIR="${HH_APK_CACHE_DIR:-$ROOT/.build/apk-cache}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

JAVA_BIN="${JAVA_BIN:-java}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

command -v "$JAVA_BIN" >/dev/null 2>&1 || { echo "java (21+) is required" >&2; exit 1; }
command -v "$PYTHON_BIN" >/dev/null 2>&1 || { echo "python3 is required" >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "curl is required" >&2; exit 1; }

mkdir -p "$CACHE_DIR"

CLI_JAR="$CACHE_DIR/morphe-desktop-${MORPHE_CLI_VERSION}-all.jar"
PATCHES_MPP="$CACHE_DIR/patches-${RVX_PATCHES_VERSION}.mpp"

if [[ ! -f "$CLI_JAR" ]]; then
  echo "Downloading Morphe CLI v${MORPHE_CLI_VERSION}..." >&2
  curl --fail --location --silent --show-error \
    "https://github.com/MorpheApp/morphe-desktop/releases/download/v${MORPHE_CLI_VERSION}/morphe-desktop-${MORPHE_CLI_VERSION}-all.jar" \
    --output "$CLI_JAR.tmp"
  mv -f "$CLI_JAR.tmp" "$CLI_JAR"
fi

if [[ ! -f "$PATCHES_MPP" ]]; then
  echo "Downloading RVX patches v${RVX_PATCHES_VERSION}..." >&2
  curl --fail --location --silent --show-error \
    "https://github.com/anddea/revanced-patches/releases/download/v${RVX_PATCHES_VERSION}/patches-${RVX_PATCHES_VERSION}.mpp" \
    --output "$PATCHES_MPP.tmp"
  mv -f "$PATCHES_MPP.tmp" "$PATCHES_MPP"
fi

if [[ "$INPUT_SOURCE" =~ ^https?:// ]]; then
  STOCK_APK="$CACHE_DIR/$(basename "${INPUT_SOURCE%%\?*}")"
  if [[ "$STOCK_APK" != *.apk && "$STOCK_APK" != *.apkm && "$STOCK_APK" != *.xapk && "$STOCK_APK" != *.apks ]]; then
    STOCK_APK="$CACHE_DIR/YouTube-stock.apk"
  fi
  if [[ ! -f "$STOCK_APK" ]]; then
    echo "Downloading stock YouTube APK..." >&2
    if [[ -n "${GH_TOKEN:-}" && "$INPUT_SOURCE" == "https://api.github.com/repos/"* ]]; then
      curl --fail --location \
        --header "Accept: application/octet-stream" \
        --header "Authorization: Bearer $GH_TOKEN" \
        "$INPUT_SOURCE" --output "$STOCK_APK.tmp"
    else
      curl --fail --location "$INPUT_SOURCE" --output "$STOCK_APK.tmp"
    fi
    mv -f "$STOCK_APK.tmp" "$STOCK_APK"
  fi
else
  STOCK_APK="$INPUT_SOURCE"
  test -f "$STOCK_APK"
fi

if [[ "$STOCK_APK" == *.apk ]]; then
  if command -v apksigner >/dev/null 2>&1; then
    CERT_LINE="$(apksigner verify --print-certs "$STOCK_APK" | grep 'Signer #1 certificate SHA-256' || true)"
    if [[ -n "$CERT_LINE" && "${CERT_LINE,,}" != *"${GOOGLE_YT_CERT_SHA256,,}"* ]]; then
      echo "Stock APK SHA-256 certificate mismatch: $CERT_LINE" >&2
      exit 1
    fi
  elif command -v keytool >/dev/null 2>&1; then
    CERT_HEX="$(keytool -printcert -jarfile "$STOCK_APK" 2>/dev/null | awk '/SHA256:/ {gsub(/:/, "", $2); print tolower($2); exit}')"
    if [[ -n "$CERT_HEX" && "$CERT_HEX" != "$GOOGLE_YT_CERT_SHA256" ]]; then
      echo "Stock APK SHA-256 certificate mismatch: $CERT_HEX" >&2
      exit 1
    fi
  fi
fi

export MORPHE_DATA_DIR="${MORPHE_DATA_DIR:-$CACHE_DIR/morphe-data}"
mkdir -p "$MORPHE_DATA_DIR"

PATCHED_TMP="$WORK/HH_YouTube_patched.apk"
RESULT_JSON="$WORK/result.json"
OPTIONS_WORK="$WORK/options.json"
cp "$ROOT/Android/options.json" "$OPTIONS_WORK"

SIGN_ARGS=(--signer "${APK_SIGNER:-HH}")
if [[ -n "${APK_KEYSTORE:-}" ]]; then
  SIGN_ARGS+=(--keystore "$APK_KEYSTORE")
  if [[ -n "${APK_KEYSTORE_PASSWORD:-}" ]]; then
    SIGN_ARGS+=(--keystore-password "$APK_KEYSTORE_PASSWORD")
  fi
  if [[ -n "${APK_KEY_ALIAS:-}" ]]; then
    SIGN_ARGS+=(--keystore-entry-alias "$APK_KEY_ALIAS")
  fi
  if [[ -n "${APK_KEY_PASSWORD:-}" ]]; then
    SIGN_ARGS+=(--keystore-entry-password "$APK_KEY_PASSWORD")
  fi
fi

STRIP_ARGS=()
if [[ -n "$APK_ARCHS" && "$APK_ARCHS" != "all" ]]; then
  STRIP_ARGS+=(--striplibs "$APK_ARCHS")
fi

"$JAVA_BIN" --enable-native-access=ALL-UNNAMED -jar "$CLI_JAR" patch \
  --patches "$PATCHES_MPP" \
  --options-file "$OPTIONS_WORK" \
  --out "$PATCHED_TMP" \
  --result-file "$RESULT_JSON" \
  --temporary-files-path "$WORK/tmp" \
  --force \
  "${STRIP_ARGS[@]}" \
  "${SIGN_ARGS[@]}" \
  "$STOCK_APK" >&2

HH_VERSION="$(awk '/^Version:/ {print $2}' "$ROOT/control" | tr -d '\r')"
YT_VERSION="$(
  "$PYTHON_BIN" - "$RESULT_JSON" "$STOCK_APK" <<'PY'
import json
import pathlib
import re
import sys

result_path = pathlib.Path(sys.argv[1])
stock_name = pathlib.Path(sys.argv[2]).name
version = ""
if result_path.is_file():
    data = json.loads(result_path.read_text(encoding="utf-8"))
    for key in ("packageVersion", "version", "appVersion", "versionName"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            version = val.strip()
            break
if not version:
    match = re.search(r"(\d+\.\d+\.\d+)", stock_name)
    version = match.group(1) if match else "unknown"
print(version)
PY
)"

if [[ -n "$OUTPUT_ARG" ]]; then
  OUTPUT="$("$PYTHON_BIN" -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$OUTPUT_ARG")"
else
  OUTPUT="$PWD/HH_${HH_VERSION}_YouTube_${YT_VERSION}.apk"
fi

mkdir -p "$(dirname "$OUTPUT")"
mv -f "$PATCHED_TMP" "$OUTPUT"
rm -f "${OUTPUT}.idsig"

"$PYTHON_BIN" "$ROOT/Tools/verify_apk.py" "$OUTPUT" >&2
echo "$OUTPUT"
