"""Contract tests for the minimal One UI 9 KnoxPatch LAB profile.

Android resources use highest matching values-vN qualifiers; on API 37, a
values-v34 array overrides an unqualified values/arrays.xml file.
"""
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAIN = ROOT / "app/src/main/java/io/mesalabs/knoxpatch/MainHook.kt"
RES = ROOT / "app/src/main/res"

EXPECTED = {
    "com.samsung.android.kmxservice": "KNOX_MATRIX_SERVICE_PACKAGE_NAME, KnoxMatrixHooks",
    "com.osp.app.signin": "SAMSUNG_ACCOUNT_PACKAGE_NAME, SamsungKeystoreHooks",
    "com.samsung.android.app.sharelive": "QUICK_SHARE_PACKAGE_NAME, SamsungKeystoreHooks",
    "com.sec.android.app.shealth": "SAMSUNG_HEALTH_PACKAGE_NAME, KnoxSDKHooks",
}


def effective_scope_for_sdk(sdk):
    """Select the highest matching API-qualified arrays.xml from this source set."""
    options = []
    for path in RES.iterdir():
        if not path.is_dir():
            continue
        qualifier = re.fullmatch(r"values(?:-v(\d+))?", path.name)
        if not qualifier:
            continue
        min_api = int(qualifier.group(1)) if qualifier.group(1) else 0
        file = path / "arrays.xml"
        if file.is_file() and min_api <= sdk:
            options.append((min_api, file))
    if not options:
        raise AssertionError(f"No scope resource for API {sdk}")
    _, selected = max(options)
    root = ET.parse(selected).getroot()
    arrays = [e for e in root.findall("string-array") if e.attrib.get("name") == "scope"]
    if len(arrays) != 1:
        raise AssertionError(f"Expected exactly one scope resource in {selected}")
    values = [e.text for e in arrays[0].findall("item")]
    if len(values) != len(set(values)):
        raise AssertionError(f"Duplicate package in {selected}")
    return values, selected


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

    def test_android17_resolves_exactly_four_app_scopes(self):
        for sdk in (37, 38, 40):
            with self.subTest(sdk=sdk):
                values, selected = effective_scope_for_sdk(sdk)
                self.assertEqual(RES / "values-v37" / "arrays.xml", selected)
                self.assertEqual(set(EXPECTED), set(values))
                self.assertEqual(len(EXPECTED), len(values))
                self.assertNotIn("android", values)
                self.assertFalse(any(v.startswith("com.google.") for v in values))

    def test_older_android_keeps_upstream_qualified_scopes(self):
        for sdk, expected_qualifier in [(28, "values"), (29, "values-v29"),
                                         (32, "values-v29"), (33, "values-v33"),
                                         (34, "values-v34"), (35, "values-v34"),
                                         (36, "values-v34")]:
            with self.subTest(sdk=sdk):
                values, selected = effective_scope_for_sdk(sdk)
                self.assertEqual(expected_qualifier, selected.parent.name)
                self.assertIn("android", values)
                self.assertGreater(len(values), len(EXPECTED))

    def test_all_scope_resources_are_well_formed(self):
        for folder in RES.iterdir():
            file = folder / "arrays.xml"
            if folder.is_dir() and folder.name.startswith("values") and file.is_file():
                with self.subTest(path=str(file)):
                    items = ET.parse(file).findall("./string-array")
                    self.assertEqual(1, len(items))
                    self.assertEqual("scope", items[0].attrib.get("name"))


if __name__ == "__main__":
    unittest.main()
