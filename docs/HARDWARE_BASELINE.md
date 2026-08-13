# ASTH Raspberry Pi 5 Hardware Baseline

**Baseline date:** 13 August 2026

This document distinguishes currently installed hardware from future hardware. Status labels are **CONFIRMED**, **VERIFIED**, **PARTIAL**, **DEFERRED**, **PLANNED** and **PENDING**. In particular, the NVMe controller/HAT has not arrived and the MHS35 LCD is not installed.

## 1. Confirmed current baseline

| Component | State | Baseline |
|---|---|---|
| Platform | **CONFIRMED** | Raspberry Pi 5 |
| Memory | **CONFIRMED** | 2 GB RAM |
| Current system storage | **CONFIRMED** | Raspberry Pi OS boots and runs from a 32 GB microSD card |
| Current Pi address | **CONFIRMED** | `192.168.100.187` observed; not documented as permanently reserved |
| ASTH portable network | **VERIFIED** | Built-in `wlan0`, AP, `ASTH-PORTABLE`, 5 GHz channel 36 (5180 MHz), 20 MHz width; persisted after reboot |
| Current internet uplink | **VERIFIED** | `eth0` through NetworkManager profile `Wired connection 1`; 1000 Mbps full-duplex |
| Optional wireless uplink | **PLANNED** | Alfa USB `wlan1`; disconnected and not involved in the 13 August test |
| Application | **CONFIRMED** | FastAPI v0.4.0, main file `/opt/asth/app/main.py` |
| Static logo assets | **CONFIRMED** | `/var/www/asth-hub/assets/` |
| Casing | **PENDING** | Final integrated assembly incomplete |
| NVMe controller/HAT | **PENDING** | Has not yet arrived; no installation or boot migration has occurred |
| LCD | **PENDING** | MHS35 is not installed; the cloned LCD-show repository was not used to run `MHS35-show` during the 13 August recovery |
| Display stack | **VERIFIED** | KMS/DRI recovered; `vc4` and `v3d` loaded and `rp1-test.service` active |
| Final power/cooling/thermal result | **PENDING** | Must be verified after final assembly |

The Raspberry Pi has 2 GB RAM. The separate 32 GB figure describes the current microSD storage capacity.

## 2. Confirmed physical recovery baseline

Physical recovery access is **CONFIRMED complete** as of 30 July 2026:

- HDMI display output and a USB keyboard worked successfully;
- local login as `asthadmin` succeeded;
- the `asthadmin` password was recovered through boot recovery;
- approved `sudo` access returned `SUDO_OK`; and
- the Raspberry Pi rebooted normally after recovery.

This confirms an available local recovery route for the current microSD deployment. Manual application rollback and restoration were subsequently verified on 13 August 2026. Database backup/restore is deferred until a database-backed module exists.

### Display-stack recovery — 13 August 2026

- `/boot/firmware/config.txt` had `dtoverlay=vc4-kms-v3d` commented out.
- A backup was created at `/boot/firmware/config.txt.before-vc4-fix-20260813`.
- The only configuration change uncommented `dtoverlay=vc4-kms-v3d`.
- After reboot, `/dev/dri`, `card0`, `card1`, `renderD128` and `/dev/dri/by-path` were present, and the `vc4` and `v3d` kernel modules were loaded.
- `rp1-test.service` initially failed because `/etc/X11/xorg.conf.d` did not exist. Creating that directory with root ownership and mode `755` allowed the service to become active.
- Final checks found zero failed systemd units, active `asth.service`, and HTTP 200 healthy ASTH v0.4.0.

## 3. Storage architecture

### Current boot medium

Raspberry Pi OS currently boots and runs entirely from the 32 GB microSD card. The live application and retained application-file recovery copies are on this microSD filesystem.

The microSD must remain the working source until the NVMe hardware arrives and passes detection, compatibility, power and stability tests. No document should imply that NVMe boot is already active.

### Existing external USB SSD evidence

Repository evidence dated 25 July records an external 512 GB ASUS ROG STRIX Arion SSD as `/dev/sda` (mounted partition `/dev/sda2`) at `/mnt/rog` through `ntfs3`, with an ASTH namespace, Samba shares and manual backup evidence. It remained the external SSD on 13 August. This device is separate from the pending NVMe controller/HAT and does not complete the future NVMe boot migration or prove database restore readiness.

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

1. **PENDING:** Receive and physically install the NVMe controller/HAT and SSD.
2. **PENDING:** Confirm detection and device identity without formatting or migrating data prematurely.
3. **PENDING:** Test power, cooling, temperature, storage stability and boot compatibility.
4. **PLANNED:** Select the migration method based on the test result.
5. **PLANNED:** Prefer full operating-system boot from NVMe if validation succeeds.
6. **PLANNED:** Preserve the current microSD as recovery media after a successful full-OS migration.
7. **PLANNED:** Store large Learning Hub content on NVMe when available.

