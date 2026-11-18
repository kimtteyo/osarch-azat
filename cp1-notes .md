# CP1 — OSArch, weeks 1–7

> 60 мин · 100 баллов · без VM, без админа · PowerShell + редактор + браузер
> Task 1 Inventory 25 · Task 2 Plan 30 · Task 3 Diagnose 45 (**транскрипт > ответ**)
> Сдача: `checkpoints/cp1/` → commit до 60-й минуты → **Copy permalink** → Canvas
> GitHub в браузере: **Add file → Create new file** → имя `checkpoints/cp1/README.md` (слэш = папка). Коммитить каждые 10–15 мин.

---

## 0. Help — как быстро найти ответ самой

|Нужно|PowerShell|Linux|
|-|-|-|
|Найти команду по слову|`Get-Command *disk*` · `Get-Command -Noun *Process*`|`man -k disk` (= `apropos disk`)|
|Справка + примеры|`Get-Help Get-Volume -Examples`|`man lsblk` → `/слово` поиск, `n` дальше, `q` выход|
|Один параметр|`Get-Help Get-Process -Parameter Id`|`lsblk --help`|
|Какие поля есть у объекта|`Get-CimInstance Win32_Processor \| Get-Member`|—|
|Показать ВСЕ поля|`... \| Format-List *`|—|
|Найти класс WMI|`Get-CimClass Win32_*memory*`|—|
|Онлайн (разрешено)|learn.microsoft.com → имя cmdlet|man7.org, manpages.ubuntu.com|

Если `Get-Help` пишет «help not found» → `Get-Help <cmd> -Online` (откроет Microsoft Learn).
Версия PS: `$PSVersionTable.PSVersion` (powershell.exe = 5.1, pwsh.exe = 7).

---

## 1. Task 1 — Inventory: вставь блок целиком в консоль PowerShell

Пишет `inventory.txt` с командой над каждым выводом (= evidence «show the command»). Ошибки (Access denied) тоже попадут в файл — это твой «what did not work». Вставлять в консоль, а не запускать .ps1 (execution policy может блокировать).

```powershell
$o = "$PWD\inventory.txt"; Remove-Item $o -ErrorAction SilentlyContinue
function S([string]$t, [scriptblock]$c) {
  "`n=== $t`nPS> $c" | Out-File $o -Append -Encoding utf8
  try { & $c 2>&1 | Out-String -Width 200 | Out-File $o -Append -Encoding utf8 }
  catch { "ERROR: $_" | Out-File $o -Append -Encoding utf8 }
}
S 'CPU' { Get-CimInstance Win32_Processor | Format-List Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed }
S 'RAM total GiB' { [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1) }
S 'RAM modules' { Get-CimInstance Win32_PhysicalMemory | Format-Table DeviceLocator, @{n='GB';e={$_.Capacity/1GB}}, Speed, ConfiguredClockSpeed, PartNumber -AutoSize }
S 'RAM slots / max' { Get-CimInstance Win32_PhysicalMemoryArray | Format-List MemoryDevices, @{n='MaxGB';e={$_.MaxCapacityEx/1MB}} }
S 'RAM used/free now' { Get-CimInstance Win32_OperatingSystem | Format-List @{n='TotalGB';e={[math]::Round($_.TotalVisibleMemorySize/1MB,1)}}, @{n='FreeGB';e={[math]::Round($_.FreePhysicalMemory/1MB,1)}} }
S 'Disks' { Get-PhysicalDisk | Format-Table FriendlyName, MediaType, BusType, @{n='GB';e={[math]::Round($_.Size/1GB)}} -AutoSize }
S 'Disks (fallback)' { Get-CimInstance Win32_DiskDrive | Format-Table Model, InterfaceType, @{n='GB';e={[math]::Round($_.Size/1GB)}} -AutoSize }
S 'Free space' { Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Format-Table DeviceID, @{n='SizeGB';e={[math]::Round($_.Size/1GB)}}, @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB)}} -AutoSize }
S 'Partition style' { Get-Disk | Format-Table Number, FriendlyName, PartitionStyle -AutoSize }
S 'Firmware type' { $env:firmware_type }
S 'BIOS' { Get-CimInstance Win32_BIOS | Format-List Manufacturer, SMBIOSBIOSVersion, ReleaseDate }
S 'Board' { Get-CimInstance Win32_BaseBoard | Format-List Manufacturer, Product }
S 'Virtualization' { Get-CimInstance Win32_Processor | Format-List VirtualizationFirmwareEnabled, VMMonitorModeExtensions, SecondLevelAddressTranslationExtensions; "HypervisorPresent: " + (Get-CimInstance Win32_ComputerSystem).HypervisorPresent }
S 'OS' { Get-CimInstance Win32_OperatingSystem | Format-List Caption, Version, OSArchitecture }
notepad $o
```

