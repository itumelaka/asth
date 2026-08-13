# Changelog

## 13 August 2026 — Network optimisation, rollback and display-stack recovery verification

- Verified manual application rollback from ASTH v0.4.0 to the retained v0.3.0 application file and successful restoration to v0.4.0, with the original/safety/restored v0.4.0 SHA-256 matching, successful service restarts and HTTP 200 healthy results at both stages.
- Re-enabled `dtoverlay=vc4-kms-v3d` after backing up `config.txt`; after reboot the expected DRI devices and `vc4`/`v3d` modules were present.
- Recorded the initial `rp1-test.service` failure caused by a missing `/etc/X11/xorg.conf.d`, its correction with root ownership and mode `755`, and the final state of zero failed units, active `asth.service` and healthy ASTH v0.4.0.
- Deferred database backup/restore because the database directory is empty and the current application has no database file, database reference or `KEY=value` environment configuration; no database restore result is claimed.
- Kept MHS35 LCD installation and `MHS35-show`, NVMe arrival/installation and boot migration pending. The system remains on the 32 GB microSD; the external 512 GB ROG SSD remains mounted at `/mnt/rog`.
- Verified the current interface roles: `eth0` provided the internet route and negotiated at 1000 Mbps full-duplex; built-in `wlan0` hosted `ASTH-PORTABLE`; Alfa USB `wlan1` and `p2p-dev-wlan0` were disconnected and did not participate in the performance test.
- Preserved the previous 2.4 GHz channel 6 hotspot as the autoconnect-disabled `ASTH-PORTABLE-2G-BACKUP` rollback profile, then migrated the active SSID to 5 GHz channel 36 (5180 MHz), 20 MHz width under the Malaysia indoor regulatory allowance.
- Recorded two successful client reconnections, stable TX-failure counters during repeated post-migration observations, and one practical result of 25 ms ping, 48.9 Mbps download and 35.8 Mbps upload. This is not a guaranteed maximum or a gigabit-Wi-Fi claim.
- Reboot verification confirmed channel 36 persisted, zero systemd units failed, and the ASTH health endpoint returned `healthy`, service `ASTH Adaptive Smart Training Hub`, version `0.4.0`.

## 30 July 2026 — Physical recovery and operational verification

- Corrected the Raspberry Pi 5 hardware baseline to 2 GB RAM.
- Recorded successful HDMI/USB-keyboard recovery, local `asthadmin` access, boot-recovery password recovery, `sudo` verification and normal reboot.
- Recorded healthy services, persistent external SSD and Samba, successful Uptime Kuma and Cockpit HTTP checks, active `ASTH-PORTABLE`, phone access and internet forwarding through `eth0`.
- Kept database backup/restore, application rollback, final casing/LCD/NVMe assembly, ownership and maintenance-window decisions pending.

## 26 July 2026 — Deployment documentation update

- Reconciled the documented hardware, network, v0.4.0 page architecture, supporting services, backups and pending NVMe/LCD/Learning Hub work with the confirmed Raspberry Pi deployment.

## 0.1 — Project Foundation

- Created ASTH README.
- Defined project principles.
- Drafted project charter.
- Drafted executive summary.
- Locked initial MVP scope.
- Created development roadmap.
