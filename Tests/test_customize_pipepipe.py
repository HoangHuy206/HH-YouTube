import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "customize_pipepipe", ROOT / "Tools" / "customize_pipepipe.py"
)
CUSTOMIZE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = CUSTOMIZE
SPEC.loader.exec_module(CUSTOMIZE)


class CustomizePipePipeTests(unittest.TestCase):
    def test_customizes_manifest_smali_strings_and_icons(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            res = root / "resources" / "package_1" / "res"
            (res / "values").mkdir(parents=True)
            (res / "xml").mkdir(parents=True)
            (root / "smali" / "classes").mkdir(parents=True)

            (root / "AndroidManifest.xml").write_text(
                '<manifest package="InfinityLoop1309.NewPipeEnhanced" android:versionName="5.6.0">'
                '<provider android:authorities="InfinityLoop1309.NewPipeEnhanced.provider"/></manifest>',
                encoding="utf-8",
            )
            (root / "resources" / "package_1" / "package.json").write_text(
                json.dumps({"package_name": "InfinityLoop1309.NewPipeEnhanced"}),
                encoding="utf-8",
            )
            (root / "smali" / "classes" / "Sample.smali").write_text(
                'const-string v0, "InfinityLoop1309.NewPipeEnhanced.provider"\n',
                encoding="utf-8",
            )
            (res / "values" / "strings.xml").write_text(
                "<resources>"
                '<string name="app_name">PipePipe</string>'
                '<string name="default_theme_value">@string/auto_device_theme_key</string>'
                '<string name="default_night_theme_value">@string/dark_theme_key</string>'
                '<string name="default_resolution_value">720p</string>'
                "</resources>",
                encoding="utf-8",
            )
            (res / "values" / "colors.xml").write_text(
                '<resources><color name="ic_launcher_background">#cd201f</color></resources>',
                encoding="utf-8",
            )
            (res / "xml" / "update_settings.xml").write_text(
                '<PreferenceScreen><SwitchPreferenceCompat android:key="@string/update_app_key" android:defaultValue="true" /></PreferenceScreen>',
                encoding="utf-8",
            )

            stats = CUSTOMIZE.customize_decoded_tree(
                root, target_package="com.hoanghuy.hh", app_name="YouTube", hh_version="1.1.1"
            )
            self.assertEqual(stats["smali_files_updated"], 1)
            self.assertEqual(stats["icons_written"], 10)

            manifest = (root / "AndroidManifest.xml").read_text(encoding="utf-8")
            self.assertIn('package="com.hoanghuy.hh"', manifest)
            self.assertIn('android:authorities="com.hoanghuy.hh.provider"', manifest)
            self.assertIn('android:versionName="1.1.1"', manifest)

            strings = (res / "values" / "strings.xml").read_text(encoding="utf-8")
            self.assertIn('<string name="app_name">YouTube</string>', strings)
            self.assertIn("@string/black_theme_key", strings)
            self.assertIn(">1080p<", strings)

            update_xml = (res / "xml" / "update_settings.xml").read_text(encoding="utf-8")
            self.assertIn('android:defaultValue="false"', update_xml)

            icon_bytes = (res / "mipmap-xxxhdpi" / "ic_launcher.png").read_bytes()
            self.assertTrue(icon_bytes.startswith(b"\x89PNG\r\n\x1a\n"))


if __name__ == "__main__":
    unittest.main()
