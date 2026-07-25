# ASTH Raspberry Pi 5 MVP Implementation Checklist

This document translates the approved [ASTH Raspberry Pi 5 Deployment Plan](DEPLOYMENT_PLAN.md) into small, independently verifiable implementation phases and records the infrastructure snapshot validated on **25 July 2026**. It remains an execution checklist only. Checked items are confirmed by the supplied validation record; unchecked items remain follow-up work or blocked. The overall infrastructure result is **Conditional Pass**, not production or application-MVP acceptance.

## Scope and operating rules

- Target hardware: Raspberry Pi 5 with 2GB LPDDR4X RAM and 32GB microSD storage.
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
| ASTH service account | Service runs as `asth.service`; runtime account not recorded | Pending confirmation | 25 July 2026 | Verify `User` and `Group` from the installed unit. |
| Pi hostname | `asth-pi` | Confirmed | 25 July 2026 | None. |
| Current LAN address | `192.168.100.187/24` | Confirmed current value | 25 July 2026 | Create DHCP reservation or another approved fixed-IP method. |
| Gateway | `192.168.100.1` | Confirmed | 25 July 2026 | None. |
| LAN and SSH administration subnet | `192.168.100.0/24` | Confirmed | 25 July 2026 | Revalidate if the deployment network changes. |
| Primary network paths | Ethernet active and built-in `wlan0` hotspot active simultaneously | Confirmed | 25 July 2026 | Ethernet fixed-IP method remains pending. |
| Portable hotspot | `ASTH-PORTABLE`, access point, 2.4 GHz (`bg`), channel 6, WPA-PSK, IPv4 shared | Confirmed | 25 July 2026 | Password is managed separately and excluded from Git. |
| Portable gateway and URL | `10.42.0.1/24`; `http://10.42.0.1` | Confirmed | 25 July 2026 | Same local URL in offline and online portable modes. |
| Portable internet uplink | ALFA AWUS036NHV on `wlan1`, `rtl8xxxu`, profile `PHONE-UPLINK` | Confirmed | 25 July 2026 | Credentials remain only in local NetworkManager. |
| Verified wlan1 route | `10.13.68.119/24`; `default via 10.13.68.67 dev wlan1` | Confirmed | 25 July 2026 | Address may change when the phone hotspot renews DHCP. |
| Portable SSH boundary | `10.42.0.0/24` to TCP port 22 on `wlan0` | Confirmed | 25 July 2026 | `ssh asthadmin@10.42.0.1` verified. |
| Router or DHCP owner | Not assigned | Pending decision | 25 July 2026 | Confirm network owner. |
| Time zone | `Asia/Kuala_Lumpur` | Confirmed | 25 July 2026 | None. |
| Release identifier and rollback release | Not recorded | Pending decision | 25 July 2026 | Define release identification and previous-known-good retention. |
| ASTH LAN URL | `http://192.168.100.187/` while the current lease remains valid | Conditional | 25 July 2026 | Update after fixed addressing and hostname resolution are approved. |
| Health endpoint | `/health` | Confirmed | 25 July 2026 | Keep response non-sensitive. |
| Minimal endpoints | `/`, `/health`, `/docs` | Confirmed | 25 July 2026 | These are infrastructure endpoints, not the real application MVP. |
| Application import target | Not recorded | Pending confirmation | 25 July 2026 | Confirm from the installed unit or release documentation. |
| SQLite location | Directory `/var/lib/asth/db`; schema and live filename not defined | Partially confirmed | 25 July 2026 | Design schema and record the production database filename. |
| Maximum request body | Not defined | Pending decision | 25 July 2026 | Set from real application requirements. |
| Environment file | `/etc/asth/asth.env`, `root:root`, mode `0600` | Confirmed | 25 July 2026 | Never expose its contents. |
| Persistent SSD mount | `/dev/sda2` at `/mnt/rog`; UUID `8E5AAE985AAE7C99`; NTFS via `ntfs3` | Confirmed complete | 25 July 2026 | Reboot and read/write verification passed; existing data preserved. |
| ASTH SSD namespace | `/mnt/rog/ASTH` with NAS, app-data, database, backups, logs and staging directories | Confirmed complete | 25 July 2026 | All directories owned by `asthadmin`; do not modify unrelated SSD contents. |
| Manual backup destination | `/mnt/rog/ASTH_BACKUP` | Confirmed preserved | 25 July 2026 | Production schedule, retention and alerting remain pending. |
| Configuration snapshot | `/mnt/rog/ASTH_BACKUP/config-snapshot` | Confirmed preserved | 25 July 2026 | Existing snapshot remained available after reboot. |
| Basic Samba NAS | `ASTH-Public`, `ASTH-Staff`, `ASTH-Uploads` read/write; `ROG-Drive` read-only | Confirmed complete | 25 July 2026 | `smbd` enabled/active; Windows read/write and read-only denial verified. |
| Cockpit console | HTTPS port 9090 on office LAN and `ASTH-PORTABLE` | Confirmed complete | 25 July 2026 | `cockpit.socket` enabled/active; self-signed certificate warning expected. |
| Backup retention and schedule | Not established | Pending decision | 25 July 2026 | Define production schedule, retention and alerting. |
| System owner | Not assigned | Pending decision | 25 July 2026 | Confirm accountable owner. |
| Technical owner | Not assigned | Pending decision | 25 July 2026 | Confirm technical owner. |
| Backup owner | Not assigned | Pending decision | 25 July 2026 | Confirm backup and restore-test owner. |
| Maintenance window | Not assigned | Pending decision | 25 July 2026 | Confirm routine and emergency windows. |
| MVP acceptance approver | Not assigned | Pending decision | 25 July 2026 | Confirm before final application acceptance. |

