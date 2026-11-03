/*
 * KnoxPatch - Secure Folder DZIF experimental app-only hook
 * Copyright (C) 2026 KnoxPatch contributors
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

package io.mesalabs.knoxpatch.hooks

import com.highcapable.yukihookapi.hook.entity.YukiBaseHooker
import com.highcapable.yukihookapi.hook.log.YLog

import com.highcapable.kavaref.KavaRef.Companion.resolve

/**
 * Targets the pre-provisioning root warning in Secure Folder 2.0.30.32 on
 * Android 17 DZIF. No system_server, DAR, KeyMint, or property hooks.
 *
 * This is an experiment: passing the welcome screen does not prove that the
 * subsequent Knox container provisioning will succeed or retain hardware
 * security guarantees after the Knox warranty fuse has been tripped.
 */
object SecureFolderExperimentalHooks : YukiBaseHooker() {
    private const val TAG = "SecureFolderExperimentalHooks"
    private const val WELCOME_VIEW_MODEL =
        "com.samsung.knox.securefolder.provisioning.setup.viewmodel.WelcomeViewModel"

    override fun onHook() {
        try {
            val viewModelClass = WELCOME_VIEW_MODEL.toClassOrNull()
            if (viewModelClass == null) {
                YLog.error(msg = "$TAG: WelcomeViewModel unavailable; no hooks installed.")
                return
            }

            val check = viewModelClass.resolve().firstMethodOrNull {
                name = "isCompromisedDevice"
                emptyParameters()
                returnType = Boolean::class
            }
            if (check == null) {
                YLog.error(msg = "$TAG: isCompromisedDevice()Z not found; no hooks installed.")
                return
            }

            check.hook {
                before {
                    // The client-side welcome screen is the only target.
                    // No binder result or hardware attestation is modified.
                    result = false
                    YLog.debug(msg = "$TAG: welcome compromised-device gate bypassed.")
                }
            }
            YLog.debug(msg = "$TAG: app-only welcome hook installed.")
        } catch (t: Throwable) {
            YLog.error(msg = "$TAG: hook setup skipped: $t")
        }
    }
}
