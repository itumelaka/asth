# ASTH Raspberry Pi 5 Operations Runbook

This runbook covers the operational ASTH Raspberry Pi hub and deployed FastAPI v0.4.0 application as of 26 July 2026. It does not contain passwords, private keys, tokens, environment-file contents or application secrets.

## Safety rules

- Run observation commands before state-changing commands.
- Commands labelled **sudo required** change or inspect privileged system state.
- Keep a working SSH session open during remote maintenance.
- Use a local console for SSH or firewall recovery.
- Do not edit or display `/etc/asth/asth.env` during routine checks.
- Confirm `/mnt/rog` is a real mount before storage, NAS, backup or restore work; never write to an unmounted mount-point directory.
- Stop if the current IP, path, service name, mount or release layout differs from this runbook.
- No disk-formatting, partitioning or filesystem-creation commands are included.
- Modify only the `/mnt/rog/ASTH` namespace; leave unrelated SSD contents unchanged.

## Current operational values

| Item | Value |
|---|---|
| Hostname | `asth-pi` |
| Office-LAN IP when `eth0` is connected | `192.168.100.187` |
| Office-LAN subnet | `192.168.100.0/24` |
| Portable SSID | `ASTH-PORTABLE` |
| Hotspot interface | Built-in Wi-Fi `wlan0` |
| Portable gateway/URL | `10.42.0.1/24`; `http://10.42.0.1` |
| Hotspot mode | 2.4 GHz (`bg`), channel 6, WPA-PSK, IPv4 shared |
| Hotspot autoconnect | Yes, priority 100 |
| Portable uplink | ALFA AWUS036NHV `wlan1`, `rtl8xxxu`, profile `PHONE-UPLINK` |
| Verified wlan1 address/route | `10.13.68.119/24`; `default via 10.13.68.67 dev wlan1` |
| Administrator | `asthadmin` |
| Application service | `asth.service` |
| Application root | `/opt/asth` |
| Deployed application file | `/opt/asth/app/main.py` |
| Static logo assets | `/var/www/asth-hub/assets/` |
| Deployed application version | `v0.4.0` |
| Application routes | `/`, `/learn/`, `/health`, `/api/hub-status` |
| Data directory | `/var/lib/asth` |
| SQLite directory | `/var/lib/asth/db` |
| Application logs | `/var/log/asth` and service journal |
| Environment file | `/etc/asth/asth.env` |
| Persistent SSD mount | `/mnt/rog` (`/dev/sda2`, UUID `8E5AAE985AAE7C99`, `ntfs3`) |
| Existing backup directory | `/mnt/rog/ASTH_BACKUP` |
| Configuration snapshot | `/mnt/rog/ASTH_BACKUP/config-snapshot` |
| Backend file backup | `/opt/asth/app/main.py.backup-20260726` |
| Previous 3D Clay UI backup | `/opt/asth/app/main.py.backup-clay-service-hub-20260726` |
| ASTH storage namespace | `/mnt/rog/ASTH` |
| Samba service | `smbd`; authenticated shares; SMB1 disabled |
| Cockpit URLs | `https://192.168.100.187:9090`; `https://10.42.0.1:9090` |

The Ethernet IP may change until a DHCP reservation or another fixed-IP method is approved. The portable hotspot gateway remains `10.42.0.1` under the verified shared-mode connection.

## Deployed application checks

The deployed source of record on the Pi is currently `/opt/asth/app/main.py`. The repository does not yet contain the confirmed v0.4.0 source, so do not use a repository file to overwrite the Pi until a controlled source synchronisation and comparison is completed.

Read-only syntax validation:

```bash
python3 -m py_compile /opt/asth/app/main.py
```

The command passed on 26 July 2026. It creates or refreshes Python bytecode cache metadata but does not restart the service.

Restart only after syntax validation and an approved change — **sudo required; brief interruption**:

```bash
sudo systemctl restart asth
```

After restart, verify:

```bash
systemctl is-active asth
curl --fail --silent --show-error http://127.0.0.1/health
curl --fail --silent --show-error http://127.0.0.1/api/hub-status
```

