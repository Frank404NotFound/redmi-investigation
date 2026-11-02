# SystemHelper literal URL inventory

Extracted from the copied APK’s DEX/native bytes without running them. Query strings are omitted. Candidates are not proof of executed requests; runtime-generated, encoded or remotely selected URLs can be missed. Compiler source links and the Android XML namespace are metadata, not evidence of Google receiving data.

| URL (query omitted) | Context |
|---|---|
| `http://dm.wo.com.cn:18080/public/ip` | registration/IP-discovery code |
| `http://dm.wo.com.cn:18080/register` | registration/IP-discovery code |
| `http://ofloc.map.baidu.com/offline_loc` | Baidu SDK literal candidate |
| `http://schemas.android.com/apk/res/android` | non-endpoint metadata (schema/compiler source URL) |
| `https://android.googlesource.com/toolchain/clang` | non-endpoint metadata (schema/compiler source URL) |
| `https://android.googlesource.com/toolchain/llvm` | non-endpoint metadata (schema/compiler source URL) |
| `https://android.googlesource.com/toolchain/llvm-project` | non-endpoint metadata (schema/compiler source URL) |
| `https://api.map.baidu.com/sdkcs/verify` | Baidu SDK literal candidate |
| `https://daup.map.baidu.com/cltr/rcvr` | Baidu SDK literal candidate |
| `https://itsdata.map.baidu.com/long-conn-gps/sdk.php` | Baidu SDK literal candidate |
| `https://loc.map.baidu.com/cc.php` | Baidu SDK literal candidate |
| `https://loc.map.baidu.com/cfgs/indoorloc/indoorroadnet` | Baidu SDK literal candidate |
| `https://loc.map.baidu.com/cfgs/loc/commcfgs` | Baidu SDK literal candidate |
| `https://loc.map.baidu.com/check_indoor_data_update` | Baidu SDK literal candidate |
| `https://loc.map.baidu.com/gpsz` | Baidu SDK literal candidate |
| `https://loc.map.baidu.com/indoorlocbuildinginfo.php` | Baidu SDK literal candidate |
| `https://loc.map.baidu.com/sdk.php` | Baidu SDK literal candidate |
| `https://loc.map.baidu.com/sdk_ep.php` | Baidu SDK literal candidate |
| `https://ofloc.map.baidu.com/LocBrokerService/do_loc_map_match` | Baidu SDK literal candidate |
| `https://ofloc.map.baidu.com/PlanarStartService/detect_parking_exits` | Baidu SDK literal candidate |
| `https://ofloc.map.baidu.com/locnu` | Baidu SDK literal candidate |
| `https://ofloc.map.baidu.com/offline_loc` | Baidu SDK literal candidate |
| `https://parking.baidu.com/parking/api/parkingdata/getcarportlistforlocation` | Baidu SDK literal candidate |

The only resolved registration IP in this investigation is the host-side DNS answer documented in the focused report. No phone peer IP was attributed to SystemHelper. No hardcoded numeric registration address was found in the traced registration path.
