# ASTH Raspberry Pi 5 Deployment Status

**Snapshot date:** 25 July 2026
**Result:** Conditional Pass — infrastructure MVP only

This snapshot records the confirmed state of the ASTH Raspberry Pi infrastructure. It does not claim that the real ASTH application MVP, production backup automation, operational handover or final MVP acceptance is complete.

## Current system identity

| Item | Confirmed value |
|---|---|
| Hostname | `asth-pi` |
| Administrator | `asthadmin` |
| Hardware | Raspberry Pi 5 Model B Rev 1.1 |
| RAM | 2GB |
| System storage | 32GB microSD |
| Cooling | Active cooling |
| Time zone | `Asia/Kuala_Lumpur` |
| Operating system | Debian GNU/Linux 13 (Trixie) |
| Kernel | `6.18.34+rpt-rpi-2712` |
| Architecture | arm64 / aarch64 |

No real password, private key, token or secret is recorded in this document.

## Architecture

```text
LAN client
    |
    | HTTP :80, allowed only from 192.168.100.0/24
    v
Nginx on asth-pi
    |
    | loopback only
    v
Uvicorn 127.0.0.1:8000, one worker
    |
    v
Minimal FastAPI infrastructure application
    |
    +-- /var/lib/asth
    +-- /var/lib/asth/db (SQLite directory; schema not yet designed)
```

Current runtime versions:

| Component | Version or state |
|---|---|
| Python | 3.13.5 |
| FastAPI | 0.140.0 |
| Uvicorn | 0.51.0 |
| Uvicorn workers | One |
| Client-facing proxy | Nginx on port 80 |
| Process supervisor | systemd |
| Container runtime | Not part of the initial MVP architecture |

The current endpoints are infrastructure probes only:

- `/`
- `/health`
- `/docs`

They do not represent the planned participant portal, trainer portal, authentication, content modules, quizzes, progress tracking, dashboard, Smart Tutor or production SQLite behavior.

## Services

| Service or control | Confirmed state |
|---|---|
| `asth.service` | Enabled and active |
| `nginx` | Enabled and active |
| `ssh` | Enabled and active |
| UFW | Active |
| Failed systemd services | None observed |
| `rpcbind` | Disabled |
| `nfs-blkmap` | Disabled |

## Paths

| Purpose | Path | Confirmed state |
|---|---|---|
| Application root | `/opt/asth` | Present |
| Mutable data | `/var/lib/asth` | Present |
| SQLite directory | `/var/lib/asth/db` | Present; schema/live filename pending |
| Application log directory | `/var/log/asth` | Present; rotation/retention pending confirmation |
| Environment file | `/etc/asth/asth.env` | `root:root`, mode `0600` |
| Temporary SSD mount | `/media/asthadmin/ROG` | Desktop automount; not persistent |
| Manual backup directory | `/media/asthadmin/ROG/ASTH_BACKUP` | Present during validation |
| Configuration snapshot | `/media/asthadmin/ROG/ASTH_BACKUP/config-snapshot` | Present during validation |

The environment-file contents are intentionally excluded.

## Network and security

| Item | Confirmed value |
|---|---|
| Current IPv4 address | `192.168.100.187/24` |
| Gateway | `192.168.100.1` |
| LAN subnet | `192.168.100.0/24` |
| Active connection | Ethernet |
| Wi-Fi | Inactive |
| Uvicorn binding | `127.0.0.1:8000` |
| Nginx listener | Port 80 |
| UFW incoming policy | Deny |
| UFW outgoing policy | Allow |
| SSH rule | Port 22 allowed only from `192.168.100.0/24` |
| HTTP rule | Port 80 allowed only from `192.168.100.0/24` |
| Port 8000 | Not exposed to LAN |
| Port 111 | Closed |
| `PermitRootLogin` | `no` |
| `X11Forwarding` | `no` |
| `MaxAuthTries` | `4` |
| `PubkeyAuthentication` | `yes` |
| `PasswordAuthentication` | `yes` temporarily |

The address `192.168.100.187` is the current address, not yet an approved fixed address. A DHCP reservation or another approved fixed-IP method is required before the URL is treated as stable.

