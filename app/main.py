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
    return HTMLResponse(
        content=LANDING_PAGE.replace("<!-- ASTH_WIFI_ACCESS -->", _wifi_access_markup())
    )


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
    raw_host = request.headers.get("host", "").strip().lower()
    if raw_host.startswith("[") and "]" in raw_host:
        host = raw_host[1:raw_host.index("]")]
    else:
        host = raw_host.split(":", 1)[0]
    client = getattr(getattr(request, "client", None), "host", "")
    return (
        host in ("127.0.0.1", "localhost", "::1")
        and client in ("127.0.0.1", "::1")
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