Open `/` in a browser for visual validation. Confirm the logos, hub state, device count, transfer rates and totals, uptime, Wi-Fi information, graph and service links. Open `/learn/` separately and confirm it has no network graph. Do not treat placeholder learning sections as completed content.

The local application backups are on the microSD filesystem. Before any source replacement, verify their metadata without displaying or modifying their contents:

```bash
stat /opt/asth/app/main.py.backup-20260726
stat /opt/asth/app/main.py.backup-clay-service-hub-20260726
```

These same-device copies do not replace an off-device backup or restore test.

## Portable hotspot operation

### Participant operating steps

1. Power on the Raspberry Pi and wait for the system and `ASTH-PORTABLE` hotspot to start.
2. On the phone, tablet or laptop, connect to Wi-Fi network `ASTH-PORTABLE` using the hotspot credential provided separately by the authorized operator.
3. Open `http://10.42.0.1` in a browser.

Expected result: the ASTH v0.4.0 landing page loads with DVS/ASTH logos, hub state, connected-device count, transfer statistics, uptime, Wi-Fi information, a real-time network graph and links to Learning Hub, Uptime Kuma and Cockpit.

Choose the operating mode before the session:

| Mode | Uplink | Client result |
|---|---|---|
| Offline portable | No uplink | ASTH works locally; “connected without internet” is expected. |
| Online portable | Phone hotspot through `PHONE-UPLINK` on `wlan1` | ASTH and internet access are available. |
| Office LAN | Approved network through `eth0` | ASTH and office-LAN forwarding are available. |

The `ASTH-PORTABLE` client steps and local URL are the same in all three modes.

The hotspot password is managed separately and must never be written to this repository, command output captured for documentation, screenshots or support tickets.

### Hotspot verification

Read-only connection and interface checks:

```bash
nmcli connection show --active
nmcli device status
nmcli -f connection.id,connection.interface-name,connection.autoconnect,connection.autoconnect-priority,802-11-wireless.mode,802-11-wireless.band,802-11-wireless.channel,802-11-wireless-security.key-mgmt,ipv4.method connection show ASTH-PORTABLE
nmcli -f GENERAL.STATE,GENERAL.CONNECTION,IP4.ADDRESS device show wlan0
ip -brief address show wlan0
iw dev wlan0 info
```

Expected values:

- connection `ASTH-PORTABLE` active on `wlan0`;
- access-point mode;
- band `bg`, channel 6;
- WPA-PSK key management without displaying the password;
- IPv4 method `shared`;
- address `10.42.0.1/24`;
- autoconnect enabled with priority 100.

Verify local web access from the Pi:

```bash
curl --fail --silent --show-error http://10.42.0.1
curl --fail --silent --show-error http://10.42.0.1/api/hub-status
```

Verify from a connected client by opening `http://10.42.0.1`. DHCP was validated with one phone and one laptop.

Listener and firewall checks — **sudo required, read-only**:

```bash
sudo ss -lntup
sudo ufw status verbose
```

Expected hotspot boundary:

- Nginx HTTP port 80 is reachable through `wlan0`;
- DHCP UDP 67 is allowed on `wlan0`;
- DNS TCP/UDP 53 is allowed on `wlan0`;
- SSH TCP port 22 is allowed on `wlan0` only from source subnet `10.42.0.0/24`; and
- Uvicorn port 8000 is not directly exposed.

### Hotspot troubleshooting

If the SSID is missing or a device does not receive an address, run:

```bash
nmcli connection show --active
nmcli device status
nmcli radio wifi
rfkill list wifi
ip -brief address show wlan0
iw dev wlan0 info
journalctl -u NetworkManager --since today --no-pager
```

Focus the NetworkManager log without displaying connection secrets:

```bash
journalctl -u NetworkManager --since today --no-pager | grep -Ei 'ASTH-PORTABLE|wlan0|dnsmasq|dhcp'
```

If `ASTH-PORTABLE` exists but is inactive, activating it changes network state and may interrupt other Wi-Fi use.

