import importlib.util
import re
import subprocess
import sys
import types
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


class _FakeFastAPI:
    def __init__(self, **kwargs):
        self.routes = []

    def mount(self, *args, **kwargs):
        return None

    def _route(self, method, path, **kwargs):
        def decorator(function):
            self.routes.append((method, path, function))
            return function

        return decorator

    def get(self, path, **kwargs):
        return self._route("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._route("POST", path, **kwargs)


class _FakeResponse:
    def __init__(self, content=None, status_code=200, **kwargs):
        self.content = content
        self.status_code = status_code


def _load_main():
    fastapi = types.ModuleType("fastapi")
    fastapi.FastAPI = _FakeFastAPI
    fastapi.Request = object
    responses = types.ModuleType("fastapi.responses")
    responses.HTMLResponse = _FakeResponse
    responses.JSONResponse = _FakeResponse
    staticfiles = types.ModuleType("fastapi.staticfiles")
    staticfiles.StaticFiles = lambda **kwargs: object()

    module_name = "asth_main_under_test"
    with mock.patch.dict(
        sys.modules,
        {
            "fastapi": fastapi,
            "fastapi.responses": responses,
            "fastapi.staticfiles": staticfiles,
        },
    ):
        spec = importlib.util.spec_from_file_location(module_name, ROOT / "app" / "main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


class _Request:
    def __init__(self, host="127.0.0.1", client="127.0.0.1", control_header=True):
        self.headers = {"host": host}
        if control_header:
            self.headers["x-asth-control"] = "touchscreen"
        self.client = types.SimpleNamespace(host=client)


class DashboardHealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = _load_main()

    def test_cpu_percent_uses_delta_between_proc_stat_samples(self):
        previous = self.main._cpu_snapshot("cpu  100 20 30 850 0 0 0 0\n")
        current = self.main._cpu_snapshot("cpu  150 20 40 890 0 0 0 0\n")

        self.assertEqual(self.main._cpu_used_percent(previous, current), 60.0)

    def test_mount_parser_classifies_root_local_media_and_itunas(self):
        mountinfo = (
            "20 1 179:2 / / rw,relatime - ext4 /dev/mmcblk0p2 rw\n"
            "21 1 8:2 / /mnt/rog rw,relatime - ntfs3 /dev/sdb2 rw\n"
            "22 1 0:54 / /mnt/office-movies ro,relatime - cifs "
            "//192.168.1.254/Movies ro,vers=3.1.1,username=hidden\n"
        )

        mounts = self.main._parse_mountinfo(mountinfo)

        self.assertEqual(self.main._find_mount(mounts, "/")["source"], "/dev/mmcblk0p2")
        self.assertEqual(
            self.main._select_local_media(mounts)["source"],
            "/dev/sdb2",
        )
        self.assertEqual(
            self.main._itunas_media_status("connected", mounts),
            {"label": "ITUNAS via WireGuard", "status": "connected", "read_only": True},
        )

    def test_itunas_is_disconnected_when_tunnel_is_down(self):
        self.assertEqual(
            self.main._itunas_media_status("disconnected", []),
            {"label": "ITUNAS via WireGuard", "status": "disconnected", "read_only": None},
        )

    def test_itunas_is_unavailable_when_mount_identity_is_unexpected(self):
        mounts = self.main._parse_mountinfo(
            "22 1 0:54 / /mnt/office-movies ro - cifs //other/Movies ro\n"
        )

        self.assertEqual(
            self.main._itunas_media_status("connected", mounts)["status"],
            "unavailable",
        )

    def test_overall_health_ignores_disconnected_optional_itunas(self):
        data = {
            "service_asth": "active",
            "service_nginx": "active",
            "service_jellyfin": "active",
            "service_smbd": "active",
            "service_cockpit": "active",
            "cpu_temperature_c": 50.0,
            "cpu_used_percent": 20.0,
            "ram_used_percent": 40.0,
            "root_storage": {"used_percent": 30.0},
            "local_media_storage": {"status": "connected"},
            "itunas_media": {"status": "disconnected"},
        }

        self.assertEqual(self.main._overall_health(data), "sihat")

    def test_overall_health_reports_core_service_failure(self):
        data = {
            "service_asth": "active",
            "service_nginx": "failed",
            "cpu_temperature_c": 50.0,
            "cpu_used_percent": 20.0,
            "ram_used_percent": 40.0,
            "root_storage": {"used_percent": 30.0},
            "local_media_storage": {"status": "connected"},
        }

        self.assertEqual(self.main._overall_health(data), "gangguan")

    def test_overall_health_warns_when_supporting_service_is_stopped(self):
        data = {
            "service_asth": "active",
            "service_nginx": "active",
            "service_jellyfin": "inactive",
            "service_smbd": "active",
            "service_cockpit": "active",
            "cpu_temperature_c": 50.0,
            "cpu_used_percent": 20.0,
            "ram_used_percent": 40.0,
            "root_storage": {"used_percent": 30.0},
            "local_media_storage": {"status": "connected"},
        }

        self.assertEqual(self.main._overall_health(data), "amaran")

    def test_network_parser_returns_lan_and_hotspot_ipv4_addresses(self):
        addresses = [
            {
                "ifname": "eth0",
                "operstate": "UP",
                "addr_info": [{"family": "inet", "local": "192.168.100.187"}],
            },
            {
                "ifname": "wlan0",
                "operstate": "UP",
                "addr_info": [{"family": "inet", "local": "10.42.0.1"}],
            },
        ]

        self.assertEqual(
            self.main._parse_network_addresses(addresses),
            {
                "lan_ip": "192.168.100.187",
                "hotspot_ip": "10.42.0.1",
                "hotspot_state": "connected",
            },
        )

    def test_cockpit_is_part_of_the_fixed_service_whitelist(self):
        self.assertEqual(self.main._HUD_UNITS["cockpit.socket"], "service_cockpit")

    def test_health_contract_remains_exact(self):
        self.assertEqual(
            self.main.health(),
            {
                "status": "healthy",
                "service": "ASTH Adaptive Smart Training Hub",
                "version": "0.4.0",
            },
        )

    def test_hub_status_preserves_legacy_fields(self):
        hud = {
            "cpu_temperature_c": 48.0,
            "ram_used_percent": 25.0,
            "rog_mounted": True,
            "rog_free_bytes": 10,
            "rog_total_bytes": 20,
            "service_asth": "active",
            "service_nginx": "active",
            "service_jellyfin": "active",
            "service_smbd": "active",
            "service_pm2": "active",
            "service_uptime_kuma": "active",
            "office_tunnel": "connected",
        }
        with mock.patch.object(self.main, "_hud_status", return_value=hud), mock.patch.object(
            self.main, "_hub_connected_stations", return_value=2
        ), mock.patch.object(self.main, "_hub_read_int", return_value=7), mock.patch.object(
            self.main, "_hub_uptime_seconds", return_value=9
        ), mock.patch.object(self.main, "_hub_wifi_ssid", return_value="ASTH-PORTABLE"):
            result = self.main.hub_status()

        legacy = {
            "status", "connected_devices", "rx_bytes", "tx_bytes", "uptime_seconds",
            "wifi_ssid", "cpu_temperature_c", "ram_used_percent", "rog_mounted",
            "rog_free_bytes", "rog_total_bytes", "service_asth", "service_nginx",
            "service_jellyfin", "service_smbd", "service_pm2", "service_uptime_kuma",
            "office_tunnel",
        }
        self.assertTrue(legacy.issubset(result))


class ItunasControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = _load_main()

    def _completed(self, returncode=0):
        return subprocess.CompletedProcess([], returncode, stdout="secret-output", stderr="secret-error")

    def test_valid_connect_starts_only_fixed_media_units_and_refreshes_status(self):
        calls = []

        def runner(command, **kwargs):
            calls.append((command, kwargs))
            return self._completed()

        with mock.patch.object(self.main.subprocess, "run", side_effect=runner), mock.patch.object(
            self.main,
            "_hud_status",
            side_effect=[
                {"office_tunnel": "connected", "itunas_media": {"status": "disconnected"}},
                {"office_tunnel": "connected", "itunas_media": {"status": "connected"}},
            ],
        ):
            result = self.main._run_itunas_action("connect")

        self.assertTrue(result["success"])
        self.assertEqual(result["itunas_status"], "connected")
        self.assertNotIn("secret", str(result))
        self.assertEqual([call[0] for call in calls], [
            ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "start", r"mnt-office\x2dmovies.automount"],
            ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "start", r"mnt-office\x2dmovies.mount"],
        ])
        self.assertTrue(all(call[1]["timeout"] == 10 for call in calls))
        self.assertNotIn("wg-quick@asth-office.service", str(calls))

    def test_valid_disconnect_stops_automount_before_fixed_mount(self):
        calls = []

        def runner(command, **kwargs):
            calls.append(command)
            return self._completed()

        with mock.patch.object(
            self.main.subprocess, "run", side_effect=runner
        ), mock.patch.object(
            self.main, "_hud_status", return_value={"itunas_media": {"status": "disconnected"}}
        ):
            result = self.main._run_itunas_action("disconnect")

        self.assertTrue(result["success"])
        self.assertEqual(calls, [
            ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "stop", r"mnt-office\x2dmovies.automount"],
            ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "stop", r"mnt-office\x2dmovies.mount"],
        ])
        self.assertNotIn("wg-quick@asth-office.service", str(calls))

    def test_connect_refuses_to_mutate_units_when_wireguard_is_not_connected(self):
        with mock.patch.object(self.main.subprocess, "run") as runner, mock.patch.object(
            self.main,
            "_hud_status",
            return_value={
                "office_tunnel": "disconnected",
                "itunas_media": {"status": "disconnected"},
            },
        ):
            result = self.main._run_itunas_action("connect")

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "office_tunnel_unavailable")
        self.assertEqual(result["wireguard_status"], "disconnected")
        runner.assert_not_called()

    def test_invalid_action_is_rejected_without_running_a_command(self):
        with mock.patch.object(self.main.subprocess, "run") as runner:
            result = self.main._run_itunas_action("restart nginx.service")

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_action")
        runner.assert_not_called()

    def test_systemctl_timeout_returns_sanitized_failure(self):
        with mock.patch.object(self.main, "_hud_status", return_value={
            "office_tunnel": "connected", "itunas_media": {"status": "disconnected"}
        }), mock.patch.object(
            self.main.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired("systemctl secret", 10, output="secret"),
        ):
            result = self.main._run_itunas_action("connect")

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "control_timeout")
        self.assertNotIn("secret", str(result))

    def test_systemctl_failure_returns_sanitized_failure(self):
        with mock.patch.object(self.main, "_hud_status", return_value={
            "office_tunnel": "connected", "itunas_media": {"status": "disconnected"}
        }), mock.patch.object(
            self.main.subprocess, "run", return_value=self._completed(returncode=1)
        ):
            result = self.main._run_itunas_action("connect")

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "control_failed")
        self.assertNotIn("secret", str(result))

    def test_successful_command_fails_when_refreshed_media_state_does_not_match(self):
        with mock.patch.object(
            self.main.subprocess, "run", return_value=self._completed()
        ), mock.patch.object(
            self.main,
            "_hud_status",
            side_effect=[
                {"office_tunnel": "connected", "itunas_media": {"status": "disconnected"}},
                {"office_tunnel": "connected", "itunas_media": {"status": "disconnected"}},
            ],
        ):
            result = self.main._run_itunas_action("connect")

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "state_not_reached")
        self.assertEqual(result["itunas_status"], "disconnected")

    def test_endpoint_rejects_non_loopback_and_extra_payload_fields(self):
        remote = self.main.itunas_control(
            _Request(host="10.42.0.1", client="10.42.0.20"),
            {"action": "connect"},
        )
        injected = self.main.itunas_control(
            _Request(),
            {"action": "connect", "service": "nginx.service"},
        )

        self.assertEqual(remote.status_code, 403)
        self.assertEqual(injected.status_code, 400)

    def test_endpoint_rejects_request_without_control_header(self):
        response = self.main.itunas_control(
            _Request(control_header=False),
            {"action": "connect"},
        )

        self.assertEqual(response.status_code, 403)

    def test_dashboard_contains_confirmation_control_and_status_refresh(self):
        page = self.main.LANDING_PAGE

        self.assertIn("CONNECT ITUNAS", page)
        self.assertIn("DISCONNECT ITUNAS", page)
        self.assertIn("/api/itunas-control", page)
        self.assertIn("window.confirm", page)
        self.assertIn("setTimeout(refreshStatus, 5000)", page)
        self.assertNotIn("setInterval(refreshStatus", page)
        self.assertIn("<strong>WireGuard</strong>", page)
        self.assertIn('id="wireguardBadge"', page)
        self.assertIn("<strong>ITUNAS Media</strong>", page)


class StudentQrAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = _load_main()

    def test_root_page_exposes_student_portal_dialog_and_instructions(self):
        page = self.main.root().content

        self.assertIn('id="studentAccessButton"', page)
        self.assertIn('id="studentQrDialog"', page)
        self.assertIn('id="closeStudentQr"', page)
        self.assertIn("AKSES PELAJAR / QR", page)
        self.assertIn("SSID: ASTH-PORTABLE", page)
        self.assertIn("1. Sambung ke Wi-Fi ASTH-PORTABLE", page)
        self.assertIn("2. Imbas QR Portal", page)
        self.assertIn("3. Akses perkhidmatan ASTH", page)

    def test_portal_qr_is_inline_black_on_white_and_has_exact_target(self):
        page = self.main.root().content
        match = re.search(r'(<svg[^>]+id="portalQr"[\s\S]*?</svg>)', page)

        self.assertIsNotNone(match)
        svg = ET.fromstring(match.group(1))
        self.assertEqual(svg.attrib["data-qr-target"], "http://10.42.0.1/")
        self.assertEqual(svg.attrib["role"], "img")
        fills = {element.attrib.get("fill") for element in svg.iter()}
        self.assertIn("#ffffff", fills)
        self.assertIn("#000000", fills)
        self.assertNotIn("<image", match.group(1))
        self.assertNotRegex(match.group(1), r'https?://[^\s"\']+\.(?:png|svg|js)')


class DashboardVisualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = _load_main()

    def test_dashboard_text_and_status_colours_meet_accessible_contrast(self):
        page = self.main.root().content
        variables = dict(re.findall(r"--([a-z]+):\s*(#[0-9a-fA-F]{6})", page))

        def luminance(colour):
            channels = [int(colour[index:index + 2], 16) / 255 for index in (1, 3, 5)]
            channels = [
                value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
                for value in channels
            ]
            return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

        def contrast(first, second="#ffffff"):
            light, dark = sorted((luminance(first), luminance(second)), reverse=True)
            return (light + 0.05) / (dark + 0.05)

        for name in ("ink", "muted", "green", "amber", "red", "blue"):
            with self.subTest(name=name):
                self.assertGreaterEqual(contrast(variables[name]), 4.5)


if __name__ == "__main__":
    unittest.main()
