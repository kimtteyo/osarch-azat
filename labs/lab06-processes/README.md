# Lab 6 — Live processes and memory pressure

**Pair:** none
**Driver first half:** Azat Zhansaya
**Machines:**
- Ubuntu VM (`lab01`, 1.6 GiB RAM, 2.0 GiB swap)
- Windows 11 VM (`DESKTOP-P17KP7A`, Windows 11 Enterprise Evaluation, version 10.0.26300, build 26300)

**Dates:** memory-pressure runs on 2026-11-17; process-tool comparison and event-log check on 2026-11-26.

---

## What I did

### Part 1 — Memory pressure on Ubuntu

Sampled baseline memory, applied sustained 2500 MB VM pressure (`stress-ng`) in the background for 60 s, and logged `free -h` at 15 s intervals:

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

Samples from `memory-pressure.txt`:

| Sample | used | free | buff/cache | available | Swap used |
|---|---|---|---|---|---|
| BEFORE | 472Mi | 771Mi | 502Mi | 1.1Gi | 60Ki |
| DURING t=15s | 1.5Gi | 65Mi | 103Mi | 40Mi | 1.4Gi |
| DURING t=30s | 1.5Gi | 68Mi | 76Mi | 30Mi | 1.3Gi |
| DURING t=45s | 1.5Gi | 68Mi | 71Mi | 28Mi | 1.4Gi |
| AFTER | 395Mi | 1.2Gi | 118Mi | 1.2Gi | 93Mi |

Then I triggered the kernel OOM killer by allocating 5 GB (more than 1.6 GiB RAM + 2.0 GiB swap = 3.6 GiB) and extracted the kernel OOM events:

```bash
stress-ng --vm 1 --vm-bytes 5G --vm-keep -t 60s
sudo journalctl -k | grep -i -E "out of memory|oom|killed process" > kernel-log-extract.txt
```

```
Nov 17 14:59:04 lab01 kernel: stress-ng-vm invoked oom-killer: gfp_mask=0x140dca(GFP_HIGHUSER_MOVABLE|__GFP_ZERO|__GFP_COMP), order=0, oom_score_adj=1000
Nov 17 14:59:05 lab01 kernel: Out of memory: Killed process 2976 (stress-ng-vm) total-vm:3620128kB, anon-rss:1325180kB, file-rss:584kB, shmem-rss:0kB, UID:1000 pgtables:6596kB oom_score_adj:1000
Nov 17 14:59:21 lab01 kernel: Out of memory: Killed process 2980 (stress-ng-vm) total-vm:3620128kB, anon-rss:1333096kB, file-rss:584kB, shmem-rss:0kB, UID:1000 pgtables:6596kB oom_score_adj:1000
Nov 17 14:59:42 lab01 kernel: Out of memory: Killed process 2981 (stress-ng-vm) total-vm:3620128kB, anon-rss:1336372kB, file-rss:584kB, shmem-rss:0kB, UID:1000 pgtables:6600kB oom_score_adj:1000
```

Copied the logs from the VM to the local repository `evidence/` directory:

```bash
scp zhansaya@192.168.100.130:~/memory-pressure.txt .
scp zhansaya@192.168.100.130:~/kernel-log-extract.txt .
```

### Part 2 — Live process inspection in three tools

I inspected one long-running process on each system and recorded PID, parent, memory and handles / file descriptors.

**Linux (Ubuntu VM):** `sleep 3000 &` (PID 2544), inspected with:

```bash
sleep 3000 &
P=$!
{ ps -o pid,ppid,stat,rss,vsz,cmd -p $P
  ls -l /proc/$P/fd
  ps -o pid,cmd -p $$
  grep -E "VmRSS|RssAnon|RssFile|RssShmem" /proc/$P/status
} > evidence-linux-process.txt
```

Output (saved to `evidence/evidence-linux-process.txt`):

```
    PID    PPID STAT   RSS    VSZ CMD
   2544    1994 S     8256  17652 sleep 3000
total 0
lrwx------ 1 zhansaya zhansaya 64 Nov 26 18:32 0 -> /dev/tty1
lrwx------ 1 zhansaya zhansaya 64 Nov 26 18:32 1 -> /dev/tty1
lrwx------ 1 zhansaya zhansaya 64 Nov 26 18:32 2 -> /dev/tty1
    PID CMD
   1994 -bash
VmRSS:      8256 kB
RssAnon:    1264 kB
RssFile:    6992 kB
RssShmem:      0 kB
```

and with `htop` (VIRT / RES / SHR / MEM%).

