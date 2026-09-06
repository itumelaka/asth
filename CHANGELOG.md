# Changelog

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
