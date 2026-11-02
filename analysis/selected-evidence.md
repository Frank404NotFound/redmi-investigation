# Selected evidence and reproducibility notes

This is a sanitized index of observations from the K40 investigation. The original package dumps, logs, instruction-level extracts, collected APKs and command journal remain private and are not part of the public release. Consequently a reader can reproduce the inspection on a comparable device, but cannot independently replay every conclusion from this release alone. APK hashes in [apk_hashes.json](apk_hashes.json) identify the examined builds without distributing the APKs. Shared-UID observations do not establish which member acted.

| Reference in reports | Source and selected observation | Interpretation |
|---|---|---|
| E2–E4 | Non-root `dumpsys package`, `cmd appops get`, process/service and log snapshots; signatures checked locally with `apksigner` | Grants and retained access times are state/history, not proof of a specific disclosure. Security Center and DMRegService share system/phone UIDs. |
| E5 / S1–S4 | SystemHelper DEX: `AppInfoRegisterReceiver.onReceive`, `control.e` app/usage builders, `control.b` serialization, and signal callbacks | Code joins usage with installed-app metadata and constructs conditional device, SIM and signal fields; no request body was captured. |
| S5–S10 | Xiaomi adapter reads `Settings.Global.device_provisioned`; Baidu privacy flag is set in code; `control.f` gates, encrypts and posts to a configurable address | Setup state and SDK flag are not evidence of separate informed consent. The default carrier-oriented endpoint is not an observed phone connection. |
| S11–S13 | `dumpsys alarm` retained SystemHelper alarm deliveries and next scheduled work; configuration Binder methods were inspected, not invoked | Alarm history does not establish successful uploads or unchanged interval preferences. |
| E6 | GuardProvider app-record builder and network helper, observed in the APK | Potential app-metadata submission to a security endpoint; delivery unverified. |
| E7 | DMRegService package/usage query and structured snapshot builder | Fields are device/SIM/network data; “snapshot” alone does not mean screenshot. |
| E8 | Analytics installed-app/usage code and identifier-provider log calls | Returned identifiers and network payloads were not captured. |
| E9 | MetokNLP location services, AppOps and embedded endpoint strings | Does not prove successful traffic to each embedded endpoint. |
| E10 | Security Center screenshot-related components, listener and request code | No inspected path established an image-bearing periodic upload. |
| E11 | Retained untagged `dumpsys netstats detail` UID buckets, summed locally | Historical transmitted byte counts have no per-request destination or content and may be incomplete. |

The [full report](../REPORT.md) gives versions, package paths, permissions, UID limitations and commands. The [focused analysis](systemhelper.md) gives report types, interval defaults, fields, transformations, gates and recipient caveats. The [disable test](../disable-test/RESULT.md) separates earlier records from the short post-change observation. No K40 packet capture or decrypted payload is available. See the README's read-only guide before collecting your own outputs; treat them as private.
