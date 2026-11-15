# Four builds for the second office

All prices in KZT, checked on 15.11.2026. Every row has its shop and a
screenshot in `budget.csv` and `evidence/vendor-quotes/`.
All four share one platform (AMD AM5, MSI PRO B650M-P board, 1 TB NVMe SSD,
550 W PSU, DeepCool CC560 V2 case, Windows 11 Pro), so spare parts and repairs
are the same everywhere. They differ where the load differs: CPU, memory,
graphics and monitor.

| Role | CPU | Memory | Graphics | Monitor | Total, KZT |
|---|---|---|---|---|---|
| Accountant | Ryzen 5 7600 | 16 GB (1 stick) | built-in | 24" FHD | 537,741 |
| Sales manager | Ryzen 5 7600 | 32 GB | built-in | 24" FHD | 641,611 |
| Web developer | Ryzen 7 7700 | 32 GB | built-in | 2 × 24" FHD | 707,381 |
| Designer | Ryzen 7 7700 | 32 GB | RTX 5060 8 GB | 27" QHD IPS | 914,990 |
| **Total** | | | | | **2,801,723** |

Budget 3,000,000 → 198,277 left as a reserve (see README, section 3).

---

### Build 1 — accountant

**Load:** 1C:Enterprise, Excel with large workbooks, bank client in a browser,
a few tabs. Heavy only at month end, when reports are built.

**Bottleneck:** single-thread CPU speed (1C report building) and memory once
Excel, 1C and the browser are open together. Graphics: none.

**Trade-off:** the cheapest build. 16 GB is one stick, not two: it runs in
single channel, which slows the built-in graphics a little, but leaves the
second slot free, so the upgrade to 32 GB is one more stick (122,990 KZT),
not a new kit.