Скопировать файл в буфер для GitHub: `Get-Content $o -Raw | Set-Clipboard`

**Только смотреть, не коммитить:** `systeminfo` (имя ПК, IP, email). Строка внизу: *Hyper-V Requirements: Virtualization Enabled In Firmware: Yes* (RU: «Виртуализация включена во встроенном ПО: Да»). «A hypervisor has been detected» / «Обнаружена низкоуровневая оболочка» = уже включено → Yes.

### Ловушки Task 1

* Threads = NumberOfLogicalProcessors (Linux: `CPU(s)`). Hybrid Intel: P-ядро 2 потока, E-ядро 1 → i7-13700 = 8P+8E = 16 ядер, 24 потока.
* RAM: total **+ число модулей + число слотов**. Пустой слот = MemoryDevices − модули. ОС показывает чуть меньше суммы модулей (резерв iGPU/firmware).
* Disk: размер ≠ свободно. «SSD» в названии ≠ NVMe → смотри BusType. Win32_DiskDrive показывает NVMe как SCSI.
* Hyper-V/WSL2 включены → VirtualizationFirmwareEnabled может быть False → смотри HypervisorPresent.
* PS 5.1: `>` = UTF-16LE. Всегда `Out-File -Encoding utf8`.
* Байты → GiB: `/1GB`. КБ (Win32_OperatingSystem, MaxCapacityEx) → GiB: `/1MB`. 8589934592 B = 8 GiB.

### Таблица в README

|What|Value|Where I got it|
|-|-|-|
|CPU model|…|`Get-CimInstance Win32_Processor`|
|Cores / threads|… / …|same, NumberOfCores / NumberOfLogicalProcessors|
|RAM total / modules / slots|… GB / … / …|Win32_ComputerSystem / Win32_PhysicalMemory / Win32_PhysicalMemoryArray|
|RAM speed|… MT/s|Win32_PhysicalMemory Speed|
|Disk model / type / bus|…|`Get-PhysicalDisk`|
|Free space on VM volume|… GB|Win32_LogicalDisk FreeSpace|
|Firmware|UEFI / Legacy, version, date|`$env:firmware_type`, Win32_BIOS|
|Virtualization present / enabled|…|Win32_Processor, HypervisorPresent|

### Два вопроса о чужой спецификации — шаблон ответа

**«Потянет две VM?»** — по шагам, с цифрой на каждом:

1. VT-x/AMD-V present **и** enabled? Нет → 64-bit гость не стартует вообще (фикс в UEFI: Intel Virtualization Technology / SVM Mode).
2. Потоки: Σ vCPU vs **потоки** хоста; хосту оставить ≥ 2.
3. RAM: свободно = total − простой хоста (Win ~4–6 GB). Ubuntu Server 2 GB + Win11 4 GB = 6 GB. Больше → стартуют, но хост в swap.
4. Disk: свободно ≥ реально записанное на thin-диски (25 + 64 GB объявлено). HDD → медленно.
5. Вывод одной фразой + названный bottleneck.

