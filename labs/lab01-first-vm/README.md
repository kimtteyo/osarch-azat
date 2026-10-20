# Lab 1 — Your first virtual machine
# Lab 1 — Your first virtual machine

Pair: Zhansaya Azat / (Solo)   Driver first half: Zhansaya Azat
Machine: Windows host, VMware Workstation Pro 26H1, guest lab01-ubuntu (Ubuntu Server 26.04.1 LTS, amd64)
Date: 16.10.2026

## Resource justification

My host has 12 threads, 16 GB of RAM and 279.54 GB free on the VM volume C: (Lab 0 numbers; free space re-measured with `Get-PSDrive`). Idle, the host already uses about 12.2 GB of RAM (Task Manager → Performance → Memory), and about 2.9 GB is available.

I gave the guest 2 vCPU of my 12 threads (about 17%), because Ubuntu Server needs 1 and the second one keeps the guest responsive during the install. This is well under the limit of half my threads (6) and leaves 10 threads for the host and for a second guest.

I gave it 2 GB of my 16 GB RAM, because Ubuntu Server needs about 1.5–2 GB to install comfortably. The host already uses 12.2 GB and has about 2.9 GB available, so after the guest takes 2 GB only about 0.9 GB stays available. That is not enough for the Windows guest in Lab 2 (Windows 11 asks for about 4 GB), so before Lab 2 I will have to shut this guest down and close applications on the host. The VMware wizard offered 6144 MB by default; I changed it to 2048 MB, because 6 GB is more than the 2.9 GB available on the host and the host would start swapping.

I gave it a 25 GB dynamically allocated disk (single file, not preallocated) of my 279.54 GB free, because Ubuntu needs about 5 GB at minimum. This leaves about 254 GB, more than the 60 GB+ I need for the Windows guest next week.

## What I did

1. Installed VMware Workstation Pro from the Broadcom portal (after reading the licence terms).
2. Checked the architecture: AMD64, so the amd64 ISO.
3. Downloaded ubuntu-26.04.1-live-server-amd64.iso (LTS, live-server, not Desktop).
4. Created the VM: Typical, ISO as installer disc, Linux → Ubuntu 64-bit, name lab01-ubuntu, 25 GB disk as a single file, 2 CPU, 2 GB RAM, NAT. Took vm-settings.png before the first power-on.
5. Installed Ubuntu Server: Ubuntu Server (not minimized), DHCP (ens33, 192.168.100.128/24), no proxy, default mirror, entire disk (no encryption), server name lab01, OpenSSH server installed, no snaps.
6. Logged in and checked what the guest sees:

```
nproc
free -h
df -h /
lsblk
ip a
```

7. From the host (PowerShell, in the evidence folder) saved the release info:

```
ssh zhansaya@192.168.100.128 lsb_release -a | Out-File -Encoding utf8 guest-release.txt
```

8. Shut the guest down (`sudo poweroff`) and took the snapshot **clean-install**.
9. Broke the guest (option A, delete the hostname):

```
cat /etc/hostname
sudo rm /etc/hostname
sudo reboot
cat /etc/hostname
hostnamectl
```

10. Reverted to clean-install and ran the same check again.

## Result

What the guest sees compared with what I gave it:

| Check | Guest shows | I gave it |
|---|---|---|
| `nproc` | 2 | 2 vCPU |
| `free -h` | 1.6 GiB total | 2 GB (a little less is normal, the kernel takes part of it) |
| `df -h /` | /dev/sda2, 25G size, 5.1G used, 19G free | 25 GB disk |

Output of `lsblk` in the guest:

```
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0    0   25G  0 disk
├─sda1   8:1    0    1M  0 part
└─sda2   8:2    0   25G  0 part /
sr0     11:0    1  2.7G  0 rom
```

(The loop devices are snap packages and are left out here.)

Disk: the root filesystem is the whole disk. There is only a 1 MB partition before it (boot loader), so almost nothing is missing between the 25 GB I created and what `df -h /` shows.

## What I broke and how I confirmed it

Option A: deleted /etc/hostname.

- Before: `cat /etc/hostname` printed lab01.
- Broke it: `sudo rm /etc/hostname`, then `sudo reboot`.
- Confirmed with `cat /etc/hostname` → `No such file or directory`, and `hostnamectl` → Static hostname: (unset).
- Observation: Transient hostname still showed lab01. The file was not recreated, so the break is confirmed by the missing file and the unset Static hostname.

## Rollback

Reverted to snapshot clean-install (VM → Snapshot → Revert to Snapshot), powered the guest on and ran the same commands:

```
cat /etc/hostname
hostnamectl
```

Result after rollback: `cat /etc/hostname` prints lab01, and `hostnamectl` shows Static hostname: lab01 (before the rollback it was (unset)). The deleted file is back, so the snapshot restored the guest to its clean state. The snapshot list after the rollback is in snapshot-list.png.

## What did not work the first time

- **SSH closed right after the password prompt.** I saw `Connection closed by 192.168.100.128 port 22`. The guest log said `Timeout before authentication`, so I took too long to type the password. I repeated the command and entered the password right away, and it worked.
- **Wrong file name in a command.** I typed `cat /etc/zhansaya` instead of `cat /etc/hostname` and got `No such file or directory`. The file I wanted is hostname; the message was my typo, not a fault.
- **Working inside a .zip.** PowerShell could not enter `repo_starter.zip\...` because an archive is not a normal folder. I extracted it and worked in the extracted folder.
- **Default memory.** The wizard proposed 6144 MB; I changed it to 2048 MB.
- **Login and reboot.** At first I typed `sudo` into the login prompt instead of my username and got `Login incorrect`. Also, I expected the hostname to disappear right after `rm /etc/hostname`, but I had to reboot the VM first.
- **Rollback to the wrong snapshot.**
  - What I saw: after the rollback the system state was confusing and the hostname result was not what I expected.
  - What it turned out to be: I had already broken the hostname the night before and tried to break it again today. When restoring, I reverted to a snapshot I had just made today instead of my original `clean-install` from the night before, so the hostname states got mixed up.
  - What I did: I opened the Snapshot Manager, found the correct `clean-install` snapshot, and reverted to it explicitly. After that the system was restored correctly.

## Evidence

- [evidence/vm-settings.png](evidence/vm-settings.png) — CPU, memory and disk as configured, taken before the first power-on
- [evidence/guest-release.txt](evidence/guest-release.txt) — output of `lsb_release -a` from the guest: Ubuntu 26.04.1 LTS
- [evidence/broken.png](evidence/broken.png) — the guest after deleting /etc/hostname: the failing command and its output
- [evidence/snapshot-list.png](evidence/snapshot-list.png) — snapshot list with clean-install, taken after the rollback
