# Redmi firmware privacy investigation

This is an independent investigation of privacy-relevant system components on my Chinese-market Redmi K40. It documents what I found, how to inspect a similar device, and the limits of the evidence. Privacy risks can justify defensive action even when a specific allegation has not been proven.

**What we found:** the installed SystemHelper APK implements reporting of device and SIM identifiers, app usage and radio/location information to a configurable address whose default is associated with China Unicom. The phone showed related runtime activity and historical UID-level network traffic. We did **not** capture the reporting payload, verify its recipient, or establish periodic screenshot uploads. A user-0 disable experiment stopped the observed process and passed limited connectivity checks; the user later reported receiving an SMS verification code. It did not establish that all reporting stopped.

Read the [full investigation](REPORT.md), [SystemHelper reporting-path analysis](analysis/systemhelper.md), [selected evidence notes](analysis/selected-evidence.md), and [disable experiment](disable-test/RESULT.md).

## Threat model

Identifiers and SIM/network information can link records to a device or subscriber; app usage, location and radio data can reveal habits, associations and movements. Potential recipients include the phone vendor, mobile operators and embedded SDK providers. Recipients or their service providers could retain, combine or disclose data, including in response to legal demands or through compromise. These are plausible downstream risks, **not findings that a government or any other party received this phone's data**.

Our goals are to reduce unnecessary collection and exposure, make consent and destinations inspectable, and preserve everyday phone functionality. ADB inspection is itself sensitive: package lists, logs, identifiers and network details can reveal personal information. Keep outputs private.

## Compatibility and limitations

The examined phone was a Redmi K40 (`M2012K11AC`, `alioth`) running Android 13 and Chinese HyperOS `V816.0.10.0.TKHCNXM`, security patch `2024-03-01`. Active package versions at the investigation snapshot were:

| Component | Package | Active version |
|---|---|---|
| SystemHelper | `com.mobiletools.systemhelper` | `3.0.0-20231222` |
| GuardProvider | `com.miui.guardprovider` | `2.1.2-20240312.0` |
| DMRegService | `com.miui.dmregservice` | `4.0` |
| Security Center | `com.miui.securitycenter` | `10.5.2-260718.0.1` |
| MetokNLP | `com.xiaomi.metoknlp` | `5.0.10` |
| Analytics | `com.miui.analytics` | `6.33.0` |

Security Center and Analytics were updated system apps, so their active versions can differ from the firmware's factory copies. Device region, firmware, updates, carrier, user profile and permissions can change behavior. Results should not be generalized to other Xiaomi/HyperOS releases. A non-root shell could not read private preferences, queues or payloads; native code and delegated services were not fully analyzed. APKs and full disassemblies are not distributed here.

## Methodology and key findings

The initial examination used non-root, read-only ADB package, AppOps, process, alarm and log snapshots, followed by local APK manifest/signature and DEX analysis using existing Android SDK and Python tools. Later, a separately authorized experiment disabled SystemHelper for user 0 without uninstalling it. No phone changes were made for this publication review.

- **SystemHelper:** privileged grants and code support app/usage, device/SIM, radio and location collection and encrypted reporting. Default app and device alarms are 24 hours and the signal-report alarm six hours; preferences can override intervals. Retained alarm history is not proof of delivery.
- **GuardProvider:** code constructs app metadata for a Xiaomi security endpoint; delivery was not observed.
- **DMRegService:** code constructs a device/SIM/network data “snapshot”; the inspected snapshot is structured data, not evidence of screen-image capture. Its phone UID is shared.
- **Security Center:** broad system-UID privileges and screenshot-related functionality exist. The inspected paths do not establish periodic screenshot uploads, and shared-UID observations cannot be attributed to it alone.
- **MetokNLP:** a running network-location provider with location-related access and embedded third-party SDK endpoints. Embedded URLs do not prove that a particular provider received data.
- **Analytics:** code supports installed-app and usage event collection; identifier-provider calls appeared in logs without returned values or captured payloads.

See [the report](REPORT.md) for package paths, signing, permissions, services and attribution limits.

### SystemHelper reporting and consent

The examined code schedules boot/SIM, periodic device/app, and signal-related work. App records are built from usage records joined to installed apps, excluding `com.android` names; they are not simply a list of every app. Device/SIM and signal fields are conditional, sometimes transformed or unavailable. The code defaults to `dm.wo.com.cn:18080/register`, with carrier-specific conditions and a Unicom-labelled encryption certificate; an override may exist. It also embeds a Baidu location SDK. The likely carrier association is supported by code and external research, but the phone's actual destination, recipients and submitted fields were not observed. The DNS answer seen on the analysis computer is not a phone traffic observation.

On the Xiaomi branch, the flag used by the reporting gate comes from `device_provisioned`, a setup-completion state. The code also programmatically sets the Baidu SDK privacy-agreement flag. Neither observation establishes that a separate meaningful user choice was obtained, nor proves the legal status of a particular transmission. [Detailed path, gating, transformations and caveats](analysis/systemhelper.md).

## Evidence matrix