**«Что апгрейдить первым?»** — bottleneck + можно ли вообще:

|Bottleneck|Симптом|Проверка возможности|
|-|-|-|
|RAM (для VM почти всегда №1)|всё тормозит сразу, swap|пустой слот? тот же DDR? распаяна (ноут/Apple) → нельзя|
|1 модуль RAM|половина bandwidth|второй такой же → dual channel (2×8 > 1×16)|
|HDD / мало места|медленный старт, диск полон|SSD; M.2 слот: M-key = NVMe, B+M = SATA|
|CPU|долгие задачи|socket + chipset + firmware; ноут BGA → нельзя|
|VT-x off|гость не стартует|не апгрейд, а настройка UEFI — первой|

---

## 2. Task 2 — Plan and justify

||Ubuntu|Windows|Σ обещано|Хост|Ratio / вывод|
|-|-|-|-|-|-|
|vCPU|2|2|4|__ threads|4/__ = __ : 1|
|RAM|2 GB|4 GB|6 GB|__ total − __ idle = __ free|6 / __|
|Disk (thin)|25 GB|64 GB|89 GB|__ free|реально сейчас ~__|
|Network|NAT|NAT|один vSwitch|—|видят друг друга + интернет|

* **Ratio** = обещано ÷ есть. CPU — против потоков. RAM — против **свободной** (total − idle).
* Обоснование = число от хоста: «4 GB из 16, т.к. Windows в простое держит 6, нужен второй гость».
* Не давать одному гостю все потоки (конкурирует с хостом и гипервизором → медленнее).
* Thin: растёт по записи, объявленный размер = потолок. Σ потолков > free → хост заполнится → гости write errors / pause. Удаление в госте не уменьшает файл (нужен compact).
* Snapshot `clean-install` **до** эксперимента. Snapshot ≠ backup.

**Что будет, если…**

* RAM overcommit + оба гостя работают → стартуют, потом сжатие → swap хоста → всё медленно.
* Σ vCPU > threads, все заняты → медленнее, ничего не падает; в госте растёт `st` (steal) в `top`.
* Bridged на кампусе → MAC filtering молча дропает: нет адреса, нет ошибки.
* Ping Ubuntu → Windows → режет Windows firewall → правило ICMP, не выключать firewall.
* VT-x off → гость НЕ стартует (не «медленнее», не «32-bit»).

**Сетевой режим:**

* Интернет + гости видят друг друга → VMware **NAT (VMnet8)** / VirtualBox **NAT Network** (обычный VBox NAT: каждый гость 10.0.2.15, друг друга не видят).
* Доступ из LAN к NAT-гостю → только **port forwarding** (host:2222 → guest:22).
* Изолированная лаба → **host-only** (+ второй NAT-адаптер только где нужен apt).
* Гость как узел LAN → **bridged** (дома да, кампус — нет).

**Verification (команда → ожидаю):**

```powershell
Get-CimInstance Win32_OperatingSystem | Format-List FreePhysicalMemory, TotalVirtualMemorySize, FreeVirtualMemory   # до/после старта гостей
Get-CimInstance Win32_PageFileUsage | Format-List CurrentUsage, PeakUsage   # рост = хост свапит
Get-ChildItem <VM folder> -Include *.vmdk,*.vdi -Recurse | Format-Table Name, Length   # thin < объявленного
New-NetFirewallRule -DisplayName "Allow ICMPv4 echo in" -Protocol ICMPv4 -IcmpType 8 -Direction Inbound -Action Allow
```

```bash
nproc; free -h; lsblk; df -h /            # гость видит 2 CPU / 2 GB / 25 GB
ip addr; ip route; ping -c 3 8.8.8.8; ping -c 3 <IP Windows>
```

---

## 3. Task 3 — Diagnose (транскрипт = результат)

