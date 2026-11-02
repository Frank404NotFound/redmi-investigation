# Baseline and rollback preparation

- ADB device matched Redmi K40 model `M2012K11AC`, device `alioth`, Android 13 and requested firmware.
- SystemHelper version `3.0.0-20231222`, active path `/system/priv-app/SystemHelper/SystemHelper.apk`; user 0 installed, enabled (Package Manager `enabled=0`, meaning manifest default).
- UID 10090 membership: SystemHelper only. Its main process was running; package-scoped active-service dump was empty.
- Three pending wakeup alarms named for app information, signal information and scheduled registration; retained history showed 212 wakeups. History predates the test.
- `GET_USAGE_STATS` AppOp was `default`; the retained rejection timestamp and other AppOps entries are historical, not proof of a new event.
- Default Wi-Fi was connected and Android reported it validated. A Wi-Fi-only HTTPS GET to Android’s standard connectivity endpoint returned HTTP 204. A single ping to a public DNS resolver received no reply at baseline; ICMP can be filtered.
- SIM state: slot 1 absent; slot 2 loaded, LTE; slot 2 voice and data registration in service. Mobile data setting was `0` (off) before the test.
- Package manager help lists `enable [--user USER_ID] PACKAGE_OR_COMPONENT`; `pm help` itself returns 255 while displaying that help. No enable operation was performed.
- Rollback: `adb shell pm enable --user 0 com.mobiletools.systemhelper`. This sets explicit enabled state even if the original state was manifest default.

**Preflight: PASS**. Detailed raw outputs and timestamped command hashes are retained locally in `private/baseline/`.
