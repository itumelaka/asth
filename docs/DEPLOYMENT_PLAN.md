# ASTH Lightweight MVP Raspberry Pi Deployment Plan

> **Status:** Planning reference reconciled with the deployed state through 13 August 2026. Actual status is tracked in [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md) and checklist evidence in [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md).

## Implemented State — through 13 August 2026

- **CONFIRMED:** Raspberry Pi 5 with 2 GB RAM is operational and currently boots Raspberry Pi OS from a 32 GB microSD card.
- **CONFIRMED:** HDMI display, USB keyboard, local `asthadmin` login, boot-recovery password recovery, `sudo` (`SUDO_OK`) and normal reboot passed; physical recovery access is complete.
- **CONFIRMED:** The ASTH portable network is operational; current Pi address observed is `192.168.100.187`.
- **CONFIRMED:** `ASTH-PORTABLE` is active on `wlan0` at `10.42.0.1/24`; a connected phone reached ASTH health and received forwarded internet through `eth0`.
- **CONFIRMED:** FastAPI v0.4.0 is deployed at `/opt/asth/app/main.py`; static logo assets are under `/var/www/asth-hub/assets/`.
- **CONFIRMED:** `/` is the live hub landing page, `/learn/` is the separate Learning Hub, `/health` remains available and `/api/hub-status` supplies live dashboard data.
- **CONFIRMED:** Syntax validation passed, the `asth` service restarted successfully and the landing page was visually confirmed.
- **PARTIAL:** Learning Hub sections are placeholders; actual modules, PDFs, videos and interactive content are not populated.
- **CONFIRMED:** Post-reboot checks found zero failed systemd units, healthy/running ASTH health, `/mnt/rog` mounted and `smbd` active.
- **CONFIRMED:** Uptime Kuma returned HTTP 200 after redirect; Cockpit listened on port 9090 and returned HTTP 200.
- **VERIFIED:** Manual application-file rollback from v0.4.0 to v0.3.0 and forward restoration to v0.4.0 passed checksum, service restart, HTTP 200, health and version checks.
- **VERIFIED:** Enabling `dtoverlay=vc4-kms-v3d` restored the expected DRI devices and `vc4`/`v3d` modules; after creating the missing Xorg configuration directory, `rp1-test.service` was active and final checks found zero failed units with healthy ASTH v0.4.0.
- **PENDING:** The MHS35 LCD is not installed and `MHS35-show` was not run; the NVMe controller/HAT has not arrived. The system remains on the 32 GB microSD.
- **PLANNED:** Prefer full-OS boot from NVMe after detection/testing, with the microSD retained as recovery media if migration succeeds.
- **PENDING:** The deployed v0.4.0 source must be committed to this repository later; it is not yet synchronised.
- **DEFERRED:** Database backup/restore has no pass/fail result because `/var/lib/asth/db` is empty and the current application has no database file/reference or `KEY=value` environment configuration.
- **PENDING:** The system custodian and maintenance window are not finalised.

The external 512 GB ROG USB SSD remains `/dev/sda`, with `/dev/sda2` mounted at `/mnt/rog`. It must not be confused with the pending NVMe controller/HAT.

## 1. Deployment Objectives

The initial deployment will provide a stable, lightweight ASTH MVP on one Raspberry Pi 5 for use inside a trusted local network. It should:

- start automatically after a normal boot;
- serve participant and trainer devices over Ethernet or Wi-Fi without requiring internet access;
- use Nginx as the only client-facing web server;
- run one FastAPI application through one Uvicorn worker;
- store MVP data in one local SQLite database;
- use the fewest practical background services;
- protect data with tested backups stored outside the microSD card;
- remain supportable through SSH; and
- fit within the current 2 GB RAM and 32 GB microSD baseline recorded in [HARDWARE_BASELINE.md](HARDWARE_BASELINE.md).

The initial request path will be:

`LAN client → Nginx :80 → Uvicorn 127.0.0.1:8000 → SQLite and local content`

Docker, container orchestration, microservices, public internet exposure, and a locally hosted large language model are outside the initial MVP. Containers may be reconsidered later if the Pi gains more RAM and SSD storage and they solve a demonstrated operational need.

## 2. Assumptions and Prerequisites

This plan assumes:

