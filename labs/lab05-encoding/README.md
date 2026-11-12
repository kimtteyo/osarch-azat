# Lab 5 — Encoding forensics

Pair: none (worked alone)                    Driver first half: Zhansaya Azat
Machine: lab01 (Ubuntu 26.04.1 LTS, VM); Windows 11 host for Excel and LibreOffice Calc
Date: 2026-11-12

## What I did

All "before" evidence was taken from the untouched original, before any change.

**1. Folder and checksum**
```
mkdir -p ~/labs/lab05-encoding/scripts ~/labs/lab05-encoding/evidence
scp $HOME\Downloads\staff-broken.csv zhansaya@192.168.100.130:~/labs/lab05-encoding/evidence/   (from Windows)
sha256sum staff-broken.csv
919027f1f8c71d85cba3f12aad0f6c927d4e0450cfb2a2d63378a69f14cab270  staff-broken.csv
```
Same hash on Windows (`Get-FileHash`), so the copy is intact (2460 bytes).

**2. What is it? (file and first 16 bytes)**
```
file staff-broken.csv | tee file-before.txt
staff-broken.csv: Non-ISO extended-ASCII text, with CRLF line terminators
file -e csv staff-broken.csv | tee -a file-before.txt
staff-broken.csv: Non-ISO extended-ASCII text, with CRLF line terminators
xxd -l 16 staff-broken.csv | tee hexdump-before.txt
00000000: d2e0 e12e b93b d4c8 ce3b c4ee ebe6 edee  .....;...;......
```

| Offset | Bytes | What they are |
|---|---|---|
| 00–02 | D2 E0 E1 | "Таб": three Cyrillic letters, one byte each (not UTF-8 pairs) |
| 03 | 2E | ASCII "." |
| 04 | B9 | "№" in RK1048 (one byte; in UTF-8 it takes three) |
| 05 | 3B | separator: semicolon |
| 06–08 | D4 C8 CE | "ФИО" |
| 09 | 3B | separator: semicolon |
| 0A–0F | C4 EE EB E6 ED EE | "Должно" (start of "Должность") |

No BOM: the file starts with D2, not EF BB BF. The first 16 bytes contain no
line ending and no Kazakh letter. The first CRLF (`0D 0A`) is at offset 0x2C
(`xxd staff-broken.csv | head -20`). The header is Cyrillic, not ASCII.

**3. Name the encoding**
```
iconv -f UTF-8 -t UTF-8 staff-broken.csv > /dev/null && echo valid
iconv: illegal input sequence at position 0          <- not UTF-8
python3 ../scripts/chars.py staff-broken.csv | grep -E '^===|U\+(04[5-9A-F]|FFFD)'
```
`scripts/chars.py` decodes the file with CP1251, RK1048 and PT154 and lists the
non-ASCII characters each one produces:

- CP1251: Ј, Ќ, Ї, Ґ, ў and similar letters that cannot occur in these names; no Қ, Ә, Ө, Ң, Ү, Ұ. Rejected.
- PT154: Ҙ, Ҝ, Ҫ and similar letters that are not in the Kazakh alphabet; Ғ, Ң, Ү, Ұ, Ө missing. Rejected.
- RK1048: exactly the Kazakh alphabet (Ә Ғ Қ Ң Ө Ұ Ү Һ І and lowercase) plus Russian letters. No U+FFFD. Accepted.

```
iconv -f RK1048 -t UTF-8 staff-broken.csv > /dev/null && echo ok
ok
```
Cross-check: byte 8D decodes to "Қ", which matches the e-mail a.kassymova for "Қасымова".

**Encoding: RK1048** (single-byte Kazakh Cyrillic code page).

**4. Name the line ending**
```
tr -cd '\r' < staff-broken.csv | wc -c
26
wc -l staff-broken.csv
26 staff-broken.csv
```
CR = LF = number of lines, so every line ends with `0D 0A`: **CRLF**, not mixed.

**5. BOM decision**

I made two versions: `staff-fixed.csv` (with BOM) and a test copy without BOM
(`tail -c +4 staff-fixed.csv > ~/staff-nobom.csv`), and opened both by
double-click.