Баллы: Method 35 · Correct result 25 (фикс **переживает reboot**) · Transcript 25 (понятно без тебя, **тупики записаны**) · Verification 15.
Прямой путь без единой ошибки = не верят, снижают.

```markdown
Symptom as reported: "<цитата>"

| # | Command (output I read) | Expected | Got | Concluded |
|---|---|---|---|---|
| 1 | df -h | / < 90% | / 61% | dead end: диск не причина |
| 2 | systemctl status app | active (running) | failed, 03:12 | упал — почему? |
| 3 | free -h | available > 500M | 80Mi, Swap 2.0G/2.0G | память+swap кончились |
| 4 | journalctl -k \| grep -i oom | запись? | 03:12 Killed process 1844 (app) | OOM killer, время = строка 2 |
| 5 | ps aux --sort=-rss \| head | app крупнейший | backup.py 1.6G | виновник backup.py, app — жертва |

## Fault — одно предложение: что и почему.
## Fix — сейчас: … / постоянно (переживёт reboot): …
## Verification — после reboot повторю <команду>, ожидаю <вывод>.
```

**Метод:** симптом дословно → слои снизу вверх **диск → память → процессы/сервисы → сеть → файлы** → гипотеза → какой вывод её проверит → вывод. Одна переменная за раз. Ищи *причину*, а не симптом. Сверяй время событий.
**Слова-маркеры в выводе:** `failed` `error` `denied` `Killed` `No such` `100%` `degraded` `[U_]` `^M` `DOWN` `Z` `<defunct>` `No space`.

### Каталог неисправностей

|Видно в выводе|Где|Причина|Постоянный фикс|
|-|-|-|-|
|`Out of memory: Killed process N (x)`|`journalctl -k`, `dmesg -T` + grep oom|RAM+swap кончились, OOM killer (max oom_score)|убрать утечку/ограничить, +RAM/swap|
|нет kernel OOM, процесс убит|`journalctl -u systemd-oomd`|systemd-oomd убил раньше|то же|
|available ≈ 0, Swap used растёт, `si/so ≠ 0`, `wa` высокий|`free -h`, `vmstat 1`|thrashing|меньше процессов/гостей, +RAM|
|`No space left on device`, `Use% 100%`|`df -h` → `du -sh /var/*`|диск полон (часто `/var/log/journal`)|`journalctl --vacuum-size=200M`, лимит логов, +диск|
|после reboot пусто в `/mnt/data`|`lsblk -f` (нет MOUNTPOINT), `cat /etc/fstab`|fstab по `/dev/sdb1`, диск стал `sdc` / нет строки|fstab по **UUID** (`blkid`), проверить `mount -a`|
|файлы «пропали» после mount|`findmnt`|писали в папку до монтирования — лежат под mountpoint|umount → перенести → mount|
|`[U_]`, `clean, degraded`|`cat /proc/mdstat`, `mdadm --detail /dev/md0`|RAID 1 потерял диск|`mdadm --manage /dev/md0 --add /dev/sdX1` → `[UU]`|
|`Active: failed` / `inactive (dead)`, `disabled`|`systemctl status x`, `journalctl -u x -n 50`|сервис упал / не в автозапуске|починить причину → `systemctl enable --now x`|
|`/bin/bash^M: bad interpreter`|`cat -A f` (`^M$`), `file f` (with CRLF)|CRLF|`sed -i 's/\r$//' f` / `dos2unix`; `.gitattributes`: `*.sh text eol=lf`|
|`#!` не работает, заголовок `﻿ID`|`xxd -l 16 f` → `ef bb bf`|UTF-8 BOM|`sed -i '1s/^\xEF\xBB\xBF//' f`|
|`[ "$x" = "Manager" ]` всегда false|`cat -A`|`\r` в последнем поле|→ LF|
|`РђР№РіРµ…`|`file`, `xxd`, `iconv -f UTF-8 -t UTF-8 f >/dev/null`|UTF-8 прочитан как CP1251|НЕ сохранять; открыть правильно / `iconv`|
|ping шлюза OK, 8.8.8.8 100% loss|`ip route` (нет `default via`)|нет default route|сейчас `ip route add default via GW`; постоянно `/etc/netplan/*.yaml` + `netplan apply`|
|`Temporary failure in name resolution`|`resolvectl status`, `/etc/resolv.conf`|DNS|nameservers в netplan|
|`state DOWN` / нет inet|`ip addr`|интерфейс выключен / DHCP не ответил (bridged + MAC filter)|netplan `dhcp4: true`; режим NAT|
|ping в одну сторону|firewall получателя|Windows блокирует ICMP|правило ICMPv4 echo|
|много `Z` / `<defunct>`|`ps -eo pid,ppid,stat,cmd`|родитель не делает `wait()`|kill не поможет → чинить/перезапустить **родителя** (PPID)|
|процессы в `D` долго|`ps`, `vmstat` (wa)|висят на дисковом I/O|смотреть диск|
|высокий `st` в top гостя|`top` → Cpu(s)|хост перегружен (steal time)|меньше vCPU суммарно|
|`Permission denied` при запуске|`ls -l` (нет x)|нет права исполнения|`chmod +x f`|
|`photo.jpg` запускается|`file`, `xxd -l 4` → `4d 5a`|это .exe (MZ)|тип = сигнатура, не расширение|
|диск 4 TB, видно ~2|`lsblk -o NAME,SIZE,PTTYPE` → `dos`|MBR (лимит 2 TiB)|GPT (стирает разделы → бэкап)|
|`VT-x is disabled in the BIOS` / `VERR_VMX_MSR_ALL_VMX_DISABLED`|ошибка гипервизора|VT-x off в firmware|UEFI → Enabled|
|все VM на паузе / write errors|free space **хоста**|thin-диски заполнили хост|освободить место, compact|
|Windows: мало памяти|`Get-WinEvent -FilterHashtable @{LogName='System'; Id=2004}`|Resource-Exhaustion-Detector 2004|как OOM|