> **Warning — Wi-Fi state change:** Confirm that `wlan0` is the built-in hotspot interface and that no maintenance operation depends on it before activation.

Activation — **sudo required**:

```bash
sudo nmcli connection up ASTH-PORTABLE
```

Then repeat the interface, UFW and `curl` checks. Do not recreate the connection or change its WPA-PSK from an undocumented command.

If clients connect but the page does not load:

```bash
systemctl is-active asth.service nginx
curl --fail --silent --show-error http://127.0.0.1/health
curl --fail --silent --show-error http://10.42.0.1
curl --fail --silent --show-error http://10.42.0.1/api/hub-status
sudo nginx -t
sudo ufw status verbose
```

If the client says “connected without internet” but the local URL works, no repair is required for offline portable mode.

### Portable internet-router mode — verified

Verified architecture:

```text
Phone hotspot
  -> PHONE-UPLINK on wlan1
  -> Raspberry Pi forwarding/UFW
  -> wlan0 ASTH-PORTABLE
  -> laptop and other client devices
```

Verified interface and route state with Ethernet removed:

- `ASTH-PORTABLE` remained active on `wlan0` at `10.42.0.1/24`;
- `PHONE-UPLINK` remained active on `wlan1`;
- `wlan1` received `10.13.68.119/24`;
- default route became `default via 10.13.68.67 dev wlan1`;
- laptop internet access succeeded with 0% packet loss;
- local ASTH access at `http://10.42.0.1` succeeded; and
- `ssh asthadmin@10.42.0.1` succeeded.

`PHONE-UPLINK` credentials are stored only in local NetworkManager. Never request or display NetworkManager secrets, copy the connection profile into Git, or capture its credentials in logs/screenshots.

#### Startup steps for online portable mode

1. Power on the phone hotspot without disclosing its credential.
2. Power on the Raspberry Pi and wait for `ASTH-PORTABLE` to appear.
3. Confirm `PHONE-UPLINK` is active on `wlan1`.
4. Confirm the default route uses `wlan1`.
5. Connect client devices to `ASTH-PORTABLE`.
6. Open `http://10.42.0.1` and verify internet access separately.
7. For administration from the portable subnet, use `ssh asthadmin@10.42.0.1`.

#### Verify active connections and addresses

```bash
nmcli -f NAME,TYPE,DEVICE connection show --active
nmcli device status
ip -brief address show wlan0
ip -brief address show wlan1
```

Expected: `ASTH-PORTABLE` on `wlan0`, `PHONE-UPLINK` on `wlan1`, `10.42.0.1/24` on `wlan0`, and the current upstream address on `wlan1`. The verified upstream address was `10.13.68.119/24`, but a phone hotspot may issue a different address later.

#### Verify routes

```bash
ip route
ip route show default
ip route get 1.1.1.1
```

With Ethernet removed, the verified default route was:

```text
default via 10.13.68.67 dev wlan1
```

Stop troubleshooting assumptions if the default route uses another interface; first identify whether the intended mode is offline, online portable or office LAN.

#### Verify wlan1 internet

```bash
ping -I wlan1 -c 4 10.13.68.67
ping -I wlan1 -c 4 1.1.1.1
```

Expected during the verified test: successful replies and 0% packet loss. Failure to reach the phone gateway indicates an uplink/profile issue; gateway success with internet failure indicates an upstream phone/mobile-data issue.

#### Verify local ASTH and SSH through wlan0

```bash
curl --fail --silent --show-error http://10.42.0.1
curl --fail --silent --show-error http://10.42.0.1/api/hub-status
```

From a client connected to `ASTH-PORTABLE`:

```bash
ssh asthadmin@10.42.0.1
```

Expected result: the ASTH v0.4.0 landing page loads. Verify live data separately through `/api/hub-status` and confirm `/learn/` opens without a network graph.

SSH is allowed only from `10.42.0.0/24` to TCP port 22 on `wlan0`. It is not a general internet-facing SSH rule.

#### Verify forwarding and UFW boundary

**sudo required, read-only:**

```bash
sudo ufw status verbose
sudo sysctl net.ipv4.ip_forward
sudo iptables -S FORWARD
```

