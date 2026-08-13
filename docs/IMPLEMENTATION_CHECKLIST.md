# ASTH Raspberry Pi 5 MVP Implementation Checklist

This document translates the approved [ASTH Raspberry Pi 5 Deployment Plan](DEPLOYMENT_PLAN.md) into small, independently verifiable implementation phases and records the deployment snapshot updated on **13 August 2026**. It remains an execution checklist only. Checked items are confirmed by the supplied validation record; unchecked items remain follow-up work, deferred or blocked. Physical recovery, the operational hub, manual application rollback/restoration and GPU/display-stack recovery are **VERIFIED**. Learning content, final hardware, kiosk, migration and MVP acceptance remain incomplete; database backup/restore is **DEFERRED** until a database-backed module exists.

## Scope and operating rules

- Confirmed current hardware: Raspberry Pi 5 with 2 GB RAM, booting Raspberry Pi OS from 32 GB microSD storage.
- Target operating system: Raspberry Pi OS, preferably 64-bit.
- Deployment boundary: trusted office LAN, offline portable hotspot, or online portable mode through the controlled `PHONE-UPLINK`; do not expose ASTH or SSH to the upstream internet.
- Runtime: Nginx reverse proxy to FastAPI served by **one** Uvicorn worker bound to `127.0.0.1:8000`.
- Data store: SQLite with one application writer process.
- Service supervision: systemd only.
- Resource policy: active cooling, bounded storage use, and minimal background services.
- Docker and other container orchestration are deferred beyond the initial MVP.
- Replace every angle-bracket placeholder with a value recorded in the Decision Log before running a command that uses it.
- Commands marked **sudo required** change host state. Review the resolved paths and values before running them.
- Capture evidence without passwords, private keys, session cookies, API keys, or other secret values.
- Complete phases in order. A phase marked Blocked must not be bypassed unless the technical lead records and approves the reason.

## Placeholder convention

Examples such as `<admin-user>`, `<asth-hostname>`, `<pi-lan-ip>`, `<lan-cidr>`, `<release-id>`, and `<backup-mount>` are labels, not literal command arguments. Never paste a command until all placeholders in that command have been resolved.

## Decision Log

Do not record passwords, private keys, tokens or secret values in this table.

| Decision | Confirmed value or current state | Status | Date | Follow-up |
|---|---|---|---|---|
| Named administrator account | `asthadmin` | Confirmed | 25 July 2026 | Establish tested SSH key access before password-login removal. |
| Physical recovery access | HDMI display, USB keyboard, local `asthadmin` login, boot-recovery password recovery and normal reboot | Confirmed complete | 30 July 2026 | Keep this path available until final assembly and revalidate afterward. |
| Named administrator sudo | `SUDO_OK` | Confirmed | 30 July 2026 | None. |
| ASTH application service | `asth`; runtime account not recorded | Verified active | 13 August 2026 | Rollback and restoration restarts succeeded; verify installed unit metadata separately. |
| Pi hostname | `asth-pi` | Confirmed | 25 July 2026 | None. |
| Current LAN address | `192.168.100.187` observed | Confirmed current value | 26 July 2026 | Do not treat as permanent until reservation/fixed addressing is confirmed. |
| Gateway | `192.168.100.1` | Confirmed | 25 July 2026 | None. |
| LAN and SSH administration subnet | `192.168.100.0/24` | Confirmed | 25 July 2026 | Revalidate if the deployment network changes. |
| Primary network paths | `eth0` current internet uplink and built-in `wlan0` hotspot active simultaneously | Verified | 13 August 2026 | Ethernet negotiated at 1000 Mbps full-duplex; fixed-IP method remains pending. |
| Current portable hotspot | `ASTH-PORTABLE` profile: access point, 5 GHz (`a`), channel 36, IPv4 shared; `iw` runtime observation: 5180 MHz, 20 MHz width | Verified | 13 August 2026 | Malaysia indoor regulatory allowance verified; password remains excluded from Git. |
| Historical hotspot baseline | `ASTH-PORTABLE`, access point, 2.4 GHz (`bg`), channel 6, 20 MHz width | Historical verified state | 25 July 2026 | Replaced on 13 August; preserved for rollback as `ASTH-PORTABLE-2G-BACKUP` with autoconnect disabled. |
| Portable gateway and URL | `10.42.0.1/24`; `http://10.42.0.1` | Confirmed | 25 July 2026 | Same local URL in offline and online portable modes. |
| Portable internet uplink | ALFA AWUS036NHV on `wlan1`, `rtl8xxxu`, profile `PHONE-UPLINK` | Historical verified test | 25 July 2026 | `wlan1` was disconnected and not tested on 13 August; credentials remain only in local NetworkManager. |
| Historical wlan1 route | `10.13.68.119/24`; `default via 10.13.68.67 dev wlan1` | Historical verified test | 25 July 2026 | Not the current route; future DHCP values may differ. |
| Current internet route | `1.1.1.1 via 192.168.100.1 dev eth0 src 192.168.100.187` | Verified | 13 August 2026 | Alfa was not involved in this test. |
| Portable SSH boundary | `10.42.0.0/24` to TCP port 22 on `wlan0` | Confirmed | 25 July 2026 | `ssh asthadmin@10.42.0.1` verified. |
| Router or DHCP owner | Not assigned | Pending decision | 25 July 2026 | Confirm network owner. |
| Time zone | `Asia/Kuala_Lumpur` | Confirmed | 25 July 2026 | None. |
| Application version and repository state | v0.4.0 deployed; repository not synchronised | Partial | 26 July 2026 | Compare and commit the deployed source later. |
| ASTH LAN URL | `http://192.168.100.187/` while the current lease remains valid | Conditional | 25 July 2026 | Update after fixed addressing and hostname resolution are approved. |
| Health and live status | `/health`; `/api/hub-status` | Confirmed | 26 July 2026 | Treat live status as an operational dependency. |
| Deployed routes | `/`, `/learn/`, `/health`, `/api/hub-status` | Confirmed | 26 July 2026 | `/` is the hub page; `/learn/` remains a placeholder Learning Hub. |
| Deployed application source | `/opt/asth/app/main.py`, v0.4.0 | Confirmed on Pi | 26 July 2026 | Commit/synchronise this source into the repository later. |
| SQLite location | `/var/lib/asth/db` exists and is empty; no database file/reference exists in the current application | Deferred | 13 August 2026 | Resume backup/restore work after a database-backed module defines the live database. |
| Maximum request body | Not defined | Pending decision | 25 July 2026 | Set from real application requirements. |
| Environment file | `/etc/asth/asth.env`, previously confirmed `root:root` mode `0600`; no `KEY=value` entries | Partial | 13 August 2026 | Define required variable names when a module needs runtime configuration; never expose secret values. |
| Persistent SSD mount | `/dev/sda2` at `/mnt/rog`; UUID `8E5AAE985AAE7C99`; NTFS via `ntfs3` | Confirmed complete | 30 July 2026 | Remained mounted after the recovery reboot; existing data preserved. |
| ASTH SSD namespace | `/mnt/rog/ASTH` with NAS, app-data, database, backups, logs and staging directories | Confirmed complete | 25 July 2026 | All directories owned by `asthadmin`; do not modify unrelated SSD contents. |
| Manual backup destination | `/mnt/rog/ASTH_BACKUP` | Confirmed preserved | 25 July 2026 | Production schedule, retention and alerting remain pending. |
| Configuration snapshot | `/mnt/rog/ASTH_BACKUP/config-snapshot` | Confirmed preserved | 25 July 2026 | Existing snapshot remained available after reboot. |
| Basic Samba NAS | `ASTH-Public`, `ASTH-Staff`, `ASTH-Uploads` read/write; `ROG-Drive` read-only | Confirmed complete | 30 July 2026 | `smbd` remained active after recovery reboot; Windows read/write and read-only denial were previously verified. |
| Uptime Kuma | Redirect followed by HTTP 200 | Confirmed | 30 July 2026 | Advanced monitoring/alerting acceptance is not implied. |
| Cockpit console | HTTPS port 9090 on office LAN and `ASTH-PORTABLE` | Confirmed complete | 30 July 2026 | TCP 9090 listening and HTTP 200 verified; self-signed certificate warning expected. |
| Post-recovery service state | Zero failed units; ASTH health `healthy`/`running` | Confirmed | 30 July 2026 | Recheck after future maintenance. |
| Manual application rollback | v0.4.0 → v0.3.0 → v0.4.0; both restarts and HTTP 200 healthy/version checks passed | Verified | 13 August 2026 | Revalidate if the deployment layout changes. |
| GPU/display stack | `dtoverlay=vc4-kms-v3d` enabled; DRI nodes and `vc4`/`v3d` present; `rp1-test.service` active | Verified | 13 August 2026 | This does not imply LCD installation. |
| LCD | MHS35 not installed; LCD-show cloned previously; `MHS35-show` not run during recovery | Pending | 13 August 2026 | Install driver only with compatible LCD/casing hardware. |
| NVMe | Controller/HAT has not arrived; system remains on 32 GB microSD | Pending | 13 August 2026 | Detect and test after arrival before migration. |
| Backup retention and schedule | Not established | Pending decision | 25 July 2026 | Define production schedule, retention and alerting. |
| System owner | Not assigned | Pending decision | 25 July 2026 | Confirm accountable owner. |
| Technical owner | Not assigned | Pending decision | 25 July 2026 | Confirm technical owner. |
| Backup owner | Not assigned | Pending decision | 25 July 2026 | Confirm backup and restore-test owner. |
| Maintenance window | Not assigned | Pending decision | 25 July 2026 | Confirm routine and emergency windows. |
| MVP acceptance approver | Not assigned | Pending decision | 25 July 2026 | Confirm before final application acceptance. |