**Windows (Windows 11 VM):** `Notepad.exe` (PID 1420, Microsoft Store Notepad 11.2609.11.0 from `C:\Program Files\WindowsApps\...`), started by typing `notepad` in PowerShell. Inspected in Task Manager (Details tab, extra columns: Handles, Working set, Active private working set, Commit size) and in Sysinternals Process Explorer (columns Private Bytes / Working Set, Handles lower pane, Properties → Image). The Task Manager and Process Explorer readings were taken one after another, not in the same second.

To see which executable the `notepad` command actually starts:

```powershell
(Get-Command notepad).Source
```

Output: `C:\WINDOWS\system32\notepad.exe`

### Part 3 — Windows event log (Step 5)

Searched the System log for Event 2004 from `Microsoft-Windows-Resource-Exhaustion-Detector`:

```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; Id=2004; ProviderName='Microsoft-Windows-Resource-Exhaustion-Detector'} -MaxEvents 5
```

To check that the provider name is correct (so that an empty result is a real result and not a typo), I listed the provider:

```powershell
Get-WinEvent -ListProvider Microsoft-Windows-Resource-Exhaustion-Detector
```

and also ran the query by ID only, to see what else uses ID 2004:

```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; Id=2004} -MaxEvents 5
```

---

## Result

### Memory pressure

**Swap pressure (2500 MB):** the kernel reclaimed page cache (buff/cache dropped from 502Mi to 71Mi at t=45s) and paged anonymous memory out to swap (1.4Gi at t=15s, 1.3Gi at t=30s, 1.4Gi at t=45s) while available RAM fell from 1.1Gi to 28Mi at t=45s. RAM + swap together were still enough for 2500 MB, so the run finished after 60 s without triggering OOM. After the run, swap usage dropped to 93Mi and available RAM recovered to 1.2Gi.

**OOM exhaustion (5 GB):** 5 GB does not fit into 1.6 GiB RAM + 2.0 GiB swap. Once both RAM and swap were full, the kernel could not find a free page for the worker's next allocation and invoked the OOM killer. The OOM killer is triggered by running out of physical pages (RAM + swap), not by a process reaching some virtual-memory size. It fired three times (PIDs 2976, 2980, 2981). At each kill the worker had `total-vm` 3620128 kB (about 3.45 GiB of mapped address space), of which `anon-rss` (about 1.33 GiB) was resident in RAM; the rest of the pages it had touched were in swap. `stress-ng-vm` sets `oom_score_adj=1000`, which makes its workers the preferred victims, so the kernel killed them and no other process appears in the OOM log. The parent `stress-ng` supervisor respawned workers (new PIDs each time) until the 60 s timer expired.

### Three-tool comparison

| | Task Manager (Details) | Process Explorer | Linux (`ps` / `htop` / `/proc`) |
|---|---|---|---|
| Process | Notepad.exe, PID 1420 | Notepad.exe, PID 1420 | `sleep 3000`, PID 2544 |
| Parent | not shown | `<Non-existent Process>` (2632) | PPID 1994 = `-bash` (alive) |
| Resident memory | Working set 100,308 K | Working Set 94,640 K | RSS 8256 K (`ps`), VmRSS 8256 K (`/proc`), RES 8256 K (`htop`) |
| Private resident memory | Active private working set 26,040 K | not shown in the columns I used | RssAnon 1264 K (`/proc`) |
| Shared resident memory | not shown | not shown in the columns I used | RssFile 6992 K + RssShmem 0 K (`/proc`), SHR 6992 K (`htop`) |
| Committed / virtual memory | Commit size 38,060 K | Private Bytes 38,112 K | VSZ 17652 K (`ps`), VIRT 17652 K (`htop`) |
| Handles / fds | 874 handles | 855 handles | 3 fds (0, 1, 2 → `/dev/tty1`) |

### Where the tools disagree, and why

