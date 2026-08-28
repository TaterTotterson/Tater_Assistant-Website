const TOOL_MODULE_URL = "./vendor/esptool-js-0.5.7.bundle.js";
const FIRMWARE_CATALOG_URL = "../firmware/latest/catalog.json";
const FIRMWARE_ASSET_ROOT = "../firmware/latest/";
const MAX_FIRMWARE_BYTES = 64 * 1024 * 1024;
const OTA_APP_PARTITION_BYTES = 0x300000;
const OTA_APP_OFFSETS = {
  "8MB": [0x20000, 0x320000],
  "16MB": [0x20000, 0x320000, 0x620000],
};

const root = document.querySelector("[data-usb-flasher]");

if (root) {
  const elements = {
    browserState: document.querySelector("[data-usb-browser-state]"),
    device: root.querySelector("[data-usb-device]"),
    firmwareSummary: root.querySelector("[data-usb-firmware-summary]"),
    modeButtons: Array.from(root.querySelectorAll("[data-usb-mode]")),
    modeWarning: root.querySelector("[data-usb-mode-warning]"),
    readySummary: root.querySelector("[data-usb-ready-summary]"),
    flashButton: root.querySelector("[data-usb-flash]"),
    statusTitle: root.querySelector("[data-usb-status-title]"),
    statusDetail: root.querySelector("[data-usb-status-detail]"),
    statusDot: root.querySelector("[data-usb-status-dot]"),
    progress: root.querySelector("[data-usb-progress]"),
    progressBar: root.querySelector("[data-usb-progress-bar]"),
    progressLabel: root.querySelector("[data-usb-progress-label]"),
    progressValue: root.querySelector("[data-usb-progress-value]"),
    log: root.querySelector("[data-usb-log]"),
    clearLog: root.querySelector("[data-usb-clear-log]"),
  };

  const state = {
    mode: "factory",
    deviceKey: "",
    catalog: null,
    catalogLoading: true,
    catalogError: "",
    busy: false,
    toolModule: null,
  };

  const formatBytes = (value) => {
    let size = Math.max(0, Number(value) || 0);
    const units = ["B", "KB", "MB", "GB"];
    for (const unit of units) {
      if (size < 1024 || unit === units.at(-1)) {
        return unit === "B" ? `${Math.round(size)} ${unit}` : `${size.toFixed(1)} ${unit}`;
      }
      size /= 1024;
    }
    return `${Number(value) || 0} B`;
  };

  const delay = (milliseconds) =>
    new Promise((resolve) => window.setTimeout(resolve, Math.max(0, Number(milliseconds) || 0)));

  const browserCapability = () => {
    if (!window.isSecureContext) {
      return { available: false, message: "Browser USB needs this secure Tater page to be opened over HTTPS." };
    }
    if (!navigator.serial || typeof navigator.serial.requestPort !== "function") {
      return { available: false, message: "Browser USB is unavailable here. Open this page in desktop Chrome or Edge." };
    }
    return {
      available: true,
      message: "Browser USB is ready. Chrome will ask which connected satellite you want to use.",
    };
  };

  const appendLog = (message, tone = "info") => {
    if (!elements.log) return;
    const messageText = String(message || "").trim();
    if (!messageText) return;
    const line = document.createElement("div");
    line.className = `usb-log-line tone-${tone}`;
    line.textContent = messageText;
    elements.log.appendChild(line);
    elements.log.scrollTop = elements.log.scrollHeight;
  };

  const setStatus = (title, detail, tone = "idle") => {
    if (elements.statusTitle) elements.statusTitle.textContent = String(title || "");
    if (elements.statusDetail) elements.statusDetail.textContent = String(detail || "");
    if (elements.statusDot) elements.statusDot.dataset.tone = tone;
  };

  const setProgress = (percent, label) => {
    const value = Math.max(0, Math.min(100, Math.round(Number(percent) || 0)));
    if (elements.progress) elements.progress.setAttribute("aria-valuenow", String(value));
    if (elements.progressBar) elements.progressBar.style.width = `${value}%`;
    if (elements.progressValue) elements.progressValue.textContent = `${value}%`;
    if (elements.progressLabel && label) elements.progressLabel.textContent = String(label);
  };

  const selectedDevice = () => {
    const devices = Array.isArray(state.catalog?.devices) ? state.catalog.devices : [];
    return devices.find((device) => device.key === state.deviceKey) || null;
  };

  const selectedFirmware = () => {
    const device = selectedDevice();
    const artifact = device?.artifacts?.[state.mode];
    if (!device || !artifact) return null;
    const filename = String(artifact.filename || "");
    return {
      device,
      name: filename,
      url: new URL(`${FIRMWARE_ASSET_ROOT}${encodeURIComponent(filename)}`, window.location.href).toString(),
      sizeBytes: Number(artifact.size_bytes || 0),
      sha256: String(artifact.sha256 || "").toLowerCase(),
      flashSize: String(artifact.flash_size || device.flash_size || ""),
      flashMode: String(artifact.flash_mode || "dio"),
      flashFreq: String(artifact.flash_freq || "40m"),
    };
  };

  const renderReadyState = () => {
    const capability = browserCapability();
    const firmware = selectedFirmware();
    if (elements.browserState) {
      elements.browserState.dataset.tone = capability.available ? "ready" : "error";
      elements.browserState.textContent = capability.message;
    }
    if (elements.flashButton) {
      elements.flashButton.disabled =
        state.busy || state.catalogLoading || Boolean(state.catalogError) || !capability.available || !firmware;
      elements.flashButton.textContent = state.busy ? "Flashing…" : "Connect & Flash Latest";
    }
    if (!elements.readySummary) return;
    if (state.busy) {
      elements.readySummary.textContent = "Keep this page open and leave the USB cable connected.";
    } else if (state.catalogLoading) {
      elements.readySummary.textContent = "Loading the latest official Tater firmware…";
    } else if (state.catalogError) {
      elements.readySummary.textContent = state.catalogError;
    } else if (!capability.available) {
      elements.readySummary.textContent = capability.message;
    } else if (!firmware) {
      elements.readySummary.textContent = "Select your Tater satellite to continue.";
    } else {
      const modeLabel = state.mode === "factory" ? "Factory Install" : "OTA · Keep Settings";
      const version = firmware.device.display_version ? `v${firmware.device.display_version}` : "latest";
      elements.readySummary.textContent = `${firmware.device.label} ${version} · ${modeLabel} is ready.`;
    }
  };

  const renderFirmwareSummary = () => {
    if (!elements.firmwareSummary) return;
    elements.firmwareSummary.replaceChildren();
    const title = document.createElement("strong");
    const detail = document.createElement("span");
    if (state.catalogLoading) {
      title.textContent = "Loading latest firmware…";
      detail.textContent = "Checking the official Tater release.";
    } else if (state.catalogError) {
      title.textContent = "Latest firmware could not be loaded.";
      detail.textContent = state.catalogError;
    } else {
      const device = selectedDevice();
      if (!device) {
        const release = String(state.catalog?.display_version || "").trim();
        title.textContent = release ? `Latest release: ${release}` : "Latest official firmware is ready.";
        detail.textContent = "Choose the satellite model connected over USB.";
      } else {
        const firmware = selectedFirmware();
        title.textContent = `${device.label} · v${device.display_version || "latest"}`;
        detail.textContent = firmware
          ? `${state.mode === "factory" ? "Factory" : "OTA"} image · ${formatBytes(firmware.sizeBytes)} · ${firmware.flashSize}`
          : "Firmware is unavailable for the selected install type.";
      }
    }
    elements.firmwareSummary.append(title, detail);
  };

  const renderMode = () => {
    for (const button of elements.modeButtons) {
      const active = button.dataset.usbMode === state.mode;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-checked", String(active));
    }
    const ota = state.mode === "ota";
    if (elements.modeWarning) {
      elements.modeWarning.dataset.tone = ota ? "keep" : "factory";
      elements.modeWarning.textContent = ota
        ? "OTA · Keep Settings updates the application without erasing Wi-Fi, pairing, or saved settings."
        : "Factory Install removes Wi-Fi, pairing, and saved settings. The device will need setup again afterward.";
    }
    renderFirmwareSummary();
    renderReadyState();
  };

  const setBusy = (busy) => {
    state.busy = Boolean(busy);
    for (const control of elements.modeButtons) control.disabled = state.busy;
    if (elements.device) elements.device.disabled = state.busy || state.catalogLoading || Boolean(state.catalogError);
    renderReadyState();
  };

  const validateArtifact = (artifact, flashSize) => {
    const filename = String(artifact?.filename || "");
    const size = Number(artifact?.size_bytes || 0);
    const sha256 = String(artifact?.sha256 || "").toLowerCase();
    return (
      /^[a-z0-9._-]+\.bin$/i.test(filename) &&
      size > 0 &&
      size <= MAX_FIRMWARE_BYTES &&
      /^[a-f0-9]{64}$/.test(sha256) &&
      String(artifact?.flash_size || "") === flashSize
    );
  };

  const validateCatalog = (catalog) => {
    if (catalog?.kind !== "tater_usb_flasher_catalog" || !Array.isArray(catalog.devices) || !catalog.devices.length) {
      throw new Error("The Tater firmware catalog is not valid.");
    }
    const keys = new Set();
    for (const device of catalog.devices) {
      const key = String(device?.key || "");
      const label = String(device?.label || "");
      const flashSize = String(device?.flash_size || "");
      if (!key || !label || keys.has(key) || !OTA_APP_OFFSETS[flashSize]) {
        throw new Error("The Tater firmware catalog contains an unsupported satellite.");
      }
      if (!validateArtifact(device?.artifacts?.factory, flashSize) || !validateArtifact(device?.artifacts?.ota, flashSize)) {
        throw new Error(`The latest firmware for ${label} is incomplete.`);
      }
      keys.add(key);
    }
    return catalog;
  };

  const loadLatestCatalog = async () => {
    state.catalogLoading = true;
    state.catalogError = "";
    renderFirmwareSummary();
    renderReadyState();
    try {
      const response = await fetch(FIRMWARE_CATALOG_URL, { cache: "no-store" });
      if (!response.ok) throw new Error(`Firmware catalog request failed (HTTP ${response.status}).`);
      state.catalog = validateCatalog(await response.json());
      if (elements.device) {
        elements.device.replaceChildren();
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Select your Tater satellite";
        elements.device.appendChild(placeholder);
        for (const device of state.catalog.devices) {
          const option = document.createElement("option");
          option.value = device.key;
          option.textContent = `${device.label} · v${device.display_version || "latest"}`;
          elements.device.appendChild(option);
        }
      }
      appendLog(`Latest firmware catalog loaded: ${state.catalog.release || "official release"}.`, "success");
      setStatus("Latest firmware ready.", "Select the satellite connected over USB.", "idle");
    } catch (error) {
      state.catalog = null;
      state.catalogError = "Reload this page to try loading the latest official firmware again.";
      appendLog(`Latest firmware failed to load: ${String(error?.message || error)}`, "error");
      setStatus("Latest firmware unavailable.", state.catalogError, "error");
    } finally {
      state.catalogLoading = false;
      if (elements.device) elements.device.disabled = Boolean(state.catalogError);
      renderFirmwareSummary();
      renderReadyState();
    }
  };

  const normalizeToolModule = (module) => {
    if (module?.ESPLoader && module?.Transport) return module;
    if (module?.default?.ESPLoader && module?.default?.Transport) return module.default;
    return null;
  };

  const loadToolModule = async () => {
    if (state.toolModule) return state.toolModule;
    const module = normalizeToolModule(await import(TOOL_MODULE_URL));
    if (!module) throw new Error("The bundled Tater USB flashing engine could not be loaded.");
    state.toolModule = module;
    return module;
  };

  const sha256Hex = async (bytes) => {
    const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
    return Array.from(digest, (value) => value.toString(16).padStart(2, "0")).join("");
  };

  const loadFirmwareBytes = async (firmware) => {
    appendLog(`Loading ${firmware.device.label} ${state.mode} firmware from Tater…`);
    setStatus("Loading latest firmware…", `${firmware.device.label} v${firmware.device.display_version || "latest"}`, "busy");
    setProgress(8, "Loading latest firmware");
    const response = await fetch(firmware.url, { cache: "no-store" });
    if (!response.ok) throw new Error(`Firmware download failed (HTTP ${response.status}).`);
    const bytes = new Uint8Array(await response.arrayBuffer());
    if (!bytes.byteLength || bytes.byteLength > MAX_FIRMWARE_BYTES || bytes.byteLength !== firmware.sizeBytes) {
      throw new Error(`Firmware size verification failed for ${firmware.name}.`);
    }
    if (bytes[0] !== 0xe9) {
      throw new Error("The latest file does not look like an ESP firmware image. Nothing was written.");
    }
    if (state.mode === "ota" && bytes.byteLength > OTA_APP_PARTITION_BYTES) {
      throw new Error(`The OTA image is too large for Tater's app partition (${formatBytes(bytes.byteLength)}).`);
    }
    const actualSha256 = await sha256Hex(bytes);
    if (actualSha256 !== firmware.sha256) {
      throw new Error("Firmware verification failed. Nothing was written to the satellite.");
    }
    appendLog(`Latest firmware verified (${formatBytes(bytes.byteLength)}).`, "success");
    return bytes;
  };

  const uint8ArrayToBinaryString = (bytes) => {
    const chunks = [];
    const chunkSize = 0x8000;
    for (let offset = 0; offset < bytes.length; offset += chunkSize) {
      chunks.push(String.fromCharCode(...bytes.subarray(offset, offset + chunkSize)));
    }
    return chunks.join("");
  };

  const portLabel = (port) => {
    const info = port?.getInfo?.() || {};
    const vendor = Number(info.usbVendorId || 0);
    const product = Number(info.usbProductId || 0);
    if (!vendor && !product) return "USB serial device";
    const hex = (value) => value.toString(16).padStart(4, "0");
    return `USB ${hex(vendor)}:${hex(product)}`;
  };

  const resetAfterFlash = async (transport, loader, port) => {
    try {
      appendLog("Restarting the satellite…");
      if (transport && typeof transport.setRTS === "function") {
        await transport.setRTS(true);
      } else if (typeof port?.setSignals === "function") {
        await port.setSignals({ dataTerminalReady: false, requestToSend: true, break: false });
      }
      await delay(100);
      if (typeof loader?.after === "function") await loader.after();
      await delay(800);
      return true;
    } catch (error) {
      appendLog(`Automatic restart warning: ${String(error?.message || error)}`, "warn");
      return false;
    }
  };

  const runFlash = async (port, firmware, bytes) => {
    const module = await loadToolModule();
    const { ESPLoader, Transport } = module;
    const transport = new Transport(port);
    const terminal = {
      clean() {},
      writeLine(data) { appendLog(String(data || "").trim(), "debug"); },
      write(data) {
        const output = String(data || "").trim();
        if (output) appendLog(output, "debug");
      },
    };
    const loader = new ESPLoader({ transport, baudrate: 115200, terminal, debugLogging: false });

    try {
      setStatus("Connecting to the satellite…", `Opening ${portLabel(port)}.`, "busy");
      setProgress(12, "Connecting");
      appendLog(`Connecting to ${portLabel(port)}…`);
      const chipName = String((await loader.main()) || "ESP device");
      appendLog(`Connected to ${chipName}.`, "success");
      if (!chipName.toUpperCase().includes("ESP32-S3")) {
        throw new Error(`Tater satellite flashing expects an ESP32-S3, but the browser found ${chipName}.`);
      }

      const addresses = state.mode === "factory" ? [0] : OTA_APP_OFFSETS[firmware.flashSize];
      if (!addresses?.length) throw new Error(`Unsupported flash size: ${firmware.flashSize || "unknown"}.`);
      const eraseAll = state.mode === "factory";
      const files = addresses.map((address) => ({ data: bytes, address }));
      const modeLabel = eraseAll ? "Factory Install" : "OTA · Keep Settings";
      appendLog(
        eraseAll
          ? "Erasing the device before writing the factory image."
          : `Writing the OTA image to ${addresses.length} Tater app slots without erasing setup data.`
      );
      setStatus(
        eraseAll ? "Erasing and installing…" : "Updating and keeping settings…",
        `${modeLabel} is now writing to ${firmware.device.label}.`,
        "busy"
      );
      setProgress(18, eraseAll ? "Erasing" : "Preparing update");

      let lastReported = -1;
      const flashOptions = {
        fileArray: files,
        flashMode: firmware.flashMode,
        flashFreq: firmware.flashFreq,
        flashSize: firmware.flashSize,
        eraseAll,
        compress: true,
        reportProgress: (fileIndex, written, total) => {
          const fileProgress = total > 0 ? written / total : 0;
          const writePercent = Math.floor(((Number(fileIndex || 0) + fileProgress) / files.length) * 100);
          if (writePercent >= lastReported + 2 || writePercent === 100) {
            lastReported = writePercent;
            setProgress(20 + Math.round(writePercent * 0.76), `Writing firmware · ${writePercent}%`);
            if (writePercent % 10 === 0 || writePercent === 100) appendLog(`Flash progress: ${writePercent}%`);
          }
        },
      };

      try {
        await loader.writeFlash(flashOptions);
      } catch (error) {
        const message = String(error?.message || error || "");
        if (!message.includes("charCodeAt")) throw error;
        appendLog("Retrying with the compatibility firmware format…", "warn");
        await loader.writeFlash({
          ...flashOptions,
          eraseAll: false,
          fileArray: addresses.map((address) => ({ data: uint8ArrayToBinaryString(bytes), address })),
        });
      }

      setProgress(97, "Restarting satellite");
      const resetWorked = await resetAfterFlash(transport, loader, port);
      if (!resetWorked) appendLog("If the satellite does not restart, unplug and reconnect its USB cable once.", "warn");
      setProgress(100, "Complete");
      setStatus("Firmware installed.", `${modeLabel} completed successfully on ${firmware.device.label}.`, "success");
      appendLog(`${modeLabel} completed successfully.`, "success");
    } finally {
      try {
        await transport.disconnect();
      } catch (_error) {
        // The reset path may already have released the serial port.
      }
    }
  };

  const startFlash = async () => {
    if (state.busy) return;
    const capability = browserCapability();
    const firmware = selectedFirmware();
    if (!capability.available || !firmware) {
      setStatus("The flasher is not ready.", capability.available ? "Select your satellite first." : capability.message, "error");
      return;
    }
    if (state.mode === "factory") {
      const confirmed = window.confirm(
        `Factory Install will erase Wi-Fi, pairing, and saved settings on this ${firmware.device.label}. Continue?`
      );
      if (!confirmed) {
        appendLog("Factory Install cancelled before USB access was requested.", "warn");
        return;
      }
    }

    let port;
    try {
      port = await navigator.serial.requestPort();
    } catch (error) {
      if (error?.name === "NotFoundError") {
        setStatus("No USB device selected.", "Click Connect & Flash Latest whenever you are ready.", "idle");
        appendLog("USB device selection was cancelled.", "warn");
        return;
      }
      setStatus("USB access failed.", String(error?.message || error), "error");
      appendLog(`USB access failed: ${String(error?.message || error)}`, "error");
      return;
    }

    setBusy(true);
    setProgress(3, "Preparing latest firmware");
    try {
      const [bytes] = await Promise.all([loadFirmwareBytes(firmware), loadToolModule()]);
      await runFlash(port, firmware, bytes);
    } catch (error) {
      const message = String(error?.message || error || "Unknown browser USB error.");
      setStatus("Flash failed.", message, "error");
      appendLog(`Flash failed: ${message}`, "error");
    } finally {
      setBusy(false);
    }
  };

  for (const button of elements.modeButtons) {
    button.addEventListener("click", () => {
      state.mode = button.dataset.usbMode === "ota" ? "ota" : "factory";
      renderMode();
    });
  }
  elements.device?.addEventListener("change", () => {
    state.deviceKey = String(elements.device.value || "");
    const device = selectedDevice();
    if (device) {
      setStatus("Satellite selected.", `${device.label} v${device.display_version || "latest"} is ready.`, "idle");
      appendLog(`Selected ${device.label} v${device.display_version || "latest"}.`);
    }
    renderMode();
  });
  elements.flashButton?.addEventListener("click", startFlash);
  elements.clearLog?.addEventListener("click", () => {
    if (elements.log) elements.log.replaceChildren();
    appendLog("Flash log cleared.", "debug");
  });

  renderMode();
  setProgress(0, "Loading firmware catalog");
  loadLatestCatalog();
}
