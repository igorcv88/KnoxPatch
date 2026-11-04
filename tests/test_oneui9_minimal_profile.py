"""Source contracts. Compiled artifact verification is a separate mandatory CI gate."""
import importlib.util
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = {'com.samsung.android.kmxservice', 'com.osp.app.signin',
            'com.samsung.android.app.sharelive', 'com.sec.android.app.shealth'}


def scopes(profile, sdk):
    candidates = {}
    for source in ('main', profile):
        for f in (ROOT / 'app/src' / source / 'res').glob('values*/arrays.xml'):
            m = re.fullmatch(r'values(?:-v(\d+))?', f.parent.name)
            if m and int(m[1] or 0) <= sdk:
                candidates[int(m[1] or 0)] = f
    f = candidates[max(candidates)]
    return {e.text for e in ET.parse(f).findall("./string-array[@name='scope']/item")}


class Profiles(unittest.TestCase):
    def test_minimal_never_inherits_full_resource_on_api37(self):
        for sdk in (28,29,32,33,34,36,37,38,40):
            self.assertEqual(EXPECTED, scopes('minimal', sdk))

    def test_full_preserves_qualified_scopes(self):
        for sdk in (28,29,33,34,36,37,40):
            scope = scopes('full', sdk)
            self.assertIn('android', scope)
            self.assertGreater(len(scope), 4)
        self.assertIn('com.samsung.android.galaxycontinuity', scopes('full',37))
        self.assertIn('com.samsung.android.scloud', scopes('full',37))

    def test_build_profiles_are_independent_of_sep_libraries(self):
        s=(ROOT/'app/build.gradle.kts').read_text()
        self.assertIn('listOf("sepCategory", "hookProfile")',s)
        for value in ('true','false'):
            self.assertIn(f'buildConfigField("boolean", "MINIMAL_PROFILE", "{value}")',s)
        # All three release flavors must share package ID, version and signing.
        full=s.split('create("full")',1)[1].split('create("minimal")',1)[0]
        minimal=s.split('create("minimal")',1)[1].split('create("balanced")',1)[0]
        balanced=s.split('create("balanced")',1)[1].split('create("sepBasic")',1)[0]
        self.assertNotIn('applicationIdSuffix',full)
        self.assertNotIn('applicationIdSuffix',minimal)
        self.assertNotIn('applicationIdSuffix',balanced)
        self.assertNotIn('versionNameSuffix',balanced)
        self.assertIn('buildConfigField("boolean", "BALANCED_PROFILE", "true")',balanced)

    def test_minimal_dispatch_exits_before_system_and_full_keeps_original_calls(self):
        s=(ROOT/'app/src/main/java/io/mesalabs/knoxpatch/MainHook.kt').read_text()
        a=s.index('if (BuildConfig.MINIMAL_PROFILE || BuildConfig.BALANCED_PROFILE)')
        b=s.index('loadSystem(SystemHooks)')
        branch=s[a:b]
        self.assertIn('return@encase',branch)
        self.assertEqual(6,branch.count('loadApp('))
        self.assertIn('KNOX_MATRIX_SERVICE_PACKAGE_NAME, SamsungKeystoreHooks',branch)
        self.assertIn('if (BuildConfig.BALANCED_PROFILE)',branch)
        self.assertIn('SECURE_FOLDER_PACKAGE_NAME, SecureFolderHooks',branch)
        self.assertNotIn('loadSystem(',branch)
        self.assertNotIn('if (sepVersion >= Constants.ONEUI_9_0)', s)
        self.assertIn('SAMSUNG_HEALTH_MONITOR_PACKAGE_NAME, RootDetectionHooks',s[b:])

    def test_release_is_manual_three_sepBasic_assets(self):
        s=(ROOT/'.github/workflows/release.yml').read_text()
        self.assertIn('workflow_dispatch:',s)
        self.assertNotIn('pull_request:',s)
        self.assertNotIn('  push:',s)
        self.assertIn(':app:assembleSepBasicFullRelease',s)
        self.assertIn(':app:assembleSepBasicBalancedRelease',s)
        self.assertIn(':app:assembleSepBasicMinimalRelease',s)
        self.assertNotIn('assembleRelease ',s)
        self.assertNotIn('ENHANCER_ASSET',s)
        self.assertNotIn('LITE_ASSET',s)
        self.assertIn('grep -Fqi "$EXPECTED_CERT"',s)
        self.assertIn('"KnoxPatch-v${VERSION_NAME}-Balanced.apk"',s)
        self.assertIn('verify_apk_profile.py',s)

    def test_scope_dump_parser_checks_every_configuration(self):
        spec=importlib.util.spec_from_file_location('verifier',ROOT/'tools/verify_apk_profile.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        fixture='''resource 0x7f030001 array/scope
          () (array) size=1
            [0] (string8) "com.whatsapp"
          (v37) (array) size=1
            [0] (string8) "android"
        resource 0x7f030002 array/other
          () (array) size=1
            [0] (string8) "ignored"
        '''
        self.assertEqual([{'com.whatsapp'},{'android'}],m.scope_configs(fixture))
        self.assertEqual([{'com.whatsapp'},{'android'}],m.scope_configs(fixture.replace('array/scope','array/renamed'),0x7f030001))
        with self.assertRaises(AssertionError):m.scope_configs(fixture,0x7f030099)
        with self.assertRaises(AssertionError):m.scope_configs('missing')


if __name__=='__main__':unittest.main()
