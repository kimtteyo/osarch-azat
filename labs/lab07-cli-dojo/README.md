# Lab 7 — CLI Dojo

- **Week:** 9 | **Outcome:** CLO 4
- **Host:** `DESKTOP-P17KP7A`
- **User:** `desktop-p17kp7a\zhansaya`
- **OS:** Microsoft Windows [Version 10.0.26300.9457]
- **Solved:** 20 / 20 (no graphical tools used)

## Challenges

| # | Challenge | Command | Time |
|---|-----------|---------|------|
| 1 | Print the full path of the directory you are in. | `cd` | 00:04 |
| 2 | Show the name of this computer and the account you are logged in as. | `hostname & whoami` | 00:07 |
| 3 | With one command, create `C:\dojo\logs\old` and `C:\dojo\backup`. | `mkdir C:\dojo\logs\old C:\dojo\backup` | 00:10 |
| 4 | With one line, create `C:\dojo\notes.txt` containing "dojo started" on the first line and the current time on the second. | `(echo dojo started& time /t) > C:\dojo\notes.txt` | 00:13 |
| 5 | Show the full path of the ping program that runs when you type `ping`. | `where ping` | 00:16 |
| 6 | Show your IPv4 address, default gateway and DNS servers — and no other lines of ipconfig's output. | `ipconfig /all \| findstr /c:"IPv4 Address" /c:"Default Gateway" /c:"DNS Servers"` | 00:22 |
| 7 | Save the list of running processes to `C:\dojo\procs.txt`, then print how many lines the file has. | `tasklist > C:\dojo\procs.txt` & `type C:\dojo\procs.txt \| find /c /v ""` | 00:25 |
| 8 | Start Notepad from the shell, find its PID, and end it by PID. | `start notepad` → `tasklist \| findstr /i notepad` → `taskkill /PID 5104` | 00:29 |
| 9 | Print only the ERROR lines of `app.log`. | `findstr /b "ERROR" C:\dojo\logs\app.log` | 00:32 |
| 10 | Print how many lines of `app.log` are not INFO lines. A number, not the lines. | `findstr /v /b "INFO" C:\dojo\logs\app.log \| find /c /v ""` | 00:35 |
| 11 | Copy `app.log` into `C:\dojo\backup`, then show the size of both copies with one `dir` command. | `copy C:\dojo\logs\app.log C:\dojo\backup` & `dir C:\dojo\logs\app.log C:\dojo\backup\app.log` | 00:38 |
| 12 | Run `dir C:\nothing-here` so that nothing appears on screen and the error message ends up in `C:\dojo\errors.txt`. | `dir C:\nothing-here > nul 2> C:\dojo\errors.txt` | 00:41 |
| 13 | In one line: ping your gateway once and print "gateway OK" if it answers, otherwise "gateway DOWN". Nothing else on screen. | `ping -n 1 -w 1000 192.168.100.2 \| find "TTL=" >nul && echo gateway OK \|\| echo gateway DOWN` | 00:44 |
| 14 | Print every line of `app.log` that mentions `user1`, case-insensitive, with line numbers. Explain why there is more than one. | `findstr /i /n "user1" C:\dojo\logs\app.log` | 00:47 |
| 15 | Print `scores.txt` sorted from the highest score to the lowest. | `sort /r C:\dojo\scores.txt` | 00:49 |
| 16 | List only the processes using more than 50 MB of memory. | `tasklist /fi "MEMUSAGE gt 51200"` | 00:52 |
| 17 | Find which process is listening on TCP port 135. Give its name, not just its PID. | `netstat -ano \| findstr ":135 " \| findstr LISTENING` & `tasklist /svc /fi "PID eq 404"` | 00:55 |
| 18 | Make the name `dojo.test` resolve to `127.0.0.1` on this machine, prove it with `ping`, then undo the change and prove that too. | `set H=C:\Windows\System32\drivers\etc\hosts` → `copy %H% %TEMP%\hosts.bak` → `echo 127.0.0.1 dojo.test>> %H%` → `ipconfig /flushdns` → `ping -n 1 dojo.test` → `copy /y %TEMP%\hosts.bak %H%` → `ipconfig /flushdns` → `ping -n 1 dojo.test` | 01:02 |
| 19 | List every file (not directory) under `C:\dojo`, including subfolders, with its path and its size in bytes. | `for /r C:\dojo %f in (*) do @echo %f %~zf` | 01:06 |
| 20 | Mirror `C:\dojo\logs` to `C:\dojo\backup\logs` with a log file at `C:\dojo\robocopy.log`. Add a file to the source, mirror; delete it, mirror; mirror once more. Print the exit code after each run and explain each one. | `robocopy C:\dojo\logs C:\dojo\backup\logs /MIR /LOG+:C:\dojo\robocopy.log /TEE` & `echo %errorlevel%` (4 runs, adding then deleting `C:\dojo\logs\extra.txt`) | 01:12 |

---

## Explanations

### Challenge 14 — Why `user1` matched 13 lines
`findstr` matches **substrings** by default, not whole words. Searching for `"user1"` matches:
- `user1` in `INFO` (line 1), `ERROR` (line 31), and `WARN` (line 38) — **3 lines**
- `user10` through `user19` in `INFO` (lines 10–19) — **10 lines**

Total: **13 lines**.

### Challenge 17 — Process on TCP Port 135
`netstat -ano` showed TCP port `135` listening on PID `404`. Running `tasklist /svc /fi "PID eq 404"` identified the process as **`svchost.exe`** hosting the **`RpcEptMapper`** and **`RpcSs`** services.

### Challenge 20 — Robocopy Exit Codes
`robocopy` returns a **bitmask exit code** (`0`–`7` mean success; `8` or higher mean failure):

| Run | Action | Exit Code | Explanation |
|-----|--------|-----------|-------------|
| 1 | Initial mirror of `C:\dojo\logs` to `C:\dojo\backup\logs` | `1` | Files were copied (`app.log`). |
| 2 | Added `C:\dojo\logs\extra.txt` and mirrored | `1` | The new file `extra.txt` was copied to the destination. |
| 3 | Deleted `C:\dojo\logs\extra.txt` and mirrored | `2` | `/MIR` detected an extra file in the destination (`extra.txt`) and purged it; nothing was copied. |
| 4 | Mirrored again with no changes | `0` | Source and destination already matched; no files were copied or deleted. |

---

## Evidence

- Combined command output: [`evidence/output-all-challenges.txt`](evidence/output-all-challenges.txt)
- Terminal screenshots: [`evidence/screenshots/`](evidence/screenshots/) (`ch01.png` – `ch20.png`)
