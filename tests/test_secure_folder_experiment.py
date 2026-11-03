"""Fail-closed source checks for the separate Secure Folder DZIF experiment."""
import pathlib
import unittest

from test_oneui9_minimal_profile import scopes

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = 'com.samsung.knox.securefolder'


class SecureFolderExperiment(unittest.TestCase):
    def test_all_resource_qualifiers_are_app_only(self):
        for sdk in (28, 29, 32, 33, 34, 36, 37, 38, 40):
            self.assertEqual({PACKAGE}, scopes('secureFolder', sdk))

    def test_companion_has_separate_application_id_and_build_flag(self):
        gradle = (ROOT/'app/build.gradle.kts').read_text()
        profile = gradle.split('create("secureFolder")', 1)[1].split('create("sepBasic")', 1)[0]
        self.assertIn('applicationIdSuffix = ".securefolderlab"', profile)
        self.assertIn('buildConfigField("boolean", "SECURE_FOLDER_EXPERIMENTAL", "true")', profile)
        for flavor in ('full', 'minimal'):
            flavor_config = gradle.split(f'create("{flavor}")',1)[1].split('manifestPlaceholders',1)[0]
            self.assertIn('buildConfigField("boolean", "SECURE_FOLDER_EXPERIMENTAL", "false")', flavor_config)

    def test_no_system_server_dispatch(self):
        main = (ROOT/'app/src/main/java/io/mesalabs/knoxpatch/MainHook.kt').read_text()
        begin = main.index('if (BuildConfig.SECURE_FOLDER_EXPERIMENTAL)')
        end = main.index('if (BuildConfig.MINIMAL_PROFILE)', begin)
        dispatch = main[begin:end]
        self.assertIn('Build.VERSION.SDK_INT != 37', dispatch)
        self.assertIn('sepVersion != Constants.ONEUI_9_0', dispatch)
        self.assertIn('loadApp(Constants.SECURE_FOLDER_PACKAGE_NAME, SecureFolderExperimentalHooks)', dispatch)
        self.assertEqual(1, dispatch.count('loadApp('))
        self.assertNotIn('loadSystem(', dispatch)
        self.assertIn('return@encase', dispatch)

    def test_only_dzif_welcome_gate_is_intercepted(self):
        hook = (ROOT/'app/src/main/java/io/mesalabs/knoxpatch/hooks/SecureFolderExperimentalHooks.kt').read_text()
        self.assertIn('provisioning.setup.viewmodel.WelcomeViewModel', hook)
        self.assertIn('name = "isCompromisedDevice"', hook)
        self.assertIn('emptyParameters()', hook)
        self.assertIn('returnType = Boolean::class', hook)
        self.assertIn('result = false', hook)
        for forbidden in ('SystemProperties', 'DarManagerService', 'replaceToTrue()', 'loadSystem(',
                          'KnoxGuard', 'ro.boot.warranty_bit'):
            self.assertNotIn(forbidden, hook)

    def test_experimental_workflow_signs_and_uploads_without_release(self):
        workflow = (ROOT/'.github/workflows/secure-folder-lab.yml').read_text()
        self.assertIn('workflow_dispatch:', workflow)
        self.assertIn('pull_request:', workflow)
        self.assertIn(':app:assembleSepBasicSecureFolderRelease', workflow)
        self.assertIn('KEYSTORE_BASE64', workflow)
        self.assertIn('apksigner', workflow)
        self.assertIn('verify_apk_profile.py', workflow)
        self.assertIn('actions/upload-artifact@', workflow)
        self.assertNotIn('gh release create', workflow)


if __name__ == '__main__':
    unittest.main()