- **Working set (100,308 K vs 94,640 K).** Both columns show pages of the process that are currently resident in RAM, including shared DLL pages. Windows trims and refaults pages all the time, so this number moves. Two Task Manager snapshots of the same process, taken a few moments apart, already differed (100,380 K and 100,308 K). The gap to Process Explorer (about 5.7 MB) is larger than that drift. The Process Explorer reading was taken after the Task Manager one, not in the same second, so I believe timing is the main reason, but I did not verify this by taking both readings at the same moment.
- **Private resident memory (26,040 K vs about 1264 K).** These count only private pages currently in RAM and leave out shared pages (for example system DLLs on Windows, shared libraries like libc on Linux). That is why they are far below the total working set / RSS. On Linux, `/proc/2544/status` splits RSS into parts: VmRSS 8256 K = RssAnon 1264 K (private anonymous memory: heap, stack) + RssFile 6992 K (file-backed pages: the `sleep` binary and shared libraries such as libc) + RssShmem 0 K. `htop` SHR is RssFile + RssShmem, so RES − SHR gives the same 1264 K as RssAnon. `sleep` is almost entirely shared library code, which is why its private part is so small.
- **Commit size vs Private Bytes (38,060 K vs 38,112 K).** These are the same quantity under two names: private virtual memory the process has committed, resident or not. The 52 K difference is drift between the two readings. It is larger than the private working set because some committed pages are paged out or not touched yet. On Linux the closest relatives are VSZ/VIRT, but those also include shared and mapped-only memory, so they are not equal to Private Bytes.
- **Linux: ps vs htop.** `ps` RSS/VSZ (8256 K and 17652 K) and `htop` RES/VIRT (8256 K and 17652 K) agree exactly because both read the same kernel counters from `/proc`. `htop` adds SHR (6992 K), the shared part of RES, which equals RssFile + RssShmem from `/proc/2544/status`.
- **Parent process.** Task Manager does not show the parent. Process Explorer shows `<Non-existent Process>(2632)`: Windows stores the parent PID at creation and does not change it when the parent exits, so the number is left pointing at a process that no longer exists. In my first attempt (Notepad PID 2616) Process Explorer showed `explorer.exe (5376)` as the parent, which was alive. This time I typed `notepad` in PowerShell. The PowerShell window stayed open the whole time, so the missing parent is not PowerShell. The `notepad` command resolves to `C:\WINDOWS\system32\notepad.exe` (`Get-Command` output above), but the running process is the Store Notepad from `C:\Program Files\WindowsApps\...` (Properties → Image). So the program I started is not the program that is running: the System32 `notepad.exe` acts as a short-lived launcher that starts the Store Notepad and then exits. That launcher is the most likely owner of PID 2632. I did not catch PID 2632 while it was running, so this part is an inference, not a direct observation. On Linux the parent of `sleep` is `-bash` (1994), which is alive; if bash exited, the kernel would reparent `sleep` to `init`/`systemd` and the PPID would change.
- **Handles (874 vs 855) and fds (3).** The 19-handle gap between Task Manager and Process Explorer is most likely timing again, because handle counts change as the process runs (an earlier Task Manager snapshot showed 877). Handles and fds are not directly comparable numbers: a Windows handle can refer to files, registry keys, events, mutexes, sections, threads, tokens and more, while a Linux fd refers to files, pipes, sockets and similar. The 3 fds of `sleep` are stdin, stdout and stderr, all pointing to `/dev/tty1` (see `ls -l /proc/2544/fd` output above). A fairer comparison would be only the File-type handles in Process Explorer; I did not count them.

### Windows event log (Step 5)

- Event 2004 from `Microsoft-Windows-Resource-Exhaustion-Detector`: **not found** (`No events were found that match the specified selection criteria`).
- `Get-WinEvent -ListProvider Microsoft-Windows-Resource-Exhaustion-Detector` found the provider (LogLinks: `System`, `Microsoft-Windows-Resource-Exhaustion-Detector/Operational`), so the provider name in the query is correct and the empty result is a real result.
- The ID-only query returned one event with ID 2004, from `Microsoft-Windows-Setup`: "Successfully logged OS information", dated 10/23/2026 12:03:23 AM. It is unrelated to memory. Event IDs are only unique per provider, so the query has to filter on both `ProviderName` and `Id`.
- **Likely explanation (not verified):** the Resource-Exhaustion-Detector reports when commit charge approaches the commit limit. In this lab Notepad used about 38 MB, and Process Explorer's status bar showed Commit Charge of 79.08% and later 75.08% (visible in the Process Explorer screenshots), so nothing pushed the system to the limit. I did not run an allocation tool such as Sysinternals `testlimit -m` to force the event, so this remains an explanation and not a test result.

---

## What did not work the first time

**Memory run**

