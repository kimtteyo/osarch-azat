# Ticket 2 — We are kitting out the new office

Author: Azat Zhansaya
Prices checked: 15.11.2026

## 1. What was asked

> From: Daniyar K. (Director)
> Subject: computers for the new office
>
> We are opening the second office and need four computers — accountant,
> sales, web developer, designer. Budget 3,000,000 tenge for everything.
> Everyone says we should just buy the same four machines, is that right?
> Make sure they last a few years. Monitors included.

## 2. What was actually needed

**Where the request is wrong:**

- **"Just buy the same four machines" — no.** The four people put different loads
  on a computer. Four identical machines means choosing one level for everyone:
  - four copies of the designer's machine cost 4 × 914,990 = **3,659,960 KZT**,
    659,960 over budget;
  - four copies of the accountant's machine cost 4 × 537,665 = **2,150,660 KZT**,
    in budget, but the designer gets no graphics card and the sales manager and
    developer get 16 GB and start swapping.

  The money has to go where each person's bottleneck is. Identical parts *inside*
  are still a good idea, so I kept the same board, SSD, PSU and case in all four.
- **"Budget for everything"** — it is not everything. The budget does not cover
  software the roles need: 1C for the accountant and Adobe or Figma subscriptions
  for the designer cost money every year.
- **"Last a few years"** in November 2026 is expensive: DDR5 memory costs about
  113,000–123,000 KZT per 16 GB, the biggest single cost in three of the builds.

**What the request left out, and what I assumed:**

| Left out | What I assumed |
|---|---|
| What each person actually runs | Accountant: 1C + Excel. Sales: CRM in a browser + video calls. Developer: web stack with Docker. Designer: Figma, Photoshop, Illustrator, web and some print; no video or 3D. |
| Which operating system | Windows 11 Pro on all four: the brief requires a licensed OS, and 1C and Adobe need Windows. Pro, not Home, for BitLocker and domain join later. |
| How many monitors and what size | One 24" for everyone, two for the developer, one 27" QHD IPS for the designer. |
| Keyboards, mice, headsets, UPS | Not in "monitors included". I left a reserve for them (section 3). |
| Who assembles and services them | We assemble ourselves (question 2 compares with buying pre-built). |
| Which shop | Kazakh shops with delivery inside Kazakhstan, the cheapest one I could confirm for each part. |

**What I would have asked Daniyar:**

1. Does the designer prepare files for print? If yes, a calibrated monitor is needed.
2. Are keyboards, mice and headsets for video calls already there?
3. Are 1C and Adobe licences paid separately, or must they fit in the 3,000,000?
4. Does "a few years" mean 3 or 5? It decides between AM5 and the cheaper AM4 (section 3).

## 3. What I did

1. Wrote down the load and the bottleneck for each role (`builds.md`).
2. Chose one shared platform and changed only CPU, memory, graphics and monitor between roles.
3. Found each part in a Kazakh shop (Shop.kz, Forcecom.kz, ctech.kz, notik.kz and others),
   saved a screenshot of every product page in `evidence/vendor-quotes/` and recorded
   shop, price and date in `budget.csv`.
4. Added up the totals with a script, not by hand.

### Budget

| Role | Total, KZT |
|---|---|
| Accountant | 537,665 |
| Sales manager | 641,535 |
| Web developer | 697,651 |
| Designer | 914,990 |
| **Total** | **2,791,841** |
| Reserve | 208,159 |

**Why I did not spend the reserve:** the brief says "monitors included" but says
nothing about keyboards, mice or headsets for the sales manager's video calls, so I
assume they must also come out of the 3,000,000. On top of that, the chosen RTX 5060
was out of stock on 15.11, and a replacement may cost more. If Daniyar confirms the
peripherals already exist, the first thing to buy from the reserve is the accountant's
second memory stick (122,990 KZT, see question 1).

### Decisions and alternatives

- **AM5 (DDR5) instead of the older AM4 (DDR4).** 32 GB DDR4 costs 139,220 KZT
  against 226,860 KZT for DDR5 — 87,640 KZT less per machine. I did not take it:
  AM4 gets no new processors, and the director asked for machines that "last a few
  years". With AM5 an upgrade in 18 months is a part, not a new machine.
  Trade-off: more expensive memory today.
