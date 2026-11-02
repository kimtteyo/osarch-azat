# Ticket 1 — New developer starts Monday, needs a test machine

Author: Azat Zhansaya
Host: Windows laptop, 16 GB LPDDR5, 12 threads, VMware Workstation Pro 26H1
Guests: ticket1-ubuntu (Ubuntu Server 26.04.1 LTS), ticket1-win11 (Windows 11 Enterprise Evaluation)
Built: 30.10–02.11.2026

## 1. What was asked

> From: Aigerim T. (Office Manager)
> Subject: test machine for new dev
>
> Hi, we have someone starting on Monday and he needs a test computer
> set up. Nothing special, just so he can try things without breaking
> anything. Can you write down how to do it so I can do the next one
> myself? Thanks

## 2. What was actually needed

**What the request left out, and what I assumed instead:**

- **Physical or virtual.** "A test computer" could mean buying a new PC.
  I assumed virtual machines on an existing computer: no purchase, ready by
  Monday, and "without breaking anything" is exactly what snapshots give.
- **Which operating system.** Not stated. I built two guests, Linux and
  Windows, because a developer usually has to test on both.
- **Which Linux edition.** I chose Ubuntu Server without a desktop: it needs
  about 2 GB of RAM, and this host has very little to spare. If the developer
  needs a graphical desktop, this assumption is wrong and Linux needs more memory.
- **How powerful the host is.** Not stated. I assumed a laptop like mine:
  16 GB RAM, 12 threads.
- **Internet and network.** Not stated. I assumed both guests need the
  internet and must see each other (for example, a web app on Linux opened
  from a browser on Windows).
- **Licences.** Not mentioned. The Windows guest is an Evaluation version:
  `08-win-license.txt` shows `EnterpriseEval edition`, `TIMEBASED_EVAL channel`
  and 90 days. After that it shuts itself down; a real employee needs a
  bought licence.

**Where the request is wrong:**

- **"Nothing special."** On a 16 GB host, two guests fit only with everything
  else closed. With my usual programs open, Task Manager showed 3.0 GB
  available; the guests need 6 GB. After closing programs: 7.1 GB, leaving
  about 1 GB for the host. The memory is LPDDR5 with 4 of 4 slots used, so it
  cannot be upgraded — the only option is to manage it.
- **"Without breaking anything."** A VM does not stop anyone from breaking
  things. Snapshots do: whatever breaks can be rolled back in a minute. So
  BUILD.md teaches snapshots, not only installation.
- **"So I can do the next one myself."** Aigerim has never opened a
  hypervisor, so BUILD.md is written for a beginner. She also needs a
  Broadcom account to download VMware and must keep the encryption password
  of the Windows VM — without it the VM cannot be opened.

**What I would have asked Aigerim:**

1. Linux, Windows or both? With or without a desktop?
2. Which computer will run the machines, and how much memory does it have?
3. Does he need internet inside the test machines?
4. Who pays for the Windows licence after the 90-day trial?

## 3. What I did

### Resources (calculated from the host)

Measured on 30.10.2026 (`evidence/00-host-specs.txt`):

| | Guests need | Host has | Left for host |
|---|---|---|---|
| Memory | 2 GB + 4 GB = 6 GB | 7.1 GB available (programs closed) | ~1.1 GB |
| CPU | 2 + 2 = 4 threads | 12 threads | 8 threads |
| Disk | 25 GB + 64 GB = 89 GB | 227.51 GB free on C: | 138.5 GB |

The CPU allocation stays under half of the host's threads (6). The disks are
dynamic, so they really use less than 89 GB. Free space fell from 279.54 GB
(Lab 1, 16.10) to 227.51 GB because the lab VMs are on the same disk.

### Steps

1. Measured the host: `systeminfo`, `Get-PSDrive C`, Task Manager → Memory.
2. Created `ticket1-ubuntu` (Typical wizard) and installed Ubuntu Server
   26.04.1. Address `192.168.100.133/24`. Snapshot `clean-install`.
3. Created `ticket1-win11`. VMware's Easy Install installed Windows by itself
   with a local account and VMware Tools. Address `192.168.100.135`.
   Saved the licence status with `slmgr /dlv`. Snapshot `clean-install`.
4. Ping from Linux to Windows failed; fixed with one firewall rule.
5. Linux had no internet; fixed the hung VMware NAT service (see below).
6. Saved the evidence as text from the host over SSH:

   ```
   ssh zhansaya@192.168.100.133 "uname -a; cat /etc/os-release" | Out-File -Encoding utf8 04-guest-uname.txt
   ssh zhansaya@192.168.100.133 "ping -c 4 192.168.100.135; ping -c 4 8.8.8.8; ping -c 4 google.com" | Out-File -Encoding utf8 05-ping-between-guests.txt
   ```

7. Took snapshots `network-ok` on both guests.
8. Wrote BUILD.md. It was not tested by another person before submission;
   the first test is the peer review in week 5.

### Settings that differ from the default

