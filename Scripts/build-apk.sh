#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 2 ]]; then
  echo "usage: build-apk.sh [output.apk] [arm64-v8a|armeabi-v7a]" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EDITION="${HH_APK_EDITION:-allinone}"
PIPEPIPE_VERSION="${PIPEPIPE_VERSION:-5.6.0}"
APKEDITOR_VERSION="${APKEDITOR_VERSION:-1.4.9}"
UBER_SIGNER_VERSION="${UBER_SIGNER_VERSION:-1.3.0}"
MORPHE_CLI_VERSION="${MORPHE_CLI_VERSION:-2.3.0}"
RVX_PATCHES_VERSION="${RVX_PATCHES_VERSION:-4.3.0}"

OUTPUT_ARG="${1:-}"
APK_ARCH="${2:-${APK_ARCH:-arm64-v8a}}"
CACHE_DIR="${HH_APK_CACHE_DIR:-$ROOT/.build/apk-cache}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

JAVA_BIN="${JAVA_BIN:-java}"
KEYTOOL_BIN="${KEYTOOL_BIN:-keytool}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

command -v "$JAVA_BIN" >/dev/null 2>&1 || { echo "java (21+) is required" >&2; exit 1; }
command -v "$PYTHON_BIN" >/dev/null 2>&1 || { echo "python3 is required" >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "curl is required" >&2; exit 1; }

mkdir -p "$CACHE_DIR"
HH_VERSION="$(awk '/^Version:/ {print $2}' "$ROOT/control" | tr -d '\r')"

if [[ "$EDITION" == "allinone" ]]; then
  BASE_APK="$CACHE_DIR/PipePipe_${PIPEPIPE_VERSION}-${APK_ARCH}-release.apk"
  APKEDITOR_JAR="$CACHE_DIR/APKEditor-${APKEDITOR_VERSION}.jar"
  SIGNER_JAR="$CACHE_DIR/uber-apk-signer-${UBER_SIGNER_VERSION}.jar"

  if [[ ! -f "$BASE_APK" ]]; then
    echo "Downloading PipePipe v${PIPEPIPE_VERSION} (${APK_ARCH})..." >&2
    curl --fail --location --silent --show-error \
      "https://github.com/InfinityLoop1308/PipePipe/releases/download/v${PIPEPIPE_VERSION}/PipePipe_${PIPEPIPE_VERSION}-${APK_ARCH}-release.apk" \
      --output "$BASE_APK.tmp"
    mv -f "$BASE_APK.tmp" "$BASE_APK"
  fi

  if [[ ! -f "$APKEDITOR_JAR" ]]; then
    echo "Downloading APKEditor v${APKEDITOR_VERSION}..." >&2
    curl --fail --location --silent --show-error \
      "https://github.com/REAndroid/APKEditor/releases/download/V${APKEDITOR_VERSION}/APKEditor-${APKEDITOR_VERSION}.jar" \
      --output "$APKEDITOR_JAR.tmp"
    mv -f "$APKEDITOR_JAR.tmp" "$APKEDITOR_JAR"
  fi

  if [[ ! -f "$SIGNER_JAR" ]]; then
    echo "Downloading uber-apk-signer v${UBER_SIGNER_VERSION}..." >&2
    curl --fail --location --silent --show-error \
      "https://github.com/patrickfav/uber-apk-signer/releases/download/v${UBER_SIGNER_VERSION}/uber-apk-signer-${UBER_SIGNER_VERSION}.jar" \
      --output "$SIGNER_JAR.tmp"
    mv -f "$SIGNER_JAR.tmp" "$SIGNER_JAR"
  fi

  DECODED_DIR="$WORK/decoded"
  UNSIGNED_APK="$WORK/HH_unsigned.apk"
  SIGNED_DIR="$WORK/signed"

  "$JAVA_BIN" -jar "$APKEDITOR_JAR" d -i "$BASE_APK" -o "$DECODED_DIR" -f >&2
  "$PYTHON_BIN" "$ROOT/Tools/customize_pipepipe.py" "$DECODED_DIR" \
    --package "com.hoanghuy.hh" \
    --name "YouTube" \
    --version "$HH_VERSION" >&2
  "$JAVA_BIN" -jar "$APKEDITOR_JAR" b -i "$DECODED_DIR" -o "$UNSIGNED_APK" -f >&2

  KEYSTORE="${APK_KEYSTORE:-$CACHE_DIR/hh-release.p12}"
  KS_PASS="${APK_KEYSTORE_PASSWORD:-hhyoutube}"
  KS_ALIAS="${APK_KEY_ALIAS:-hh}"
  KEY_PASS="${APK_KEY_PASSWORD:-$KS_PASS}"

  if [[ ! -f "$KEYSTORE" ]]; then
    "$KEYTOOL_BIN" -genkeypair -keystore "$KEYSTORE" -storetype PKCS12 \
      -alias "$KS_ALIAS" -keyalg RSA -keysize 2048 -validity 10000 \
      -storepass "$KS_PASS" -keypass "$KEY_PASS" \
      -dname "CN=HH, OU=Mobile, O=HoangHuy206, C=VN" >/dev/null 2>&1
  fi

  mkdir -p "$SIGNED_DIR"
  "$JAVA_BIN" -jar "$SIGNER_JAR" \
    --apks "$UNSIGNED_APK" \
    --out "$SIGNED_DIR" \
    --ks "$KEYSTORE" \
    --ksAlias "$KS_ALIAS" \
    --ksPass "$KS_PASS" \
    --ksKeyPass "$KEY_PASS" >&2

  SIGNED_APK="$(find "$SIGNED_DIR" -maxdepth 1 -name '*aligned*signed.apk' -print -quit)"
  test -n "$SIGNED_APK"

  if [[ -n "$OUTPUT_ARG" ]]; then
    OUTPUT="$("$PYTHON_BIN" -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$OUTPUT_ARG")"
  elif [[ "$APK_ARCH" == "arm64-v8a" ]]; then
    OUTPUT="$PWD/HH_${HH_VERSION}_YouTube.apk"
  else
    OUTPUT="$PWD/HH_${HH_VERSION}_YouTube_${APK_ARCH}.apk"
  fi

  mkdir -p "$(dirname "$OUTPUT")"
  mv -f "$SIGNED_APK" "$OUTPUT"

  VERIFY_FLAGS=(--package "com.hoanghuy.hh" --no-patches)
  if [[ "$APK_ARCH" != "arm64-v8a" ]]; then
    VERIFY_FLAGS+=(--no-arm64)
  fi
  "$PYTHON_BIN" "$ROOT/Tools/verify_apk.py" "${VERIFY_FLAGS[@]}" "$OUTPUT" >&2
  echo "$OUTPUT"
  exit 0