## Implementation Progress

Status as of **13 August 2026**:

| Not Started | In Progress | Deferred | Blocked | Complete |
|---:|---:|---:|---:|---:|
| 0 | 13 | 2 | 1 | 6 |

| Phase | Implementation phase | State | Evidence or reason |
|---:|---|---|---|
| 1 | Pre-deployment verification | In Progress | Physical recovery is complete; technical/operational owners and maintenance window remain unconfirmed. |
| 2 | Raspberry Pi physical and thermal checks | In Progress | Casing, NVMe and LCD are pending; repeat power/cooling/thermal checks after final assembly. |
| 3 | Raspberry Pi OS and architecture verification | Complete | Debian 13, arm64/aarch64, kernel and time zone recorded. |
| 4 | Hostname and network configuration | In Progress | Portable offline/online router modes are complete; Ethernet fixed-IP method remains pending. |
| 5 | User account and SSH preparation | In Progress | Local `asthadmin` login, password recovery and `sudo` pass; key login is not yet established and password login remains enabled. |
| 6 | System update and essential package preparation | Complete | Validated runtime stack and no failed services. |
| 7 | ASTH directories and ownership | In Progress | Required paths exist; full ownership/mode inventory was not supplied. |
| 8 | Python virtual environment preparation | In Progress | Runtime versions work; virtual-environment path, pinned dependency inventory and `pip check` evidence were not supplied. |
| 9 | FastAPI v0.4.0 application readiness | Complete | Syntax check, service restart and visual landing-page validation passed; `/learn/` content remains partial. |
| 10 | Uvicorn local service validation | Complete | One worker bound only to `127.0.0.1:8000`. |
| 11 | systemd service preparation | Complete | `asth.service` enabled and active. |
| 12 | Nginx reverse proxy preparation | Complete | Nginx enabled/active on port 80; port 8000 not LAN-exposed. |
| 13 | SQLite directory and permissions | Deferred | Directory exists but is empty; the current application has no database file or reference. |
| 14 | Environment variables and secrets | In Progress | File metadata was previously confirmed, but the file has no `KEY=value` configuration. |
| 15 | Logging and log rotation | In Progress | `/var/log/asth` exists; production retention and rotation evidence remain pending. |
| 16 | Backup destination and recovery test | Deferred | Off-device storage evidence exists; database backup/restore awaits a database-backed module and has no pass/fail result. |
| 17 | Basic security hardening | In Progress | UFW/SSH/rpcbind controls pass; SSH key cutover remains pending. |
| 18 | Resource and thermal monitoring | In Progress | Baseline resource/thermal values pass; representative sustained multi-device load evidence remains pending. |
| 19 | End-to-end local-network validation | In Progress | Landing page and live status are confirmed; populated learning and participant/trainer workflows remain pending. |
| 20 | Rollback readiness | In Progress | Manual application-file rollback/restoration is verified; release-layout and database-coupled recovery remain outstanding or deferred. |
| 21 | Documentation and handover | In Progress | Deployment documents are updated; system custodian, maintenance window and final handover remain unconfirmed. |
| 22 | Final MVP acceptance checklist | Blocked | Operational hub and application rollback are verified, but final hardware, content, deferred database recovery, source sync and acceptance remain outstanding. |

### Confirmed v0.4.0 hub deployment

- [x] Raspberry Pi 5 with 2 GB RAM boots and runs from the 32 GB microSD card.
- [x] HDMI display, USB keyboard, local `asthadmin` login, boot-recovery password recovery, `sudo` (`SUDO_OK`) and normal reboot passed.
- [x] ASTH portable network is operational; `192.168.100.187` is the current observed Pi address.
- [x] `/opt/asth/app/main.py` passed `python3 -m py_compile`.
- [x] `sudo systemctl restart asth` completed successfully.
- [x] The live `/` landing page was visually confirmed with DVS/ASTH logos, live metrics, graph and supporting-service links.
- [x] `/learn/` exists separately without a network graph and contains placeholder learning sections.
- [x] `/health` remains available and `/api/hub-status` is an operational live-data dependency.
- [x] Uptime Kuma and Cockpit are available as separately linked services.
- [x] Zero failed units, healthy/running ASTH health, persistent `/mnt/rog`, active `smbd`, Uptime Kuma HTTP 200 after redirect and Cockpit port 9090/HTTP 200 were verified after recovery.
- [x] A phone on `ASTH-PORTABLE` reached ASTH health and internet forwarding through `eth0` passed.
- [x] Migrated the `ASTH-PORTABLE` profile to 5 GHz band `a`, channel 36; reconnected two clients and observed through `iw` that the runtime radio used 5180 MHz with 20 MHz width before and after reboot.
- [x] Recorded one practical result of 25 ms ping, 48.9 Mbps download and 35.8 Mbps upload without treating it as guaranteed throughput.
- [x] Local application backups exist at `/opt/asth/app/main.py.backup-20260726` and `/opt/asth/app/main.py.backup-clay-service-hub-20260726`.
- [x] Manual rollback to v0.3.0 and restoration to v0.4.0 passed SHA-256, service restart, HTTP 200, health and version checks.
- [x] KMS/DRI recovery produced the expected devices and modules; `rp1-test.service` and `asth.service` were active with zero failed units.
- [ ] Complete the compatible casing/LCD assembly and install the NVMe controller/HAT and SSD after arrival.
- [ ] Validate final power, cooling, temperature, NVMe and kiosk startup.
- [ ] Complete database backup/restore after a database-backed module exists; application rollback is verified.
- [ ] Populate Learning Hub content and move large content to NVMe when available.
- [ ] Synchronise and commit the deployed v0.4.0 source into this repository later.

### Completed storage and administration deployments

- [x] Persistent SSD mount by UUID at `/mnt/rog`, with `mnt-rog.mount` active after full reboot.
- [x] Existing SSD data and `ASTH_BACKUP` preserved; no formatting or repartitioning performed.
- [x] ASTH storage namespace and directory ownership created under `/mnt/rog/ASTH`.
- [x] Basic Samba NAS deployed with three authenticated read/write ASTH shares and intentionally read-only `ROG-Drive`; SMB1 disabled.
- [x] Cockpit deployed with Storage, Networking and administration components; socket and TCP 9090 verified after reboot.
- [x] UFW restricted Samba and Cockpit to `192.168.100.0/24` and `10.42.0.0/24` on `wlan0`.

---

## Phase 1 — Pre-deployment verification
**Objective:** Confirm that the approved baseline, responsible people, recovery access, and required inputs exist before changing the Pi.

**Prerequisites:** Physical access to the Pi; access to the current documentation; an approved maintenance window; permission to administer the device.

**Current state:** **In Progress** — Hardware, host, network, services, backup locations and physical recovery access are recorded. System/technical/backup owners, maintenance window and acceptance approver remain unconfirmed.

1. [x] Read `docs/DEPLOYMENT_PLAN.md` and record its verified Git reference: `77b81bb6b1d57cac0902162cd449b9c7ce37f4d7 | 2026-07-25 | docs: record Raspberry Pi infrastructure deployment status`.
2. [x] Confirm the Pi has 2 GB RAM and the current microSD system storage is 32 GB.
3. [x] Confirm the deployment remains LAN-only and Docker remains deferred.
4. [ ] Assign the technical lead, network owner, recovery operator, and acceptance approver.
5. [x] Confirm HDMI display and USB keyboard local recovery access.
5a. [x] Confirm local `asthadmin` login, boot-recovery password recovery, `sudo` (`SUDO_OK`) and normal reboot.
6. [x] Record the current hostname, IP addresses, route, disk use, and memory before changes.
7. [x] Confirm an off-device location is available for initial configuration records and backups.

