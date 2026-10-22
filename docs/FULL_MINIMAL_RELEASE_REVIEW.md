# Full and Minimal release review

Baseline source: PR #4 head `f023f650f4e6f7d4f345a98f5999b76d3650e06f`.

The previous Minimal implementation selected its dispatcher by SEP version. That made every One UI 9 APK Minimal, including an APK renamed Full. The `hookProfile` Gradle dimension now selects a compile-time `MINIMAL_PROFILE` constant, independently of the Samsung `sepCategory` dimension. Both published variants use sepBasic. Full retains the traditional dispatcher and every existing hook class on One UI 9; Minimal returns before the full dispatcher. Minimal refuses earlier One UI versions.

The main API-37 scope is restored to the API-34 full scope. Minimal overlays every scope qualifier, including values-v37, so an older qualified full resource cannot override an unqualified Minimal array. Regression coverage evaluates Android 28–40 resource selection and Full's Android scope separately from Minimal's four apps.

Source tests are not artifact or device tests. The review and manual release workflows build both release variants and independently inspect the decoded Manifest (identity, profile, scope metadata, Samsung library), every packaged scope configuration, legacy/modern Xposed metadata and DEX strings. SystemHooks-specific DarManagerService and KnoxGuard implementations must be present in Full and absent in Minimal. Both signed public assets must match the certificate derived from the configured release key; signature verification, zip alignment, package/version checks and SHA-256 hashing are retained. Different final hashes are required.

Only Full/Minimal APKs and their SHA-256 files go into the main GitHub Release. sepLite and Enhancer source remain for compatibility; neither is needed for the four-app One UI 9 profile. Enhancer's separate features remain explicitly outside Minimal. The release workflow is still manually dispatched on main. Updating this PR neither merges it nor authorizes a release.

## Validation and remaining evidence

- Local Python source/resource/workflow contracts: passed (6 test methods).
- Workflow YAML and embedded Bash syntax: checked locally.
- Local Android compilation: blocked; Android SDK/JDK 21 and Gradle distribution are unavailable in this container. CI must pass on the final head.
- APK inspection is an enforced build gate, not a result that can be claimed before CI finishes.
- No installation or new physical Full test was performed. The older physically used Minimal APK is not replaced by this source change.

## Switching and rollback

Release profiles share package/version/certificate; replace without uninstalling when Android permits same-version replacement. Do not uninstall to work around a LAB certificate mismatch. Select only the four recommended scopes after moving to Minimal; LSPosed may retain old selections. Already running processes retain old hooks until restarted. Keep the previously working APK and configuration; disable the newly tested module and use the established recovery/reboot procedure if needed. A passing build does not establish Play Integrity or Wallet outcomes.

## Knox Matrix app-local parity

Minimal installs both KnoxMatrixHooks and SamsungKeystoreHooks in Knox Matrix, matching Full within that process. This adds AttestParameterSpec.isVerifiableIntegrity handling without adding a fifth process or system_server hooks. The requirement is based on code parity; physical necessity on One UI 9 remains unproven.
