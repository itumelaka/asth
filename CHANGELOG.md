# Changelog

## 2026-09-16 — Learning Hub Core v1 and field validation

- Deployed **Biosekuriti Asas Ladang** at `/learn/packs/biosekuriti/`, based on WIM `A014-006-3:2022-C08 — Laksana Sistem Biosekuriti Ladang Poltri`.
- Deployed **Pengendalian Telur Sajian & Telur Tetasan** at `/learn/packs/pengendalian-telur/`, based on WIM `A014-006-3:2022-C05 — Laksana Pengendalian Telur Poltri`.
- Confirmed Learning Hub Core v1 now has three live packs, including **Persediaan Reban & Brooder** at `/learn/packs/reban-brooder/`.
- Verified a participant phone could remain connected to `ASTH-PORTABLE` while reporting no Internet access, open `http://10.42.0.1/` and use the Learning Hub locally. No captive-portal auto-launch claim is made.
- Verified a UGREEN powerbank powered a spare Raspberry Pi 5 through boot, LAN/SSH operation and a 120-second four-core `stress-ng` test with `throttled=0x0` before and after and a post-test temperature of 55.4 C.
- Verified the main ASTH Pi booted to desktop from the UGREEN powerbank, retained `throttled=0x0`, ran `asth.service`, returned HTTP 200 for `/learn/` and served the Learning Hub through `ASTH-PORTABLE`.
- Kept the power evidence bounded: no long-duration runtime or full-load certification is claimed, and the `DC 12V 2A` monitor still requires a separate suitable power solution.
- Verified Jellyfin active and two concurrent devices playing ITUNAS media smoothly through WireGuard `asth-office`; average receive throughput during the validated test was approximately 64.51 Mbps. This is not a maximum-throughput or reliable-4K claim; 1080p remains the practical content target.
- Updated **Manual Penggunaan ASTH v1.2**, **Poster Konsep Operasi v1.2** and **Learning Hub infographic v1.2**. Other still-current infographics were unchanged, and final NTRIC competition materials remain pending.

## 16 September 2026 — ITUNAS live deployment and production verification

- Deployed the exact-match CIFS/autofs parser correction to the Raspberry Pi; `asth.service` restarted successfully and remained active/running.
- Verified the dashboard loaded and `/api/hub-status` returned HTTP 200, with WireGuard and ITUNAS Media initially `CONNECTED`.
- Verified **DISCONNECT ITUNAS** from the local touchscreen changed ITUNAS Media to `DISCONNECTED` and changed the control to **CONNECT ITUNAS**.
- Verified **CONNECT ITUNAS** restored ITUNAS Media to `CONNECTED`.
- Confirmed WireGuard remained `CONNECTED` throughout both actions, proving the dashboard mutates only the fixed ITUNAS mount/automount units and does not mutate WireGuard.
- Preserved the earlier pending-deployment entry below as historical context for the state before production verification.

## 16 September 2026 — Current prototype scope and operations documentation

- Reframed ASTH as a portable, offline-first Raspberry Pi 5 training-delivery hub and explicitly separated it from SPDK course and participant administration.
- Documented the live 1024x600 kiosk Health Console, `ASTH-PORTABLE` participant hotspot, offline portal QR flow, Bluetooth input/audio peripherals and current microSD/USB-storage platform.
- Recorded local media at `/mnt/rog` and read-only ITUNAS media at `/mnt/office-movies`, including the rule that dashboard controls mutate only the fixed mount/automount units and never WireGuard.
- Documented the narrowly scoped `asthadmin` mutation path through `/usr/bin/sudo -n /usr/bin/systemctl`, fixed-unit allowlist and loopback/local endpoint restriction.
- Marked the exact-CIFS ITUNAS status correction as prepared and tested locally but still pending Raspberry Pi deployment and production verification.
- Added LIVE, VERIFIED, PENDING and FUTURE classifications, retained useful historical verification records, and clarified the Learning Hub roadmap. Documentation only; no deployment or system configuration change is claimed.