| Reader | Without BOM | With BOM |
|---|---|---|
| Excel, double-click | garbage ("РўР°Р±.в„–…"), observed | correct, Kazakh letters intact, observed |
| LibreOffice Calc | correct, dialog says UTF-8, observed | correct, observed |
| cat in UTF-8 terminal | correct | correct (BOM is invisible) |
| Script reading first header | `Таб.№` | `\ufeffТаб.№` (invisible character) |

Decision: I added a BOM (the original had none). Excel decided it: without a BOM
it reads UTF-8 as CP1251, with a BOM it opens correctly. The cost is an invisible
U+FEFF in the first header for scripts that do not strip it.

**6. Convert** (`scripts/fix.sh`, run with `bash scripts/fix.sh` from `~/labs/lab05-encoding`)
```
{
  printf '\xEF\xBB\xBF'
  iconv -f "RK1048" -t UTF-8 "evidence/staff-broken.csv" | sed 's/\r$//'
} > evidence/staff-fixed.csv

evidence/staff-fixed.csv: Unicode text, UTF-8 (with BOM) text
00000000: efbb bfd0 a2d0 b0d0 b12e e284 963b d0a4  .............;..
```

| | Before | After |
|---|---|---|
| BOM | none | `EF BB BF` (exactly one) |
| "Т" | `D2` | `D0 A2` |
| "а" | `E0` | `D0 B0` |
| "б" | `E1` | `D0 B1` |
| "." | `2E` | `2E` |
| "№" | `B9` | `E2 84 96` |
| ";" | `3B` | `3B` |
| line end | `0D 0A` | `0A` |

**7. Verify**
```
file staff-fixed.csv        | tee file-after.txt
staff-fixed.csv: Unicode text, UTF-8 (with BOM) text
file -e csv staff-fixed.csv | tee -a file-after.txt
staff-fixed.csv: Unicode text, UTF-8 (with BOM) text
iconv -f UTF-8 -t UTF-8 staff-fixed.csv > /dev/null && echo valid
tr -cd '\r' < staff-fixed.csv | wc -c
awk -F, '{ print $NF "|" }' staff-fixed.csv | head -3
sha256sum staff-broken.csv
919027f1f8c71d85cba3f12aad0f6c927d4e0450cfb2a2d63378a69f14cab270  staff-broken.csv
```
Valid UTF-8, 0 CR bytes, `|` right after the date (no hidden CR), original
checksum unchanged.

Opened in: Excel 2108 (build 14332.20651, Microsoft Office LTSC Professional
Plus 2021; double-click, not the import wizard), LibreOffice Calc 26.8.3.1
(X86_64, Windows 11; import dialog accepted as proposed: "Автоматически" /
"Юникод (UTF-8)"), `cat` on Ubuntu 26.04.1 LTS over SSH from Windows Terminal.

## Result

The file was **RK1048**, **CRLF**, **no BOM**, separator `;`. It is now UTF-8
with one BOM and LF line endings, and the names (including Қасымова Әлия
Серікқызы) read correctly in Excel, LibreOffice Calc and `cat`
(`evidence/opens-correctly.png`).

What each application was doing wrong with the original / no-BOM files:

- **Excel:** with no BOM there is no hint that the file is UTF-8, so it assumes
  the Windows ANSI code page (CP1251 on this Russian-locale Windows). Each
  two-byte UTF-8 character was split into two single-byte characters, e.g.
  `D0 A2` ("Т") became "Р" + "ў". ASCII (digits, e-mails) survived because it is
  identical in both encodings.
- **LibreOffice Calc:** in "Automatic" mode it checks whether the bytes are valid
  UTF-8 and, since they are, picks UTF-8 with or without a BOM.
- **cat:** the terminal decodes output as UTF-8. The original RK1048 bytes are not
  valid UTF-8, so every Cyrillic letter is printed as a replacement symbol
  ("♦" or "?" boxes on the VM console, e.g. `1001;♦♦♦♦♦♦♦♦ ♦♦♦♦ ...`), while
  ASCII stays readable: digits, `;`, "E-mail", the e-mail addresses and dates
  (`a.kassymova@tumar-office.kz;12.03.2019`). The fixed file is UTF-8, so it
  matches the terminal.

