# Lab 0 — Inventory your own machine

Pair: none
Driver first half: Azat Zhansaya (CYB26-1)
Machine: ASUS Vivobook S 16 M5606KA
Date: 10.10.2026

## What I did

```
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

Name                      : AMD Ryzen AI 5 340 w/ Radeon 840M
NumberOfCores             : 6
NumberOfLogicalProcessors : 12
```

```
Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel, Manufacturer, Capacity, Speed, ConfiguredClockSpeed

BankLabel    Manufacturer        Capacity Speed ConfiguredClockSpeed
---------    ------------        -------- ----- --------------------
P0 CHANNEL A Micron Technology 4294967296  8000                 8000
P0 CHANNEL B Micron Technology 4294967296  8000                 8000
P0 CHANNEL C Micron Technology 4294967296  8000                 8000
P0 CHANNEL D Micron Technology 4294967296  8000                 8000

Total GB: 16
```

```
Get-PhysicalDisk | Select-Object FriendlyName, MediaType, BusType, Size

FriendlyName : HFS512GEM9X174N
MediaType    : SSD
BusType      : NVMe
Size         : 512110190592

Get-Volume -DriveLetter C

DriveLetter FriendlyName FileSystemType DriveType HealthStatus OperationalStatus SizeRemaining      Size
----------- ------------ -------------- --------- ------------ ----------------- -------------      ----
C                        NTFS           Fixed     Healthy      OK                    294.61 GB 475.89 GB
```

```
Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate
(Get-ComputerInfo).BiosFirmwareType

Manufacturer                            SMBIOSBIOSVersion ReleaseDate
------------                            ----------------- -----------
American Megatrends International, LLC. M5606KA.307       04.07.2025 5:00:00

Uefi
```

```
systeminfo | Select-String "Virtualization","hypervisor"

Требования Hyper-V:                      Обнаружена низкоуровневая оболочка. Функции, необходимые для Hyper-V, отображены не будут.

Get-CimInstance Win32_Processor | Select-Object Name, VirtualizationFirmwareEnabled

Name                                            VirtualizationFirmwareEnabled
----                                            -----------------------------
AMD Ryzen AI 5 340 w/ Radeon 840M                                        True
```

## Result

| What | Value | Where I got it |
|------|-------|----------------|
| CPU model | AMD Ryzen AI 5 340 w/ Radeon 840M | `Get-CimInstance Win32_Processor` |
| Cores / threads | 6 / 12 | `Get-CimInstance Win32_Processor` |
| Total RAM | 16 GB | `Get-CimInstance Win32_PhysicalMemory` |
| RAM modules / speed | 4 modules / 8000 MHz | `Get-CimInstance Win32_PhysicalMemory` |
| Disk model | HFS512GEM9X174N | `Get-PhysicalDisk` |
| Disk type | NVMe (SSD) | `Get-PhysicalDisk` (BusType, MediaType) |
| Free space (VM volume) | 294.6 GB | `Get-Volume -DriveLetter C` |
| Firmware type | UEFI | `(Get-ComputerInfo).BiosFirmwareType` |
| Firmware version / date | M5606KA.307, 04.07.2025 (4 July 2025) | `Get-CimInstance Win32_BIOS` |
| Virtualization | enabled | `systeminfo`, `VirtualizationFirmwareEnabled` |

## What did not work the first time

- `Confirm-SecureBootUEFI` gave "Access denied" because PowerShell was not run as administrator. The firmware type (UEFI) was confirmed with `(Get-ComputerInfo).BiosFirmwareType` instead.
- The computer updated and restarted in the middle of the lab and PowerShell closed. I tried a wrong path (`repo_starter\labs\...`), but my repo has no `repo_starter` folder. I listed the folders with `dir` and found the lab at `osarch-azat\labs\lab00-inventory`. The evidence files were still there.
- `systeminfo` on Russian Windows printed only one Hyper-V line ("a hypervisor has been detected"), so I double-checked virtualization with `VirtualizationFirmwareEnabled` (True).

## Evidence

- [evidence/cpu.txt](evidence/cpu.txt) — CPU model, cores, threads
- [evidence/memory.txt](evidence/memory.txt) — RAM size, modules, speed
- [evidence/disk.txt](evidence/disk.txt) — disk model, type, free space

## Help used

I used an AI assistant (Claude) to help with troubleshooting the commands and formatting this README. I ran all commands myself on my own laptop and the values come from my own output.