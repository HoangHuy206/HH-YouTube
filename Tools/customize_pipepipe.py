#!/usr/bin/env python3
"""Customize a decoded PipePipe tree into the single-APK HH YouTube Android client."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import struct
import zlib


UPSTREAM_PACKAGE = "InfinityLoop1309.NewPipeEnhanced"
DEFAULT_TARGET_PACKAGE = "com.hoanghuy.hh"
DEFAULT_APP_NAME = "YouTube"

LAUNCHER_SIZES = {
    "mipmap-mdpi": (48, 108),
    "mipmap-hdpi": (72, 162),
    "mipmap-xhdpi": (96, 216),
    "mipmap-xxhdpi": (144, 324),
    "mipmap-xxxhdpi": (192, 432),
}

MONOCHROME_VECTOR_XML = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#FFFFFFFF"
        android:fillType="evenOdd"
        android:pathData="M38,36h32c5,0 9,4 9,9v18c0,5 -4,9 -9,9H38c-5,0 -9,-4 -9,-9V45c0,-5 4,-9 9,-9zM48,46v16l14,-8z" />
</vector>
"""


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def _encode_rgba_png(width: int, height: int, rows: list[bytes]) -> bytes:
    raw = b"".join(b"\x00" + row for row in rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(raw, level=9))
        + _png_chunk(b"IEND", b"")
    )


def _inside_rounded_rect(
    x: float, y: float, x0: float, y0: float, x1: float, y1: float, r: float
) -> bool:
    if x < x0 or x > x1 or y < y0 or y > y1:
        return False
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def _inside_play_triangle(
    x: float, y: float, left_x: float, right_x: float, half_h: float
) -> bool:
    """Centered horizontal play triangle pointing right from (left_x, 0.5+-half_h) to (right_x, 0.5)."""
    if x < left_x or x > right_x:
        return False
    progress = (right_x - x) / (right_x - left_x)
    max_dy = half_h * progress
    return abs(y - 0.5) <= max_dy


def render_youtube_icon_png(size: int, adaptive_foreground: bool) -> bytes:
    """Render a crisp anti-aliased YouTube-style play-badge PNG (4x4 supersampled)."""
    rows: list[bytes] = []
    if adaptive_foreground:
        # Fits cleanly inside Android 108dp adaptive icon 66dp safe zone
        bx0, bx1 = 0.27, 0.73
        by0, by1 = 0.338, 0.662
        br = 0.085
        tri_left, tri_right, tri_half_h = 0.445, 0.585, 0.082
    else:
        # Legacy launcher icon: white squircle plate + red play badge
        bx0, bx1 = 0.16, 0.84
        by0, by1 = 0.26, 0.74
        br = 0.125
        tri_left, tri_right, tri_half_h = 0.42, 0.625, 0.122

    offsets = (0.125, 0.375, 0.625, 0.875)
    inv_samples = 1.0 / 16.0

    for py in range(size):
        row = bytearray(size * 4)
        for px in range(size):
            r_acc = g_acc = b_acc = a_acc = 0.0
            for sy in offsets:
                ny = (py + sy) / size
                for sx in offsets:
                    nx = (px + sx) / size
                    if _inside_play_triangle(nx, ny, tri_left, tri_right, tri_half_h):
                        r_acc += 255.0
                        g_acc += 255.0
                        b_acc += 255.0
                        a_acc += 255.0
                    elif _inside_rounded_rect(nx, ny, bx0, by0, bx1, by1, br):
                        # YouTube vivid red (#FF0033 / #FF0000)
                        r_acc += 255.0
                        g_acc += 0.0
                        b_acc += 0.0
                        a_acc += 255.0
                    elif not adaptive_foreground and _inside_rounded_rect(
                        nx, ny, 0.03, 0.03, 0.97, 0.97, 0.22
                    ):
                        # Clean white launcher plate (#FFFFFF)
                        r_acc += 255.0
                        g_acc += 255.0
                        b_acc += 255.0
                        a_acc += 255.0
            idx = px * 4
            row[idx] = int(r_acc * inv_samples + 0.5)
            row[idx + 1] = int(g_acc * inv_samples + 0.5)
            row[idx + 2] = int(b_acc * inv_samples + 0.5)
            row[idx + 3] = int(a_acc * inv_samples + 0.5)
        rows.append(bytes(row))
    return _encode_rgba_png(size, size, rows)


def _replace_string_tag(xml_text: str, name: str, new_value: str) -> str:
    pattern = re.compile(rf'(<string\s+name="{re.escape(name)}"[^>]*>)(.*?)(</string>)', re.S)
    updated, count = pattern.subn(rf"\g<1>{new_value}\g<3>", xml_text)
    if count == 0:
        raise RuntimeError(f'Missing <string name="{name}"> in strings.xml')
    return updated


