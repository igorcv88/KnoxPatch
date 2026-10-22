<p align="center">
  <img loading="lazy" src="readme-res/kp-readme-header.png" width="75%"/>
  <br>
  <a href="https://apt.izzysoft.de/fdroid/index/apk/io.mesalabs.knoxpatch"><img loading="lazy" src="https://gitlab.com/IzzyOnDroid/repo/-/raw/master/assets/IzzyOnDroid.png" width="170"/></a>
  <br>
  <a href="https://github.com/igorcv88/KnoxPatch/releases/latest"><img loading="lazy" src="https://img.shields.io/github/v/release/igorcv88/KnoxPatch?style=flat-square"/></a>
  <img loading="lazy" src="https://img.shields.io/github/repo-size/igorcv88/KnoxPatch?style=flat-square"/>
  <a href="https://github.com/igorcv88/KnoxPatch/commits/main"><img loading="lazy" src="https://img.shields.io/github/last-commit/igorcv88/KnoxPatch/main?style=flat-square"/></a>
  <a href="https://github.com/igorcv88/KnoxPatch/actions"><img loading="lazy" src="https://img.shields.io/github/actions/workflow/status/igorcv88/KnoxPatch/android.yml?style=flat-square"/></a>
  <br><br>
  An <a href="https://github.com/LSPosed/LSPosed">LSPosed</a> module to get Samsung apps/features working again in your rooted Galaxy device.
  <br><br>
  Fork maintained with One UI 9 / Android 17 compatibility.
  <br>
</p>

## Supported Android versions
- Android 9 (One UI 1.x)
- Android 10 (One UI 2.x)
- Android 11 (One UI 3.x)
- Android 12 (One UI 4.x)
- Android 12L (One UI 4.1.1)
- Android 13 (One UI 5.x)
- Android 14 (One UI 6.x)
- Android 15 (One UI 7.x)
- Android 16 (One UI 8.x)
- Android 17 (One UI 9.x)

The Full APK enables the traditional hook set on One UI 9. The Minimal APK uses only four application scopes. Hook setup paths that depend on Samsung or Android framework internals are fail-soft, so a moved or removed class/method is logged and skipped instead of aborting the whole module hook initialization.

## Full vs Minimal

Each manually published release contains two separately built, signed APKs and their SHA-256 files:

| APK | Profile | Intended use |
| --- | --- | --- |
| `KnoxPatch-vX.Y.Z-Minimal.apk` | Four application scopes, no `SystemHooks` or `system_server` hooks | Recommended for the S25 Ultra One UI 9 baseline: Knox Matrix, Samsung Account, Quick Share and Samsung Health |
| `KnoxPatch-vX.Y.Z-Full.apk` | Traditional complete dispatcher, including on One UI 9 | Other supported fixes, including Secure Folder, Samsung Cloud, Samsung Flow, Secure Wi-Fi and security-service hooks |

Minimal supports One UI 9. It refuses hook installation on earlier versions; use Full there. Its scopes are `com.samsung.android.kmxservice`, `com.osp.app.signin`, `com.samsung.android.app.sharelive` and `com.sec.android.app.shealth`. It does not restore every Samsung feature. Fewer hooks do not guarantee Play Integrity or Google Wallet approval.

Full retains the original hook implementations and may modify `system_server` and Samsung security services. Compatibility still depends on the firmware and the individual feature; build checks are not physical validation of every Full feature.

Both public APKs use `sepBasic` (`com.samsung.device`). `sepLite` (`com.samsung.device.lite`) remains available internally for devices that require that library; it is independent of the Full/Minimal choice. The Enhancer ZIP remains in source for its separate legacy/extra-feature requirements, but neither it nor sepLite is published in the main release.

The APKs share package ID `io.mesalabs.knoxpatch`, versionCode and release signing certificate. Install the other profile over the current APK without uninstalling to preserve app data; the installer must permit replacement at the same versionCode. A higher installed versionCode requires a newer release. A LAB APK signed with a different certificate cannot update the release APK. LSPosed can retain manually selected scopes: after switching to Minimal explicitly remove Android system/framework and unrelated apps, then restart the previously hooked processes or reboot using your established recovery procedure. Minimal's dispatcher rejects the full path even if an old scope remains selected; replacing the APK does not undo hooks already installed in running processes.

