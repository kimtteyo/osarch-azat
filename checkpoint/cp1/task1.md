# Task 1b — A machine you have never seen: a thin-and-light laptop

Driver first half: Azat Zhansaya
Date: 2026-11-19

## What I did

|Figure|This computer|Command it came from|
|-|-|-|
|CPU model|AMD Ryzen AI 5 340 w/ Radeon 840M|`Get-CimInstance Win32_Processor`|
|Cores / logical processors|6/ 12|same, NumberOfCores / NumberOfLogicalProcessors|
|Hardware virtualization: supported? enabled in firmware?|VirtualizationFirmwareEnabled: True/VMMonitorModeExtensions: False/SecondLevelAddressTranslationExtensions : False|`Get-CimInstance Win32_Processor`|
|Memory: total / available now| 15,1GB/5.8GB|Get-CimInstance Win32_OperatingSystem|
|System disk: size, free space, SSD or HDD|476GB/136GB/SSD|`Get-PhysicalDisk`,`Get-CimInstance Win32_LogicalDisk`
|Partition style of the system disk|GPT|Get-Disk|
|OS and version|Caption        : Майкрософт Windows 11 Pro
Version        : 10.0.26300
OSArchitecture : 64-разрядная|`Get-CimInstance Win32_OperatingSystem`

1b. A machine you have never seen: a thin-and-light laptop
|Part|Specification|
|-|-|
|CPU |2 cores / 4 threads, 1.1 GHz; AMD-V supported and enabled|
|Memory |8 GB LPDDR4X, soldered to the board|
|Storage |128 GB eMMC, soldered, 31 GB free|
|OS |Windows 11 Home in S mode|

1.Both guests? Could this laptop run both of the guests you built in Labs 1–2 at the same time, at the sizes you gave them (take them from your build log)? Show the arithmetic for CPU, memory and disk, and say what you assumed for the host itself.
No, 64-bit guest will not start (fix in UEFI: Intel Virtualization Technology / SVM Mode).
Threads Σ vCPU vs **threads** host; leave to the host ≥ 2.
3. RAM: 31 GB Free. Ubuntu Server 2 GB + Win11 4 GB = 6 GB. More → will start, but host is in swap.
4. Disk: 31 GB ≥ 25 + 64 GB. HDD → Slow.
5. Вывод одной фразой + названный bottleneck.

2.Upgrade first. What would you upgrade or change first, and why? Can it actually be upgraded on this machine? If the honest answer is “nothing can be”, say so and say what you would do instead.

|Bottleneck|Symptome|Check opportunities|
|-|-|-|
|RAM |everything is lagging, swap|пустой слот? тот же DDR? распаяна (ноут/Apple) → нельзя|
|1 модуль RAM|половина bandwidth|второй такой же → dual channel (2×8 > 1×16)|
|HDD / мало места|медленный старт, диск полон|SSD; M.2 слот: M-key = NVMe, B+M = SATA|
|CPU|долгие задачи|socket + chipset + firmware; ноут BGA → нельзя|
|VT-x off|гость не стартует|не апгрейд, а настройка UEFI — первой|



## Evidence

- [evidence/task1.txt](evidence/task1.txt) 