- **What I saw:** on the first run, `memory-pressure.txt` showed almost no swap usage (`Swap: 60Ki` used, `Mem` free 889Mi) during the DURING phase, and `kernel-log-extract.txt` was completely empty.
- **What it turned out to be:** two issues: (1) `stress-ng` ran in the foreground, so `free -h` executed after the workload had already exited (the run took 1 min 30.23 s), and (2) percentage-based allocation (120%) was calculated against available RAM (627.79 MB → 753.35 MB), which never exhausted physical memory or swap.
- **What I did about it:** ran `stress-ng` in the background (`&`) with a 15-second sleep loop for synchronized sampling, switched to explicit byte sizes (`2500M` for swap saturation, `5G` to exceed the 3.6 GiB RAM + swap limit), and extracted the OOM events with `sudo journalctl -k`.

**Linux process inspection**

- **What I saw:** when I went back to collect the `ps` output for `sleep` (PID 2056), `ps -p 2056` printed nothing and bash reported `[1]+ Done sleep 3000`.
- **What it turned out to be:** `sleep 3000` lasts 3000 s = 50 min, and that time had passed. The process had exited normally.
- **What I did about it:** started a new `sleep 3000 &` (PID 2544) in the same bash (PID 1994) and captured `ps`, `/proc/2544/fd` and `/proc/2544/status` in one command block right after starting it, then took the `htop` screenshot for the same PID.

**Windows measurements**

- **What I saw:** my first Task Manager and Process Explorer screenshots were of Notepad PID 2616, and the numbers did not line up when I compared them. The Event 2004 query with the provider name returned nothing.
- **What it turned out to be:** the screenshots had been taken at different times, so they showed the process in different states. The empty query result was a real result and not a typo in the provider name: `Get-WinEvent -ListProvider` found the provider.
- **What I did about it:** restarted Notepad (new PID 1420), took the Task Manager and Process Explorer readings one after another for the same process, replaced the old screenshots, checked the provider name with `-ListProvider`, and re-ran the event query by ID only to see what else uses ID 2004.

---

## Evidence

- [evidence/memory-pressure.txt](evidence/memory-pressure.txt) — proves RAM exhaustion (available dropping to 28Mi) and active swap usage (1.4Gi) during the 2500 MB `stress-ng` run. The `=== OOM RUN ===` line at the end of the file is empty; the OOM evidence is in `kernel-log-extract.txt`.
- [evidence/kernel-log-extract.txt](evidence/kernel-log-extract.txt) — proves kernel OOM killer invocation and termination of `stress-ng-vm` workers (PIDs 2976, 2980, 2981, `oom_score_adj=1000`) under the 5 GB allocation.
- [evidence/evidence-linux-process.txt](evidence/evidence-linux-process.txt) — `ps` output for `sleep 3000` (PID 2544, PPID 1994, RSS 8256 K, VSZ 17652 K), `ls -l /proc/2544/fd` (fds 0, 1, 2 → `/dev/tty1`), `ps` for the parent `-bash` (PID 1994), and VmRSS / RssAnon / RssFile / RssShmem from `/proc/2544/status`.
- [evidence/linux-htop-tree.png](evidence/linux-htop-tree.png) — `htop` in tree mode (F5) on the Ubuntu VM showing `sleep 3000` (PID 2544) under `-bash` (PID 1994), with VIRT 17652, RES 8256, SHR 6992, MEM% 0.5. `htop` itself (PID 2603) is the other child of the same `-bash`.
- [evidence/windows-taskmgr-notepad.png](evidence/windows-taskmgr-notepad.png) — Windows Task Manager Details view of Notepad.exe (PID 1420): Working set 100,308 K, Active private working set 26,040 K, Commit size 38,060 K, 874 handles, x64.
- [evidence/windows-procexp-handles.png](evidence/windows-procexp-handles.png) — Sysinternals Process Explorer: Notepad.exe (PID 1420), Private Bytes 38,112 K, Working Set 94,640 K, the Handles lower pane, and Commit Charge 79.08% in the status bar.
- [evidence/windows-procexp-properties.png](evidence/windows-procexp-properties.png) — Notepad.exe (PID 1420) Properties → Image: parent `<Non-existent Process>(2632)`, user `DESKTOP-P17KP7A\zhansaya`, started 10:42:01 PM 11/26/2026, memory protections (DEP, ASLR, CFG), and Commit Charge 75.08% in the status bar.
- [evidence/windows-event-2004.txt](evidence/windows-event-2004.txt) — PowerShell output of the three `Get-WinEvent` commands from Part 3: empty result for Resource-Exhaustion-Detector, the `-ListProvider` result, and the unrelated `Microsoft-Windows-Setup` event with ID 2004.

- [evidence/windows-procexp-properties.png](evidence/windows-procexp-properties.png) — proves `Notepad.exe` (`PID 2616`) parent-child relationship, user context, and memory protections (DEP, ASLR, CFG).