Local build tasks: `:app:assembleSepBasicFullRelease` and `:app:assembleSepBasicMinimalRelease`. `release.yml` remains **workflow_dispatch only**, restricted to `main`; merging a PR does not publish a release. The release checks each compiled APK's Manifest profile, packaged scope configurations, Xposed entrypoint and DEX hook markers independently before publishing both assets in one release. SHA-256 files cover the final signed APKs.

The supported-app list below describes Full; Minimal is limited to the four apps above.

## Supported apps
- ✅ [Auto Blocker](https://www.samsung.com/uk/support/mobile-devices/protect-your-galaxy-device-with-the-new-auto-blocker-feature/)
- ➖ [Galaxy Wearable (Gear Manager)](https://www.samsung.com/us/support/owners/app/samsung-galaxy-wearable-watch) ([Enhancer](#knoxpatch-enhancer) required)
- ✅ Samsung Cloud ([FMM](https://www.samsung.com/uk/support/mobile-devices/what-is-find-my-mobile-and-how-can-i-use-it-to-locate-lock-or-wipe-my-device/), [Enhanced data protection](https://www.samsung.com/ae/support/mobile-devices/what-is-the-enhanced-data-protection-function-and-when-can-i-use-it/))
- ✅ [Samsung Flow](https://www.samsung.com/uk/apps/samsung-flow/)
- ✅ [Samsung Health](https://www.samsung.com/uk/apps/samsung-health/)
- ✅ [Samsung Health Monitor](https://www.samsung.com/uk/apps/samsung-health-monitor/)
- ➖ [Samsung TV Plus](https://www.samsungtvplus.com/) ([TrickyStore](https://github.com/5ec1cff/TrickyStore/releases/latest) required)
- ✅ [Secure Folder](https://www.samsungknox.com/en/solutions/personal-apps/secure-folder) ([Enhancer](#knoxpatch-enhancer) might be required)
- ✅ [Secure Wi-Fi](https://www.samsung.com/uk/support/mobile-devices/what-is-the-secure-wifi-feature-and-how-do-i-enable-or-use-it/)
- ✅ [SmartThings](https://www.samsung.com/smartthings/app/)
- ➖ [Smart View](https://www.samsung.com/uk/tvs/tv-buying-guide/what-is-samsung-smart-view/) ([Enhancer](#knoxpatch-enhancer) required)
- ✅ [Private Share](https://www.samsung.com/uk/support/mobile-devices/how-to-keep-your-personal-data-safe-using-private-share/)*
- ❌ [Samsung Pass](https://www.samsung.com/uk/apps/samsung-pass/)
- ❌ [Samsung Wallet (Pay)](https://www.samsung.com/uk/apps/samsung-wallet/)

\* Devices running One UI 5.1 or lower might need [PIF](https://github.com/chiteroman/PlayIntegrityFix/releases/latest) or similar for this feature to work correctly since the integration in Quick Share.

## KnoxPatch Enhancer

KnoxPatch Enhancer is a flashable zip that will take care of the (currently) non-fixable apps/features via the Xposed API's. There are two different install modes:

- Via the [Magisk](https://github.com/topjohnwu/Magisk)/[KernelSU](https://github.com/tiann/KernelSU) app (fix Galaxy Wearable apps/Smart View):

  Obtain the separately built Enhancer ZIP from a compatible historical release or a reviewed local build and install it from the "Modules" tab inside the Magisk/KernelSU app. The app will then show an "Enhanced" badge if the module is installed and active:

<p align="center">
  <img loading="lazy" src="readme-res/kp-enhancer.png" width="35%" />
</p>

- Via a custom recovery (fix Secure Folder on legacy devices):

  Legacy devices running One UI 2.x or 3.x with [FBE](https://source.android.com/docs/security/features/encryption/file-based) require additional patches in the system partition to fix Secure Folder. Obtain the separately built Enhancer ZIP from a compatible historical release or a reviewed local build and install it via a custom recovery, this will apply the necessary patches to fix Secure Folder. The zip will also create a backup of your original system files, flashing it again will restore them.

## Credits
- Samsung
- [Salvo Giangreco / original KnoxPatch](https://github.com/salvogiangri/KnoxPatch)
- [LSPosed Team](https://github.com/LSPosed/LSPosed)
- [YukiHookAPI](https://github.com/fankes/YukiHookAPI)
- [Rikka](https://github.com/RikkaApps)

## Copyright
```
/*
 * Copyright (C) 2022 Salvo Giangreco
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
```