- **Ryzen 7 7700 for the developer and designer, Ryzen 5 7600 for the others.**
  The 8-core costs only 8,180 KZT more; for 1C and a browser it would do nothing.
- **Graphics card only for the designer.** The built-in Radeon drives two monitors
  for the developer. Trade-off: the developer cannot do GPU work (ML) locally.
- **RTX 5060 8 GB, not 5060 Ti 16 GB** (348,700 KZT, +154,200): the Ti would fit in
  the reserve, but 16 GB of video memory matters for 3D, video and AI, not for
  Figma and Photoshop. I would rather keep the money than buy a capability nobody uses.
- **One 16 GB stick for the accountant, not two 8 GB.** Single channel is a little
  slower, but the upgrade later is one stick into an empty slot.
- **1 TB SSD everywhere, not 500 GB** (29,301 KZT cheaper): 500 GB fills up with
  1C databases, mail and project files within the "few years".
- **Windows 11 Pro at 78,100 KZT (notik.kz), not 58,595 KZT.** The cheaper page
  promises to e-mail "a licence key" and shows a Windows 10 box, so I could not
  confirm it is a genuine DSP licence that a company can show in an audit.

### The three questions

**1. Which machine will I upgrade first, in 18 months, and why?**

The accountant's memory. It runs on one 16 GB stick by design, and by then 1C
databases and Excel files will be larger. The upgrade is one more 16 GB stick into
the free slot (122,990 KZT today): it doubles the memory and switches to dual
channel, which also speeds up the built-in graphics. It is the cheapest upgrade with
the biggest effect, and it can even be done now from the reserve if the peripherals
are already in the office.

**2. Pre-built machines: what does the company gain and lose?**

| Role | Pre-built found | Price, KZT |
|---|---|---|
| Accountant, sales, developer | HP Pro Tower 400 G9 (881Z3EA): i3-14100 (4 cores), 8 GB DDR5, 512 GB SSD, Win 11 Pro, keyboard + mouse — ITmag.kz | 452,413 each |
| Designer | ARDOR GAMING NEO M264: Ryzen 5 7500F, 16 GB DDR5, 1 TB, RTX 5050 8 GB, no OS — DNS | 508,590 + Windows 78,100 |

With the same monitors as in my builds, the four pre-built machines cost
**2,215,500 KZT** — 576,341 KZT less than my builds.

*Gains:* that money; HP's warranty and onsite service (the page promises a 3-year
next-business-day extension, though the specification table says 12 months, so this
must be confirmed in writing); one supplier; keyboard and mouse included; no
assembly time, and nobody in the office has to diagnose a faulty part.

*Losses:* the HP has half the memory of my cheapest build and a quarter of what I
gave sales and development, a 4-core CPU for the developer's builds and containers,
and 512 GB of storage. The designer's machine has a weaker graphics card and an
entry-level A620 board. Bringing these machines up to what the roles need would eat
most of the saving, and HP's own case and board limit later upgrades.

My conclusion: a pre-built HP (with one extra memory stick) is a fair choice for the
accountant; for the sales manager, developer and designer it saves money by
under-buying exactly where their bottleneck is.

**3. Who will complain within a month, and about what?**

The accountant, at the first month-end close. With 1C building reports, two large
Excel workbooks and the bank client open at once, 16 GB in single channel will
start swapping and the reports will take noticeably longer. This is the trade-off
I accepted to give 32 GB to sales and development, and it is why the accountant's
memory is the first upgrade.

## 4. Evidence

- [budget.csv](budget.csv) — every part with price in KZT, shop, screenshot and date; totals per role
- [builds.md](builds.md) — load, bottleneck and trade-off for each machine
- [evidence/pcpartpicker-links.md](evidence/pcpartpicker-links.md) — every price with its shop and screenshot, the pre-built machines and the rejected alternatives; why PCPartPicker was not usable
- [evidence/vendor-quotes/](evidence/vendor-quotes/) — screenshots of each product page with the price, taken 15.11.2026

## 5. What I would do differently

I would ask one shop for a written quote for all four machines instead of
collecting prices from seven shops. Prices and stock change daily — the graphics
card I chose was already out of stock when I checked — and one quote would fix the
prices for a few days, give a single warranty contact and probably a discount for
buying four sets at once.