Conceptual forwarding boundary:

- allow `wlan0` to `wlan1` for online portable mode;
- retain `wlan0` to `eth0` for office-LAN mode;
- allow return traffic for established forwarded connections;
- allow hotspot DHCP/DNS and local HTTP on `wlan0`;
- allow SSH on `wlan0` only from `10.42.0.0/24`; and
- do not expose Uvicorn port 8000.

> **Warning — firewall and routing risk:** Do not modify UFW forwarding, NAT or SSH rules during routine checks. A mistake can remove client internet access or broaden administrative exposure. Use an approved change window and local recovery access.

#### Troubleshoot PHONE-UPLINK

```bash
nmcli -f NAME,TYPE,DEVICE connection show --active
nmcli device status
ip -brief address show wlan1
ip route show default
ping -I wlan1 -c 4 10.13.68.67
journalctl -u NetworkManager --since today --no-pager | grep -Ei 'PHONE-UPLINK|wlan1|dhcp|route'
```

If `PHONE-UPLINK` exists but is inactive, activation changes routing state.

> **Warning — uplink state change:** Confirm the phone hotspot is intended, Ethernet-dependent work is stopped, and the profile name is exactly `PHONE-UPLINK`.

Activation — **sudo required**:

```bash
sudo nmcli connection up PHONE-UPLINK
```

Do not recreate the profile or enter credentials from this runbook. If `PHONE-UPLINK` cannot connect, use offline portable mode: local ASTH at `10.42.0.1` remains the expected fallback.

#### Verify office-LAN mode

When `eth0` is connected to the approved office LAN:

```bash
ip -brief address show eth0
ip route show default
sudo ufw status verbose
sudo iptables -S FORWARD
```

Expected: the intended office route is selected and the retained `wlan0` to `eth0` forwarding policy is present. Do not assume office routing merely because the Ethernet link is up.

## Samba NAS access

Samba `4.22.10-Debian-4.22.10+dfsg-0+deb13u1` is enabled through `smbd`. Use the separately managed Samba account for `asthadmin`; do not use or record its password in commands, documentation or tickets.

| Share | Server path | Access |
|---|---|---|
| `ASTH-Public` | `/mnt/rog/ASTH/nas/public` | Authenticated read/write |
| `ASTH-Staff` | `/mnt/rog/ASTH/nas/staff` | Authenticated read/write |
| `ASTH-Uploads` | `/mnt/rog/ASTH/nas/uploads` | Authenticated read/write |
| `ROG-Drive` | `/mnt/rog` | Authenticated read-only by design |

### Access through the office LAN

1. Connect the Windows device to `192.168.100.0/24`.
2. In File Explorer, enter the exact UNC path `\\192.168.100.187\ASTH-Public`, `\\192.168.100.187\ASTH-Staff`, `\\192.168.100.187\ASTH-Uploads` or `\\192.168.100.187\ROG-Drive`.
3. Authenticate as `asthadmin` with the separately managed Samba credential.

### Access through ASTH-PORTABLE

1. Connect the Windows device to `ASTH-PORTABLE`.
2. In File Explorer, enter the exact UNC path `\\10.42.0.1\ASTH-Public`, `\\10.42.0.1\ASTH-Staff`, `\\10.42.0.1\ASTH-Uploads` or `\\10.42.0.1\ROG-Drive`.
3. Authenticate as `asthadmin` with the separately managed Samba credential.

Windows mapping and creation of `NAS-TEST.txt` were verified on `\\192.168.100.187\ASTH-Public`. `ROG-Drive` deliberately exposes the SSD read-only; `NT_STATUS_ACCESS_DENIED` on an attempted write is the expected result, not a fault.

Read-only server verification:

```bash
systemctl is-active smbd
smbclient -L localhost -U asthadmin
```

The `smbclient` command prompts interactively; never put the password on the command line. Expect `ASTH-Public`, `ASTH-Staff`, `ASTH-Uploads` and `ROG-Drive`, and no SMB1 requirement.

### Samba troubleshooting

