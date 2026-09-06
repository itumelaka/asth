# ASTH Office Media and Jellyfin Integration

**Verification date:** 6 September 2026  
**Status:** Verified — tunnel and CIFS automount persistence passed reboot validation; Jellyfin media playback was subsequently validated

This document records the verified integration that makes office-hosted training media available to Jellyfin on the ASTH Raspberry Pi. It contains no passwords, keys, tokens, public WAN address, complete WireGuard configuration or credential-file contents.

## Architecture

```text
ASTH-PORTABLE clients (10.42.0.0/24)
    -> Raspberry Pi ASTH
    -> WireGuard interface asth-office
    -> Office LAN (192.168.1.0/24)
    -> ITUNAS (192.168.1.254)
    -> SMB3 share Movies
    -> /mnt/office-movies on the Pi
    -> Jellyfin library Movies ITUNAS
```

The WireGuard interface is `asth-office`, managed by `wg-quick@asth-office.service`. Split routing sends office-LAN traffic through the tunnel while normal Internet traffic uses the ordinary uplink. The tunnel and split route survived reboot. The office server `192.168.1.254` and its required services were reachable during validation; that server is a validation target for this integration, not a general tunnel-health probe.

## Office source and SMB access

| Item | Verified value |
|---|---|
| Windows server | `ITUNAS` (`192.168.1.254`) |
| Windows source folder | `D:\Movies` |
| SMB share | `\\192.168.1.254\Movies` |
| Protocol | Authenticated SMB3 |
| Active Directory domain | `myitu.local` |
| NetBIOS domain | `NETVN` |
| Service account | `ASTH-Jellyfin` |
| NTFS permission | `ReadAndExecute`, `Synchronize` |

The service-account password must never be recorded in this repository. An existing `Everyone` permission with `FullControl` was observed on the Windows source, but it was not changed as part of this work. The integration uses authenticated SMB3 rather than weakening SMB signing.

A guest `smbclient` listing worked during investigation, but a guest kernel CIFS mount failed SMB signature verification. That result was not used as a reason to weaken signing or deploy guest access. The final mount uses authenticated SMB3 and is intentionally read-only.

Jellyfin on the Windows Server was not configured or changed.

## Raspberry Pi mount

| Item | Verified value |
|---|---|
| Mount point | `/mnt/office-movies` |
| Filesystem/access | CIFS, SMB3, read-only |
| Credential file | `/etc/samba/credentials-office-movies` |
| Credential-file ownership/mode | `root:root`, `600` |
| Jellyfin Linux identity | UID `110`, GID `115` |
| File mode | `0444` |
| Directory mode | `0555` |
| Persistence | `/etc/fstab` |
| Mount behavior | `_netdev,nofail,x-systemd.automount` |
| Tunnel dependency | Mount is ordered after and requires `wg-quick@asth-office.service` |
| Generated unit | `mnt-office\x2dmovies.automount` |

The credential file contents must never be displayed, logged or committed. Its root-only ownership and mode protect the SMB service credential. The read-only mount prevents Jellyfin or an ASTH client from modifying the office source through this path.

The persistent mount and generated automount unit passed reboot validation. The tunnel dependency ensures the office-media mount is attempted only in the appropriate network ordering. `_netdev` marks it as a network filesystem, `nofail` prevents an unavailable office share from blocking normal boot, and `x-systemd.automount` defers connection until the path is accessed.

## Jellyfin configuration and access

| Item | Verified value |
|---|---|
| Raspberry Pi server name | `asth-media` |
| Jellyfin version observed | `10.11.11` |
| New library | `Movies ITUNAS` |
| New library folder | `/mnt/office-movies` |
| Existing local library | `/mnt/rog/Movies`, retained separately |
| Library scan schedule | Every 30 minutes |
| Portable URL | [http://10.42.0.1:8096](http://10.42.0.1:8096) |
| Home-LAN URL | [http://192.168.100.187:8096](http://192.168.100.187:8096) |

Keeping `Movies ITUNAS` separate from `/mnt/rog/Movies` makes the source and availability of each library clear. An initial full scan can generate temporary storage and metadata activity and may cause short playback buffering. Processes named `ffprobe` observed during validation were associated with library scanning.

## Playback validation

Jellyfin Media Player `1.12.0` on `BurnRogZ13` successfully played *Thor: Love and Thunder* from `Movies ITUNAS`. Jellyfin reported **Direct Play**, and no active `ffmpeg` transcoding process was observed during playback.

Direct Play is preferred because the Raspberry Pi has 2 GB RAM. Playback behavior still depends on client codec support, media format and concurrent workload; this verification establishes the observed title and client result rather than a guarantee for every media file.

## Reboot and operational verification

The following behavior was verified after reboot:

- `wg-quick@asth-office.service` returned and the `asth-office` split tunnel remained usable;
- the generated `mnt-office\x2dmovies.automount` unit was available;
- `/mnt/office-movies` mounted read-only through authenticated SMB3 when accessed;
- Jellyfin `asth-media` could access the reboot-validated `/mnt/office-movies` mount after the `Movies ITUNAS` library was configured; and
- playback from the office library succeeded through an ASTH client.

If office media is temporarily unavailable, check the tunnel service, interface, office route, automount unit and read-only mount state without printing credential contents. Do not replace these checks with routine active probes against `192.168.1.254`, weaken SMB signing, enable guest mounting, or grant write access merely to clear an availability error.

## Security boundaries

- Never record passwords, API keys, Jellyfin tokens, WireGuard private keys, pre-shared keys, public WAN addresses, QR codes or complete tunnel configuration.
- Never print or commit `/etc/samba/credentials-office-movies` contents.
- Keep the credential file owned by `root:root` with mode `600`.
- Keep the CIFS mount read-only with files exposed as `0444` and directories as `0555`.
- Preserve authenticated SMB3 and SMB signing requirements.
- Do not treat the observed `Everyone: FullControl` permission as approved hardening; it was observed and left unchanged.
- Keep Jellyfin on the Windows Server outside this integration; it was not configured or modified.
