#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


DEFAULT_LATEST_URL = (
    "https://github.com/TaterTotterson/Tater-Native-Firmware/"
    "releases/latest/download/latest.json"
)
OFFICIAL_RELEASE_PATH_PREFIX = "/TaterTotterson/Tater-Native-Firmware/releases/download/"
MAX_METADATA_BYTES = 1024 * 1024
MAX_FIRMWARE_BYTES = 64 * 1024 * 1024
DOWNLOAD_TIMEOUT_SECONDS = 90


def _request_bytes(url: str, *, limit: int) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/octet-stream",
            "User-Agent": "Tater-Assistant-Website-Firmware-Mirror/1",
        },
    )
    with urlopen(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        content_length = int(response.headers.get("Content-Length") or 0)
        if content_length > limit:
            raise RuntimeError(f"Download is larger than the allowed {limit} bytes: {url}")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = response.read(min(1024 * 1024, limit + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > limit:
                raise RuntimeError(f"Download is larger than the allowed {limit} bytes: {url}")
    return b"".join(chunks)


def _request_json(url: str) -> dict[str, Any]:
    try:
        payload = json.loads(_request_bytes(url, limit=MAX_METADATA_BYTES).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Firmware metadata is not valid JSON: {url}") from error
    if not isinstance(payload, dict):
        raise RuntimeError(f"Firmware metadata must be a JSON object: {url}")
    return payload


def _official_release_url(value: Any, *, expected_suffix: str) -> str:
    url = str(value or "").strip()
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "github.com"
        or not parsed.path.startswith(OFFICIAL_RELEASE_PATH_PREFIX)
        or not parsed.path.lower().endswith(expected_suffix.lower())
    ):
        raise RuntimeError(f"Unexpected official firmware release URL: {url or '(missing)'}")
    return url


def _safe_asset_name(url: str) -> str:
    name = Path(unquote(urlparse(url).path)).name
    if not name or name in {".", ".."} or not name.lower().endswith(".bin"):
        raise RuntimeError(f"Firmware asset does not have a safe .bin filename: {url}")
    return name


def _artifact_catalog_entry(artifact: dict[str, Any], *, target_dir: Path) -> dict[str, Any]:
    url = _official_release_url(artifact.get("path"), expected_suffix=".bin")
    filename = _safe_asset_name(url)
    expected_size = int(artifact.get("size_bytes") or 0)
    expected_sha256 = str(artifact.get("sha256") or "").strip().lower()
    if expected_size <= 0 or expected_size > MAX_FIRMWARE_BYTES:
        raise RuntimeError(f"Firmware metadata has an invalid size for {filename}.")
    if len(expected_sha256) != 64 or any(char not in "0123456789abcdef" for char in expected_sha256):
        raise RuntimeError(f"Firmware metadata has an invalid SHA-256 for {filename}.")

    data = _request_bytes(url, limit=MAX_FIRMWARE_BYTES)
    if len(data) != expected_size:
        raise RuntimeError(
            f"Firmware size check failed for {filename}: expected {expected_size}, downloaded {len(data)}."
        )
    actual_sha256 = hashlib.sha256(data).hexdigest()
    if actual_sha256 != expected_sha256:
        raise RuntimeError(f"Firmware SHA-256 check failed for {filename}.")
    if not data or data[0] != 0xE9:
        raise RuntimeError(f"Firmware image check failed for {filename}.")

    (target_dir / filename).write_bytes(data)
    return {
        "filename": filename,
        "size_bytes": expected_size,
        "sha256": expected_sha256,
        "flash_size": str(artifact.get("flash_size") or "").strip(),
        "flash_mode": str(artifact.get("flash_mode") or "dio").strip(),
        "flash_freq": str(artifact.get("flash_freq") or "40m").strip(),
    }


def mirror_latest_firmware(site_root: Path, *, latest_url: str | None = None) -> dict[str, Any]:
    source_url = str(latest_url or os.getenv("TATER_WIKI_FIRMWARE_LATEST_URL") or DEFAULT_LATEST_URL).strip()
    if source_url != DEFAULT_LATEST_URL:
        _official_release_url(source_url, expected_suffix="latest.json")

    latest = _request_json(source_url)
    if latest.get("kind") != "tater_native_satellite_firmware_latest":
        raise RuntimeError("The latest firmware index has the wrong type.")
    manifest_url = _official_release_url(latest.get("manifest"), expected_suffix="-manifest.json")
    manifest = _request_json(manifest_url)
    if manifest.get("kind") != "tater_native_satellite_firmware":
        raise RuntimeError("The latest firmware manifest has the wrong type.")

    devices = manifest.get("devices")
    if not isinstance(devices, list) or not devices:
        raise RuntimeError("The latest firmware manifest has no satellite devices.")

    firmware_root = site_root / "firmware"
    firmware_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".latest-", dir=firmware_root))
    target = firmware_root / "latest"
    previous = firmware_root / ".latest-previous"
    catalog_devices: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    seen_files: set[str] = set()
    try:
        for device in devices:
            if not isinstance(device, dict):
                raise RuntimeError("The latest firmware manifest contains an invalid device entry.")
            key = str(device.get("key") or "").strip()
            label = str(device.get("label") or "").strip()
            flash_size = str(device.get("flash_size") or "").strip()
            if not key or not label or key in seen_keys:
                raise RuntimeError("The latest firmware manifest contains an invalid or duplicate device.")
            if flash_size not in {"8MB", "16MB"}:
                raise RuntimeError(f"Unsupported flash size for {label}: {flash_size or '(missing)'}")
            artifacts = device.get("artifacts")
            if not isinstance(artifacts, dict):
                raise RuntimeError(f"The latest firmware manifest has no artifacts for {label}.")

            mirrored_artifacts: dict[str, dict[str, Any]] = {}
            for mode in ("factory", "ota"):
                artifact = artifacts.get(mode)
                if not isinstance(artifact, dict):
                    raise RuntimeError(f"The latest firmware manifest has no {mode} image for {label}.")
                entry = _artifact_catalog_entry(artifact, target_dir=staging)
                if entry["filename"] in seen_files:
                    raise RuntimeError(f"Duplicate firmware filename: {entry['filename']}")
                seen_files.add(entry["filename"])
                if entry["flash_size"] != flash_size:
                    raise RuntimeError(f"Firmware flash-size metadata does not match for {label} {mode}.")
                mirrored_artifacts[mode] = entry

            seen_keys.add(key)
            catalog_devices.append(
                {
                    "key": key,
                    "label": label,
                    "board": str(device.get("board") or "").strip(),
                    "firmware_version": str(device.get("firmware_version") or "").strip(),
                    "display_version": str(device.get("display_version") or "").strip(),
                    "flash_size": flash_size,
                    "artifacts": mirrored_artifacts,
                }
            )

        catalog = {
            "schema": 1,
            "kind": "tater_usb_flasher_catalog",
            "release": str(manifest.get("version") or latest.get("version") or "").strip(),
            "display_version": str(manifest.get("display_version") or latest.get("display_version") or "").strip(),
            "devices": catalog_devices,
        }
        (staging / "catalog.json").write_text(
            json.dumps(catalog, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        if previous.exists():
            shutil.rmtree(previous)
        if target.exists():
            target.rename(previous)
        try:
            staging.rename(target)
        except Exception:
            if previous.exists() and not target.exists():
                previous.rename(target)
            raise
        if previous.exists():
            shutil.rmtree(previous)
        return catalog
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        if previous.exists() and not target.exists():
            previous.rename(target)
        raise


if __name__ == "__main__":
    root = Path(os.getenv("TATER_WIKI_SITE_DIR") or Path(__file__).resolve().parents[1] / "public_html")
    result = mirror_latest_firmware(root.resolve())
    print(f"Mirrored {result['release']} firmware for {len(result['devices'])} satellites.")
