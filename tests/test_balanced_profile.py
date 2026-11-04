"""Balanced is exactly Minimal plus DZIF Secure Folder, without system hooks."""
import pathlib
import unittest

from test_oneui9_minimal_profile import EXPECTED as MINIMAL, scopes

ROOT = pathlib.Path(__file__).resolve().parents[1]
SECURE_FOLDER = 'com.samsung.knox.securefolder'


class BalancedProfile(unittest.TestCase):
    def test_every_resource_qualifier_overrides_full_with_five_apps(self):
        for sdk in (28, 29, 32, 33, 34, 36, 37, 38, 40):
            self.assertEqual(MINIMAL | {SECURE_FOLDER}, scopes('balanced', sdk))

    def test_balanced_reuses_primary_package_and_has_only_its_build_flag(self):
        gradle = (ROOT/'app/build.gradle.kts').read_text()
        balanced = gradle.split('create("balanced")', 1)[1].split('create("sepBasic")', 1)[0]
        self.assertIn('manifestPlaceholders["hookProfile"] = "Balanced"', balanced)
        self.assertIn('buildConfigField("boolean", "BALANCED_PROFILE", "true")', balanced)
        self.assertNotIn('applicationIdSuffix', balanced)
        self.assertNotIn('versionNameSuffix', balanced)
        self.assertNotIn('SECURE_FOLDER_EXPERIMENTAL', gradle)
        for profile in ('full', 'minimal'):
            flavor = gradle.split(f'create("{profile}")', 1)[1].split('manifestPlaceholders', 1)[0]
            self.assertIn('buildConfigField("boolean", "BALANCED_PROFILE", "false")', flavor)

    def test_balanced_loads_only_dzif_secure_folder_after_minimal_hooks(self):
        main = (ROOT/'app/src/main/java/io/mesalabs/knoxpatch/MainHook.kt').read_text()
        branch = main.split('if (BuildConfig.MINIMAL_PROFILE || BuildConfig.BALANCED_PROFILE)', 1)[1]
        branch = branch.split('loadSystem(SystemHooks)', 1)[0]
        self.assertIn('BuildConfig.BALANCED_PROFILE && Build.VERSION.SDK_INT != 37', branch)
        self.assertIn('loadApp(Constants.SECURE_FOLDER_PACKAGE_NAME, SecureFolderHooks)', branch)
        self.assertEqual(6, branch.count('loadApp('))
        self.assertNotIn('loadSystem(', branch)
        self.assertIn('return@encase', branch)

    def test_secure_folder_hook_is_app_local_and_fails_closed(self):
        hook = (ROOT/'app/src/main/java/io/mesalabs/knoxpatch/hooks/SecureFolderHooks.kt').read_text()
        self.assertIn('provisioning.setup.viewmodel.WelcomeViewModel', hook)
        self.assertIn('name = "isCompromisedDevice"', hook)
        self.assertIn('emptyParameters()', hook)
        self.assertIn('returnType = Boolean::class', hook)
        self.assertIn('result = false', hook)
        self.assertIn('if (viewModelClass == null)', hook)
        self.assertIn('if (check == null)', hook)
        for forbidden in ('SystemProperties', 'DarManagerService', 'replaceToTrue()', 'loadSystem(',
                          'KnoxGuard', 'ro.boot.warranty_bit'):
            self.assertNotIn(forbidden, hook)

    def test_lab_flavor_and_workflow_are_removed(self):
        self.assertFalse((ROOT/'.github/workflows/secure-folder-lab.yml').exists())
        self.assertFalse(any((ROOT/'app/src/secureFolder').rglob('*.xml')))
        self.assertFalse((ROOT/'app/src/main/java/io/mesalabs/knoxpatch/hooks/SecureFolderExperimentalHooks.kt').exists())

    def test_review_and_release_workflows_publish_balanced(self):
        release = (ROOT/'.github/workflows/release.yml').read_text()
        review = (ROOT/'.github/workflows/validate-oneui9-minimal.yml').read_text()
        self.assertIn('workflow_dispatch:', release)
        self.assertNotIn('pull_request:', release)
        for profile in ('Full', 'Balanced', 'Minimal'):
            task = f':app:assembleSepBasic{profile}Release'
            self.assertIn(task, release)
            self.assertIn(task, review)
            self.assertIn(f'"KnoxPatch-v${{VERSION_NAME}}-{profile}.apk"', release)
        self.assertIn('grep -Fqi "$EXPECTED_CERT"', release)
        self.assertIn('verify_apk_profile.py', release)


if __name__ == '__main__':
    unittest.main()