## 6 September 2026 — Tailscale remote access for ASTH and Jellyfin

- **VERIFIED:** Installed Tailscale 1.102.3 from the official Debian Trixie repository; `tailscaled.service` is active and the Pi appears as `asth-pi` at overlay IPv4 `100.87.140.5`.
- **VERIFIED:** An Android phone on cellular data loaded the ASTH Service Hub through Tailscale. The HUD remained operational and displayed Office Tunnel as Connected; no ASTH service was intentionally exposed directly to the public Internet.
- **VERIFIED:** Enabled Jellyfin Remote Access through its UI after the disabled setting blocked the initial remote API request. After restart, `asth-media` 10.11.11, its web interface and `Movies ITUNAS` were accessible through Tailscale.
- **OBSERVED:** UFW remained active, the existing LAN/portable rules remained in place, and services listened on ports 80, 3001, 8096 and 9090. No `tailscale0` UFW rule was added in this phase.
- **PARTIAL / PENDING HARDENING:** Added an owner-specific Tailscale rule for the Pi on ports 22, 80, 3001, 8096 and 9090, but the broad pre-existing all-users/devices allow-all rule remains active. It has not been removed, and the restricted rule has not been validated as the sole access path.
- Kept Tailscale client access separate from the `asth-office` Pi-to-office WireGuard tunnel and recorded no authentication URLs, account email, credentials, keys, tokens or public WAN address.

## 6 September 2026 — Office WireGuard media integration and Jellyfin Direct Play

- Documented the reboot-persistent `asth-office` split tunnel between `ASTH-PORTABLE` (`10.42.0.0/24`) and the office LAN (`192.168.1.0/24`).
- Recorded authenticated SMB3 access to the `Movies` share on `ITUNAS` (`192.168.1.254`), mounted read-only at `/mnt/office-movies` with protected root-only credentials and Jellyfin-compatible ownership/modes.
- Recorded the persistent `_netdev,nofail,x-systemd.automount` setup ordered and required after `wg-quick@asth-office.service`, including successful reboot validation of `mnt-office\x2dmovies.automount`.
- Added the Jellyfin library `Movies ITUNAS` while preserving `/mnt/rog/Movies` as a separate library. Jellyfin on the Windows server was not configured or changed.
- Verified Jellyfin Media Player 1.12.0 on `BurnRogZ13` playing *Thor: Love and Thunder* by Direct Play, with no active `ffmpeg` transcoding process; observed `ffprobe` processes were library scanning.
- Documented the 30-minute media scan schedule, possible temporary buffering during an initial full scan, the 2 GB Pi preference for Direct Play, and the decision to retain authenticated, signed SMB3 rather than weaken SMB security.

## 6 September 2026 — ROG SSD, Samba and auxiliary Jellyfin verification

- Recorded `/dev/sda2` (label `ROG`) persistently mounted at `/mnt/rog` using Linux `ntfs3`, uid/gid 1000 and the supplied runtime mount options after a full reboot.
- Updated Samba `ROG-Drive` to authenticated read/write at `/mnt/rog`, with `valid users` and `force user` set to `asthadmin`; Windows write/rename succeeded and `smbd` remained active after reboot.
- Documented enabled/running Jellyfin, listener `0.0.0.0:8096`, library `/mnt/rog/Movies`, LAN and ASTH-PORTABLE URLs, and subnet-limited UFW rules for TCP 8096.
- Recorded the validated official Open Subtitles plugin, Malay preference and observed 20-download/day allowance without account credentials; added naming and release-timing guidance.
- Added September reboot checks and kept Jellyfin auxiliary to the ASTH core MVP, with a 2 GB RAM warning against heavy transcoding or many concurrent streams.
- Preserved dated July/August evidence, including former storage/share behavior, without treating unrelated application, backup or hardware work as newly complete. Documentation only; no host configuration changes.

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