- a Raspberry Pi 5 with 2 GB RAM and a 32 GB microSD card;
- Raspberry Pi OS is already installed and boots successfully;
- a reliable USB-C power supply, preferably 5V/5A;
- active cooling and unobstructed airflow for sustained server use;
- administrative access to the Pi during initial setup;
- a router or access point serving the deployment LAN;
- temporary internet access during preparation for operating-system updates and package installation;
- the currently deployed FastAPI v0.4.0 file at `/opt/asth/app/main.py`, pending later repository synchronisation;
- application dependencies pinned in a project dependency file;
- no other service using TCP ports 80 or 8000; and
- a separate USB drive, NAS, or administrator workstation for off-device backups.

If Raspberry Pi OS Desktop is currently installed, it may remain installed for the first setup. After confirming remote administration, the desktop boot target and unused desktop services should be disabled only if they are not required for on-site support. Reinstallation with Raspberry Pi OS Lite 64-bit is an optimization, not an initial prerequisite.

Before implementation, record the installed OS release and architecture:

```bash
cat /etc/os-release
uname -m
```

The expected architecture is `aarch64` for a 64-bit installation. Package names and configuration paths must be rechecked if the installed OS differs from the current Raspberry Pi OS release.

## 3. Raspberry Pi Initial Preparation

Initial preparation should be performed with the Pi connected to stable power, active cooling, a display and keyboard if SSH is not yet proven, and preferably wired Ethernet.

1. Confirm the hardware and filesystem:

   ```bash
   cat /proc/device-tree/model
   free -h
   df -h /
   vcgencmd measure_temp
   ```

2. Confirm the system clock, time zone, and locale. The deployment time zone should match the operating site; for the current project context, `Asia/Kuala_Lumpur` is the proposed value:

   ```bash
   timedatectl
   sudo timedatectl set-timezone Asia/Kuala_Lumpur
   ```

3. Confirm adequate free storage before updating or copying a release. Keep at least 20% of the root filesystem free during normal operation.
4. Verify that cooling is working and check for power or thermal throttling:

   ```bash
   vcgencmd get_throttled
   ```

   A result of `0x0` indicates that no current or historical throttling flags are set.

5. If the graphical desktop is not required, plan a later change to the non-graphical boot target only after SSH access has been tested:

   ```bash
   sudo systemctl set-default multi-user.target
   ```

This command changes the next boot target and should not be used until remote recovery access is available.

## 4. Hostname, User Account and Network Planning

### Hostname

Use a short, unique hostname such as `asth-pi`:

```bash
sudo hostnamectl set-hostname asth-pi
```

The corresponding `/etc/hosts` entry should be checked so the local hostname resolves correctly. Clients may be able to use `http://asth-pi.local/` when multicast DNS is available, but deployment materials should also publish the Pi's reserved IPv4 address because `.local` resolution is not equally reliable on every client.

### Accounts

Use separate responsibilities:

- a named administrative account, such as `asth-admin`, for human SSH administration and controlled `sudo` access;
- a locked, non-login `asth` system account for the application service; and
- the existing bootstrap account only until the named administrator has been tested.

The application must not run as `root`, the Nginx user, or the human administrator. Each administrator should have an individual account where practical; accounts and SSH keys should not be shared.

### Network

Prefer Gigabit Ethernet for the Pi and use Wi-Fi for participant devices. Configure a DHCP reservation on the router for the Pi's Ethernet MAC address rather than hard-coding an address on the Pi. Proposed planning values are:

- hostname: `asth-pi`;
- service URL: `http://asth-pi.local/`;
- fallback URL: an address reserved by the site router, for example `http://192.168.10.20/`; and
- Uvicorn: loopback only at `127.0.0.1:8000`.

The example address must be replaced with an unused address in the site's actual subnet. Record the router, subnet, DHCP range, reserved address, DNS behavior, Wi-Fi SSID ownership, and expected client count in the site handover notes. Do not expose port 8000 to the LAN.

## 5. SSH and Remote Administration

Install and enable the Raspberry Pi OS SSH service during implementation if it is not already available. Administration should follow this order:

1. Create the named administrative account and give it a strong unique password for initial setup.
2. Add an administrator's public key to `~/.ssh/authorized_keys`.
3. Verify a new key-based SSH session before changing authentication settings.
4. Set `PermitRootLogin no`.
5. Set `PasswordAuthentication no` only after key login and an emergency access method have both been proven.
6. Restrict SSH to the trusted LAN with the host firewall.

Useful read-only checks are:

```bash
systemctl status ssh --no-pager
ss -lntp
```

Maintain at least one tested recovery path: local keyboard/display access or a documented method to mount and repair the microSD card from another machine. Avoid changing the SSH port merely as a substitute for access controls. Remote administration from outside the LAN is not part of this phase; use a properly managed VPN in a future phase rather than router port forwarding.

The local keyboard/display recovery path was confirmed on 30 July 2026 using HDMI and a USB keyboard. Local `asthadmin` login, boot-recovery password recovery, approved `sudo` access and a normal reboot all passed.

## 6. System Update and Essential Packages

During the implementation window, update package metadata and apply operating-system updates before installing ASTH:

```bash
sudo apt update
sudo apt full-upgrade
sudo reboot
```

After the reboot, install only the required packages:

```bash
sudo apt install --no-install-recommends nginx python3 python3-venv python3-pip git sqlite3 curl ca-certificates
```

`rsync` may be added for file-based backup transfer, and `ufw` may be added if it is selected as the host-firewall interface. Do not install a compiler toolchain unless a pinned Python dependency actually requires compilation. Record the OS version, package changes, and reboot in the deployment log.

Automatic security updates may be enabled after confirming they will not unexpectedly reboot during training. Reboots should be scheduled and tested rather than assumed.

## 7. Recommended ASTH Directory Structure

Use Linux filesystem conventions and keep code, configuration, mutable data, and backups separate:

```text
/opt/asth/
├── current -> /opt/asth/releases/<release-id>
└── releases/
    └── <release-id>/
        ├── asth/               # Application package
        ├── static/             # Versioned static assets
        ├── requirements.txt    # Pinned runtime dependencies
        └── .venv/              # Virtual environment for this release

/etc/asth/
└── asth.env                    # Runtime configuration and secrets

/var/lib/asth/
├── db/
│   └── asth.sqlite3
├── media/                      # Mutable uploaded or managed content
└── backup-staging/             # Short-lived local backup staging only

/var/log/asth/                  # Used only if file logging is later required
```

The deployment process should create a new immutable release directory, build its virtual environment, validate it, and then atomically update `/opt/asth/current`. Retain the current and immediately previous releases only. This layout supports rollback without keeping many duplicate environments on the 32GB card.

Ownership should be:

- release files: `root:asth`, not writable by the service account;
- `/etc/asth/asth.env`: `root:asth` with mode `0640`;
- `/var/lib/asth` and its contents: `asth:asth`;
- `/opt/asth` directories: not writable by the application; and
- Nginx: no access to the database or secrets file.

## 8. Python Virtual Environment Setup

Create one virtual environment inside each release. The planned implementation sequence for a prepared release directory is:

```bash
cd /opt/asth/releases/<release-id>
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --requirement requirements.txt
```

`<release-id>` represents a recorded version or commit identifier chosen during release preparation; it is not a literal directory name. Dependency versions should be pinned and tested on 64-bit Raspberry Pi OS before deployment. The service must call executables by their absolute paths and must not depend on shell activation.

Do not install ASTH Python dependencies globally and do not run `sudo pip`. Keep development and test-only packages out of the production dependency set. If dependency installation needs large temporary build files, build and verify the release before copying it to the Pi where practical.

## 9. FastAPI and Uvicorn Deployment Approach

The initial application process will:

- expose the FastAPI object as `asth.main:app`;
- run with one Uvicorn worker;
- bind only to `127.0.0.1:8000`;
- use the release virtual environment;
- send access and application output to standard output/error for journald;
- provide a lightweight unauthenticated health endpoint such as `/health` that reveals no sensitive details; and
- let Nginx serve cacheable static assets where the application build permits it.

The planned start command is:

```bash
/opt/asth/current/.venv/bin/uvicorn asth.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 1 \
  --proxy-headers \
  --forwarded-allow-ips 127.0.0.1
```

Uvicorn's development reload mode must not be used in production. Retain the currently validated process model until representative load and SQLite behaviour justify a controlled change. Increase concurrency only after measuring representative participant activity on the actual Pi.

