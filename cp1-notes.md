# CP1 — OSArch, weeks 1–7

> 60 min · 100 points · no VM, no admin rights · PowerShell + text editor + browser
> Task 1 Inventory 25 · Task 2 Plan 30 · Task 3 Diagnose 45 (**the transcript is worth more than the result**)
> Submit: `checkpoints/cp1/` → commit before minute 60 → **Copy permalink** → Canvas
> GitHub in the browser: **Add file → Create new file** → name it `checkpoints/cp1/README.md` (the slash creates the folder). Commit every 10–15 min.

---

## 0. Help — find the answer yourself

| Need | PowerShell | Linux |
|---|---|---|
| Find a command by keyword | `Get-Command *disk*` · `Get-Command -Noun *Process*` | `man -k disk` (= `apropos disk`) |
| Help + examples | `Get-Help Get-Volume -Examples` | `man lsblk` → `/word` to search, `n` next, `q` quit |
| One parameter | `Get-Help Get-Process -Parameter Id` | `lsblk --help` |
| Which fields an object has | `Get-CimInstance Win32_Processor \| Get-Member` | — |
| Show ALL fields | `... \| Format-List *` | — |
| Find a WMI/CIM class | `Get-CimClass Win32_*memory*` | — |
| Online (allowed) | learn.microsoft.com → cmdlet name | man7.org, manpages.ubuntu.com |

If `Get-Help` says help is not found → `Get-Help <cmd> -Online` (opens Microsoft Learn).
PowerShell version: `$PSVersionTable.PSVersion` (powershell.exe = 5.1, pwsh.exe = 7).

---

## 1. Task 1 — Inventory: paste this whole block into the PowerShell console

Writes `inventory.txt` with the command above each output (= evidence that shows the command). Errors such as Access denied go into the file too — that is your "what did not work". Paste it into the console rather than running a .ps1 (execution policy may block scripts).

```powershell
$o = "$PWD\inventory.txt"; Remove-Item $o -ErrorAction SilentlyContinue
function S([string]$t, [scriptblock]$c) {
  "`n=== $t`nPS> $c" | Out-File $o -Append -Encoding utf8
  try { & $c 2>&1 | Out-String -Width 200 | Out-File $o -Append -Encoding utf8 }
  catch { "ERROR: $_" | Out-File $o -Append -Encoding utf8 }
}
S 'CPU' { Get-CimInstance Win32_Processor | Format-List Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed }
S 'RAM total GiB' { [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1) }
S 'RAM modules' { Get-CimInstance Win32_PhysicalMemory | Format-Table DeviceLocator, @{n='GB';e={$_.Capacity/1GB}}, Speed, ConfiguredClockSpeed, PartNumber -AutoSize }
S 'RAM slots / max' { Get-CimInstance Win32_PhysicalMemoryArray | Format-List MemoryDevices, @{n='MaxGB';e={$_.MaxCapacityEx/1MB}} }
S 'RAM used/free now' { Get-CimInstance Win32_OperatingSystem | Format-List @{n='TotalGB';e={[math]::Round($_.TotalVisibleMemorySize/1MB,1)}}, @{n='FreeGB';e={[math]::Round($_.FreePhysicalMemory/1MB,1)}} }
S 'Disks' { Get-PhysicalDisk | Format-Table FriendlyName, MediaType, BusType, @{n='GB';e={[math]::Round($_.Size/1GB)}} -AutoSize }
S 'Disks (fallback)' { Get-CimInstance Win32_DiskDrive | Format-Table Model, InterfaceType, @{n='GB';e={[math]::Round($_.Size/1GB)}} -AutoSize }
S 'Free space' { Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Format-Table DeviceID, @{n='SizeGB';e={[math]::Round($_.Size/1GB)}}, @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB)}} -AutoSize }
S 'Partition style' { Get-Disk | Format-Table Number, FriendlyName, PartitionStyle -AutoSize }
S 'Firmware type' { $env:firmware_type }
S 'BIOS' { Get-CimInstance Win32_BIOS | Format-List Manufacturer, SMBIOSBIOSVersion, ReleaseDate }
S 'Board' { Get-CimInstance Win32_BaseBoard | Format-List Manufacturer, Product }
S 'Virtualization' { Get-CimInstance Win32_Processor | Format-List VirtualizationFirmwareEnabled, VMMonitorModeExtensions, SecondLevelAddressTranslationExtensions; "HypervisorPresent: " + (Get-CimInstance Win32_ComputerSystem).HypervisorPresent }
S 'OS' { Get-CimInstance Win32_OperatingSystem | Format-List Caption, Version, OSArchitecture }
notepad $o
```