### Временно vs переживает reboot

|До reboot|Переживает reboot|
|-|-|
|`ip route add default via X`|netplan yaml + `netplan apply`|
|`mount /dev/sdb1 /mnt/x`|`/etc/fstab` по UUID + `mount -a`|
|`systemctl start svc`|`systemctl enable svc`|
|`swapon /swapfile`|строка swap в `/etc/fstab`|
|`kill` тяжёлого процесса|убрать причину|

Verification = после reboot та же команда: `ip route` → `default via …` · `systemctl is-enabled x` → `enabled` · `findmnt /mnt/data` → есть строка · `cat /proc/mdstat` → `[UU]`.

### Как читать типичные выводы Linux

* `free -h` — смотри **available**, не free (free мало = норм, это page cache). Строка `Swap: used`.
* `df -h` — `Use%`, `Avail`, `Mounted on`.
* `lsblk` — disk/part/lvm/raid1; пустой MOUNTPOINT = не смонтировано; `lsblk -f` даёт FSTYPE + UUID.
* `vmstat 1` — `si/so` swap in/out, `wa` ожидание I/O, `st` steal.
* `top` — `%Cpu(s): … wa … st`; `S` колонка: R S D Z.
* `ip addr` — `state UP/DOWN`, `inet 192.168.x.x/24`. `ip route` — `default via <GW>`.
* `systemctl status` — `Loaded: … ; enabled/disabled` + `Active: active/failed/inactive` + последние строки лога.
* `/proc/mdstat` — `[2/2] [UU]` здорово, `[2/1] [U_]` degraded, `recovery = 42%`.
* `cat -A` — `^M$` = CRLF, `$` = LF, `M-…` = байты > 7F (не декодирует).
* `file` — `ASCII` / `UTF-8` / `UTF-8 (with BOM)` / `UTF-16 little-endian` / `ISO-8859`, `Non-ISO extended-ASCII` (= какая-то code page) / `with CRLF line terminators`. CSV на Ubuntu 24.04 → `file -e csv`.