Use the complete UNC path, including the share name. `\\192.168.100.187` or `\\10.42.0.1` names the server; a valid share path ends in `\ASTH-Public`, `\ASTH-Staff`, `\ASTH-Uploads` or `\ROG-Drive`.

Windows can cache a different username or an old Samba password for the same server. If authentication fails unexpectedly, close mappings and File Explorer sessions for that server, remove only the matching saved entry for `192.168.100.187` or `10.42.0.1` in Windows Credential Manager, then reconnect as `asthadmin`. Do not record the replacement password.

If a read/write share fails, verify the mount and `smbd` first. If only `ROG-Drive` rejects writes, no repair is required because that share is intentionally read-only.

## Cockpit web console

Cockpit from the Debian Trixie package set includes `cockpit-system`, `cockpit-networkmanager`, `cockpit-packagekit` and `cockpit-storaged`. It provides Overview, Logs, Storage, Networking, Accounts, Services, Applications, Software Updates and Terminal.

### Access through the office LAN

1. Connect the administrator device to `192.168.100.0/24`.
2. Open `https://192.168.100.187:9090`.
3. Accept the expected local self-signed certificate warning only after confirming the address is the ASTH Pi.
4. Sign in with the Linux account `asthadmin` and its Linux credential, not the Samba password.

### Access through ASTH-PORTABLE

1. Connect the administrator device to `ASTH-PORTABLE`.
2. Open `https://10.42.0.1:9090`.
3. Accept the same expected local self-signed certificate warning after confirming the address.
4. Sign in with the Linux account `asthadmin`.

Read-only verification:

```bash
systemctl is-active cockpit.socket
ss -lnt | grep -E 'LISTEN.+:9090\b'
```

Expected result: `cockpit.socket` is active and TCP 9090 is listening. UFW permits it only from the office LAN and `10.42.0.0/24` on `wlan0`.

### Cockpit troubleshooting

The browser warning is expected because this local deployment uses a self-signed certificate. A different host/address or an unexpectedly changed certificate still requires investigation.

A normal login may initially show limited access. Use Cockpit's administrative-access control when a privileged task is authorized; the verified deployment successfully enabled administrative access. Do not confuse limited-access mode with a failed login, and do not leave elevated access active longer than the maintenance task requires.

## SSH access

From a client connected to `ASTH-PORTABLE` (`10.42.0.0/24`):

```bash
ssh asthadmin@10.42.0.1
```

This portable SSH path was verified. UFW restricts it to TCP port 22 on `wlan0` from `10.42.0.0/24`.

From an administrator workstation on the office LAN (`192.168.100.0/24`):

```bash
ssh asthadmin@192.168.100.187
```

Preferred after key enrollment:

```bash
ssh -o PreferredAuthentications=publickey asthadmin@192.168.100.187
```

Expected result: the server identity is `asth-pi`, and the named administrator reaches a shell without using root login.

Password authentication is temporarily enabled. Do not disable it until key authentication succeeds in a second session and local console recovery is confirmed.

## Service status

Read-only:

```bash
systemctl status asth.service --no-pager
systemctl status nginx --no-pager
systemctl status ssh --no-pager
systemctl status mnt-rog.mount smbd cockpit.socket --no-pager
systemctl is-enabled asth.service nginx ssh smbd cockpit.socket
systemctl is-active asth.service nginx ssh mnt-rog.mount smbd cockpit.socket
systemctl --failed --no-pager
```

Expected result: ASTH, Nginx, SSH, the SSD mount, Samba and Cockpit are active; enabled services/sockets are enabled; the failed-unit list is empty.

## Start, stop, restart and reload

### Start

**sudo required:**

```bash
sudo systemctl start asth.service
sudo systemctl start nginx
```

Run health checks after starting.

### Stop

> **Warning — service interruption:** Stopping ASTH makes application endpoints unavailable. Stopping Nginx removes all client-facing HTTP access. Confirm an approved maintenance window, notify users and record the pre-change state first.

**sudo required:**

```bash
sudo systemctl stop asth.service
sudo systemctl stop nginx
```

Recovery:

```bash
sudo systemctl start asth.service
sudo systemctl start nginx
```