**Safe verification commands:**

```bash
cat /proc/device-tree/model
grep MemTotal /proc/meminfo
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
hostnamectl
ip -brief address
ip route
df -h /
```

**Expected result:** Hardware and storage match the baseline; named owners and local recovery access are recorded; the current host/network state is captured.

**Stop condition:** Stop if the device is not the confirmed Pi, RAM/storage differs materially, permission is missing, the root filesystem is unhealthy or nearly full, or no local recovery path exists.

**Evidence to record:** Pi model output, memory output, block-device summary, disk usage, current hostname/IP, maintenance approval, owner names, and evidence storage location.

## Phase 2 — Raspberry Pi physical and thermal checks

**Objective:** Establish stable power, active cooling, airflow, and an acceptable idle thermal state.

**Prerequisites:** Phase 1 complete; Pi safely shut down before fitting or reseating hardware.

**Current state:** **In Progress** — Earlier cooling/thermal evidence exists, but casing, NVMe and LCD are pending. Power, cooling and temperature must be revalidated after final assembly.

1. [ ] Verify a suitable USB-C power supply is identified; prefer a quality 5V/5A supply.
2. [ ] Inspect the microSD seating, case ventilation, cables, and strain relief.
3. [x] Confirm an active cooler or compatible fan is installed and operating.
4. [ ] Place the Pi where vents are unobstructed and accidental disconnection is unlikely.
5. [x] Boot the Pi and allow it to idle for five minutes.
6. [x] Record temperature and throttling state at idle.
7. [ ] Confirm the kernel reports no repeated undervoltage, storage, or thermal warnings.

**Safe verification commands:**

```bash
vcgencmd measure_temp
vcgencmd get_throttled
dmesg --level=err,warn
```

`dmesg` may require **sudo** on some Raspberry Pi OS installations:

```bash
sudo dmesg --level=err,warn
```

**Expected result:** Cooling is running, temperature is stable, `get_throttled` reports `0x0` for a clean current/history state, and no recurring power or storage errors appear.

**Stop condition:** Stop if the fan does not operate, temperature rises continuously at idle, throttling/undervoltage is reported, the power supply is unsuitable, or storage errors appear.

**Evidence to record:** Power-supply rating, cooler type, placement photo, idle temperature, throttling output, and relevant warning output.

## Phase 3 — Raspberry Pi OS and architecture verification

**Objective:** Verify a supported Raspberry Pi OS installation, 64-bit architecture, correct clock settings, and adequate free space.

**Prerequisites:** Phase 2 complete; administrative access available.

**Current state:** **Complete** — Debian GNU/Linux 13 (Trixie), arm64/aarch64, kernel `6.18.34+rpt-rpi-2712`, time zone `Asia/Kuala_Lumpur`, and about 26% root-disk use are recorded.

1. [x] Record the Raspberry Pi OS release and kernel.
2. [x] Verify the userspace architecture is `aarch64` or otherwise obtain explicit approval before continuing.
3. [x] Confirm the system clock, time zone, and synchronization state.
4. [x] Confirm the root filesystem is mounted normally and has at least 20% free space.
5. [x] Record active swap; do not enlarge it without a separate storage-wear review.
6. [x] Confirm the OS installation is intended to be retained rather than re-imaged.

**Safe verification commands:**

```bash
cat /etc/os-release
uname -a
dpkg --print-architecture
timedatectl
findmnt /
df -h /
free -h
swapon --show
```

**Expected result:** Raspberry Pi OS is identified, architecture is 64-bit, time is correct or synchronizing, and sufficient disk/RAM headroom exists.

**Stop condition:** Stop for an unsupported/unknown OS, 32-bit architecture without approval, incorrect time that cannot synchronize, filesystem errors/read-only state, or less than 20% free storage.

**Evidence to record:** OS release, kernel, architecture, time zone, time-sync status, filesystem type, free-space percentage, and swap summary.

## Phase 4 — Hostname and network configuration

**Objective:** Give the Pi a unique recorded hostname and stable LAN address without exposing it to the internet.

**Prerequisites:** Phase 3 complete; `<asth-hostname>`, `<pi-lan-ip>`, `<lan-cidr>`, and `<network-interface>` confirmed with the network owner.

**Current state:** **In Progress** — `ASTH-PORTABLE` on `wlan0` is complete on 5 GHz channel 36 for offline use and current Ethernet-backed operation. On 13 August, `eth0` supplied the route; `wlan1` was disconnected. The separate 25 July test verified `PHONE-UPLINK` with Ethernet removed, but portable-mode uplink revalidation after the hotspot migration remains pending. Ethernet fixed-IP work also remains pending.

**Portable hotspot deployment:** **Complete**

1. [x] Configure connection/SSID `ASTH-PORTABLE` on built-in interface `wlan0` in access-point mode.
2. [x] Historically set 2.4 GHz (`bg`), channel 6, WPA-PSK and IPv4 shared mode without recording the password.
3. [x] Confirm gateway `10.42.0.1/24`, autoconnect enabled and autoconnect priority 100.
4. [x] Confirm Nginx port 80 is accessible through `wlan0` at `http://10.42.0.1`.
5. [x] Confirm DHCP issued addresses to a phone and laptop.
6. [x] Confirm DHCP UDP 67 and DNS TCP/UDP 53 are allowed through UFW on `wlan0`.
7. [x] Restrict SSH on `wlan0` to source subnet `10.42.0.0/24` and TCP port 22; verify `ssh asthadmin@10.42.0.1`.
8. [x] Confirm Ethernet and the portable hotspot operate simultaneously.
9. [x] Confirm `ASTH-PORTABLE` returns automatically after a full Raspberry Pi reboot.
10. [x] Confirm the v0.4.0 landing page loads and displays the verified live hub interface.
11. [x] Verify online portable mode through `PHONE-UPLINK` on `wlan1`, including forwarded internet with Ethernet removed.
12. [x] Verify a phone can reach ASTH health through `ASTH-PORTABLE` and receive internet forwarding through `eth0`.
13. [x] Clone the historical configuration as `ASTH-PORTABLE-2G-BACKUP` with autoconnect disabled and no credential recorded.
14. [x] Change the active NetworkManager profile to 5 GHz band `a` and channel 36, then confirm two clients reconnect.
15. [x] Use `iw` to observe AP mode on channel 36 at 5180 MHz with 20 MHz runtime width; reboot and confirm the same runtime observation, zero failed units and healthy ASTH v0.4.0.
16. [ ] Revalidate the Alfa `PHONE-UPLINK` path with Ethernet removed after the 5 GHz migration.

**Portable operating steps:**

1. Power on the Raspberry Pi and wait for startup.
2. Connect the participant device to Wi-Fi network `ASTH-PORTABLE` using the separately managed credential.
3. Open `http://10.42.0.1`.

“Connected without internet” is expected in offline portable mode. The current verified uplink is Ethernet on `eth0`. The 25 July test showed `PHONE-UPLINK` on `wlan1` could provide internet while retaining the same local ASTH URL, but that path was disconnected and not retested on 13 August.

**Safe hotspot verification commands:**

```bash
nmcli connection show --active
nmcli device status
nmcli -f connection.id,connection.interface-name,connection.autoconnect,connection.autoconnect-priority,802-11-wireless.mode,802-11-wireless.band,802-11-wireless.channel,802-11-wireless-security.key-mgmt,ipv4.method connection show ASTH-PORTABLE
ip -brief address show wlan0
iw dev wlan0 info
curl --fail --silent --show-error http://10.42.0.1
ip route show default
```

The general hotspot check above does not require Alfa. On 13 August 2026, `wlan1` was present but disconnected and was not tested as the active uplink. Run the following only when the Alfa adapter is installed, deliberate portable wireless-uplink testing is in scope, and `PHONE-UPLINK` has been intentionally activated:

```bash
ip -brief address show wlan1
ip route get 1.1.1.1
ping -I wlan1 -c 4 1.1.1.1
```

From an `ASTH-PORTABLE` client:

```bash
ssh asthadmin@10.42.0.1
```

UFW verification — **sudo required, read-only**:

```bash
sudo ufw status verbose
```
1. [ ] Check that the proposed hostname is unique on the deployment LAN.
2. [x] Record the current network configuration before making changes.
3. [x] Set the confirmed hostname using the supported Raspberry Pi OS mechanism.
4. [ ] Create a DHCP reservation on the router for the Pi rather than hard-coding an address where practical.
5. [x] Reconnect or reboot during the maintenance window.
6. [ ] Verify the reserved IP, default route, DNS behavior, and hostname resolution.
7. [ ] Confirm no router port forwarding exposes ports 22, 80, 443, or 8000.
8. [x] Test reachability from one intended participant device.

**Safe verification commands:**

```bash
hostnamectl
ip -brief address show <network-interface>
ip route
getent hosts <asth-hostname>
ping -c 4 <pi-lan-ip>
```

Hostname change — **sudo required**:

```bash
sudo hostnamectl set-hostname <asth-hostname>
```

**Expected result:** The hostname and reserved address match the Decision Log, resolve on the intended LAN where supported, and are unreachable from unapproved networks.

**Stop condition:** Stop on address conflict, loss of local/SSH access, incorrect subnet/gateway, unresolved ownership of router changes, or any internet-facing port forwarding.

**Evidence to record:** Hostname, MAC address, reserved IP, subnet, interface, router reservation screenshot, resolution output, participant-device ping result, and port-forwarding review.

## Phase 5 — User account and SSH preparation

**Objective:** Establish a named administrator with tested key-based SSH access and a retained local recovery path.

**Prerequisites:** Phase 4 complete; `<admin-user>` confirmed; administrator public key available; local console access working.

**Current state:** **In Progress** — Local `asthadmin` login, boot-recovery password recovery, approved `sudo` and physical console recovery pass. SSH and public-key support are present, but password authentication remains temporarily enabled until key login is established and tested.

1. [ ] List current human and system accounts and identify unused defaults for later review.
2. [x] Confirm `<admin-user>` is a named, accountable account rather than a shared login.
3. [x] Create the account only if it does not already exist.
4. [ ] Grant only the administrative group membership required by Raspberry Pi OS.
5. [ ] Install the administrator's public key with correct ownership and modes.
6. [ ] Open a second SSH session using the key and keep the first session open.
7. [x] Verify approved `sudo` access from the named account with `SUDO_OK`.
8. [x] Confirm local HDMI/USB-keyboard console recovery and normal reboot work before later disabling password SSH.

**Safe verification commands:**

```bash
getent passwd <admin-user>
id <admin-user>
sshd -T | grep -E '^(permitrootlogin|passwordauthentication|pubkeyauthentication) '
```

Account creation and group change — **sudo required**:

```bash
sudo adduser <admin-user>
sudo usermod -aG sudo <admin-user>
```

**Expected result:** A named administrator can authenticate with an SSH key in a second session, use approved `sudo`, and recover through the local console.

**Stop condition:** Stop before changing SSH authentication if key login, `sudo`, or local recovery is unverified. Stop if the proposed username conflicts with an existing account.

**Evidence to record:** Username, `id` output, public-key fingerprint only, successful second-session test, `sudo` test, and local recovery test. Do not record private keys or passwords.

## Phase 6 — System update and essential package preparation

**Objective:** Patch Raspberry Pi OS and install only the packages required by the approved deployment plan.

**Prerequisites:** Phase 5 complete; network access for maintenance; backup/configuration record available; maintenance window active.

**Current state:** **Complete** — The validated minimal stack is installed and active, with no failed services.

1. [ ] Record currently upgradable packages.
2. [ ] Refresh package metadata.
3. [ ] Apply approved OS updates.
4. [ ] Reboot if required, then recheck network, temperature, throttling, disk, and time.
5. [x] Confirm the exact essential package list: Python 3, `venv`, `pip`, Nginx, SQLite CLI, Git if release retrieval requires it, and the chosen firewall tool.
6. [x] Install only missing approved packages.
7. [x] Record installed versions and enabled services.
8. [x] Confirm Docker, database servers, desktop extras, and heavy monitoring agents were not added for the MVP.

**Safe verification commands:**

```bash
apt list --upgradable
python3 --version
nginx -v
sqlite3 --version
systemctl --type=service --state=running
```

Package operations — **sudo required**:

```bash
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-venv python3-pip nginx sqlite3
```

**Expected result:** The OS is patched, required commands are available, and no unapproved service puts unnecessary pressure on the 2 GB RAM footprint.

**Stop condition:** Stop on package errors, dependency conflicts, insufficient storage, failed reboot, lost network access, new power/thermal warnings, or an unapproved package/service requirement.

**Evidence to record:** Update transcript, package/version list, reboot time if used, post-update health outputs, running-service list, and free disk space.

## Phase 7 — ASTH directories and ownership

**Objective:** Prepare the approved immutable-release and mutable-data layout with least-privilege ownership.

**Prerequisites:** Phase 6 complete; service account name and `<release-id>` confirmed; directory design reviewed against `docs/DEPLOYMENT_PLAN.md`.

**Current state:** **In Progress** — `/opt/asth`, `/var/lib/asth`, `/var/lib/asth/db`, `/var/log/asth` and `/etc/asth/asth.env` exist. A complete ownership/mode inventory for application and data paths remains required.

1. [ ] Confirm the `asth` service account does not already represent a different purpose.
2. [ ] Create a locked, non-interactive system service account if absent.
3. [x] Create `/opt/asth/releases/<release-id>` for the prepared release.
4. [x] Create `/var/lib/asth/db`, approved mutable content paths, and `/var/lib/asth/backup-staging`.
5. [x] Reserve `/etc/asth` for later protected configuration.
6. [ ] Apply `root:asth` ownership to release/configuration paths and `asth:asth` to mutable data paths.
7. [ ] Create `/opt/asth/current` as an initial symlink only if it does not already exist, pointing to the verified release.
8. [ ] Verify the service account cannot modify release files.
9. [ ] Record permissions with numeric modes.

**Safe verification commands:**

```bash
getent passwd asth
namei -l /opt/asth/releases/<release-id>
namei -l /var/lib/asth/db
stat -c '%U:%G %a %n' /opt/asth /var/lib/asth /var/lib/asth/db /etc/asth
readlink -f /opt/asth/current
```

Creation and ownership changes — **sudo required**:

```bash
sudo adduser --system --group --home /var/lib/asth --no-create-home asth
sudo install -d -o root -g asth -m 0750 /opt/asth /opt/asth/releases /opt/asth/releases/<release-id> /etc/asth
sudo install -d -o asth -g asth -m 0750 /var/lib/asth /var/lib/asth/db /var/lib/asth/backup-staging
sudo ln -s /opt/asth/releases/<release-id> /opt/asth/current
```

The `ln -s` command deliberately omits `-f`; it must fail rather than replace an existing `current` link. Inspect an existing link and follow the rollback procedure before changing it.

**Expected result:** Release/configuration paths are not application-writable; mutable data paths are writable only by the service account and authorized administrators; `current` resolves to the verified release.

**Stop condition:** Stop if any placeholder is unresolved, a target path contains unrelated data, `current` already exists with an unexpected target, ownership differs from the plan, or the service account gains an interactive shell or excessive privileges.

**Evidence to record:** Service-account entry, resolved release path, `namei`/`stat` output, owner/group/modes, and release identifier.

## Phase 8 — Python virtual environment preparation

**Objective:** Build an isolated, reproducible Python environment inside the exact release directory.

**Prerequisites:** Phase 7 complete; reviewed release files and pinned production `requirements.txt` present; exact release/commit recorded.

**Current state:** **In Progress** — Python 3.13.5, FastAPI 0.140.0 and Uvicorn 0.51.0 run successfully. The virtual-environment path, pinned dependency inventory and `pip check` evidence were not supplied.

1. [ ] Verify release files identify the intended Git commit or package version.
2. [ ] Confirm production dependencies are pinned and exclude development-only packages.
3. [ ] Check available disk space before dependency installation.
4. [ ] Create `.venv` inside `/opt/asth/releases/<release-id>`.
5. [ ] Install dependencies only into that virtual environment; do not use global `sudo pip`.
6. [ ] Record dependency installation output and final package inventory.
7. [x] Verify the virtual-environment interpreter imports FastAPI, Uvicorn, and the application package.
8. [ ] Confirm release files remain non-writable by `asth` after preparation.

**Safe verification commands:**

```bash
df -h /
/opt/asth/releases/<release-id>/.venv/bin/python --version
/opt/asth/releases/<release-id>/.venv/bin/python -m pip check
/opt/asth/releases/<release-id>/.venv/bin/python -m pip freeze
```

