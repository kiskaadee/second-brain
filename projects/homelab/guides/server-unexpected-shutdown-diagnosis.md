---
type: guide
project: homelab
tags:
  - homelab
  - troubleshooting
  - hardware
  - linux
  - systemd
---

# 🛠️ Diagnosing Unexpected Server Shutdowns Runbook

When a headless homelab server abruptly powers off or reboots without warning, diagnosing the root cause requires checking logs across the operating system, the Linux kernel, and the hardware layer.

---

## 1. Quick Triage: Abrupt Power Cut vs. Graceful Shutdown

Determine whether the OS initiated a shutdown sequence or if power was cut abruptly.

### Check the Shutdown & Boot History
```bash
last -x -n 10 shutdown reboot
journalctl --list-boots
```
* **Graceful shutdown**: You will see a `shutdown system down` entry in `wtmp` immediately preceding the subsequent `reboot system boot`.
* **Abrupt power loss / hard crash**: The previous boot record ends without a clean `shutdown` entry, or `last` marks it as `crash` / `still running`.

---

## 2. Inspecting Previous Boot Logs (`systemd-journald`)

Inspect what happened in the final moments before the machine went down:

```bash
# View the end of the previous boot (-b -1 is previous boot, -e jumps to end)
journalctl -b -1 -e

# Search the previous boot for thermal, power, or critical ACPI events
journalctl -b -1 -p 0..3
journalctl -b -1 | grep -iE "thermal|temperature|throttling|power|acpi|shutdown"
```

### Interpreting the Log Tail:
1. **Log ends abruptly with normal service operations**:
   * The OS was not aware it was shutting down; disk buffer flushing was cut off mid-stream.
   * High probability of **silicon hardware-level protection** (CPU PROCHOT thermal cut-off at ~105°C), **PSU trip**, **motherboard protection**, or **wall power loss**.
2. **ACPI Thermal Event (`critical temperature reached`)**:
   * The Linux thermal governor caught an overheating sensor and initiated a clean poweroff:
     `thermal thermal_zone0: critical temperature reached (XX C), shutting down`
3. **Graceful systemd target entered**:
   * Look for `systemd[1]: Reached target Power-Off` or user/cron triggers (`systemctl poweroff` triggered by a script, UPS daemon, or ACPI power button event).

---

## 3. Temperature & Hardware Sensor Verification

### Check Real-Time Sensor Readings
```bash
# On systems with lm-sensors:
sensors

# Direct sysfs inspection (NixOS / minimal environments):
for f in /sys/class/hwmon/hwmon*; do
  echo "=== $(cat $f/name) ==="
  for t in $f/temp*_label; do
    [ -f "$t" ] && echo "$(cat $t): $(cat ${t%_label}_input 2>/dev/null | awk '{print $1/1000}')°C"
  done
done
```
* Check temperatures against critical trip points.
* Verify fan RPMs to ensure fans are not stalling or clogged with dust.

### Machine Check Exceptions (MCE / Hardware Errors)
Hardware errors (failing CPU cores, RAM parity errors, PCIe bus faults) can cause sudden reboots:
```bash
journalctl -k -b -1 | grep -iE "mce|hardware error"
dmesg | grep -iE "hardware error|mce"
```

---

## 4. Kernel Panic & Post-Mortem Dumps (`pstore` / `kdump`)

If the kernel panicked before dying, logs may be saved in persistent memory:
```bash
# Inspect EFI / RAM persistent storage
ls -la /sys/fs/pstore/
cat /sys/fs/pstore/* 2>/dev/null

# Inspect crash dumps if crashkernel is configured
ls -la /var/crash/
```

---

## 5. Root Cause Summary Matrix

| Observed Log Pattern | Primary Root Cause | Actionable Next Step |
| :--- | :--- | :--- |
| `journalctl -b -1` halts mid-operation with zero shutdown logs | CPU hardware PROCHOT cut-off / PSU OCP trip / Power outage | Clean mini PC fans/heatsink, check thermal paste, verify power brick capacity, inspect container CPU workloads |
| `thermal_zoneX: critical temperature reached` | Software-governed ACPI thermal poweroff | Adjust fan profiles, reduce background transcode concurrency, improve room ventilation |
| ACPI Power Button / Signal logged | Physical power button press, UPS shutdown daemon (`nut`, `apcupsd`) | Check physical cables, UPS daemon battery thresholds, cron tasks |
| Kernel Panic / MCE entries | RAM instability, faulty CPU silicon, kernel bug | Run Memtest86+, check memory timings, review recent kernel updates |
