# Redmi K40 system-component investigation

**Read-only examination: 2026-11-01, America/Los_Angeles.** Device serial redacted. The phone reports `M2012K11AC` / `alioth`, Android 13 (API 33), firmware `V816.0.10.0.TKHCNXM`, security patch `2024-03-01`, production `user` build, `ro.debuggable=0`. ADB shell runs as UID 2000, without root. Initial runtime collection was approximately 21:10–21:14 PST; a later setup-flag query supplemented it.

**Result:** The installed APKs substantiate implementations for collecting app metadata, usage information, device/SIM identifiers, and location-related data. Permission grants, recent location AppOps records, identifier API log entries, and historical network counters provide additional device-specific evidence. **Periodic screenshot uploads were not verified.** No captured image, image-bearing request, or capture-to-upload execution chain was observed.

**Focused follow-up:** [SystemHelper’s reporting path](analysis/systemhelper.md) traces triggers, conditional payload fields, carrier/Baidu recipients, encryption, runtime scheduling and consent gates. It adds identifier hashing/clearing and programmatic SDK privacy-flag findings.

## Confirmed findings

### Installed versions, paths and signing

Paths below identify the active APK. Randomized update-directory names are redacted. The complete inventory is retained privately; [selected evidence](analysis/selected-evidence.md) summarizes the methods and findings. [APK hashes](analysis/apk_hashes.json) identify the exact copies examined.

| Package | Active version (versionCode; target SDK) | Active APK | UID / privilege | Signer |
|---|---|---|---|---|---|
| `com.mobiletools.systemhelper` | `3.0.0-20231222` (31; 33) | `/system/priv-app/SystemHelper/SystemHelper.apk` | 10090; system privileged app; its named shared UID currently contains only this package | NewDM |
| `com.miui.guardprovider` | `2.1.2-20240312.0` (212; 33) | `/product/app/MIUIGuardProvider/MIUIGuardProvider.apk` | 10121; system app, not marked privileged | Platform |
| `com.miui.dmregservice` | `4.0` (4; 33) | `/system/priv-app/DMRegService/DMRegService.apk` | 1001, shared `android.uid.phone`; privileged and persistent | Platform |
| `com.miui.securitycenter` | `10.5.2-260718.0.1` (40001052; 34) | `/data/app/<REDACTED>/base.apk` | 1000, shared `android.uid.system`; updated privileged system app | Platform |
| `com.xiaomi.metoknlp` | `5.0.10` (13010; 33) | `/product/app/MetokNLP/MetokNLP.apk` | 10148; system app, not marked privileged | Platform |
| `com.miui.analytics` | `6.33.0` (2026091500; 36) | `/data/app/<REDACTED>/base.apk` | 10147; updated system app, not marked privileged | Platform |

Security Center's factory copy is under `/product/priv-app/MIUISecurityCenter`; Analytics' factory copy is `/product/app/AnalyticsCore` (version `5.23.0`). This analysis used the **active updated APKs**, not just the original firmware versions.

All six APK signatures verified using the existing SDK `apksigner`. “Platform” means the signing certificate matches the phone's copied `framework-res.apk`, not merely a matching certificate name:

- Platform certificate SHA-256: `c9009d01ebf9f5d0302bc71b2fe9aa9a47a432bba17308a3111b75d7b2149025` (CN=MIUI, O=Xiaomi).
- SystemHelper certificate SHA-256: `874b8ca2297f53a373b1b935c134cb0eb1ff7381e54491b88c643a6b9c46db77` (CN=NewDM, OU=RI, O=CU). These certificate fields alone do not establish the operator's identity or intent.

Evidence: package dumps and `pm path`; signature transcripts in [E3](analysis/selected-evidence.md).

### Sensitive access and observed activity

“Granted” below means Package Manager records a permission, including a shared UID's permission union where applicable. It does not mean every API call succeeds or every capability is exercised.