### Restart

> **Warning — brief service interruption:** Restarting ASTH or Nginx can interrupt active requests. Use an approved maintenance window for planned work.

**sudo required:**

```bash
sudo systemctl restart asth.service
sudo systemctl restart nginx
```

### Reload Nginx

Always test syntax before reload.

**sudo required:**

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Expected result: `nginx -t` reports successful syntax and the reload completes without stopping Nginx.

No ASTH reload action is documented. Use a controlled restart only when required.

## Health checks

From the Pi, direct Uvicorn loopback check:

```bash
curl --fail --silent --show-error http://127.0.0.1:8000/health
```

From the Pi through Nginx:

```bash
curl --fail --silent --show-error http://127.0.0.1/health
curl --fail --silent --show-error http://127.0.0.1/
curl --fail --silent --show-error http://127.0.0.1/learn/
curl --fail --silent --show-error http://127.0.0.1/api/hub-status
```

From an approved LAN client:

```bash
curl --fail --silent --show-error http://192.168.100.187/health
```

Expected result: HTTP success for `/`, `/learn/`, `/health` and `/api/hub-status` through the deployed client-facing service. These checks prove route availability. They do not prove populated learning content, final LCD kiosk operation, NVMe migration or complete MVP acceptance.

Confirm Uvicorn is not LAN-facing:

```bash
ss -lntp
```

Expected listener boundary: Nginx on port 80 and Uvicorn on `127.0.0.1:8000`, not `0.0.0.0:8000` or `192.168.100.187:8000`.

## Nginx syntax test

**sudo required:**

```bash
sudo nginx -t
```

Do not reload or restart Nginx if this check fails. Preserve the running known-good process, inspect the reported file/line and correct the configuration through the approved change process.

## systemd verification

Read-only unit identity and runtime properties:

```bash
systemctl cat asth.service
systemctl show asth.service -p User -p Group -p MainPID -p NRestarts -p ActiveState -p SubState -p EnvironmentFiles
```

Do not use `systemctl show -p Environment`; it may expose environment values.

Unit verification — **sudo required**:

```bash
sudo systemd-analyze verify /etc/systemd/system/asth.service
```

If the unit is stored elsewhere, obtain its fragment path first:

```bash
systemctl show asth.service -p FragmentPath
```

## Application logs

Service journal, read-only:

```bash
journalctl -u asth.service --since today --no-pager
journalctl -u asth.service -n 100 --no-pager
```

Follow live logs; exit with `Ctrl+C`:

```bash
journalctl -u asth.service -f
```

Application log-directory metadata — **sudo required**:

```bash
sudo find /var/log/asth -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\n'
```

To inspect a confirmed non-secret log file — **sudo required**:

```bash
sudo tail -n 100 /var/log/asth/<confirmed-log-file>
```

Stop if logs contain passwords, tokens, cookies, environment values or unnecessary personal data. Do not paste sensitive log lines into tickets or documentation.

## Nginx logs

**sudo required:**

```bash
sudo tail -n 100 /var/log/nginx/access.log
sudo tail -n 100 /var/log/nginx/error.log
```

Follow the error log; exit with `Ctrl+C`:

```bash
sudo tail -f /var/log/nginx/error.log
```

Check logrotate configuration without forcing rotation:

```bash
sudo logrotate --debug /etc/logrotate.conf
```

## UFW status

**sudo required, read-only:**

```bash
sudo ufw status verbose
sudo ufw status numbered
```

Expected policy and rules:

- incoming deny;
- outgoing allow;
- port 22 allowed only from `192.168.100.0/24`;
- port 80 allowed from `192.168.100.0/24` and through `wlan0`;
- DHCP UDP 67 and DNS TCP/UDP 53 allowed on `wlan0`;
- SSH TCP port 22 on `wlan0` allowed only from `10.42.0.0/24`;
- Samba is allowed only from `192.168.100.0/24` and `10.42.0.0/24` on `wlan0`;
- Cockpit TCP 9090 is allowed only from `192.168.100.0/24` and `10.42.0.0/24` on `wlan0`; and
- no exposure of port 8000 or port 111.

