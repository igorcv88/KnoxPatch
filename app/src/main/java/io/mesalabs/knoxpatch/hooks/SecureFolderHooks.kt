/*
 * KnoxPatch - Secure Folder DZIF app-only hook (Balanced profile)
 * Copyright (C) 2026 KnoxPatch contributors
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

package io.mesalabs.knoxpatch.hooks

import com.highcapable.yukihookapi.hook.entity.YukiBaseHooker
import com.highcapable.yukihookapi.hook.log.YLog

import com.highcapable.kavaref.KavaRef.Companion.resolve

/**
 * Verified on Secure Folder 2.0.30.32 / Android 17 DZIF. The workaround is
 * limited to the application's own welcome screen. The hardware warranty fuse,
 * KeyMint, DAR service, and system properties are never patched by this hook.
 */
object SecureFolderHooks : YukiBaseHooker() {
    private const val TAG = "SecureFolderHooks"
    private const val WELCOME_VIEW_MODEL =
        "com.samsung.knox.securefolder.provisioning.setup.viewmodel.WelcomeViewModel"

    override fun onHook() {
        try {
            val viewModelClass = WELCOME_VIEW_MODEL.toClassOrNull()
            if (viewModelClass == null) {
                YLog.error(msg = "$TAG: WelcomeViewModel unavailable; no hook installed.")
                return
            }

            val check = viewModelClass.resolve().firstMethodOrNull {
                name = "isCompromisedDevice"
                emptyParameters()
                returnType = Boolean::class
            }
            if (check == null) {
                YLog.error(msg = "$TAG: isCompromisedDevice()Z unavailable; no hook installed.")
                return
            }

            check.hook {
                before {
                    result = false
                    YLog.debug(msg = "$TAG: welcome compromised-device gate bypassed.")
                }
            }
            YLog.debug(msg = "$TAG: Secure Folder app-only welcome hook installed.")
        } catch (t: Throwable) {
            YLog.error(msg = "$TAG: hook setup skipped: $t")
        }
    }
}