---

## 4. Факты и числа

**Железо**

* 6C/12T = 6 ядер × 2 потока (SMT); OS видит 12 logical CPU; второй поток +15–30%.
* L1/L2/L3 = SRAM (6 транз./бит), RAM = DRAM (1T+1C). Ближе = дороже/байт. Locality.
* RAM ~100 ns · SSD ~100 µs · HDD ~10 ms. Диск ~1000× медленнее RAM.
* DDR4 ≠ DDR5 (вырез). DIMM/SO-DIMM. DDR4-3200 = PC4-25600 (×8). Разная скорость → по медленной. 2 канала: слоты A2+B2.
* ECC: 8 бит на 64; fix 1-бит, detect 2-бит; нужно модуль+CPU+плата; не быстрее, не больше. DDR5 on-die ECC ≠ ECC.
* M.2 = форма; SATA/NVMe = интерфейс. 2280 = 22×80 мм. HDD 150–250 MB/s · SATA SSD ~550 · PCIe3 x4 ~3500 · PCIe4 x4 ~7000. NVMe быстрее из-за PCIe + очередей (65535 vs 1×32 AHCI), память та же (NAND).
* Апгрейд CPU: socket + chipset → firmware → кулер/БП. LGA1151: 100/200 → 6–7 gen, 300 → 8–9. LGA1700 = 12–14. AM5 = DDR5. Ноут BGA = нельзя.
* БП +30–40% запаса. TDP = тепло для кулера. Перегрев → throttling.
* Apple Silicon: SoC, unified memory (CPU+GPU), не апгрейдится, гости arm64.
* BIOS → MBR, UEFI → GPT + Secure Boot. Boot: power → firmware → bootloader → kernel → login.

**Виртуализация**

* Type 1 = на железе (ESXi, Hyper-V, KVM, Xen); Type 2 = app на ОС (Workstation, VirtualBox). Определяет только «что под ним». Hyper-V/WSL2 on → Windows сама гость на type 1.
* VT-x/AMD-V(SVM): CPU сам ловит privileged instructions. Нужно present **и** enabled.
* Container: **нет своего ядра** (ядро хоста). Docker на Windows = скрытая Linux VM.
* Cloud vCPU ≈ 1 поток, не ядро. vCPU = поток гипервизора на хосте.
* GVA → (guest PT) → GPA → (EPT/NPT) → HPA. TLB miss в VM до 24 чтений вместо 4.
* Память кончается: lazy alloc → page sharing (KSM) → ballooning → compression → host swap. Overcommit измерять на **хосте**.
* Overcommit: CPU норм (медленнее) · RAM риск (swap) · thin disk риск (хост полон) · сеть норм.
* Диски: .vmdk VMware · .vdi VBox · .vhdx Hyper-V · .qcow2 KVM.
* Snapshot = frozen + delta (CoW); revert выкидывает delta; delete сливает. Не копия/бэкап/export. Full clone независим, linked зависит от родителя, OVA = архив для переноса.
* Guest additions: разрешение, буфер, shared folders, time sync, balloon. НЕ лицензия, НЕ CPU, НЕ интернет.

|Режим|→ интернет|гость↔гость|хост→гость|LAN→гость|
|-|-|-|-|-|
|NAT VMware|да|да|да|port fwd|
|NAT VBox|да|нет|port fwd|port fwd|
|NAT Network VBox|да|да|port fwd|port fwd|
|Bridged|если пустят MAC|да|да|да|
|Host-only|нет|да|да|нет|
|Internal|нет|да|нет|нет|