> **Warning — firewall lockout risk:** Do not add, delete, reset, disable or reload firewall rules without local console access, an existing SSH session, the approved source subnet and a tested rollback. This runbook intentionally provides no firewall-change command.

## Resource monitoring

One-time process and load view:

```bash
uptime
top
ps -eo pid,user,%cpu,%mem,rss,cmd --sort=-rss | head -n 20
```

Continuous virtual-memory view; exit with `Ctrl+C`:

```bash
vmstat 1
```

Service resource state:

```bash
systemctl show asth.service -p MainPID -p NRestarts -p MemoryCurrent -p CPUUsageNSec
pgrep -a -f uvicorn
```

Record the current application process count and compare it with the installed service definition; do not infer completion from RAM capacity alone.

## Temperature and throttling

```bash
vcgencmd measure_temp
vcgencmd get_throttled
```

Validated baseline: approximately 45.5 C and `throttled=0x0`.

Stop workload escalation and investigate cooling/power if temperature rises abnormally, throttling becomes nonzero or kernel logs show power/thermal warnings.

## Disk and memory checks

```bash
free -h
swapon --show
df -h /
df -i /
du -sh /opt/asth /var/lib/asth /var/log/asth
journalctl --disk-usage
```

The current confirmed hardware has 32 GB RAM and a 32 GB microSD system disk. Record fresh values after final casing, NVMe and LCD assembly; investigate sustained swap use, rapid log/data growth or root-disk use approaching 80%.

## External SSD verification

The existing NTFS filesystem on `/dev/sda2` is persistently mounted at `/mnt/rog` through `ntfs3`. It was not formatted or repartitioned. Verify it before storage, NAS, backup or restore work:

```bash
findmnt /mnt/rog
systemctl is-active mnt-rog.mount
lsblk -f
findmnt -no SOURCE,FSTYPE,OPTIONS,TARGET /mnt/rog
df -h /mnt/rog
test -d /mnt/rog/ASTH_BACKUP
test -d /mnt/rog/ASTH/nas/public
```

Expected result: source `/dev/sda2`, label `ROG`, UUID `8E5AAE985AAE7C99`, NTFS through driver `ntfs3`, target `/mnt/rog`, and active unit `mnt-rog.mount`. The `/etc/fstab` options are `uid=1000,gid=1000,umask=0022,nofail,x-systemd.device-timeout=10`. The verified capacity was approximately 477 GB total, 305 GB used and 173 GB available.

`findmnt --verify` produced 0 parse errors and 0 errors. One warning is expected because the on-disk type is reported as `ntfs` while the Linux driver name is `ntfs3`.

Stop immediately if `findmnt` returns no mount, the source/UUID is unexpected, the path resolves to the microSD filesystem, the mount is unexpectedly read-only or available space is insufficient. Never write into an unmounted `/mnt/rog` directory. Modify only `/mnt/rog/ASTH`; preserve unrelated contents outside that namespace.

## Backup verification

List backup metadata without reading secret contents:

```bash
find /mnt/rog/ASTH_BACKUP -maxdepth 2 -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\n'
du -sh /mnt/rog/ASTH_BACKUP
```

Calculate a SHA-256 checksum for a selected backup artifact:

```bash
sha256sum /mnt/rog/ASTH_BACKUP/<confirmed-backup-file>
```

If an approved checksum manifest exists:

```bash
cd /mnt/rog/ASTH_BACKUP
sha256sum --check <confirmed-checksum-manifest>
```

Expected result: every checked entry reports `OK`. Do not invent a manifest name or compare against an untrusted checksum.

Non-destructive comparison of a source tree and recovery copy:

```bash
rsync --archive --dry-run --checksum --itemize-changes <source-directory>/ <recovered-copy>/
```

Expected result: no differences for the scope under test. This is a dry run and does not copy or delete files.

## Configuration snapshot verification

Confirm the snapshot path and metadata:

