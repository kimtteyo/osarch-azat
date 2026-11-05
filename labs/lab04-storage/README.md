# Lab 4 — Partition, mirror, fail, recover

Author: Zhansaya Azat
Driver first half: Zhansaya Azat

Machine: Windows 11 guest (lab02-win11), Ubuntu guest (lab01), VMware Workstation
Date: 5 November 2026

## What I did

### 1. Added virtual disks (guests powered off)
- Windows guest: one 2 GB disk.
- Linux guest: three 2 GB SCSI disks (A, B, spare for the rebuild).

### 2. Windows: partition, format, letter
```powershell
PS> Get-Disk
Number Friendly Name  HealthStatus OperationalStatus Total Size Partition Style
0      VMware Vir...  Healthy      Online            64 GB      GPT
1      VMware Vir...  Healthy      Online            2 GB       RAW

PS> Initialize-Disk -Number 1 -PartitionStyle GPT
PS> New-Partition -DiskNumber 1 -UseMaximumSize -DriveLetter E
PartitionNumber  DriveLetter  Offset     Size     Type
2                E            16777216   1.98 GB  Basic

PS> Format-Volume -DriveLetter E -FileSystem NTFS -NewFileSystemLabel LAB4
DriveLetter FriendlyName FileSystemType DriveType HealthStatus OperationalStatus SizeRemaining Size
E           LAB4         NTFS           Fixed     Healthy      OK                1.97 GB       1.98 GB

PS> Get-Disk
Number Friendly Name  HealthStatus OperationalStatus Total Size Partition Style
0      VMware Vir...  Healthy      Online            64 GB      GPT
1      VMware Vir...  Healthy      Online            2 GB       GPT

PS> Get-Partition -DiskNumber 1
PartitionNumber  DriveLetter  Offset     Size      Type
1                             17408      15.98 MB  Reserved
2                E            16777216   1.98 GB   Basic

PS> $env:firmware_type
UEFI
```

**MBR or GPT, and why**
- **Disk 0 (system disk):** GPT. `firmware_type` is UEFI, and UEFI firmware boots from a GPT disk (the EFI System Partition lives on GPT), so the firmware type decides the style.
- **New disk (Disk 1):** GPT, my choice. A 2 GB disk works with either table. The choice would matter if the disk were over 2 TB (MBR cannot address more than 2 TB), if I needed more than four primary partitions (MBR limit), or if I booted from it on a UEFI machine. GPT also keeps a backup copy of the partition table at the end of the disk.
- The 15.98 MB Reserved partition is the Microsoft Reserved Partition that Windows creates automatically on GPT disks.

### 3. Linux: layout before
```bash
$ mkdir -p ~/lab04/evidence && cd ~/lab04/evidence
$ lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT > lsblk-before.txt
$ cat lsblk-before.txt
NAME    SIZE TYPE FSTYPE   MOUNTPOINT
loop0   1.5M loop squashfs /snap/hwctl/123
loop1   1.5M loop squashfs /snap/hwctl/131
loop2  44.7M loop squashfs /snap/snapd/28254
loop3  66.8M loop squashfs /snap/core24/2124
loop4  66.8M loop squashfs /snap/core24/1643
loop5  50.1M loop squashfs /snap/snapd/27710
sda      25G disk
├─sda1    1M part
└─sda2   25G part ext4     /
sdb       2G disk
sdc       2G disk
sdd       2G disk
sr0     2.7G rom  iso9660
```
The system disk is sda (25G, mounted on `/`). The new disks are sdb, sdc and sdd: 2G, no children, no mount point. Only these were written to.

| Role          | Device |
|---------------|--------|
| Mirror half A | sdb1   |
| Failed half   | sdc1   |
| Replacement   | sdd1   |