| Setting | Default | Mine | Why |
|---|---|---|---|
| Ubuntu memory | VMware's suggestion (6144 MB in Lab 1) | 2048 MB | Server needs ~2 GB; only 7.1 GB is available for both guests |
| Ubuntu disk | split into multiple files | single file, 25 GB | one file is easier to copy and move |
| Ubuntu storage | LVM on | LVM off | with LVM, `/` gets only about half of the disk |
| OpenSSH server | not installed | installed | to save command output from the host as text |
| Windows install | manual setup | Easy Install | fewer steps for a beginner; local account, no Microsoft account |
| Windows encryption | — | only TPM files | Windows 11 needs TPM; VMware keeps the virtual TPM encrypted |
| Windows firewall | ICMP echo blocked | one rule: ping from local subnet only | guests must see each other; the rest of the firewall stays on |

### Decisions and alternatives

- **NAT, not Bridged or Host-only.** NAT gives both internet and
  guest-to-guest traffic: both guests are on VMnet8, 192.168.100.0/24.
  Bridged gives each guest its own MAC on the real network, and the
  university network filters by MAC. Host-only has no internet.
- **Ubuntu Server, not Desktop.** Saves about 2 GB of RAM that this host
  does not have. Trade-off: the developer gets no graphical desktop.
- **Easy Install, not manual Windows setup.** Faster and no questions about
  accounts, which suits Aigerim. Trade-off: I could not see what it
  configured, and it turned on automatic login without asking.
- **VMware Workstation Pro, not VirtualBox.** I already know it from Labs 1–2,
  and its NAT puts all guests in one network by default. Trade-off: Aigerim
  needs a Broadcom account; VirtualBox downloads without one.
- **One firewall rule, not turning the firewall off.** The rule allows only
  ICMP echo requests (type 8) and only from the local subnet.

### What went wrong

**Linux had no internet, although the guests could see each other.**
`evidence/05-ping-failed-no-internet.txt` shows the failure.
The guests could ping each other, so Ubuntu's network interface and the
virtual switch worked. Only traffic leaving for the internet failed, and in
VMware NAT mode that traffic goes through the VMware NAT service on the host.
So I looked at the host, not at Ubuntu.

On the host, in PowerShell as administrator, I checked the services:

```
Get-Service "VMware NAT Service", VMnetDHCP
Restart-Service "VMware NAT Service"
```

`Restart-Service` was not enough: the service did not come back up, and
`Start-Service` alone did not fix it either. The `vmnat` process had hung,
so I killed it and started the service again. It took two attempts:

```
Stop-Process -Name vmnat -Force
Start-Service "VMware NAT Service"
Get-Service "VMware NAT Service"
```

Then in Ubuntu I cleared the cached neighbour table (my first attempt had a
typo, `flush a11`), and the internet worked:

```
sudo ip neigh flush all
```

**Ping from Linux to Windows: 100% packet loss.** Windows treats the new
network as Public and the firewall drops incoming ping
(`07-ping-before-fix.txt`). I added one rule in PowerShell as administrator:

```
New-NetFirewallRule -DisplayName "Ticket1 - allow ping (ICMPv4 echo)" -Direction Inbound -Protocol ICMPv4 -IcmpType 8 -RemoteAddress LocalSubnet -Action Allow
```

**Not enough memory at first.** The first measurement showed 3.0 GB
available — not enough for two guests. After closing programs: 7.1 GB.
That is why BUILD.md tells the reader to close everything first.

## 4. Evidence

- [00-host-specs.txt](evidence/00-host-specs.txt) — host memory, CPU and free disk on the day of the build
- [01-new-vm-wizard.png](evidence/01-new-vm-wizard.png) — the Typical wizard used to create the VM (retaken after installation)
- [02-disk-settings.png](evidence/02-disk-settings.png) — 25 GB disk stored as a single file (retaken after installation)
- [03-network-adapter.png](evidence/03-network-adapter.png) — network adapter set to NAT (retaken after installation)
- [04-guest-uname.txt](evidence/04-guest-uname.txt) — kernel and Ubuntu 26.04.1 release of the guest, taken over SSH
- [05-ping-failed-no-internet.txt](evidence/05-ping-failed-no-internet.txt) — Linux had no internet before the NAT service was fixed
- [05-ping-between-guests.txt](evidence/05-ping-between-guests.txt) — after the fixes: the guests reach each other in both directions and the internet
- [06-snapshot-list.txt](evidence/06-snapshot-list.txt) — snapshots `clean-install` and `network-ok` exist
- [07-ping-before-fix.txt](evidence/07-ping-before-fix.txt) — ping to Windows failed before the firewall rule; network profile was Public
- [08-win-license.txt](evidence/08-win-license.txt) — Windows is an Evaluation licence, 90 days
- [09-ubuntu-vmx.txt](evidence/09-ubuntu-vmx.txt) — memory, CPUs and NAT as written in the VM configuration file
- `step-*.png` — screenshots used in BUILD.md

Screenshots 01–03 were taken after installation, by opening the wizard again
and cancelling it, and from VM → Settings. The settings themselves are
confirmed by `09-ubuntu-vmx.txt`.

## 5. What I would do differently

I would test BUILD.md with someone outside IT before submitting, not after:
I wrote it for Aigerim, but I am the only person who has followed it, and I
already knew every answer. I would also take the screenshots during the
build, not afterwards — screenshots 01–03 had to be retaken, and Easy Install
skipped the Windows setup screens before I noticed.
