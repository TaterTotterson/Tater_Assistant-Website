from __future__ import annotations

import unittest
import hashlib
import json
import tempfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "build_wiki.py"
FLASHER = ROOT / "public_html" / "assets" / "usb-flasher.js"
FLASHER_ENGINE = ROOT / "public_html" / "assets" / "vendor" / "esptool-js-0.5.7.bundle.js"
FLASHER_LICENSE = ROOT / "public_html" / "assets" / "vendor" / "esptool-js-0.5.7.LICENSE.txt"
FLASHER_MASCOT = ROOT / "public_html" / "assets" / "images" / "tater-mascot-firmware-flasher.png"
FIRMWARE_MIRROR = ROOT / "scripts" / "mirror_latest_firmware.py"


class UsbFlasherSiteTests(unittest.TestCase):
    def test_generator_keeps_usb_flasher_in_navigation_and_build(self) -> None:
        source = GENERATOR.read_text(encoding="utf-8")

        self.assertIn('("usb-flasher", "USB Flasher"', source)
        self.assertIn("def render_usb_flasher_page()", source)
        self.assertIn('SITE_ROOT / "usb-flasher" / "index.html"', source)
        self.assertIn("Factory Install", source)
        self.assertIn("OTA · Keep Settings", source)
        self.assertIn("data-usb-device", source)
        self.assertIn("tater-mascot-firmware-flasher.png", source)
        self.assertNotIn("data-usb-file", source)
        self.assertNotIn("data-usb-flash-size", source)
        self.assertIn('src="../assets/usb-flasher.js"', source)

    def test_browser_flasher_loads_verified_latest_firmware_and_uses_safe_offsets(self) -> None:
        source = FLASHER.read_text(encoding="utf-8")

        self.assertIn('"8MB": [0x20000, 0x320000]', source)
        self.assertIn('"16MB": [0x20000, 0x320000, 0x620000]', source)
        self.assertIn('state.mode === "factory" ? [0]', source)
        self.assertIn('const eraseAll = state.mode === "factory"', source)
        self.assertIn("navigator.serial.requestPort()", source)
        self.assertIn("window.isSecureContext", source)
        self.assertIn("../firmware/latest/catalog.json", source)
        self.assertIn('crypto.subtle.digest("SHA-256"', source)
        self.assertIn("bytes.byteLength !== firmware.sizeBytes", source)
        self.assertNotIn("FileReader", source)
        self.assertNotIn("web.esphome.io", source)

    def test_firmware_mirror_verifies_and_publishes_a_complete_release(self) -> None:
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import mirror_latest_firmware as mirror
        finally:
            sys.path.pop(0)

        factory = bytes([0xE9, 1, 2, 3])
        ota = bytes([0xE9, 4, 5, 6])
        manifest_url = (
            "https://github.com/TaterTotterson/Tater-Native-Firmware/"
            "releases/download/native-test/native-test-manifest.json"
        )
        factory_url = (
            "https://github.com/TaterTotterson/Tater-Native-Firmware/"
            "releases/download/native-test/native-test-satellite1-factory.bin"
        )
        ota_url = (
            "https://github.com/TaterTotterson/Tater-Native-Firmware/"
            "releases/download/native-test/native-test-satellite1-ota.bin"
        )
        latest = {
            "kind": "tater_native_satellite_firmware_latest",
            "version": "native-test",
            "display_version": "test",
            "manifest": manifest_url,
        }
        manifest = {
            "kind": "tater_native_satellite_firmware",
            "version": "native-test",
            "display_version": "test",
            "devices": [
                {
                    "key": "satellite1",
                    "label": "Satellite1",
                    "board": "satellite1",
                    "firmware_version": "native-satellite1-test",
                    "display_version": "test",
                    "flash_size": "16MB",
                    "artifacts": {
                        "factory": {
                            "path": factory_url,
                            "size_bytes": len(factory),
                            "sha256": hashlib.sha256(factory).hexdigest(),
                            "flash_size": "16MB",
                        },
                        "ota": {
                            "path": ota_url,
                            "size_bytes": len(ota),
                            "sha256": hashlib.sha256(ota).hexdigest(),
                            "flash_size": "16MB",
                        },
                    },
                }
            ],
        }

        responses = {
            mirror.DEFAULT_LATEST_URL: json.dumps(latest).encode(),
            manifest_url: json.dumps(manifest).encode(),
            factory_url: factory,
            ota_url: ota,
        }
        with tempfile.TemporaryDirectory() as temporary:
            site_root = Path(temporary)
            with mock.patch.object(mirror, "_request_bytes", side_effect=lambda url, limit: responses[url]):
                catalog = mirror.mirror_latest_firmware(site_root)
            target = site_root / "firmware" / "latest"
            self.assertEqual(catalog["release"], "native-test")
            self.assertEqual((target / "native-test-satellite1-factory.bin").read_bytes(), factory)
            self.assertEqual((target / "native-test-satellite1-ota.bin").read_bytes(), ota)
            self.assertEqual(json.loads((target / "catalog.json").read_text())["devices"][0]["key"], "satellite1")

    def test_bundled_flashing_engine_and_license_are_present(self) -> None:
        self.assertGreater(FLASHER_ENGINE.stat().st_size, 100_000)
        self.assertIn("Apache License", FLASHER_LICENSE.read_text(encoding="utf-8"))
        self.assertTrue(FIRMWARE_MIRROR.is_file())
        self.assertGreater(FLASHER_MASCOT.stat().st_size, 500_000)


if __name__ == "__main__":
    unittest.main()