### 4. Partition the disks and build the mirror
```bash
$ mdadm --version
mdadm - v4.5 - 2025-12-16 - Ubuntu 4.5-5ubuntu1
$ sudo parted /dev/sdb --script mklabel gpt mkpart lab4 1MiB 100% set 1 raid on
$ sudo parted /dev/sdc --script mklabel gpt mkpart lab4 1MiB 100% set 1 raid on
$ lsblk /dev/sdb /dev/sdc
NAME   MAJ:MIN RM SIZE RO TYPE MOUNTPOINTS
sdb      8:16   0   2G  0 disk
└─sdb1   8:17   0   2G  0 part
sdc      8:32   0   2G  0 disk
└─sdc1   8:33   0   2G  0 part
$ sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb1 /dev/sdc1
mdadm: Defaulting to version 1.2 metadata
mdadm: array /dev/md0 started.
$ cat /proc/mdstat
md0 : active raid1 sdc1[1] sdb1[0]
      2093056 blocks super 1.2 [2/2] [UU]
      bitmap: 0/1 pages [0KB], 65536KB chunk
$ date > array-healthy.txt
$ cat /proc/mdstat >> array-healthy.txt
$ sudo mdadm --detail /dev/md0 >> array-healthy.txt
```
Healthy state (saved at 06:58:21 AM): `[2/2] [UU]`, `State : clean`, `Failed Devices : 0`, sdb1 and sdc1 both `active sync`.

### 5. Format, mount, write the proof
```bash
$ sudo mkfs.ext4 -L lab4 /dev/md0
$ sudo mkdir -p /mnt/mirror
$ sudo mount /dev/md0 /mnt/mirror
$ sudo chown $USER /mnt/mirror
$ echo "Lab 4 - azat - $(date)" > /mnt/mirror/proof.txt
$ dd if=/dev/urandom of=/mnt/mirror/random.bin bs=1M count=200
200+0 records in
200+0 records out
209715200 bytes (210 MB, 200 MiB) copied, 1.93698 s, 108 MB/s
$ sync
$ sha256sum /mnt/mirror/proof.txt /mnt/mirror/random.bin > checksum-before.txt
$ cat checksum-before.txt
13f5571c1e9833ba40b790a022cc34500e2ebe4f8f0ad8580fee621275b0135c  /mnt/mirror/proof.txt
e11ac2d196191a0533e5a8dcb812ad0e0b4edaad1e3438e917bba126c5efcc3c  /mnt/mirror/random.bin
```

### 6. Fail one half
```bash
$ sudo mdadm /dev/md0 --fail /dev/sdc1
md/raid1:md0: Disk failure on sdc1, disabling device.
md/raid1:md0: Operation continuing on 1 devices.
$ date > array-degraded.txt
$ cat /proc/mdstat >> array-degraded.txt
$ sudo mdadm --detail /dev/md0 >> array-degraded.txt
$ sudo mdadm /dev/md0 --remove /dev/sdc1
mdadm: hot removed /dev/sdc1 from /dev/md0
$ cat array-degraded.txt
Thu Nov  5 03:44:41 PM UTC 2026
md0 : active raid1 sdc1[1](F) sdb1[0]
      2093056 blocks super 1.2 [2/1] [U_]
...
            State : clean, degraded
    Active Devices : 1
   Failed Devices : 1
...
    0   8   17   0   active sync   /dev/sdb1
    -   0    0   1   removed
    1   8   33   -   faulty        /dev/sdc1
```
The degraded state was saved right after `--fail` and before `--remove`.

Proof from the disk, not the cache (unmount and mount first):
```bash
$ cd ~/lab04/evidence
$ sudo umount /mnt/mirror
$ sudo mount /dev/md0 /mnt/mirror
$ sha256sum /mnt/mirror/proof.txt /mnt/mirror/random.bin > checksum-after-failure.txt
$ cat /mnt/mirror/proof.txt
Lab 4 - azat - Thu Nov  5 03:20:05 PM UTC 2026
$ diff checksum-before.txt checksum-after-failure.txt && echo MATCH
MATCH
```