fi

# Optional RVX edition (stock YouTube APK + Morphe/RVX patches)
DEFAULT_APK_URL="https://archive.org/download/jhc-apks/apks/com.google.android.youtube/com.google.android.youtube-21.13.164-all.apk"
STOCK_URL="${APK_URL:-$DEFAULT_APK_URL}"
STOCK_APK="$CACHE_DIR/$(basename "${STOCK_URL%%\?*}")"
CLI_JAR="$CACHE_DIR/morphe-desktop-${MORPHE_CLI_VERSION}-all.jar"
PATCHES_MPP="$CACHE_DIR/patches-${RVX_PATCHES_VERSION}.mpp"

[[ -f "$CLI_JAR" ]] || curl --fail --location --silent --show-error \
  "https://github.com/MorpheApp/morphe-desktop/releases/download/v${MORPHE_CLI_VERSION}/morphe-desktop-${MORPHE_CLI_VERSION}-all.jar" \
  --output "$CLI_JAR"
[[ -f "$PATCHES_MPP" ]] || curl --fail --location --silent --show-error \
  "https://github.com/anddea/revanced-patches/releases/download/v${RVX_PATCHES_VERSION}/patches-${RVX_PATCHES_VERSION}.mpp" \
  --output "$PATCHES_MPP"
[[ -f "$STOCK_APK" ]] || curl --fail --location "$STOCK_URL" --output "$STOCK_APK"

export MORPHE_DATA_DIR="${MORPHE_DATA_DIR:-$CACHE_DIR/morphe-data}"
mkdir -p "$MORPHE_DATA_DIR"
PATCHED_TMP="$WORK/HH_RVX.apk"
OPTIONS_WORK="$WORK/options.json"
cp "$ROOT/Android/options.json" "$OPTIONS_WORK"

"$JAVA_BIN" --enable-native-access=ALL-UNNAMED -jar "$CLI_JAR" patch \
  --patches "$PATCHES_MPP" \
  --options-file "$OPTIONS_WORK" \
  --out "$PATCHED_TMP" \
  --temporary-files-path "$WORK/tmp" \
  --striplibs "arm64-v8a,armeabi-v7a" \
  --signer "HH" \
  --force \
  "$STOCK_APK" >&2

OUTPUT="${OUTPUT_ARG:-$PWD/HH_${HH_VERSION}_YouTube_RVX_21.13.164.apk}"
mkdir -p "$(dirname "$OUTPUT")"
mv -f "$PATCHED_TMP" "$OUTPUT"
rm -f "${OUTPUT}.idsig"
"$PYTHON_BIN" "$ROOT/Tools/verify_apk.py" "$OUTPUT" >&2
echo "$OUTPUT"
