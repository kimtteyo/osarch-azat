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

**Total:** 537,741 KZT (`budget.csv`, rows 2–10)

### Build 2 — sales manager

**Load:** CRM in a browser, 30–40 tabs, Excel, several hours of video calls a
day, often at the same time.

**Bottleneck:** memory, not CPU. A browser with forty tabs plus a video call
takes 11–12 GB; with 16 GB the machine would start swapping during a call.

**Trade-off:** the same 6-core Ryzen 5 7600 as the accountant (the CPU mostly
idles here) and the money spent on 32 GB instead: +103,870 KZT over 16 GB.

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

**Total:** 914,990 KZT (`budget.csv`, rows 30–39)