def customize_decoded_tree(
    decoded_dir: pathlib.Path,
    target_package: str = DEFAULT_TARGET_PACKAGE,
    app_name: str = DEFAULT_APP_NAME,
    hh_version: str = "1.1.1",
) -> dict[str, int]:
    manifest_path = decoded_dir / "AndroidManifest.xml"
    pkg_json_path = decoded_dir / "resources" / "package_1" / "package.json"
    res_dir = decoded_dir / "resources" / "package_1" / "res"

    if not manifest_path.is_file() or not res_dir.is_dir():
        raise RuntimeError(f"Invalid APKEditor decoded directory: {decoded_dir}")

    # 1. Update AndroidManifest.xml package, authorities, and versionName
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_text = manifest_text.replace(UPSTREAM_PACKAGE, target_package)
    manifest_text = re.sub(
        r'android:versionName="([^"]+)"',
        f'android:versionName="{hh_version}"',
        manifest_text,
        count=1,
    )
    manifest_path.write_text(manifest_text, encoding="utf-8")

    # 2. Update ARSCLib package.json
    if pkg_json_path.is_file():
        pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8"))
        pkg_data["package_name"] = target_package
        pkg_json_path.write_text(json.dumps(pkg_data, indent=2), encoding="utf-8")

    # 3. Update smali string constants referencing upstream applicationId/authorities/actions
    smali_touched = 0
    smali_root = decoded_dir / "smali"
    if smali_root.is_dir():
        for smali_file in smali_root.rglob("*.smali"):
            content = smali_file.read_text(encoding="utf-8")
            if UPSTREAM_PACKAGE in content:
                smali_file.write_text(
                    content.replace(UPSTREAM_PACKAGE, target_package),
                    encoding="utf-8",
                )
                smali_touched += 1

    # 4. Update app_name ("YouTube") and optimal defaults in values/strings.xml
    strings_path = res_dir / "values" / "strings.xml"
    strings_text = strings_path.read_text(encoding="utf-8")
    strings_text = _replace_string_tag(strings_text, "app_name", app_name)
    strings_text = _replace_string_tag(strings_text, "default_theme_value", "@string/black_theme_key")
    strings_text = _replace_string_tag(strings_text, "default_night_theme_value", "@string/black_theme_key")
    strings_text = _replace_string_tag(strings_text, "default_resolution_value", "1080p")
    strings_path.write_text(strings_text, encoding="utf-8")

    # 5. Disable upstream auto-update checks by default so it won't prompt incompatible APK updates
    update_xml_path = res_dir / "xml" / "update_settings.xml"
    if update_xml_path.is_file():
        update_xml = update_xml_path.read_text(encoding="utf-8")
        update_xml = re.sub(
            r'(<SwitchPreferenceCompat[^>]*android:key="@string/update_app_key"[^>]*android:defaultValue=")true(")',
            r"\g<1>false\g<2>",
            update_xml,
            flags=re.S,
        )
        update_xml_path.write_text(update_xml, encoding="utf-8")

    # 6. Set white YouTube adaptive launcher background (#FFFFFF) & render YouTube play-badge icons
    colors_path = res_dir / "values" / "colors.xml"
    if colors_path.is_file():
        colors_text = colors_path.read_text(encoding="utf-8")
        colors_text = re.sub(
            r'(<color\s+name="ic_launcher_background">).*?(</color>)',
            r"\g<1>#ffffff\g<2>",
            colors_text,
        )
        colors_path.write_text(colors_text, encoding="utf-8")

    icons_written = 0
    for folder_name, (legacy_px, adaptive_px) in LAUNCHER_SIZES.items():
        folder = res_dir / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "ic_launcher.png").write_bytes(
            render_youtube_icon_png(legacy_px, adaptive_foreground=False)
        )
        (folder / "ic_launcher_foreground.png").write_bytes(
            render_youtube_icon_png(adaptive_px, adaptive_foreground=True)
        )
        icons_written += 2

    mono_candidates = list(res_dir.rglob("ic_launcher_monochrome.xml"))
    if mono_candidates:
        for mono_path in mono_candidates:
            mono_path.write_text(MONOCHROME_VECTOR_XML, encoding="utf-8")
    else:
        drawable_dir = res_dir / "drawable"
        drawable_dir.mkdir(parents=True, exist_ok=True)
        (drawable_dir / "ic_launcher_monochrome.xml").write_text(
            MONOCHROME_VECTOR_XML, encoding="utf-8"
        )

    return {"smali_files_updated": smali_touched, "icons_written": icons_written}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Customize decoded PipePipe into YouTube APK")
    parser.add_argument("decoded_dir", type=pathlib.Path)
    parser.add_argument("--package", default=DEFAULT_TARGET_PACKAGE)
    parser.add_argument("--name", default=DEFAULT_APP_NAME)
    parser.add_argument("--version", default="1.1.1")
    args = parser.parse_args(argv)

    stats = customize_decoded_tree(
        args.decoded_dir,
        target_package=args.package,
        app_name=args.name,
        hh_version=args.version,
    )
    print(
        f"customized APK tree: package={args.package}, name={args.name}, "
        f"smali_updated={stats['smali_files_updated']}, icons={stats['icons_written']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