## Implementation Progress

Status as of **25 July 2026**:

| Not Started | In Progress | Blocked | Complete |
|---:|---:|---:|---:|
| 0 | 12 | 3 | 7 |

| Phase | Implementation phase | State | Evidence or reason |
|---:|---|---|---|
| 1 | Pre-deployment verification | In Progress | Technical/operational owners and maintenance window remain unconfirmed. |
| 2 | Raspberry Pi physical and thermal checks | In Progress | Cooling/thermal evidence passes; power-supply and full physical-inspection evidence were not supplied. |
| 3 | Raspberry Pi OS and architecture verification | Complete | Debian 13, arm64/aarch64, kernel and time zone recorded. |
| 4 | Hostname and network configuration | In Progress | Portable offline/online router modes are complete; Ethernet fixed-IP method remains pending. |
| 5 | User account and SSH preparation | In Progress | `asthadmin`, SSH and public-key support exist; key login is not yet established and password login remains enabled. |
| 6 | System update and essential package preparation | Complete | Validated runtime stack and no failed services. |
| 7 | ASTH directories and ownership | In Progress | Required paths exist; full ownership/mode inventory was not supplied. |
| 8 | Python virtual environment preparation | In Progress | Runtime versions work; virtual-environment path, pinned dependency inventory and `pip check` evidence were not supplied. |
| 9 | Minimal FastAPI application readiness | Complete | `/`, `/health` and `/docs` return HTTP 200; real ASTH features remain outside this result. |
| 10 | Uvicorn local service validation | Complete | One worker bound only to `127.0.0.1:8000`. |
| 11 | systemd service preparation | Complete | `asth.service` enabled and active. |
| 12 | Nginx reverse proxy preparation | Complete | Nginx enabled/active on port 80; port 8000 not LAN-exposed. |
| 13 | SQLite directory and permissions | In Progress | Directory exists; schema, live filename and permission evidence remain pending. |
| 14 | Environment variables and secrets | Complete | Environment file is `root:root` mode `0600`; no secret values are documented. |
| 15 | Logging and log rotation | In Progress | `/var/log/asth` exists; production retention and rotation evidence remain pending. |
| 16 | Backup destination and recovery test | In Progress | Persistent mount plus manual `rsync` and SHA-256 recovery passed; schedule, retention and SQLite integrity evidence remain pending. |
| 17 | Basic security hardening | In Progress | UFW/SSH/rpcbind controls pass; SSH key cutover remains pending. |
| 18 | Resource and thermal monitoring | In Progress | Baseline resource/thermal values pass; representative sustained multi-device load evidence remains pending. |
| 19 | End-to-end local-network validation | Blocked | Minimal endpoints pass; real participant/trainer/application workflows are not implemented. |
| 20 | Rollback readiness | In Progress | Configuration snapshot and recovery evidence exist; release/database rollback is not yet proven. |
| 21 | Documentation and handover | Blocked | Runbook/status documents are being created; owners and maintenance window are unconfirmed. |
| 22 | Final MVP acceptance checklist | Blocked | Infrastructure has Conditional Pass only; application MVP and approver are outstanding. |

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