Check yourself:

1. **Which byte told the encoding family, which the line ending?** The first byte
   `D2` (not `EF`, `FF` or `FE`) and Cyrillic as single bytes in 80–FF mean a
   single-byte code page. The line ending is `0D 0A` at offsets 0x2C–0x2D,
   confirmed by 26 CR = 26 LF.
2. **Why did Excel and LibreOffice differ?** Excel without a BOM assumes the
   system ANSI code page; Calc checks the bytes and detects valid UTF-8.
3. **If I had picked CP1251?** Every name with Ә, Ғ, Қ, Ң, Ө, Ұ, Ү, Һ or І would be
   wrong (decoded as Ј, Ќ, Ї, Ґ and similar). Purely Russian names would stay correct.
4. **What did the conversion change at the start of the file?** It added
   `EF BB BF`, re-encoded `D2 E0 E1` as `D0 A2 D0 B0 D0 B1` and `B9` as
   `E2 84 96`, and replaced `0D 0A` with `0A`.
5. **"Just open it in Notepad and Save As UTF-8".** It works only if Notepad
   guesses the right source encoding; otherwise it saves the garbage as UTF-8
   (double encoding). It is not an answer here because it gives no evidence of
   what the encoding was and changes the bytes with no record.

## What did not work the first time

- **`xxd -1 16` printed the help text.** I typed the digit one instead of the
  letter l, so `xxd` showed its usage and wrote it into `hexdump-before.txt`.
  Fix: `xxd -l 16 staff-broken.csv | tee hexdump-before.txt` overwrote the file;
  `cat` showed one line of 16 bytes.
- **Names showed as "♦" on the VM console.** I first thought the encoding was
  wrong. It was the console font, which lacks Kazakh letters. I stopped judging
  by eye, listed Unicode character names per candidate encoding
  (`scripts/chars.py`), and chose RK1048 from those. Screenshots are taken over
  SSH in Windows Terminal.
- **Python one-liner in bash gave `syntax error near unexpected token '('`.**
  I pasted Python into the shell, then wrote the heredoc as `<< ' EOF'` (space
  inside the quotes) so it never closed. Fix: Ctrl+C, then `<< 'EOF'` with `EOF`
  alone on the last line.
- **`fix.sh` contained `bash scripts/fix.sh` as its last line.** I typed the run
  command inside nano. It would have made the script call itself. Fix: deleted
  that line, saved, checked with `cat scripts/fix.sh`.
- **Excel showed `#########` in the date column.** Not an encoding problem: the
  column was too narrow. Fix: AutoFit Column Width (never saved the file).
- **`scp` run in the wrong shell.** I ran the Windows `scp $HOME\Desktop\...`
  command inside Ubuntu, where bash swallowed the backslashes. Fix: run it in
  PowerShell. The screenshot was in `OneDrive\Desktop`, found with
  `Get-ChildItem`. Earlier `ssh` also timed out once until the VM network was
  checked.

## Evidence

- [evidence/](evidence/)
  - `staff-broken.csv`: the untouched original; SHA-256 `919027f1…cab270` matches the Canvas file.
  - `staff-fixed.csv`: UTF-8 with one BOM, LF line endings; the result of `scripts/fix.sh`.
  - `file-before.txt`: `file` on the original: extended-ASCII text, CRLF (not UTF-8).
  - `hexdump-before.txt`: first 16 bytes of the original; shows no BOM, single-byte Cyrillic, `;`.
  - `file-after.txt`: `file` on the fixed file: UTF-8 with BOM.
  - `opens-correctly.png`: Excel, LibreOffice Calc and `cat` showing the same names correctly.
- [scripts/fix.sh](scripts/fix.sh): the conversion (RK1048 → UTF-8, CRLF → LF, BOM added).
- [scripts/chars.py](scripts/chars.py): lists characters per candidate code page; the basis for choosing RK1048.
