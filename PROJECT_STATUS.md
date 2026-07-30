# ASTH Project Status

**Status date:** 30 July 2026
**Deployed application version:** v0.4.0
**Current phase:** Raspberry Pi integration and Learning Hub content preparation
**Overall status:** Active — operational foundation, partial learning experience
**Primary next action:** Complete the integrated casing/LCD assembly and test the NVMe without disturbing the working microSD deployment.

## Completed

- Project principles, charter, executive summary, MVP scope, roadmap and README drafted.
- Raspberry Pi 5 with 2 GB RAM operational from a 32 GB microSD card.
- HDMI display, USB keyboard, local `asthadmin` login, boot-recovery password recovery and `sudo` (`SUDO_OK`) verified; the Pi rebooted normally afterward.
- ASTH portable network operational on `wlan0` at `10.42.0.1/24`; a connected phone reached the ASTH health endpoint and internet forwarding through `eth0` succeeded.
- Main landing page at `/`, Learning Hub shell at `/learn/`, `/health` and live `/api/hub-status` endpoint operational.
- v0.4.0 syntax validation, service restart and visual landing-page check completed on the Pi.
- Zero failed systemd units, healthy/running local ASTH health, persistent `/mnt/rog`, active `smbd`, Uptime Kuma HTTP 200 after redirect and Cockpit listening on port 9090 with HTTP 200 verified.
- Physical recovery access complete.

## Partial

- Learning Hub contains placeholder sections for modules, training videos and interactive exercises.
- Uptime Kuma and Cockpit are available as linked supporting services; advanced monitoring, alerting and security completion is not claimed.
- Two application backups are present on the microSD filesystem.

## Pending

- Project team names and roles.
- Final system custodian and maintenance window.
- Competition submission requirements.
- Confirmed source modules and SOP.
- GitHub repository owner and name.
- Complete the integrated casing/LCD assembly and install the NVMe base/HAT and SSD.
- Test NVMe, decide the migration method and retain the microSD as recovery media if full OS migration succeeds.
- Configure LCD kiosk mode for `/`.
- Populate and validate Learning Hub content.
- Perform database backup/restore testing and application rollback testing.
- Perform final post-assembly validation after the casing, NVMe and LCD are installed.
- Commit the deployed v0.4.0 source into this repository later.