**Current state:** **In Progress** — Hardware, host, network, services and backup locations are recorded. System/technical/backup owners, maintenance window and acceptance approver remain unconfirmed.

1. [x] Read `docs/DEPLOYMENT_PLAN.md` and record its verified Git reference: `77b81bb6b1d57cac0902162cd449b9c7ce37f4d7 | 2026-07-25 | docs: record Raspberry Pi infrastructure deployment status`.
2. [x] Confirm the Pi is the 2GB model and the microSD is 32GB.
3. [x] Confirm the deployment remains LAN-only and Docker remains deferred.
4. [ ] Assign the technical lead, network owner, recovery operator, and acceptance approver.
5. [ ] Confirm a keyboard/display, serial console, or equivalent local recovery route is available.
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

**Current state:** **In Progress** — Active cooling is installed; measured temperature was approximately 45.5 C and `throttled=0x0`. Power-supply rating and full physical-inspection evidence were not supplied.

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

**Current state:** **In Progress** — `ASTH-PORTABLE` on `wlan0` is complete for offline and online portable use. With Ethernet removed, `PHONE-UPLINK` on `wlan1` supplied the default route and client internet successfully. Ethernet fixed-IP work remains pending for office-LAN mode.

**Portable hotspot deployment:** **Complete**

1. [x] Configure connection/SSID `ASTH-PORTABLE` on built-in interface `wlan0` in access-point mode.
2. [x] Set 2.4 GHz (`bg`), channel 6, WPA-PSK and IPv4 shared mode without recording the password.
3. [x] Confirm gateway `10.42.0.1/24`, autoconnect enabled and autoconnect priority 100.
4. [x] Confirm Nginx port 80 is accessible through `wlan0` at `http://10.42.0.1`.
5. [x] Confirm DHCP issued addresses to a phone and laptop.
6. [x] Confirm DHCP UDP 67 and DNS TCP/UDP 53 are allowed through UFW on `wlan0`.
7. [x] Restrict SSH on `wlan0` to source subnet `10.42.0.0/24` and TCP port 22; verify `ssh asthadmin@10.42.0.1`.
8. [x] Confirm Ethernet and the portable hotspot operate simultaneously.
9. [x] Confirm `ASTH-PORTABLE` returns automatically after a full Raspberry Pi reboot.
10. [x] Record the verified root response: `{"service":"ASTH Lightweight MVP","status":"running"}`.
11. [x] Verify online portable mode through `PHONE-UPLINK` on `wlan1`, including forwarded internet with Ethernet removed.

**Portable operating steps:**

1. Power on the Raspberry Pi and wait for startup.
2. Connect the participant device to Wi-Fi network `ASTH-PORTABLE` using the separately managed credential.
3. Open `http://10.42.0.1`.

“Connected without internet” is expected only in offline portable mode. In online portable mode, `PHONE-UPLINK` on `wlan1` provides internet while the same local ASTH URL remains available.

**Safe hotspot verification commands:**