VMware NAT: GW 192.168.x.2, гости .128–.254, хост .1. VBox NAT: гость 10.0.2.15, GW 10.0.2.2. MAC: VMware 00:0C:29/00:50:56, VBox 08:00:27. Пакет режут: сеть (MAC filter) / NAT (нет правила) / firewall гостя.

**Хранение**

* Диск = ряд блоков (LBA). sda/sda1 · nvme0n1p1 · vda · md0. Имена меняются при загрузке → проверяй размер и mountpoint.
* Запись → RAM (write-back) → диск позже. «Saved» ≠ на диске. `sync`, `umount`. Проверка данных: umount → mount.
* MBR: 2 TiB (2³² × 512 B), 4 primary, 1 копия, BIOS. GPT: 128, 2 копии + checksum, UEFI. GPT обязателен: > 2 TB **или** UEFI boot. `Get-Disk` → Partition Style; `lsblk -o NAME,PTTYPE` → gpt/dos.
* Quick format = новые структуры, данные остаются. Full = нули. NTFS, ext4 (журнал), FAT32 (≤ 4 GB/файл, EFI), exFAT.
* Windows = буква на том; Linux = одно дерево от `/`. `umount` (без n); busy → `cd ~`. fstab по UUID.
* RAID 0 stripe (0 защиты) · 1 mirror · 5 −1 диск · 6 −2 · 10. 4×2 TB: R0 8 · R5 6 · R6 4 · R10 4. [UU] → [U_] → recovery → [UU].
* RAID ≠ backup (удаление, ransomware, ФС, пожар, кража — на оба диска). **3-2-1**: 3 копии, 2 носителя, 1 off-site (+1 offline, 0 ошибок restore-теста).

**Кодировки**

* 1 байт = 2 hex. 0x0A=10 · 0x41=65 · 0x7F=127 (последний ASCII) · 0x80=128 · 0xC0=192 · 0xC8=200 · 0xFF=255. `printf '%d\n' 0xFF` · PS: `0xFF`, `'{0:X2}' -f 255`.
* ASCII 0–127: 09 tab · 0A LF · 0D CR · 20 space · 2C `,` · 3B `;` · 22 `"` · 41 A · 61 a.
* UTF-8: ASCII 1 B · кириллица и казахские 2 B (D0/D1 рус, D2/D3 каз) · € и BOM 3 B · emoji 4 B. A = 41; А = U+0410 = D0 90; Ә = D3 98. UTF-16LE: A = 41 00, А = 10 04.
* Code pages (1 байт 80–FF): CP1251, CP866, KOI8-R без казахских; **RK1048, PT154** с казахскими. C0: CP1251 А · CP866 └ · KOI8-R ю. «ANSI» = системная (RU/KZ CP1251, EN CP1252).

|Видишь «Айгерим» как|Записано|Прочитано|
|-|-|-|
|`РђР№РіРµСЂРёРј`|UTF-8|CP1251|
|`Ð…Ð¹Ð³…`|UTF-8|CP1252|
|`���`|CP1251|UTF-8|
|`└щухЁшь`|CP1251|CP866|
|`юИЦЕПХЛ`|CP1251|KOI8-R|
|`?лия ?асымова`|потеря данных (Kazakh → CP1251)|—|