Database migrations or schema initialization must be a deliberate release step, not an automatic action performed independently by every service start. Any migration must be backed up, tested, and assessed for backward compatibility before the release symlink changes.

## 10. Nginx Reverse Proxy Approach

Nginx will listen on LAN-facing port 80 and proxy application requests to `http://127.0.0.1:8000`. The site configuration should:

- set the expected hostname and reserved IP behavior;
- pass `Host`, `X-Real-IP`, `X-Forwarded-For`, and `X-Forwarded-Proto`;
- apply conservative request and upstream timeouts;
- limit request-body size to the largest justified ASTH upload;
- serve versioned static files with cache headers where appropriate;
- avoid caching authenticated or user-specific responses;
- hide unnecessary version information with `server_tokens off`;
- provide a clear maintenance or upstream-unavailable response; and
- be validated with `sudo nginx -t` before reload.

The upstream should remain loopback-only. Reload configuration without dropping established connections:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Plain HTTP is acceptable only for the initial trusted-LAN pilot. Authentication cookies should still use `HttpOnly` and an appropriate `SameSite` policy. A later phase should add locally trusted HTTPS if the site can distribute a trusted certificate authority or use a hostname and certificate strategy that works without internet access. Do not use a self-signed certificate without documenting client trust setup and renewal.

## 11. SQLite Database Location and Permissions

Store the live database at:

```text
/var/lib/asth/db/asth.sqlite3
```

The `asth` service account should own the database directory and file. Directory write permission is essential because SQLite may create journal, write-ahead log, and shared-memory files beside the database. A planned baseline is:

```text
/var/lib/asth             asth:asth 0750
/var/lib/asth/db          asth:asth 0750
/var/lib/asth/db/*        asth:asth 0640
```

Only the application service and controlled backup operation should access the database. Nginx must never serve `/var/lib/asth`.

Enable foreign-key enforcement for every connection. Consider SQLite WAL mode after functional and power-loss testing because it can improve read/write overlap, but it also creates additional files and writes that must be understood by backup and recovery procedures. Configure a reasonable busy timeout, keep transactions short, add indexes for measured query patterns, and avoid multiple independent writer processes.

## 12. systemd Service Approach

Create one `asth.service` unit during implementation. It should:

- start after the network is available;
- run as `User=asth` and `Group=asth`;
- use `/opt/asth/current` as its working directory;
- load `/etc/asth/asth.env` through `EnvironmentFile=`;
- start Uvicorn with the absolute virtual-environment path;
- restart on unexpected failure with a short delay;
- stop cleanly within a bounded timeout;
- set a conservative file-descriptor limit;
- use a restrictive `UMask`;
- enable practical systemd sandboxing that has been tested against SQLite and media writes; and
- allow writes only to the required mutable ASTH paths.

Candidate hardening settings include `NoNewPrivileges=true`, `PrivateTmp=true`, `ProtectSystem=strict`, `ProtectHome=true`, and `ReadWritePaths=/var/lib/asth`. They must be introduced and verified together because an overly restrictive unit can prevent database, media, or temporary-file operations.

