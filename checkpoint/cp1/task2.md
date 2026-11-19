# Task 2: Plan and justify

## Host figures (from Task 1)

| Resource | Value |
|-|-|
| CPU | AMD Ryzen AI 5 340, 6 cores / 12 threads |
| RAM | 15.1 GB total (soldered LPDDR5X), 5.8 GB free at measurement time |
| Disk | 477 GB NVMe SSD, GPT, UEFI; C: 476 GB, 136 GB free |
| OS | Windows 11 Pro 10.0.26300, 64-bit |
| Virtualization | `VirtualizationFirmwareEnabled: True`, `HypervisorPresent: True` |

`VMMonitorModeExtensions` and `SecondLevelAddressTranslationExtensions` read False because a hypervisor is already running and owns those features. The value that matters is `VirtualizationFirmwareEnabled: True`, so virtualization is available.

## Allocation

| | Ubuntu Server guest | Windows 11 guest |
|-|-|-|
| vCPUs | 1 | 2 |
| Memory | 2 GB (2048 MB), static | 4 GB (4096 MB), static |
| Disk | 20 GB, dynamically allocated | 64 GB, dynamically allocated |
| Adapter | 1 adapter on Hyper-V **Default Switch** (NAT) | 1 adapter on Hyper-V **Default Switch** (NAT) |
| Generation | Gen 2 (Secure Boot: Microsoft UEFI CA template) | Gen 2, Secure Boot + virtual TPM (required by Win 11) |

## Arithmetic

**Assumptions for the host:** Windows 11 plus Hyper-V, a browser and the management tools need about 4 threads, about 6 GB RAM, and about 40 GB of free disk (roughly 8% of the disk) so Windows updates, the page file and VM checkpoints do not fail.

| Resource | Total | Guests use | Left for host | Host needs | OK? |
|-|-|-|-|-|-|
| CPU | 12 threads | 1 + 2 = 3 vCPU | 9 threads | 4 | Yes |
| RAM | 15.1 GB | 2 + 4 = 6 GB | 9.1 GB | 6 GB | Yes, 3.1 GB spare |
| Disk (worst case, both disks full) | 136 GB free | 20 + 64 = 84 GB | 52 GB | 40 GB | Yes |
| Disk (at start, dynamic) | 136 GB free | about 5 + 25 = 30 GB | about 106 GB | 40 GB | Yes |

**RAM caveat:** only 5.8 GB was free when I measured, because my open applications use about 9.3 GB. Starting 6 GB of guests in that state would leave the host short by 0.2 GB and push it into paging. Before starting the lab I close heavy applications until at least 8 GB is free. After that the plan fits, as the table shows.

## Justification

**Hypervisor: Hyper-V.** The host is Windows 11 Pro, which includes Hyper-V, and a hypervisor is already active. VirtualBox or VMware would run on top of the Windows Hypervisor Platform, which is slower.

**Network mode: Default Switch (NAT) for both guests.** The requirement is that the host can ssh to Ubuntu and Ubuntu can still reach the internet.

| Option | SSH from host | Internet from guest | Verdict |
|-|-|-|-|
| **Default Switch (NAT)** | Yes, the host has an adapter on the same virtual network and can reach the guest IP (or `ubuntu-lab.mshome.net`) | Yes, through NAT | **Chosen**: meets both needs with one adapter |
| External switch (bridged) | Yes | Yes | Rejected: bridging a laptop's Wi-Fi is unreliable, and it puts the test guests directly on the office LAN |
| Internal switch | Yes | No, unless internet sharing is set up on the host | Rejected: fails the internet requirement without extra work |
| Private switch | No | No | Rejected: host cannot reach the guest |

The Default Switch gives the guest a new IP after each host reboot, so I connect by the name `<vm-name>.mshome.net` or read the IP with `ip -br a`.

**vCPUs.** Ubuntu Server is idle most of the time and needs one vCPU. Windows 11 requires 2, so I did not go lower. Total 3 of 12 threads leaves the host plenty.

**Memory.** Windows 11 requires 4 GB, so it gets exactly 4 GB. Ubuntu Server runs from 1 GB, and 2 GB is comfortable for ssh and basic services. I chose static memory so the guests cannot grow and starve the host.

**Disk.** Windows 11 requires 64 GB, so it gets 64 GB. Ubuntu Server needs only a few GB, and 20 GB leaves room for packages and logs. I chose dynamic disks because the host SSD is NVMe, so the small speed penalty is negligible, and the disks cost only what they actually use. Even if both grow to their maximum (84 GB), 52 GB stays free, so dynamic allocation carries no risk of filling the host.

**Below any minimum?** Nothing is set below a stated minimum. Windows 11 is exactly at its minimums (2 vCPU, 4 GB, 64 GB), and Ubuntu Server is above its minimums.

## Verification plan

**On the host (PowerShell, as Administrator)**

```powershell
Get-VM | Format-Table Name, State, ProcessorCount, MemoryAssigned
```
Expected: both VMs `Running`; Ubuntu `1` and `2147483648`; Windows `2` and `4294967296`.

```powershell
Get-VM | Get-VMHardDiskDrive | ForEach-Object { Get-VHD $_.Path } | Format-Table Path, VhdType, @{n='SizeGB';e={$_.Size/1GB}}, @{n='UsedGB';e={[math]::Round($_.FileSize/1GB,1)}}
```
Expected: `VhdType` is `Dynamic` for both; SizeGB 20 and 64; UsedGB small (about 5 and 25).

```powershell
Get-VMNetworkAdapter -VMName * | Format-Table VMName, SwitchName, IPAddresses
```
Expected: `SwitchName` is `Default Switch` for both, each with an IP such as `172.2x.x.x`.

```powershell
Get-CimInstance Win32_OperatingSystem | Format-List @{n='FreeGB';e={[math]::Round($_.FreePhysicalMemory/1MB,1)}}
Get-PSDrive C | Format-List @{n='FreeGB';e={[math]::Round($_.Free/1GB)}}
```
Expected, with both guests running: host free RAM about 3 GB or more, and C: free about 100 GB or more at first (never below 40 GB at maximum growth).

**SSH from the host to Ubuntu**

```powershell
ssh <user>@ubuntu-lab.mshome.net "hostname; nproc; free -h | head -2"
```
Expected: the Ubuntu hostname, `1`, and a `Mem:` line with total about `1.9Gi`.

**Inside the Ubuntu guest**

```bash
nproc                      # 1
free -h                    # Mem total ~1.9Gi
lsblk                      # sda  20G
df -h /                    # size ~19G
ip -br a                   # eth0 UP 172.x.x.x/20
ip route                   # default via 172.x.x.1 dev eth0
systemctl is-active ssh    # active
ss -tlnp | grep ':22'      # LISTEN on 0.0.0.0:22
ping -c 3 1.1.1.1          # 0% packet loss
ping -c 3 ubuntu.com       # resolves and replies (proves DNS and internet)
```

**Inside the Windows 11 guest (PowerShell)**

```powershell
(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors   # 2
[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)   # about 4 (3.9-4.0)
Get-Disk | Format-Table Number, @{n='GB';e={[math]::Round($_.Size/1GB)}}   # 64
ipconfig                   # IPv4 172.x.x.x, gateway 172.x.x.1
Test-Connection 1.1.1.1 -Count 3   # replies received
```

Both guests running at the same time, all values above matching, and the host still responsive (free RAM at least 3 GB, free disk at least 40 GB) proves the plan was carried out.
