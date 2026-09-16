import subprocess
import os
import shutil
import threading
import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="ASTH Adaptive Smart Training Hub",
    version="0.4.0",
)

app.mount(
    "/assets",
    StaticFiles(directory="/var/www/asth-hub/assets"),
    name="assets",
)


LANDING_PAGE = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASTH Adaptive Smart Training Hub</title>

    <style>
        :root {
            --blue: #3977f6;
            --dark-blue: #17335b;
            --cyan: #25c7e8;
            --yellow: #ffd45c;
            --green: #38ca87;
            --red: #f36d79;
            --text: #213a60;
            --muted: #657792;
            --surface: rgba(248, 251, 255, 0.94);
            --shadow:
                8px 10px 0 rgba(41, 83, 151, 0.12),
                14px 18px 28px rgba(47, 74, 119, 0.15);
        }

        * {
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;
            margin: 0;
            color: var(--text);
            background:
                radial-gradient(circle at 12% 8%, #fff1a8 0, transparent 22%),
                radial-gradient(circle at 88% 12%, #b9eaff 0, transparent 25%),
                linear-gradient(145deg, #dfeaff, #f8fbff 48%, #dcecff);
            font-family:
                Inter, ui-rounded, "Segoe UI", Arial, sans-serif;
        }

        .page {
            width: min(1180px, calc(100% - 28px));
            margin: auto;
            padding: 24px 0 30px;
        }

        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            margin-bottom: 20px;
            padding: 20px 24px;
            border: 3px solid rgba(255, 255, 255, 0.9);
            border-radius: 30px;
            background: rgba(250, 252, 255, 0.86);
            box-shadow: var(--shadow);
            backdrop-filter: blur(12px);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 18px;
            min-width: 0;
        }

        .logos {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-shrink: 0;
        }

        .logo-box {
            display: grid;
            width: 74px;
            height: 74px;
            place-items: center;
            padding: 7px;
            border: 3px solid white;
            border-radius: 22px;
            background: #ffffff;
            box-shadow:
                5px 6px 0 rgba(38, 88, 170, 0.17),
                8px 10px 16px rgba(51, 76, 117, 0.14);
        }

        .logo-box img {
            display: block;
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .eyebrow {
            margin: 0 0 5px;
            color: var(--blue);
            font-size: 0.74rem;
            font-weight: 900;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        h1 {
            margin: 0;
            font-size: clamp(1.65rem, 4vw, 2.55rem);
            line-height: 1.05;
        }

        .subtitle {
            margin: 7px 0 0;
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.45;
        }

        .status-pill {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            flex-shrink: 0;
            padding: 11px 15px;
            border: 2px solid white;
            border-radius: 999px;
            color: #725719;
            background: #fff1bd;
            box-shadow: 4px 5px 0 rgba(65, 91, 130, 0.12);
            font-size: 0.8rem;
            font-weight: 900;
        }

        .status-dot {
            width: 11px;
            height: 11px;
            border-radius: 50%;
            background: var(--yellow);
            box-shadow: 0 0 0 5px rgba(255, 212, 92, 0.22);
        }

        .status-pill.online {
            color: #14623e;
            background: #dff8eb;
        }

        .status-pill.online .status-dot {
            background: var(--green);
            box-shadow: 0 0 0 5px rgba(56, 202, 135, 0.2);
        }

        .status-pill.offline {
            color: #8d3440;
            background: #ffe7ea;
        }

        .status-pill.offline .status-dot {
            background: var(--red);
            box-shadow: 0 0 0 5px rgba(243, 109, 121, 0.18);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 17px;
        }

        .card {
            position: relative;
            overflow: hidden;
            min-width: 0;
            padding: 19px;
            border: 3px solid rgba(255, 255, 255, 0.88);
            border-radius: 25px;
            background: var(--surface);
            box-shadow: var(--shadow);
        }

        .card::after {
            position: absolute;
            top: -24px;
            right: -18px;
            width: 65px;
            height: 65px;
            border-radius: 45% 55% 60% 40%;
            background: rgba(57, 119, 246, 0.09);
            content: "";
            transform: rotate(25deg);
        }

        .metric-top {
            display: flex;
            align-items: center;
            gap: 11px;
            margin-bottom: 13px;
        }

        .metric-icon {
            display: grid;
            flex: 0 0 43px;
            width: 43px;
            height: 43px;
            place-items: center;
            border: 3px solid white;
            border-radius: 14px;
            font-size: 1.18rem;
            box-shadow:
                4px 5px 0 rgba(34, 75, 145, 0.18),
                6px 8px 13px rgba(64, 91, 130, 0.13);
        }

        .devices-icon { background: #dce9ff; }
        .download-icon { background: #d8f8fb; }
        .upload-icon { background: #fff0cf; }
        .uptime-icon { background: #e3f8e9; }

        .card-label {
            margin: 0;
            color: var(--muted);
            font-size: 0.7rem;
            font-weight: 900;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .card-value {
            margin: 0;
            overflow-wrap: anywhere;
            font-size: clamp(1.35rem, 3vw, 2rem);
            font-weight: 900;
        }

        .card-note {
            margin: 8px 0 0;
            overflow-wrap: anywhere;
            color: var(--muted);
            font-size: 0.75rem;
        }

        .chart-card {
            grid-column: span 3;
            min-height: 300px;
        }

        .chart-heading {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 15px;
            margin-bottom: 15px;
        }

        .chart-title {
            display: flex;
            align-items: center;
            gap: 11px;
        }

        .chart-heading h2 {
            margin: 0;
            font-size: 1.04rem;
        }

        .legend {
            display: flex;
            gap: 13px;
            color: var(--muted);
            font-size: 0.74rem;
            font-weight: 700;
        }

        .legend span::before {
            display: inline-block;
            width: 10px;
            height: 10px;
            margin-right: 6px;
            border-radius: 4px;
            content: "";
        }

        .rx::before { background: var(--cyan); }
        .tx::before { background: var(--blue); }

        .chart-shell {
            height: 210px;
            padding: 11px;
            border: 3px solid white;
            border-radius: 20px;
            background: #edf4fc;
            box-shadow:
                inset 5px 5px 10px rgba(89, 113, 145, 0.12),
                inset -5px -5px 10px rgba(255, 255, 255, 0.82);
        }

        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }

        .services {
            display: flex;
            flex-direction: column;
            min-height: 300px;
            background:
                radial-gradient(
                    circle at top right,
                    rgba(255, 255, 255, 0.68),
                    transparent 32%
                ),
                linear-gradient(145deg, #ffe591, #ffc870);
        }

        .services h2 {
            margin: 5px 0 8px;
            font-size: 1.35rem;
        }

        .services p {
            margin: 0;
            color: #685a48;
            font-size: 0.78rem;
            line-height: 1.45;
        }

        .service-links {
            display: grid;
            gap: 9px;
            margin-top: 17px;
        }

        .service-button {
            position: relative;
            z-index: 2;
            display: flex;
            align-items: center;
            gap: 9px;
            padding: 10px 12px;
            border: 3px solid rgba(255, 255, 255, 0.85);
            border-radius: 14px;
            color: white;
            background: linear-gradient(145deg, #4e88fa, #2862dd);
            box-shadow:
                4px 5px 0 #1749b5,
                7px 9px 13px rgba(50, 79, 135, 0.2);
            font-size: 0.76rem;
            font-weight: 900;
            text-decoration: none;
            transition: transform 0.15s ease;
        }

        .service-button:hover {
            transform: translateY(-2px);
        }


        .services details {
            margin-top: 17px;
            position: relative;
            z-index: 2;
        }

        .services summary {
            cursor: pointer;
            font-weight: 900;
        }

        .services .access-value {
            display: block;
            margin: 7px 0 10px;
            padding: 8px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.65);
            overflow-wrap: anywhere;
            white-space: pre-wrap;
            user-select: text;
        }

        .services .access-actions {
            display: flex;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .services button.service-button {
            font-family: inherit;
            cursor: pointer;
            text-align: left;
        }

        .services :is(summary, button, a):focus-visible {
            outline: 3px solid var(--dark-blue);
            outline-offset: 3px;
        }

        .services .copy-status {
            margin-top: 12px;
            overflow-wrap: anywhere;
        }


        .hud { grid-column: 1 / -1; }
        .hud h2 { margin: 0 0 12px; font-size: 1.1rem; }
        .hud-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr));
            gap: 12px;
        }
        .hud-grid div {
            padding: 10px;
            border-radius: 14px;
            background: #edf4fc;
            overflow-wrap: anywhere;
        }
        .hud dt { color: var(--muted); font-size: 0.8rem; }
        .hud dd { margin: 6px 0 0; font-weight: 900; }

        footer {
            margin-top: 23px;
            color: var(--muted);
            font-size: 0.73rem;
            text-align: center;
        }

        @media (max-width: 920px) {
            .grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .chart-card,
            .services {
                grid-column: span 2;
            }

            .services {
                min-height: auto;
            }
        }

        @media (max-width: 650px) {
            .page {
                width: min(100% - 18px, 1180px);
                padding-top: 12px;
            }

            header {
                align-items: flex-start;
                flex-direction: column;
                padding: 17px;
                border-radius: 23px;
            }

            .brand {
                align-items: flex-start;
                flex-direction: column;
            }

            .logo-box {
                width: 65px;
                height: 65px;
                border-radius: 19px;
            }

            .status-pill {
                align-self: stretch;
            }

            .grid {
                grid-template-columns: 1fr;
            }

            .chart-card,
            .services {
                grid-column: span 1;
            }

            .chart-heading {
                align-items: flex-start;
                flex-direction: column;
            }
        }
    </style>
</head>

<body>
    <main class="page">
        <header>
            <div class="brand">
                <div class="logos">
                    <div class="logo-box">
                        <img src="/assets/logo-dvs.png" alt="Logo DVS">
                    </div>

                    <div class="logo-box">
                        <img src="/assets/logo-asth.png" alt="Logo ASTH">
                    </div>
                </div>

                <div>
                    <p class="eyebrow">Adaptive Smart Training Hub</p>
                    <h1>ASTH Service Hub</h1>
                    <p class="subtitle">
                        Pusat akses setempat untuk pembelajaran, pemantauan
                        rangkaian dan perkhidmatan Raspberry Pi ASTH.
                    </p>
                </div>
            </div>

            <div id="statusPill" class="status-pill">
                <span class="status-dot"></span>
                <span id="statusText">Menghubungkan...</span>
            </div>
        </header>

        <section class="grid">
            <article class="card">
                <div class="metric-top">
                    <div class="metric-icon devices-icon">&#128101;</div>
                    <p class="card-label">Peranti Tersambung</p>
                </div>

                <p id="devices" class="card-value">&#8212;</p>
                <p class="card-note">Connected ke hotspot ASTH</p>
            </article>

            <article class="card">
                <div class="metric-top">
                    <div class="metric-icon download-icon">&#8595;</div>
                    <p class="card-label">Muat Turun</p>
                </div>

                <p id="rxRate" class="card-value">&#8212;</p>
                <p id="rxTotal" class="card-note">Jumlah RX: &#8212;</p>
            </article>

            <article class="card">
                <div class="metric-top">
                    <div class="metric-icon upload-icon">&#8593;</div>
                    <p class="card-label">Muat Naik</p>
                </div>

                <p id="txRate" class="card-value">&#8212;</p>
                <p id="txTotal" class="card-note">Jumlah TX: &#8212;</p>
            </article>

            <article class="card">
                <div class="metric-top">
                    <div class="metric-icon uptime-icon">&#9201;</div>
                    <p class="card-label">System Uptime</p>
                </div>

                <p id="uptime" class="card-value">&#8212;</p>
                <p id="ssid" class="card-note">Wi-Fi: &#8212;</p>
            </article>

            <article class="card chart-card">
                <div class="chart-heading">
                    <div class="chart-title">
                        <div class="metric-icon download-icon">&#128202;</div>
                        <h2>Aktiviti Rangkaian Masa Nyata</h2>
                    </div>

                    <div class="legend">
                        <span class="rx">Download</span>
                        <span class="tx">Upload</span>
                    </div>
                </div>

                <div class="chart-shell">
                    <canvas id="networkChart"></canvas>
                </div>
            </article>

            <article class="card services">
                <div>
                    <p class="eyebrow">ASTH Services</p>
                    <h2>Akses Servis</h2>
                    <p>
                        Pilih perkhidmatan pembelajaran atau pengurusan
                        sistem yang diperlukan.
                    </p>
                </div>

                <div class="service-links">
                    <a class="service-button" href="/learn/">
                        &#127891; Learning Hub
                    </a>

                    <a
                        id="jellyfinLink"
                        class="service-button"
                        href="#"
                        target="_blank"
                        rel="noopener"
                    >
                        🎬 Jellyfin
                    </a>

                    <a
                        id="uptimeLink"
                        class="service-button"
                        href="#"
                        target="_blank"
                        rel="noopener"
                    >
                        &#128200; Uptime Kuma
                    </a>

                    <a
                        id="cockpitLink"
                        class="service-button"
                        href="#"
                        target="_blank"
                        rel="noopener"
                    >
                        &#128421;&#65039; Cockpit
                    </a>
                </div>

                <details>
                    <summary>ROG Drive</summary>
                    <p>Network Address:</p>
                    <code id="rogAddress" class="access-value"></code>
                    <p>Username: <strong>asthadmin</strong></p>
                    <p>Password stored privately.</p>
                    <p>Tampal alamat dalam bar alamat Windows File Explorer.</p>
                    <div class="access-actions">
                        <button type="button" class="service-button" id="copyRog">
                            Copy network address
                        </button>
                    </div>
                </details>

                <details>
                    <summary>SSH</summary>
                    <p>SSH Command:</p>
                    <code id="sshCommand" class="access-value"></code>
                    <p>Username: <strong>asthadmin</strong></p>
                    <p>Use the ASTH server administrator account.</p>
                    <p>Jalankan perintah dalam terminal dengan klien SSH.</p>
                    <div class="access-actions">
                        <button type="button" class="service-button" id="copySsh">
                            Copy SSH command
                        </button>
                    </div>
                </details>
                <p id="copyStatus" class="copy-status" aria-live="polite"></p>
            </article>
            <article class="card hud">
                <h2>Status Sistem</h2>
                <dl class="hud-grid">
                    <div><dt>CPU temperature</dt><dd id="hudTemp">Unavailable</dd></div>
                    <div><dt>RAM usage</dt><dd id="hudRam">Unavailable</dd></div>
                    <div><dt>ROG SSD</dt><dd id="hudMount">Unavailable</dd></div>
                    <div><dt>ROG free / total</dt><dd id="hudSpace">Unavailable</dd></div>
                    <div><dt>ASTH App</dt><dd id="hudAsth">Unavailable</dd></div>
                    <div><dt>Nginx</dt><dd id="hudNginx">Unavailable</dd></div>
                    <div><dt>Jellyfin</dt><dd id="hudJellyfin">Unavailable</dd></div>
                    <div><dt>Samba</dt><dd id="hudSamba">Unavailable</dd></div>
                    <div><dt>Uptime Kuma</dt><dd id="hudKuma">Unavailable</dd></div>
                    <div><dt>Office Tunnel</dt><dd id="hudOffice">Unavailable</dd></div>
                </dl>
                <p class="card-note" id="hudNote">Updates every 30 seconds. Running indicates process state, not service reachability.</p>
            </article>
        </section>

        <footer>
            Data dikemas kini automatik setiap 5 saat &#183; ASTH v0.4.0
        </footer>
    </main>

    <script>
        const devices = document.getElementById("devices");
        const rxRate = document.getElementById("rxRate");
        const txRate = document.getElementById("txRate");
        const rxTotal = document.getElementById("rxTotal");
        const txTotal = document.getElementById("txTotal");
        const uptime = document.getElementById("uptime");
        const ssid = document.getElementById("ssid");
        const statusPill = document.getElementById("statusPill");
        const statusText = document.getElementById("statusText");
        const canvas = document.getElementById("networkChart");
        const context = canvas.getContext("2d");

        document.getElementById("uptimeLink").href =
            `http://${location.hostname}:3001`;

        document.getElementById("cockpitLink").href =
            `https://${location.hostname}:9090`;


        document.getElementById("jellyfinLink").href =
            `http://${location.hostname}:8096`;

        // Construct separators without Python/JavaScript backslash ambiguity.
        const uncSeparator = String.fromCharCode(92);
        const rogAddress = document.getElementById("rogAddress");
        const sshCommand = document.getElementById("sshCommand");
        rogAddress.textContent =
            uncSeparator.repeat(2) + location.hostname + uncSeparator + "ROG-Drive";
        sshCommand.textContent = `ssh asthadmin@${location.hostname}`;

        async function copyAccess(source, successMessage) {
            const feedback = document.getElementById("copyStatus");
            feedback.textContent = "";
            try {
                if (!navigator.clipboard ||
                    typeof navigator.clipboard.writeText !== "function") {
                    throw new Error("Clipboard unavailable");
                }
                await navigator.clipboard.writeText(source.textContent);
                feedback.textContent = successMessage;
            } catch (error) {
                feedback.textContent =
                    "Salinan automatik tidak tersedia. Sila salin teks secara manual.";
            }
        }

        document.getElementById("copyRog").addEventListener("click", () =>
            copyAccess(rogAddress, "Alamat ROG Drive disalin.")
        );
        document.getElementById("copySsh").addEventListener("click", () =>
            copyAccess(sshCommand, "Perintah SSH disalin.")
        );

        let previous = null;
        let rxHistory = Array(30).fill(0);
        let txHistory = Array(30).fill(0);

        function formatBytes(bytes) {
            if (!Number.isFinite(bytes) || bytes <= 0) {
                return "0 B";
            }

            const units = ["B", "KB", "MB", "GB", "TB"];
            const index = Math.min(
                Math.floor(Math.log(bytes) / Math.log(1024)),
                units.length - 1
            );

            const value = bytes / Math.pow(1024, index);
            return value.toFixed(index === 0 ? 0 : 1) + " " + units[index];
        }

        function formatRate(bytesPerSecond) {
            return formatBytes(bytesPerSecond) + "/s";
        }

        function formatUptime(seconds) {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);

            if (days > 0) {
                return `${days}h ${hours}j`;
            }

            if (hours > 0) {
                return `${hours}j ${minutes}m`;
            }

            return `${minutes} min`;
        }

        function drawChart() {
            const ratio = window.devicePixelRatio || 1;
            const width = canvas.clientWidth;
            const height = canvas.clientHeight;

            if (!width || !height) {
                return;
            }

            canvas.width = Math.round(width * ratio);
            canvas.height = Math.round(height * ratio);
            context.setTransform(ratio, 0, 0, ratio, 0, 0);
            context.clearRect(0, 0, width, height);

            context.strokeStyle = "rgba(82, 112, 154, 0.13)";
            context.lineWidth = 1;

            for (let row = 1; row < 5; row++) {
                const y = (height / 5) * row;
                context.beginPath();
                context.moveTo(0, y);
                context.lineTo(width, y);
                context.stroke();
            }

            const maximum = Math.max(...rxHistory, ...txHistory, 1024);

            function plot(values, colour) {
                context.beginPath();
                context.strokeStyle = colour;
                context.lineWidth = 4;
                context.lineJoin = "round";
                context.lineCap = "round";

                values.forEach((value, index) => {
                    const x = (index / (values.length - 1)) * width;
                    const y =
                        height -
                        (value / maximum) * (height - 22) -
                        11;

                    if (index === 0) {
                        context.moveTo(x, y);
                    } else {
                        context.lineTo(x, y);
                    }
                });

                context.stroke();
            }

            plot(rxHistory, "#25c7e8");
            plot(txHistory, "#3977f6");
        }

        function setConnectionStatus(isOnline) {
            statusPill.className =
                "status-pill " + (isOnline ? "online" : "offline");

            statusText.textContent =
                isOnline ? "Hub Online" : "Hub Offline";
        }


        function renderHud(data) {
            const set = (id, value) => { document.getElementById(id).textContent = value; };
            set("hudTemp", Number.isFinite(data.cpu_temperature_c) ? data.cpu_temperature_c + " °C" : "Unavailable");
            set("hudRam", Number.isFinite(data.ram_used_percent) ? data.ram_used_percent + "%" : "Unavailable");
            set("hudMount", data.rog_mounted === true ? "Mounted" : data.rog_mounted === false ? "Not mounted / unexpected device" : "Unavailable");
            set("hudSpace", Number.isFinite(data.rog_free_bytes) && Number.isFinite(data.rog_total_bytes)
                ? formatBytes(data.rog_free_bytes) + " / " + formatBytes(data.rog_total_bytes) : "Unavailable");
            set("hudOffice", data.office_tunnel === "connected" ? "Connected"
                : data.office_tunnel === "disconnected" ? "Disconnected" : "Unavailable");
            const labels = {active: "Running", inactive: "Stopped", failed: "Failed", activating: "Starting", deactivating: "Stopping"};
            for (const [id, field] of Object.entries({
                hudAsth: "service_asth", hudNginx: "service_nginx",
                hudJellyfin: "service_jellyfin", hudSamba: "service_smbd",
                hudKuma: "service_uptime_kuma"
            })) set(id, Object.prototype.hasOwnProperty.call(labels, data[field]) ? labels[data[field]] : "Unavailable");
            document.getElementById("hudNote").textContent =
                "Updates every 30 seconds. Running indicates process state, not service reachability.";
        }

        async function refreshStatus() {
            try {
                const response = await fetch(
                    "/api/hub-status",
                    { cache: "no-store" }
                );

                if (!response.ok) {
                    throw new Error("Status API gagal");
                }

                const data = await response.json();
                renderHud(data);
                const now = Date.now();

                let currentRxRate = 0;
                let currentTxRate = 0;

                if (previous) {
                    const seconds = Math.max(
                        (now - previous.time) / 1000,
                        1
                    );

                    currentRxRate = Math.max(
                        (data.rx_bytes - previous.rx) / seconds,
                        0
                    );

                    currentTxRate = Math.max(
                        (data.tx_bytes - previous.tx) / seconds,
                        0
                    );
                }

                previous = {
                    time: now,
                    rx: data.rx_bytes,
                    tx: data.tx_bytes
                };

                rxHistory.push(currentRxRate);
                txHistory.push(currentTxRate);
                rxHistory.shift();
                txHistory.shift();

                devices.textContent = data.connected_devices;
                rxRate.textContent = formatRate(currentRxRate);
                txRate.textContent = formatRate(currentTxRate);

                rxTotal.textContent =
                    "Jumlah RX: " + formatBytes(data.rx_bytes);

                txTotal.textContent =
                    "Jumlah TX: " + formatBytes(data.tx_bytes);

                uptime.textContent =
                    formatUptime(data.uptime_seconds);

                ssid.textContent =
                    "Wi-Fi: " + data.wifi_ssid;

                setConnectionStatus(data.status === "online");
                drawChart();
            } catch (error) {
                setConnectionStatus(false);
                renderHud({});
                document.getElementById("hudNote").textContent = "System status unavailable.";
            }
        }

        window.addEventListener("resize", drawChart);

        drawChart();
        refreshStatus();
        setInterval(refreshStatus, 5000);
    </script>
</body>
</html>
"""


LEARNING_PAGE = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASTH Learning Hub</title>

    <style>
        :root {
            --blue: #3977f6;
            --dark: #17335b;
            --muted: #657792;
            --yellow: #ffd45c;
            --shadow:
                8px 10px 0 rgba(41, 83, 151, 0.12),
                14px 18px 28px rgba(47, 74, 119, 0.15);
        }

        * {
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;
            margin: 0;
            color: var(--dark);
            background:
                radial-gradient(circle at 10% 8%, #fff0a7, transparent 24%),
                radial-gradient(circle at 90% 10%, #b9eaff, transparent 25%),
                linear-gradient(145deg, #dfeaff, #f9fbff 50%, #dcecff);
            font-family:
                Inter, ui-rounded, "Segoe UI", Arial, sans-serif;
        }

        .page {
            width: min(1100px, calc(100% - 28px));
            margin: auto;
            padding: 25px 0 35px;
        }

        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            padding: 22px;
            border: 3px solid white;
            border-radius: 29px;
            background: rgba(250, 252, 255, 0.9);
            box-shadow: var(--shadow);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .logos {
            display: flex;
            gap: 9px;
        }

        .logo {
            display: grid;
            width: 68px;
            height: 68px;
            place-items: center;
            padding: 7px;
            border: 3px solid white;
            border-radius: 20px;
            background: white;
            box-shadow: 5px 6px 0 rgba(38, 88, 170, 0.16);
        }

        .logo img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .eyebrow {
            margin: 0 0 5px;
            color: var(--blue);
            font-size: 0.73rem;
            font-weight: 900;
            letter-spacing: 0.11em;
            text-transform: uppercase;
        }

        h1 {
            margin: 0;
            font-size: clamp(1.65rem, 4vw, 2.4rem);
        }

        .subtitle {
            margin: 7px 0 0;
            color: var(--muted);
            font-size: 0.86rem;
        }

        .back {
            flex-shrink: 0;
            padding: 11px 15px;
            border: 3px solid white;
            border-radius: 15px;
            color: white;
            background: linear-gradient(145deg, #4e88fa, #2862dd);
            box-shadow: 4px 5px 0 #1749b5;
            font-size: 0.8rem;
            font-weight: 900;
            text-decoration: none;
        }

        .intro {
            margin: 20px 0;
            padding: 25px;
            border: 3px solid white;
            border-radius: 27px;
            background:
                radial-gradient(
                    circle at top right,
                    rgba(255, 255, 255, 0.75),
                    transparent 35%
                ),
                linear-gradient(145deg, #ffe591, #ffc870);
            box-shadow: var(--shadow);
        }

        .intro h2 {
            margin: 0 0 8px;
            font-size: 1.5rem;
        }

        .intro p {
            max-width: 720px;
            margin: 0;
            color: #665842;
            line-height: 1.6;
        }

        .modules {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
        }

        .module {
            min-height: 205px;
            padding: 21px;
            border: 3px solid white;
            border-radius: 25px;
            background: rgba(249, 252, 255, 0.94);
            box-shadow: var(--shadow);
        }

        .icon {
            display: grid;
            width: 55px;
            height: 55px;
            margin-bottom: 16px;
            place-items: center;
            border: 3px solid white;
            border-radius: 17px;
            background: #dce9ff;
            box-shadow: 4px 5px 0 rgba(34, 75, 145, 0.17);
            font-size: 1.55rem;
        }

        .module:nth-child(2) .icon {
            background: #d8f8fb;
        }

        .module:nth-child(3) .icon {
            background: #fff0cf;
        }

        .module h3 {
            margin: 0 0 8px;
        }

        .module p {
            margin: 0;
            color: var(--muted);
            font-size: 0.84rem;
            line-height: 1.55;
        }

        .coming {
            display: inline-block;
            margin-top: 16px;
            padding: 7px 10px;
            border-radius: 999px;
            color: #795b12;
            background: #fff1bd;
            font-size: 0.69rem;
            font-weight: 900;
        }

        footer {
            margin-top: 24px;
            color: var(--muted);
            font-size: 0.74rem;
            text-align: center;
        }

        @media (max-width: 800px) {
            .modules {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 650px) {
            header {
                align-items: flex-start;
                flex-direction: column;
            }

            .brand {
                align-items: flex-start;
                flex-direction: column;
            }

            .back {
                width: 100%;
                text-align: center;
            }

            .logo {
                width: 62px;
                height: 62px;
            }
        }
    </style>
</head>

<body>
    <main class="page">
        <header>
            <div class="brand">
                <div class="logos">
                    <div class="logo">
                        <img src="/assets/logo-dvs.png" alt="Logo DVS">
                    </div>

                    <div class="logo">
                        <img src="/assets/logo-asth.png" alt="Logo ASTH">
                    </div>
                </div>

                <div>
                    <p class="eyebrow">Adaptive Smart Training Hub</p>
                    <h1>ASTH Learning Hub</h1>
                    <p class="subtitle">
                        Pusat bahan latihan dan pembelajaran digital ITU.
                    </p>
                </div>
            </div>

            <a class="back" href="/">&#8592; Kembali ke Hub</a>
        </header>

        <section class="intro">
            <h2>Selamat datang ke Learning Hub &#127891;</h2>
            <p>
                Ruang ini disediakan untuk modul pembelajaran, nota,
                video, bahan kursus dan latihan interaktif yang boleh
                diakses melalui rangkaian ASTH.
            </p>
        </section>

        <section class="modules">
            <article class="module">
                <div class="icon">&#128218;</div>
                <h3>Modul Pembelajaran</h3>
                <p>
                    Koleksi modul kursus dan bahan rujukan untuk peserta
                    latihan.
                </p>
                <span class="coming">Akan Datang</span>
            </article>

            <article class="module">
                <div class="icon">&#127916;</div>
                <h3>Video Latihan</h3>
                <p>
                    Video demonstrasi, tutorial dan kandungan latihan
                    yang boleh ditonton dalam rangkaian tempatan.
                </p>
                <span class="coming">Akan Datang</span>
            </article>

            <article class="module">
                <div class="icon">&#129514;</div>
                <h3>Latihan Interaktif</h3>
                <p>
                    Aktiviti praktikal, kuiz dan bahan pembelajaran
                    interaktif untuk peserta.
                </p>
                <span class="coming">Akan Datang</span>
            </article>
        </section>

        <footer>
            ASTH Learning Hub &#183; Institut Teknologi Unggas
        </footer>
    </main>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    return HTMLResponse(content=LANDING_PAGE)


@app.get("/learn/", response_class=HTMLResponse)
def learning_hub() -> HTMLResponse:
    return HTMLResponse(content=LEARNING_PAGE)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "ASTH Adaptive Smart Training Hub",
        "version": "0.4.0",
    }

def _hub_read_int(path: str) -> int:
    try:
        with open(path, encoding="ascii") as source:
            return max(0, int(source.read().strip()))
    except (OSError, ValueError):
        return 0


def _hub_wifi_ssid() -> str:
    try:
        result = subprocess.run(
            ["/usr/sbin/iw", "dev", "wlan0", "info"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=1,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return ""

    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("ssid "):
            return line[5:].strip()

    return ""


def _hub_connected_stations() -> int:
    try:
        result = subprocess.run(
            ["/usr/sbin/iw", "dev", "wlan0", "station", "dump"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=1,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return 0

    return sum(
        1
        for line in result.stdout.splitlines()
        if line.lstrip().startswith("Station ")
    )


def _hub_uptime_seconds() -> int:
    try:
        with open("/proc/uptime", encoding="ascii") as source:
            return max(0, int(float(source.read().split()[0])))
    except (OSError, ValueError, IndexError, OverflowError):
        return 0



_HUD_UNITS = {
    "asth.service": "service_asth",
    "nginx.service": "service_nginx",
    "jellyfin.service": "service_jellyfin",
    "smbd.service": "service_smbd",
    "pm2-asthadmin.service": "service_pm2",
}
_hud_lock = threading.Lock()
_hud_cache = None
_hud_expires = 0.0


def _hud_text(path):
    with open(path, encoding="ascii") as source:
        return source.read()


def _hud_rog_identity():
    for line in _hud_text("/proc/self/mountinfo").splitlines():
        left, right = line.split(" - ", 1)
        fields, filesystem = left.split(), right.split()
        if fields[4] == "/mnt/rog":
            if filesystem[:2] == ["ntfs3", "/dev/sda2"]:
                return tuple(fields[:6] + filesystem[:2])
            return None
    return None



def _hud_office_tunnel(service_state):
    if service_state in ("inactive", "failed", "activating", "deactivating"):
        return "disconnected"
    if service_state != "active":
        return "unavailable"
    try:
        os.stat("/sys/class/net/asth-office")
    except FileNotFoundError:
        return "disconnected"
    except OSError:
        return "unavailable"
    try:
        result = subprocess.run(
            ["/usr/sbin/ip", "route", "show", "192.168.1.0/24"],
            capture_output=True, text=True, errors="replace",
            timeout=2, check=True,
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if not lines:
            return "disconnected"
        if len(lines) != 1:
            return "unavailable"
        fields = lines[0].split()
        if not fields or fields[0] != "192.168.1.0/24":
            return "unavailable"
        device_fields = [index for index, value in enumerate(fields) if value == "dev"]
        if len(device_fields) != 1 or device_fields[0] + 1 >= len(fields):
            return "unavailable"
        return "connected" if fields[device_fields[0] + 1] == "asth-office" else "disconnected"
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def _hud_collect():
    data = {
        "cpu_temperature_c": None, "ram_used_percent": None,
        "rog_mounted": None, "rog_free_bytes": None, "rog_total_bytes": None,
        **{field: "unknown" for field in _HUD_UNITS.values()},
        "service_uptime_kuma": "unknown",
        "office_tunnel": "unavailable",
    }
    try:
        if _hud_text("/sys/class/thermal/thermal_zone0/type").strip() == "cpu-thermal":
            value = int(_hud_text("/sys/class/thermal/thermal_zone0/temp")) / 1000
            if 0 <= value <= 150:
                data["cpu_temperature_c"] = round(value, 1)
    except (OSError, ValueError):
        pass
    try:
        memory = {}
        for line in _hud_text("/proc/meminfo").splitlines():
            key, value = line.split(":", 1)
            if key in ("MemTotal", "MemAvailable"):
                memory[key] = int(value.split()[0])
        total, available = memory["MemTotal"], memory["MemAvailable"]
        if total > 0 and 0 <= available <= total:
            data["ram_used_percent"] = round(100 * (total - available) / total, 1)
    except (OSError, ValueError, KeyError, IndexError):
        pass
    try:
        identity = _hud_rog_identity()
        data["rog_mounted"] = identity is not None
        if identity is not None:
            usage = shutil.disk_usage("/mnt/rog")
            if identity == _hud_rog_identity():
                data["rog_free_bytes"] = usage.free
                data["rog_total_bytes"] = usage.total
            else:
                data["rog_mounted"] = None
    except (OSError, ValueError, IndexError):
        data["rog_mounted"] = None
    office_service = "unknown"
    try:
        result = subprocess.run(
            ["/usr/bin/systemctl", "show", "--no-pager",
             "--property=Id,LoadState,ActiveState", *_HUD_UNITS,
             "wg-quick@asth-office.service"],
            capture_output=True, text=True, errors="replace", timeout=2,
            check=False,
        )
        for block in result.stdout.strip().split("\n\n"):
            properties = dict(line.split("=", 1) for line in block.splitlines() if "=" in line)
            if properties.get("Id") == "wg-quick@asth-office.service":
                if properties.get("LoadState") == "loaded":
                    office_service = properties.get("ActiveState", "unknown")
            field = _HUD_UNITS.get(properties.get("Id"))
            state = properties.get("ActiveState")
            if field and properties.get("LoadState") == "loaded":
                if state in ("active", "inactive", "failed", "activating", "deactivating"):
                    data[field] = state
    except (OSError, subprocess.SubprocessError):
        pass
    data["office_tunnel"] = _hud_office_tunnel(office_service)
    # Never invoke PM2 CLI: it may start a daemon or expose process environments.
    # A matching process name is evidence of a process, not HTTP health.
    if data["service_pm2"] == "active":
        try:
            with os.scandir("/proc") as entries:
                for entry in entries:
                    if entry.name.isdecimal():
                        try:
                            if _hud_text("/proc/" + entry.name + "/comm").strip() == "uptime-kuma":
                                data["service_uptime_kuma"] = "active"
                                break
                        except (OSError, ValueError):
                            continue
        except OSError:
            pass
    return data


def _hud_status():
    global _hud_cache, _hud_expires
    with _hud_lock:
        now = time.monotonic()
        if _hud_cache is None or now >= _hud_expires:
            _hud_cache = _hud_collect()
            _hud_expires = time.monotonic() + 30
        return dict(_hud_cache)


@app.get("/api/hub-status")
def hub_status():
    return {
        "status": "online",
        "connected_devices": _hub_connected_stations(),
        "rx_bytes": _hub_read_int(
            "/sys/class/net/wlan0/statistics/rx_bytes"
        ),
        "tx_bytes": _hub_read_int(
            "/sys/class/net/wlan0/statistics/tx_bytes"
        ),
        "uptime_seconds": _hub_uptime_seconds(),
        "wifi_ssid": _hub_wifi_ssid(),
        **_hud_status(),
    }
