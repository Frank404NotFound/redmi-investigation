# SystemHelper disable test

**Result: SystemHelper remains disabled for Android user 0.** The requested checks found no significant regression during the short observation. Wi-Fi HTTPS, ADB and the previously registered SIM remained available. Mobile data was already off and could not be functionally tested without changing the user's settings. Three existing SystemHelper alarms remain registered; their eventual behavior is unverified.

The test ran on November 1, 2026, approximately 21:43–21:46 PST, on the specified Redmi K40 and firmware. [Baseline and preflight](BASELINE.md) were saved before the change.

## Change and package state

The sole deliberate phone configuration command was:

```sh
adb shell pm disable-user --user 0 com.mobiletools.systemhelper
```

It returned `Package com.mobiletools.systemhelper new state: disabled-user`. Android's package log records the change at 21:44:37. The target was explicitly selected by serial during the test.

| Check | Before | After |
|---|---|---|
| User 0 state | Installed and enabled; Package Manager `enabled=0` (manifest default) | Installed and `disabled-user`; `enabled=3` |
| APK | `/system/priv-app/SystemHelper/SystemHelper.apk` | Same path and version |
| UID membership | UID 10090: SystemHelper only | Same |
| Process | Main process running | No target process in the immediate or second snapshot |
| Active services | None found in package-scoped dump | None found |
| Receiver/service resolution | Manifest declared the receivers and service | Default Package Manager queries found no tested explicit signal receiver, boot receiver, or registration service; queries with `MATCH_DISABLED_COMPONENTS` found the declarations |
| Target alarms | Three pending wakeup alarms | The same three remained registered in both post-disable snapshots |

The resolver checks were read-only. They establish that Android's ordinary package queries do not resolve the tested components; they do **not** prove every privileged activation path is impossible. No service was started and no test broadcast was sent.

The retained alarm history reported **212 wakeups before and after**. Those are historical counts, not new firings. The three current alarms are one-shot PendingIntents, with the earliest still several hours away. The observation ended about 58 seconds after disabling, before any was due; whether Android later discards or delivers them is unknown. AppOps `time`/`rejectTime` entries likewise describe retained earlier activity. No payload or destination was monitored, so **this test does not establish that reporting has stopped**.

## Functional checks and observations

| Check | Outcome |
|---|---|
| ADB | Connected before and after. |
| Wi-Fi | Connected and Android reported the default network validated before and after. |
| Internet over Wi-Fi | The phone's existing `curl` received HTTP 204 from Android's standard connectivity-check URL both before and after. One ICMP ping to a public DNS resolver received no reply in either test; that diagnostic failure predates the disable and ICMP may be filtered. |
| SIM and network | First slot absent; second loaded and registered for voice/data on LTE both before and after. The second slot was reported roaming in both snapshots. |
| SMS receipt | The user later reported successfully receiving an SMS verification code after disabling. This is a user-reported functional observation; no message contents or independent SMS log are published. Sending and general SMS reliability remain untested. |
| Mobile data | The global mobile-data setting was off (`0`) before and after. No mobile-data traffic test was performed. |
| Crashes | The bounded crash-log buffer was byte-for-byte unchanged across baseline, immediate and later snapshots. Existing earlier crashes are not new test failures. |
| Related system errors | No new error naming SystemHelper was found in the inspected post-change main/system logs. `BackupTransportManager` logged a warning that its enabled state was `3`. AppOps UID/package mismatch errors for Weather and Xiaomi connectivity appeared after the change, but the larger retained log also contained the same error patterns before it; causation is unestablished. |

Android's package-change handling also logged a request to remove Wi-Fi settings associated with SystemHelper. The configured-network section of the Wi-Fi dump was byte-for-byte identical before and after, and the current connection remained up; the log does not show that any saved network was actually removed. An indexing component logged `doRemovePackageData`; the message does not identify exactly what was removed. No app-data, database, or cached-report deletion command was issued; ADB shell could not inspect the app's private files, so their contents cannot be independently compared.

During the automated test no reboot, network-setting change, package uninstall, forced component activation, call, SMS, or mobile-data enable was performed. The user later reported receiving a verification SMS. Disabling this package does not establish that other components have stopped collecting or transmitting telemetry.

## Physical checks still needed

- Place and receive a call.
- Send an SMS and, if useful, repeat receipt; one verification SMS was received according to the user.
- Test mobile data when convenient; it was off during the automated test.
- Test hotspot.
- Test GPS/location.

These checks may involve your carrier plan. If a significant problem appears, restore SystemHelper and retest:

```sh
adb shell pm enable --user 0 com.mobiletools.systemhelper
adb shell dumpsys package com.mobiletools.systemhelper
```

If multiple ADB devices are connected, add `-s` followed by the serial in your request to each command. Verify user 0 is enabled. The rollback command sets an explicit enabled state; the original state was enabled by manifest default. Re-enabling may not restart the app until a normal trigger occurs; this test did not reboot the phone.

## Evidence handling

[Rollback notes](ROLLBACK.md) are available; the collector and checks remain local and are excluded from publication. Unredacted logs and network details are under `private/` (mode 700) and should not be shared without review. Raw command outputs include timestamps, exit codes and SHA-256 hashes; A local, unpublished result-building script checks the before/after findings without modifying the phone. The baseline and post-disable internet probes sent only standard connectivity requests, with no logs or device identifiers uploaded.
