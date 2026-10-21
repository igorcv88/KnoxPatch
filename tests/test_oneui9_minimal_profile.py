"""Contract tests for the opt-in One UI 9 minimal KnoxPatch LAB profile."""
import pathlib
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAIN = ROOT / "app/src/main/java/io/mesalabs/knoxpatch/MainHook.kt"
SCOPE = ROOT / "app/src/main/res/values/arrays.xml"

EXPECTED = {
    "com.samsung.android.kmxservice": "KNOX_MATRIX_SERVICE_PACKAGE_NAME, KnoxMatrixHooks",
    "com.osp.app.signin": "SAMSUNG_ACCOUNT_PACKAGE_NAME, SamsungKeystoreHooks",
    "com.samsung.android.app.sharelive": "QUICK_SHARE_PACKAGE_NAME, SamsungKeystoreHooks",
    "com.sec.android.app.shealth": "SAMSUNG_HEALTH_PACKAGE_NAME, KnoxSDKHooks",
}


class MinimalProfileContract(unittest.TestCase):
    def test_oneui9_returns_before_systemserver_hooks(self):
        src = MAIN.read_text(encoding="utf-8")
        first = src.index("if (sepVersion >= Constants.ONEUI_9_0) {")
        end = src.index("return@encase", first)
        system_hook = src.index("loadSystem(SystemHooks)")
        self.assertLess(first, end)
        self.assertLess(end, system_hook)
        minimal = src[first:end]
        self.assertNotIn("loadSystem", minimal)
        for target in EXPECTED.values():
            self.assertIn("loadApp(Constants." + target + ")", minimal)
        self.assertEqual(minimal.count("loadApp("), len(EXPECTED))
        self.assertIn("loadSystem(SystemHooks)", src[end:])
        self.assertIn("loadApp(Constants.SAMSUNG_HEALTH_MONITOR_PACKAGE_NAME, RootDetectionHooks)", src[end:])

    def test_default_scope_is_exactly_the_four_target_apps(self):
        tree = ET.parse(SCOPE)
        groups = tree.findall("./string-array")
        self.assertEqual(1, len(groups))
        self.assertEqual("scope", groups[0].attrib.get("name"))
        names = [item.text for item in groups[0].findall("item")]
        self.assertEqual(set(EXPECTED), set(names))
        self.assertEqual(len(names), len(EXPECTED))
        self.assertNotIn("android", names)
        self.assertFalse(any(v.startswith("com.google.") for v in names))


if __name__ == "__main__":
    unittest.main()