Preparation commands, run from the reviewed release directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --requirement requirements.txt
```

**Expected result:** A self-contained virtual environment passes `pip check`, imports the application, and is tied to a recorded release.

**Stop condition:** Stop for unpinned dependencies, failed builds/imports, unexpected native compilation, insufficient storage, dependency conflicts, or any instruction to use global `sudo pip`.

**Evidence to record:** Release ID/commit, Python/pip versions, requirements checksum, installation transcript, `pip check`, package inventory, and disk usage.

## Phase 9 — FastAPI v0.4.0 application readiness

**Objective:** Verify the actual deployed application without claiming repository synchronisation or completed learning content.

**Prerequisites:** Administrative access to the Pi and a maintenance window for restart actions.

**Current state:** **Complete for the deployed hub shell** — `/opt/asth/app/main.py` passed syntax validation, `asth` restarted successfully and the landing page was visually confirmed. `/learn/` remains a placeholder Learning Hub.

1. [x] Confirm the deployed version shown by the FastAPI application is v0.4.0.
2. [x] Confirm the main deployed file is `/opt/asth/app/main.py`.
3. [x] Confirm DVS and ASTH logo assets are under `/var/www/asth-hub/assets/`.
4. [x] Run `python3 -m py_compile /opt/asth/app/main.py` successfully.
5. [x] Restart with `sudo systemctl restart asth` successfully.
6. [x] Visually confirm `/` with hub status, device count, current rates, totals, uptime, Wi-Fi information, graph and service links.
7. [x] Confirm `/learn/` is separate, has no network graph and contains the three placeholder sections.
8. [x] Confirm `/health` remains available and `/api/hub-status` supplies live status data.
9. [ ] Populate approved Learning Hub modules, PDFs, videos and interactive content.
10. [ ] Compare and commit the deployed v0.4.0 source into this repository later.

**Safe validation command:**

```bash
python3 -m py_compile /opt/asth/app/main.py
```

Restart — **sudo required; brief interruption**:

```bash
sudo systemctl restart asth
```

**Expected result:** Syntax validation and restart pass, operational routes recover and the live page matches the confirmed architecture.

**Stop condition:** Stop if syntax validation fails, the service does not recover, `/api/hub-status` fails or the page no longer matches the confirmed layout. Do not overwrite the Pi from this repository because v0.4.0 is not yet synchronised here.

**Evidence to record:** Version, file paths, command result, service result, route checks and non-sensitive visual evidence.

## Phase 10 — Uvicorn local service validation

**Objective:** Prove the application runs with one Uvicorn worker on loopback before introducing systemd or Nginx.

**Prerequisites:** Phase 9 complete; protected runtime values temporarily available through an approved method; database path prepared or application able to start in its approved readiness mode.

**Current state:** **Complete** — One Uvicorn worker is bound to `127.0.0.1:8000`; port 8000 is not exposed to the LAN.

1. [x] Start Uvicorn in the foreground as the `asth` service account.
2. [x] Bind only to `127.0.0.1:8000`.
3. [x] Retain the previously validated single-worker process model until representative testing justifies a controlled change.
4. [x] Confirm development reload mode is absent.
5. [x] Request `<health-path>` from the Pi itself.
6. [x] Check listeners and verify port 8000 is not bound to `0.0.0.0` or the LAN address.
7. [x] Exercise one safe read-only application route.
8. [ ] Stop the foreground process cleanly and confirm the listener closes.

**Safe verification commands:**

```bash
curl --fail --silent --show-error http://127.0.0.1:8000<health-path>
ss -lntp
```

Planned foreground command:

```bash
/opt/asth/releases/<release-id>/.venv/bin/uvicorn <app-import> --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers --forwarded-allow-ips 127.0.0.1
```

**Expected result:** Health/read checks pass locally; exactly one Uvicorn worker listens only on loopback; graceful stop removes the listener.

**Stop condition:** Stop if Uvicorn binds to a LAN address, starts multiple workers, exposes debug output, logs secrets, cannot read/write approved paths, or cannot stop cleanly.

**Evidence to record:** Exact start command with secrets omitted, health status/body, `ss` output, worker/process count, read-route result, and clean-stop result.

## Phase 11 — systemd service preparation

**Objective:** Prepare and validate one least-privilege systemd service without adding a duplicate process supervisor.

**Prerequisites:** Phase 10 complete; reviewed `asth.service` content supplied separately; environment-file path and writable paths confirmed.

**Current state:** **Complete** — `asth.service` is enabled and active, and no failed services were observed.

1. [x] Review the proposed unit before placing it on the Pi.
2. [ ] Confirm `User=asth`, `Group=asth`, `WorkingDirectory=/opt/asth/current`, and absolute Uvicorn path.
3. [x] Confirm the Uvicorn arguments preserve loopback binding and one worker.
4. [x] Confirm the unit references `/etc/asth/asth.env` and does not contain secret values.
5. [ ] Review restart behavior, stop timeout, `UMask`, file-descriptor limit, and ordering.
6. [ ] Introduce hardening settings only with explicit writable paths for SQLite/media.
7. [ ] Validate unit syntax before enabling it.
8. [ ] Start, stop, restart, and inspect the service.
9. [x] Enable boot start only after all manual lifecycle checks pass.
10. [x] Reboot after physical recovery and verify automatic service recovery.

**Safe verification commands:**

```bash
systemd-analyze verify /etc/systemd/system/asth.service
systemctl status asth.service --no-pager
systemctl show asth.service -p User -p Group -p MainPID -p NRestarts
journalctl -u asth.service --since today --no-pager
```

Lifecycle operations — **sudo required**:

```bash
sudo systemctl daemon-reload
sudo systemctl start asth.service
sudo systemctl stop asth.service
sudo systemctl restart asth.service
sudo systemctl enable asth.service
```

**Expected result:** One unprivileged service starts/stops/restarts cleanly, survives reboot, accesses only required mutable paths, and passes the health check.

**Stop condition:** Stop if unit validation fails, the service runs as root, multiple workers/process supervisors appear, secrets are embedded, hardening blocks required writes, or restart loops occur.

**Evidence to record:** Reviewed unit checksum, verification output, status/show output, lifecycle test results, health checks, relevant journal entries, and reboot recovery time.

## Phase 12 — Nginx reverse proxy preparation

**Objective:** Provide LAN-facing HTTP through Nginx while keeping Uvicorn loopback-only.

**Prerequisites:** Phase 11 complete; reviewed Nginx site configuration supplied separately; hostname, LAN address, and request-size limit confirmed.

**Current state:** **Complete** — Nginx is enabled and active on port 80 and successfully proxies the validated endpoints.

1. [x] Confirm Nginx will listen only as required for the intended LAN pilot.
2. [x] Confirm proxy upstream is `http://127.0.0.1:8000`.
3. [ ] Review forwarded headers, conservative timeouts, `<max-request-size>`, and `server_tokens off`.
4. [ ] Confirm authenticated/user-specific responses are not cached.
5. [ ] Confirm static caching applies only to suitable versioned assets.
6. [ ] Validate Nginx syntax before every reload.
7. [ ] Reload Nginx without dropping established connections.
8. [x] Test the health route through Nginx from the Pi and one LAN client.
9. [ ] Stop ASTH briefly in the maintenance window and verify Nginx fails safely without exposing details.
10. [x] Reconfirm port 8000 is not LAN-facing.

**Safe verification commands:**

```bash
findmnt /mnt/rog
systemctl is-active mnt-rog.mount
systemctl is-active smbd
smbclient -L localhost -U asthadmin
systemctl is-active cockpit.socket
ss -lnt | grep -E 'LISTEN.+:9090\b'
curl http://10.42.0.1
curl --fail --silent --show-error http://127.0.0.1<health-path>
curl --fail --silent --show-error http://<pi-lan-ip><health-path>
ss -lntp
```

Validation and reload — **sudo required**:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

**Expected result:** Nginx serves the intended LAN URL, proxies health/application traffic to loopback Uvicorn, and presents a controlled upstream-unavailable response.

**Stop condition:** Stop if `nginx -t` fails, port 8000 is LAN-facing, sensitive headers/details leak, caching affects authenticated content, the default site conflicts, or unintended interfaces/networks can connect.

**Evidence to record:** Site checksum, `nginx -t`, listener list, Pi/LAN-client HTTP results, relevant response headers, safe-failure result, and Nginx status.

## Phase 13 — SQLite directory and permissions

