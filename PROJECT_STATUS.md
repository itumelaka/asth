# ASTH Project Status

**Status date:** 13 August 2026
**Deployed application version:** v0.4.0
**Current phase:** Raspberry Pi integration and Learning Hub content preparation
**Overall status:** Active — operational foundation, partial learning experience
**Primary next action:** Install and validate compatible LCD/casing hardware when available, then test the NVMe after the controller/HAT arrives without disturbing the working microSD deployment.

## Completed

- Project principles, charter, executive summary, MVP scope, roadmap and README drafted.
- Raspberry Pi 5 with 2 GB RAM operational from a 32 GB microSD card.
- HDMI display, USB keyboard, local `asthadmin` login, boot-recovery password recovery and `sudo` (`SUDO_OK`) verified; the Pi rebooted normally afterward.
- ASTH portable network operational on built-in `wlan0` at `10.42.0.1/24`; on 13 August it was migrated from the historical 2.4 GHz channel 6 configuration to 5 GHz channel 36 (5180 MHz), 20 MHz width. Two clients reconnected successfully and the setting persisted across reboot.
- Current internet routing uses `eth0` via `192.168.100.1`; the link negotiated at 1000 Mbps full-duplex and was not the identified local bottleneck. Alfa USB `wlan1` was disconnected and not involved in the 13 August performance test.
- One post-migration speedtest through `ASTH-PORTABLE` observed 25 ms ping, 48.9 Mbps download and 35.8 Mbps upload. This is a single observation, not a guaranteed maximum; the 20 MHz Raspberry Pi hotspot remains the likely local throughput constraint relative to Ethernet.
- The previous 2.4 GHz NetworkManager profile is retained as `ASTH-PORTABLE-2G-BACKUP` (UUID `5a0b842f-34cf-4892-96e3-c56c1c98e247`) with autoconnect disabled for rollback.
- Main landing page at `/`, Learning Hub shell at `/learn/`, `/health` and live `/api/hub-status` endpoint operational.
- v0.4.0 syntax validation, service restart and visual landing-page check completed on the Pi.
- Zero failed systemd units, healthy/running local ASTH health, persistent `/mnt/rog`, active `smbd`, Uptime Kuma HTTP 200 after redirect and Cockpit listening on port 9090 with HTTP 200 verified.
- Physical recovery access complete.
- Manual application rollback from the active ASTH v0.4.0 file to the retained v0.3.0 file, followed by restoration to the original v0.4.0 file, was verified on 13 August 2026. Both service restarts succeeded; rollback and final health checks returned HTTP 200 and `healthy` at the expected versions.
- The Raspberry Pi display stack was recovered by enabling `dtoverlay=vc4-kms-v3d`; after reboot the expected `/dev/dri` devices and `vc4`/`v3d` modules were present. After creating the missing `/etc/X11/xorg.conf.d` directory with root ownership and mode `755`, `rp1-test.service` became active. Final checks showed zero failed units, active `asth.service`, and healthy ASTH v0.4.0 over HTTP 200.

## Partial

- Learning Hub contains placeholder sections for modules, training videos and interactive exercises.
- Uptime Kuma and Cockpit are available as linked supporting services; advanced monitoring, alerting and security completion is not claimed.
- Retained application-file copies, including the pre-test v0.4.0 safety copy, are present on the microSD filesystem.
- Database backup/restore is deferred, not passed or failed: `/var/lib/asth/db` exists but is empty, the current application has no database file or reference, and `/etc/asth/asth.env` has no `KEY=value` configuration.

## Pending

- Project team names and roles.
- Final system custodian and maintenance window.
- Competition submission requirements.
- Confirmed source modules and SOP.
- GitHub repository owner and name.
- Install compatible casing/LCD hardware; the MHS35 LCD is not installed, and the previously cloned LCD-show repository was not used to run `MHS35-show` during display recovery.
- Install the NVMe controller/HAT after it arrives; the system still boots from the 32 GB microSD, while the external 512 GB ROG SSD remains `/dev/sda` and mounted at `/mnt/rog`.
- Test NVMe, decide the migration method and retain the microSD as recovery media if full OS migration succeeds.
- Configure LCD kiosk mode for `/`.
- Populate and validate Learning Hub content.
- Perform database backup/restore testing only after a database-backed module exists.
- Perform final post-assembly validation after the casing, NVMe and LCD are installed.
- Revalidate Alfa `wlan1` as the wireless uplink with Ethernet removed after the 5 GHz hotspot migration. The 25 July portable-mode evidence remains historical; `wlan1` was disconnected and not tested on 13 August.
- Commit the deployed v0.4.0 source into this repository later.