## 4. Display and kiosk baseline

The MHS35 LCD is currently not installed. The LCD-show repository was cloned previously, but `MHS35-show` was not executed during display-stack recovery. The landing page at `/` remains the intended LCD kiosk target, but kiosk mode and LCD driver installation are deferred until compatible LCD/casing hardware is installed.

After arrival:

- install the LCD and correct display cable;
- verify stable display output after boot;
- confirm power and temperature with the final assembly;
- configure kiosk mode to open `/`;
- verify automatic recovery after a reboot; and
- retain a documented local recovery path if kiosk startup fails.

## 5. Network baseline

The current interface roles verified on 13 August are: `eth0` uses NetworkManager profile `Wired connection 1` and provides the route to `1.1.1.1` via `192.168.100.1` with source `192.168.100.187`; built-in `wlan0` hosts `ASTH-PORTABLE`; Alfa USB `wlan1` is disconnected; and disconnected `p2p-dev-wlan0` is normal. Ethernet negotiated at 1000 Mbps full-duplex and was not the identified local bottleneck.

The active hotspot uses 5 GHz channel 36 (5180 MHz), 20 MHz width and AP mode. Malaysia (`MY`) regulatory rules permitted this channel for indoor use; this does not establish outdoor approval or unrestricted operation. Two clients reconnected successfully. Observed link rates included 86.6 Mbps TX and 65–86.6 Mbps RX for one client, and 65 Mbps TX and 96.1 Mbps RX for the other. TX-failure counters remained unchanged during repeated observations after migration.

The prior 2.4 GHz channel 6, 20 MHz configuration remains historical evidence: traffic link rates were generally 57.7–72.2 Mbps, one client temporarily fell to 5.5 Mbps, TX failures increased, and practical throughput was about 3.5 MB/s (around 28 Mbps). Its profile was cloned as `ASTH-PORTABLE-2G-BACKUP` (UUID `5a0b842f-34cf-4892-96e3-c56c1c98e247`) with autoconnect disabled for rollback; no credential is recorded.

One practical post-migration speedtest through `ASTH-PORTABLE` observed 25 ms ping, 48.9 Mbps download and 35.8 Mbps upload. This is not a guaranteed maximum and does not indicate gigabit Wi-Fi. The Raspberry Pi hotspot remains on a 20 MHz channel and is the likely local throughput constraint relative to the gigabit Ethernet uplink. Alfa remains available as a future wireless uplink when Ethernet is unavailable, but it was not tested on 13 August.

After reboot, `wlan0` remained an AP on channel 36 at 5180 MHz with 20 MHz width, `systemctl --failed` returned zero failed units, and ASTH health returned status `healthy`, service `ASTH Adaptive Smart Training Hub`, version `0.4.0`. The first SSH attempt timed out while the Pi was still booting; the following attempt succeeded. The main landing page obtains live network/system data through `/api/hub-status` and displays connected devices, download/upload rates, cumulative RX/TX, Wi-Fi information, uptime and a real-time activity graph.

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

Confirmed microSD-local application copies include:

- `/opt/asth/app/main.py.backup-20260726`;
- `/opt/asth/app/main.py.backup-clay-service-hub-20260726`.
- `/opt/asth/app/main.py.pre-rollback-test-20260730`, created as the v0.4.0 safety copy before the 13 August rollback test.

The safety copy and active v0.4.0 `main.py` both had SHA-256 `c984a4b412f00117b763f9daa6fa9f948102b84a913e99fe6201b0fba350a0d3`. The v0.3.0 rollback file had SHA-256 `d9ab6ed2312d0fddcae36af94c26df1c7e72a26c84afee0117a5b5b37564726a`. Manual application rollback to v0.3.0 and restoration to v0.4.0 both restarted successfully and returned HTTP 200 healthy results. These files remain same-device recovery references, not off-device backups.

Database backup/restore was neither passed nor failed. The test is **DEFERRED** because `/var/lib/asth/db` exists but is empty, the current application contains no database file or database reference, and `/etc/asth/asth.env` contains no `KEY=value` configuration.

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
- application rollback is revalidated after final installation if the deployment layout changes; and
- database backup/restore is tested after a database-backed module exists.

## 11. Conclusion

The confirmed current baseline is a Raspberry Pi 5 with 2 GB RAM running Raspberry Pi OS and ASTH v0.4.0 from a 32 GB microSD card. Physical recovery, manual application rollback/restoration and the GPU/display stack are verified. The MHS35 LCD remains uninstalled, the NVMe controller/HAT has not arrived, and database backup/restore is deferred until a database-backed module exists. Full-OS boot from NVMe with microSD recovery is a preferred **PLANNED** direction, not a completed deployment state.