| Package | Apps / usage | Device identifiers | Location | Screen / accessibility |
|---|---|---|---|---|
| SystemHelper | `QUERY_ALL_PACKAGES`, `PACKAGE_USAGE_STATS` granted | Privileged and precise phone-state permissions granted | Fine/coarse/background granted; fine location and Wi-Fi scan access recorded ~8 minutes before collection | No direct screen-capture grant or accessibility service identified |
| GuardProvider | `QUERY_ALL_PACKAGES` granted; no usage-statistics grant found | Privileged phone state granted, but retained `READ_DEVICE_IDENTIFIERS` operation is `deny` | No location permission grant found; Wi-Fi scan AppOp has an access record ~37 minutes earlier | No capture grant/accessibility service; `screenshotUrl` is URL-check model data |
| DMRegService | Package visibility and usage-statistics grants in shared phone UID | Privileged phone state granted | Shared UID has fine/coarse grants; UID AppOps restrict location to foreground | No direct screen-capture grant/accessibility service identified |
| Security Center | System UID has broad app visibility, usage statistics and `GET_INSTALLED_APPS` | Shared system UID has privileged phone state | Fine/coarse/background granted to shared UID | UID has `READ_FRAME_BUFFER`, `MANAGE_MEDIA_PROJECTION`, `CAPTURE_BLACKOUT_CONTENT`, and accessibility-management privileges |
| MetokNLP | No `QUERY_ALL_PACKAGES` or usage-statistics grant found; limited visibility may still exist | `READ_PHONE_STATE`, `LOCAL_MAC_ADDRESS`; privileged phone-state grant absent; retained device-identifier operation denied | Fine/coarse/background granted; fine location/Wi-Fi scan ~10 minutes earlier; location monitoring marked running | No capture grant/accessibility service identified |
| Analytics | `QUERY_ALL_PACKAGES`, `PACKAGE_USAGE_STATS` granted | Privileged phone state granted; logs record calls to VAID/UDID provider methods, without returned values | Fine/coarse/background granted; location/Wi-Fi scan access ~22 hours earlier | No capture grant/accessibility service identified |

Important interpretation limits:

- SystemHelper, DMRegService, Security Center and Analytics show `GET_USAGE_STATS: default` with retained `rejectTime` entries. **This does not establish that usage access is blocked.** Android 13's reference service falls back to the permission grant in default mode and allows the system UID directly. This is a reference-model interpretation; the exact HyperOS service implementation was not audited. [AOSP Android 13 source](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-13.0.0_r1/services/usage/java/com/android/server/usage/UsageStatsService.java)
- UID 1000 has 56 current package members and UID 1001 has 17. Shared permissions, AppOps and byte counters cannot automatically be attributed to Security Center or DMRegService alone.
- Accessibility was disabled (`accessibility_enabled=0`, empty enabled-service list), and MediaProjection reported `null`. Security Center declares `AntiMsgAccessibilityService`, configured to retrieve window content for QQ/WeChat notification events; its XML does not declare screenshot capability. A recorded `BIND_ACCESSIBILITY_SERVICE` AppOp does not establish an enabled spying service.
- Android permits signature-authorized screen access beyond ordinary user-consented MediaProjection. Thus the null projection snapshot does not rule out capture through privileged paths. [AOSP screen-reading restrictions](https://source.android.com/docs/core/permissions/restricted-screen-reading)
- `QUERY_ALL_PACKAGES` expands visibility; it does not prove enumeration or upload. [Android package visibility documentation](https://developer.android.com/training/package-visibility/declaring)

Evidence: [E2/E4 and selected runtime evidence](analysis/selected-evidence.md), [selected runtime summary](analysis/selected-evidence.md). Very old AppOps timestamps may survive upgrades or clock changes; they are not reliable acquisition dates.

### Running components and scheduling

All six packages had a process in the initial read-only snapshot, before the later [disable experiment](disable-test/RESULT.md). SystemHelper had no active service in its package-scoped service dump, but had scheduled alarms. The other packages had active services:

| Package | Relevant active services / receivers | Registered jobs or alarms |
|---|---|---|
| SystemHelper | Manifest boot, connectivity and SIM receivers; app/signal/registration receivers | Alarms for `AppInfoRegisterReceiver`, `SignalInfoRegisterReceiver`, `ScheduleRegisterReceiver`; no JobScheduler job found |
| GuardProvider | `manager.SecurityService`; connectivity receiver | Retained 7-day cache job reports `comp=false` (component unavailable); SDK alarm history |
| DMRegService | `cn.richinfo.dm.service.DMService`; third-party dynamic-request receiver | Registration-related alarm; no JobScheduler job found |
| Security Center | `OperationListCollectService`, `AppPredictService`, `AiService`, antivirus, firewall, traffic-management and notification-listener services | Virus update/app management/connectivity jobs daily; storage optimization every 6 hours; scan every 3 hours; additional alarms |
| MetokNLP | Network location, geocoding and geofencing services; screen-on/off receivers | No JobScheduler job found |
| Analytics | `OneTrackService`, `TrackService`; advertising-ID change/reset receivers | `internal.WakeupService` alarms; no JobScheduler job found |

Service names and periodic jobs establish activity/scheduling, not what data is sent. Selected component, receiver and AppOps findings are described in [the evidence notes](analysis/selected-evidence.md); full raw inventories remain private.

### Historical network transmission

Summing only retained, untagged `UID stats` histories from `dumpsys netstats detail` produced:

| UID / association | Transmitted bytes |
|---|---:|
| 10090 — SystemHelper | 890,457 |
| 10121 — GuardProvider | 5,852,037 |
| 10147 — Analytics | 17,578,453 |
| 10148 — MetokNLP | 2,179,696 |
| 1000 — shared system UID | 13,605,112 |
| 1001 — shared phone UID | 0 in retained buckets |

Most histories span bucket starts from September 27 through November 1, 2026; coverage is incomplete and predates this session. These counters confirm historical network transmission for the positive UIDs, **without identifying payloads or destinations**. Zero retained transmitted bytes for UID 1001 does not establish that DMRegService has never transmitted. [Evidence and counting method: E11](analysis/selected-evidence.md)

## Suspicious indicators: implemented collection/reporting paths

These are confirmed properties of the copied code, but execution, field values, server receipt and consent status remain unverified unless explicitly described above.

- **SystemHelper:** `AppInfoRegisterReceiver.onReceive` reschedules itself, then requests registration type `A`. `control.e.b()` calls `getInstalledApplications`; `control.e.a()` queries aggregated usage, and another method queries per-app network statistics. Record keys include `pkgName`, `appLabel`, `runTime` and traffic totals. `control.b.a()` serializes device/SIM identifier fields and `AppInfo`; `control.f.a(control.b)` passes the record through encryption helpers to a POST routine with content type `application/encrypted-json`. Default registration endpoint: `http://dm.wo.com.cn:18080/register`; a private preference can override it. The default app-report interval is 86,400,000 ms (24 hours), not a screenshot interval. **On the Xiaomi branch, the flag labelled `isUserPermissionOpen` is set from `Settings.Global.device_provisioned==1`; the phone returned `1`.** This is setup completion, not evidence of a separate informed-consent decision. Which app records were actually collected/sent remains unknown. [E5a–E5h](analysis/selected-evidence.md)
- **GuardProvider:** `j0.c.b(List)` builds app records with `pkg`, `version`, `signature`, `appname` and a `uuid`, then calls a network helper for `https://flash.sec.miui.com/detect/app`, labelled `virus_scan`. This is a concrete app-metadata submission implementation, plausibly related to antivirus/anti-fraud classification. Server delivery was not observed. [E6](analysis/selected-evidence.md)
- **DMRegService:** `cn.richinfo.dm.a.b.l/m` enumerates packages and queries foreground time/launch information. Its “snapshot” builder `cn.richinfo.dm.bean.l` assembles IMEI/IMSI/ICCID, MAC, cell, device and optional phone-number fields. `cn.richinfo.dm.a.F.b(bean.l)` sends serialized JSON through `EncryptJsonRequest` toward `sdkphoto/accept?func=tsdk:photoReg` or an `auc.fxltsbl.com` route. **The inspected “snapshot/拍照采集” path is a structured device-data snapshot; it does not establish screen-image capture.** [E7](analysis/selected-evidence.md)
- **Analytics:** Installed-app event code builds package/version/installer/install-time/update-time records; separate code queries usage events. Tracking configuration includes `https://tracking.miui.com/track/v1`. Existing process logs record VAID/UDID API calls, but neither returned values nor outbound payloads were exposed. [E8](analysis/selected-evidence.md)
- **MetokNLP:** Active location-provider services, location AppOps, and embedded AMap/Baidu/Tencent SDKs support a network-location role. Code includes `loc.map.baidu.com`, `nlp.map.qq.com`, `cgicol.amap.com` and other location-service endpoints. Embedded endpoints do not prove that each vendor received this device's data. [E9](analysis/selected-evidence.md)
- **Security Center:** A running operation-collection service registers screen/user-present/headset/network/screenshot-event listeners. Other code sends a screenshot-request broadcast or hides/restores bubbles around screenshot completion. `/data/system/app_screenshot` appears in storage-accounting code. A `/game/screen_shot` request constructs package/sign parameters and returns a string; the inspected method does not pass screen-image bytes. These merit scrutiny, but do not establish periodic screenshot exfiltration. [E10](analysis/selected-evidence.md)

## Unverified allegations and evidence still required

**Not established:** periodic screenshots; screenshot uploads by any named package; the contents/recipients of this phone's reporting requests; collection of every installed app; or whether particular transmissions lacked user consent. Permissions, API names, endpoint strings, encrypted traffic sizes and periodic alarms are insufficient individually or together to prove an image upload.

A convincing screenshot-upload finding would connect:

1. **Capture:** a timestamped call capturing display pixels, attributed to the actual process/UID and its caller. Distinguish app icons, webpage previews, game artwork and structured “snapshots” from screen contents.
2. **Data flow:** the returned image buffer through encoding/encryption into a specific outbound request, with destination and timing. Inspecting plaintext before encryption may be necessary; this package's custom payload encryption can remain opaque even over HTTP.
3. **Transmission/receipt:** a locally retained request payload containing identifiable pixels from harmless test content, ideally matched to server acknowledgement or receipt. Repeat across several natural cycles to establish periodicity and conditions.

Within the current constraints, an **already authorized local router/gateway capture** could establish destinations, timing and volumes without installing anything on the phone. It generally cannot establish image contents inside TLS or application encryption, or uniquely identify shared-UID callers. No such capture was performed. Installing a VPN/certificate, changing proxy settings, rooting or instrumenting the phone would exceed this investigation's constraints; a separately authorized lab device/firmware replica would be preferable for intrusive verification.

## Commands, artifacts and limitations

Representative commands executed (serial redacted):

```sh
adb -s <SERIAL> shell dumpsys package <PACKAGE>
adb -s <SERIAL> shell cmd appops get <PACKAGE>
adb -s <SERIAL> shell pm path <PACKAGE>
adb -s <SERIAL> shell dumpsys activity services <PACKAGE>
adb -s <SERIAL> shell dumpsys activity broadcasts
adb -s <SERIAL> shell dumpsys jobscheduler
adb -s <SERIAL> shell dumpsys alarm
adb -s <SERIAL> shell dumpsys accessibility
adb -s <SERIAL> shell dumpsys media_projection
adb -s <SERIAL> shell settings get secure enabled_accessibility_services
adb -s <SERIAL> shell settings get global device_provisioned
adb -s <SERIAL> shell dumpsys netstats detail
adb -s <SERIAL> logcat -d --pid=<PID> -t 500 -v threadtime
adb -s <SERIAL> pull <APK_PATH> <LOCAL_PATH>
aapt dump xmltree <LOCAL_APK> AndroidManifest.xml
apksigner verify --verbose --print-certs <LOCAL_APK>
dexdump -d <EXTRACTED_DEX>
```

The local collection/analysis scripts are excluded from the public release; the [reproducibility guide](README.md#reproducibility-guide) provides read-only commands. The private command journal includes timestamps, exit codes and SHA-256 hashes of ADB outputs. Selected shareable excerpts retain source line numbers and hashes. All six active APKs and framework resources were copied locally; nine DEX files were disassembled. ASCII strings in 54 embedded native-library entries were triaged, including both ABI copies where present; native code was not comprehensively reverse engineered.

During the initial read-only examination, no root, installation, uninstallation, disabling, settings changes, app launches, forced jobs or synthetic broadcasts were used. A separate, later experiment disabled SystemHelper; see [the result](disable-test/RESULT.md). Existing host ADB/SDK/Python tools were used; nothing was downloaded or installed. During the initial examination, only generic public Android documentation/source was consulted online; device artifacts were not uploaded.

App-private directory listings were denied to ADB shell; preferences, databases and reporting queues could not be examined. Socket enumeration via `ss` was denied; `tcpdump` was not found in PATH. Existing logs were bounded and incomplete; the Security Center log sample covered its main process, not its separate remote process. Observation focused on user 0, not a complete audit of every profile or firmware service. Reflection, native code, server configuration, external code and delegated privileged services limit negative conclusions. No full call-graph proof or runtime payload tracing was performed.

**Handling:** The publication allowlist excludes raw logs, private device data and full disassemblies. No automated scan can guarantee that all identifying information is absent. Unredacted material remains local under `private/` (directory mode 700; ignored by Git). Do not share that directory without reviewing/redacting it.