**Objective:** Establish the live SQLite database location and permissions needed for database, journal, WAL, and shared-memory files.

**Prerequisites:** Phases 7 and 9 complete; schema/migration version approved; a pre-change backup exists if data already exists.

**Current state:** **Deferred** — `/var/lib/asth/db` exists but is empty. No database file or database reference was found in the current application, so schema, live filename, connection and recovery work await a database-backed module.

1. [ ] Confirm the live path is `/var/lib/asth/db/asth.sqlite3` or record the approved alternative.
2. [ ] Verify `/var/lib/asth/db` is owned by `asth:asth` with mode `0750`.
3. [ ] Initialize or migrate the database only through the application's reviewed release procedure.
4. [ ] Set database-file ownership to `asth:asth` and target mode `0640`.
5. [ ] Confirm foreign keys are enabled for application connections.
6. [ ] Record the selected journal mode and busy timeout.
7. [ ] Run SQLite integrity and foreign-key checks.
8. [ ] Perform one controlled application write and read-back.
9. [ ] Verify Nginx cannot read or serve the database directory.

**Safe verification commands:**

```bash
stat -c '%U:%G %a %n' /var/lib/asth/db /var/lib/asth/db/asth.sqlite3
sqlite3 /var/lib/asth/db/asth.sqlite3 "PRAGMA integrity_check;"
sqlite3 /var/lib/asth/db/asth.sqlite3 "PRAGMA foreign_key_check;"
sqlite3 /var/lib/asth/db/asth.sqlite3 "PRAGMA journal_mode; PRAGMA busy_timeout;"
```

**Expected result:** SQLite reports `ok` for integrity, no foreign-key violations, correct permissions, and a successful application-level write/read with one writer process.

**Stop condition:** Stop before initialization/migration without a tested procedure and backup. Stop on integrity errors, ownership mismatch, multiple writers, database placement under a web-served path, or unexplained schema mismatch.

**Evidence to record:** Database path, schema version, owner/modes, PRAGMA outputs, migration result, controlled write/read test, and pre-change backup reference.

## Phase 14 — Environment variables and secrets

**Objective:** Supply production runtime values through a protected systemd-compatible environment file without exposing secrets.

**Prerequisites:** Phase 13 complete; reviewed environment-variable inventory; authorized secret custodian and protected off-device recovery location.

**Current state:** **In Progress** — File metadata was previously confirmed as `root:root` mode `0600`. A non-secret structural check on 13 August 2026 found no `KEY=value` entries; required runtime-variable inventory and configuration therefore remain deferred until a module needs them.

1. [ ] List required variable names and document purpose, owner, and whether each is secret.
2. [ ] Confirm `/etc/asth/asth.env` will be owned by `root:asth` with mode `0640`.
3. [ ] Generate production secrets on the Pi or another approved secure system; never use example values.
4. [ ] Enter only required simple systemd-compatible `KEY=value` entries when the reviewed application configuration defines them.
5. [ ] Confirm trusted hosts/origins contain only the approved hostname/IP values.
6. [x] Confirm offline features are the default and cloud/API integrations are disabled.
7. [ ] Store required recovery secrets separately under stronger off-device controls.
8. [x] Restart ASTH and validate configuration without printing values.
9. [x] Check Git, logs, screenshots, and shell history procedures for accidental secret disclosure.

Secret generation example; output is sensitive and must not be captured:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Metadata-only checks — **sudo required**:

```bash
sudo stat -c '%U:%G %a %n' /etc/asth/asth.env
sudo systemctl show asth.service -p EnvironmentFiles
```

**Expected result:** Runtime values load successfully; file metadata is `root:asth 640`; no secret value appears in Git, logs, screenshots, unit files, or client assets.

**Stop condition:** Stop if secret ownership is unclear, file modes are broader than `0640`, secrets would be pasted into tracked files/commands/logs, or required trusted-host/origin values are unconfirmed.

**Evidence to record:** Variable-name inventory only, file checksum if policy permits, owner/mode, secret-custodian confirmation, recovery-copy location reference, restart/health result, and disclosure scan result.

## Phase 15 — Logging and log rotation

**Objective:** Produce useful non-sensitive service/proxy logs while bounding writes on the current 32 GB microSD.

**Prerequisites:** Phases 11 and 12 complete; logging owner and retention targets approved.

**Current state:** **In Progress** — `/var/log/asth` exists. Production log rotation, retention and capacity behavior still require confirmation.

1. [ ] Confirm FastAPI/Uvicorn writes standard output/error to journald.
2. [ ] Confirm production level defaults to `INFO`, not debug.
3. [ ] Exercise a normal request and a controlled error; verify actionable entries.
4. [ ] Check that passwords, tokens, cookies, request bodies, and unnecessary personal data are absent.
5. [ ] Record current journald disk use and retention behavior.
6. [ ] Review a bounded journald target, initially approximately 100MB and 14 days, against whole-host needs.
7. [ ] Confirm Raspberry Pi OS logrotate covers Nginx access/error logs.
8. [ ] Run a non-destructive logrotate debug check.
9. [ ] Confirm `/var/log` and `/` remain comfortably below capacity thresholds.

**Safe verification commands:**

```bash
journalctl -u asth.service --since today --no-pager
journalctl --disk-usage
du -sh /var/log
df -h /
grep -R "/var/log/nginx" /etc/logrotate.d
```

Logrotate debug mode — **sudo required**, but does not rotate files:

```bash
sudo logrotate --debug /etc/logrotate.conf
```

**Expected result:** Relevant events are visible, sensitive values are absent, Nginx rotation is recognized, and logs have an approved bounded-retention plan.

**Stop condition:** Stop if secrets/personal data appear, logs grow without bounds, rotation validation errors occur, disk usage is already high, or diagnostic verbosity is left enabled.

**Evidence to record:** Redacted sample entries, journald disk use, retention decision, logrotate debug result, `/var/log` size, root free space, and reviewer sign-off.

## Phase 16 — Backup destination and recovery test

**Objective:** Prove ASTH data can be backed up consistently to separate storage and restored into a safe test location.

**Prerequisites:** Phase 13 complete; `<backup-mount>` and retention confirmed; recovery operator assigned; sufficient off-device capacity; controlled test window.

**Current state:** **Deferred for database recovery** — The persistent external SSD and earlier manual file-copy/checksum evidence remain confirmed. However, `/var/lib/asth/db` is empty and the current application has no database file or reference. Database backup/restore has not passed or failed and resumes only after a database-backed module exists. Production schedule and retention decisions also remain open.

1. [x] Verify the backup destination is a different physical device or approved network/workstation destination.
2. [x] Record destination identity, mount type, capacity, owner, and access controls.
2a. [x] Confirm UUID-based `/mnt/rog` auto-mount and active `mnt-rog.mount` after a full reboot.
2b. [x] Confirm existing SSD data remains preserved and read/write access succeeds.
3. [ ] Choose a unique `<backup-id>` such as an approved UTC timestamp and confirm the snapshot filename does not already exist.
4. [ ] Create a consistent SQLite snapshot using SQLite's `.backup` mechanism.
5. [ ] Run `PRAGMA integrity_check;` on the snapshot.
6. [ ] Copy the snapshot and approved mutable content to the off-device destination.
7. [x] Verify copied file sizes and cryptographic checksums.
8. [ ] Restore the copied database snapshot into a separate test directory, never over the live database.
9. [ ] Run integrity/foreign-key checks against the restored test copy.
10. [ ] Complete an application-level database restore rehearsal in an isolated location or approved maintenance window.
11. [ ] Record recovery time, recovery point, lost-transaction window, and deviations.
12. [ ] Confirm the retention schedule will not fill either destination or local staging.

**Safe verification commands:**

```bash
findmnt /mnt/rog
systemctl is-active mnt-rog.mount
df -h /mnt/rog
test ! -e /var/lib/asth/backup-staging/asth-<backup-id>.sqlite3
sqlite3 /var/lib/asth/db/asth.sqlite3 ".backup '/var/lib/asth/backup-staging/asth-<backup-id>.sqlite3'"
sqlite3 /var/lib/asth/backup-staging/asth-<backup-id>.sqlite3 "PRAGMA integrity_check;"
sha256sum /var/lib/asth/backup-staging/asth-<backup-id>.sqlite3
```

**Warning:** Never restore over `/var/lib/asth/db/asth.sqlite3` while ASTH is running. Preserve the current database first, stop the service for an approved live restore, and retain both the failed database and matching release for recovery.

**Expected result:** An integrity-checked, checksum-verified off-device backup restores successfully to a separate location and passes the core data checks.

