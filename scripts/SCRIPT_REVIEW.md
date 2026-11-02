# Investigation script review

The original investigation toolkit contains 23 Python scripts; the surviving artifacts do not establish the invocation of every helper. No shell scripts were found outside the private artifacts. The originals are preserved locally and are not published; they were written for one investigation, not a portable toolkit. The tools listed below are adapted versions: they require explicit inputs, do not modify the phone, do not make network requests, and do not contain recorded device data. They do not reproduce every manual analysis step or establish a report's transmission. Review all outputs before sharing them.

| Original script | Purpose and disposition |
|---|---|
| `scripts/collect.py` | Read-only package and runtime collector, including APK pulls. **Modified:** `adb_snapshot_public.py` collects a selected subset, with explicit device/package/output and without pulling APKs. |
| `scripts/runtime_followup.py` | Read-only UID and PID follow-up tied to the original device. **Keep local:** hardcoded UIDs and dependent files; the snapshot tool covers general observations, not every follow-up. |
| `scripts/supplement.py` | Read-only network, access and framework collection. **Keep local:** device-specific paths, UID/network-sensitive dumps and APK pull; select commands manually as needed. |
| `scripts/systemhelper_observe.py` | Read-only SystemHelper follow-up. **Keep local:** original UID and input layout; snapshot tool covers general state and alarms. |
| `scripts/static_analysis.py` | APK manifest, signer and DEX analysis. **Modified:** `apk_static_public.py` requires explicit APK, build-tools and output paths. |
| `scripts/index_bytecode.py` | Index method indicators in disassembly. **Keep local:** exports large instruction sets tied to local paths; use `dex_evidence_public.py` for targeted method and reference searches. |
| `scripts/method_view.py` | Select DEX methods. **Modified:** `dex_evidence_public.py` accepts an explicit disassembly and query. |
| `scripts/summarize_methods.py` | Summarize method strings and calls. **Keep local:** assumes private layout; targeted method viewing covers much of its purpose. |
| `scripts/systemhelper_trace.py` | Offline method, instruction and field index for reporting-path reconstruction. **Keep local:** hardcoded original DEX and full instruction cache; the optional `dex_index_public.py` streams method headers and literal references without a cache, but field-index generation is not reproduced. |
| `scripts/systemhelper_endpoints.py` | Extract literal APK URLs. **Modified:** `apk_urls_public.py` accepts an explicit APK and does not claim that endpoints executed. |
| `scripts/scan_native.py` | Scan native strings for screen/URL indicators. **Keep local:** fixed private APK layout and potentially sensitive output; the public URL scanner covers URL literals but not all screenshot indicators. |
| `scripts/summarize_network.py` | Sum selected UID network counters. **Modified:** `netstats_summary_public.py` requires an explicit dump and UIDs. |
| `scripts/build_inventory.py` | Build original manifest/package inventory. **Keep local:** assumes fixed raw layout and can expose UID membership and installed-package context. |
| `scripts/build_runtime.py` | Generate original runtime report. **Keep local:** depends on private inventory and fixed device dumps; output can contain personal context. |
| `scripts/build_evidence.py` | Generate original selected evidence from fixed disassembly line ranges. **Keep local:** depends on the exact proprietary disassemblies and can overwrite published artifacts. |
| `scripts/build_systemhelper_evidence.py` | Generate specific SystemHelper excerpts and certificate metadata. **Keep local:** tied to original bytecode and private analysis, may output large proprietary excerpts, and requires `cryptography`. |
| `disable-test/collect.py` | Baseline/post-change collector. **Modified:** `adb_snapshot_public.py` offers a general read-only snapshot; it does not make all original telephony queries. |
| `disable-test/observe_later.py` | Later-state collector. **Modified:** take another snapshot with `adb_snapshot_public.py` using a separate output directory. |
| `disable-test/query_components.py` | Read-only SystemHelper component resolution queries. **Keep local:** package-specific fixed paths; package dumps remain inspectable with the snapshot tool. |
| `disable-test/supplement.py` | SIM properties and conditional ICMP probe. **Keep local:** performs a network probe and is coupled to one dump format. |
| `disable-test/wifi_http.py` | Conditional HTTPS connectivity probe. **Keep local:** contacts an external service and is coupled to one dump format. |
| `disable-test/preflight.py` | Evaluate original-device preflight and regenerate baseline. **Keep local:** fixed phone/UID and hardcoded result text; it must not be used to approve changes on another device. |
| `disable-test/build_result.py` | Regenerate original result from fixed private inputs. **Keep local:** modifies original local evidence and embeds historical event assumptions. `compare_snapshots_public.py` provides a limited generic comparison, not an automatic pass/fail. |

No published script disables, enables, uninstalls, starts, or force-stops an Android package. The documented manual disable/enable commands remain potentially disruptive; follow the device and UID checks, explicit user decision and rollback instructions in the [mitigation guide](../README.md#mitigation-guide). Raw snapshots, disassemblies and APKs are sensitive or proprietary, and can include identifiers and credentials; never commit them without separate review.
