import html
import json
import os
import re
import shutil
import subprocess
import threading
import time

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
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


_ASTH_WIFI_SSID = "ASTH-PORTABLE"
_ASTH_PORTAL_URL = "http://10.42.0.1/"
_QR_LOW_VERSIONS = (
    (1, 19, 7, ()),
    (2, 34, 10, (6, 18)),
    (3, 55, 15, (6, 22)),
    (4, 80, 20, (6, 26)),
    (5, 108, 26, (6, 30)),
)


def _qr_append_bits(bits, value, length):
    bits.extend((value >> index) & 1 for index in range(length - 1, -1, -1))


def _qr_multiply(left, right):
    result = 0
    for index in range(7, -1, -1):
        result = (result << 1) ^ ((result >> 7) * 0x11D)
        if (right >> index) & 1:
            result ^= left
    return result


def _qr_divisor(degree):
    result = [0] * (degree - 1) + [1]
    root = 1
    for _ in range(degree):
        for index in range(degree):
            result[index] = _qr_multiply(result[index], root)
            if index + 1 < degree:
                result[index] ^= result[index + 1]
        root = _qr_multiply(root, 2)
    return result


def _qr_remainder(data, divisor):
    result = [0] * len(divisor)
    for value in data:
        factor = value ^ result.pop(0)
        result.append(0)
        for index, coefficient in enumerate(divisor):
            result[index] ^= _qr_multiply(coefficient, factor)
    return result


