\# Lab 2: Windows 11 guest and network



Pair: Zhansaya Azat / (Solo)   Driver first half: Zhansaya Azat

Machine: Windows host, VMware Workstation Pro 26H1, guests: lab01-ubuntu (Ubuntu Server 26.04.1 LTS, amd64) and lab02-win11 (Windows 11 Enterprise Evaluation, x64)

Date: 23.10.2026



\## Network diagram



```

\&#x20;                Internet

\&#x20;                   |

\&#x20;    \\\[ Host: laptop ]   real network: Wi-Fi 192.168.8.189

\&#x20;                   |

\&#x20;     ( NAT router of VMware )   gateway 192.168.100.2

\&#x20;                   |

\&#x20;  ===== virtual switch: VMnet8 (NAT), 192.168.100.0/24 =====

\&#x20;         |                              |

\&#x20; \\\[ lab01 (Ubuntu) ]            \\\[ lab02-win11 (Windows 11) ]

\&#x20; ens33                         Ethernet0

\&#x20; 192.168.100.130               192.168.100.131

```



\## Why this network mode



I used VMware NAT (VMnet8) mode for both guests.



Requirement: the guests must reach each other and the internet.



NAT meets both. Both guests are on the same virtual switch and in the same subnet (192.168.100.0/24), so they see each other, and the VMware NAT router gives them internet access (ping 8.8.8.8 works from both).



I did not use bridged because NAT already meets the requirement, and on a campus network bridged may be dropped by MAC filtering (the guest gets no address and no error). I did not try it.



I did not use host-only because it has no internet access.



\## Addresses



| Guest | Interface | IPv4 address |

|---|---|---|

| Ubuntu (lab01) | ens33 | 192.168.100.130/24 |

| Windows 11 (lab02-win11) | Ethernet0 | 192.168.100.131/24 |



Gateway: 192.168.100.2. Evidence: `ipconfig-windows.txt`, `ip-addr-linux.txt`.



\## Firewall



Windows -> Linux ping worked at once (4 of 4 replies). Linux -> Windows ping failed: 4 transmitted, 0 received, 100% packet loss.



`Get-NetConnectionProfile` showed `NetworkCategory: Public`. Windows treats the new network as public, and Windows Defender Firewall drops incoming ICMP echo requests on it. The network itself was fine.



I did not turn the firewall off. I added one specific rule in PowerShell run as administrator:



```

New-NetFirewallRule -DisplayName "Lab02 - allow ping (ICMPv4 echo)" -Direction Inbound -Protocol ICMPv4 -IcmpType 8 -RemoteAddress LocalSubnet -Action Allow

```



The rule allows only inbound ICMPv4 echo requests (type 8), and only from the local subnet. `Get-NetFirewallRule -DisplayName "Lab02\\\*"` shows `Enabled: True`, `Direction: Inbound`, `Action: Allow`.



After the rule, Linux -> Windows: 4 transmitted, 4 received, 0% loss (`ttl=128`, so Windows answered). Internet: `ping 8.8.8.8` works from both guests (2 of 2 replies, about 115 ms). Evidence: `ping-both-ways.txt`.



\## Overcommitment experiment



Host: 16 GB RAM (15.1 GB usable). Promised to the guests: Ubuntu 8 GB + Windows 12 GB = 20 GB, which is 1.25x the host RAM. Each single guest is below the host total.



I loaded both guests: `stress-ng --vm 1 --vm-bytes 90% --vm-keep --timeout 300s` in Ubuntu, and many heavy tabs open in Edge in Windows.



All numbers were measured on the host, with the same tool and view (Task Manager -> Performance -> Memory).



| | Before | After |

|---|---|---|

| In use | 6.8 GB | 15.0 GB (99%) |

| Compressed | 0 MB | 396 MB |

| Available | 8.3 GB | 146 MB |

| Committed | 7.6 / 24.1 GB | 34.2 / 38.4 GB |

| Cached | 4.1 GB | 422 MB |



What happened: Available memory fell from 8.3 GB to 146 MB and the cache was dropped from 4.1 GB to 422 MB. Compressed memory grew from 0 MB to 396 MB, so the host started compressing memory. Committed memory rose to 34.2 GB, far above the 16 GB of RAM, so the promised memory was only possible because the commit limit includes the page file on disk (the limit grew from 24.1 GB to 38.4 GB). The number that shows compression in the "after" screenshot is "In use (compressed)": 396 MB. Disk activity did not clearly change (22% before, 16% after), so my screenshots do not show heavy swapping by themselves.



Host behaviour: nothing lagged. The mouse and windows stayed responsive, even with only 146 MB available. VMware showed no warning when starting both guests. "Killed" did not appear in Ubuntu.



Restore: after the experiment I stopped the load, shut both guests down and set the allocations back to Ubuntu 2048 MB and Windows 4096 MB. Both guests start and still ping each other (`ping -n 2 192.168.100.130` from Windows: 2 of 2 replies).



Evidence: `host-memory-before.png`, `host-memory-after.png`.



\## What did not work



\- SSH from Windows to Ubuntu first gave "Permission denied", because I used the user name `student` from the lab text instead of my own Ubuntu user `zhansaya`.

\- `New-NetFirewallRule` gave "Access is denied" in a PowerShell without administrator rights. It worked in PowerShell run as administrator.

\- I pasted the output of a PowerShell command into cmd by mistake, and cmd printed "is not recognized" errors. It was harmless and changed nothing.

\- Windows 11 asked for a work or school account during setup. I did not use my university account and created a local account instead.
