# ASTH Raspberry Pi 5 Hardware Baseline

**Baseline date:** 30 July 2026

This document distinguishes currently installed hardware from future hardware. Status labels are **CONFIRMED**, **PARTIAL**, **PLANNED** and **PENDING**. In particular, the NVMe base/HAT, NVMe SSD, casing and LCD have **not** been installed.

## 1. Confirmed current baseline

| Component | State | Baseline |
|---|---|---|
| Platform | **CONFIRMED** | Raspberry Pi 5 |
| Memory | **CONFIRMED** | 2 GB RAM |
| Current system storage | **CONFIRMED** | Raspberry Pi OS boots and runs from a 32 GB microSD card |
| Current Pi address | **CONFIRMED** | `192.168.100.187` observed; not documented as permanently reserved |
| ASTH portable network | **CONFIRMED** | Operational |
| Application | **CONFIRMED** | FastAPI v0.4.0, main file `/opt/asth/app/main.py` |
| Static logo assets | **CONFIRMED** | `/var/www/asth-hub/assets/` |
| Casing | **PENDING** | Final integrated assembly incomplete |
| NVMe base/HAT and SSD | **PENDING** | Not yet installed |
| LCD and display cable | **PENDING** | Final integrated assembly incomplete |
| Final power/cooling/thermal result | **PENDING** | Must be verified after final assembly |

The Raspberry Pi has 2 GB RAM. The separate 32 GB figure describes the current microSD storage capacity.

## 2. Confirmed physical recovery baseline

Physical recovery access is **CONFIRMED complete** as of 30 July 2026:

- HDMI display output and a USB keyboard worked successfully;
- local login as `asthadmin` succeeded;
- the `asthadmin` password was recovered through boot recovery;
- approved `sudo` access returned `SUDO_OK`; and
- the Raspberry Pi rebooted normally after recovery.

This confirms an available local recovery route for the current microSD deployment. It does not replace the still-pending database backup/restore test or application rollback test.

## 3. Storage architecture

### Current boot medium

Raspberry Pi OS currently boots and runs entirely from the 32 GB microSD card. The live application and the two confirmed application-file backups are on this microSD filesystem.

The microSD must remain the working source until the NVMe hardware arrives and passes detection, compatibility, power and stability tests. No document should imply that NVMe boot is already active.

### Existing external USB SSD evidence

Repository evidence dated 25 July records an external ASUS ROG STRIX Arion SSD mounted at `/mnt/rog` through `ntfs3`, with an ASTH namespace, Samba shares and manual backup evidence. On 30 July, `/mnt/rog` was confirmed still mounted after reboot and `smbd` was active. This external USB SSD is separate from the pending NVMe base/HAT and NVMe SSD. Its presence does not complete the future NVMe boot migration or prove database restore readiness.

Existing documented namespace:

```text
/mnt/rog/ASTH/
├── nas/
│   ├── public
│   ├── staff
│   └── uploads
├── app-data
├── database
├── backups
├── logs
└── staging
```

Existing unrelated data outside `/mnt/rog/ASTH` must remain untouched.

### Planned NVMe direction

1. **PENDING:** Receive and physically install the NVMe base/HAT and SSD.
2. **PENDING:** Confirm detection and device identity without formatting or migrating data prematurely.
3. **PENDING:** Test power, cooling, temperature, storage stability and boot compatibility.
4. **PLANNED:** Select the migration method based on the test result.
5. **PLANNED:** Prefer full operating-system boot from NVMe if validation succeeds.
6. **PLANNED:** Preserve the current microSD as recovery media after a successful full-OS migration.
7. **PLANNED:** Store large Learning Hub content on NVMe when available.

## 4. Display and kiosk baseline

The final integrated LCD/casing assembly is pending. The landing page at `/` is the intended LCD kiosk target, but kiosk mode is not yet configured and no final LCD installation is complete.

After arrival:

- install the LCD and correct display cable;
- verify stable display output after boot;
- confirm power and temperature with the final assembly;
- configure kiosk mode to open `/`;
- verify automatic recovery after a reboot; and
- retain a documented local recovery path if kiosk startup fails.

