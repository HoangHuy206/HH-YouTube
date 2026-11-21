#!/usr/bin/env python3
"""Verify structural integrity, signature presence, and HH patches of a built APK."""

from __future__ import annotations

import argparse
import pathlib
import struct
import sys
import zipfile


APK_SIG_BLOCK_MAGIC = b"APK Sig Block 42"
EOCD_MAGIC = b"PK\x05\x06"
REQUIRED_ENTRIES = ("AndroidManifest.xml", "resources.arsc", "classes.dex")


class APKVerificationError(RuntimeError):
    pass


def _manifest_contains_text(manifest_bytes: bytes, token: str) -> bool:
    utf8 = token.encode("utf-8")
    utf16 = token.encode("utf-16-le")
    return utf8 in manifest_bytes or utf16 in manifest_bytes


def _has_apk_signing_block(apk_path: pathlib.Path) -> bool:
    size = apk_path.stat().st_size
    if size < 38:
        return False
    with apk_path.open("rb") as handle:
        handle.seek(max(0, size - 65558))
        tail = handle.read()
        eocd_pos = tail.rfind(EOCD_MAGIC)
        if eocd_pos == -1 or eocd_pos + 20 > len(tail):
            return False
        cd_offset = struct.unpack_from("<I", tail, eocd_pos + 16)[0]
        if cd_offset < 16 or cd_offset > size:
            return False
        handle.seek(cd_offset - 16)
        return handle.read(16) == APK_SIG_BLOCK_MAGIC


def verify_apk(
    apk_path: pathlib.Path,
    expected_package: str = "com.hoanghuy.hh.youtube",
    require_arm64: bool = True,
    require_patches: bool = True,
) -> dict[str, object]:
    if not apk_path.is_file():
        raise APKVerificationError(f"APK file not found: {apk_path}")

    if not zipfile.is_zipfile(apk_path):
        raise APKVerificationError(f"Not a valid ZIP/APK archive: {apk_path}")

    with zipfile.ZipFile(apk_path, "r") as archive:
        names = set(archive.namelist())
        missing = [entry for entry in REQUIRED_ENTRIES if entry not in names]
        if missing:
            raise APKVerificationError(f"Missing required APK entries: {', '.join(missing)}")

        dex_files = sorted(
            name for name in names if name.startswith("classes") and name.endswith(".dex")
        )
        if not dex_files:
            raise APKVerificationError("No DEX bytecode files found in APK")

        arm64_libs = sorted(
            name for name in names if name.startswith("lib/arm64-v8a/") and name.endswith(".so")
        )
        if require_arm64 and not arm64_libs:
            raise APKVerificationError("No arm64-v8a native libraries found in APK")

        v1_sigs = [
            name
            for name in names
            if name.startswith("META-INF/")
            and name.upper().endswith((".RSA", ".DSA", ".EC"))
        ]
        v2_or_v3 = _has_apk_signing_block(apk_path)
        if not v1_sigs and not v2_or_v3:
            raise APKVerificationError("APK is unsigned (no v1 META-INF cert or APK Signing Block)")

        manifest_bytes = archive.read("AndroidManifest.xml")
        if expected_package and not _manifest_contains_text(manifest_bytes, expected_package):
            raise APKVerificationError(
                f"Expected package '{expected_package}' not found in AndroidManifest.xml"
            )

        if require_patches:
            patched_markers = any(
                "morphe" in name.lower() or "revanced" in name.lower() for name in names
            ) or _manifest_contains_text(manifest_bytes, "morphe_")
            if not patched_markers:
                raise APKVerificationError("Patched extension resources/aliases not detected in APK")

    return {
        "path": str(apk_path),
        "size_bytes": apk_path.stat().st_size,
        "dex_count": len(dex_files),
        "arm64_lib_count": len(arm64_libs),
        "signed_v2_v3": v2_or_v3,
        "signed_v1": bool(v1_sigs),
        "package": expected_package,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify built HH YouTube APK")
    parser.add_argument("apk", type=pathlib.Path, help="Path to the patched APK")
    parser.add_argument(
        "--package",
        default="com.hoanghuy.hh.youtube",
        help="Expected Android package name (empty string to skip check)",
    )
    parser.add_argument(
        "--no-arm64",
        action="store_true",
        help="Do not require lib/arm64-v8a/*.so entries",
    )
    parser.add_argument(
        "--no-patches",
        action="store_true",
        help="Do not require Morphe/RVX patch markers (e.g. for stock/companion APKs)",
    )
    args = parser.parse_args(argv)

    try:
        info = verify_apk(
            args.apk,
            expected_package=args.package,
            require_arm64=not args.no_arm64,
            require_patches=not args.no_patches,
        )
    except APKVerificationError as error:
        print(f"verification failed: {error}", file=sys.stderr)
        return 1

    print(
        f"verified: {info['path']} "
        f"(package={info['package']}, dex={info['dex_count']}, "
        f"arm64_libs={info['arm64_lib_count']}, size={info['size_bytes']} bytes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