* Mojibake ≠ corruption (ASCII цел) ≠ нет шрифта (□) ≠ шифрование. Save → double encoding.
* BOM: EF BB BF UTF-8 · FF FE UTF-16LE · FE FF UTF-16BE. Excel dbl-click без BOM → ANSI (мусор), с BOM → OK. LibreOffice угадывает. cat OK. Скрипты ломаются на BOM. Решает **кто читает**.
* CRLF 0D 0A Windows · LF 0A Linux/mac · CR 0D old Mac. Это не кодировки.
* Signatures: PNG 89 50 4E 47 · JPEG FF D8 FF · PDF 25 50 44 46 · ZIP/docx 50 4B 03 04 · gzip 1F 8B · ELF 7F 45 4C 46 · EXE 4D 5A · script 23 21.
* PS 5.1: `>`/Out-File → UTF-16LE+BOM · Set-Content → ANSI (каз. → ?) · `-Encoding utf8` → UTF-8+BOM. PS 7: UTF-8 без BOM.
* Lab 5 цепочка: `sha256sum` → `file` + `file -e csv` → `xxd -l 16` → `iconv -f UTF-8 -t UTF-8` → цикл кандидатов → `cat -A` + `tr -cd '\r' | wc -c` + `wc -l` → `iconv` (+BOM, +sed) → verify Excel dbl-click / Calc default / cat → `sha256sum` оригинала тот же.
* PS-аналоги: `Get-FileHash` · `Format-Hex f | Select-Object -First 1` · `[Text.Encoding]::GetEncoding(1251)` + `[IO.File]::ReadAllText/WriteAllText` + `New-Object Text.UTF8Encoding($true)`.

**Процессы и память**

* Program = файл; process = экземпляр (address space, registers+PC, open files, PID/PPID/user). PCB.
* States: Running ↔ Ready; Running → Blocked (I/O) → Ready. htop S: R · S · D (диск, непрерываемо) · Z (zombie).
* fork() копия (родитель получает PID ребёнка, ребёнок 0) · exec() заменяет программу, PID тот же, не возвращается · wait() забирает exit status. `ls` = fork → exec → wait. PID 1 = systemd. Windows: CreateProcess, дерево не держится («Non-existent process»).
* Threads: свои registers+stack, общие память и файлы. Scheduler планирует потоки.
* Service/daemon = без интерактивной сессии; systemd стартует, перезапускает, journal. Windows: Service Control Manager.
* Контроль ОС: user/kernel mode · system call (trap) · timer interrupt (каждые ms) · scheduler (time slice; не cron!) · context switch. `strace -c ls`.
* Address space: code · data · heap ↓ · free · ↑ stack. Все адреса виртуальные → изоляция + swap.

|Память|htop|Process Explorer|Task Manager|
|-|-|-|-|
|Всё mapped|VIRT|Virtual Size|—|
|В RAM сейчас|RES|Working Set|Working set|
|Общее (libs)|SHR|WS Shareable|—|
|Только своё|—|Private Bytes|Commit size|
|Default «Memory»|—|—|Private working set|
|Open files|fd (`/proc/PID/fd`, lsof)|Handles|Handles|

* Расхождения: Σ RES > RAM (shared libs) · TM Memory < Working Set · handle шире fd · htop потоки строками (H).
* OOM путь: cache shrinks → swapping (si/so) → thrashing → OOM killer (max oom_score) / Windows ID 2004.

```powershell
$PID; Get-CimInstance Win32_Process -Filter "ProcessId=$PID" | Select-Object ProcessId, ParentProcessId, Name
Get-Process -Id $PID | Select-Object Id, WorkingSet64, PrivateMemorySize64, VirtualMemorySize64, HandleCount
```

```bash
echo $$; ps -o pid,ppid,user,cmd -p $$; pstree -p | head -30
grep -E 'Name|PPid|VmSize|VmRSS|Threads' /proc/$PID/status; ls -l /proc/$PID/fd | wc -l
free -h; swapon --show; vmstat 1; journalctl -k | grep -iE 'out of memory|oom|killed process'
```

---

## 5. Шаблон README любой лабы

```markdown
# Lab N — <title>
Machine: …  Date: …
## What I did        (команды в code blocks, не проза)
## Result            (таблица / число / вывод)
## What did not work the first time   (обязательно ≥ 1)
## Evidence          - [evidence/x.txt](evidence/x.txt) — что доказывает
```

Правила: diagnose first · оригинал не трогать (checksum) · точные имена (CP1251, CRLF, OOM) · у числа — команда · текст > скриншот · одна переменная за раз · доказать фикс.