**Stop condition:** Stop if the destination is on the same microSD, checksums differ, integrity checks fail, access controls are inadequate, capacity is insufficient, or a safe isolated restore target is unavailable.

**Evidence to record:** Destination identity/capacity, backup timestamp and recovery point, source/destination checksums, integrity results, restore location, recovery-test results/time, and retention calculation.

## Phase 17 — Basic security hardening

**Objective:** Reduce the LAN attack surface without locking out administrators or breaking ASTH.

**Prerequisites:** Phases 5, 12, 14, and 16 complete; local console present; second key-authenticated SSH session open; `<lan-cidr>` and `<admin-cidr>` confirmed.

**Current state:** **In Progress** — UFW permits required hotspot services, restricted SSH from `10.42.0.0/24`, forwarding `wlan0` to `wlan1` for online portable mode, and forwarding `wlan0` to `eth0` verified with a phone on 30 July. SSH password login is still temporarily enabled.

**Portable hotspot firewall checks:**

1. [x] Permit DHCP UDP 67 on `wlan0` for hotspot clients.
2. [x] Permit DNS TCP/UDP 53 on `wlan0` for shared-mode name resolution.
3. [x] Permit Nginx HTTP port 80 through `wlan0`.
4. [x] Allow SSH on `wlan0` only from `10.42.0.0/24` to TCP port 22.
5. [x] Keep Uvicorn port 8000 unexposed.
6. [x] Exclude the hotspot password from documentation and Git.
7. [x] Verify UFW forwarding from `wlan0` to `wlan1` and retain forwarding from `wlan0` to `eth0`.
8. [x] Allow Samba only from `192.168.100.0/24` and `10.42.0.0/24` on `wlan0`.
9. [x] Allow Cockpit TCP 9090 only from `192.168.100.0/24` and `10.42.0.0/24` on `wlan0`.
1. [x] Inventory listening ports, enabled services, accounts, and router port forwarding.
2. [x] Disable direct root SSH login after key access is verified.
3. [ ] Disable SSH password authentication only after the second key session and local recovery pass.
4. [x] Define firewall rules using the real administration subnet and deployment LAN.
5. [ ] Keep the current SSH session open while applying and testing rules.
6. [ ] Verify a second new SSH connection before closing the original session.
7. [x] Permit HTTP only from the deployment LAN and SSH only from the administration subnet.
8. [x] Verify Uvicorn remains loopback-only.
9. [x] Disable only reviewed unused services; record each decision.
10. [ ] Confirm no router forwarding exposes ports 22, 80, 443, or 8000.
11. [ ] Verify application host/origin validation, session protections, login throttling, and upload limits through supplied tests.
12. [ ] Record a future locally trusted HTTPS decision; plain HTTP remains limited to the initial trusted-LAN pilot.

**Safe verification commands:**

```bash
ss -lntup
systemctl list-unit-files --state=enabled
sshd -T | grep -E '^(permitrootlogin|passwordauthentication|pubkeyauthentication) '
```

SSH/firewall changes require **sudo**. Use the chosen Raspberry Pi OS firewall tool and the confirmed CIDRs; validate its syntax before applying.

**Warning:** Incorrect SSH or firewall settings can lock out the administrator. Keep local console access and an existing SSH session. If a new key-authenticated session fails, revert the last change from the console before proceeding.

**Expected result:** Only approved LAN/admin traffic reaches Nginx/SSH, Uvicorn remains local, key access works, root/password SSH policy is hardened, and core ASTH functions still pass.

**Stop condition:** Stop on any access loss, unresolved CIDR, failed second SSH session, unexpected open port, internet exposure, application regression, or lack of a tested recovery console.

**Evidence to record:** Before/after listener and service inventories, effective SSH settings, firewall rule listing, two-session test, router screenshot, application security-test summary, and rollback notes.

## Phase 18 — Resource and thermal monitoring

**Objective:** Establish measured operating limits for CPU, RAM, swap, disk, temperature and throttling on the current Pi and repeat them after final assembly.

**Prerequisites:** Phases 12, 15, and 17 complete; active cooling operating; representative ASTH data and at least five test devices available.

**Current state:** **In Progress** — About 445 MiB RAM used, available memory must be remeasured, 26% root-disk use, 45.5 C and `throttled=0x0` were recorded. Sustained representative multi-device load evidence remains pending.

1. [x] Record an idle baseline after boot stabilization.
2. [ ] Run the core workflow on one device and record peak observations.
3. [ ] Run representative concurrent activity on at least five devices.
4. [x] Observe memory, swap, CPU load, storage, temperature, throttling, and service restarts.
5. [x] Confirm exactly one Uvicorn worker remains active.
6. [ ] Check that logging and temporary files do not grow unexpectedly.
7. [x] Confirm at least 20% root storage remains free.
8. [ ] Record acceptable pilot thresholds and an operator response for exceeding each.
9. [ ] Repeat monitoring after at least 15 minutes of representative load.

**Safe verification commands:**

```bash
free -h
vmstat 1
top
df -h /
vcgencmd measure_temp
vcgencmd get_throttled
systemctl show asth.service -p MainPID -p NRestarts -p MemoryCurrent
pgrep -a -f uvicorn
```

Use `Ctrl+C` to stop `vmstat 1` or `top`; these are observation commands.

**Expected result:** Core flows remain responsive for five representative devices with no OOM event, sustained swap pressure, throttling, restart loop, overheating, or storage threshold breach.

**Stop condition:** Stop pilot progression on any OOM kill, nonzero throttling state, sustained heavy swap, repeated service restart, rapidly rising temperature, less than 20% storage free, or unacceptable response times.

**Evidence to record:** Idle/load timestamps, device count/workload, peak RAM/swap/CPU/temperature, throttling output, storage use, restart count, response observations, thresholds, and test duration.

## Phase 19 — End-to-end local-network validation

**Objective:** Validate the confirmed hub journey now and the full learning journey after content is populated.

**Prerequisites:** Operational ASTH portable network; representative clients; approved test content and accounts for later learning-flow acceptance.

**Current state:** **In Progress** — The portable network, landing page and live status are confirmed. Two clients reconnected after migration to 5 GHz channel 36, and one Ethernet-backed speedtest observed 25 ms ping, 48.9 Mbps download and 35.8 Mbps upload. This is not a guaranteed maximum. Populated learning content, participant/trainer workflows, portable-mode uplink revalidation and representative concurrency remain pending.

1. [x] Connect intended client devices to the ASTH network.
2. [x] Open the recorded ASTH URL and visually confirm the v0.4.0 landing page.
3. [x] Confirm DVS/ASTH logos and the live hub online/offline state.
4. [x] Confirm connected devices, current download/upload, cumulative RX/TX, Wi-Fi information and uptime are supplied through `/api/hub-status`.
5. [x] Confirm the real-time graph appears on `/`.
6. [x] Confirm `/learn/` opens separately and intentionally has no network graph.
7. [ ] Populate and test Modul Pembelajaran, Video Latihan and Latihan Interaktif.
8. [ ] Test participant login, module/SOP viewing, quiz, score and progress if implemented.
9. [ ] Test trainer login and dashboard read-back if implemented.
10. [ ] Test the local knowledge-base Smart Tutor and source display if implemented.
11. [x] Confirm the hub remains locally available in the documented offline portable mode.
12. [ ] Run the approved complete learning flow concurrently on at least five devices.
13. [ ] Check logs, data consistency, resources and temperature during representative load.
14. [x] Retain the previously verified boundary that clients cannot connect directly to port 8000.
15. [x] Confirm the 5 GHz hotspot returns after reboot and `iw` again reports AP mode on channel 36 at 5180 MHz with 20 MHz runtime width, with zero failed units and healthy ASTH v0.4.0.

**Expected result:** The current hub data remains reliable and, after content implementation, all approved learning flows work for representative clients without requiring upstream internet.

**Stop condition:** Stop acceptance for live-status failure, data leakage, direct Uvicorn exposure, internet dependency in a core flow, repeated server errors, inconsistent learning results or resource/thermal breach.

**Evidence to record:** Device/browser matrix, URL, status data, screenshots without credentials, offline result, concurrency timing, log review and defect references.

## Phase 20 — Rollback readiness

**Objective:** Prove the immediately previous known-good release and matching data can be restored within a controlled window.

**Prerequisites:** For database-coupled rollback, Phase 16 complete with compatibility notes and an off-device database backup. For the current database-free application-only path, preserve verified current and previous files with checksums and an explicit forward-restoration copy.

