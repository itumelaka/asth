# ASTH Raspberry Pi 5 Deployment Status

**Snapshot date:** 26 July 2026
**Overall result:** **PARTIAL — operational hub and v0.4.0 interface; final hardware, content and recovery work pending**

This snapshot records the confirmed deployment state. Status labels mean:

- **CONFIRMED:** directly observed or validated on the deployed Raspberry Pi;
- **PARTIAL:** operational but incomplete for the intended MVP;
- **PLANNED:** preferred future direction, subject to testing or approval; and
- **PENDING:** not yet received, installed, configured or validated.

No password, private key, token, API key or private credential is recorded here.

## Status summary

| Area | State | Current position |
|---|---|---|
| Raspberry Pi 5 | **CONFIRMED** | Operational with 32 GB RAM. |
| System storage | **CONFIRMED** | Raspberry Pi OS boots and runs from a 32 GB microSD card. |
| Portable network | **CONFIRMED** | Operational; current Pi address observed as `192.168.100.187`. |
| ASTH web application | **CONFIRMED** | FastAPI v0.4.0 is deployed and the live landing page was visually confirmed. |
| Landing page `/` | **CONFIRMED** | Main hub dashboard and intended LCD kiosk page. |
| Learning Hub `/learn/` | **PARTIAL** | Separate page exists; learning sections remain placeholders and have no network graph. |
| Live status API | **CONFIRMED** | `/api/hub-status` is an existing operational dependency. |
| Health check | **CONFIRMED** | `/health` remains available. |
| Uptime Kuma and Cockpit | **CONFIRMED** | Available as separate services linked from `/`; advanced feature completion is not implied. |
| Casing, NVMe and LCD | **PENDING** | Hardware has not arrived and is not installed. |
| Repository source sync | **PENDING** | Deployed v0.4.0 source is not yet committed to this repository. |
| Final backup/recovery acceptance | **PENDING** | Post-installation backup and recovery testing remains required. |

## Confirmed hardware and storage

| Item | Confirmed state |
|---|---|
| Platform | Raspberry Pi 5 |
| RAM | 32 GB |
| Current boot/system medium | 32 GB microSD card |
| Casing | Pending arrival and installation |
| NVMe base/HAT and SSD | Pending arrival and installation |
| LCD and display cable | Pending arrival and installation |

The NVMe hardware and LCD must not be described as installed. The preferred future direction is to boot the full operating system from NVMe and retain the microSD card as recovery media, but only after the NVMe is detected, tested and the migration method is approved.

Existing documentation from 25 July records an external ASUS ROG STRIX Arion USB SSD mounted at `/mnt/rog`, with Samba storage and a manual backup area. That external USB device is separate from the **pending NVMe base/HAT and SSD**. Its earlier evidence remains useful, but it does not prove that the future NVMe migration or final backup design is complete.

## Confirmed network and live hub data

- The ASTH portable network is operational.
- The current Raspberry Pi address observed on 26 July 2026 is `192.168.100.187`.
- This address is an observed current value; the existing documentation does not establish it as a permanent reserved address.
- `/api/hub-status` supplies live network and system data used by the landing page.
- The dashboard displays connected devices, current download and upload rates, cumulative RX/TX, Wi-Fi information and system uptime.
- The landing page also displays a real-time network activity graph.

Earlier repository evidence documents portable hotspot modes, interface names, local addressing and firewall rules. Those details remain in the operations runbook for support continuity. This update does not introduce a new SSID, interface, credential, port or network configuration.

## Confirmed application deployment

| Item | Confirmed value |
|---|---|
| FastAPI application version | v0.4.0 |
| Main application file | `/opt/asth/app/main.py` |
| Static logo assets | `/var/www/asth-hub/assets/` |
| Main landing page | `/` |
| Learning Hub | `/learn/` |
| Health endpoint | `/health` |
| Live status endpoint | `/api/hub-status` |

Python syntax validation passed using:

```bash
python3 -m py_compile /opt/asth/app/main.py
```

The application restarted successfully using:

```bash
sudo systemctl restart asth
```

The live landing page was then visually confirmed working. This validation establishes the current deployed file and service result; it does not establish that the same v0.4.0 source is already present in this repository.

## Page architecture