def _qr_mask(mask, x, y):
    tests = (
        (x + y) % 2 == 0,
        y % 2 == 0,
        x % 3 == 0,
        (x + y) % 3 == 0,
        (x // 3 + y // 2) % 2 == 0,
        x * y % 2 + x * y % 3 == 0,
        (x * y % 2 + x * y % 3) % 2 == 0,
        ((x + y) % 2 + x * y % 3) % 2 == 0,
    )
    return tests[mask]


def _qr_penalty(modules):
    size = len(modules)
    score = 0
    for lines in (modules, zip(*modules)):
        for line in lines:
            values = list(line)
            run_colour = values[0]
            run_length = 1
            for value in values[1:]:
                if value == run_colour:
                    run_length += 1
                else:
                    if run_length >= 5:
                        score += run_length - 2
                    run_colour = value
                    run_length = 1
            if run_length >= 5:
                score += run_length - 2
            pattern = "".join("1" if value else "0" for value in values)
            score += 40 * (pattern.count("10111010000") + pattern.count("00001011101"))
    for y in range(size - 1):
        for x in range(size - 1):
            colour = modules[y][x]
            if all(modules[y + dy][x + dx] == colour for dy in (0, 1) for dx in (0, 1)):
                score += 3
    dark = sum(sum(row) for row in modules)
    score += abs(dark * 20 - size * size * 10) // (size * size) * 10
    return score


def _qr_matrix(payload):
    encoded = payload.encode("utf-8")
    selected = next(
        (entry for entry in _QR_LOW_VERSIONS if len(encoded) <= entry[1] - 2),
        None,
    )
    if selected is None:
        raise ValueError("QR payload is too long")
    version, data_codewords, error_codewords, alignment_positions = selected
    bits = []
    _qr_append_bits(bits, 0b0100, 4)
    _qr_append_bits(bits, len(encoded), 8)
    for value in encoded:
        _qr_append_bits(bits, value, 8)
    bits.extend([0] * min(4, data_codewords * 8 - len(bits)))
    bits.extend([0] * ((-len(bits)) % 8))
    data = [sum(bits[index + offset] << (7 - offset) for offset in range(8))
            for index in range(0, len(bits), 8)]
    for pad in (0xEC, 0x11) * data_codewords:
        if len(data) >= data_codewords:
            break
        data.append(pad)
    codewords = data + _qr_remainder(data, _qr_divisor(error_codewords))
    size = version * 4 + 17
    modules = [[False] * size for _ in range(size)]
    functions = [[False] * size for _ in range(size)]

    def set_function(x, y, value):
        if 0 <= x < size and 0 <= y < size:
            modules[y][x] = value
            functions[y][x] = True

    def draw_finder(center_x, center_y):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                distance = max(abs(dx), abs(dy))
                set_function(center_x + dx, center_y + dy, distance not in (2, 4))

    def draw_alignment(center_x, center_y):
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                set_function(center_x + dx, center_y + dy, max(abs(dx), abs(dy)) != 1)

    def draw_format(mask):
        value = (1 << 3) | mask
        remainder = value
        for _ in range(10):
            remainder = (remainder << 1) ^ ((remainder >> 9) * 0x537)
        value = ((value << 10) | remainder) ^ 0x5412
        bit = lambda index: ((value >> index) & 1) != 0
        for index in range(6):
            set_function(8, index, bit(index))
        set_function(8, 7, bit(6))
        set_function(8, 8, bit(7))
        set_function(7, 8, bit(8))
        for index in range(9, 15):
            set_function(14 - index, 8, bit(index))
        for index in range(8):
            set_function(size - 1 - index, 8, bit(index))
        for index in range(8, 15):
            set_function(8, size - 15 + index, bit(index))
        set_function(8, size - 8, True)

    for index in range(8, size - 8):
        set_function(6, index, index % 2 == 0)
        set_function(index, 6, index % 2 == 0)
    draw_finder(3, 3)
    draw_finder(size - 4, 3)
    draw_finder(3, size - 4)
    for center_y in alignment_positions:
        for center_x in alignment_positions:
            if not functions[center_y][center_x]:
                draw_alignment(center_x, center_y)
    draw_format(0)

    data_index = 0
    right = size - 1
    while right >= 1:
        if right == 6:
            right = 5
        upward = ((right + 1) & 2) == 0
        for vertical in range(size):
            y = size - 1 - vertical if upward else vertical
            for offset in range(2):
                x = right - offset
                if not functions[y][x] and data_index < len(codewords) * 8:
                    modules[y][x] = ((codewords[data_index >> 3] >> (7 - (data_index & 7))) & 1) != 0
                    data_index += 1
        right -= 2

    best = None
    best_score = None
    for mask in range(8):
        candidate = [row[:] for row in modules]
        for y in range(size):
            for x in range(size):
                if not functions[y][x] and _qr_mask(mask, x, y):
                    candidate[y][x] = not candidate[y][x]
        modules_before_format = modules
        modules = candidate
        draw_format(mask)
        candidate = modules
        modules = modules_before_format
        score = _qr_penalty(candidate)
        if best_score is None or score < best_score:
            best = candidate
            best_score = score
    return best


def _qr_svg(payload, element_id, title):
    modules = _qr_matrix(payload)
    quiet_zone = 4
    size = len(modules) + quiet_zone * 2
    path = "".join(
        f"M{x + quiet_zone} {y + quiet_zone}h1v1h-1z"
        for y, row in enumerate(modules)
        for x, dark in enumerate(row)
        if dark
    )
    escaped_id = html.escape(element_id, quote=True)
    escaped_payload = html.escape(payload, quote=True)
    escaped_title = html.escape(title)
    return (
        f'<svg id="{escaped_id}" data-qr-target="{escaped_payload}" role="img" '
        f'aria-label="{escaped_title}" viewBox="0 0 {size} {size}" shape-rendering="crispEdges">'
        f'<rect width="{size}" height="{size}" fill="#ffffff"/>'
        f'<path fill="#000000" d="{path}"/></svg>'
    )


def _wifi_qr_payload(password):
    escaped = re.sub(r'([\\;,":])', r'\\\1', password)
    return f"WIFI:T:WPA;S:{_ASTH_WIFI_SSID};P:{escaped};;"


def _wifi_access_markup():
    password = os.environ.get("ASTH_WIFI_PASSWORD")
    if not password:
        return (
            '<div class="wifi-unconfigured" role="status">'
            'PASSWORD WI-FI BELUM DIKONFIGURASI</div>'
            f'<p class="qr-detail">SSID: {_ASTH_WIFI_SSID}</p>'
        )
    payload = _wifi_qr_payload(password)
    try:
        svg = _qr_svg(payload, "wifiQr", "Kod QR Wi-Fi ASTH-PORTABLE")
    except ValueError:
        return (
            '<div class="wifi-unconfigured" role="status">'
            'PASSWORD WI-FI BELUM DIKONFIGURASI</div>'
            f'<p class="qr-detail">SSID: {_ASTH_WIFI_SSID}</p>'
        )
    return (
        svg
        + f'<p class="qr-detail">SSID: {_ASTH_WIFI_SSID}<br>'
        + f'Password: {html.escape(password)}</p>'
    )


LANDING_PAGE = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASTH Health Console</title>
    <style>
        :root {
            --navy: #08213f; --blue: #0755b8; --cyan: #007c95;
            --green: #006b38; --amber: #8a4a00; --red: #a91f32;
            --ink: #071a31; --muted: #3d536b; --line: #7893ae;
            --panel: #ffffff; --bg: #dce7f2;
        }
        * { box-sizing: border-box; }
        html, body { width: 100%; height: 100%; margin: 0; }
        body {
            overflow: hidden; color: var(--ink); background: var(--bg);
            font-family: "Segoe UI", Arial, sans-serif;
        }
        button, a { font: inherit; }
        button { cursor: pointer; }
        .console {
            display: grid; grid-template-rows: 68px 110px minmax(0, 1fr) 48px;
            gap: 8px; width: 100%; height: 100dvh; padding: 8px;
        }
        .panel {
            min-width: 0; min-height: 0; overflow: hidden;
            border: 2px solid var(--line); border-radius: 15px;
            background: var(--panel); box-shadow: 0 2px 0 rgba(8, 33, 63, .16);
        }
        header {
            display: grid; grid-template-columns: minmax(0, 1fr) auto auto;
            align-items: center; gap: 14px; padding: 7px 13px;
            color: white; border-radius: 15px;
            background: linear-gradient(120deg, var(--navy), #0a4b86);
        }
        .brand { display: flex; align-items: center; min-width: 0; gap: 10px; }
        .logos { display: flex; gap: 6px; flex: 0 0 auto; }
        .logo {
            display: grid; place-items: center; width: 48px; height: 48px;
            padding: 4px; border-radius: 10px; background: white;
        }
        .logo img { max-width: 100%; max-height: 100%; object-fit: contain; }
        .brand-copy { min-width: 0; }
        .brand-copy h1 { margin: 0; font-size: 1.27rem; line-height: 1.05; }
        .brand-copy p {
            margin: 3px 0 0; overflow: hidden; color: #d8e8f8;
            font-size: .71rem; white-space: nowrap; text-overflow: ellipsis;
        }
        .overall {
            min-width: 118px; padding: 9px 15px; border-radius: 12px;
            color: white; background: var(--amber); font-size: 1rem;
            font-weight: 900; text-align: center; letter-spacing: .05em;
        }
        .overall.sihat { background: var(--green); }
        .overall.gangguan { background: var(--red); }
        .clock { min-width: 132px; text-align: right; }
        .clock strong { display: block; font-size: 1.2rem; }
        .clock span { color: #d8e8f8; font-size: .72rem; }
        .health-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
        .metric { padding: 10px 12px; }
        .metric-label, .kicker {
            margin: 0; color: var(--muted); font-size: .75rem;
            font-weight: 800; letter-spacing: .07em; text-transform: uppercase;
        }
        .metric-value { margin: 6px 0 1px; font-size: 1.5rem; font-weight: 900; }
        .metric-note {
            margin: 0; overflow: hidden; color: var(--muted); font-size: .75rem;
            line-height: 1.2; white-space: nowrap; text-overflow: ellipsis;
        }
        .bar { height: 7px; margin-top: 8px; overflow: hidden; border-radius: 9px; background: #c8d5e3; }
        .bar span { display: block; width: 0; height: 100%; background: var(--blue); transition: width .2s; }
        .workspace { display: grid; grid-template-columns: 1.12fr .86fr 1.02fr; gap: 8px; min-height: 0; }
        .section { padding: 11px 12px; }
        .section-title { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
        .section-title h2 { margin: 0; font-size: .98rem; }
        .small-status { color: var(--muted); font-size: .72rem; font-weight: 800; }
        .network-stats {
            display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px;
            margin-top: 8px;
        }
        .network-stats div, .media-box {
            min-width: 0; padding: 7px 8px; border: 1px solid #9bb0c5;
            border-radius: 10px; background: #e3ebf4;
        }
        .network-stats span, .media-box small { display: block; color: var(--muted); font-size: .72rem; }
        .network-stats strong {
            display: block; margin-top: 2px; overflow: hidden; font-size: .79rem;
            white-space: nowrap; text-overflow: ellipsis;
        }
        .traffic { display: flex; justify-content: space-between; gap: 8px; margin-top: 7px; }
        .traffic div { min-width: 0; }
        .traffic span { color: var(--muted); font-size: .7rem; }
        .traffic strong { display: block; font-size: .82rem; }
        .chart-shell { height: 83px; margin-top: 6px; border: 1px solid #9bb0c5; border-radius: 9px; background: #e3ebf4; }
        canvas { display: block; width: 100%; height: 100%; }
        .service-list { display: grid; gap: 5px; margin-top: 8px; }
        .service-row {
            display: flex; align-items: center; justify-content: space-between;
            min-height: 31px; padding: 5px 8px; border: 1px solid #9bb0c5;
            border-radius: 9px; background: #e3ebf4;
            font-size: .78rem; font-weight: 700;
        }
        .state { display: inline-flex; align-items: center; gap: 5px; color: var(--muted); font-size: .72rem; }
        .state::before { width: 10px; height: 10px; border: 1px solid #263d55; border-radius: 50%; background: #52677e; content: ""; }
        .state.active::before { background: var(--green); }
        .state.warning::before { background: var(--amber); }
        .state.failed::before { background: var(--red); }
        .media-stack { display: grid; gap: 7px; margin-top: 8px; }
        .media-box { padding: 9px; }
        .media-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
        .media-head strong { font-size: .81rem; }
        .badge {
            flex: 0 0 auto; padding: 4px 7px; border-radius: 999px;
            color: white; background: #52677e; font-size: .69rem; font-weight: 900;
        }
        .badge.connected { background: var(--green); }
        .badge.disconnected { background: var(--amber); }
        .media-detail { margin: 5px 0 0; color: var(--muted); font-size: .73rem; line-height: 1.25; }
        .media-detail + .media-head { margin-top: 6px; padding-top: 6px; border-top: 2px solid var(--line); }
        .warning-note { color: #713900; }
        .control-button {
            width: 100%; min-height: 44px; margin-top: 8px; padding: 8px 10px;
            border: 0; border-radius: 10px; color: white; background: var(--blue);
            font-size: .72rem; font-weight: 900;
        }
        .control-button.disconnect { background: var(--red); }
        .control-button:disabled { cursor: not-allowed; opacity: .5; }
        .feedback { min-height: 16px; margin: 5px 0 0; color: var(--muted); font-size: .7rem; line-height: 1.2; }
        .actions { display: grid; grid-template-columns: 1.55fr repeat(5, 1fr); gap: 7px; }
        .action {
            display: flex; align-items: center; justify-content: center; min-height: 48px;
            padding: 5px 8px; border: 2px solid var(--line); border-radius: 11px;
            color: var(--navy); background: white; font-size: .72rem; font-weight: 800;
            text-align: center; text-decoration: none;
        }
        .action.primary { color: white; border-color: var(--blue); background: var(--blue); }
        .action.student-access {
            color: white; border: 2px solid #073f91; background: #075fc8;
            font-size: .78rem; letter-spacing: .02em;
        }
        .stale { opacity: .7; }
        dialog {
            width: min(560px, calc(100% - 30px)); padding: 18px;
            border: 0; border-radius: 16px; color: var(--ink); background: white;
        }
        dialog::backdrop { background: rgba(10, 28, 48, .66); }
        dialog h2 { margin: 0 0 10px; }
        dialog details { margin: 8px 0; padding: 10px; border: 1px solid #9bb0c5; border-radius: 10px; background: #e3ebf4; }
        dialog summary { min-height: 32px; cursor: pointer; font-weight: 800; }
        .access-value { display: block; margin: 8px 0; overflow-wrap: anywhere; user-select: text; }
        .dialog-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }
        .dialog-actions button { min-height: 44px; padding: 8px 14px; border: 0; border-radius: 9px; }
        #studentQrDialog {
            width: min(960px, calc(100% - 32px)); max-width: none;
            height: min(568px, calc(100% - 32px)); max-height: none; margin: auto;
            padding: 12px 14px; overflow: hidden; border: 3px solid #102846;
        }
        .student-layout {
            display: grid; grid-template-rows: auto minmax(0, 1fr) auto auto;
            gap: 7px; height: 100%;
        }
        .student-layout > h2 {
            margin: 0; color: #102846; font-size: 1.35rem; line-height: 1.1; text-align: center;
        }
        .qr-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; min-height: 0; }
        .qr-card {
            display: grid; grid-template-rows: auto minmax(0, 1fr) auto; min-width: 0;
            padding: 8px 10px; overflow: hidden; border: 3px solid #075fc8;
            border-radius: 13px; background: #eef5fc;
        }
        .qr-card h3 { margin: 0; color: #071a31; font-size: 1.08rem; text-align: center; }
        .qr-panel { display: grid; min-height: 0; place-items: center; }
        .qr-panel svg {
            display: block; width: auto; max-width: 100%; height: min(100%, 300px);
            border: 6px solid white; background: white; image-rendering: pixelated;
        }
        .qr-detail {
            min-height: 38px; margin: 3px 0 0; overflow-wrap: anywhere;
            color: #071a31; font-size: .86rem; line-height: 1.18; text-align: center;
        }
        .wifi-unconfigured {
            display: grid; place-items: center; min-height: 180px; padding: 14px;
            border: 4px solid #a91f32; color: #7d1022; background: white;
            font-size: 1.12rem; font-weight: 900; line-height: 1.25; text-align: center;
        }
        .student-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 0; }
        .student-steps p {
            margin: 0; padding: 5px 7px; border-left: 5px solid #075fc8;
            color: #102846; background: #e0ebf6; font-size: .78rem; font-weight: 800;
        }
        #closeStudentQr {
            width: 100%; min-height: 52px; border: 2px solid #102846; border-radius: 11px;
            color: white; background: #102846; font-size: 1rem; font-weight: 900;
        }
        :focus-visible { outline: 3px solid #f3ad29; outline-offset: 2px; }
        @media (max-width: 800px), (max-height: 520px) {
            body { overflow: auto; }
            .console { height: auto; min-height: 100%; grid-template-rows: auto; }
            header { grid-template-columns: 1fr auto; }
            .clock { display: none; }
            .health-grid { grid-template-columns: repeat(2, 1fr); }
            .workspace { grid-template-columns: 1fr; }
            .actions { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <main id="console" class="console">
        <header>
            <div class="brand">
                <div class="logos">
                    <div class="logo"><img src="/assets/logo-dvs.png" alt="Logo DVS"></div>
                    <div class="logo"><img src="/assets/logo-asth.png" alt="Logo ASTH"></div>
                </div>
                <div class="brand-copy">
                    <h1>ASTH Health Console</h1>
                    <p>Adaptive Smart Training Hub &middot; Raspberry Pi 5</p>
                </div>
            </div>
            <div id="overallStatus" class="overall">MEMUAT</div>
            <div class="clock"><strong id="clock">--:--</strong><span id="date">--</span><span id="uptime"> &middot; Uptime --</span></div>
        </header>

        <section class="health-grid" aria-label="Kesihatan sistem">
            <article class="panel metric">
                <p class="metric-label">CPU</p><p id="cpuValue" class="metric-value">--</p>
                <p id="cpuNote" class="metric-note">Suhu --</p><div class="bar"><span id="cpuBar"></span></div>
            </article>
            <article class="panel metric">
                <p class="metric-label">Memori RAM</p><p id="ramValue" class="metric-value">--</p>
                <p class="metric-note">Penggunaan semasa</p><div class="bar"><span id="ramBar"></span></div>
            </article>
            <article class="panel metric">
                <p class="metric-label">Storan Sistem</p><p id="rootValue" class="metric-value">--</p>
                <p id="rootNote" class="metric-note">Digunakan / jumlah</p><div class="bar"><span id="rootBar"></span></div>
            </article>
            <article class="panel metric">
                <p class="metric-label">Local Media Storage</p><p id="localValue" class="metric-value">--</p>
                <p id="localNote" class="metric-note">Mengesan storan...</p><div class="bar"><span id="localBar"></span></div>
            </article>
        </section>

        <section class="workspace">
            <article class="panel section">
                <div class="section-title"><h2>Rangkaian</h2><span id="ssid" class="small-status">Wi-Fi: --</span></div>
                <div class="network-stats">
                    <div><span>LAN IP</span><strong id="lanIp">--</strong></div>
                    <div><span>HOTSPOT IP</span><strong id="hotspotIp">--</strong></div>
                    <div><span>ASTH-PORTABLE</span><strong id="hotspotState">--</strong></div>
                    <div><span>PERANTI</span><strong id="devices">--</strong></div>
                </div>
                <div class="traffic">
                    <div><span>MUAT TURUN</span><strong id="rxRate">--</strong><span id="rxTotal">RX --</span></div>
                    <div><span>MUAT NAIK</span><strong id="txRate">--</strong><span id="txTotal">TX --</span></div>
                </div>
                <div class="chart-shell"><canvas id="networkChart" aria-label="Graf aktiviti rangkaian"></canvas></div>
            </article>

            <article class="panel section">
                <div class="section-title"><h2>Perkhidmatan</h2><span class="small-status">STATUS PROSES</span></div>
                <div class="service-list">
                    <div class="service-row">ASTH App <span id="serviceAsth" class="state">--</span></div>
                    <div class="service-row">Nginx <span id="serviceNginx" class="state">--</span></div>
                    <div class="service-row">Jellyfin <span id="serviceJellyfin" class="state">--</span></div>
                    <div class="service-row">Samba <span id="serviceSamba" class="state">--</span></div>
                    <div class="service-row">Cockpit <span id="serviceCockpit" class="state">--</span></div>
                    <div class="service-row">Uptime Kuma <span id="serviceKuma" class="state">--</span></div>
                </div>
            </article>

            <article class="panel section">
                <div class="section-title"><h2>Sumber Media</h2><span class="small-status">JELLYFIN</span></div>
                <div class="media-stack">
                    <div class="media-box">
                        <div class="media-head"><strong>LOCAL MEDIA STORAGE</strong><span id="localBadge" class="badge">UNAVAILABLE</span></div>
                        <p id="localMediaDetail" class="media-detail">Status storan tempatan tidak tersedia.</p>
                    </div>
                    <div class="media-box">
                        <div class="media-head"><strong>WireGuard</strong><span id="wireguardBadge" class="badge">UNAVAILABLE</span></div>
                        <p id="wireguardDetail" class="media-detail">Status Office tunnel tidak tersedia.</p>
                        <div class="media-head"><strong>ITUNAS Media</strong><span id="itunasBadge" class="badge">UNAVAILABLE</span></div>
                        <p id="itunasDetail" class="media-detail">Status media jauh tidak tersedia.</p>
                        <button id="itunasControl" class="control-button" type="button" disabled>ITUNAS UNAVAILABLE</button>
                        <p id="itunasFeedback" class="feedback" aria-live="polite"></p>
                    </div>
                </div>
            </article>
        </section>

        <nav class="actions" aria-label="Akses perkhidmatan">
            <button id="studentAccessButton" class="action student-access" type="button">AKSES PELAJAR / QR</button>
            <a class="action primary" href="/learn/">Learning Hub</a>
            <a id="jellyfinLink" class="action" href="#" target="_blank" rel="noopener">Jellyfin</a>
            <a id="uptimeLink" class="action" href="#" target="_blank" rel="noopener">Uptime Kuma</a>
            <a id="cockpitLink" class="action" href="#" target="_blank" rel="noopener">Cockpit</a>
            <button id="accessButton" class="action" type="button">Akses ROG / SSH</button>
        </nav>
    </main>

    <dialog id="studentQrDialog" aria-labelledby="studentQrTitle">
        <div class="student-layout">
            <h2 id="studentQrTitle">Akses Pelajar / Pelawat</h2>
            <div class="qr-grid">
                <section class="qr-card" aria-labelledby="wifiQrHeading">
                    <h3 id="wifiQrHeading">SAMBUNG WI-FI</h3>
                    <div class="qr-panel"><!-- ASTH_WIFI_ACCESS --></div>
                </section>
                <section class="qr-card" aria-labelledby="portalQrHeading">
                    <h3 id="portalQrHeading">BUKA PORTAL ASTH</h3>
                    <div class="qr-panel">
                <svg id="portalQr" data-qr-target="http://10.42.0.1/" role="img" aria-labelledby="portalQrTitle" viewBox="0 0 33 33" shape-rendering="crispEdges">
                    <title id="portalQrTitle">Kod QR Portal ASTH http://10.42.0.1/</title>
                    <rect width="33" height="33" fill="#ffffff"/>
                    <path fill="#000000" d="M4 4h1v1h-1zM5 4h1v1h-1zM6 4h1v1h-1zM7 4h1v1h-1zM8 4h1v1h-1zM9 4h1v1h-1zM10 4h1v1h-1zM13 4h1v1h-1zM16 4h1v1h-1zM17 4h1v1h-1zM18 4h1v1h-1zM20 4h1v1h-1zM22 4h1v1h-1zM23 4h1v1h-1zM24 4h1v1h-1zM25 4h1v1h-1zM26 4h1v1h-1zM27 4h1v1h-1zM28 4h1v1h-1zM4 5h1v1h-1zM10 5h1v1h-1zM14 5h1v1h-1zM15 5h1v1h-1zM16 5h1v1h-1zM18 5h1v1h-1zM19 5h1v1h-1zM20 5h1v1h-1zM22 5h1v1h-1zM28 5h1v1h-1zM4 6h1v1h-1zM6 6h1v1h-1zM7 6h1v1h-1zM8 6h1v1h-1zM10 6h1v1h-1zM12 6h1v1h-1zM13 6h1v1h-1zM14 6h1v1h-1zM16 6h1v1h-1zM17 6h1v1h-1zM18 6h1v1h-1zM19 6h1v1h-1zM22 6h1v1h-1zM24 6h1v1h-1zM25 6h1v1h-1zM26 6h1v1h-1zM28 6h1v1h-1zM4 7h1v1h-1zM6 7h1v1h-1zM7 7h1v1h-1zM8 7h1v1h-1zM10 7h1v1h-1zM13 7h1v1h-1zM14 7h1v1h-1zM15 7h1v1h-1zM17 7h1v1h-1zM18 7h1v1h-1zM22 7h1v1h-1zM24 7h1v1h-1zM25 7h1v1h-1zM26 7h1v1h-1zM28 7h1v1h-1zM4 8h1v1h-1zM6 8h1v1h-1zM7 8h1v1h-1zM8 8h1v1h-1zM10 8h1v1h-1zM14 8h1v1h-1zM18 8h1v1h-1zM19 8h1v1h-1zM20 8h1v1h-1zM22 8h1v1h-1zM24 8h1v1h-1zM25 8h1v1h-1zM26 8h1v1h-1zM28 8h1v1h-1zM4 9h1v1h-1zM10 9h1v1h-1zM13 9h1v1h-1zM17 9h1v1h-1zM19 9h1v1h-1zM20 9h1v1h-1zM22 9h1v1h-1zM28 9h1v1h-1zM4 10h1v1h-1zM5 10h1v1h-1zM6 10h1v1h-1zM7 10h1v1h-1zM8 10h1v1h-1zM9 10h1v1h-1zM10 10h1v1h-1zM12 10h1v1h-1zM14 10h1v1h-1zM16 10h1v1h-1zM18 10h1v1h-1zM20 10h1v1h-1zM22 10h1v1h-1zM23 10h1v1h-1zM24 10h1v1h-1zM25 10h1v1h-1zM26 10h1v1h-1zM27 10h1v1h-1zM28 10h1v1h-1zM12 11h1v1h-1zM13 11h1v1h-1zM14 11h1v1h-1zM16 11h1v1h-1zM17 11h1v1h-1zM18 11h1v1h-1zM19 11h1v1h-1zM4 12h1v1h-1zM5 12h1v1h-1zM6 12h1v1h-1zM8 12h1v1h-1zM9 12h1v1h-1zM10 12h1v1h-1zM11 12h1v1h-1zM12 12h1v1h-1zM14 12h1v1h-1zM15 12h1v1h-1zM18 12h1v1h-1zM21 12h1v1h-1zM22 12h1v1h-1zM26 12h1v1h-1zM4 13h1v1h-1zM5 13h1v1h-1zM6 13h1v1h-1zM8 13h1v1h-1zM12 13h1v1h-1zM14 13h1v1h-1zM15 13h1v1h-1zM18 13h1v1h-1zM21 13h1v1h-1zM22 13h1v1h-1zM23 13h1v1h-1zM28 13h1v1h-1zM10 14h1v1h-1zM11 14h1v1h-1zM12 14h1v1h-1zM13 14h1v1h-1zM17 14h1v1h-1zM20 14h1v1h-1zM21 14h1v1h-1zM24 14h1v1h-1zM26 14h1v1h-1zM27 14h1v1h-1zM28 14h1v1h-1zM5 15h1v1h-1zM15 15h1v1h-1zM20 15h1v1h-1zM21 15h1v1h-1zM22 15h1v1h-1zM23 15h1v1h-1zM27 15h1v1h-1zM4 16h1v1h-1zM5 16h1v1h-1zM6 16h1v1h-1zM7 16h1v1h-1zM8 16h1v1h-1zM10 16h1v1h-1zM11 16h1v1h-1zM12 16h1v1h-1zM16 16h1v1h-1zM19 16h1v1h-1zM20 16h1v1h-1zM22 16h1v1h-1zM23 16h1v1h-1zM25 16h1v1h-1zM27 16h1v1h-1zM28 16h1v1h-1zM12 17h1v1h-1zM13 17h1v1h-1zM15 17h1v1h-1zM16 17h1v1h-1zM17 17h1v1h-1zM22 17h1v1h-1zM23 17h1v1h-1zM25 17h1v1h-1zM28 17h1v1h-1zM4 18h1v1h-1zM8 18h1v1h-1zM10 18h1v1h-1zM11 18h1v1h-1zM14 18h1v1h-1zM15 18h1v1h-1zM16 18h1v1h-1zM18 18h1v1h-1zM20 18h1v1h-1zM21 18h1v1h-1zM22 18h1v1h-1zM23 18h1v1h-1zM24 18h1v1h-1zM26 18h1v1h-1zM27 18h1v1h-1zM28 18h1v1h-1zM5 19h1v1h-1zM13 19h1v1h-1zM16 19h1v1h-1zM17 19h1v1h-1zM18 19h1v1h-1zM19 19h1v1h-1zM21 19h1v1h-1zM23 19h1v1h-1zM25 19h1v1h-1zM27 19h1v1h-1zM4 20h1v1h-1zM6 20h1v1h-1zM7 20h1v1h-1zM8 20h1v1h-1zM10 20h1v1h-1zM12 20h1v1h-1zM14 20h1v1h-1zM15 20h1v1h-1zM18 20h1v1h-1zM20 20h1v1h-1zM21 20h1v1h-1zM22 20h1v1h-1zM23 20h1v1h-1zM24 20h1v1h-1zM25 20h1v1h-1zM12 21h1v1h-1zM15 21h1v1h-1zM18 21h1v1h-1zM20 21h1v1h-1zM24 21h1v1h-1zM25 21h1v1h-1zM26 21h1v1h-1zM27 21h1v1h-1zM28 21h1v1h-1zM4 22h1v1h-1zM5 22h1v1h-1zM6 22h1v1h-1zM7 22h1v1h-1zM8 22h1v1h-1zM9 22h1v1h-1zM10 22h1v1h-1zM12 22h1v1h-1zM17 22h1v1h-1zM19 22h1v1h-1zM20 22h1v1h-1zM22 22h1v1h-1zM24 22h1v1h-1zM27 22h1v1h-1zM28 22h1v1h-1zM4 23h1v1h-1zM10 23h1v1h-1zM12 23h1v1h-1zM15 23h1v1h-1zM19 23h1v1h-1zM20 23h1v1h-1zM24 23h1v1h-1zM25 23h1v1h-1zM4 24h1v1h-1zM6 24h1v1h-1zM7 24h1v1h-1zM8 24h1v1h-1zM10 24h1v1h-1zM12 24h1v1h-1zM13 24h1v1h-1zM16 24h1v1h-1zM20 24h1v1h-1zM21 24h1v1h-1zM22 24h1v1h-1zM23 24h1v1h-1zM24 24h1v1h-1zM28 24h1v1h-1zM4 25h1v1h-1zM6 25h1v1h-1zM7 25h1v1h-1zM8 25h1v1h-1zM10 25h1v1h-1zM13 25h1v1h-1zM14 25h1v1h-1zM15 25h1v1h-1zM16 25h1v1h-1zM17 25h1v1h-1zM19 25h1v1h-1zM20 25h1v1h-1zM21 25h1v1h-1zM24 25h1v1h-1zM26 25h1v1h-1zM4 26h1v1h-1zM6 26h1v1h-1zM7 26h1v1h-1zM8 26h1v1h-1zM10 26h1v1h-1zM12 26h1v1h-1zM15 26h1v1h-1zM16 26h1v1h-1zM18 26h1v1h-1zM19 26h1v1h-1zM21 26h1v1h-1zM24 26h1v1h-1zM25 26h1v1h-1zM28 26h1v1h-1zM4 27h1v1h-1zM10 27h1v1h-1zM12 27h1v1h-1zM16 27h1v1h-1zM17 27h1v1h-1zM18 27h1v1h-1zM19 27h1v1h-1zM20 27h1v1h-1zM21 27h1v1h-1zM24 27h1v1h-1zM25 27h1v1h-1zM27 27h1v1h-1zM4 28h1v1h-1zM5 28h1v1h-1zM6 28h1v1h-1zM7 28h1v1h-1zM8 28h1v1h-1zM9 28h1v1h-1zM10 28h1v1h-1zM12 28h1v1h-1zM13 28h1v1h-1zM14 28h1v1h-1zM15 28h1v1h-1zM18 28h1v1h-1zM20 28h1v1h-1zM23 28h1v1h-1zM27 28h1v1h-1zM28 28h1v1h-1z"/>
                </svg>
                    </div>
                    <p class="qr-detail"><strong>Portal:</strong> http://10.42.0.1/</p>
                </section>
            </div>
            <div class="student-steps" aria-label="Langkah akses">
                <p>1. Sambung ke Wi-Fi ASTH-PORTABLE</p>
                <p>2. Imbas QR Portal</p>
                <p>3. Akses perkhidmatan ASTH</p>
            </div>
            <button id="closeStudentQr" type="button">KEMBALI / TUTUP</button>
        </div>
    </dialog>

    <dialog id="accessDialog">
        <h2>Akses Pentadbiran</h2>
        <details open><summary>ROG Drive</summary><code id="rogAddress" class="access-value"></code><p>Username: <strong>asthadmin</strong>. Password stored privately.</p><button id="copyRog" type="button">Copy network address</button></details>
        <details><summary>SSH</summary><code id="sshCommand" class="access-value"></code><p>Use the ASTH server administrator account.</p><button id="copySsh" type="button">Copy SSH command</button></details>
        <p id="copyStatus" class="feedback" aria-live="polite"></p>
        <div class="dialog-actions"><button id="closeDialog" type="button">Tutup</button></div>
    </dialog>

    <script>
        const byId = id => document.getElementById(id);
        const canvas = byId("networkChart");
        const context = canvas.getContext("2d");
        const consoleElement = byId("console");
        const localControlHost = ["127.0.0.1", "localhost", "::1"].includes(location.hostname);
        let previous = null;
        let currentItunasStatus = "unavailable";
        let refreshInFlight = false;
        let refreshTimer = null;
        let rxHistory = Array(24).fill(0);
        let txHistory = Array(24).fill(0);

        byId("uptimeLink").href = `http://${location.hostname}:3001`;
        byId("cockpitLink").href = `https://${location.hostname}:9090`;
        byId("jellyfinLink").href = `http://${location.hostname}:8096`;
        const uncSeparator = String.fromCharCode(92);
        byId("rogAddress").textContent = uncSeparator.repeat(2) + location.hostname + uncSeparator + "ROG-Drive";
        byId("sshCommand").textContent = `ssh asthadmin@${location.hostname}`;

        function formatBytes(bytes) {
            if (!Number.isFinite(bytes)) return "--";
            if (bytes === 0) return "0 B";
            const units = ["B", "KB", "MB", "GB", "TB"];
            const index = Math.min(Math.floor(Math.log(Math.max(bytes, 1)) / Math.log(1024)), units.length - 1);
            return (bytes / Math.pow(1024, index)).toFixed(index ? 1 : 0) + " " + units[index];
        }
        function percent(value) { return Number.isFinite(value) ? value.toFixed(1) + "%" : "--"; }
        function setBar(id, value) { byId(id).style.width = Number.isFinite(value) ? Math.min(100, Math.max(0, value)) + "%" : "0"; }
        function formatUptime(seconds) {
            if (!Number.isFinite(seconds)) return "--";
            const days = Math.floor(seconds / 86400), hours = Math.floor((seconds % 86400) / 3600);
            return days ? `${days}h ${hours}j` : `${hours}j ${Math.floor((seconds % 3600) / 60)}m`;
        }
        function updateClock() {
            const now = new Date();
            byId("clock").textContent = now.toLocaleTimeString("ms-MY", {hour: "2-digit", minute: "2-digit"});
            byId("date").textContent = now.toLocaleDateString("ms-MY", {weekday: "short", day: "numeric", month: "short"});
        }
        function setOverall(value) {
            const state = ["sihat", "amaran", "gangguan"].includes(value) ? value : "amaran";
            byId("overallStatus").className = "overall " + state;
            byId("overallStatus").textContent = state.toUpperCase();
        }
        function setService(id, value) {
            const node = byId(id);
            const labels = {active: "AKTIF", inactive: "BERHENTI", failed: "GAGAL", activating: "BERMULA", deactivating: "BERHENTI"};
            node.textContent = labels[value] || "TIDAK TERSEDIA";
            node.className = "state " + (value === "active" ? "active" : value === "failed" ? "failed" : value && value !== "unknown" ? "warning" : "");
        }
        function renderStorage(storage) {
            const available = storage && storage.status === "connected";
            return available ? `${formatBytes(storage.used_bytes)} / ${formatBytes(storage.total_bytes)}` : storage && storage.status === "disconnected" ? "OFFLINE" : "--";
        }
        function renderItunas(media, tunnel) {
            currentItunasStatus = media && media.status || "unavailable";
            const wireguardBadge = byId("wireguardBadge"), wireguardDetail = byId("wireguardDetail");
            const wireguardStatus = ["connected", "disconnected"].includes(tunnel) ? tunnel : "unavailable";
            wireguardBadge.className = "badge " + wireguardStatus;
            wireguardBadge.textContent = wireguardStatus.toUpperCase();
            wireguardDetail.textContent = wireguardStatus === "connected"
                ? "Office tunnel aktif (status sahaja)."
                : wireguardStatus === "disconnected"
                    ? "Office tunnel tidak bersambung."
                    : "Status Office tunnel tidak dapat disahkan.";
            const badge = byId("itunasBadge"), button = byId("itunasControl"), detail = byId("itunasDetail");
            badge.className = "badge " + currentItunasStatus;
            badge.textContent = currentItunasStatus.toUpperCase();
            if (currentItunasStatus === "connected") {
                detail.textContent = "Media jauh tersedia. Main balik Jellyfin menggunakan internet lokasi ASTH.";
                detail.className = "media-detail warning-note";
                button.textContent = "DISCONNECT ITUNAS"; button.className = "control-button disconnect";
            } else if (currentItunasStatus === "disconnected") {
                detail.textContent = "Media jauh tidak dipasang.";
                detail.className = "media-detail";
                button.textContent = "CONNECT ITUNAS"; button.className = "control-button";
            } else {
                detail.textContent = "Status ITUNAS tidak dapat disahkan.";
                detail.className = "media-detail";
                button.textContent = "ITUNAS UNAVAILABLE"; button.className = "control-button";
            }
            button.disabled = !localControlHost || currentItunasStatus === "unavailable";
            if (!localControlHost) byId("itunasFeedback").textContent = "Kawalan hanya tersedia pada skrin sentuh tempatan.";
        }
        function render(data) {
            setOverall(data.overall_status);
            byId("cpuValue").textContent = percent(data.cpu_used_percent);
            byId("cpuNote").textContent = Number.isFinite(data.cpu_temperature_c) ? `Suhu ${data.cpu_temperature_c.toFixed(1)} °C` : "Suhu tidak tersedia";
            byId("ramValue").textContent = percent(data.ram_used_percent);
            byId("rootValue").textContent = percent(data.root_storage && data.root_storage.used_percent);
            byId("rootNote").textContent = renderStorage(data.root_storage);
            byId("localValue").textContent = percent(data.local_media_storage && data.local_media_storage.used_percent);
            byId("localNote").textContent = renderStorage(data.local_media_storage);
            setBar("cpuBar", data.cpu_used_percent); setBar("ramBar", data.ram_used_percent);
            setBar("rootBar", data.root_storage && data.root_storage.used_percent);
            setBar("localBar", data.local_media_storage && data.local_media_storage.used_percent);
            const network = data.network || {};
            byId("lanIp").textContent = network.lan_ip || "TIDAK TERSEDIA";
            byId("hotspotIp").textContent = network.hotspot_ip || "TIDAK TERSEDIA";
            byId("hotspotState").textContent = network.hotspot_state === "connected" ? "AKTIF" : network.hotspot_state === "disconnected" ? "OFFLINE" : "TIDAK TERSEDIA";
            byId("devices").textContent = Number.isFinite(data.connected_devices) ? data.connected_devices : "--";
            byId("ssid").textContent = "Wi-Fi: " + (data.wifi_ssid || "TIDAK TERSEDIA");
            byId("uptime").textContent = " · Uptime " + formatUptime(data.uptime_seconds);
            setService("serviceAsth", data.service_asth); setService("serviceNginx", data.service_nginx);
            setService("serviceJellyfin", data.service_jellyfin); setService("serviceSamba", data.service_smbd);
            setService("serviceCockpit", data.service_cockpit); setService("serviceKuma", data.service_uptime_kuma);
            const local = data.local_media_storage || {};
            byId("localBadge").className = "badge " + (local.status || "unavailable");
            byId("localBadge").textContent = (local.status || "unavailable").toUpperCase();
            byId("localMediaDetail").textContent = local.status === "connected" ? `${local.mount_point || "Media tempatan"} · ${renderStorage(local)}` : "Storan media tempatan tidak bersambung.";
            renderItunas(data.itunas_media, data.office_tunnel);
        }
        function drawChart() {
            const ratio = window.devicePixelRatio || 1, width = canvas.clientWidth, height = canvas.clientHeight;
            if (!width || !height) return;
            canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
            context.setTransform(ratio, 0, 0, ratio, 0, 0); context.clearRect(0, 0, width, height);
            const maximum = Math.max(...rxHistory, ...txHistory, 1024);
            function plot(values, colour) {
                context.beginPath(); context.strokeStyle = colour; context.lineWidth = 2.5;
                values.forEach((value, index) => {
                    const x = index / (values.length - 1) * width;
                    const y = height - value / maximum * (height - 12) - 6;
                    index ? context.lineTo(x, y) : context.moveTo(x, y);
                });
                context.stroke();
            }
            plot(rxHistory, "#12a9c8"); plot(txHistory, "#1f68d5");
        }
        async function refreshStatus() {
            if (refreshInFlight) return;
            refreshInFlight = true;
            clearTimeout(refreshTimer);
            try {
                const response = await fetch("/api/hub-status", {cache: "no-store"});
                if (!response.ok) throw new Error("status_failed");
                const data = await response.json(), now = Date.now();
                let rx = 0, tx = 0;
                if (previous && Number.isFinite(previous.rx) && Number.isFinite(previous.tx)
                    && Number.isFinite(data.rx_bytes) && Number.isFinite(data.tx_bytes)) {
                    const seconds = Math.max((now - previous.time) / 1000, 1);
                    rx = Math.max((data.rx_bytes - previous.rx) / seconds, 0);
                    tx = Math.max((data.tx_bytes - previous.tx) / seconds, 0);
                }
                previous = Number.isFinite(data.rx_bytes) && Number.isFinite(data.tx_bytes)
                    ? {time: now, rx: data.rx_bytes, tx: data.tx_bytes} : null;
                rxHistory.push(rx); txHistory.push(tx); rxHistory.shift(); txHistory.shift();
                byId("rxRate").textContent = formatBytes(rx) + "/s";
                byId("txRate").textContent = formatBytes(tx) + "/s";
                byId("rxTotal").textContent = "RX " + formatBytes(data.rx_bytes);
                byId("txTotal").textContent = "TX " + formatBytes(data.tx_bytes);
                render(data); drawChart(); consoleElement.classList.remove("stale");
            } catch (error) {
                setOverall("gangguan"); consoleElement.classList.add("stale");
                byId("itunasFeedback").textContent = "Data sistem tidak tersedia. Cubaan semula sedang berjalan.";
            } finally {
                refreshInFlight = false;
                refreshTimer = setTimeout(refreshStatus, 5000);
            }
        }
        async function controlItunas() {
            const action = currentItunasStatus === "connected" ? "disconnect" : "connect";
            const verb = action === "connect" ? "CONNECT ITUNAS" : "DISCONNECT ITUNAS";
            if (!window.confirm(`${verb}? Perubahan ini hanya menukar mount ITUNAS Media.`)) return;
            const button = byId("itunasControl"); button.disabled = true;
            byId("itunasFeedback").textContent = action === "connect" ? "Menyambung ITUNAS Media..." : "Memutuskan ITUNAS Media...";
            try {
                const response = await fetch("/api/itunas-control", {
                    method: "POST", headers: {"Content-Type": "application/json", "X-ASTH-Control": "touchscreen"},
                    body: JSON.stringify({action})
                });
                const result = await response.json();
                const errors = {
                    office_tunnel_unavailable: "Office WireGuard tunnel tidak tersedia. ITUNAS Media tidak diubah.",
                    control_timeout: "Kawalan ITUNAS Media tamat masa.",
                    control_unavailable: "Kawalan ITUNAS Media tidak tersedia.",
                    control_failed: "Kawalan ITUNAS Media gagal.",
                    state_not_reached: "Keadaan ITUNAS Media tidak dapat disahkan."
                };
                byId("itunasFeedback").textContent = result.success
                    ? (action === "connect" ? "ITUNAS Media berjaya disambungkan." : "ITUNAS Media berjaya diputuskan.")
                    : (errors[result.error] || "Tindakan ITUNAS Media gagal.");
            } catch (error) {
                byId("itunasFeedback").textContent = "Tindakan gagal. Servis kawalan tidak tersedia.";
            }
            while (refreshInFlight) await new Promise(resolve => setTimeout(resolve, 50));
            await refreshStatus();
        }
        async function copyAccess(id, message) {
            try { await navigator.clipboard.writeText(byId(id).textContent); byId("copyStatus").textContent = message; }
            catch (error) { byId("copyStatus").textContent = "Salinan automatik tidak tersedia. Sila salin secara manual."; }
        }
        const dialog = byId("accessDialog");
        const studentQrDialog = byId("studentQrDialog");
        byId("studentAccessButton").addEventListener("click", () => {
            studentQrDialog.showModal();
            byId("closeStudentQr").focus();
        });
        byId("closeStudentQr").addEventListener("click", () => studentQrDialog.close());
        byId("accessButton").addEventListener("click", () => dialog.showModal());
        byId("closeDialog").addEventListener("click", () => dialog.close());
        byId("copyRog").addEventListener("click", () => copyAccess("rogAddress", "Alamat ROG Drive disalin."));
        byId("copySsh").addEventListener("click", () => copyAccess("sshCommand", "Perintah SSH disalin."));
        byId("itunasControl").addEventListener("click", controlItunas);
        window.addEventListener("resize", drawChart);
        updateClock(); setInterval(updateClock, 1000); refreshStatus();
    </script>
</body>
</html>
"""


PARTICIPANT_PAGE = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASTH Learning Portal</title>
    <style>
        :root { --navy: #08213f; --blue: #0755b8; --ink: #071a31; --bg: #dce7f2; }
        * { box-sizing: border-box; }
        html, body { min-height: 100%; margin: 0; }
        body {
            display: grid; min-height: 100dvh; place-items: center; padding: 24px;
            color: var(--ink); background: var(--bg); font-family: "Segoe UI", Arial, sans-serif;
        }
        main {
            width: min(680px, 100%); padding: clamp(24px, 5vw, 48px);
            border: 3px solid #52708e; border-radius: 22px; background: white;
            box-shadow: 0 8px 24px rgba(8, 33, 63, .22); text-align: center;
        }
        .logos { display: flex; justify-content: center; gap: 14px; margin-bottom: 20px; }
        .logo {
            display: grid; width: 82px; height: 82px; padding: 8px; place-items: center;
            border: 2px solid #7893ae; border-radius: 16px; background: white;
        }
        .logo img { max-width: 100%; max-height: 100%; object-fit: contain; }
        h1 { margin: 0; color: var(--navy); font-size: clamp(1.8rem, 6vw, 2.7rem); line-height: 1.08; }
        .welcome { margin: 16px auto 24px; max-width: 520px; color: #304b67; font-size: 1.08rem; line-height: 1.5; }
        nav { display: grid; gap: 14px; }
        .primary-action {
            display: grid; min-height: 62px; padding: 14px 18px; place-items: center;
            border: 3px solid #073f91; border-radius: 13px; color: white;
            background: var(--blue); font-size: 1.05rem; font-weight: 900;
            letter-spacing: .02em; text-decoration: none;
        }
        .primary-action:focus-visible { outline: 4px solid #f3ad29; outline-offset: 3px; }
        .note { margin: 20px 0 0; color: #49627b; font-size: .9rem; }
    </style>
</head>
<body>
    <main>
        <div class="logos" aria-label="ASTH">
            <div class="logo"><img src="/assets/logo-dvs.png" alt="Logo DVS"></div>
            <div class="logo"><img src="/assets/logo-asth.png" alt="Logo ASTH"></div>
        </div>
        <h1>ASTH Learning Portal</h1>
        <p class="welcome">Selamat datang. Peranti anda telah disambungkan ke rangkaian tempatan ASTH.</p>
        <nav aria-label="Akses pembelajaran">
            <a class="primary-action" href="/learn/">MASUK LEARNING HUB</a>
            <a class="primary-action" href="__ASTH_JELLYFIN_URL__">BUKA JELLYFIN</a>
        </nav>
        <p class="note">Akses tempatan melalui ASTH-PORTABLE atau rangkaian LAN.</p>
    </main>
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

        .available {
            display: inline-block;
            margin-bottom: 12px;
            padding: 7px 10px;
            border-radius: 999px;
            color: #075b34;
            background: #baf4d2;
            font-size: 0.69rem;
            font-weight: 900;
        }

        .module-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin-top: 12px;
        }

        .module-meta span {
            padding: 6px 9px;
            border: 2px solid #aec3e4;
            border-radius: 999px;
            color: var(--dark);
            background: #edf4ff;
            font-size: 0.72rem;
            font-weight: 800;
        }

        .module-action {
            display: inline-block;
            margin-top: 16px;
            padding: 10px 14px;
            border: 3px solid white;
            border-radius: 13px;
            color: white;
            background: linear-gradient(145deg, #4e88fa, #2862dd);
            box-shadow: 3px 4px 0 #1749b5;
            font-size: 0.76rem;
            font-weight: 900;
            text-decoration: none;
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
                    <p class="subtitle">Latihan praktikal di mana sahaja.</p>
                </div>
            </div>

            <a class="back" href="/">&#8592; Kembali ke Hub</a>
        </header>

        <section class="intro">
            <h2>Learning Pack ASTH</h2>
            <p>
                Kandungan latihan ringkas, praktikal dan offline-first
                untuk digunakan terus di lokasi latihan.
            </p>
        </section>

        <section class="modules">
            <article class="module">
                <div class="icon">&#128736;</div>
                <span class="available">TERSEDIA</span>
                <h3>Persediaan Reban &amp; Brooder</h3>
                <p>Persediaan asas sebelum anak ayam tiba dan pemerhatian awal selepas kemasukan.</p>
                <div class="module-meta">
                    <span>&plusmn;10 minit</span><span>Praktikal</span><span>Offline</span>
                </div>
                <a class="module-action" href="/learn/packs/reban-brooder/">MULA</a>
            </article>

            <article class="module">
                <div class="icon">&#128737;</div>
                <span class="available">LIVE</span>
                <h3>Biosekuriti Asas Ladang</h3>
                <p>Kawalan kemasukan, makhluk perosak serta penyelenggaraan parit dan pagar.</p>
                <div class="module-meta">
                    <span>7 bahagian</span><span>Praktikal</span><span>Offline</span>
                </div>
                <a class="module-action" href="/learn/packs/biosekuriti/">MULA</a>
            </article>

            <article class="module">
                <div class="icon">&#129370;</div>
                <h3>Pengendalian Telur Bernas</h3>
                <p>Pengenalan praktikal kepada pemerhatian dan pengendalian asas telur bernas.</p>
                <span class="coming">AKAN DATANG</span>
            </article>
        </section>

        <footer>
            ASTH Learning Hub &#183; Institut Teknologi Unggas
        </footer>
    </main>
</body>
</html>
"""


LEARNING_SUBPAGE_STYLE = """
    :root {
        --blue: #3977f6; --dark: #17335b; --muted: #657792;
        --yellow: #ffd45c; --line: #aec3e4;
        --shadow: 6px 8px 0 rgba(41, 83, 151, .12), 10px 14px 24px rgba(47, 74, 119, .14);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
        min-height: 100vh; margin: 0; color: var(--dark);
        background: radial-gradient(circle at 10% 8%, #fff0a7, transparent 24%),
                    radial-gradient(circle at 90% 10%, #b9eaff, transparent 25%),
                    linear-gradient(145deg, #dfeaff, #f9fbff 50%, #dcecff);
        font-family: Inter, ui-rounded, "Segoe UI", Arial, sans-serif;
    }
    .learning-page { width: min(980px, calc(100% - 28px)); margin: auto; padding: 22px 0 32px; }
    .learning-header {
        display: flex; align-items: center; justify-content: space-between; gap: 18px;
        padding: 18px 20px; border: 3px solid white; border-radius: 25px;
        background: rgba(250, 252, 255, .94); box-shadow: var(--shadow);
    }
    .learning-brand { display: flex; align-items: center; gap: 14px; min-width: 0; }
    .learning-logos { display: flex; gap: 7px; flex: 0 0 auto; }
    .learning-logo {
        display: grid; width: 58px; height: 58px; padding: 6px; place-items: center;
        border: 3px solid white; border-radius: 17px; background: white;
        box-shadow: 4px 5px 0 rgba(38, 88, 170, .16);
    }
    .learning-logo img { max-width: 100%; max-height: 100%; object-fit: contain; }
    .learning-eyebrow {
        margin: 0 0 4px; color: var(--blue); font-size: .7rem; font-weight: 900;
        letter-spacing: .1em; text-transform: uppercase;
    }
    h1 { margin: 0; font-size: clamp(1.5rem, 4vw, 2.2rem); }
    .learning-subtitle { margin: 5px 0 0; color: var(--muted); font-size: .84rem; }
    .learning-back, .learning-action {
        display: inline-block; padding: 11px 15px; border: 3px solid white;
        border-radius: 14px; color: white; background: linear-gradient(145deg, #4e88fa, #2862dd);
        box-shadow: 4px 5px 0 #1749b5; font-size: .8rem; font-weight: 900;
        text-align: center; text-decoration: none;
    }
    .learning-panel {
        margin-top: 18px; padding: clamp(20px, 4vw, 30px); border: 3px solid white;
        border-radius: 25px; background: rgba(249, 252, 255, .96); box-shadow: var(--shadow);
    }
    .demo-label {
        display: inline-block; margin-bottom: 10px; padding: 7px 10px; border-radius: 999px;
        color: #795b12; background: #fff1bd; font-size: .7rem; font-weight: 900;
    }
    .learning-panel p { color: var(--muted); line-height: 1.6; }
    .topic-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 20px; padding: 0; list-style: none; }
    .topic-list li, .topic-list a {
        padding: 8px 10px; border: 2px solid var(--line); border-radius: 999px;
        color: var(--dark); background: #edf4ff; font-size: .78rem; font-weight: 800;
        text-decoration: none;
    }
    .lesson-section {
        margin-top: 14px; padding: 20px; border: 2px solid var(--line);
        border-radius: 18px; background: white;
    }
    .lesson-section h2 { margin: 0 0 8px; font-size: 1.25rem; }
    .lesson-section p { margin: 0; }
    .end-panel { text-align: center; background: linear-gradient(145deg, #ffe591, #ffc870); }
    .end-panel p { color: #665842; }
    footer { margin-top: 22px; color: var(--muted); font-size: .74rem; text-align: center; }
    @media (max-width: 650px) {
        .learning-header { align-items: stretch; flex-direction: column; }
        .learning-brand { align-items: flex-start; flex-direction: column; }
        .learning-back, .learning-action { width: 100%; }
        .learning-logo { width: 54px; height: 54px; }
    }
"""


MODULE_LIST_PAGE = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modul Pembelajaran ASTH</title>
    <style>
""" + LEARNING_SUBPAGE_STYLE + """
    .module-card h2 { margin: 0 0 8px; font-size: clamp(1.35rem, 3vw, 1.8rem); }
</style>
</head>
<body>
    <main class="learning-page">
        <header class="learning-header">
            <div class="learning-brand">
                <div class="learning-logos">
                    <div class="learning-logo"><img src="/assets/logo-dvs.png" alt="Logo DVS"></div>
                    <div class="learning-logo"><img src="/assets/logo-asth.png" alt="Logo ASTH"></div>
                </div>
                <div>
                    <p class="learning-eyebrow">ASTH Learning Hub</p>
                    <h1>Modul Pembelajaran</h1>
                    <p class="learning-subtitle">Koleksi modul latihan yang tersedia secara tempatan.</p>
                </div>
            </div>
            <a class="learning-back" href="/learn/">&#8592; Kembali</a>
        </header>

        <article class="learning-panel module-card">
            <span class="demo-label">MODUL DEMO</span>
            <h2>Asas Penternakan Ayam Kampung</h2>
            <p>
                Pengenalan ringkas kepada perkara asas yang akan diperhatikan dalam pembelajaran
                ayam kampung. Kandungan ini ialah demonstrasi struktur modul ASTH.
            </p>
            <ul class="topic-list" aria-label="Topik modul">
                <li>Pengenalan</li><li>Reban</li><li>Pemakanan</li>
                <li>Kesihatan</li><li>Biosekuriti</li>
            </ul>
            <a class="learning-action" href="/learn/modules/ayam-kampung/">MULA BELAJAR</a>
        </article>

        <footer>ASTH Learning Hub &#183; Institut Teknologi Unggas</footer>
    </main>
</body>
</html>
"""


DEMO_MODULE_PAGE = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asas Penternakan Ayam Kampung</title>
    <style>
""" + LEARNING_SUBPAGE_STYLE + """
</style>
</head>
<body>
    <main class="learning-page">
        <header class="learning-header">
            <div class="learning-brand">
                <div class="learning-logos">
                    <div class="learning-logo"><img src="/assets/logo-dvs.png" alt="Logo DVS"></div>
                    <div class="learning-logo"><img src="/assets/logo-asth.png" alt="Logo ASTH"></div>
                </div>
                <div>
                    <p class="learning-eyebrow">Modul Demo ASTH</p>
                    <h1>Asas Penternakan Ayam Kampung</h1>
                    <p class="learning-subtitle">Bahan pengenalan ringkas untuk demonstrasi Learning Hub.</p>
                </div>
            </div>
            <a class="learning-back" href="/learn/modules/">&#8592; Senarai Modul</a>
        </header>

        <section class="learning-panel">
            <span class="demo-label">KANDUNGAN DEMO</span>
            <p>
                Modul ini menunjukkan susunan pembelajaran Phase Learning 1. Kandungannya bersifat
                umum dan bukan pengganti latihan rasmi atau nasihat veterinar yang berkelayakan.
            </p>
            <nav aria-label="Topik modul">
                <ul class="topic-list">
                    <li><a href="#pengenalan">Pengenalan</a></li>
                    <li><a href="#reban">Reban</a></li>
                    <li><a href="#pemakanan">Pemakanan</a></li>
                    <li><a href="#kesihatan">Kesihatan</a></li>
                    <li><a href="#biosekuriti">Biosekuriti</a></li>
                </ul>
            </nav>

            <section id="pengenalan" class="lesson-section">
                <h2>Pengenalan</h2>
                <p>Kenali tujuan modul, istilah asas dan perkara umum yang akan diperhatikan sepanjang pembelajaran.</p>
            </section>
            <section id="reban" class="lesson-section">
                <h2>Reban</h2>
                <p>Perhatikan secara umum ruang, pengudaraan, kebersihan dan keselamatan persekitaran ternakan.</p>
            </section>
            <section id="pemakanan" class="lesson-section">
                <h2>Pemakanan</h2>
                <p>Pelajari kepentingan air bersih, rutin pemakanan dan pemerhatian penggunaan makanan secara umum.</p>
            </section>
            <section id="kesihatan" class="lesson-section">
                <h2>Kesihatan</h2>
                <p>Amalkan pemerhatian harian, catat perubahan dan dapatkan bantuan berkelayakan apabila diperlukan.</p>
            </section>
            <section id="biosekuriti" class="lesson-section">
                <h2>Biosekuriti</h2>
                <p>Fahami konsep asas kebersihan, kawalan pergerakan dan penggunaan peralatan mengikut prosedur rasmi.</p>
            </section>

            <section class="lesson-section end-panel">
                <h2>Tamat Pembelajaran Demo</h2>
                <p>Anda telah sampai ke penghujung modul demonstrasi ini. Kemajuan belum disimpan dalam Phase Learning 1.</p>
                <a class="learning-action" href="/learn/modules/">TAMAT MODUL</a>
            </section>
        </section>

        <footer>ASTH Learning Hub &#183; Institut Teknologi Unggas</footer>
    </main>
</body>
</html>
"""


REBAN_BROODER_PACK_PAGE = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Persediaan Reban &amp; Brooder | ASTH Learning Hub</title>
    <style>
""" + LEARNING_SUBPAGE_STYLE + """
    .pack-meta, .section-labels {
        display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;
    }
    .pack-meta span, .section-labels span {
        padding: 7px 10px; border: 2px solid var(--line); border-radius: 999px;
        color: var(--dark); background: #edf4ff; font-size: .76rem; font-weight: 850;
    }
    .pack-intro { background: linear-gradient(145deg, #fff2b7, #ffd275); }
    .pack-intro p { color: #51421f; }
    .pack-section {
        margin-top: 18px; padding: clamp(19px, 4vw, 28px); border: 3px solid #9fb6d8;
        border-radius: 23px; background: #ffffff; box-shadow: var(--shadow);
    }
    .section-kicker {
        margin: 0 0 6px; color: #245bc5; font-size: .72rem; font-weight: 900;
        letter-spacing: .08em; text-transform: uppercase;
    }
    .pack-section h2 { margin: 0 0 10px; font-size: clamp(1.3rem, 3vw, 1.75rem); }
    .pack-section > p { margin: 0; color: var(--muted); line-height: 1.6; }
    .practical-list {
        display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px;
        margin: 18px 0 0; padding: 0; list-style: none;
    }
    .practical-list li {
        display: flex; gap: 11px; align-items: flex-start; padding: 14px;
        border: 2px solid #aac0df; border-radius: 15px; background: #f6f9ff;
        color: #243b5b; font-size: .9rem; line-height: 1.45;
    }
    .practical-list li::before {
        content: "\2713"; display: grid; flex: 0 0 26px; width: 26px; height: 26px;
        place-items: center; border-radius: 50%; color: white; background: #147647;
        font-weight: 900;
    }
    .behaviour-grid {
        display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 17px;
    }
    .behaviour-card {
        padding: 17px; border: 3px solid #a9bddb; border-radius: 18px; background: #f7faff;
    }
    .behaviour-card strong { display: block; margin-bottom: 7px; color: #17335b; }
    .behaviour-card p { margin: 0; color: #415979; line-height: 1.45; }
    .behaviour-card.good { border-color: #278b58; background: #e5f8ed; }
    .video-placeholder {
        margin-top: 16px; padding: 25px; border: 3px dashed #738cac; border-radius: 18px;
        background: #edf3fb; text-align: center;
    }
    .video-placeholder strong { display: block; margin-bottom: 8px; font-size: 1.05rem; }
    .video-status {
        display: inline-block; padding: 7px 10px; border-radius: 999px;
        color: #6f4d00; background: #ffd86a; font-size: .72rem; font-weight: 900;
    }
    .check-grid {
        display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 9px;
        margin: 17px 0;
    }
    .check-card {
        display: flex; min-height: 76px; align-items: center; justify-content: center;
        padding: 10px; border: 3px solid #a5b9d7; border-radius: 15px;
        background: #f7faff; font-weight: 850; text-align: center; cursor: pointer;
    }
    .check-card:has(input:checked) { border-color: #147647; background: #dff7e9; }
    .check-card input { width: 20px; height: 20px; margin: 0 8px 0 0; accent-color: #147647; }
    .pack-button {
        min-height: 46px; padding: 11px 17px; border: 0; border-radius: 13px;
        color: white; background: #225fcf; box-shadow: 0 4px 0 #123c8e;
        font: inherit; font-size: .82rem; font-weight: 900; cursor: pointer;
    }
    .pack-button.secondary { color: #17335b; background: #d8e6fb; box-shadow: 0 4px 0 #9ab3d8; }
    .feedback {
        min-height: 24px; margin: 14px 0 0; color: #17335b; font-weight: 850;
    }
    .quiz-question {
        margin: 15px 0 0; padding: 16px; border: 2px solid #afc1dc;
        border-radius: 17px; background: #f8faff;
    }
    .quiz-question legend { padding: 0 4px; color: #17335b; font-weight: 850; line-height: 1.4; }
    .quiz-question label { display: block; margin-top: 9px; color: #334d70; line-height: 1.4; }
    .quiz-question input { width: 19px; height: 19px; margin-right: 8px; vertical-align: middle; accent-color: #225fcf; }
    .quiz-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 17px; }
    .completion { border-color: #33865d; background: linear-gradient(145deg, #e1f7e9, #c5efd5); }
    .completion p { color: #274f39; }
    @media (max-width: 720px) {
        .practical-list, .behaviour-grid { grid-template-columns: 1fr; }
        .check-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 420px) {
        .learning-page { width: min(100% - 20px, 980px); padding-top: 10px; }
        .pack-section { padding: 17px; }
        .check-grid { grid-template-columns: 1fr; }
        .check-card { min-height: 58px; justify-content: flex-start; text-align: left; }
    }
    </style>
</head>
<body>
    <main class="learning-page">
        <header class="learning-header">
            <div class="learning-brand">
                <div class="learning-logos">
                    <div class="learning-logo"><img src="/assets/logo-dvs.png" alt="Logo DVS"></div>
                    <div class="learning-logo"><img src="/assets/logo-asth.png" alt="Logo ASTH"></div>
                </div>
                <div>
                    <p class="learning-eyebrow">ASTH Learning Pack</p>
                    <h1>Persediaan Reban &amp; Brooder</h1>
                    <div class="pack-meta"><span>&plusmn;10 minit</span><span>Praktikal</span><span>Offline</span></div>
                </div>
            </div>
            <a class="learning-back" href="/learn/">&#8592; Learning Hub</a>
        </header>

        <section class="learning-panel pack-intro">
            <p class="section-kicker">01 Pengenalan</p>
            <h2>Persediaan sebelum anak ayam tiba</h2>
            <p>
                Persediaan reban dan brooder yang baik sebelum anak ayam tiba membantu menyediakan
                persekitaran permulaan yang bersih, selesa dan terkawal. Learning Pack ini memberi
                panduan pemeriksaan asas untuk latihan praktikal, bukan diagnosis veterinar.
            </p>
        </section>

        <section class="pack-section">
            <p class="section-kicker">02 Checklist Persediaan</p>
            <h2>Semak sebelum kemasukan</h2>
            <ul class="practical-list">
                <li>Pastikan reban telah dibersihkan dan kawasan brooder bebas daripada sisa lama.</li>
                <li>Sediakan litter yang bersih, kering dan rata.</li>
                <li>Pasang serta uji pemanas/brooder sebelum anak ayam tiba.</li>
                <li>Pastikan kawasan brooder tidak terkena tiupan angin terus.</li>
                <li>Sediakan bekas minuman dan makanan secukupnya serta mudah dicapai.</li>
                <li>Pastikan air minuman telah tersedia sebelum anak ayam dimasukkan.</li>
                <li>Periksa pencahayaan supaya kawasan makan dan minum mudah dilihat.</li>
                <li>Pastikan pengudaraan baik tanpa menyebabkan anak ayam kesejukan.</li>
                <li>Periksa keselamatan peralatan, kabel, pemanas dan kawasan sekeliling.</li>
                <li>Selepas anak ayam dimasukkan, perhatikan taburan dan tingkah laku anak ayam untuk menilai keselesaan kawasan brooder.</li>
            </ul>
        </section>

        <section class="pack-section">
            <p class="section-kicker">03 Baca Tingkah Laku Anak Ayam</p>
            <h2>Gunakan pemerhatian sebagai petunjuk awal</h2>
            <p>Corak ini ialah petunjuk praktikal untuk pemeriksaan persekitaran, bukan diagnosis kesihatan.</p>
            <div class="behaviour-grid">
                <article class="behaviour-card"><strong>Berkumpul rapat bawah pemanas</strong><p>kemungkinan terlalu sejuk</p></article>
                <article class="behaviour-card"><strong>Menjauh daripada sumber haba</strong><p>kemungkinan terlalu panas</p></article>
                <article class="behaviour-card"><strong>Berkumpul pada satu bahagian sahaja</strong><p>semak tiupan angin atau keadaan persekitaran</p></article>
                <article class="behaviour-card good"><strong>Tersebar sekata dan aktif</strong><p>petunjuk keadaan lebih selesa</p></article>
            </div>
        </section>

        <section class="pack-section">
            <p class="section-kicker">04 Video Demo</p>
            <h2>Demonstrasi tempatan</h2>
            <div class="video-placeholder">
                <strong>Cara Menyediakan Brooder Sebelum Anak Ayam Tiba</strong>
                <span class="video-status">AKAN DITAMBAH</span>
            </div>
        </section>

        <section class="pack-section" id="brooder-check">
            <p class="section-kicker">05 Aktiviti Interaktif</p>
            <h2>Brooder Check</h2>
            <p>Pilih lima perkara utama yang perlu diperiksa sebelum anak ayam ditempatkan di dalam brooder.</p>
            <div class="check-grid">
                <label class="check-card"><input type="checkbox" data-check="pemanas">Pemanas</label>
                <label class="check-card"><input type="checkbox" data-check="air">Air</label>
                <label class="check-card"><input type="checkbox" data-check="makanan">Makanan</label>
                <label class="check-card"><input type="checkbox" data-check="litter">Litter</label>
                <label class="check-card"><input type="checkbox" data-check="pengudaraan">Pengudaraan</label>
            </div>
            <button class="pack-button" id="checkBrooder" type="button">SEMAK</button>
            <p class="feedback" id="brooderFeedback" role="status" aria-live="polite"></p>
        </section>

        <section class="pack-section" id="quick-quiz">
            <p class="section-kicker">06 Quick Quiz</p>
            <h2>Semak kefahaman anda</h2>
            <p>Kuiz ringkas ini tidak disimpan dan bukan penilaian atau pensijilan rasmi.</p>
            <form id="packQuiz">
                <fieldset class="quiz-question">
                    <legend>1. Apakah tindakan yang paling sesuai dilakukan sebelum anak ayam tiba?</legend>
                    <label><input type="radio" name="q1" value="A">A. Pasang pemanas selepas anak ayam dimasukkan</label>
                    <label><input type="radio" name="q1" value="B">B. Sediakan dan uji brooder terlebih dahulu</label>
                    <label><input type="radio" name="q1" value="C">C. Biarkan kawasan reban kosong tanpa pemeriksaan</label>
                    <label><input type="radio" name="q1" value="D">D. Sediakan makanan sahaja</label>
                </fieldset>
                <fieldset class="quiz-question">
                    <legend>2. Anak ayam berkumpul sangat rapat di bawah sumber haba. Apakah perkara pertama yang patut diperiksa?</legend>
                    <label><input type="radio" name="q2" value="A">A. Warna litter</label>
                    <label><input type="radio" name="q2" value="B">B. Keadaan suhu/haba kawasan brooder</label>
                    <label><input type="radio" name="q2" value="C">C. Saiz pintu reban</label>
                    <label><input type="radio" name="q2" value="D">D. Bilangan lampu luar</label>
                </fieldset>
                <fieldset class="quiz-question">
                    <legend>3. Mengapa air minuman perlu tersedia apabila anak ayam dimasukkan?</legend>
                    <label><input type="radio" name="q3" value="A">A. Supaya kawasan litter menjadi basah</label>
                    <label><input type="radio" name="q3" value="B">B. Supaya anak ayam mudah mendapatkan air selepas tiba</label>
                    <label><input type="radio" name="q3" value="C">C. Untuk menyejukkan seluruh reban</label>
                    <label><input type="radio" name="q3" value="D">D. Untuk membersihkan bekas makanan</label>
                </fieldset>
                <fieldset class="quiz-question">
                    <legend>4. Apakah ciri litter yang sesuai semasa persediaan awal?</legend>
                    <label><input type="radio" name="q4" value="A">A. Basah dan padat</label>
                    <label><input type="radio" name="q4" value="B">B. Bersih, kering dan rata</label>
                    <label><input type="radio" name="q4" value="C">C. Dicampurkan dengan sisa lama</label>
                    <label><input type="radio" name="q4" value="D">D. Tidak perlu diperiksa</label>
                </fieldset>
                <fieldset class="quiz-question">
                    <legend>5. Selepas anak ayam dimasukkan ke dalam brooder, apakah pemerhatian yang penting dilakukan?</legend>
                    <label><input type="radio" name="q5" value="A">A. Warna dinding reban</label>
                    <label><input type="radio" name="q5" value="B">B. Taburan dan tingkah laku anak ayam</label>
                    <label><input type="radio" name="q5" value="C">C. Jenama peralatan</label>
                    <label><input type="radio" name="q5" value="D">D. Kedudukan kenderaan di luar reban</label>
                </fieldset>
                <div class="quiz-actions">
                    <button class="pack-button" type="submit">SEMAK JAWAPAN</button>
                    <button class="pack-button secondary" id="retryQuiz" type="button">CUBA SEMULA</button>
                </div>
                <p class="feedback" id="quizResult" role="status" aria-live="polite">Keputusan akan memaparkan jumlah betul daripada 5.</p>
            </form>
        </section>

        <section class="pack-section completion">
            <p class="section-kicker">07 Tamat Learning Pack</p>
            <h2>Anda telah selesai Learning Pack: Persediaan Reban &amp; Brooder.</h2>
            <p>
                Anda telah melihat asas persediaan kawasan brooder, checklist sebelum kemasukan anak ayam,
                cara membaca tingkah laku awal anak ayam serta pemeriksaan asas selepas kemasukan.
                Kemajuan tidak direkodkan.
            </p>
            <a class="learning-action" href="/learn/">KEMBALI KE LEARNING HUB</a>
        </section>

        <footer>ASTH Learning Hub &#183; Institut Teknologi Unggas</footer>
    </main>

    <script>
        (() => {
            const requiredChecks = ["pemanas", "air", "makanan", "litter", "pengudaraan"];
            const brooderButton = document.getElementById("checkBrooder");
            const brooderFeedback = document.getElementById("brooderFeedback");
            const quiz = document.getElementById("packQuiz");
            const quizResult = document.getElementById("quizResult");
            const retryButton = document.getElementById("retryQuiz");

            brooderButton.addEventListener("click", () => {
                const selected = new Set(
                    Array.from(document.querySelectorAll("[data-check]:checked"))
                        .map((item) => item.dataset.check)
                );
                const complete = requiredChecks.every((item) => selected.has(item));
                brooderFeedback.textContent = complete
                    ? "Lengkap. Kelima-lima pemeriksaan utama telah dipilih."
                    : `Pilih semua lima pemeriksaan. ${selected.size} daripada 5 telah dipilih.`;
            });

            quiz.addEventListener("submit", (event) => {
                event.preventDefault();
                let correct = 0;
                let answered = 0;
                for (let number = 1; number <= 5; number += 1) {
                    const choice = quiz.querySelector(`input[name="q${number}"]:checked`);
                    if (choice) {
                        answered += 1;
                        if (choice.value === "B") correct += 1;
                    }
                }
                quizResult.textContent = answered === 5
                    ? `Anda menjawab ${correct} daripada 5 dengan betul.`
                    : `Sila jawab semua soalan. ${answered} daripada 5 telah dijawab.`;
            });

            retryButton.addEventListener("click", () => {
                quiz.reset();
                quizResult.textContent = "Keputusan dikosongkan. Cuba semula semua lima soalan.";
            });
        })();
    </script>
</body>
</html>
"""


BIOSECURITY_PACK_PAGE = """
<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biosekuriti Asas Ladang | ASTH Learning Hub</title>
    <style>
""" + LEARNING_SUBPAGE_STYLE + """
    .pack-meta, .zone-grid, .topic-grid {
        display: flex; flex-wrap: wrap; gap: 9px; margin-top: 14px;
    }
    .pack-meta span, .zone-grid span {
        padding: 8px 11px; border: 2px solid var(--line); border-radius: 999px;
        color: var(--dark); background: #edf4ff; font-size: .78rem; font-weight: 850;
    }
    .pack-intro { background: linear-gradient(145deg, #fff2b7, #ffd275); }
    .pack-intro p { color: #51421f; }
    .source-note {
        margin-top: 16px; padding: 13px 15px; border: 2px solid #9a7619;
        border-radius: 14px; color: #43350e; background: #fff8d9;
        font-size: .82rem; font-weight: 750; line-height: 1.5;
    }
    .pack-section {
        margin-top: 18px; padding: clamp(19px, 4vw, 28px); border: 3px solid #9fb6d8;
        border-radius: 23px; background: #ffffff; box-shadow: var(--shadow);
    }
    .section-kicker {
        margin: 0 0 6px; color: #245bc5; font-size: .72rem; font-weight: 900;
        letter-spacing: .08em; text-transform: uppercase;
    }
    .pack-section h2 { margin: 0 0 10px; font-size: clamp(1.3rem, 3vw, 1.75rem); }
    .pack-section > p { margin: 0; color: var(--muted); line-height: 1.6; }
    .topic-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .topic-card {
        padding: 16px; border: 2px solid #aac0df; border-radius: 16px;
        color: #243b5b; background: #f6f9ff; line-height: 1.5;
    }
    .topic-card strong { display: block; margin-bottom: 7px; color: #17335b; }
    .practical-list {
        display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px;
        margin: 18px 0 0; padding: 0; list-style: none;
    }
    .practical-list li {
        display: flex; gap: 11px; align-items: flex-start; padding: 14px;
        border: 2px solid #aac0df; border-radius: 15px; background: #f6f9ff;
        color: #243b5b; font-size: .9rem; line-height: 1.45;
    }
    .practical-list li::before {
        content: "\\2713"; display: grid; flex: 0 0 26px; width: 26px; height: 26px;
        place-items: center; border-radius: 50%; color: white; background: #147647;
        font-weight: 900;
    }
    .audit-grid { display: grid; gap: 13px; margin-top: 18px; }
    .audit-card {
        padding: 17px; border: 3px solid #8ba7cd; border-radius: 18px; background: #f7faff;
    }
    .audit-card h3 { margin: 0 0 7px; color: #17335b; font-size: 1rem; }
    .audit-card p { color: #3b5375; line-height: 1.5; }
    .audit-action[hidden] { display: none; }
    .audit-action {
        margin-top: 12px; padding: 13px; border: 2px solid #278b58; border-radius: 13px;
        color: #17472f; background: #e5f8ed; font-weight: 800;
    }
    .pack-button {
        min-height: 46px; padding: 11px 17px; border: 0; border-radius: 13px;
        color: white; background: #225fcf; box-shadow: 0 4px 0 #123c8e;
        font: inherit; font-size: .82rem; font-weight: 900; cursor: pointer;
    }
    .pack-button.secondary { color: #17335b; background: #d8e6fb; box-shadow: 0 4px 0 #9ab3d8; }
    .feedback { min-height: 24px; margin: 11px 0 0; color: #17335b; font-weight: 850; }
    .quiz-question {
        margin: 15px 0 0; padding: 16px; border: 2px solid #afc1dc;
        border-radius: 17px; background: #f8faff;
    }
    .quiz-question legend { padding: 0 4px; color: #17335b; font-weight: 850; line-height: 1.4; }
    .quiz-question label { display: block; margin-top: 9px; color: #334d70; line-height: 1.4; }
    .quiz-question input { width: 19px; height: 19px; margin-right: 8px; vertical-align: middle; accent-color: #225fcf; }
    .quiz-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 17px; }
    .completion { border-color: #33865d; background: linear-gradient(145deg, #e1f7e9, #c5efd5); }
    .completion p { color: #274f39; }
    .completion ul { color: #274f39; line-height: 1.7; }
    .official-note {
        margin-top: 14px; padding: 12px 14px; border-left: 5px solid #245bc5;
        color: #243b5b; background: #edf4ff; font-size: .82rem; line-height: 1.5;
    }
    @media (max-width: 720px) {
        .topic-grid, .practical-list { grid-template-columns: 1fr; }
    }
    @media (max-width: 420px) {
        .learning-page { width: min(100% - 20px, 980px); padding-top: 10px; }
        .pack-section { padding: 17px; }
        .pack-button { width: 100%; }
    }
    </style>
</head>
<body>
    <main class="learning-page">
        <header class="learning-header">
            <div class="learning-brand">
                <div class="learning-logos">
                    <div class="learning-logo"><img src="/assets/logo-dvs.png" alt="Logo DVS"></div>
                    <div class="learning-logo"><img src="/assets/logo-asth.png" alt="Logo ASTH"></div>
                </div>
                <div>
                    <p class="learning-eyebrow">ASTH Learning Pack</p>
                    <h1>Biosekuriti Asas Ladang</h1>
                    <div class="pack-meta"><span>7 bahagian</span><span>Praktikal</span><span>Offline</span></div>
                </div>
            </div>
            <a class="learning-back" href="/learn/">&#8592; Learning Hub</a>
        </header>

        <section class="learning-panel pack-intro">
            <p class="section-kicker">01 Pengenalan Biosekuriti</p>
            <h2>Asas sistem biosekuriti ladang poltri</h2>
            <p>Biosekuriti mengawal kemasukan dan penyebaran kuman dalam ladang.</p>
            <div class="topic-grid">
                <div class="topic-card"><strong>Tiga aktiviti utama C08</strong>Nyah kuman personel dan kenderaan; kawalan makhluk perosak; penyelenggaraan parit dan pagar.</div>
                <div class="topic-card"><strong>Amalan kerja</strong>Patuhi kebersihan ladang dan amalkan prinsip 5S.</div>
            </div>
            <div class="zone-grid" aria-label="Tiga kawasan ladang">
                <span>kawasan luar</span><span>kawasan bukan produksi</span><span>kawasan produksi</span>
            </div>
            <div class="source-note">
                Diadaptasi untuk mikro-pembelajaran ASTH daripada WIM A014-006-3:2022-C08 —
                Laksana Sistem Biosekuriti Ladang Poltri.
            </div>
        </section>

        <section class="pack-section">
            <p class="section-kicker">02 Kawalan Kemasukan Personel &amp; Kenderaan</p>
            <h2>Kawal laluan masuk sebelum ke kawasan produksi</h2>
            <ul class="practical-list">
                <li>Gunakan satu pintu utama dan pastikan pintu sentiasa ditutup.</li>
                <li>Dapatkan kebenaran pengurusan. Kehadiran pelawat diminimumkan.</li>
                <li>Gunakan laluan keluar dan masuk yang dikawal.</li>
                <li>Personel dan kenderaan melalui proses nyah kuman sebelum memasuki kawasan produksi.</li>
                <li>Lokasi yang dinyatakan ialah bilik mandi, celupan kaki dan semburan kenderaan.</li>
                <li>Bersihkan lumpur, jerami dan kotoran yang kelihatan sebelum proses nyah kuman.</li>
                <li>Gunakan PPE mengikut keperluan kerja.</li>
                <li>Pantau proses dan rekodkan aktiviti yang dilakukan.</li>
            </ul>
        </section>

        <section class="pack-section">
            <p class="section-kicker">03 Kawalan Makhluk Perosak</p>
            <h2>Kenal pasti, kawal persekitaran dan rekod</h2>
            <ul class="practical-list">
                <li>Kenal pasti jenis dan lokasi makhluk perosak.</li>
                <li>Pastikan persekitaran ladang sentiasa bersih.</li>
                <li>Urus rumput dan selenggara parit serta pagar.</li>
                <li>Keluarkan sampah, bahan terkumpul dan peralatan yang tidak digunakan.</li>
                <li>Gunakan PPE mengikut keperluan kerja.</li>
                <li>Baca label produk dan Risalah Data Keselamatan Kimia apabila berkenaan.</li>
                <li>Ikut proses kerja kawalan yang ditetapkan.</li>
                <li>Rekod aktiviti kawalan makhluk perosak.</li>
            </ul>
        </section>

        <section class="pack-section">
            <p class="section-kicker">04 Penyelenggaraan Parit</p>
            <h2>Pastikan laluan air tidak terhalang</h2>
            <p>Punca biasa parit tersumbat ialah tanah runtuh, rumput panjang dan sampah sarap.</p>
            <ul class="practical-list">
                <li>Periksa lokasi kerja dan jadual penyelenggaraan.</li>
                <li>Pakai PPE sebelum memulakan kerja.</li>
                <li>Buang rumput, tumbuhan dan dahan yang menghalang.</li>
                <li>Buang sampah dan keluarkan tanah yang terkumpul.</li>
                <li>Bersihkan perangkap sampah supaya air dapat mengalir.</li>
                <li>Bersihkan dan simpan peralatan selepas digunakan.</li>
                <li>Rekod aktiviti penyelenggaraan parit.</li>
            </ul>
        </section>

        <section class="pack-section">
            <p class="section-kicker">05 Penyelenggaraan Pagar</p>
            <h2>Periksa dan selenggara pagar ladang</h2>
            <p>Periksa pagar sempadan serta pagar yang memisahkan kawasan produksi dan kawasan pengurusan.</p>
            <ul class="practical-list">
                <li>Periksa lubang dan bahagian pagar yang roboh.</li>
                <li>Periksa tumbuhan, dahan melampai, lubang tanah dan sampah.</li>
                <li>Tampal pagar yang berlubang dan tegakkan semula pagar yang roboh.</li>
                <li>Timbus lubang tanah dan bersihkan tumbuhan serta kawasan pagar.</li>
                <li>Bersihkan dan simpan peralatan selepas digunakan.</li>
                <li>Rekod aktiviti penyelenggaraan pagar.</li>
            </ul>
        </section>

        <section class="pack-section" id="audit-biosekuriti">
            <p class="section-kicker">06 Audit Biosekuriti Ladang</p>
            <h2>Semak tindakan bagi setiap situasi</h2>
            <p>Tekan butang pada setiap kad untuk melihat tindakan yang disokong oleh C08.</p>
            <div class="audit-grid">
                <article class="audit-card" data-audit-scenario="1">
                    <h3>Situasi 1</h3>
                    <p>Pelawat mahu memasuki kawasan produksi.</p>
                    <button class="pack-button audit-reveal" type="button" data-target="auditAction1" data-feedback="auditFeedback1">LIHAT TINDAKAN</button>
                    <div class="audit-action" id="auditAction1" hidden>Dapatkan kebenaran, gunakan laluan terkawal dan lalui proses nyah kuman.</div>
                    <p class="feedback" id="auditFeedback1" role="status" aria-live="polite">Maklum balas akan dipaparkan di sini.</p>
                </article>
                <article class="audit-card" data-audit-scenario="2">
                    <h3>Situasi 2</h3>
                    <p>Tayar dan gerbang roda kenderaan mempunyai lumpur atau jerami.</p>
                    <button class="pack-button audit-reveal" type="button" data-target="auditAction2" data-feedback="auditFeedback2">LIHAT TINDAKAN</button>
                    <div class="audit-action" id="auditAction2" hidden>Bersihkan kotoran sebelum nyah kuman dan beri perhatian kepada roda serta bahagian bawah kenderaan.</div>
                    <p class="feedback" id="auditFeedback2" role="status" aria-live="polite">Maklum balas akan dipaparkan di sini.</p>
                </article>
                <article class="audit-card" data-audit-scenario="3">
                    <h3>Situasi 3</h3>
                    <p>Tanda makhluk perosak ditemui dalam reban.</p>
                    <button class="pack-button audit-reveal" type="button" data-target="auditAction3" data-feedback="auditFeedback3">LIHAT TINDAKAN</button>
                    <div class="audit-action" id="auditAction3" hidden>Kenal pasti jenis dan lokasi, ikut proses kerja, gunakan PPE dan rekod tindakan.</div>
                    <p class="feedback" id="auditFeedback3" role="status" aria-live="polite">Maklum balas akan dipaparkan di sini.</p>
                </article>
                <article class="audit-card" data-audit-scenario="4">
                    <h3>Situasi 4</h3>
                    <p>Parit dipenuhi rumput, sampah dan tanah.</p>
                    <button class="pack-button audit-reveal" type="button" data-target="auditAction4" data-feedback="auditFeedback4">LIHAT TINDAKAN</button>
                    <div class="audit-action" id="auditAction4" hidden>Pakai PPE, buang halangan, bersihkan perangkap sampah dan rekod kerja.</div>
                    <p class="feedback" id="auditFeedback4" role="status" aria-live="polite">Maklum balas akan dipaparkan di sini.</p>
                </article>
                <article class="audit-card" data-audit-scenario="5">
                    <h3>Situasi 5</h3>
                    <p>Pagar berlubang, roboh dan terdapat lubang tanah.</p>
                    <button class="pack-button audit-reveal" type="button" data-target="auditAction5" data-feedback="auditFeedback5">LIHAT TINDAKAN</button>
                    <div class="audit-action" id="auditAction5" hidden>Tampal lubang, tegakkan pagar, timbus lubang tanah, bersihkan kawasan dan rekod kerja.</div>
                    <p class="feedback" id="auditFeedback5" role="status" aria-live="polite">Maklum balas akan dipaparkan di sini.</p>
                </article>
            </div>
        </section>

        <section class="pack-section" id="biosecurity-quiz">
            <p class="section-kicker">07 Quick Quiz &amp; Tamat Pack</p>
            <h2>Uji pemahaman anda</h2>
            <form id="biosecurityQuiz">
                <fieldset class="quiz-question" data-quiz-question="1">
                    <legend>1. Mengapakah proses nyah kuman personel dan kenderaan dilakukan?</legend>
                    <label><input type="radio" name="bioQ1" value="A">A. Untuk kebersihan ladang poltri.</label>
                    <label><input type="radio" name="bioQ1" value="B">B. Untuk mewangikan ladang ayam.</label>
                    <label><input type="radio" name="bioQ1" value="C" data-correct="true">C. Untuk mencegah jangkitan penyakit pada ayam.</label>
                    <label><input type="radio" name="bioQ1" value="D">D. Untuk memastikan pelawat suka melawat ladang poltri.</label>
                    <p class="feedback" id="bioQuizFeedback1" role="status" aria-live="polite"></p>
                </fieldset>
                <fieldset class="quiz-question" data-quiz-question="2">
                    <legend>2. Yang manakah tiga kategori kawasan ladang poltri dalam C08?</legend>
                    <label><input type="radio" name="bioQ2" value="A" data-correct="true">A. Kawasan luar, kawasan bukan produksi, kawasan produksi.</label>
                    <label><input type="radio" name="bioQ2" value="B">B. Pelawat, pekerja, pembekal.</label>
                    <label><input type="radio" name="bioQ2" value="C">C. Bilik mandi, celupan kaki, semburan kenderaan.</label>
                    <label><input type="radio" name="bioQ2" value="D">D. Parit, pagar, reban.</label>
                    <p class="feedback" id="bioQuizFeedback2" role="status" aria-live="polite"></p>
                </fieldset>
                <fieldset class="quiz-question" data-quiz-question="3">
                    <legend>3. Mengapakah PPE digunakan ketika membuat penyemburan racun serangga?</legend>
                    <label><input type="radio" name="bioQ3" value="A" data-correct="true">A. Mengelakkan kesan sampingan bahan toksik kepada pekerja.</label>
                    <label><input type="radio" name="bioQ3" value="B">B. Menentukan lokasi makhluk perosak.</label>
                    <label><input type="radio" name="bioQ3" value="C">C. Menyediakan rekod pengawalan.</label>
                    <label><input type="radio" name="bioQ3" value="D">D. Mengemas kini jadual penyelenggaraan pagar.</label>
                    <p class="feedback" id="bioQuizFeedback3" role="status" aria-live="polite"></p>
                </fieldset>
                <fieldset class="quiz-question" data-quiz-question="4">
                    <legend>4. Apakah yang perlu dilakukan sebelum personel dan kenderaan memasuki kawasan produksi?</legend>
                    <label><input type="radio" name="bioQ4" value="A" data-correct="true">A. Melalui proses nyah kuman.</label>
                    <label><input type="radio" name="bioQ4" value="B">B. Personel menggunakan semburan kenderaan.</label>
                    <label><input type="radio" name="bioQ4" value="C">C. Kenderaan melalui bilik mandi.</label>
                    <label><input type="radio" name="bioQ4" value="D">D. Masuk melalui mana-mana laluan.</label>
                    <p class="feedback" id="bioQuizFeedback4" role="status" aria-live="polite"></p>
                </fieldset>
                <fieldset class="quiz-question" data-quiz-question="5">
                    <legend>5. Yang manakah tiga punca parit tersumbat menurut C08?</legend>
                    <label><input type="radio" name="bioQ5" value="A" data-correct="true">A. Tanah runtuh, rumput panjang dan sampah sarap.</label>
                    <label><input type="radio" name="bioQ5" value="B">B. Pagar berlubang, rumput panjang dan sampah sarap.</label>
                    <label><input type="radio" name="bioQ5" value="C">C. Pagar roboh, lubang tanah dan pokok menjalar.</label>
                    <label><input type="radio" name="bioQ5" value="D">D. Tikus, burung liar dan lalat.</label>
                    <p class="feedback" id="bioQuizFeedback5" role="status" aria-live="polite"></p>
                </fieldset>
                <div class="quiz-actions">
                    <button class="pack-button" type="submit">SEMAK SKOR</button>
                    <button class="pack-button secondary" id="retryBiosecurityQuiz" type="button">CUBA SEMULA</button>
                </div>
                <p class="feedback" id="biosecurityQuizResult" role="status" aria-live="polite">Keputusan akan memaparkan jumlah betul daripada 5.</p>
            </form>
        </section>

        <section class="pack-section completion">
            <p class="section-kicker">Learning Pack Selesai</p>
            <h2>Anda telah selesai Learning Pack: Biosekuriti Asas Ladang.</h2>
            <p>Tiga aktiviti utama C08 yang telah dipelajari:</p>
            <ul>
                <li>Nyah kuman personel dan kenderaan</li>
                <li>Kawalan makhluk perosak</li>
                <li>Penyelenggaraan parit dan pagar</li>
            </ul>
            <div class="source-note">
                Diadaptasi untuk mikro-pembelajaran ASTH daripada WIM A014-006-3:2022-C08 —
                Laksana Sistem Biosekuriti Ladang Poltri.
            </div>
            <div class="official-note">Learning Pack ASTH ini ialah mikro-pembelajaran dan bukan pengganti WIM atau penilaian kompetensi rasmi.</div>
            <a class="learning-action" href="/learn/">KEMBALI KE LEARNING HUB</a>
        </section>

        <footer>ASTH Learning Hub &#183; Institut Teknologi Unggas</footer>
    </main>

    <script>
        (() => {
            document.querySelectorAll(".audit-reveal").forEach((button) => {
                button.addEventListener("click", () => {
                    const action = document.getElementById(button.dataset.target);
                    const feedback = document.getElementById(button.dataset.feedback);
                    action.hidden = false;
                    feedback.textContent = "Tindakan dipaparkan berdasarkan aliran kerja C08.";
                    button.textContent = "TINDAKAN DIPAPARKAN";
                });
            });

            const quiz = document.getElementById("biosecurityQuiz");
            const result = document.getElementById("biosecurityQuizResult");
            const retry = document.getElementById("retryBiosecurityQuiz");
            const explanations = {
                1: "Tujuannya ialah mencegah personel dan kenderaan menjadi punca jangkitan penyakit.",
                2: "C08 membahagikan ladang kepada kawasan luar, bukan produksi dan produksi.",
                3: "PPE digunakan untuk mengurangkan pendedahan pekerja kepada bahan toksik.",
                4: "Personel dan kenderaan melalui proses nyah kuman sebelum memasuki kawasan produksi.",
                5: "C08 menyenaraikan tanah runtuh, rumput panjang dan sampah sarap sebagai punca parit tersumbat."
            };

            quiz.querySelectorAll('input[type="radio"]').forEach((choice) => {
                choice.addEventListener("change", () => {
                    const question = choice.closest("[data-quiz-question]").dataset.quizQuestion;
                    const feedback = document.getElementById(`bioQuizFeedback${question}`);
                    feedback.textContent = choice.dataset.correct === "true"
                        ? `Betul. ${explanations[question]}`
                        : `Belum tepat. ${explanations[question]}`;
                });
            });

            quiz.addEventListener("submit", (event) => {
                event.preventDefault();
                let answered = 0;
                let correct = 0;
                for (let number = 1; number <= 5; number += 1) {
                    const choice = quiz.querySelector(`input[name="bioQ${number}"]:checked`);
                    if (choice) {
                        answered += 1;
                        if (choice.dataset.correct === "true") correct += 1;
                    }
                }
                result.textContent = answered === 5
                    ? `Anda menjawab ${correct} daripada 5 dengan betul.`
                    : `Sila jawab semua soalan. ${answered} daripada 5 telah dijawab.`;
            });

            retry.addEventListener("click", () => {
                quiz.reset();
                quiz.querySelectorAll(".quiz-question .feedback").forEach((feedback) => {
                    feedback.textContent = "";
                });
                result.textContent = "Keputusan dikosongkan. Cuba semula semua lima soalan.";
            });
        })();
    </script>
</body>
</html>
"""


def _request_hostname(request):
    raw_host = request.headers.get("host", "").strip().lower()
    if raw_host.startswith("[") and "]" in raw_host:
        return raw_host[1:raw_host.index("]")]
    if raw_host.count(":") == 1:
        return raw_host.split(":", 1)[0]
    return raw_host


def _loopback_request(request):
    client = getattr(getattr(request, "client", None), "host", "")
    return (
        _request_hostname(request) in ("127.0.0.1", "localhost", "::1")
        and client in ("127.0.0.1", "::1")
    )


def _participant_page(request):
    hostname = _request_hostname(request)
    url_hostname = f"[{hostname}]" if ":" in hostname else hostname
    jellyfin_url = html.escape(f"http://{url_hostname}:8096", quote=True)
    return PARTICIPANT_PAGE.replace("__ASTH_JELLYFIN_URL__", jellyfin_url)


@app.get("/", response_class=HTMLResponse)
def root(request: Request) -> HTMLResponse:
    if not _loopback_request(request):
        return HTMLResponse(content=_participant_page(request))
    return HTMLResponse(
        content=LANDING_PAGE.replace("<!-- ASTH_WIFI_ACCESS -->", _wifi_access_markup())
    )


@app.get("/learn/", response_class=HTMLResponse)
def learning_hub() -> HTMLResponse:
    return HTMLResponse(content=LEARNING_PAGE)


@app.get("/learn/packs/reban-brooder/", response_class=HTMLResponse)
def learning_pack_reban_brooder() -> HTMLResponse:
    return HTMLResponse(content=REBAN_BROODER_PACK_PAGE)


@app.get("/learn/packs/biosekuriti/", response_class=HTMLResponse)
def learning_pack_biosecurity() -> HTMLResponse:
    return HTMLResponse(content=BIOSECURITY_PACK_PAGE)


@app.get("/learn/modules/", response_class=HTMLResponse)
def learning_modules() -> HTMLResponse:
    return HTMLResponse(content=MODULE_LIST_PAGE)


@app.get("/learn/modules/ayam-kampung/", response_class=HTMLResponse)
def learning_module_ayam_kampung() -> HTMLResponse:
    return HTMLResponse(content=DEMO_MODULE_PAGE)


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
    "cockpit.socket": "service_cockpit",
    "pm2-asthadmin.service": "service_pm2",
}
_WIREGUARD_UNIT = "wg-quick@asth-office.service"
_ITUNAS_MOUNT = "/mnt/office-movies"
_ITUNAS_SOURCE = "//192.168.1.254/Movies"
_ITUNAS_MOUNT_UNIT = r"mnt-office\x2dmovies.mount"
_ITUNAS_AUTOMOUNT_UNIT = r"mnt-office\x2dmovies.automount"
_ITUNAS_ACTIONS = {
    "connect": (
        ("start", _ITUNAS_AUTOMOUNT_UNIT),
        ("start", _ITUNAS_MOUNT_UNIT),
    ),
    "disconnect": (
        ("stop", _ITUNAS_AUTOMOUNT_UNIT),
        ("stop", _ITUNAS_MOUNT_UNIT),
    ),
}
_hud_lock = threading.Lock()
_hud_cache = None
_hud_expires = 0.0
_hud_cpu_sample = None


def _hud_text(path):
    with open(path, encoding="ascii") as source:
        return source.read()


def _mount_unescape(value):
    return re.sub(
        r"\\([0-7]{3})",
        lambda match: chr(int(match.group(1), 8)),
        value,
    )


def _parse_mountinfo(text):
    mounts = []
    for line in text.splitlines():
        try:
            left, right = line.split(" - ", 1)
            fields = left.split()
            filesystem = right.split()
            if len(fields) < 6 or len(filesystem) < 3:
                continue
            mounts.append({
                "mount_point": _mount_unescape(fields[4]),
                "options": set(fields[5].split(",")),
                "filesystem": filesystem[0],
                "source": _mount_unescape(filesystem[1]),
                "super_options": set(filesystem[2].split(",")),
            })
        except (ValueError, IndexError):
            continue
    return mounts


def _find_mount(mounts, mount_point):
    if mounts is None:
        return None
    return next(
        (mount for mount in mounts if mount["mount_point"] == mount_point),
        None,
    )


def _select_local_media(mounts):
    if mounts is None:
        return None
    candidates = [
        mount for mount in mounts
        if mount["source"].startswith("/dev/")
        and mount["mount_point"] != "/"
        and (
            mount["mount_point"].startswith("/mnt/")
            or mount["mount_point"].startswith("/media/")
        )
    ]
    candidates.sort(key=lambda mount: (mount["mount_point"] != "/mnt/rog", mount["mount_point"]))
    return candidates[0] if candidates else None


def _storage_status(mount, label, missing_status="unavailable"):
    if mount is None:
        return {
            "label": label,
            "status": missing_status,
            "mount_point": None,
            "filesystem": None,
            "total_bytes": None,
            "used_bytes": None,
            "available_bytes": None,
            "used_percent": None,
        }
    try:
        usage = shutil.disk_usage(mount["mount_point"])
        used_percent = round(100 * usage.used / usage.total, 1) if usage.total else None
        return {
            "label": label,
            "status": "connected",
            "mount_point": mount["mount_point"],
            "filesystem": mount["filesystem"],
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "available_bytes": usage.free,
            "used_percent": used_percent,
        }
    except OSError:
        return {
            "label": label,
            "status": "unavailable",
            "mount_point": mount["mount_point"],
            "filesystem": mount["filesystem"],
            "total_bytes": None,
            "used_bytes": None,
            "available_bytes": None,
            "used_percent": None,
        }


def _cpu_snapshot(text):
    first = text.splitlines()[0].split()
    if not first or first[0] != "cpu" or len(first) < 5:
        raise ValueError("Invalid /proc/stat CPU line")
    values = [int(value) for value in first[1:]]
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    return sum(values), idle


def _cpu_used_percent(previous, current):
    if previous is None or current is None:
        return None
    total_delta = current[0] - previous[0]
    idle_delta = current[1] - previous[1]
    if total_delta <= 0 or idle_delta < 0:
        return None
    value = 100 * (total_delta - idle_delta) / total_delta
    return round(min(100.0, max(0.0, value)), 1)


def _parse_network_addresses(interfaces):
    result = {"lan_ip": None, "hotspot_ip": None, "hotspot_state": "unavailable"}
    by_name = {
        interface.get("ifname"): interface
        for interface in interfaces
        if isinstance(interface, dict)
    }
    for name, field in (("eth0", "lan_ip"), ("wlan0", "hotspot_ip")):
        interface = by_name.get(name, {})
        for address in interface.get("addr_info", []):
            if address.get("family") == "inet" and address.get("local"):
                result[field] = address["local"]
                break
    wlan = by_name.get("wlan0")
    if wlan is not None:
        result["hotspot_state"] = (
            "connected"
            if wlan.get("operstate") in ("UP", "UNKNOWN") and result["hotspot_ip"]
            else "disconnected"
        )
    return result


def _hud_network():
    try:
        result = subprocess.run(
            ["/usr/sbin/ip", "-j", "address", "show"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=2,
            check=True,
        )
        interfaces = json.loads(result.stdout)
        if not isinstance(interfaces, list):
            raise ValueError("Unexpected address data")
        return _parse_network_addresses(interfaces)
    except (OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError):
        return {"lan_ip": None, "hotspot_ip": None, "hotspot_state": "unavailable"}



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


def _itunas_media_status(tunnel_status, mounts):
    result = {
        "label": "ITUNAS via WireGuard",
        "status": "unavailable",
        "read_only": None,
    }
    if tunnel_status == "disconnected":
        result["status"] = "disconnected"
        return result
    if tunnel_status != "connected" or mounts is None:
        return result
    target_mounts = [
        mount for mount in mounts
        if mount["mount_point"] == _ITUNAS_MOUNT
    ]
    if not target_mounts:
        result["status"] = "disconnected"
        return result
    mount = next(
        (
            mount for mount in target_mounts
            if mount["filesystem"] == "cifs" and mount["source"] == _ITUNAS_SOURCE
        ),
        None,
    )
    if mount is None:
        return result
    read_only = "ro" in mount["options"] or "ro" in mount["super_options"]
    if not read_only:
        return result
    result.update(status="connected", read_only=True)
    return result


def _overall_health(data):
    core_states = (data.get("service_asth"), data.get("service_nginx"))
    if any(state in ("inactive", "failed") for state in core_states):
        return "gangguan"
    metrics = (
        (data.get("cpu_temperature_c"), 70, 80),
        (data.get("cpu_used_percent"), 85, 95),
        (data.get("ram_used_percent"), 85, 95),
        ((data.get("root_storage") or {}).get("used_percent"), 80, 90),
    )
    if any(value is not None and value >= critical for value, _, critical in metrics):
        return "gangguan"
    if any(state not in ("active",) for state in core_states):
        return "amaran"
    if any(value is None or value >= warning for value, warning, _ in metrics):
        return "amaran"
    if (data.get("local_media_storage") or {}).get("status") != "connected":
        return "amaran"
    supporting = (
        data.get("service_jellyfin"),
        data.get("service_smbd"),
        data.get("service_cockpit"),
    )
    if any(state != "active" for state in supporting):
        return "amaran"
    return "sihat"


def _hud_collect():
    global _hud_cpu_sample
    data = {
        "cpu_temperature_c": None, "cpu_used_percent": None,
        "ram_used_percent": None,
        "rog_mounted": None, "rog_free_bytes": None, "rog_total_bytes": None,
        **{field: "unknown" for field in _HUD_UNITS.values()},
        "service_uptime_kuma": "unknown",
        "office_tunnel": "unavailable",
        "root_storage": _storage_status(None, "SYSTEM STORAGE"),
        "local_media_storage": _storage_status(None, "LOCAL MEDIA STORAGE", "disconnected"),
        "itunas_media": _itunas_media_status("unavailable", None),
        "network": {"lan_ip": None, "hotspot_ip": None, "hotspot_state": "unavailable"},
    }
    try:
        if _hud_text("/sys/class/thermal/thermal_zone0/type").strip() == "cpu-thermal":
            value = int(_hud_text("/sys/class/thermal/thermal_zone0/temp")) / 1000
            if 0 <= value <= 150:
                data["cpu_temperature_c"] = round(value, 1)
    except (OSError, ValueError):
        pass
    try:
        current_cpu_sample = _cpu_snapshot(_hud_text("/proc/stat"))
        data["cpu_used_percent"] = _cpu_used_percent(_hud_cpu_sample, current_cpu_sample)
        _hud_cpu_sample = current_cpu_sample
    except (OSError, ValueError, IndexError):
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
    mounts = None
    try:
        mounts = _parse_mountinfo(_hud_text("/proc/self/mountinfo"))
        root_mount = _find_mount(mounts, "/")
        local_mount = _select_local_media(mounts)
        data["root_storage"] = _storage_status(root_mount, "SYSTEM STORAGE")
        data["local_media_storage"] = _storage_status(
            local_mount,
            "LOCAL MEDIA STORAGE",
            "disconnected",
        )
        rog_mount = _find_mount(mounts, "/mnt/rog")
        data["rog_mounted"] = rog_mount is not None and rog_mount["source"].startswith("/dev/")
        if data["rog_mounted"]:
            rog_usage = shutil.disk_usage("/mnt/rog")
            data["rog_free_bytes"] = rog_usage.free
            data["rog_total_bytes"] = rog_usage.total
    except (OSError, ValueError, IndexError):
        data["rog_mounted"] = None
    office_service = "unknown"
    try:
        result = subprocess.run(
            ["/usr/bin/systemctl", "show", "--no-pager",
             "--property=Id,LoadState,ActiveState", *_HUD_UNITS,
             _WIREGUARD_UNIT],
            capture_output=True, text=True, errors="replace", timeout=2,
            check=False,
        )
        for block in result.stdout.strip().split("\n\n"):
            properties = dict(line.split("=", 1) for line in block.splitlines() if "=" in line)
            if properties.get("Id") == _WIREGUARD_UNIT:
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
    data["itunas_media"] = _itunas_media_status(data["office_tunnel"], mounts)
    data["network"] = _hud_network()
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
    data["overall_status"] = _overall_health(data)
    return data


def _hud_status(force=False):
    global _hud_cache, _hud_expires
    with _hud_lock:
        now = time.monotonic()
        if force or _hud_cache is None or now >= _hud_expires:
            _hud_cache = _hud_collect()
            _hud_expires = time.monotonic() + 10
        return dict(_hud_cache)


def _hud_invalidate():
    global _hud_expires
    with _hud_lock:
        _hud_expires = 0.0


def _run_itunas_action(action):
    operations = _ITUNAS_ACTIONS.get(action)
    if operations is None:
        return {"success": False, "error": "invalid_action", "itunas_status": "unavailable"}

    wireguard_status = "unavailable"
    if action == "connect":
        current = _hud_status(force=True)
        wireguard_status = current.get("office_tunnel", "unavailable")
        if wireguard_status != "connected":
            return {
                "success": False,
                "error": "office_tunnel_unavailable",
                "itunas_status": (current.get("itunas_media") or {}).get("status", "unavailable"),
                "wireguard_status": wireguard_status,
            }

    for systemctl_action, unit in operations:
        try:
            result = subprocess.run(
                ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", systemctl_action, unit],
                capture_output=True,
                text=True,
                errors="replace",
                timeout=10,
                check=False,
            )
        except subprocess.TimeoutExpired:
            _hud_invalidate()
            return {
                "success": False, "error": "control_timeout",
                "itunas_status": "unavailable", "wireguard_status": wireguard_status,
            }
        except OSError:
            _hud_invalidate()
            return {
                "success": False, "error": "control_unavailable",
                "itunas_status": "unavailable", "wireguard_status": wireguard_status,
            }
        if result.returncode != 0:
            _hud_invalidate()
            return {
                "success": False, "error": "control_failed",
                "itunas_status": "unavailable", "wireguard_status": wireguard_status,
            }

    _hud_invalidate()
    refreshed = _hud_status(force=True)
    status = (refreshed.get("itunas_media") or {}).get("status", "unavailable")
    wireguard_status = refreshed.get("office_tunnel", wireguard_status)
    expected = "connected" if action == "connect" else "disconnected"
    if status != expected:
        return {
            "success": False,
            "error": "state_not_reached",
            "itunas_status": status,
            "wireguard_status": wireguard_status,
        }
    return {
        "success": True,
        "action": action,
        "itunas_status": status,
        "wireguard_status": wireguard_status,
        "message": "ITUNAS Media connected." if action == "connect" else "ITUNAS Media disconnected.",
    }


def _loopback_control_request(request):
    return (
        _loopback_request(request)
        and request.headers.get("x-asth-control") == "touchscreen"
    )


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


@app.post("/api/itunas-control")
def itunas_control(request: Request, payload: dict):
    if not _loopback_control_request(request):
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": "local_access_required",
                "itunas_status": "unavailable",
            },
        )
    if set(payload) != {"action"} or payload.get("action") not in _ITUNAS_ACTIONS:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "invalid_action",
                "itunas_status": "unavailable",
            },
        )
    result = _run_itunas_action(payload["action"])
    return JSONResponse(status_code=200 if result["success"] else 503, content=result)