**Current state:** **In Progress / application path verified** — On 13 August 2026, manual application rollback from v0.4.0 to v0.3.0 and forward restoration to v0.4.0 passed checksum, service restart, HTTP 200, health and version checks. Release-symlink rollback is not applicable to the confirmed single-file test; matching SQLite recovery is deferred because no database-backed module exists.

1. [x] Record current and previous application versions and file checksums.
2. [ ] Verify `/opt/asth/current` resolves to the intended current release.
3. [ ] Confirm the previous release has its own complete virtual environment.
4. [ ] Record current configuration checksum without exposing secret values.
5. [ ] Confirm database schema compatibility after a database-backed module exists.
6. [ ] Confirm a matching pre-deployment SQLite backup is off-device and integrity-checked after a live database exists.
7. [x] Rehearse application-only rollback and restore the current application during an approved controlled test.
8. [ ] Rehearse matching database recovery after a database-backed module and non-backward-compatible schema change exist.
9. [ ] Validate health, login, one read, one write, dashboard read-back, and media after rollback.
10. [x] Record the forward-recovery route after the rehearsal.

**Safe verification commands:**

```bash
readlink -f /opt/asth/current
ls -ld /opt/asth/releases/<current-release-id> /opt/asth/releases/<previous-release-id>
sha256sum <reviewed-non-secret-config-copy>
sqlite3 <restored-test-database> "PRAGMA integrity_check;"
```

**Warning:** Repointing the current release or restoring a live database changes production state. Stop `asth.service`, preserve the current database and symlink target, use an approved maintenance window, and keep the known-good release plus off-device backup available. Never delete a release during the rehearsal.

**Expected result:** For the current database-free application, operators can restore the verified previous file and then forward-restore v0.4.0 with matching checksums and health/version checks. After a database-backed module exists, the matching data recovery path must also pass its separate integrity and application checks.

**Stop condition:** Stop if release IDs/checksums are unknown, previous dependencies are incomplete, schema compatibility is unclear, backup integrity is unproven, or any rollback step would overwrite the only recoverable copy.

**Evidence to record:** Release IDs/checksums, symlink targets before/after, schema compatibility decision, backup reference, rollback/forward-recovery duration, validation results, and operator name.

## Phase 21 — Documentation and handover

**Objective:** Give the named operator enough accurate, non-secret information to operate, monitor, back up, recover, and escalate ASTH.

**Prerequisites:** Phases 19 and 20 complete; operational owners identified; evidence repository selected.

**Current state:** **In Progress** — Status and runbook documentation are updated through 13 August 2026, but handover cannot complete until the system custodian, technical and backup owners plus the maintenance window are confirmed.

1. [ ] Record hardware identity, hostname, reserved IP, LAN URL, interface, and physical location.
2. [ ] Record current/previous release IDs, application health path, database path, and schema version.
3. [ ] Record service/proxy status and log-inspection commands.
4. [ ] Record backup destination, schedule, retention, last success, and last restore-test result.
5. [ ] Record monitoring thresholds and response/escalation actions.
6. [ ] Record maintenance, safe shutdown/startup, rollback, and recovery procedures.
7. [ ] Record administrative contacts and access-request process without recording credentials.
8. [ ] Record known limitations: 32 GB microSD system storage, NVMe controller/HAT not arrived, MHS35 LCD not installed, placeholder Learning Hub content, database recovery deferred and repository source not synchronised.
9. [ ] Walk the operator through health, logs, backup evidence, shutdown/startup, and escalation.
10. [ ] Have the operator perform a supervised read-only health/status check.
11. [ ] Store screenshots/outputs in the approved non-secret evidence location.
12. [ ] Obtain handover acknowledgement and schedule the first maintenance/capacity review.

**Safe verification commands:**

```bash
hostnamectl
ip -brief address
readlink -f /opt/asth/current
systemctl status asth.service nginx --no-pager
journalctl -u asth.service --since today --no-pager
df -h /
```

**Expected result:** The operator can independently locate ASTH, check health/status/logs, identify backup/rollback points, and follow the escalation path without receiving secrets in documentation.

**Stop condition:** Stop handover if instructions disagree with the deployed state, ownership is missing, backup/rollback evidence is absent, credentials appear in documents, or the operator cannot complete the supervised checks.

**Evidence to record:** Handover date, operator/approver names, document versions, supervised-check result, evidence location, known-issues list, and first review date.

## Phase 22 — Final MVP acceptance checklist

**Objective:** Obtain evidence-based approval that the lightweight ASTH MVP is safe and ready for the controlled LAN pilot.

**Prerequisites:** Phases 1–21 complete; all blocking defects resolved or explicitly rejected from acceptance; acceptance owner present.

**Current state:** **Blocked / PARTIAL** — Physical recovery, the operational hub, manual application rollback/restoration and GPU/display-stack recovery are verified. Final hardware, Learning Hub content, kiosk, NVMe migration, deferred database backup/restore, source synchronisation, ownership and final approval remain outstanding.

1. [x] Confirm Raspberry Pi 5, 2 GB RAM and current 32 GB microSD match the confirmed baseline.
2. [ ] Confirm casing, NVMe, LCD, final power, cooling and temperature after assembly.
3. [x] Confirm Raspberry Pi OS architecture/time/storage checks pass.
4. [ ] Confirm hostname, reserved IP, LAN URL, and network boundary are documented.
5. [ ] Confirm named key-based administration.
5a. [x] Confirm local physical recovery, password recovery and approved `sudo` access work.
6. [x] Confirm only approved essential packages/services are present.
7. [ ] Confirm directory, release, environment, and SQLite ownership/modes match the plan.
8. [x] Confirm FastAPI runs through systemd with exactly one Uvicorn worker on `127.0.0.1:8000`.
9. [x] Confirm Nginx syntax passes and the LAN proxy/static behavior is correct.
10. [ ] Confirm secrets are protected and absent from Git, logs, screenshots, and client code.
11. [ ] Confirm journald/Nginx logs are useful, non-sensitive, and bounded.
12. [ ] Confirm an off-device backup and successful recovery test exist.
13. [ ] Confirm SSH/firewall/router hardening passes with no direct port 8000 or internet exposure.
14. [ ] Confirm five-device concurrent and offline core-flow tests pass.
15. [ ] Confirm quiz writes, progress, trainer dashboard, and Smart Tutor results are correct.
16. [ ] Confirm representative resource results and final-assembly power/cooling/thermal checks pass.
17. [ ] Confirm every required rollback path passes; application rollback/forward recovery passed, while database recovery is deferred.
18. [ ] Confirm handover is acknowledged and maintenance/review dates are scheduled.
19. [ ] Record remaining non-blocking limitations and obtain signed MVP pilot acceptance.

**Safe final verification commands:**

```bash
systemctl is-active asth.service nginx
systemctl is-enabled asth.service nginx
findmnt /mnt/rog
systemctl is-active mnt-rog.mount
systemctl is-active smbd
smbclient -L localhost -U asthadmin
systemctl is-active cockpit.socket
ss -lnt | grep -E 'LISTEN.+:9090\b'
curl http://10.42.0.1
curl --fail --silent --show-error http://127.0.0.1<health-path>
ss -lntp
free -h
df -h /
vcgencmd measure_temp
vcgencmd get_throttled
journalctl --disk-usage
readlink -f /opt/asth/current
```

**Expected result:** Every acceptance item has current evidence, no blocking defect remains, and `<acceptance-owner>` approves only the controlled LAN pilot.

**Stop condition:** Do not accept the MVP if any required phase is incomplete/blocked, a core flow fails, required backup/restore or rollback evidence is absent, secrets are exposed, Uvicorn is LAN-facing, internet exposure exists, or resource/thermal limits are exceeded. Application rollback is verified; database backup/restore remains deferred and cannot satisfy final database acceptance.

**Evidence to record:** Completed acceptance checklist, command-output bundle, test matrix, screenshots, current release/schema IDs, backup/restore/rollback references, known limitations, approver name, decision, and date.

---

## Destructive-action safety rule

This checklist intentionally does not provide commands to delete accounts, packages, releases, databases, logs, or configuration. If later implementation requires deletion or replacement:

1. identify the exact resolved target;
2. preserve a recoverable copy off-device where material;
3. stop affected services in an approved window;
4. document the recovery command and decision owner;
5. test recovery where practical; and
6. obtain explicit approval before the destructive command is run.

Do not use broad recursive deletion, unresolved variables, globs, or `/`, `/opt/asth`, `/var/lib/asth`, a home directory, or a workspace root as a destructive target.