The service should be enabled only after a manual foreground start and health check succeed:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now asth.service
systemctl status asth.service --no-pager
```

Nginx should start after the network and may be enabled through its packaged service. `systemd` is the sole process supervisor; do not add Supervisor, PM2, or another duplicate manager.

## 13. Environment Variables and Secrets Handling

Store production runtime values in `/etc/asth/asth.env`, owned by `root:asth` with mode `0640`. The file should contain only simple `KEY=value` entries compatible with systemd's `EnvironmentFile` parsing. Planned variables include:

- deployment environment;
- SQLite database path;
- secret key used for sessions or token signing;
- trusted hostnames or origins;
- upload and content paths;
- log level; and
- feature flags needed for offline operation.

Generate secrets with a cryptographically secure tool during implementation, for example:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Never commit the production environment file, secret values, private SSH keys, or backup credentials. Do not put secrets directly in the systemd unit, shell history, QR code, client-side JavaScript, logs, or screenshots. Keep a protected off-device recovery copy of required secrets. Changing a signing key may invalidate existing sessions, so rotation must be scheduled and documented.

If future integration requires cloud/API credentials, keep it optional, disabled by default, and isolated from the offline MVP path.

## 14. Logging and Log Rotation

Use journald for FastAPI/Uvicorn standard output and error. This avoids a separate application log daemon and makes service inspection consistent:

```bash
journalctl -u asth.service --since today
journalctl -u asth.service -f
```

Application logging should:

- default to `INFO` in production;
- avoid request bodies, passwords, tokens, session cookies, and unnecessary personal data;
- include timestamps, severity, request/correlation identifiers, and actionable error context;
- avoid verbose SQL logging except during a controlled diagnostic window; and
- rate-limit repetitive failures in the application where practical.

Set bounded journald retention after measuring existing system usage; an initial target is approximately 100MB of persistent journal data and 14 days of retention. Because journald limits affect the whole host, validate the final values before applying them.

Use the logrotate configuration supplied by Raspberry Pi OS for Nginx and verify that it covers access and error logs. If `/var/log/asth` is later used, add a dedicated size-bounded logrotate rule and make the application reopen files correctly after rotation. Monitor:

```bash
journalctl --disk-usage
du -sh /var/log
df -h /
```

## 15. Backup and Recovery Approach

The microSD card must not hold the only backup. Use a scheduled process, initially daily, that:

1. creates a consistent SQLite snapshot with SQLite's backup mechanism rather than copying a live database file:

   ```bash
   sqlite3 /var/lib/asth/db/asth.sqlite3 \
     ".backup '/var/lib/asth/backup-staging/asth.sqlite3'"
   ```

2. checks the snapshot:

   ```bash
   sqlite3 /var/lib/asth/backup-staging/asth.sqlite3 "PRAGMA integrity_check;"
   ```

3. packages the database snapshot, mutable media, and non-secret configuration inventory;
4. copies the result to a mounted USB/SSD, NAS, or administrator-controlled workstation;
5. verifies the copy before deleting old staging files; and
6. retains multiple recovery points, for example seven daily and four weekly copies, subject to available off-device capacity.

Secrets should be backed up separately with stronger access controls. The application release itself should be reproducible from Git and pinned dependencies, so release directories are not the primary backup.

Recovery should be rehearsed on a separate location:

1. stop `asth.service`;
2. preserve the failed database for investigation;
3. restore a selected verified snapshot with correct ownership and permissions;
4. run `PRAGMA integrity_check;`;
5. start the service;
6. validate login, content, quiz write, dashboard read, and media access; and
7. record the recovery point and any lost transaction window.

Perform a controlled restore test before pilot use and at regular intervals. Consider a UPS to reduce filesystem and SQLite damage from sudden power loss.

## 16. Basic Security Hardening

For the local-network MVP:

- apply operating-system security updates during planned maintenance;
- remove or disable unused accounts, services, and packages;
- prohibit direct root SSH login;
- use SSH keys and disable password authentication after verification;
- use a host firewall that allows SSH only from the administration subnet and HTTP only from the deployment LAN;
- keep Uvicorn bound to loopback;
- run Nginx and ASTH as separate unprivileged accounts;
- use least-privilege filesystem permissions;
- validate `Host` and allowed origins in the application;
- protect state-changing requests against cross-site request forgery when cookie authentication is used;
- set secure password hashing, login throttling, and session expiry in the application design;
- set upload type and size limits, generate server-side filenames, and never execute uploaded content;
- remove sample/default Nginx sites after the ASTH site is validated;
- maintain accurate time for logs and session expiry; and
- do not forward router ports 22, 80, 443, or 8000 to the Pi.

Firewall changes can lock out administrators. Build and test rules while a local console is available, keep the current SSH session open, and verify a second session before closing it. The exact firewall rules must use the site's real subnet, not the example address in this document.

Because the Pi serves multiple participants, the training Wi-Fi should use modern encryption and a controlled password. Client isolation must not block clients from reaching the Pi. Separate the training network from sensitive organizational systems where the network infrastructure permits it.

## 17. Performance Considerations for the Current Hardware

The constraints and unsuitable workloads are documented in [HARDWARE_BASELINE.md](HARDWARE_BASELINE.md). The initial deployment should:

- run one Uvicorn worker and one modular application;
- avoid Docker, local LLMs, heavy monitoring agents, task queues, and duplicate process supervisors;
- keep background work short and execute only necessary scheduled jobs;
- paginate dashboards and list endpoints;
- optimize and size-limit images, video, uploads, and course content;
- let Nginx serve and cache versioned static assets;
- use efficient SQLite queries, indexes, short transactions, and bounded result sets;
- avoid excessive swap activity because it reduces performance and increases microSD writes;
- retain only two application releases and bounded logs;
- schedule backups outside training sessions;
- keep at least 20% storage free; and
- use active cooling and preferably a 5V/5A supply.

Measure representative operations with the expected devices, not only synthetic homepage requests. Observe:

```bash
free -h
vmstat 1
top
df -h /
vcgencmd measure_temp
vcgencmd get_throttled
```

After real learning workflows are populated, test at least the MVP target from the development roadmap: five simultaneous devices performing the approved representative workflow. Establish observed latency, peak RAM, swap activity, CPU load, temperature, and database write behavior before increasing the participant count.

## 18. Deployment Validation Checklist

### Host and network

- [x] Raspberry Pi 5, 2 GB RAM and current 32 GB microSD match the confirmed 30 July baseline.
- [ ] Power supply, cooling and temperature are revalidated after the final casing, NVMe and LCD assembly.
- [ ] OS version, architecture, time zone, and free storage are recorded.
- [ ] Hostname resolves where expected.
- [ ] Router DHCP reservation is active and documented.
- [x] Pi is reachable from a phone connected to `ASTH-PORTABLE`; the ASTH health endpoint succeeded.
- [ ] Ports exposed by `ss -lntp` match the plan; Uvicorn is not LAN-facing.

### Administration and security

- [ ] Named administrator can authenticate using an SSH key.
- [x] A tested local HDMI/USB-keyboard recovery path exists.
- [x] Local `asthadmin` login, boot-recovery password recovery and approved `sudo` access are verified.
- [ ] Root SSH login is disabled.
- [ ] Password SSH login is disabled only after key access is proven.
- [ ] Firewall permits the intended LAN and blocks unintended networks.
- [ ] No router port forwarding exposes the Pi.
- [ ] File ownership and modes match the directory plan.
- [ ] Production secrets are absent from Git and logs.

### Application and proxy

- [ ] Release files and pinned dependencies identify an exact version.
- [ ] Uvicorn starts manually as the service user.
- [ ] `asth.service` starts, stops, restarts, and survives a reboot.
- [ ] `nginx -t` passes before reload.
- [ ] Nginx proxies dynamic requests and serves intended static assets.
- [x] `/health` remains available and the live landing page was visually confirmed after service restart.
- [x] `/api/hub-status` supplies the live landing-page status data.
- [x] `/learn/` exists separately and intentionally has no network graph.
- [ ] Populate and validate actual modules, PDFs, videos and interactive content; participant/trainer, quiz, progress and Smart Tutor workflows remain pending.
- [ ] Upload and request-size limits behave as designed.
- [ ] Five representative client devices complete the core flow concurrently.

### Data and operations

- [ ] SQLite foreign keys, busy timeout, and selected journal mode are verified.
- [ ] Database and media remain writable only by intended processes.
- [ ] Journald and Nginx rotation limits are active and storage remains bounded.
- [ ] A consistent off-device backup completes and passes integrity checking.
- [ ] After a database-backed module exists, a database restore is tested and the recovered application passes core checks; this is currently deferred.
- [x] A normal recovery reboot returned ASTH, `/mnt/rog`, Samba, Uptime Kuma, Cockpit and `ASTH-PORTABLE` to service.
- [ ] Temperature, throttling, RAM, swap, CPU, and disk usage remain acceptable during the load test.
- [ ] Site handover notes contain URLs, network details, backup location, recovery steps, and administrative contacts.

## 19. Rollback Approach

The current single-file application path was verified on 13 August 2026. The active v0.4.0 file and safety copy `/opt/asth/app/main.py.pre-rollback-test-20260730` had SHA-256 `c984a4b412f00117b763f9daa6fa9f948102b84a913e99fe6201b0fba350a0d3`. The v0.3.0 rollback file `/opt/asth/app/main.py.backup-clay-service-hub-20260726` had SHA-256 `d9ab6ed2312d0fddcae36af94c26df1c7e72a26c84afee0117a5b5b37564726a`. Rollback and forward restoration each restarted `asth.service` successfully and returned HTTP 200, `healthy`, with the expected version.

The release-directory procedure below remains the target for a future structured deployment. Database-coupled rollback remains deferred until a database-backed module exists.

Each deployment should preserve:

- the current release identifier;
- the immediately previous release directory and virtual environment;
- the configuration version or checksum;
- a pre-deployment SQLite backup stored off-device; and
- the schema version and migration compatibility notes.

For an application-only failure with a backward-compatible database:

1. stop `asth.service`;
2. repoint `/opt/asth/current` to the previous known-good release;
3. start the service;
4. validate `/health` and the core user flow through Nginx; and
5. record the failed release and evidence.

If a database migration is not backward compatible, application rollback alone is unsafe. Stop the service, preserve the failed database, restore the matching pre-deployment database backup, correct ownership and permissions, check integrity, then start and validate the previous release. This loses writes made after the backup, so the deployment window and operator decision must be documented.

Nginx and systemd configuration changes should be backed up before alteration and validated before reload. If a configuration reload fails, keep the running known-good configuration in place; do not reboot as a first response.

Rollback is complete only when health, login, a read operation, a write operation, and relevant media access have passed. Diagnose the failed release separately rather than editing production files in place.

## 20. Final Hardware, Content and Migration Sequence

1. Preserve the working microSD deployment and the two confirmed local application backups.
2. Receive and install compatible casing hardware.
3. Receive and install the NVMe controller/HAT and SSD, then detect and test the device before any migration.
4. Install the MHS35 LCD and appropriate display cable; run the compatible LCD driver procedure only then.
5. Verify power-supply suitability, cooling and temperature with the final assembly.
6. Decide and execute the NVMe migration method; prefer full-OS boot from NVMe only if testing passes.
7. Retain and label the microSD as recovery media after a successful full migration.
8. Configure LCD kiosk mode to open `/` and verify reboot recovery.
9. Populate `/learn/` with approved modules, PDFs, videos and interactive content, placing large content on NVMe when available.
10. Perform post-installation endpoint, visual, multi-device and final-assembly validation.
11. Complete database backup/restore after a database-backed module exists; revalidate application rollback if the deployment layout changes.
12. Finalise the system custodian and maintenance window.
13. Bring the deployed v0.4.0 source into this repository through a controlled comparison and commit later; do not overwrite the Pi from the stale repository state.

## 21. General Implementation Sequence

1. Confirm the hardware, OS, power, cooling, filesystem, and site network details against [HARDWARE_BASELINE.md](HARDWARE_BASELINE.md).
2. Record current configuration and take an initial off-device microSD image or equivalent recovery backup.
3. Set the hostname, time zone, DHCP reservation, and documented LAN URLs.
4. Create and verify the named administrator, SSH key access, and local recovery path.
5. Update Raspberry Pi OS, reboot, and recheck storage, power, temperature, and connectivity.
6. Install only the approved essential packages.
7. Create the locked `asth` service account and the planned directories, ownership, and permissions.
8. Prepare an exact application release and its pinned virtual environment under `/opt/asth/releases`.
9. Create `/etc/asth/asth.env`, generate secrets, and store the protected recovery copy.
10. Create or initialize SQLite deliberately, apply tested schema changes, and make the pre-service backup.
11. Run Uvicorn in the foreground as the `asth` user and validate the loopback health endpoint.
12. Add and harden `asth.service`, then test start, stop, restart, failure recovery, and boot startup.
13. Add the Nginx site, validate it with `nginx -t`, reload, and test from LAN clients.
14. Apply SSH and firewall hardening while keeping verified recovery access.
15. Set bounded journald/Nginx log retention and verify useful, non-sensitive logs.
16. Configure the off-device backup schedule and complete a restore rehearsal.
17. Run the full validation checklist, including five-device testing and hardware monitoring.
18. Record the release, checksums, configuration, results, known limitations, rollback point, and handover instructions.
19. Schedule the first maintenance, backup review, and capacity review after the pilot.

This sequence is the basis for later implementation instructions and scripts. It does not authorize package installation, account changes, service configuration, or deployment on a Pi by itself.
