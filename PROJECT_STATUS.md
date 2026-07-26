# ASTH Project Status

**Status date:** 26 July 2026
**Deployed application version:** v0.4.0
**Current phase:** Raspberry Pi integration and Learning Hub content preparation
**Overall status:** Active — operational foundation, partial learning experience
**Primary next action:** Receive and test the casing, NVMe hardware and LCD without disturbing the working microSD deployment.

## Completed

- Project principles, charter, executive summary, MVP scope, roadmap and README drafted.
- Raspberry Pi 5 with 32 GB RAM operational from a 32 GB microSD card.
- ASTH portable network operational.
- Main landing page at `/`, Learning Hub shell at `/learn/`, `/health` and live `/api/hub-status` endpoint operational.
- v0.4.0 syntax validation, service restart and visual landing-page check completed on the Pi.

## Partial

- Learning Hub contains placeholder sections for modules, training videos and interactive exercises.
- Uptime Kuma and Cockpit are available as linked supporting services; advanced monitoring, alerting and security completion is not claimed.
- Two application backups are present on the microSD filesystem.

## Pending

- Project team names and roles.
- Competition submission requirements.
- Confirmed source modules and SOP.
- GitHub repository owner and name.
- Receive and install the casing, NVMe base/HAT and SSD, LCD and suitable display cable.
- Test NVMe, decide the migration method and retain the microSD as recovery media if full OS migration succeeds.
- Configure LCD kiosk mode for `/`.
- Populate and validate Learning Hub content.
- Perform post-installation, backup and recovery testing.
- Commit the deployed v0.4.0 source into this repository later.
