import importlib.util
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_apk", ROOT / "Tools" / "verify_apk.py"
)
VERIFY_APK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = VERIFY_APK
SPEC.loader.exec_module(VERIFY_APK)


def build_fixture_apk(
    path: pathlib.Path,
    package: str = "com.hoanghuy.hh.youtube",
    signed: bool = True,
    arm64: bool = True,
    patched: bool = True,
) -> None:
    manifest = b"AXML\x00\x00" + package.encode("utf-16-le")
    if patched:
        manifest += b".morphe_youtube_black_5".decode("ascii").encode("utf-16-le")
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("AndroidManifest.xml", manifest)
        archive.writestr("resources.arsc", b"ARSC")
        archive.writestr("classes.dex", b"dex\n039\x00")
        if arm64:
            archive.writestr("lib/arm64-v8a/libcronet.so", b"\x7fELF")
        if patched:
            archive.writestr("res/layout/morphe_icon_list_item.xml", b"<LinearLayout/>")
        if signed:
            archive.writestr("META-INF/CERT.RSA", b"PKCS7")


class VerifyAPKTests(unittest.TestCase):
    def test_accepts_valid_patched_apk(self):
        with tempfile.TemporaryDirectory() as directory:
            apk = pathlib.Path(directory) / "HH_1.1.1_YouTube.apk"
            build_fixture_apk(apk)
            result = VERIFY_APK.verify_apk(apk)
            self.assertEqual(result["dex_count"], 1)
            self.assertEqual(result["arm64_lib_count"], 1)
            self.assertTrue(result["signed_v1"])

    def test_accepts_v2_signing_block_without_v1(self):
        with tempfile.TemporaryDirectory() as directory:
            apk = pathlib.Path(directory) / "v2_only.apk"
            build_fixture_apk(apk, signed=False)
            raw = apk.read_bytes()
            eocd = raw.rfind(b"PK\x05\x06")
            cd_offset = struct.unpack_from("<I", raw, eocd + 16)[0]
            sig_block = b"\x18\x00\x00\x00\x00\x00\x00\x00" + b"APK Sig Block 42"
            new_eocd = bytearray(raw[eocd:])
            struct.pack_into("<I", new_eocd, 16, cd_offset + len(sig_block))
            rebuilt = raw[:cd_offset] + sig_block + raw[cd_offset:eocd] + bytes(new_eocd)
            apk.write_bytes(rebuilt)
            result = VERIFY_APK.verify_apk(apk)
            self.assertTrue(result["signed_v2_v3"])
            self.assertFalse(result["signed_v1"])

    def test_rejects_unsigned_apk(self):
        with tempfile.TemporaryDirectory() as directory:
            apk = pathlib.Path(directory) / "unsigned.apk"
            build_fixture_apk(apk, signed=False)
            with self.assertRaises(VERIFY_APK.APKVerificationError):
                VERIFY_APK.verify_apk(apk)

    def test_rejects_wrong_package(self):
        with tempfile.TemporaryDirectory() as directory:
            apk = pathlib.Path(directory) / "wrong_pkg.apk"
            build_fixture_apk(apk, package="com.google.android.youtube")
            with self.assertRaises(VERIFY_APK.APKVerificationError):
                VERIFY_APK.verify_apk(apk)

    def test_rejects_unpatched_apk(self):
        with tempfile.TemporaryDirectory() as directory:
            apk = pathlib.Path(directory) / "stock.apk"
            build_fixture_apk(apk, patched=False)
            with self.assertRaises(VERIFY_APK.APKVerificationError):
                VERIFY_APK.verify_apk(apk)


if __name__ == "__main__":
    unittest.main()
