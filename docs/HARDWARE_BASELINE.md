# ASTH Raspberry Pi 5 Hardware Baseline

**Baseline date:** 26 July 2026

This document distinguishes currently installed hardware from future hardware. Status labels are **CONFIRMED**, **PARTIAL**, **PLANNED** and **PENDING**. In particular, the NVMe base/HAT, NVMe SSD, casing and LCD have **not** been installed.

## 1. Confirmed current baseline

| Component | State | Baseline |
|---|---|---|
| Platform | **CONFIRMED** | Raspberry Pi 5 |
| Memory | **CONFIRMED** | 32 GB RAM |
| Current system storage | **CONFIRMED** | Raspberry Pi OS boots and runs from a 32 GB microSD card |
| Current Pi address | **CONFIRMED** | `192.168.100.187` observed; not documented as permanently reserved |
| ASTH portable network | **CONFIRMED** | Operational |
| Application | **CONFIRMED** | FastAPI v0.4.0, main file `/opt/asth/app/main.py` |
| Static logo assets | **CONFIRMED** | `/var/www/asth-hub/assets/` |
| Casing | **PENDING** | Awaiting arrival and installation |
| NVMe base/HAT and SSD | **PENDING** | Awaiting arrival and installation |
| LCD and display cable | **PENDING** | Awaiting arrival and installation |
| Final power/cooling/thermal result | **PENDING** | Must be verified after final assembly |

The 32 GB figures describe two different resources: the Raspberry Pi has 32 GB RAM and the current microSD has 32 GB storage.

## 2. Storage architecture

### Current boot medium

Raspberry Pi OS currently boots and runs entirely from the 32 GB microSD card. The live application and the two confirmed application-file backups are on this microSD filesystem.

The microSD must remain the working source until the NVMe hardware arrives and passes detection, compatibility, power and stability tests. No document should imply that NVMe boot is already active.

### Existing external USB SSD evidence

Repository evidence dated 25 July records an external ASUS ROG STRIX Arion SSD mounted at `/mnt/rog` through `ntfs3`, with an ASTH namespace, Samba shares and manual backup evidence. This external USB SSD is separate from the pending NVMe base/HAT and NVMe SSD. Its presence does not complete the future NVMe boot migration.

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

## 3. Display and kiosk baseline

The LCD and appropriate display cable are pending arrival. The landing page at `/` is the intended LCD kiosk target, but kiosk mode is not yet configured and no LCD installation is complete.

After arrival:

- install the LCD and correct display cable;
- verify stable display output after boot;
- confirm power and temperature with the final assembly;
- configure kiosk mode to open `/`;
- verify automatic recovery after a reboot; and
- retain a documented local recovery path if kiosk startup fails.

## 4. Network baseline

The ASTH portable network is operational. The main landing page obtains live network/system data through `/api/hub-status` and displays connected devices, download/upload rates, cumulative RX/TX, Wi-Fi information, uptime and a real-time activity graph.

Earlier repository evidence documents the existing portable SSID, interface names, local gateway, office-LAN subnet, firewall boundaries and optional uplink mode. These established values may be used for support, but this update does not invent or change network names, credentials, ports or configuration.

## 5. Suitable workloads

The confirmed Raspberry Pi 5 is suitable for:

- the current FastAPI v0.4.0 landing page and Learning Hub shell;
- live local network-status polling and graph display;
- responsive offline-first learning content;
- locally stored modules, PDFs and optimised media;
- lightweight quizzes, progress records and trainer workflows when implemented and tested;
- Uptime Kuma and Cockpit as separate supporting services within measured resource limits; and
- a simple, maintainable application architecture.

The larger RAM capacity does not remove storage, thermal, power, data-integrity or operational risks. Service count and complexity should still be justified by measured need.

## 6. Workloads and practices to avoid

- Treating the 32 GB microSD as unlimited media or backup capacity.
- Storing the only recovery copy on the same microSD as the running OS.
- Migrating or formatting the future NVMe before detection and recovery planning are complete.
- Assuming LCD kiosk operation before the display and cable are installed and tested.
- Heavy video transcoding or uncontrolled high-resolution media delivery.
- Unbounded logs, caches, uploads or monitoring retention.
- Exposing credentials in documentation, commands, screenshots or source control.
- Claiming advanced monitoring, alerting or security readiness without evidence.

## 7. Power, cooling and thermal requirements

The final assembly has not been validated because the casing, NVMe hardware and LCD are pending. After installation:

- identify and verify the power-supply capability for the Pi and all attached hardware;
- confirm cooling is installed correctly and airflow is unobstructed;
- record idle and representative-load temperature;
- check for undervoltage, throttling and storage errors;
- test with the LCD, NVMe and any external storage connected; and
- repeat the checks after a sustained representative workload.

Earlier thermal measurements remain historical evidence only; they do not replace validation of the final assembly.

## 8. Backup and recovery baseline

Confirmed microSD-local application copies:

- `/opt/asth/app/main.py.backup-20260726`;
- `/opt/asth/app/main.py.backup-clay-service-hub-20260726`.

These files are useful local rollback references but are not off-device backups. Existing external SSD backup evidence may be retained, but final acceptance requires a fresh post-installation backup and restore test covering the chosen NVMe/microSD architecture.

If full-OS NVMe migration succeeds, the microSD should be preserved as recovery media only after:

- the NVMe system boots reliably;
- the deployed application and all required endpoints work;
- the LCD kiosk and portable network recover after reboot;
- backup and restore procedures have been tested; and
- the microSD recovery purpose, date and limitations are labelled.

## 9. Final assembly acceptance

The hardware milestone remains **PENDING** until all of the following are evidenced:

- casing, NVMe and LCD installed;
- correct display cable fitted;
- power, cooling and temperature verified;
- NVMe detected and tested;
- migration method recorded and executed successfully if approved;
- microSD retained and tested as recovery media if full migration succeeds;
- kiosk mode opens `/` after boot;
- large Learning Hub content placement confirmed; and
- post-installation backup and recovery testing passes.

## 10. Conclusion

The confirmed current baseline is a Raspberry Pi 5 with 32 GB RAM running Raspberry Pi OS and ASTH v0.4.0 from a 32 GB microSD card. The portable hub is operational. The casing, NVMe and LCD remain pending. Full-OS boot from NVMe with microSD recovery is a preferred **PLANNED** direction, not a completed deployment state.
