# ASTH Raspberry Pi 5 Deployment Status

**Snapshot date:** 13 August 2026
**Overall result:** **PARTIAL — operational v0.4.0 hub with verified application rollback and display-stack recovery; final hardware and content pending, database recovery deferred**

This snapshot records the confirmed deployment state. Status labels mean:

- **CONFIRMED:** directly observed or validated on the deployed Raspberry Pi;
- **VERIFIED:** a controlled recovery or rollback action completed and its final state was checked;
- **PARTIAL:** operational but incomplete for the intended MVP;
- **DEFERRED:** deliberately postponed because the required application component does not yet exist;
- **PLANNED:** preferred future direction, subject to testing or approval; and
- **PENDING:** not yet received, installed, configured or validated.

No password, private key, token, API key or private credential is recorded here.

## Status summary

| Area | State | Current position |
|---|---|---|
| Raspberry Pi 5 | **CONFIRMED** | Operational with 2 GB RAM. |
| System storage | **CONFIRMED** | Raspberry Pi OS boots and runs from a 32 GB microSD card. |
| Physical recovery access | **CONFIRMED** | HDMI, USB keyboard, local `asthadmin` login, boot-recovery password recovery, `sudo` and normal reboot passed. |
| Portable network | **CONFIRMED** | `ASTH-PORTABLE` active on `wlan0` at `10.42.0.1/24`; phone health access and internet forwarding through `eth0` passed. |
| ASTH web application | **CONFIRMED** | FastAPI v0.4.0 is deployed and the live landing page was visually confirmed. |
| Landing page `/` | **CONFIRMED** | Main hub dashboard and intended LCD kiosk page. |
| Learning Hub `/learn/` | **PARTIAL** | Separate page exists; learning sections remain placeholders and have no network graph. |
| Live status API | **CONFIRMED** | `/api/hub-status` is an existing operational dependency. |
| Health check | **CONFIRMED** | Local ASTH health returned `healthy`/`running`. |
| System services | **CONFIRMED** | `systemctl --failed` reported zero failed units after recovery reboot. |
| GPU and display stack | **VERIFIED** | KMS enabled; DRI devices and `vc4`/`v3d` present; `rp1-test.service` active after its missing Xorg directory was created. |
| External SSD and Samba | **CONFIRMED** | `/mnt/rog` remained mounted after reboot and `smbd` was active. |
| Uptime Kuma and Cockpit | **CONFIRMED** | Uptime Kuma returned HTTP 200 after redirect; Cockpit listened on port 9090 and returned HTTP 200. |
| Application rollback/restoration | **VERIFIED** | v0.4.0 → v0.3.0 → v0.4.0 manual file rollback passed service restart, HTTP 200 and healthy/version checks. |
| Database backup/restore | **DEFERRED** | No database-backed module, database file or database reference exists; no pass/fail result is claimed. |
| Casing, NVMe and LCD | **PENDING** | MHS35 LCD is not installed and NVMe controller/HAT has not arrived. |
| Repository source sync | **PENDING** | Deployed v0.4.0 source is not yet committed to this repository. |
| Ownership and maintenance window | **PENDING** | System custodian and maintenance window are not finalised. |

## Confirmed hardware and storage

| Item | Confirmed state |
|---|---|
| Platform | Raspberry Pi 5 |
| RAM | 2 GB |
| Current boot/system medium | 32 GB microSD card |
| Casing | Final integrated assembly pending |
| NVMe controller/HAT | Not yet arrived |
| LCD | MHS35 not installed; driver installation deferred |

The NVMe hardware and LCD must not be described as installed. The LCD-show repository was cloned previously, but `MHS35-show` was not executed during the 13 August recovery. The preferred future direction is to boot the full operating system from NVMe and retain the microSD card as recovery media, but only after the controller/HAT arrives and the NVMe is detected, tested and approved.