Password authentication must remain enabled until a named administrator proves key-based login in a second session and confirms a local recovery path. It may then be disabled through a controlled SSH hardening change.

## Validation evidence

| Check | Confirmed result |
|---|---|
| Root endpoint | HTTP 200 |
| Health endpoint | HTTP 200 |
| Docs endpoint | HTTP 200 |
| `asth.service` | Enabled and active |
| Nginx | Enabled and active |
| SSH | Enabled and active |
| UFW | Active |
| Failed services | None |
| Temperature | Approximately 45.5 C |
| Throttling | `throttled=0x0` |
| RAM used | Approximately 445 MiB |
| RAM available | Approximately 1.5 GiB |
| Root disk use | Approximately 26% |

These values establish a healthy infrastructure baseline. Representative sustained multi-device load and real application workflow validation remain outstanding.

## Backup status

An external ASUS ROG STRIX Arion SSD, approximately 512GB and formatted NTFS, was connected during validation. It was desktop-automounted at `/media/asthadmin/ROG`.

Confirmed backup evidence:

- manual backup directory: `/media/asthadmin/ROG/ASTH_BACKUP`;
- configuration snapshot: `/media/asthadmin/ROG/ASTH_BACKUP/config-snapshot`;
- recovery test completed successfully using `rsync`; and
- source/recovered content was compared using SHA-256 checksums.

Current limitations:

- the SSD mount is not persistent;
- the path depends on desktop automount behavior;
- a production backup schedule is not defined;
- retention is not defined;
- failure alerting is not defined;
- the backup owner is not assigned; and
- the test does not prove recovery of a future live SQLite application database or release rollback.

The current backup is useful recovery evidence but must not be described as production-ready backup automation.

## Conditional Pass explanation

The infrastructure MVP receives a **Conditional Pass** because the confirmed host, proxy, single-worker application service, LAN firewall, minimal endpoints, resource baseline and manual backup/recovery test operate as intended.

The pass is conditional because the following production and application requirements are not complete:

- stable network addressing;
- persistent SSD mounting;
- SSH-key cutover and password-login removal;
- complete filesystem ownership/mode evidence;
- production log rotation and retention evidence;
- real ASTH application requirements and features;
- SQLite schema and real data behavior;
- production backup schedule, retention and owner;
- representative multi-device application validation;
- release and database rollback rehearsal;
- operational ownership and maintenance window; and
- final MVP acceptance by an assigned approver.

## Outstanding decisions

- [ ] Select DHCP reservation or another approved fixed-IP method.
- [ ] Configure and test persistent SSD mounting by UUID.
- [ ] Establish SSH key authentication before disabling password login.
- [ ] Define the real ASTH application MVP requirements.
- [ ] Design the SQLite schema and migration/recovery approach.
- [ ] Implement and validate real application features.
- [ ] Define production backup schedule, retention and alerting.
- [ ] Confirm the system owner.
- [ ] Confirm the technical owner.
- [ ] Confirm the backup owner.
- [ ] Confirm the maintenance window.
- [ ] Confirm the MVP acceptance approver.

## Next recommended implementation order

1. Assign the system, technical and backup owners plus the maintenance window and acceptance approver.
2. Establish key-based SSH access, verify a second session and local recovery, then disable password authentication.
3. Create the DHCP reservation or approved fixed-IP method and update the documented LAN URL.
4. Configure the SSD by UUID, test it after reboot and verify that backup tasks fail safely when the mount is absent.
5. Define backup content, schedule, retention, verification, alerting and periodic restore tests.
6. Complete ownership/mode and log-rotation evidence for the existing infrastructure paths.
7. Define and approve the real ASTH application MVP requirements.
8. Design the SQLite schema, migration rules, integrity checks and backup/recovery behavior.
9. Implement real application features through the normal development and test process.
10. Run representative LAN, offline, multi-device, security, resource and thermal validation.
11. Rehearse release rollback and matching database recovery.
12. Complete operational handover and obtain final MVP acceptance.

For safe day-to-day commands, see [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md). For phase tracking, see [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md).