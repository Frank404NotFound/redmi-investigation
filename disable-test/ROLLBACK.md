# Rollback prepared

For the connected target device, run:

```sh
adb shell pm enable --user 0 com.mobiletools.systemhelper
adb shell dumpsys package com.mobiletools.systemhelper
```

Verify the user 0 package entry is enabled. If several devices are connected, add `-s` and the target serial shown in the user's request to both commands. The pre-existing package state can be `default` rather than an explicit enable; this command restores functional availability but sets an explicit enabled state.
