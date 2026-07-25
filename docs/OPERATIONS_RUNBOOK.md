# ASTH Raspberry Pi 5 Operations Runbook

This runbook covers the validated lightweight infrastructure on `asth-pi` as of 25 July 2026. It does not contain passwords, private keys, tokens, environment-file contents or application secrets.

## Safety rules

- Run observation commands before state-changing commands.
- Commands labelled **sudo required** change or inspect privileged system state.
- Keep a working SSH session open during remote maintenance.
- Use a local console for SSH or firewall recovery.
- Do not edit or display `/etc/asth/asth.env` during routine checks.
- Do not assume `/media/asthadmin/ROG` is mounted; it is currently a non-persistent desktop automount.
- Stop if the current IP, path, service name, mount or release layout differs from this runbook.
- No disk-formatting, partitioning or filesystem-creation commands are included.

## Current operational values

| Item | Value |
|---|---|
| Hostname | `asth-pi` |
| Current LAN IP | `192.168.100.187` |
| LAN subnet | `192.168.100.0/24` |
| Administrator | `asthadmin` |
| Application service | `asth.service` |
| Application root | `/opt/asth` |
| Data directory | `/var/lib/asth` |
| SQLite directory | `/var/lib/asth/db` |
| Application logs | `/var/log/asth` and service journal |
| Environment file | `/etc/asth/asth.env` |
| Temporary SSD mount | `/media/asthadmin/ROG` |
| Backup directory | `/media/asthadmin/ROG/ASTH_BACKUP` |
| Configuration snapshot | `/media/asthadmin/ROG/ASTH_BACKUP/config-snapshot` |

The current IP may change until a DHCP reservation or another fixed-IP method is approved.

## SSH access

From an administrator workstation on `192.168.100.0/24`:

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
systemctl is-enabled asth.service nginx ssh
systemctl is-active asth.service nginx ssh
systemctl --failed --no-pager
```

Expected result: ASTH, Nginx and SSH are enabled and active; the failed-unit list is empty.

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
curl --fail --silent --show-error http://127.0.0.1/docs
```

From an approved LAN client:

```bash
curl --fail --silent --show-error http://192.168.100.187/health
```

Expected result: HTTP success for `/`, `/health` and `/docs` through Nginx. These checks prove minimal infrastructure availability only.

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
- port 80 allowed only from `192.168.100.0/24`; and
- no LAN rule exposing port 8000 or port 111.

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

Expected Uvicorn state: one worker process for the 2GB MVP.

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

Validated baseline: approximately 445 MiB RAM used, 1.5 GiB available and 26% root-disk use. Investigate sustained swap use, rapid log/data growth or root-disk use approaching 80%.

## External SSD verification

The SSD is not yet persistently mounted. Verify it before every backup or restore action:

```bash
findmnt /media/asthadmin/ROG
lsblk -f
findmnt -no SOURCE,FSTYPE,OPTIONS,TARGET /media/asthadmin/ROG

df -h /media/asthadmin/ROG
test -d /media/asthadmin/ROG/ASTH_BACKUP
```

Expected result: the mount source identifies the external SSD, filesystem is NTFS, capacity is approximately 512GB, and the backup directory exists.

Stop immediately if `findmnt` returns no mount, the source is unexpected, the path resolves to the microSD filesystem, the mount is read-only unexpectedly or available space is insufficient. Never allow a backup job to write into an unmounted `/media/asthadmin/ROG` directory on the root filesystem.

## Backup verification

List backup metadata without reading secret contents:

```bash
find /media/asthadmin/ROG/ASTH_BACKUP -maxdepth 2 -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\n'
du -sh /media/asthadmin/ROG/ASTH_BACKUP
```

Calculate a SHA-256 checksum for a selected backup artifact:

```bash
sha256sum /media/asthadmin/ROG/ASTH_BACKUP/<confirmed-backup-file>
```

If an approved checksum manifest exists:

```bash
cd /media/asthadmin/ROG/ASTH_BACKUP
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
test -d /media/asthadmin/ROG/ASTH_BACKUP/config-snapshot
find /media/asthadmin/ROG/ASTH_BACKUP/config-snapshot -maxdepth 2 -printf '%y %TY-%Tm-%Td %TH:%TM %s %p\n'
```

If a trusted manifest exists:

```bash
cd /media/asthadmin/ROG/ASTH_BACKUP/config-snapshot
sha256sum --check <confirmed-configuration-manifest>
```

Do not use `cat`, `grep` or similar content commands on snapshots of `/etc/asth/asth.env`, private keys or other secret-bearing files. Verify those files by metadata/checksum only and restrict evidence to non-secret results.

## Controlled reboot

Pre-reboot checks:

```bash
systemctl --failed --no-pager
systemctl is-active asth.service nginx ssh
findmnt /media/asthadmin/ROG
sync
```

> **Warning — host-wide outage and non-persistent SSD mount:** Reboot disconnects SSH and stops all ASTH access. The SSD may not remount automatically. Use an approved maintenance window, notify users, keep local recovery access available and confirm no backup/restore is running.

Reboot — **sudo required**:

```bash
sudo systemctl reboot
```

After the Pi returns, reconnect and verify:

```bash
ssh asthadmin@192.168.100.187
systemctl is-active asth.service nginx ssh
systemctl --failed --no-pager
curl --fail --silent --show-error http://127.0.0.1/health
vcgencmd measure_temp
vcgencmd get_throttled
findmnt /media/asthadmin/ROG
```

A failed SSD `findmnt` check is expected until persistent UUID mounting is implemented; do not run backup automation in that state.

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