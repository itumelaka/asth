# ASTH Remote Access with Tailscale

**Verification date:** 6 September 2026  
**Status:** Remote ASTH and Jellyfin access verified; least-privilege access-policy hardening remains partial

This document records the verified private remote-access path to ASTH. It contains no Tailscale authentication URL, account email address, token, API key, device key, Jellyfin token, password, WireGuard key, pre-shared key or public WAN address.

## Purpose

Tailscale gives trusted remote clients private overlay-network access to services hosted by the ASTH Raspberry Pi. It does not publish ASTH directly to the public Internet and does not replace normal service authentication.

Tailscale and `asth-office` are separate tunnels with separate purposes:

- **Tailscale:** trusted remote client access to ASTH services on the Pi.
- **`asth-office` WireGuard:** Pi-to-office connectivity for the office LAN and office-hosted media.

The local portable network remains `ASTH-PORTABLE` (`10.42.0.0/24`). The separate `asth-office` tunnel carries the Pi's office-bound traffic to the office LAN (`192.168.1.0/24`).

## Architecture

Remote access to local ASTH services follows this path:

```text
Phone on 4G/5G
    -> Tailscale private network
    -> Raspberry Pi ASTH (asth-pi)
    -> ASTH local services
```

Office-hosted Jellyfin media follows both tunnels for different parts of the path:

```text
Phone on 4G/5G
    -> Tailscale
    -> Raspberry Pi ASTH / Jellyfin asth-media
    -> /mnt/office-movies
    -> existing asth-office WireGuard tunnel
    -> ITUNAS office SMB source
```

The office-media mount and Jellyfin integration are documented separately in [Office Media and Jellyfin Integration](OFFICE_MEDIA_JELLYFIN.md).

## Installation state

| Item | Verified value |
|---|---|
| Installation source | Official Tailscale repository for Debian 13 Trixie |
| Observed version | `1.102.3` |
| Service | `tailscaled.service` active |
| Tailscale device name | `asth-pi` |
| Observed Tailscale IPv4 | `100.87.140.5` |

No public port forwarding was configured for this Tailscale remote-access path. The overlay address is a private Tailscale address and must not be described as direct public exposure.

## Verified remote ASTH access

An Android phone disconnected from ASTH Wi-Fi and using cellular/mobile data successfully connected through Tailscale. The phone loaded the ASTH Service Hub through the Pi Tailscale address. The ASTH HUD remained operational and displayed **Office Tunnel: Connected** during this test.

This validates private remote access from that trusted Tailscale client. It does not claim anonymous access, direct public Internet availability or availability from devices outside the applicable Tailscale policy.

## Verified remote Jellyfin access

Jellyfin remains hosted by the Raspberry Pi as server `asth-media`; the observed version was `10.11.11`.

The initial remote API request failed because `/etc/jellyfin/network.xml` showed `EnableRemoteAccess=false`.

Remote Access was enabled through the Jellyfin user interface. After Jellyfin restarted, the setting was observed as `EnableRemoteAccess=true`.

From the cellular-connected phone through Tailscale, `http://100.87.140.5:8096/System/Info/Public` returned the expected `asth-media` / Jellyfin `10.11.11` public server information. The Jellyfin web interface then loaded remotely, and the `Movies ITUNAS` library was visible.

This was authenticated Jellyfin use over the private overlay. It does not make Jellyfin publicly Internet-accessible. No Jellyfin API key, session token, password or authentication detail is recorded here. Jellyfin must remain authenticated.

## Relationship with office media

Tailscale terminates remote client access at the Pi. When Jellyfin reads a title from `Movies ITUNAS`, the Pi accesses the read-only `/mnt/office-movies` CIFS mount through the existing `asth-office` WireGuard tunnel to the `ITUNAS` SMB source.

The two tunnels therefore have independent roles and failure modes. A working Tailscale connection does not prove that the office tunnel or SMB source is available. Conversely, a working office-media mount does not provide a remote client with access to the Pi.