Copy the file to the clipboard for GitHub: `Get-Content $o -Raw | Set-Clipboard`

**Read on screen only, never commit:** `systeminfo` (computer name, IP, email). Line at the bottom: *Hyper-V Requirements: Virtualization Enabled In Firmware: Yes* (Russian Windows: «Виртуализация включена во встроенном ПО: Да»). "A hypervisor has been detected" / «Обнаружена низкоуровневая оболочка» = already enabled → Yes.

### Task 1 traps
- Threads = NumberOfLogicalProcessors (Linux: `CPU(s)`). Hybrid Intel: P-core 2 threads, E-core 1 → i7-13700 = 8P+8E = 16 cores, 24 threads.
- RAM: total **+ number of modules + number of slots**. Empty slots = MemoryDevices − modules. The OS shows slightly less than the modules add up to (reserved for iGPU/firmware).
- Disk: size ≠ free space. "SSD" in the model name ≠ NVMe → look at BusType. Win32_DiskDrive reports NVMe as SCSI.
- Hyper-V/WSL 2 on → VirtualizationFirmwareEnabled may say False → check HypervisorPresent.
- PS 5.1: `>` writes UTF-16LE. Always `Out-File -Encoding utf8`.
- Bytes → GiB: `/1GB`. KB (Win32_OperatingSystem, MaxCapacityEx) → GiB: `/1MB`. 8589934592 B = 8 GiB.

### README table
| What | Value | Where I got it |
|---|---|---|
| CPU model | … | `Get-CimInstance Win32_Processor` |
| Cores / threads | … / … | same, NumberOfCores / NumberOfLogicalProcessors |
| RAM total / modules / slots | … GB / … / … | Win32_ComputerSystem / Win32_PhysicalMemory / Win32_PhysicalMemoryArray |
| RAM speed | … MT/s | Win32_PhysicalMemory Speed |
| Disk model / type / bus | … | `Get-PhysicalDisk` |
| Free space on VM volume | … GB | Win32_LogicalDisk FreeSpace |
| Firmware | UEFI / Legacy, version, date | `$env:firmware_type`, Win32_BIOS |
| Virtualization present / enabled | … | Win32_Processor, HypervisorPresent |

### Two questions about an unseen spec — answer template
**"Can it run two VMs?"** — step by step, a number at each step:
1. VT-x/AMD-V present **and** enabled? No → a 64-bit guest does not start at all (fix in UEFI: Intel Virtualization Technology / SVM Mode).
2. Threads: Σ vCPU vs host **threads**; leave the host ≥ 2.
3. RAM: free = total − host idle (Windows ~4–6 GB). Ubuntu Server 2 GB + Win 11 4 GB = 6 GB. More → guests start, but the host swaps.
4. Disk: free ≥ what thin disks will really write (25 + 64 GB declared). HDD → slow.
5. One-sentence conclusion + the named bottleneck.

**"What would you upgrade first?"** — bottleneck + is it upgradable at all:

| Bottleneck | Symptom | Check whether it is possible |
|---|---|---|
| RAM (almost always #1 for VMs) | everything slows at once, swapping | free slot? same DDR generation? soldered (laptop/Apple) → impossible |
| Single RAM module | half the bandwidth | add an identical one → dual channel (2×8 beats 1×16) |
| HDD / little free space | slow start, disk full | SSD; M.2 slot: M-key = NVMe, B+M = SATA |
| CPU | long jobs take minutes | socket + chipset + firmware; laptop BGA → impossible |
| VT-x off | guest won't start | not an upgrade but a UEFI setting — do it first |

---

## 2. Task 2 — Plan and justify

| | Ubuntu | Windows | Σ promised | Host | Ratio / verdict |
|---|---|---|---|---|---|
| vCPU | 2 | 2 | 4 | __ threads | 4/__ = __ : 1 |
| RAM | 2 GB | 4 GB | 6 GB | __ total − __ idle = __ free | 6 / __ |
| Disk (thin) | 25 GB | 64 GB | 89 GB | __ free | actually used now ~__ |
| Network | NAT | NAT | one vSwitch | — | guests see each other + internet |

- **Ratio** = promised ÷ available. CPU against threads. RAM against **free** RAM (total − idle).
- A justification is a number from the host: "4 GB of 16, because Windows holds 6 idle and I need a second guest".
- Never give one guest all host threads (it competes with the host and hypervisor → slower).
- Thin: grows as data is written; declared size = ceiling. Σ ceilings > free → host fills → guests get write errors / are paused. Deleting inside the guest doesn't shrink the file (needs compact).
- Snapshot `clean-install` **before** the experiment. Snapshot ≠ backup.

**What happens if…**
- RAM overcommitted + both guests busy → they start, then compression → host swap → everything slow.
- Σ vCPU > threads, all busy → slower, nothing crashes; `st` (steal) grows in the guest's `top`.
- Bridged on campus → MAC filtering silently drops it: no address, no error.
- Ping Ubuntu → Windows → Windows firewall drops it → add an ICMP rule, don't turn the firewall off.
- VT-x off → guest does NOT start (not "slower", not "32-bit").

**Network mode:**
- Internet + guests see each other → VMware **NAT (VMnet8)** / VirtualBox **NAT Network** (plain VirtualBox NAT: every guest is 10.0.2.15 and they can't see each other).
- LAN access to a NAT guest → **port forwarding** only (host:2222 → guest:22).
- Isolated lab → **host-only** (+ a second NAT adapter only where apt is needed).
- Guest as a full LAN member → **bridged** (works at home, not on campus).

**Verification (command → what I expect):**
```powershell
Get-CimInstance Win32_OperatingSystem | Format-List FreePhysicalMemory, TotalVirtualMemorySize, FreeVirtualMemory   # before/after starting guests
Get-CimInstance Win32_PageFileUsage | Format-List CurrentUsage, PeakUsage   # growing = host is swapping
Get-ChildItem <VM folder> -Include *.vmdk,*.vdi -Recurse | Format-Table Name, Length   # thin file < declared size
New-NetFirewallRule -DisplayName "Allow ICMPv4 echo in" -Protocol ICMPv4 -IcmpType 8 -Direction Inbound -Action Allow
```
```bash
nproc; free -h; lsblk; df -h /            # guest sees 2 CPUs / 2 GB / 25 GB
ip addr; ip route; ping -c 3 8.8.8.8; ping -c 3 <Windows IP>
```

---

## 3. Task 3 — Diagnose (the transcript is the deliverable)

Marks: Method 35 · Correct result 25 (fix **survives a reboot**) · Transcript 25 (followable without you, **dead ends recorded**) · Verification 15.
A perfectly straight path with no wrong turn is not believed and is marked down.

```markdown
Symptom as reported: "<quote>"

| # | Command (output I read) | Expected | Got | Concluded |
|---|---|---|---|---|
| 1 | df -h | / < 90% | / 61% | dead end: disk is not the cause |
| 2 | systemctl status app | active (running) | failed, 03:12 | it crashed — why? |
| 3 | free -h | available > 500M | 80Mi, Swap 2.0G/2.0G | RAM + swap exhausted |
| 4 | journalctl -k \| grep -i oom | entry? | 03:12 Killed process 1844 (app) | OOM killer, time matches row 2 |
| 5 | ps aux --sort=-rss \| head | app is biggest | backup.py 1.6G | culprit is backup.py, app was the victim |

## Fault — one sentence: what broke and why.
## Fix — now: … / permanent (survives reboot): …
## Verification — after reboot I rerun <command>, expect <output>.
```

**Method:** quote the symptom → layers bottom-up **disk → memory → processes/services → network → files** → hypothesis → which output tests it → conclusion. One variable at a time. Find the *cause*, not the symptom. Compare timestamps.
**Marker words in output:** `failed` `error` `denied` `Killed` `No such` `100%` `degraded` `[U_]` `^M` `DOWN` `Z` `<defunct>` `No space`.

### Fault catalogue
| What you see | Where | Cause | Permanent fix |
|---|---|---|---|
| `Out of memory: Killed process N (x)` | `journalctl -k`, `dmesg -T` + grep oom | RAM + swap exhausted, OOM killer (highest oom_score) | remove leak / limit it, +RAM/swap |
| no kernel OOM, process killed | `journalctl -u systemd-oomd` | systemd-oomd killed it first | same |
| available ≈ 0, Swap used rising, `si/so ≠ 0`, high `wa` | `free -h`, `vmstat 1` | thrashing | fewer processes/guests, +RAM |
| `No space left on device`, `Use% 100%` | `df -h` → `du -sh /var/*` | disk full (often `/var/log/journal`) | `journalctl --vacuum-size=200M`, cap logs, bigger disk |
| `/mnt/data` empty after reboot | `lsblk -f` (no MOUNTPOINT), `cat /etc/fstab` | fstab uses `/dev/sdb1`, disk became `sdc` / no line | fstab by **UUID** (`blkid`), test with `mount -a` |
| files "vanished" after mount | `findmnt` | written to the folder before mounting — hidden under the mountpoint | umount → move → mount |
| `[U_]`, `clean, degraded` | `cat /proc/mdstat`, `mdadm --detail /dev/md0` | RAID 1 lost a disk | `mdadm --manage /dev/md0 --add /dev/sdX1` → `[UU]` |
| `Active: failed` / `inactive (dead)`, `disabled` | `systemctl status x`, `journalctl -u x -n 50` | service crashed / not enabled at boot | fix the cause → `systemctl enable --now x` |
| `/bin/bash^M: bad interpreter` | `cat -A f` (`^M$`), `file f` (with CRLF) | CRLF line endings | `sed -i 's/\r$//' f` / `dos2unix`; `.gitattributes`: `*.sh text eol=lf` |
| `#!` ignored, header is `﻿ID` | `xxd -l 16 f` → `ef bb bf` | UTF-8 BOM | `sed -i '1s/^\xEF\xBB\xBF//' f` |
| `[ "$x" = "Manager" ]` always false | `cat -A` | `\r` in the last field | convert to LF |
| `РђР№РіРµ…` | `file`, `xxd`, `iconv -f UTF-8 -t UTF-8 f >/dev/null` | UTF-8 read as CP1251 | DON'T save; open with the right encoding / `iconv` |
| gateway pings, 8.8.8.8 100% loss | `ip route` (no `default via`) | no default route | now `ip route add default via GW`; permanent `/etc/netplan/*.yaml` + `netplan apply` |
| `Temporary failure in name resolution` | `resolvectl status`, `/etc/resolv.conf` | DNS | nameservers in netplan |
| `state DOWN` / no inet | `ip addr` | interface down / DHCP no answer (bridged + MAC filter) | netplan `dhcp4: true`; switch to NAT |
| ping works one way only | receiver's firewall | Windows blocks inbound ICMP | ICMPv4 echo rule |
| many `Z` / `<defunct>` | `ps -eo pid,ppid,stat,cmd` | parent never calls `wait()` | kill won't help → fix/restart the **parent** (PPID) |
| processes stuck in `D` | `ps`, `vmstat` (wa) | blocked on disk I/O | look at the disk |
| high `st` in the guest's top | `top` → Cpu(s) | host overloaded (steal time) | fewer vCPUs in total |
| `Permission denied` running a script | `ls -l` (no x) | no execute bit | `chmod +x f` |
| `photo.jpg` runs | `file`, `xxd -l 4` → `4d 5a` | it's an .exe (MZ) | type = signature, not extension |
| 4 TB disk, only ~2 TB visible | `lsblk -o NAME,SIZE,PTTYPE` → `dos` | MBR (2 TiB limit) | GPT (wipes partitions → back up first) |
| `VT-x is disabled in the BIOS` / `VERR_VMX_MSR_ALL_VMX_DISABLED` | hypervisor error | VT-x off in firmware | UEFI → Enabled |
| all VMs paused / write errors | **host** free space | thin disks filled the host | free space, compact |
| Windows: low memory | `Get-WinEvent -FilterHashtable @{LogName='System'; Id=2004}` | Resource-Exhaustion-Detector 2004 | as for OOM |

### Temporary vs survives a reboot
| Works until reboot | Survives reboot |
|---|---|
| `ip route add default via X` | netplan yaml + `netplan apply` |
| `mount /dev/sdb1 /mnt/x` | `/etc/fstab` by UUID + `mount -a` |
| `systemctl start svc` | `systemctl enable svc` |
| `swapon /swapfile` | swap line in `/etc/fstab` |
| `kill` the heavy process | remove the cause |

Verification = after reboot, the same command: `ip route` → `default via …` · `systemctl is-enabled x` → `enabled` · `findmnt /mnt/data` → line present · `cat /proc/mdstat` → `[UU]`.

### Reading common Linux output
- `free -h` — look at **available**, not free (low free is normal: page cache). `Swap: used` line.
- `df -h` — `Use%`, `Avail`, `Mounted on`.
- `lsblk` — disk/part/lvm/raid1; empty MOUNTPOINT = not mounted; `lsblk -f` adds FSTYPE + UUID.
- `vmstat 1` — `si/so` swap in/out, `wa` I/O wait, `st` steal.
- `top` — `%Cpu(s): … wa … st`; `S` column: R S D Z.
- `ip addr` — `state UP/DOWN`, `inet 192.168.x.x/24`. `ip route` — `default via <GW>`.
- `systemctl status` — `Loaded: … ; enabled/disabled` + `Active: active/failed/inactive` + last log lines.
- `/proc/mdstat` — `[2/2] [UU]` healthy, `[2/1] [U_]` degraded, `recovery = 42%`.
- `cat -A` — `^M$` = CRLF, `$` = LF, `M-…` = bytes > 7F (it decodes nothing).
- `file` — `ASCII` / `UTF-8` / `UTF-8 (with BOM)` / `UTF-16 little-endian` / `ISO-8859`, `Non-ISO extended-ASCII` (= some code page) / `with CRLF line terminators`. CSV on Ubuntu 24.04 → `file -e csv`.

---

## 4. Facts and numbers

**Hardware**
- 6C/12T = 6 cores × 2 threads (SMT); the OS sees 12 logical CPUs; the second thread adds ~15–30%.
- L1/L2/L3 = SRAM (6 transistors/bit), RAM = DRAM (1T + 1C). Closer = more expensive per byte. Works because of locality.
- RAM ~100 ns · SSD ~100 µs · HDD ~10 ms. Disk ~1000× slower than RAM.
- DDR4 ≠ DDR5 (notch). DIMM/SO-DIMM. DDR4-3200 = PC4-25600 (×8). Mixed speeds → all run at the slowest. Dual channel: slots A2 + B2.
- ECC: 8 bits per 64; fixes 1-bit, detects 2-bit; needs module + CPU + board; not faster, not bigger. DDR5 on-die ECC ≠ ECC memory.
- M.2 = shape; SATA/NVMe = interface. 2280 = 22×80 mm. HDD 150–250 MB/s · SATA SSD ~550 · PCIe 3 x4 ~3500 · PCIe 4 x4 ~7000. NVMe is faster because of PCIe + queues (65,535 vs 1×32 for AHCI); the flash is the same (NAND).
- CPU upgrade: socket + chipset → firmware → cooler/PSU. LGA1151: 100/200-series → gen 6–7, 300-series → gen 8–9. LGA1700 = gen 12–14. AM5 = DDR5 only. Laptop BGA = impossible.
- PSU: 30–40% headroom. TDP = heat the cooler must remove. Too hot → throttling.
- Apple Silicon: SoC, unified memory (CPU + GPU), not upgradable, arm64 guests only.
- BIOS → MBR, UEFI → GPT + Secure Boot. Boot: power → firmware → bootloader → kernel → login.

**Virtualization**
- Type 1 = on bare hardware (ESXi, Hyper-V, KVM, Xen); Type 2 = an app on a host OS (Workstation, VirtualBox). Defined only by what is underneath. Hyper-V/WSL 2 on → Windows itself becomes a guest on type 1.
- VT-x / AMD-V (SVM): the CPU itself traps privileged instructions. Needs present **and** enabled.
- Container: **no kernel of its own** (uses the host kernel). Docker on Windows = hidden Linux VM.
- Cloud vCPU ≈ 1 thread, not a core. A vCPU = a hypervisor thread on the host.
- GVA → (guest page table) → GPA → (EPT/NPT) → HPA. TLB miss in a VM: up to 24 reads instead of 4.
- When host RAM runs out: lazy allocation → page sharing (KSM) → ballooning → compression → host swap. Measure overcommit on the **host**.
- Overcommit: CPU fine (slower) · RAM risky (swap) · thin disk risky (host fills) · network fine.
- Disk images: .vmdk VMware · .vdi VirtualBox · .vhdx Hyper-V · .qcow2 KVM.
- Snapshot = frozen point + delta (copy-on-write); revert discards the delta; delete merges it. Not a copy / backup / export. Full clone is independent, linked clone needs its parent, OVA = archive to move a VM.
- Guest additions: resolution, clipboard, shared folders, time sync, balloon driver. NOT licensing, NOT CPU speed, NOT internet.

| Mode | → internet | guest↔guest | host→guest | LAN→guest |
|---|---|---|---|---|
| NAT VMware | yes | yes | yes | port fwd |
| NAT VirtualBox | yes | no | port fwd | port fwd |
| NAT Network VirtualBox | yes | yes | port fwd | port fwd |
| Bridged | if LAN accepts the MAC | yes | yes | yes |
| Host-only | no | yes | yes | no |
| Internal | no | yes | no | no |

VMware NAT: gateway 192.168.x.2, guests .128–.254, host .1. VirtualBox NAT: guest 10.0.2.15, gateway 10.0.2.2. MAC: VMware 00:0C:29 / 00:50:56, VirtualBox 08:00:27. A packet can be stopped by: the real network (MAC filter) / the hypervisor NAT (no forward rule) / the guest firewall.

**Storage**
- A disk = a row of numbered blocks (LBA). sda/sda1 · nvme0n1p1 · vda · md0. Names are assigned at boot → check size and mountpoint before writing.
- Writes go to RAM (write-back), to disk later. "Saved" ≠ on disk. `sync`, `umount`. To verify data: umount → mount.
- MBR: 2 TiB (2³² × 512 B), 4 primary, one copy, BIOS. GPT: 128 partitions, two copies + checksums, UEFI. GPT required: disk > 2 TB **or** UEFI boot. `Get-Disk` → Partition Style; `lsblk -o NAME,PTTYPE` → gpt/dos.
- Quick format = new structures only, data stays. Full format = zeros. NTFS, ext4 (journal), FAT32 (≤ 4 GB per file, EFI partition), exFAT.
- Windows = a letter per volume; Linux = one tree from `/`. `umount` (no n); "busy" → `cd ~`. fstab by UUID.
- RAID 0 stripe (no protection) · 1 mirror · 5 survives 1 disk · 6 survives 2 · 10. 4×2 TB usable: R0 8 · R5 6 · R6 4 · R10 4. [UU] → [U_] → recovery → [UU].
- RAID ≠ backup (deletion, ransomware, FS corruption, fire, theft hit both halves). **3-2-1**: 3 copies, 2 media, 1 off-site (+1 offline/immutable, 0 errors in restore test).

**Encodings**
- 1 byte = 2 hex digits. 0x0A=10 · 0x41=65 · 0x7F=127 (last ASCII) · 0x80=128 · 0xC0=192 · 0xC8=200 · 0xFF=255. `printf '%d\n' 0xFF` · PS: `0xFF`, `'{0:X2}' -f 255`.
- ASCII 0–127: 09 tab · 0A LF · 0D CR · 20 space · 2C `,` · 3B `;` · 22 `"` · 41 A · 61 a.
- UTF-8: ASCII 1 B · Cyrillic and all Kazakh letters 2 B (D0/D1 Russian, D2/D3 Kazakh additions) · € and BOM 3 B · emoji 4 B. Latin A = 41; Cyrillic А = U+0410 = D0 90; Ә = D3 98. UTF-16LE: A = 41 00, А = 10 04.
- Code pages (1 byte, 80–FF): CP1251, CP866, KOI8-R — no Kazakh letters; **RK1048, PT154** — with Kazakh. Byte C0: CP1251 А · CP866 └ · KOI8-R ю. "ANSI" = system code page (RU/KZ CP1251, EN CP1252).

| "Айгерим" shows as | Written as | Read as |
|---|---|---|
| `РђР№РіРµСЂРёРј` | UTF-8 | CP1251 |
| `Ð…Ð¹Ð³…` | UTF-8 | CP1252 |
| `�������` | CP1251 | UTF-8 |
| `└щухЁшь` | CP1251 | CP866 |
| `юИЦЕПХЛ` | CP1251 | KOI8-R |
| `?лия ?асымова` | data loss (Kazakh saved as CP1251) | — |

- Mojibake ≠ corruption (ASCII intact) ≠ missing font (□) ≠ encryption. Pressing Save → double encoding.
- BOM: EF BB BF UTF-8 · FF FE UTF-16LE · FE FF UTF-16BE. Excel double-click without BOM → ANSI (garbage), with BOM → OK. LibreOffice guesses. cat is fine. Scripts trip on a BOM. Decide by **who reads the file**.
- CRLF 0D 0A Windows · LF 0A Linux/macOS · CR 0D classic Mac. These are not encodings.
- Signatures: PNG 89 50 4E 47 · JPEG FF D8 FF · PDF 25 50 44 46 · ZIP/docx 50 4B 03 04 · gzip 1F 8B · ELF 7F 45 4C 46 · EXE 4D 5A · script 23 21.
- PS 5.1: `>`/Out-File → UTF-16LE + BOM · Set-Content → ANSI (Kazakh → ?) · `-Encoding utf8` → UTF-8 + BOM. PS 7: UTF-8 without BOM.
- Lab 5 chain: `sha256sum` → `file` + `file -e csv` → `xxd -l 16` → `iconv -f UTF-8 -t UTF-8` → loop over candidates → `cat -A` + `tr -cd '\r' | wc -c` + `wc -l` → `iconv` (+BOM, +sed) → verify in Excel double-click / Calc defaults / cat → original's `sha256sum` unchanged.
- PS equivalents: `Get-FileHash` · `Format-Hex f | Select-Object -First 1` · `[Text.Encoding]::GetEncoding(1251)` + `[IO.File]::ReadAllText/WriteAllText` + `New-Object Text.UTF8Encoding($true)`.

**Processes and memory**
- Program = file; process = running instance (address space, registers incl. PC, open files, PID/PPID/user). Kernel record = PCB.
- States: Running ↔ Ready; Running → Blocked (I/O) → Ready. htop S: R · S · D (disk, uninterruptible) · Z (zombie).
- fork() copies (parent gets child PID, child gets 0) · exec() replaces the program, same PID, doesn't return on success · wait() collects the exit status. `ls` = fork → exec → wait. PID 1 = systemd. Windows: CreateProcess, tree not kept ("Non-existent process").
- Threads: own registers + stack, shared memory and files. The scheduler schedules threads.
- Service/daemon = no interactive session; systemd starts, restarts, logs to the journal. Windows: Service Control Manager.
- How the OS keeps control: user/kernel mode · system call (trap) · timer interrupt (every few ms) · scheduler (time slices; not cron!) · context switch. `strace -c ls`.
- Address space: code · data · heap ↓ · free · ↑ stack. Every address is virtual → isolation + swap possible.

| Memory | htop | Process Explorer | Task Manager |
|---|---|---|---|
| All mapped | VIRT | Virtual Size | — |
| In RAM now | RES | Working Set | Working set |
| Shared (libs) | SHR | WS Shareable | — |
| Private only | — | Private Bytes | Commit size |
| Default "Memory" | — | — | Private working set |
| Open files | fd (`/proc/PID/fd`, lsof) | Handles | Handles |

- Disagreements: Σ RES > RAM (shared libs counted in each) · TM Memory < Working Set · Windows handle is broader than a Linux fd · htop shows threads as rows (H hides).
- Out-of-memory path: cache shrinks → swapping (si/so) → thrashing → OOM killer (highest oom_score) / Windows event ID 2004.

```powershell
$PID; Get-CimInstance Win32_Process -Filter "ProcessId=$PID" | Select-Object ProcessId, ParentProcessId, Name
Get-Process -Id $PID | Select-Object Id, WorkingSet64, PrivateMemorySize64, VirtualMemorySize64, HandleCount
```
```bash
echo $$; ps -o pid,ppid,user,cmd -p $$; pstree -p | head -30
grep -E 'Name|PPid|VmSize|VmRSS|Threads' /proc/$PID/status; ls -l /proc/$PID/fd | wc -l
free -h; swapon --show; vmstat 1; journalctl -k | grep -iE 'out of memory|oom|killed process'
```

---

## 5. README template for any lab
```markdown
# Lab N — <title>
Machine: …  Date: …
## What I did        (commands in code blocks, not prose)
## Result            (table / number / output)
## What did not work the first time   (at least one)
## Evidence          - [evidence/x.txt](evidence/x.txt) — what it proves
```
Rules: diagnose first · never touch the original (checksum) · exact names (CP1251, CRLF, OOM) · every number has its command · text over screenshots · one variable at a time · prove the fix.

---

## 6. Windows-only toolkit (no VM, no Linux tools)

### Encoding forensics in PowerShell (Lab 5 without `file` / `xxd` / `iconv`)
```powershell
$f = "$PWD\staff-broken.csv"
Get-FileHash $f                                   # write it down; must match at the end
Format-Hex $f | Select-Object -First 2            # first 32 bytes
$b = [IO.File]::ReadAllBytes($f)
"UTF-8 BOM: "    + ($b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
"UTF-16LE BOM: " + ($b[0] -eq 0xFF -and $b[1] -eq 0xFE)
"CR: " + ($b | Where-Object { $_ -eq 13 }).Count + "   LF: " + ($b | Where-Object { $_ -eq 10 }).Count
"Bytes > 0x7F: " + ($b | Where-Object { $_ -gt 127 }).Count     # 0 = pure ASCII
try { [void](New-Object Text.UTF8Encoding($false, $true)).GetString($b); "valid UTF-8" } catch { "NOT valid UTF-8 -> single-byte code page" }
# try candidates: 1251 = CP1251, 866 = CP866, 20866 = KOI8-R, 1252 = Western
foreach ($cp in 1251, 866, 20866, 1252) { "=== $cp"; [Text.Encoding]::GetEncoding($cp).GetString($b).Split("`n")[0..4] }
```
- PowerShell 7: if `GetEncoding(1251)` fails, first run `[Text.Encoding]::RegisterProvider([Text.CodePagesEncodingProvider]::Instance)`.
- .NET has no RK1048 / PT154. If Russian letters read correctly under 1251 but Kazakh letters (Ә Ғ Қ Ң Ө Ұ Ү Һ І) come out as other symbols → the file is RK1048 or PT154. Say so in the README; converting it exactly needs `iconv` (Linux, WSL or Git Bash if installed).
- Reading CR/LF: CR = LF = lines → CRLF · CR = 0 → LF · CR = lines, LF = 0 → CR · in between → mixed.

### Windows diagnostics (CMD and PowerShell)
| Question | CMD | PowerShell |
|---|---|---|
| IP, gateway, DNS | `ipconfig /all` | `Get-NetIPConfiguration` |
| Default route | `route print` | `Get-NetRoute -DestinationPrefix 0.0.0.0/0` |
| Reachability | `ping 8.8.8.8` · `tracert 8.8.8.8` | `Test-NetConnection 8.8.8.8 -TraceRoute` |
| Port open? | — | `Test-NetConnection 192.168.10.5 -Port 22` |
| DNS | `nslookup google.com` | `Resolve-DnsName google.com` |
| Listening ports + PID | `netstat -ano` | `Get-NetTCPConnection -State Listen` |
| Service state | `sc query spooler` | `Get-Service spooler` · `Get-Service \| Where-Object Status -eq Stopped` |
| Service autostart | `sc qc spooler` | `Get-CimInstance Win32_Service -Filter "Name='spooler'" \| Select-Object Name, State, StartMode` |
| Processes by memory | `tasklist` | `Get-Process \| Sort-Object WS -Descending \| Select-Object -First 10 Name, Id, WS` |
| Firewall ICMP rules | — | `Get-NetFirewallRule -Direction Inbound -Enabled True \| Where-Object DisplayName -like '*ICMP*'` |
| Recent errors | — | `Get-WinEvent -FilterHashtable @{LogName='System'; Level=2} -MaxEvents 20` |
| Low memory events | — | `Get-WinEvent -FilterHashtable @{LogName='System'; Id=2004}` |
| Disk free | `wmic logicaldisk get caption,freespace` (old) | `Get-PSDrive -PSProvider FileSystem` |

Windows "survives reboot": `Start-Service x` → also `Set-Service x -StartupType Automatic`; firewall rules made with `New-NetFirewallRule` are already permanent.

### Config file syntax (for Task 3 fixes)
`/etc/fstab` — one line per mount, by UUID (get it from `blkid` or `lsblk -f`):
```text
UUID=3f1c2a9e-0b7d-4c1e-9a2f-5d6e7f8a9b0c  /mnt/data  ext4  defaults  0  2
```
Test without rebooting: `sudo mount -a` (no error = OK) → `findmnt /mnt/data`.

`/etc/netplan/*.yaml` — static address + default route + DNS (spaces only, no tabs):
```yaml
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: false
      addresses: [192.168.10.24/24]
      routes:
        - to: default
          via: 192.168.10.1
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
```
DHCP instead: `ens33: {dhcp4: true}`. Apply: `sudo netplan apply` (or `sudo netplan try` — rolls back if you lose the connection). Older files use `gateway4: 192.168.10.1` (deprecated, still works).

RAID that survives reboot: `sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf` → `sudo update-initramfs -u`.

Service: `sudo systemctl enable --now x` → check `systemctl is-enabled x` = `enabled`, `systemctl is-active x` = `active`.
