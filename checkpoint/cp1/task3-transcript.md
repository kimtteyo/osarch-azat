# Task 3: Transcript (office-srv, evidence pack of Mon 2026-11-16 ~09:42 UTC)

| # | Evidence file (command) | What I expected | What I found | What I concluded |
|---|-------------------------|-----------------|--------------|------------------|
| 1 | 00-README.txt | list of files, the command behind each | 22 files, collected over SSH as aigerim | I work from files, not the live server. |
| 2 | 01 (hostnamectl), 02 (uptime) | what kind of machine, how long up | Ubuntu 24.04.1 VM on VirtualBox, up 6 d 23 h, Boot ID 9b2d61f0... | Last boot was about Nov 9 09:50. That Boot ID is the last boot in file 11, so there has been no reboot since. |
| 3 | 05 (systemctl --failed) | nightly-report failing | two failed units: legacy-sync and nightly-report | Two leads. Only nightly-report is named in the ticket, but I check both. |
| 4 | 06 (systemctl list-timers) | timer dead or never scheduled (the "scheduler" is suspect) | nightly-report.timer is active: last run 09:42:01, next 09:44:01 | The timer fires every 2 minutes, as the accountant said. **Dead end: timer ruled out.** The fault is in what it starts. |
| 5 | 08 (systemctl cat service + timer) | typo or wrong path in ExecStart | ExecStart=/usr/local/bin/nightly-report.sh, Type=oneshot, OnBootSec=1min, OnUnitActiveSec=2min | Unit files look correct. Next check: why does that path fail? |
| 6 | 07 (systemctl status nightly-report) | an exit code and a reason | status=203/EXEC, "Failed to execute ...: No such file or directory", CPU 2 ms | systemd could not start the program at all, so the script never ran. Hypothesis 1: the file is missing. |
| 7 | 13 (ls -l /usr/local/bin) | empty directory if the file is missing | file exists: -rwxr-xr-x root, 91 bytes, modified Nov 9 14:20 | **Hypothesis 1 ruled out.** Hypothesis 2 (permissions) is also ruled out: x bit set, and a permission problem would say "Permission denied". The message is misleading. mtime 14:20 will matter. |
| 8 | 09 (journalctl -u nightly-report) | when failures began | success every 2 min through 14:18:01 on Nov 9, first failure 14:20:01, same error every run since | Broke between 14:18 and 14:20 on Nov 9. Combined with #7 (file modified 14:20), the replaced file is the suspect. |
| 9 | 14 (ls -l /var/log), 15 (tail nightly-report.log) | latest log entries | last entry Mon Nov 9 14:18:01, log mtime 14:18. Entries hold `date` + `df` only, no `free -h` | Log stopped because the script stopped, not because the log is unwritable. The old script had no `free -h`, so the "update" added it. |
| 10 | 03 (df -h), 04 (free -h) | disk full or no memory | / 48% used, 5.8 G free; RAM 1.5 Gi available, swap unused | **Dead end: resources ruled out.** A full disk would also not give 203/EXEC. |
| 11 | 10 (status legacy-sync), 11 (journalctl legacy-sync) | a related failure | ExecStart=/bin/false, "no longer used", fails once per boot: Sep 14, Oct 2, Oct 19, Nov 9 09:51 | **Dead end: unrelated.** It has failed since September and ran at boot, while nightly-report worked until 14:18. It is noise for this ticket. |
| 12 | 21 (apt history) | something that changed | Nov 9 09:38-09:41 full-upgrade: bash, systemd, kernel, openssh; reboot afterwards | Hypothesis 3: the upgrade broke exec. Test: the same unit and script succeeded for about 4.5 h after the upgrade and reboot (#8). **Ruled out as the cause.** |
| 13 | 12 (journalctl -p err -b) | other errors explaining it | vboxguest/vmwgfx lines at boot, legacy-sync, nightly-report | Nothing new. The vbox/vmwgfx lines are VM guest noise. |
| 14 | 22 (bash history, aigerim) | what was done on Nov 9 | after reboot: `sudo cp ~/nightly-report.sh /usr/local/bin/...`, `chmod +x`, start, status, `ls -l`, `chmod 755`, start, status, exit | The script was replaced by a copy from the home directory (matches mtime 14:20). Two chmod attempts were a **dead end**: permissions were never wrong (#7). The cause was never found. |
| 15 | 16 (cat nightly-report.sh) | syntax error or wrong command | three correct-looking lines, `#!/bin/bash`, appends date, `df -h /`, `free -h` to the log | The text is fine by eye, so something invisible must be wrong. |
| 16 | 19 (run by hand) | runs, or a syntax error | `cannot execute: required file not found`; sudo: `No such file or directory` | Same error outside systemd, so unit and timer are cleared. This bash message means the interpreter on the shebang line was not found. |
| 17 | 20 (ls -l /bin/bash) | /bin/bash missing | exists, rwxr-xr-x, 1446024 bytes | The interpreter exists, so the shebang must name something other than `/bin/bash`. Look at the exact bytes. |
| 18 | 17 (cat -A) | hidden characters | every line ends in `^M$`, including `#!/bin/bash^M$` | The file has Windows (CRLF) line endings. |
| 19 | 18 (head -1 ... \| od -c) | confirm line 1 | `# ! / b i n / b a s h \r \n`, 13 bytes | The kernel looks for the interpreter `/bin/bash\r`, which does not exist, so it returns ENOENT. Byte check: 13 + 18 + 60 = 91 bytes, equal to the size in #7. Without the 3 CRs it would be 88. |

## Root cause

`/usr/local/bin/nightly-report.sh` was replaced on Nov 9 at 14:20 with a copy that has Windows CRLF line endings. The shebang line therefore names `/bin/bash\r`, which does not exist, so exec fails with "No such file or directory" (status 203/EXEC) although the file is present. Evidence: 17 and 18 (`^M`, `\r\n`), 13 (91 bytes, mtime 14:20), 09 (first failure 14:20:01), 20 (bash is present), 19 (fails by hand too).

## Fix

Run as aigerim on office-srv:

```bash
# 1. keep the broken file as evidence
sudo cp -p /usr/local/bin/nightly-report.sh /root/nightly-report.sh.crlf

# 2. convert CRLF to LF (sed -i keeps owner and mode)
sudo sed -i 's/\r$//' /usr/local/bin/nightly-report.sh

# 3. fix the source copy too, so a later "cp" does not bring the fault back
sed -i 's/\r$//' ~/nightly-report.sh

# 4. check the result
file /usr/local/bin/nightly-report.sh
stat -c '%s bytes, mode %a, owner %U' /usr/local/bin/nightly-report.sh
cat -A /usr/local/bin/nightly-report.sh

# 5. clear the failed state and run once now
sudo systemctl reset-failed nightly-report.service
sudo systemctl start nightly-report.service
```

## Verification

| Check | Command | Expected output |
|-|-|-|
| Line endings gone | `file /usr/local/bin/nightly-report.sh` | `Bourne-Again shell script, ASCII text executable` (no "with CRLF line terminators") |
| Size, mode | `stat -c '%s bytes, mode %a, owner %U' ...` | `88 bytes, mode 755, owner root` |
| No `^M` | `cat -A /usr/local/bin/nightly-report.sh` | lines end in `$` only |
| Runs by hand | `sudo /usr/local/bin/nightly-report.sh; echo $?` | no output, `0` |
| Service ran | `systemctl status nightly-report.service` | `inactive (dead)`, `ExecStart=... (code=exited, status=0/SUCCESS)` |
| Log written | `tail -n 12 /var/log/nightly-report.log` | new block with the current date, the `df` line and the `free -h` lines (`Mem:`, `Swap:`) |
| Timer keeps working | wait 5 min, then `journalctl -u nightly-report.service --since "10 min ago" --no-pager` | `Finished nightly-report.service` every 2 minutes, no 203/EXEC |
| No new failures | `systemctl --failed` | only `legacy-sync.service` (unrelated, pre-existing) |

**After a reboot:**

```bash
sudo reboot
# reconnect, then:
uptime -s                                     # a time after the fix
systemctl is-enabled nightly-report.timer     # enabled
# wait about 3 minutes (OnBootSec=1min + first run)
systemctl list-timers nightly-report.timer    # NEXT and LAST are after the boot time
tail -n 12 /var/log/nightly-report.log        # new blocks stamped after the boot
cat -A /usr/local/bin/nightly-report.sh       # still no ^M
```

The fix survives a reboot because it is a change to the file on disk, and the timer unit is installed under `timers.target`.

## Notes for the accountant

- Reports from Nov 9 14:20 until the fix were never written and cannot be back-filled, because the script only records the current state.
- Separate tickets, not part of this fix:
  - `legacy-sync.service` (`ExecStart=/bin/false`) can be disabled once the owner agrees.
  - The timer is still on its 2-minute test schedule, so it will need a real nightly schedule (`OnCalendar=`).