```bash
nmcli connection show --active
nmcli device status
nmcli -f connection.id,connection.interface-name,connection.autoconnect,connection.autoconnect-priority,802-11-wireless.mode,802-11-wireless.band,802-11-wireless.channel,802-11-wireless-security.key-mgmt,ipv4.method connection show ASTH-PORTABLE
ip -brief address show wlan0
iw dev wlan0 info
curl --fail --silent --show-error http://10.42.0.1
ip -brief address show wlan1
ip route show default
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

**Current state:** **In Progress** — Administrator `asthadmin`, SSH service and public-key support are present. Password authentication remains temporarily enabled until key login is established and tested.

1. [ ] List current human and system accounts and identify unused defaults for later review.
2. [x] Confirm `<admin-user>` is a named, accountable account rather than a shared login.
3. [x] Create the account only if it does not already exist.
4. [ ] Grant only the administrative group membership required by Raspberry Pi OS.
5. [ ] Install the administrator's public key with correct ownership and modes.
6. [ ] Open a second SSH session using the key and keep the first session open.
7. [ ] Verify approved `sudo` access from the named account.
8. [ ] Confirm local console recovery still works before later disabling password SSH.

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

**Expected result:** The OS is patched, required commands are available, and no unapproved service increases the 2GB RAM footprint.

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

## Phase 9 — Minimal FastAPI application readiness

**Objective:** Verify the supplied application release meets the minimum production interface without creating application source code on the Pi.

**Prerequisites:** Phase 8 complete; application release supplied through the approved development/release process; `<app-import>` and `<health-path>` confirmed.

**Current state:** **Complete for minimal infrastructure only** — `/`, `/health` and `/docs` return HTTP 200. No real ASTH application functionality is claimed.

1. [ ] Confirm the import target resolves, with the planned value `asth.main:app` unless the Decision Log says otherwise.
2. [x] Confirm a lightweight unauthenticated health endpoint exists and exposes no sensitive details.
3. [x] Confirm production reload/debug modes are disabled.
4. [x] Confirm the configured database and mutable paths point outside the immutable release.
5. [ ] Confirm schema initialization or migration is an explicit release step, not an uncontrolled service-start side effect.
6. [ ] Run the application's existing automated readiness checks, if supplied by the release.
7. [x] Import the ASGI application without starting a LAN listener.
8. [x] Confirm no application secret is embedded in source, client assets, or committed configuration.

**Safe verification commands:**

```bash
cd /opt/asth/releases/<release-id>
.venv/bin/python -c "from asth.main import app; print(type(app).__name__)"
.venv/bin/python -m pip check
```

Adjust the import-only check to the confirmed `<app-import>` without printing configuration values.

**Expected result:** The application imports successfully, has a non-sensitive health endpoint, uses external mutable paths, and is production-ready for local foreground testing.

**Stop condition:** Stop if imports fail, the health endpoint is missing/sensitive, reload/debug is enabled, migrations are uncontrolled, mutable data targets the release tree, or secrets are found in source.

**Evidence to record:** Release ID, import-test output, automated test summary, confirmed health path, migration/schema version, and secret-scan result without secret contents.

## Phase 10 — Uvicorn local service validation

**Objective:** Prove the application runs with one Uvicorn worker on loopback before introducing systemd or Nginx.

**Prerequisites:** Phase 9 complete; protected runtime values temporarily available through an approved method; database path prepared or application able to start in its approved readiness mode.

**Current state:** **Complete** — One Uvicorn worker is bound to `127.0.0.1:8000`; port 8000 is not exposed to the LAN.

1. [x] Start Uvicorn in the foreground as the `asth` service account.
2. [x] Bind only to `127.0.0.1:8000`.
3. [x] Specify exactly `--workers 1` because the Pi has 2GB RAM and SQLite.
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
10. [ ] Reboot once in the maintenance window and verify automatic recovery.

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

**Current state:** **In Progress** — `/var/lib/asth/db` exists, but the SQLite schema, live database filename, connection settings and permission evidence are not yet defined.

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

**Current state:** **Complete for infrastructure** — `/etc/asth/asth.env` is `root:root` mode `0600`; its contents remain secret and are not documented.

1. [ ] List required variable names and document purpose, owner, and whether each is secret.
2. [ ] Confirm `/etc/asth/asth.env` will be owned by `root:asth` with mode `0640`.
3. [ ] Generate production secrets on the Pi or another approved secure system; never use example values.
4. [x] Enter only simple systemd-compatible `KEY=value` entries.
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

**Objective:** Produce useful non-sensitive service/proxy logs while bounding writes on the 32GB microSD.

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

**Current state:** **In Progress** — The persistent SSD mount and manual backup/recovery using `rsync` and SHA-256 comparison passed. Production backup schedule/retention, SQLite snapshot and integrity evidence remain undefined.

1. [x] Verify the backup destination is a different physical device or approved network/workstation destination.
2. [x] Record destination identity, mount type, capacity, owner, and access controls.
2a. [x] Confirm UUID-based `/mnt/rog` auto-mount and active `mnt-rog.mount` after a full reboot.
2b. [x] Confirm existing SSD data remains preserved and read/write access succeeds.
3. [ ] Choose a unique `<backup-id>` such as an approved UTC timestamp and confirm the snapshot filename does not already exist.
4. [ ] Create a consistent SQLite snapshot using SQLite's `.backup` mechanism.
5. [ ] Run `PRAGMA integrity_check;` on the snapshot.
6. [ ] Copy the snapshot and approved mutable content to the off-device destination.
7. [x] Verify copied file sizes and cryptographic checksums.
8. [x] Restore the copied snapshot into a separate test directory, never over the live database.
9. [ ] Run integrity/foreign-key checks against the restored test copy.
10. [x] Complete an application-level recovery rehearsal in an isolated location or approved maintenance window.
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

**Current state:** **In Progress** — UFW permits required hotspot services, restricted SSH from `10.42.0.0/24`, forwarding `wlan0` to `wlan1` for online portable mode, and retained forwarding `wlan0` to `eth0` for office-LAN mode. SSH password login is still temporarily enabled.

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

**Objective:** Establish measured operating limits for CPU, RAM, swap, disk, temperature, and throttling on the real 2GB Pi.

**Prerequisites:** Phases 12, 15, and 17 complete; active cooling operating; representative ASTH data and at least five test devices available.

**Current state:** **In Progress** — About 445 MiB RAM used, 1.5 GiB available, 26% root-disk use, 45.5 C and `throttled=0x0` were recorded. Sustained representative multi-device load evidence remains pending.

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

**Objective:** Validate the complete MVP journey through Nginx from representative LAN devices with internet independence.

**Prerequisites:** Phases 12–18 complete; approved test accounts/data; at least five representative phones/tablets/computers; planned internet-disconnection test.

**Current state:** **Blocked for application acceptance** — Offline portable, online portable through `wlan1`, office-LAN forwarding through `eth0`, local ASTH access, client internet and restricted hotspot SSH are verified. Real login, content, quiz, progress, dashboard, Smart Tutor and SQLite workflows remain unimplemented.

1. [x] Connect each device to the intended training LAN.
2. [x] Open the recorded ASTH LAN URL through Nginx.
3. [ ] Verify health, landing page, static assets, and responsive layout.
4. [ ] Test participant login, module/SOP viewing, quiz submission, score, and progress.
5. [ ] Test trainer login and dashboard read-back of the submitted result.
6. [ ] Test the local knowledge-base Smart Tutor and source display.
7. [ ] Verify authentication separation and logout/session expiry behavior.
8. [ ] Test justified upload limits and safe rejection if uploads are in scope.
9. [x] Disconnect upstream internet while preserving the LAN, then repeat the core flow.
10. [ ] Run the core flow concurrently on at least five devices.
11. [ ] Check logs, database write/read consistency, resources, and temperature during the test.
12. [x] Confirm clients cannot connect directly to port 8000.

**Safe client/Pi verification commands:**

```bash
curl --fail --silent --show-error http://<pi-lan-ip><health-path>
curl --connect-timeout 3 http://<pi-lan-ip>:8000<health-path>
```

The second command is expected to fail from a LAN client.

**Expected result:** All critical participant/trainer flows work through Nginx for at least five devices, persist correctly in SQLite, and continue without upstream internet.

**Stop condition:** Stop acceptance for data loss/cross-user leakage, direct Uvicorn exposure, internet dependency in a core flow, authentication failure, repeated server errors, inconsistent dashboard results, or resource/thermal breach.

**Evidence to record:** Device/browser matrix, LAN URL and IP, pass/fail per flow, quiz record identifier without personal data, screenshots, offline test result, concurrency timing, listener test, log review, and defect references.

## Phase 20 — Rollback readiness

**Objective:** Prove the immediately previous known-good release and matching data can be restored within a controlled window.

**Prerequisites:** Phase 16 complete; current and immediately previous releases retained; release compatibility notes and pre-deployment off-device backup available.

**Current state:** **In Progress** — A configuration snapshot and successful file-recovery comparison exist. A known-good release rollback and matching SQLite recovery are not yet proven.

1. [ ] Record current and previous release IDs and checksums.
2. [ ] Verify `/opt/asth/current` resolves to the intended current release.
3. [ ] Confirm the previous release has its own complete virtual environment.
4. [ ] Record current configuration checksum without exposing secret values.
5. [ ] Confirm database schema compatibility between current and previous releases.
6. [ ] Confirm a matching pre-deployment SQLite backup is off-device and integrity-checked.
7. [ ] Rehearse application-only rollback using test data or an approved maintenance window when schemas are backward-compatible.
8. [ ] Rehearse matching database recovery when schemas are not backward-compatible.
9. [ ] Validate health, login, one read, one write, dashboard read-back, and media after rollback.
10. [ ] Record the forward-recovery route after the rehearsal.

**Safe verification commands:**

```bash
readlink -f /opt/asth/current
ls -ld /opt/asth/releases/<current-release-id> /opt/asth/releases/<previous-release-id>
sha256sum <reviewed-non-secret-config-copy>
sqlite3 <restored-test-database> "PRAGMA integrity_check;"
```

**Warning:** Repointing the current release or restoring a live database changes production state. Stop `asth.service`, preserve the current database and symlink target, use an approved maintenance window, and keep the known-good release plus off-device backup available. Never delete a release during the rehearsal.

**Expected result:** Operators can identify and restore the previous compatible release/data, then pass core checks within the recorded recovery time.

**Stop condition:** Stop if release IDs/checksums are unknown, previous dependencies are incomplete, schema compatibility is unclear, backup integrity is unproven, or any rollback step would overwrite the only recoverable copy.

**Evidence to record:** Release IDs/checksums, symlink targets before/after, schema compatibility decision, backup reference, rollback/forward-recovery duration, validation results, and operator name.

## Phase 21 — Documentation and handover

**Objective:** Give the named operator enough accurate, non-secret information to operate, monitor, back up, recover, and escalate ASTH.

**Prerequisites:** Phases 19 and 20 complete; operational owners identified; evidence repository selected.

**Current state:** **Blocked** — Status and runbook documentation can be prepared, but handover cannot complete until system, technical and backup owners plus the maintenance window are confirmed.

1. [ ] Record hardware identity, hostname, reserved IP, LAN URL, interface, and physical location.
2. [ ] Record current/previous release IDs, application health path, database path, and schema version.
3. [ ] Record service/proxy status and log-inspection commands.
4. [ ] Record backup destination, schedule, retention, last success, and last restore-test result.
5. [ ] Record monitoring thresholds and response/escalation actions.
6. [ ] Record maintenance, safe shutdown/startup, rollback, and recovery procedures.
7. [ ] Record administrative contacts and access-request process without recording credentials.
8. [ ] Record known limitations: 2GB RAM, 32GB microSD, one Uvicorn worker, LAN-only HTTP pilot, minimal services, and no Docker.
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

**Current state:** **Blocked / Conditional Pass** — Infrastructure checks pass conditionally; real application requirements, implementation, operational ownership and final acceptance approval remain outstanding.

1. [x] Confirm Raspberry Pi 5, 2GB RAM, 32GB microSD, power, and active cooling match the baseline.
2. [x] Confirm Raspberry Pi OS architecture/time/storage checks pass.
3. [ ] Confirm hostname, reserved IP, LAN URL, and network boundary are documented.
4. [ ] Confirm named key-based administration and local recovery work.
5. [x] Confirm only approved essential packages/services are present.
6. [ ] Confirm directory, release, environment, and SQLite ownership/modes match the plan.
7. [x] Confirm FastAPI runs through systemd with exactly one Uvicorn worker on `127.0.0.1:8000`.
8. [x] Confirm Nginx syntax passes and the LAN proxy/static behavior is correct.
9. [ ] Confirm secrets are protected and absent from Git, logs, screenshots, and client code.
10. [ ] Confirm journald/Nginx logs are useful, non-sensitive, and bounded.
11. [ ] Confirm an off-device backup and successful recovery test exist.
12. [ ] Confirm SSH/firewall/router hardening passes with no direct port 8000 or internet exposure.
13. [ ] Confirm five-device concurrent and offline core-flow tests pass.
14. [ ] Confirm quiz writes, progress, trainer dashboard, and Smart Tutor results are correct.
15. [x] Confirm resource, storage, power, and thermal results remain within recorded thresholds.
16. [ ] Confirm rollback rehearsal and forward recovery pass.
17. [ ] Confirm handover is acknowledged and maintenance/review dates are scheduled.
18. [ ] Record remaining non-blocking limitations and obtain signed MVP pilot acceptance.

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

**Stop condition:** Do not accept the MVP if any required phase is incomplete/blocked, a core flow fails, backup/restore or rollback is unproven, secrets are exposed, Uvicorn is LAN-facing, internet exposure exists, or resource/thermal limits are exceeded.

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
