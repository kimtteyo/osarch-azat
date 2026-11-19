# Task 1b — A machine you have never seen: a thin-and-light laptop

Driver first half: Azat Zhansaya
Date: 2026-11-19

## What I did

|Figure|This computer|Command it came from|
|-|-|-|
|CPU model|AMD Ryzen AI 5 340 w/ Radeon 840M|`Get-CimInstance Win32_Processor`|
|Cores / logical processors|6/ 12|`Get-CimInstance Win32_Processor`/NumberOfCores / NumberOfLogicalProcessors|
|Hardware virtualization: supported? enabled in firmware?|VirtualizationFirmwareEnabled: True/VMMonitorModeExtensions: False/SecondLevelAddressTranslationExtensions : False|`Get-CimInstance Win32_Processor`|
|Memory: total / available now| 15,1GB/5.8GB|Get-CimInstance Win32_OperatingSystem|
|System disk: size, free space, SSD or HDD|476GB/136GB/SSD|`Get-PhysicalDisk`,`Get-CimInstance Win32_LogicalDisk`
|Partition style of the system disk|GPT|Get-Disk|
|OS and version|Caption: Майкрософт Windows 11 Pro/Version: 10.0.26300/OSArchitecture : 64-разрядная|`Get-CimInstance Win32_OperatingSystem`

1b. A machine you have never seen: a thin-and-light laptop
|Part|Specification|
|-|-|
|CPU |2 cores / 4 threads, 1.1 GHz; AMD-V supported and enabled|
|Memory |8 GB LPDDR4X, soldered to the board|
|Storage |128 GB eMMC, soldered, 31 GB free|
|OS |Windows 11 Home in S mode|

## 1. Both guests?

**Assumptions for the host:** Windows 11 needs about 3 GB RAM, 2 threads of CPU, and I keep about 10-15% of the disk free (about 13-19 GB of 128 GB).

| Resource | Guests need | Host has available | Result |
|-|-|-|-|
| CPU | Ubuntu 2 + Win11 2 = 4 vCPU | 4 threads - 2 for host = 2 (only 2 physical cores) | Overcommitted |
| RAM | 2 + 4 = 6 GB + ~0.5 GB hypervisor overhead = 6.5 GB | 8 GB - 3 GB = 5 GB | Short by ~1.5 GB, host will swap |
| Disk | 25 + 64 = 89 GB (maximum sizes) | 31 GB free | Short by 58 GB |

Even with thin-provisioned disks, Windows 11 alone grows to about 25 GB, so it would still fill the free space.

Virtualization is not a blocker: AMD-V is supported and enabled. However, Windows 11 Home in **S mode** only runs Microsoft Store apps, so VirtualBox/VMware cannot be installed until S mode is switched off. Home also has no Hyper-V.

**Conclusion:** No. The laptop cannot run both guests at the same time. The main bottleneck is **disk** (89 GB needed vs 31 GB free on slow eMMC), followed by RAM and CPU. Ubuntu Server alone (2 GB, 25 GB) would fit.

## 2. Upgrade first

**Honest answer: nothing inside this machine can be upgraded.**

| Bottleneck | Upgradeable? | Why |
|-|-|-|
| RAM (8 GB LPDDR4X) | No | Soldered to the board, no free slot |
| Storage (128 GB eMMC) | No | Soldered, no M.2 slot |
| CPU (2C/4T, 1.1 GHz) | No | BGA-mounted, no socket |
| Virtualization (AMD-V) | Already enabled | Nothing to change in UEFI |

**What I would do instead, in order:**

1. **Switch out of S mode** (Settings -> System -> Activation). It is free but one-way. It is a setting, not an upgrade, but nothing else works without it.
2. **Put the VM disk images on an external USB 3 SSD.** This is the only real fix for the disk problem and avoids the slow eMMC.
3. **Run one guest at a time**, with at most 2 vCPU and 2-4 GB RAM.
4. If both guests are needed together, use a different machine (16 GB RAM or more, 4+ cores, NVMe SSD).

## Evidence

- [evidence/task1.txt](evidence/task1.txt) 