| Claim | Evidence and scope | Limit |
|---|---|---|
| SystemHelper can collect and serialize app, SIM and radio/location fields | [Static code paths and fields](analysis/systemhelper.md#what-enters-the-payload); [selected evidence](analysis/selected-evidence.md) from the K40 APK | Capabilities, not a captured payload or proof every field was populated |
| Carrier-oriented reporting is implemented | [Sender, gates, default endpoint and certificate](analysis/systemhelper.md#sending-storage-and-destinations) | Configured override, actual connection and receipt unknown |
| SystemHelper ran and had scheduled work | K40 [AppOps, logs and retained alarm history](analysis/selected-evidence.md) | Historical entries and delivery counts are not proof of current uploads |
| SystemHelper's UID transmitted data historically | K40 [netstats summary](REPORT.md#historical-network-transmission) | UID counters contain no destination, timing of individual requests, or payload |
| A disable stopped the observed process and ordinary component resolution | [Before/after experiment](disable-test/RESULT.md) | Short observation; old alarms remained; no payload monitoring |
| SMS verification code was received afterward | User report in [experiment results](disable-test/RESULT.md) | Single reported receipt, not a general messaging reliability test |
| Periodic screenshot uploads | No capture-to-upload chain or image-bearing request was found | Unverified allegation; absence of a finding is not proof of impossibility |
| Sensitive transmissions in prior research | Liu, Leith and Patras, [WiSec 2023 paper](https://doi.org/10.1145/3558482.3581775), [author-accessible preprint](https://arxiv.org/html/2302.01890v1) and [supplementary connection data](https://github.com/Mobile-Intelligence-Lab/android_CN_trafficdata) | Their traffic experiments included a Redmi Note 11 on Android 11/MIUI, not this K40; their observed traffic is not a capture from this device |

No packet capture or decrypted report from this K40 is available. To substantiate an alleged screenshot upload, future work would need to connect a timestamped screen-pixel capture to the encoded request and its destination, then demonstrate image contents and repeated timing. A gateway capture can show destinations and timing but may not reveal encrypted content or uniquely attribute shared-UID traffic.

## Reproducibility guide

These commands are **read-only** and need an already authorized ADB connection, not root. USB debugging authorization is a security-sensitive setting; turn it off when finished if you do not need it. Commands and output vary by Android version, and some dumps may be restricted. Replace `<SERIAL>` with the identifier shown locally by `adb devices`; don't publish it. The example targets SystemHelper on user 0.

```sh
adb devices -l
adb -s <SERIAL> shell getprop ro.product.model
adb -s <SERIAL> shell getprop ro.build.version.release
adb -s <SERIAL> shell getprop ro.build.version.incremental
adb -s <SERIAL> shell pm path com.mobiletools.systemhelper
adb -s <SERIAL> shell dumpsys package com.mobiletools.systemhelper
adb -s <SERIAL> shell cmd appops get com.mobiletools.systemhelper
adb -s <SERIAL> shell pidof com.mobiletools.systemhelper
adb -s <SERIAL> shell dumpsys activity services com.mobiletools.systemhelper
adb -s <SERIAL> shell dumpsys alarm
adb -s <SERIAL> shell dumpsys jobscheduler
```

Package dumps can show enabled state, UID, version, permissions and declared components. Alarm and job dumps are system-wide: review locally for the package name and treat existing timestamps/counters as historical. Check UID membership before attributing shared-UID activity; permissions and AppOps do not prove collection. These commands can reveal serials, installed apps, network details and other personal data; do not publish raw output. For further ADB syntax see [Android's documentation](https://developer.android.com/tools/adb).

## Mitigation guide

Start with inspection and review the phone's own privacy and permission controls. Available controls may not affect privileged permissions and changing location or networking can impair services. Network-level domain blocking may reduce some connections but can break functions, miss alternate destinations or encrypted DNS, and cannot establish what data was sent. Assess each component individually: avoid broad debloating or disabling shared-UID telephony and security services on the strength of package names alone.

**Tested option: SystemHelper for user 0.** On this K40, after checking the exact model, package, enabled state, UID membership and rollback, the experiment used:

```sh
adb -s <SERIAL> shell pm disable-user --user 0 com.mobiletools.systemhelper
```

The process disappeared and Wi-Fi/ADB and network registration remained available. A later user-reported verification SMS was received. Mobile data was already off; calls, SMS sending, hotspot and GPS were not tested. Three old alarms persisted and were not due during the short observation. These results cannot guarantee functionality on another device or prove reporting has stopped. The experiment left SystemHelper disabled at its last observation; subsequent state was not checked during this publication review.

To restore functional availability for user 0, run and verify:

```sh
adb -s <SERIAL> shell pm enable --user 0 com.mobiletools.systemhelper
adb -s <SERIAL> shell dumpsys package com.mobiletools.systemhelper
```

Check the user 0 enabled state. The original state was manifest-default enabled; `pm enable` sets an explicit enabled state. If the package is protected or the command fails, stop rather than bypass protection. See [test details and rollback](disable-test/RESULT.md). The package can have other dependencies, and disabling it does **not** address Analytics, GuardProvider, DMRegService, or other telemetry components.

## References and publication scope

- Haoyu Liu, Douglas J. Leith and Paul Patras, *Android OS Privacy Under the Loupe – A Tale from the East*, ACM WiSec 2023, [DOI](https://doi.org/10.1145/3558482.3581775); [preprint](https://arxiv.org/html/2302.01890v1); [supplementary data](https://github.com/Mobile-Intelligence-Lab/android_CN_trafficdata).
- [Android Debug Bridge documentation](https://developer.android.com/tools/adb).
- Raw logs, APKs, full proprietary disassemblies and the copyrighted paper PDF are not included.