### 7. Rebuild with the spare
```bash
$ sudo parted /dev/sdd --script mklabel gpt mkpart lab4 1MiB 100% set 1 raid on
$ sudo mdadm /dev/md0 --add /dev/sdd1
$ watch -n 1 cat /proc/mdstat
md0 : active raid1 sdd1[2] sdb1[0]
      2093056 blocks super 1.2 [2/2] [UU]
$ date > array-rebuilt.txt
$ cat /proc/mdstat >> array-rebuilt.txt
$ sudo mdadm --detail /dev/md0 >> array-rebuilt.txt
```
Rebuilt state (saved at 04:09:00 PM): `[2/2] [UU]`, `State : clean`, sdb1 and sdd1 `active sync`, `Events : 49` (it was 18 when healthy and 20 when degraded). The 2 GB rebuild finished within seconds, so I did not catch the progress bar.

### 8. Linux layout after the rebuild
```bash
$ lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
NAME     SIZE TYPE  FSTYPE            MOUNTPOINT
loop0    1.5M loop  squashfs          /snap/hwctl/123
loop1    1.5M loop  squashfs          /snap/hwctl/131
loop2   44.7M loop  squashfs          /snap/snapd/28254
loop3   66.8M loop  squashfs          /snap/core24/2124
loop4   66.8M loop  squashfs          /snap/core24/1643
loop5   50.1M loop  squashfs          /snap/snapd/27710
sda       25G disk
├─sda1     1M part
└─sda2    25G part  ext4              /
sdb        2G disk
└─sdb1     2G part  linux_raid_member
  └─md0    2G raid1 ext4              /mnt/mirror
sdc        2G disk
└─sdc1     2G part  linux_raid_member
sdd        2G disk
└─sdd1     2G part  linux_raid_member
  └─md0    2G raid1 ext4              /mnt/mirror
sr0      2.7G rom   iso9660
```
md0 now sits under sdb1 and sdd1. sdc1 still carries a RAID signature but belongs to no array.

## Result
- Windows: the new 2 GB disk is GPT with an NTFS partition E: (label LAB4). Disk 0 is GPT because the guest boots in UEFI mode.
- Linux: a RAID 1 mirror md0 was built from sdb1 and sdc1 and formatted as ext4.
- After failing sdc1 the filesystem stayed readable, and the SHA-256 checksums matched (`MATCH`) after unmount and remount, so the data came from the one surviving disk.
- The array was rebuilt onto sdd1 and returned to `[2/2] [UU]`, `clean`.

## What did not work the first time
1. **Typo in the device name.** I ran `mdadm --create ... /dev/sbd1 /dev/sdc1` (the letters b and d swapped). mdadm printed `cannot open /dev/sbd1: No such file or directory`, and `/proc/mdstat` showed `unused devices: <none>`, so nothing had been created. I re-ran the command with `/dev/sdb1` and the array started. Nothing was written to a wrong disk.
2. **Windows `Initialize-Disk` error.** It failed with `Access to a CIM resource was not available to the client` (PermissionDenied). I checked `Get-Disk` to confirm that the 2 GB RAW disk was number 1, opened PowerShell as Administrator, and the command then worked.

## Evidence
- `evidence/lsblk-before.txt` — disk layout before: sda is the system disk, sdb/sdc/sdd are the empty 2 GB disks.
- `evidence/array-healthy.txt` — healthy mirror at 06:58:21 AM: `[UU]`, `clean`, two `active sync` members.
- `evidence/checksum-before.txt` — SHA-256 of `proof.txt` and `random.bin` before the failure.
- `evidence/array-degraded.txt` — array right after `--fail` at 03:44:41 PM: `[U_]`, `clean, degraded`, sdc1 marked `(F)`.
- `evidence/checksum-after-failure.txt` — checksums taken after unmount and mount with one disk; identical to the before file.
- `evidence/array-rebuilt.txt` — array after rebuild onto sdd1 at 04:09:00 PM: `[UU]`, `clean`, sdb1 and sdd1 `active sync`.

## The question
Your colleague deleted the wrong file from the mirror an hour ago. Does RAID 1 help? Why?

No, RAID 1 does not help here. A mirror writes every change to both disks, and a deletion is a change too, so the file vanished from both halves at the same moment. What would have helped is a backup or a snapshot taken before the file was deleted.