Existing documentation from 25 July records the external 512 GB ASUS ROG STRIX Arion USB SSD as `/dev/sda` (mounted partition `/dev/sda2`) at `/mnt/rog`, with Samba storage and a manual backup area. It remains separate from the **pending NVMe controller/HAT**. Its availability does not prove database restore or future NVMe migration.

## Confirmed physical recovery and reboot

Physical recovery access is complete:

- HDMI display output and a USB keyboard worked;
- local login as `asthadmin` succeeded;
- the `asthadmin` password was recovered through boot recovery;
- `sudo` access returned `SUDO_OK`; and
- the Raspberry Pi rebooted normally afterward.

After reboot, `systemctl --failed` reported zero failed units, local ASTH health returned `healthy`/`running`, `/mnt/rog` remained mounted and `smbd` was active.

## Verified GPU and display-stack recovery

On 13 August 2026, `/boot/firmware/config.txt` was found with `dtoverlay=vc4-kms-v3d` commented out. A backup was created at `/boot/firmware/config.txt.before-vc4-fix-20260813`, then the single configuration change uncommented that overlay.

After reboot:

- `/dev/dri`, `card0`, `card1`, `renderD128` and `/dev/dri/by-path` were present;
- kernel modules `vc4` and `v3d` were loaded;
- `rp1-test.service` initially failed because `/etc/X11/xorg.conf.d` did not exist;
- the missing directory was created with root ownership and mode `755`, after which `rp1-test.service` became active; and
- final checks returned zero failed systemd units, active `asth.service`, and HTTP 200 healthy ASTH v0.4.0.

This verifies the GPU/display stack only. The MHS35 LCD is not installed, and no LCD-show driver script was run.

## Confirmed network and live hub data

- The ASTH portable network is operational.
- `ASTH-PORTABLE` was confirmed active on `wlan0` at `10.42.0.1/24`.
- A phone connected through `ASTH-PORTABLE` successfully accessed the ASTH health endpoint.
- Internet forwarding for that client through `eth0` was successfully verified.
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

Uptime Kuma responded successfully after redirect with HTTP 200. Cockpit was listening on TCP port 9090 and returned HTTP 200. Both remain linked from the main landing page. This snapshot does not claim that every advanced monitoring, alerting, notification, retention or security feature is configured or accepted.

## Current application backups

The following deployed application backups are confirmed on the Raspberry Pi microSD filesystem:

| Purpose | Path | State |
|---|---|---|
| Existing backend backup | `/opt/asth/app/main.py.backup-20260726` | **CONFIRMED** |
| Previous 3D Clay service-hub UI | `/opt/asth/app/main.py.backup-clay-service-hub-20260726` | **CONFIRMED** |
| Pre-test v0.4.0 safety copy | `/opt/asth/app/main.py.pre-rollback-test-20260730` | **VERIFIED** |

These copies provide local rollback reference only. Because they reside on the same microSD filesystem as the running OS, they do not protect against microSD failure and do not constitute a completed production backup strategy.

## Verified application rollback and restoration — 13 August 2026

The active file before testing was ASTH v0.4.0. The safety copy and original active `main.py` shared SHA-256:

`c984a4b412f00117b763f9daa6fa9f948102b84a913e99fe6201b0fba350a0d3`

The active file was temporarily replaced by `/opt/asth/app/main.py.backup-clay-service-hub-20260726`, whose SHA-256 was:

`d9ab6ed2312d0fddcae36af94c26df1c7e72a26c84afee0117a5b5b37564726a`

`asth.service` restarted successfully, and the rollback application returned HTTP 200, `healthy`, version v0.3.0. The current file was then restored from the safety copy; its SHA-256 again matched the original v0.4.0 file. The service restarted successfully, and final health verification returned HTTP 200, `healthy`, version v0.4.0. This proves manual application-file rollback and forward restoration for the current deployment.

## Deferred database backup and restore

Database backup/restore was not tested and is neither passed nor failed:

- `/var/lib/asth/db` exists but is empty;
- no database file or database reference was found in the current application; and
- `/etc/asth/asth.env` contains no `KEY=value` configuration.

Testing is **DEFERRED** until a database-backed module exists.

## Completed milestones

- **CONFIRMED:** Raspberry Pi 5 with 2 GB RAM is operational from the 32 GB microSD card.
- **CONFIRMED:** Physical recovery access, local login, password recovery, `sudo` and normal reboot passed.
- **CONFIRMED:** ASTH portable network, phone health access and internet forwarding through `eth0` are operational.
- **CONFIRMED:** v0.4.0 syntax validation passed.
- **CONFIRMED:** `asth` service restart succeeded.
- **CONFIRMED:** Live landing page was visually checked.
- **CONFIRMED:** `/`, `/learn/`, `/health` and `/api/hub-status` exist in the deployed page architecture.
- **CONFIRMED:** Main dashboard shows the specified live network/system data and graph.
- **CONFIRMED:** Zero failed units, healthy/running ASTH health, persistent `/mnt/rog` and active `smbd` were observed after reboot.
- **CONFIRMED:** Uptime Kuma and Cockpit returned HTTP 200; Cockpit listened on port 9090.
- **CONFIRMED:** Retained application-file recovery copies are present on the microSD filesystem, including the pre-test v0.4.0 safety copy.
- **VERIFIED:** Manual application rollback to v0.3.0 and restoration to v0.4.0 passed checksum, restart, HTTP 200, health and version checks.
- **VERIFIED:** The KMS/DRI display stack recovered, `rp1-test.service` became active and final system checks returned zero failed units with healthy ASTH v0.4.0.

## Partial milestones

- **PARTIAL:** Learning Hub shell exists, but contains placeholders rather than approved learning content.
- **PARTIAL:** Infrastructure monitoring and administration services exist, but advanced monitoring, alerting and security completion is not established.
- **DEFERRED:** Database backup/restore awaits a database-backed module; no database test result exists.
- **PARTIAL:** The landing page is ready to be the kiosk target, but no LCD is installed and kiosk mode is not configured.

## Planned direction

- **PLANNED:** Detect and test the NVMe after the hardware arrives.
- **PLANNED:** Decide the migration method based on test results.
- **PLANNED:** Prefer full operating-system boot from NVMe and preserve the current microSD as recovery media if migration succeeds.
- **PLANNED:** Store large Learning Hub content on NVMe when available.

## Pending work

1. Complete the Raspberry Pi 5 casing assembly with compatible LCD hardware.
2. Receive and install the NVMe controller/HAT and NVMe SSD.
3. Install the MHS35 LCD and run the compatible driver procedure; `MHS35-show` was not run during display recovery.
4. Verify the power supply, cooling and temperature after final assembly.
5. Detect and test NVMe before migration.
6. Decide and execute the final NVMe migration method.
7. Preserve the microSD as recovery media if full OS migration succeeds.
8. Configure LCD kiosk mode to open `/`.
9. Populate Learning Hub with actual modules, PDFs, videos and interactive content.
10. Move large Learning Hub content to NVMe when available.
11. Perform final post-assembly validation.
12. Commit the deployed v0.4.0 application source into this repository later.
13. Complete database backup/restore testing after a database-backed module exists.
14. Revalidate application rollback if final hardware or deployment-layout changes affect the recovery path.
15. Finalise the system custodian and maintenance window.

## Acceptance boundary

Physical recovery access, the operational network, core services, the v0.4.0 hub interface, manual application rollback/restoration and GPU/display-stack recovery are verified. Final assembled-hardware acceptance, complete Learning Hub content, LCD kiosk operation, NVMe migration, representative user validation, ownership, maintenance-window approval and repository source synchronisation remain incomplete. Database backup/restore is deferred until a database-backed module exists. The overall project must therefore remain **PARTIAL**, not production-complete.

For operating commands, see [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md). For phase tracking, see [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md).