### `/` — main ASTH landing page

The main landing page is intended to become the Raspberry Pi LCD kiosk page. It contains:

- DVS and ASTH logos;
- hub online/offline status;
- connected-device count;
- current download and upload rates;
- total RX and TX;
- system uptime;
- Wi-Fi information;
- a real-time network activity graph; and
- links to Learning Hub, Uptime Kuma and Cockpit.

### `/learn/` — ASTH Learning Hub

The Learning Hub is deliberately separate from the network dashboard and intentionally has no network graph. It currently contains placeholder sections for:

- Modul Pembelajaran;
- Video Latihan; and
- Latihan Interaktif.

Actual modules, PDFs, videos and interactive learning content have not yet been populated. The Learning Hub is therefore **PARTIAL**, not complete.

## Supporting services

Uptime Kuma and Cockpit are available as separate services and are linked from the main landing page. Existing repository evidence also records Cockpit and other infrastructure checks. This snapshot does not claim that every advanced monitoring, alerting, notification, retention or security feature is configured or accepted.

## Current application backups

The following deployed application backups are confirmed on the Raspberry Pi microSD filesystem:

| Purpose | Path | State |
|---|---|---|
| Existing backend backup | `/opt/asth/app/main.py.backup-20260726` | **CONFIRMED** |
| Previous 3D Clay service-hub UI | `/opt/asth/app/main.py.backup-clay-service-hub-20260726` | **CONFIRMED** |

These copies provide local rollback reference only. Because they reside on the same microSD filesystem as the running OS, they do not protect against microSD failure and do not constitute a completed production backup strategy.

## Completed milestones

- **CONFIRMED:** Raspberry Pi 5 with 32 GB RAM is operational from the 32 GB microSD card.
- **CONFIRMED:** ASTH portable network is operational.
- **CONFIRMED:** v0.4.0 syntax validation passed.
- **CONFIRMED:** `asth` service restart succeeded.
- **CONFIRMED:** Live landing page was visually checked.
- **CONFIRMED:** `/`, `/learn/`, `/health` and `/api/hub-status` exist in the deployed page architecture.
- **CONFIRMED:** Main dashboard shows the specified live network/system data and graph.
- **CONFIRMED:** Uptime Kuma and Cockpit are available as linked supporting services.
- **CONFIRMED:** Two application-file backups are present on the microSD filesystem.

## Partial milestones

- **PARTIAL:** Learning Hub shell exists, but contains placeholders rather than approved learning content.
- **PARTIAL:** Infrastructure monitoring and administration services exist, but advanced monitoring, alerting and security completion is not established.
- **PARTIAL:** Backup evidence exists, but final post-installation backup, restore and recovery-media validation is outstanding.
- **PARTIAL:** The landing page is ready to be the kiosk target, but no LCD is installed and kiosk mode is not configured.

## Planned direction

- **PLANNED:** Detect and test the NVMe after the hardware arrives.
- **PLANNED:** Decide the migration method based on test results.
- **PLANNED:** Prefer full operating-system boot from NVMe and preserve the current microSD as recovery media if migration succeeds.
- **PLANNED:** Store large Learning Hub content on NVMe when available.

## Pending work

1. Receive and install the Raspberry Pi 5 casing.
2. Receive and install the NVMe base/HAT and SSD.
3. Receive and install the LCD and appropriate display cable.
4. Verify the power supply, cooling and temperature after final assembly.
5. Detect and test NVMe before migration.
6. Decide and execute the final NVMe migration method.
7. Preserve the microSD as recovery media if full OS migration succeeds.
8. Configure LCD kiosk mode to open `/`.
9. Populate Learning Hub with actual modules, PDFs, videos and interactive content.
10. Move large Learning Hub content to NVMe when available.
11. Perform post-installation validation, backup and recovery testing.
12. Commit the deployed v0.4.0 application source into this repository later.

## Acceptance boundary

The operational network and v0.4.0 hub interface are confirmed. Final assembled-hardware acceptance, complete Learning Hub content, kiosk operation, NVMe migration, representative user validation, backup/recovery acceptance and repository source synchronisation remain incomplete. The overall project must therefore remain **PARTIAL**, not production-complete.

For operating commands, see [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md). For phase tracking, see [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md).