```bash
test -d /mnt/rog/ASTH_BACKUP/config-snapshot
find /mnt/rog/ASTH_BACKUP/config-snapshot -maxdepth 2 -printf '%y %TY-%Tm-%Td %TH:%TM %s %p\n'
```

If a trusted manifest exists:

```bash
cd /mnt/rog/ASTH_BACKUP/config-snapshot
sha256sum --check <confirmed-configuration-manifest>
```

Do not use `cat`, `grep` or similar content commands on snapshots of `/etc/asth/asth.env`, private keys or other secret-bearing files. Verify those files by metadata/checksum only and restrict evidence to non-secret results.

## Controlled reboot

Pre-reboot checks:

```bash
systemctl --failed --no-pager
systemctl is-active asth.service nginx ssh
systemctl is-active mnt-rog.mount
systemctl is-active smbd
systemctl is-active cockpit.socket
findmnt /mnt/rog
sync
```

> **Warning — host-wide outage:** Reboot disconnects SSH, web, Samba and Cockpit access. Use an approved maintenance window, notify users, keep local recovery access available and confirm no backup/restore or NAS write is running.

Reboot — **sudo required**:

```bash
sudo systemctl reboot
```

After the Pi returns, reconnect and verify:

```bash
ssh asthadmin@192.168.100.187
findmnt /mnt/rog
systemctl is-active mnt-rog.mount
systemctl is-active smbd
smbclient -L localhost -U asthadmin
systemctl is-active cockpit.socket
ss -lnt | grep -E 'LISTEN.+:9090\b'
systemctl is-active asth.service
systemctl is-active nginx ssh
systemctl --failed --no-pager
curl --fail --silent --show-error http://127.0.0.1/health
nmcli connection show --active
ip -brief address show wlan0
curl --fail --silent --show-error http://10.42.0.1
curl --fail --silent --show-error http://10.42.0.1/api/hub-status
vcgencmd measure_temp
vcgencmd get_throttled
```

Expected after reboot: applicable storage and supporting services return, `asth.service` is active, the v0.4.0 landing page loads, `/health` succeeds and `/api/hub-status` returns live status data. Stop storage or NAS work if any required mount check fails.

## Basic rollback guidance

Rollback is not yet production-proven because a current/previous release layout, release identifiers, SQLite schema and schema compatibility record have not been confirmed.

### Read-only readiness checks

```bash
readlink -f /opt/asth/current
find /opt/asth/releases -mindepth 1 -maxdepth 1 -type d -printf '%f\n'
systemctl show asth.service -p FragmentPath -p WorkingDirectory -p ExecStart
```

If `/opt/asth/current` or `/opt/asth/releases` does not exist, stop and obtain the actual deployment layout. Do not create or switch symlinks based only on this runbook.

### Controlled application rollback prerequisites

- current and previous release IDs/checksums recorded;
- previous virtual environment complete;
- current configuration snapshot verified;
- pre-change SQLite backup verified off-device;
- schema compatibility decision recorded;
- approved maintenance window and technical owner present; and
- original symlink target recorded for forward recovery.

> **Warning — service interruption and release-link replacement:** A rollback stops ASTH and may replace the `/opt/asth/current` symlink. An incorrect target can prevent startup. Do not remove or replace a symlink until the exact release layout, original target and recovery action have been independently verified.

Stop ASTH only after prerequisites pass — **sudo required**:

```bash
sudo systemctl stop asth.service
```

At this stage, follow an approved release-specific rollback procedure. This runbook intentionally omits a symlink-removal or replacement command because the current release layout and previous-known-good release are not confirmed.

Recovery from a halted but unchanged release — **sudo required**:

```bash
sudo systemctl start asth.service
systemctl status asth.service --no-pager
curl --fail --silent --show-error http://127.0.0.1/health
```

> **Warning — database data-loss risk:** Never overwrite `/var/lib/asth/db`, copy a live SQLite file or restore a database while ASTH is running. Preserve the failed database, stop the service, verify the matching backup and schema, restore only through an approved recovery procedure, then run integrity and application checks.

Rollback is complete only after health, logs, one approved read, one approved write and any relevant media/database checks pass. Record the failed release, recovery point, operator, duration and evidence.
