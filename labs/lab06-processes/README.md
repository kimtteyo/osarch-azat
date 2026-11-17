# Lab 6 — Live processes and memory pressure

Pair: none                    Driver first half: Azat Zhansaya
Machine: Ubuntu VM (`lab01`, 1.6 GiB RAM, 2.0 GiB Swap)
Date: 2026-11-17

## What I did

1. Sampled baseline memory, applied sustained 2500 MB VM pressure (`stress-ng`) in the background for 60s, and logged `free -h` at 15s intervals:

```bash
echo "=== BEFORE ===" > memory-pressure.txt
free -h >> memory-pressure.txt
stress-ng --vm 1 --vm-bytes 2500M --vm-keep -t 60s > stress.log 2>&1 &
for i in 1 2 3; do
  sleep 15
  echo "=== DURING (t=$((i*15))s) ===" >> memory-pressure.txt
  free -h >> memory-pressure.txt
done
wait
echo "=== AFTER ===" >> memory-pressure.txt
free -h >> memory-pressure.txt
```

```text
=== BEFORE ===
Mem:           1.6Gi       472Mi       771Mi       1.3Mi       502Mi       1.1Gi
Swap:          2.0Gi        60Ki       2.0Gi
=== DURING (t=30s) ===
Mem:           1.6Gi       1.5Gi        68Mi       1.1Mi        76Mi        30Mi
Swap:          2.0Gi       1.3Gi       681Mi
=== AFTER ===
Mem:           1.6Gi       395Mi       1.2Gi        44Ki       118Mi       1.2Gi
Swap:          2.0Gi        93Mi       1.9Gi
```

2. Triggered the kernel OOM killer by allocating 5 GB (exceeding 1.6 GiB RAM + 2.0 GiB Swap = 3.6 GiB) and extracted kernel OOM events:

```bash
stress-ng --vm 1 --vm-bytes 5G --vm-keep -t 60s
sudo journalctl -k | grep -i -E "out of memory|oom|killed process" > kernel-log-extract.txt
```

```text
Nov 17 14:59:04 lab01 kernel: stress-ng-vm invoked oom-killer: gfp_mask=0x140dca(GFP_HIGHUSER_MOVABLE|__GFP_ZERO|__GFP_COMP), order=0, oom_score_adj=1000
Nov 17 14:59:05 lab01 kernel: Out of memory: Killed process 2976 (stress-ng-vm) total-vm:3620128kB, anon-rss:1325180kB, file-rss:584kB, shmem-rss:0kB, UID:1000 pgtables:6596kB oom_score_adj:1000
Nov 17 14:59:21 lab01 kernel: Out of memory: Killed process 2980 (stress-ng-vm) total-vm:3620128kB, anon-rss:1333096kB, file-rss:584kB, shmem-rss:0kB, UID:1000 pgtables:6596kB oom_score_adj:1000
Nov 17 14:59:42 lab01 kernel: Out of memory: Killed process 2981 (stress-ng-vm) total-vm:3620128kB, anon-rss:1336372kB, file-rss:584kB, shmem-rss:0kB, UID:1000 pgtables:6600kB oom_score_adj:1000
```

3. Copied the captured logs from the VM to the local repository `evidence/` directory via `scp`:

```powershell
scp zhansaya@192.168.100.130:~/memory-pressure.txt .
scp zhansaya@192.168.100.130:~/kernel-log-extract.txt .
```

## Result

- **Swap pressure (2500 MB):** Reclaimed page cache (`buff/cache` dropped from `502Mi` to `71Mi`) and paged out `1.4Gi` of anonymous memory into swap while `available` RAM fell from `1.1Gi` to `28Mi`. The system remained responsive and completed without triggering OOM.
- **OOM exhaustion (5 GB):** Once virtual memory hit ~3.45 GiB (`total-vm: 3620128kB`, `anon-rss: ~1.33 GiB`), the kernel invoked `oom-killer` three times (`PID 2976`, `2980`, `2981`). Because `stress-ng-vm` sets `oom_score_adj=1000`, the kernel terminated the worker processes while keeping `sshd` and core system daemons alive; the parent `stress-ng` supervisor respawned workers until the 60s timer expired.

## What did not work the first time

- **What I saw:** On the first run, `memory-pressure.txt` showed almost no swap usage (`Swap: 60Ki` used, `Mem free: 889Mi`) during the `DURING` phase, and `kernel-log-extract.txt` was completely empty.
- **What it turned out to be:** Two issues caused this: (1) `stress-ng` ran in the foreground, so `free -h` executed *after* the workload had already exited (`successful run completed in 1 min 30.23 secs`), and (2) percentage-based allocation (`120%`) was calculated against *available* RAM (`627.79 MB` -> `753.35 MB`), which never exhausted physical memory or swap.
- **What I did about it:** Ran `stress-ng` in the background (`&`) with a 15-second `sleep` loop for synchronized sampling, switched to explicit byte sizes (`2500M` for swap saturation, `5G` to exceed the 3.6 GiB RAM + swap limit), and extracted the OOM events with `sudo journalctl -k`.

## Evidence

- [evidence/memory-pressure.txt](evidence/memory-pressure.txt) — proves RAM exhaustion (`available` dropping to `28Mi`) and active swap usage (`1.4Gi`) during the 2500 MB `stress-ng` run.
- [evidence/kernel-log-extract.txt](evidence/kernel-log-extract.txt) — proves kernel OOM killer invocation and termination of `stress-ng-vm` workers (`PID 2976`, `2980`, `2981`, `oom_score_adj=1000`) under the 5 GB allocation.
- [evidence/evidence-linux-process.txt](evidence/evidence-linux-process.txt) — proves live process inspection and process tree/state capture on the target Linux host.