## 5. Network baseline

The ASTH portable network is operational. On 30 July, `ASTH-PORTABLE` was active on `wlan0` at `10.42.0.1/24`; a connected phone reached the ASTH health endpoint and internet forwarding through `eth0` succeeded. The main landing page obtains live network/system data through `/api/hub-status` and displays connected devices, download/upload rates, cumulative RX/TX, Wi-Fi information, uptime and a real-time activity graph.

Earlier repository evidence documents the existing portable SSID, interface names, local gateway, office-LAN subnet, firewall boundaries and optional uplink mode. These established values may be used for support, but this update does not invent or change network names, credentials, ports or configuration.

## 6. Suitable workloads

The confirmed Raspberry Pi 5 is suitable for:

- the current FastAPI v0.4.0 landing page and Learning Hub shell;
- live local network-status polling and graph display;
- responsive offline-first learning content;
- locally stored modules, PDFs and optimised media;
- lightweight quizzes, progress records and trainer workflows when implemented and tested;
- Uptime Kuma and Cockpit as separate supporting services within measured resource limits; and
- a simple, maintainable application architecture.

The 2 GB RAM baseline requires a lightweight service footprint. Storage, thermal, power, data-integrity and operational risks also remain, so service count and complexity must be justified by measured need.

## 7. Workloads and practices to avoid

- Treating the 32 GB microSD as unlimited media or backup capacity.
- Storing the only recovery copy on the same microSD as the running OS.
- Migrating or formatting the future NVMe before detection and recovery planning are complete.
- Assuming LCD kiosk operation before the display and cable are installed and tested.
- Heavy video transcoding or uncontrolled high-resolution media delivery.
- Unbounded logs, caches, uploads or monitoring retention.
- Exposing credentials in documentation, commands, screenshots or source control.
- Claiming advanced monitoring, alerting or security readiness without evidence.

## 8. Power, cooling and thermal requirements

The final assembly has not been validated because the casing, NVMe hardware and LCD are pending. After installation:

- identify and verify the power-supply capability for the Pi and all attached hardware;
- confirm cooling is installed correctly and airflow is unobstructed;
- record idle and representative-load temperature;
- check for undervoltage, throttling and storage errors;
- test with the LCD, NVMe and any external storage connected; and
- repeat the checks after a sustained representative workload.

Earlier thermal measurements remain historical evidence only; they do not replace validation of the final assembly.

## 9. Backup and recovery baseline

Confirmed microSD-local application copies:

- `/opt/asth/app/main.py.backup-20260726`;
- `/opt/asth/app/main.py.backup-clay-service-hub-20260726`.

These files are useful local rollback references but are not off-device backups. The external SSD remaining mounted after reboot does not prove database backup/restore. Database backup/restore testing and application rollback testing remain pending, and final acceptance also requires a fresh post-installation test covering the chosen NVMe/microSD architecture.

If full-OS NVMe migration succeeds, the microSD should be preserved as recovery media only after:

- the NVMe system boots reliably;
- the deployed application and all required endpoints work;
- the LCD kiosk and portable network recover after reboot;
- backup and restore procedures have been tested; and
- the microSD recovery purpose, date and limitations are labelled.

## 10. Final assembly acceptance

The hardware milestone remains **PENDING** until all of the following are evidenced:

- casing, NVMe and LCD installed;
- correct display cable fitted;
- power, cooling and temperature verified;
- NVMe detected and tested;
- migration method recorded and executed successfully if approved;
- microSD retained and tested as recovery media if full migration succeeds;
- kiosk mode opens `/` after boot;
- large Learning Hub content placement confirmed; and
- post-installation database backup/restore and application rollback testing passes.

## 11. Conclusion

The confirmed current baseline is a Raspberry Pi 5 with 2 GB RAM running Raspberry Pi OS and ASTH v0.4.0 from a 32 GB microSD card. Physical recovery access and the portable hub are operational. The casing, NVMe and LCD remain pending. Database backup/restore and application rollback testing also remain pending. Full-OS boot from NVMe with microSD recovery is a preferred **PLANNED** direction, not a completed deployment state.