| Part | Model | Price, KZT | Shop | Screenshot |
|---|---|---|---|---|
| CPU | AMD Ryzen 5 7600 OEM (6C/12T, AM5, iGPU) | 92,810 | [Forcecom.kz](https://forcecom.kz/catalog/processors/model/361014/) | [01](evidence/vendor-quotes/01-cpu-ryzen5-7600-forcecom.png) |
| CPU cooler | DeepCool GammaXX GT V2 RGB | 16,990 | [Shop.kz](https://shop.kz/offer/kuler-deepcool-gammaxx-gt-v2-rgb/) | [03](evidence/vendor-quotes/03-cooler-gammaxx-gt-v2-shopkz.png) |
| Motherboard | MSI PRO B650M-P (AM5, mATX) | 61,990 | [Shop.kz](https://shop.kz/offer/materinskaya-plata-msi-pro-b650m-p-am5/) | [04](evidence/vendor-quotes/04-mb-msi-b650m-p-shopkz.png) |
| Memory | AMD Radeon R5 DDR5-5200 16 GB (1x16) R5516G5200U1S-U | 122,990 | [Shop.kz](https://shop.kz/offer/ddr-5-dimm-16-gb-5200-mhz-amd-radeon-r5-entertainment-series-box-r5516g5200u1s-u/) | [05](evidence/vendor-quotes/05-ram-ddr5-16gb-shopkz.png) |
| SSD | Netac NV3000 1 TB NVMe PCIe 3.0 | 74,990 | [Shop.kz](https://shop.kz/offer/ssd-nakopitel-1-tb-netac-nv3000-m-2-pcie-3-0/) | [07](evidence/vendor-quotes/07-ssd-netac-1tb-shopkz.png) |
| PSU | MSI MAG A550BN 550 W 80+ Bronze | 22,590 | [Shop.kz](https://shop.kz/offer/blok-pitaniya-atx-550-w-msi-mag-a550bn/) | [08](evidence/vendor-quotes/08-psu-msi-a550bn-shopkz.png) |
| Case | DeepCool CC560 V2 Black (Midi Tower) | 28,990 | [Shop.kz](https://shop.kz/offer/korpus-deepcool-cc560-v2-black/) | [09](evidence/vendor-quotes/09-case-cc560-v2-shopkz.png) |
| OS | Windows 11 Pro 64-bit Russian DSP OEI Kazakhstan Only DVD FQC-10548 | 78,100 | [notik.kz](https://notik.kz/shop/software/operacionnaya-sistema-microsoft-windows-11-pro/) | [11](evidence/vendor-quotes/11-windows-11-pro-notikkz.png) |
| Monitor | AOC 24B31H 23.8" IPS 1920x1080 120 Hz (HDMI, VGA) | 38,291 | [ITmag.kz](https://itmag.kz/p/117405-monitor-23-8-aoc-24b31h-01-ips-1920x1080-1/) | [12](evidence/vendor-quotes/12-monitor-aoc-24b31h.png) |

**Total:** 537,741 KZT (`budget.csv`, rows 2–10)

### Build 2 — sales manager

**Load:** CRM in a browser, 30–40 tabs, Excel, several hours of video calls a
day, often at the same time.

**Bottleneck:** memory, not CPU. A browser with forty tabs plus a video call
takes 11–12 GB; with 16 GB the machine would start swapping during a call.

**Trade-off:** the same 6-core Ryzen 5 7600 as the accountant (the CPU mostly
idles here) and the money spent on 32 GB instead: +103,870 KZT over 16 GB.

| Part | Model | Price, KZT | Shop | Screenshot |
|---|---|---|---|---|
| CPU | AMD Ryzen 5 7600 OEM (6C/12T, AM5, iGPU) | 92,810 | [Forcecom.kz](https://forcecom.kz/catalog/processors/model/361014/) | [01](evidence/vendor-quotes/01-cpu-ryzen5-7600-forcecom.png) |
| CPU cooler | DeepCool GammaXX GT V2 RGB | 16,990 | [Shop.kz](https://shop.kz/offer/kuler-deepcool-gammaxx-gt-v2-rgb/) | [03](evidence/vendor-quotes/03-cooler-gammaxx-gt-v2-shopkz.png) |
| Motherboard | MSI PRO B650M-P (AM5, mATX) | 61,990 | [Shop.kz](https://shop.kz/offer/materinskaya-plata-msi-pro-b650m-p-am5/) | [04](evidence/vendor-quotes/04-mb-msi-b650m-p-shopkz.png) |
| Memory | Kingston Fury Beast DDR5-6000 32 GB (2x16) KF560C36BBE2K2-32 | 226,860 | [ctech.kz](https://ctech.kz/p130445162-kingston-fury-beast.html) | [06](evidence/vendor-quotes/06-ram-ddr5-32gb-ctechkz.png) |
| SSD | Netac NV3000 1 TB NVMe PCIe 3.0 | 74,990 | [Shop.kz](https://shop.kz/offer/ssd-nakopitel-1-tb-netac-nv3000-m-2-pcie-3-0/) | [07](evidence/vendor-quotes/07-ssd-netac-1tb-shopkz.png) |
| PSU | MSI MAG A550BN 550 W 80+ Bronze | 22,590 | [Shop.kz](https://shop.kz/offer/blok-pitaniya-atx-550-w-msi-mag-a550bn/) | [08](evidence/vendor-quotes/08-psu-msi-a550bn-shopkz.png) |
| Case | DeepCool CC560 V2 Black (Midi Tower) | 28,990 | [Shop.kz](https://shop.kz/offer/korpus-deepcool-cc560-v2-black/) | [09](evidence/vendor-quotes/09-case-cc560-v2-shopkz.png) |
| OS | Windows 11 Pro 64-bit Russian DSP OEI Kazakhstan Only DVD FQC-10548 | 78,100 | [notik.kz](https://notik.kz/shop/software/operacionnaya-sistema-microsoft-windows-11-pro/) | [11](evidence/vendor-quotes/11-windows-11-pro-notikkz.png) |
| Monitor | AOC 24B31H 23.8" IPS 1920x1080 120 Hz (HDMI, VGA) | 38,291 | [ITmag.kz](https://itmag.kz/p/117405-monitor-23-8-aoc-24b31h-01-ips-1920x1080-1/) | [12](evidence/vendor-quotes/12-monitor-aoc-24b31h.png) |

**Total:** 641,611 KZT (`budget.csv`, rows 11–19)

### Build 3 — web developer

**Load:** IDE, Docker containers (database, backend), local build tools,
two or three browsers for testing, documentation on a second screen.

**Bottleneck:** memory first (each container and browser keeps its own copy of
everything), then CPU cores during builds.

**Trade-off:** Ryzen 7 7700 (8 cores) for only 8,180 KZT more than the Ryzen 5,
the best value in the list. Two 24" FHD monitors instead of one 27" QHD: for
code, a second screen helps more than more pixels. The second monitor
(AOC 24B3QA2) has DisplayPort, so the built-in graphics drives both screens
(HDMI + DisplayPort on the board) without a graphics card.

| Part | Model | Price, KZT | Shop | Screenshot |
|---|---|---|---|---|
| CPU | AMD Ryzen 7 7700 OEM (8C/16T, AM5, iGPU) | 100,990 | [Shop.kz](https://shop.kz/offer/protsessor-amd-ryzen-7-7700-am5-oem/) | [02](evidence/vendor-quotes/02-cpu-ryzen7-7700-shopkz.png) |
| CPU cooler | DeepCool GammaXX GT V2 RGB | 16,990 | [Shop.kz](https://shop.kz/offer/kuler-deepcool-gammaxx-gt-v2-rgb/) | [03](evidence/vendor-quotes/03-cooler-gammaxx-gt-v2-shopkz.png) |
| Motherboard | MSI PRO B650M-P (AM5, mATX) | 61,990 | [Shop.kz](https://shop.kz/offer/materinskaya-plata-msi-pro-b650m-p-am5/) | [04](evidence/vendor-quotes/04-mb-msi-b650m-p-shopkz.png) |
| Memory | Kingston Fury Beast DDR5-6000 32 GB (2x16) KF560C36BBE2K2-32 | 226,860 | [ctech.kz](https://ctech.kz/p130445162-kingston-fury-beast.html) | [06](evidence/vendor-quotes/06-ram-ddr5-32gb-ctechkz.png) |
| SSD | Netac NV3000 1 TB NVMe PCIe 3.0 | 74,990 | [Shop.kz](https://shop.kz/offer/ssd-nakopitel-1-tb-netac-nv3000-m-2-pcie-3-0/) | [07](evidence/vendor-quotes/07-ssd-netac-1tb-shopkz.png) |
| PSU | MSI MAG A550BN 550 W 80+ Bronze | 22,590 | [Shop.kz](https://shop.kz/offer/blok-pitaniya-atx-550-w-msi-mag-a550bn/) | [08](evidence/vendor-quotes/08-psu-msi-a550bn-shopkz.png) |
| Case | DeepCool CC560 V2 Black (Midi Tower) | 28,990 | [Shop.kz](https://shop.kz/offer/korpus-deepcool-cc560-v2-black/) | [09](evidence/vendor-quotes/09-case-cc560-v2-shopkz.png) |
| OS | Windows 11 Pro 64-bit Russian DSP OEI Kazakhstan Only DVD FQC-10548 | 78,100 | [notik.kz](https://notik.kz/shop/software/operacionnaya-sistema-microsoft-windows-11-pro/) | [11](evidence/vendor-quotes/11-windows-11-pro-notikkz.png) |
| Monitor | AOC 24B31H 23.8" IPS 1920x1080 120 Hz (HDMI, VGA) | 38,291 | [ITmag.kz](https://itmag.kz/p/117405-monitor-23-8-aoc-24b31h-01-ips-1920x1080-1/) | [12](evidence/vendor-quotes/12-monitor-aoc-24b31h.png) |
| Monitor | AOC 24B3QA2 23.8" IPS 1920x1080 120 Hz (DP, HDMI) | 57,590 | [Shop.kz](https://shop.kz/offer/monitor-23-8-aoc-24b3qa2-01-black/) | [13](evidence/vendor-quotes/13-monitor-aoc-24b3qa2.png) |

**Total:** 707,381 KZT (`budget.csv`, rows 20–29)

### Build 4 — designer

**Load:** Figma, Photoshop and Illustrator with large layered files, export for
web and print, many reference images open.

**Bottleneck:** graphics and screen. Photoshop and Figma use the GPU for the
canvas, filters and zoom; colour work needs an IPS panel that covers sRGB.

**Trade-off:** the only build with a graphics card: RTX 5060 8 GB, not the
RTX 5060 Ti 16 GB (348,700 KZT, +154,200). 16 GB of video memory matters for 3D,
video and AI tools, which I assumed the designer does not use. The monitor is a
27" QHD IPS with good sRGB coverage, not a calibrated professional monitor:
fine for web, not reliable for print colour proofs.

**Risk:** on 15.11 the RTX 5060 was out of stock at Forcecom. If it is still
out of stock when ordering, the replacement comes out of the reserve.

| Part | Model | Price, KZT | Shop | Screenshot |
|---|---|---|---|---|
| CPU | AMD Ryzen 7 7700 OEM (8C/16T, AM5, iGPU) | 100,990 | [Shop.kz](https://shop.kz/offer/protsessor-amd-ryzen-7-7700-am5-oem/) | [02](evidence/vendor-quotes/02-cpu-ryzen7-7700-shopkz.png) |
| CPU cooler | DeepCool GammaXX GT V2 RGB | 16,990 | [Shop.kz](https://shop.kz/offer/kuler-deepcool-gammaxx-gt-v2-rgb/) | [03](evidence/vendor-quotes/03-cooler-gammaxx-gt-v2-shopkz.png) |
| Motherboard | MSI PRO B650M-P (AM5, mATX) | 61,990 | [Shop.kz](https://shop.kz/offer/materinskaya-plata-msi-pro-b650m-p-am5/) | [04](evidence/vendor-quotes/04-mb-msi-b650m-p-shopkz.png) |
| Memory | Kingston Fury Beast DDR5-6000 32 GB (2x16) KF560C36BBE2K2-32 | 226,860 | [ctech.kz](https://ctech.kz/p130445162-kingston-fury-beast.html) | [06](evidence/vendor-quotes/06-ram-ddr5-32gb-ctechkz.png) |
| SSD | Netac NV3000 1 TB NVMe PCIe 3.0 | 74,990 | [Shop.kz](https://shop.kz/offer/ssd-nakopitel-1-tb-netac-nv3000-m-2-pcie-3-0/) | [07](evidence/vendor-quotes/07-ssd-netac-1tb-shopkz.png) |
| GPU | Inno3D GeForce RTX 5060 Twin X2 OC 8 GB (out of stock on 15.11) | 194,500 | [Forcecom.kz](https://forcecom.kz/catalog/graphics-cards/model/531798/) | [10](evidence/vendor-quotes/10-gpu-rtx5060-forcecom.png) |
| PSU | MSI MAG A550BN 550 W 80+ Bronze | 22,590 | [Shop.kz](https://shop.kz/offer/blok-pitaniya-atx-550-w-msi-mag-a550bn/) | [08](evidence/vendor-quotes/08-psu-msi-a550bn-shopkz.png) |
| Case | DeepCool CC560 V2 Black (Midi Tower) | 28,990 | [Shop.kz](https://shop.kz/offer/korpus-deepcool-cc560-v2-black/) | [09](evidence/vendor-quotes/09-case-cc560-v2-shopkz.png) |
| OS | Windows 11 Pro 64-bit Russian DSP OEI Kazakhstan Only DVD FQC-10548 | 78,100 | [notik.kz](https://notik.kz/shop/software/operacionnaya-sistema-microsoft-windows-11-pro/) | [11](evidence/vendor-quotes/11-windows-11-pro-notikkz.png) |
| Monitor | MSI MAG 275QF 27" IPS 2560x1440, good sRGB | 108,990 | [Shop.kz](https://shop.kz/offer/monitor-27-msi-mag-275qf-black/) | [14](evidence/vendor-quotes/14-monitor-msi-275qf-ekatalog.png) |

**Total:** 914,990 KZT (`budget.csv`, rows 30–39)