## Current Tailscale access policy

A specific general-access rule was created with:

| Policy element | Current value |
|---|---|
| Source | Owner/user identity; email address deliberately omitted |
| Destination | Pi Tailscale address `100.87.140.5` |
| Allowed ports | `22`, `80`, `3001`, `8096`, `9090` |

This restricted rule has not yet been validated as the sole active access path. A broad pre-existing/default rule still allows all users/devices to reach all users/devices on all ports and protocols. The broad rule has not been deleted or disabled.

The access-policy state is therefore **PARTIAL / PENDING HARDENING**, not verified complete. Uptime Kuma, Cockpit and SSH have not been fully revalidated under only the restricted rule because the broad rule remains active.

## UFW and listener observations

- UFW remained active during this phase.
- Existing UFW rules continued to restrict normal LAN/portable access for ASTH HTTP, SSH, Jellyfin, Uptime Kuma, Cockpit and Samba.
- Services were observed listening on ports `80`, `8096`, `9090` and `3001`.
- No UFW rule for `tailscale0` was added.
- UFW hardening specifically for Tailscale is not claimed complete.

Tailscale policy and host firewall behavior are distinct controls. The successful test does not establish that every service or port has the intended final defense-in-depth policy.

## Security boundaries

- Do not record authentication URLs, account email addresses, passwords, API keys, session tokens, device keys, WireGuard keys, pre-shared keys, QR codes or public WAN addresses.
- Do not paste complete Tailscale, Jellyfin or WireGuard configuration into documentation or logs.
- Keep Jellyfin authenticated.
- Keep the office SMB mount authenticated and read-only; do not weaken SMB signing or WireGuard security for remote access.
- Do not configure public port forwarding for ASTH services as a substitute for Tailscale.
- Do not describe the current broad Tailscale rule as least privilege or completed hardening.

## Troubleshooting boundaries

If remote ASTH access fails, distinguish these layers without exposing credentials:

1. Confirm the remote device is using cellular or another external network and is connected to the intended Tailscale network.
2. Confirm `tailscaled.service` is active and the Pi still has its expected Tailscale device identity/address. Sanitize diagnostic output before saving it because peer listings can contain identities or account information.
3. Confirm the relevant Pi service is locally active and listening on its expected port.
4. Review the active Tailscale access policy without copying owner email addresses, tokens or authentication material into evidence.
5. For Jellyfin, confirm Remote Access remains enabled and restart state is healthy; never include API keys or session data in diagnostic captures.
6. If only `Movies ITUNAS` fails, troubleshoot `/mnt/office-movies` and the separate `asth-office` path using [Office Media and Jellyfin Integration](OFFICE_MEDIA_JELLYFIN.md).

Do not troubleshoot by exposing a service publicly, weakening authentication, disabling SMB signing, printing credential files or pasting full configurations.

## Pending hardening checklist

- [x] Install Tailscale from the official Debian Trixie repository.
- [x] Confirm `tailscaled.service` is active.
- [x] Verify ASTH Service Hub access from an Android phone on cellular data.
- [x] Verify the ASTH HUD remains functional and reports the office tunnel state.
- [x] Enable and verify private remote Jellyfin access.
- [x] Confirm `Movies ITUNAS` is visible remotely.
- [x] Create the owner-specific rule for ports 22, 80, 3001, 8096 and 9090 on the Pi.
- [ ] Review and remove or disable the broad all-users/devices allow-all rule in a controlled session.
- [ ] Validate the restricted rule as the sole active remote-access path.
- [ ] Revalidate ASTH, Jellyfin, Uptime Kuma, Cockpit and SSH after broad-rule removal.
- [ ] Review whether explicit `tailscale0` UFW policy is required; no such rule exists today.
- [ ] Record the final least-privilege result without identities, credentials, tokens or public WAN details.
