# Feedback on Azat Zhansaya's BUILD.md

Reviewer: Togzhan Ilyas
Commit reviewed: https://github.com/kimtteyo/osarch-azat/tree/85d79fbd6de755f0ff241baf83a5047567d64d17/tickets/ticket1-vm-build-doc
Hypervisor I used: VMware Workstation Pro on Windows. (Before this I used VMware Fusion on a MacBook.)

## First step where I got stuck

None. I did not get stuck at any step of this guide. The process was new to me, because before this I had only used a MacBook, but the guide was clear enough that I did not need outside help.

These steps had a reason that convinced me, so I did not have to guess:

* Step 6 (Memory 2048 MB, NAT): the "Why" lines explain why not to accept VMware's larger suggestion and why NAT is used instead of Bridged or Host-only.
* Step 10 (untick LVM): the guide explains that "erase disk" only touches the virtual 25 GB disk, and that LVM would leave Linux only about half of it.
* Step 17 (TPM encryption): the guide says clearly that the password cannot be recovered, so I wrote it down at once.

## Other places I hesitated

* Step 10: "Done → Done → Continue" does not say which screen each button belongs to (storage screen, summary screen, the red "Confirm destructive action" pop-up).
* Step 13: While typing a password in Linux nothing appears on the screen. The guide does not say this is normal.
* Step 13: `sudo apt upgrade -y` can open a pink/blue "restart services" window. The guide does not say what to press (Enter, the default).
* Step 16: The Easy Install screen can have a "Product key" field and possibly a Windows version drop-down. The guide does not say to leave the key empty or which version to choose.
* Step 20: Windows setup may show "Press any key to boot from CD or DVD" for a few seconds. The guide does not mention it.
* Step 23: The IP addresses from Steps 9 and 20 can change after a long shutdown or after restarting the NAT service. The guide does not say to re-check them if a ping fails.
* Before you start: The guide names the sites (Broadcom, ubuntu.com, microsoft.com/evalcenter) but not the exact pages, and it does not say whether Workstation Pro is free for company use.
* Before you hand it over: There is no list of what to give the developer (IP addresses, usernames and passwords, snapshot names `clean-install` and `network-ok`, the 90-day limit). OpenSSH is installed in Step 12, but the guide never shows how to connect, for example `ssh <username>@192.168.100.133`.

## Settings I would not have chosen without the document

* Step 5: Store the virtual disk as a single file, 25 GB (I would have kept the default split into several files).
* Step 6: Memory 2048 MB instead of the larger value VMware suggests, and NAT instead of Bridged.
* Step 10: Untick the LVM option. I did not know that otherwise Linux gets only about half of the disk.
* Step 12: Tick "Install OpenSSH server".
* Step 17: "Only the files needed to support a TPM are encrypted", and the warning that the password cannot be recovered.
* Step 18: A 64 GB disk for Windows (I would not have known that Windows 11 refuses a smaller disk).
* Step 22: A firewall rule that allows only ping from the local subnet, instead of switching the firewall off.

## One thing that worked well

* The "Why" lines and the "Check" lines. They explained the reason for each setting and let me confirm that a step worked before moving on. Before this I had only used a MacBook (VMware Fusion), so Windows, VMware Workstation Pro and most of the steps in this guide were completely new to me. Even so, the guide was very clear, and I could follow it from start to finish on Windows without outside help.

