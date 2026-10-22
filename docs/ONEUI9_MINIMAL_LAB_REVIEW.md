# One UI 9 KnoxPatch app-only LAB review

**Not production validated. Do not auto-merge or replace the currently functioning KnoxPatch build.**

This experiment reduces the Android 17/One UI 9 runtime footprint to four
application process targets. The existing upstream full feature set remains
available for earlier One UI releases through the source code, but the
suggested Xposed scope is minimized for the One UI 9 lab use case.

| Application | Loaded hook | Reason |
|---|---|---|
| com.samsung.android.kmxservice | KnoxMatrixHooks | Samsung Account logout / Knox Matrix trust state reported in upstream issue #152 |
| com.osp.app.signin | SamsungKeystoreHooks | Account SAK parameter handling |
| com.samsung.android.app.sharelive | SamsungKeystoreHooks | Quick Share SAK handling |
| com.sec.android.app.shealth | KnoxSDKHooks | Samsung Health Knox SDK detection |

On One UI 9, **none** of the following runs: `SystemHooks` in
`system_server` (KnoxGuard constructor interceptions, DAR/Secure Folder
attestation hooks, or ASKS property interceptions), `PropSpoofHooks`,
`RootDetectionHooks`, `SAKDisableHooks`, or Samsung Cloud/Flow/SmartThings/
Secure Wi-Fi/Secure Folder/Health Monitor compatibility hooks.

**Functional trade-offs:** Secure Folder, Samsung Health Monitor, Samsung
Cloud sync, Auto Blocker, SmartThings, Secure Wi-Fi, Samsung Flow, Samsung
checkout and legacy Samsung-specific functions are not promised by this
profile. The original full upstream profile should remain available as
rollback, but do not activate it alongside the experiment.

### Hardware-validation plan

1. Before installing the APK, record Samsung Account session state,
   Quick Share transfer, Samsung Health launch/login, Google Play Integrity
   STRONG, Google Wallet, SELinux and current Xposed scopes.
2. Install the experimental app and enable exactly the four package scopes.
   Verify these package identities match the installed firmware.
3. Make sure `android` / System Framework is **not** selected in LSPosed.
   Soft reboot only through the previously verified safe path.
4. Confirm no KnoxPatch hook initialization in `system_server`, no
   KnoxGuard/ASKS/DAR hook registration, and confirm the four app hooks
   actually initialize (not merely that the APK is installed).
5. Validate Samsung Account still logged in after 10, 30 and 60 minutes,
   then after a day; Quick Share send/receive; Samsung Health functionality;
   Play Integrity and Wallet at each stage.
6. On logout or regression, collect LSPosed logs, Samsung Account and
   Knox Matrix app versions. Stop and revert the experimental scope/APK
   before restoring one hook family at a time. Do not introduce PIF,
   TrickyStore, filesystem overlays or global property spoofing.

Evidence: https://github.com/salvogiangri/KnoxPatch/issues/152 (account
logout associated with Knox Matrix update and developer's hook fix).
This does **not** establish that KnoxGuard is irrelevant on every firmware.

Tests prove scope and dispatcher invariants only; they cannot prove
runtime Samsung Account, STRONG or Wallet behavior.
