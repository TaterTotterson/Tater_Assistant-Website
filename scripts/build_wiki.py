from __future__ import annotations

import ast
import html
import json
import os
import re
import textwrap
from pathlib import Path
from typing import Any

from mirror_latest_firmware import mirror_latest_firmware


SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent


def resolve_path(env_name: str, *candidates: Path) -> Path:
    override = str(os.getenv(env_name, "") or "").strip()
    if override:
        return Path(override).expanduser().resolve()

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    return candidates[0].resolve()


SITE_ROOT = resolve_path("TATER_WIKI_SITE_DIR", BASE_DIR / "public_html", BASE_DIR)
TATER_DIR = resolve_path("TATER_WIKI_TATER_DIR", SCRIPT_DIR / "Tater", BASE_DIR / "Tater")
TATER_SHOP_DIR = resolve_path("TATER_WIKI_TATER_SHOP_DIR", SCRIPT_DIR / "Tater_Shop", BASE_DIR / "Tater_Shop")
TATER_INTEGRATIONS_DIR = resolve_path(
    "TATER_WIKI_TATER_INTEGRATIONS_DIR",
    SCRIPT_DIR / "Tater_Integrations",
    BASE_DIR / "Tater_Integrations",
    BASE_DIR.parent / "Tater_Integrations",
)
TATER_SHOP_MANIFEST = TATER_SHOP_DIR / "manifest.json"
TATER_INTEGRATIONS_MANIFEST = TATER_INTEGRATIONS_DIR / "manifest.json"
TATER_README = TATER_DIR / "README.md"
LEGACY_MUSIC_PROVIDER_PLUGIN_IDS = {"music_assistant", "roon_music"}

DEFAULT_INSTALL_README_NOTE = (
    "Tater currently recommends using gemma-4-26b-a4b (disable thinking), "
    "qwen/qwen3.5-35b-a3b (disable thinking), qwen3-coder-next, qwen3-next-80b, "
    "or gpt-oss-120b (disable thinking)."
)

CERBERUS_SOURCE = resolve_path(
    "TATER_WIKI_HYDRA_SOURCE",
    TATER_DIR / "hydra" / "__init__.py",
    TATER_DIR / "cerberus" / "__init__.py",
)
TOOL_RUNTIME_SOURCE = TATER_DIR / "tool_runtime.py"
SPUDEX_TOOLS_SOURCE = TATER_DIR / "spudex" / "hydra_tools.py"
SPUDEX_SETTINGS_SOURCE = TATER_DIR / "spudex" / "settings.py"
PLUGIN_DIR = resolve_path("TATER_WIKI_VERBA_DIR", TATER_DIR / "verba")

REMOVED_PORTAL_TAGS = {"homeassistant"}


def clean_platforms(value: Any) -> list[str]:
    platforms: list[str] = []
    seen: set[str] = set()
    for item in value or []:
        token = str(item).strip().lower()
        if not token or token in REMOVED_PORTAL_TAGS or token in seen:
            continue
        platforms.append(token)
        seen.add(token)
    return platforms

MACOS_MENU_COMPANION = {
    "title": "Tater Menu (macOS app)",
    "summary": "Lightweight menu-bar app that connects to Tater's built-in macOS routes for chat, quick actions, clipboard workflows, screen captures, and attachment handling.",
    "chips": ["Status bar app", "Main Tater port", "Quick actions"],
    "details": [
        "Install with python3.11 -m pip install -e . inside the Tater-MacOS repo, then run python3.11 tater_menu.py.",
        "It can also run in the background with python3.11 tater_menu.py --background and stays as a menu-bar-only app.",
        "Set Server URL to the main Tater URL, for example http://127.0.0.1:8501, plus optional API key/Auth Token and Quick Action Plugin from the app Settings menu.",
        "The app uses /macos/... routes mounted inside Tater instead of a separate desktop bridge port.",
        "The local config is stored at ~/Library/Application Support/TaterMenu/config.json.",
    ],
    "links": [
        {
            "label": "Tater-MacOS Repo",
            "href": "https://github.com/TaterTotterson/Tater-MacOS",
        },
    ],
}

MACOS_APP_GUIDES = [
    {
        "title": "First connection",
        "summary": "Point the app at the main Tater URL and verify bootstrap and polling are healthy.",
        "chips": ["Server URL", "Auth token", "Bootstrap"],
        "details": [
            "Default Tater URL is http://127.0.0.1:8501, but the app can target any reachable Tater host.",
            "If API auth is enabled in macOS portal settings, the app must send the same API key in X-Tater-Token.",
            "The app bootstraps assistant identity and recent history from /macos/bootstrap before normal chat usage.",
        ],
    },
    {
        "title": "Quick actions",
        "summary": "Clipboard and screen presets call the plugin endpoint first, then fall back to chat when needed.",
        "chips": ["/macos/plugin", "/macos/chat", "Plugin fallback"],
        "details": [
            "Quick actions are sent to /macos/plugin with a configured plugin name, defaulting to macos_quick_action.",
            "If plugin handling fails or is unavailable, the app can fall back to /macos/chat for normal assistant handling.",
            "This keeps menu actions fast while still allowing broader Hydra-driven behavior when needed.",
        ],
    },
    {
        "title": "Permissions",
        "summary": "Screen and rewrite flows depend on standard macOS privacy permissions.",
        "chips": ["Screen Recording", "Accessibility", "Apple Events"],
        "details": [
            "Screen capture tools require macOS Screen Recording permission for the Python process or packaged app.",
            "Rewrite selected text relies on Accessibility permission because it drives keystrokes with AppleScript.",
            "Frontmost-app context and rewrite flows can also require Apple Events access depending on target apps.",
        ],
    },
    {
        "title": "Notifications and attachments",
        "summary": "The app long-polls notifications and can download or auto-open returned attachments.",
        "chips": ["/macos/notifications/next", "Assets", "Downloads"],
        "details": [
            "The client polls /macos/notifications/next for queued notices, including tool_wait status updates.",
            "Returned artifacts are exposed through /macos/asset/{asset_id} download URLs scoped to the active device or session.",
            "Image attachments from direct actions can be opened automatically, while other files are saved in app-support downloads.",
        ],
    },
]

KERNEL_TOOL_OVERRIDES = {
    "search_web": {
        "purpose": "Search the public web through any enabled web-search integration, including SearXNG, Brave Search, Google Custom Search, or Serper.",
        "usage": """{
  "function": "search_web",
  "arguments": {
    "query": "latest Home Assistant release notes",
    "num_results": 5,
    "site": "home-assistant.io"
  }
}""",
    },
}

INTEGRATION_DOC_OVERRIDES = {
    "aladdin": {
        "category": "Access",
        "capabilities": ["garage_door", "garage", "entry_sensor", "open_close", "door"],
        "summary": "Exposes Genie/Aladdin garage doors as generic open/close devices.",
        "notes": [
            "Useful to Awareness Core and other device-aware flows without adding Aladdin-specific code to those cores.",
            "Disabled installs do not import or log in to Aladdin.",
        ],
    },
    "brave_search": {
        "category": "Web search",
        "capabilities": ["web_search"],
        "summary": "Adds Brave Search as one selectable provider for the search_web kernel tool.",
        "notes": [
            "Enable it when you want Brave's API results instead of or alongside another provider.",
            "Providers with the same order are tried by stable provider name/id order.",
        ],
    },
    "google_search": {
        "category": "Web search",
        "capabilities": ["web_search"],
        "summary": "Adds Google Custom Search as a modular search provider.",
        "notes": [
            "Requires both a Google API key and Programmable Search Engine CX value.",
            "Existing legacy Google search settings can still be migrated by Tater.",
        ],
    },
    "homeassistant": {
        "category": "Smart home",
        "capabilities": ["light", "switch", "plug", "fan", "sensor", "garage_door", "entry_sensor", "lock", "cover", "climate", "camera", "media_player"],
        "summary": "Imports Home Assistant devices, rooms, actions, media players, cameras, and sensors into Tater's shared integration catalog.",
        "notes": [
            "Home Assistant is now optional; Tater can boot and run without this module installed.",
            "Device Control, the Devices browser, room organization, Automation Core, Awareness Core, and other consumers use the same normalized metadata instead of Home Assistant-specific tool paths.",
            "The current integration refreshes category metadata for lights, switches, plugs, fans, locks, covers, climate, cameras, media players, and common sensor types.",
        ],
    },
    "homekit": {
        "category": "Climate",
        "capabilities": ["thermostat", "climate", "hvac", "temperature", "humidity"],
        "summary": "Pairs Ecobee thermostats through HomeKit and exposes thermostats plus remote sensors.",
        "notes": [
            "The runtime owner maps Ecobee HomeKit devices under the HomeKit integration.",
            "Environment Core can use the exposed temperature and humidity devices once enabled.",
        ],
    },
    "hue": {
        "category": "Lighting",
        "capabilities": ["light", "switch", "sensor", "button", "motion"],
        "summary": "Pairs a Philips Hue Bridge and exposes lights, switches, and Hue resources through generic device capabilities.",
        "notes": [
            "Bridge pairing and app-key storage stay inside the integration.",
            "Tater cores can discover Hue lights without provider-specific core edits.",
        ],
    },
    "huggingface": {
        "category": "Models",
        "capabilities": ["model_downloads", "token_storage"],
        "summary": "Stores an optional Hugging Face token for gated models and higher-rate downloads.",
        "notes": [
            "The token can be injected into speech/model download environments when needed.",
            "No model download happens at module import time.",
        ],
    },
    "searxng_search": {
        "category": "Web search",
        "capabilities": ["web_search"],
        "summary": "Adds a self-hosted SearXNG instance as a modular search provider.",
        "notes": [
            "Best fit when operators want self-hosted search routing.",
            "Supports an optional bearer token for protected SearXNG instances.",
        ],
    },
    "serper_search": {
        "category": "Web search",
        "capabilities": ["web_search"],
        "summary": "Adds Serper's Google Search API as a modular search provider.",
        "notes": [
            "Enable it when you prefer Serper's API over direct Google Custom Search credentials.",
            "It participates in the same ordered provider discovery as the other web-search integrations.",
        ],
    },
    "sonos": {
        "category": "Audio",
        "capabilities": ["speaker", "media_player", "audio_output", "announcement_target", "play_media"],
        "summary": "Discovers Sonos speakers for announcements, room-aware Music Core playback, synchronized temporary groups, and mixed Sonos/native scenes.",
        "notes": [
            "Music Core can prefer Sonos for automatic room selection and create a temporary synchronized group for one playback session.",
            "Existing Sonos grouping, queue, and playback state are restored after temporary music scenes and Audio Clip announcements.",
            "Stereo-pair members and mixed Sonos/Tater satellite groups are normalized so users choose readable playback destinations instead of low-level member IDs.",
        ],
    },
    "roon": {
        "category": "Audio",
        "capabilities": ["speaker", "media_player", "audio_output", "roon_zone"],
        "description": "Roon Core pairing and zone transport control for installs that still need direct Roon access.",
        "summary": "Pairs with Roon for external zone discovery and control, while Music Core uses Tater Tube as the current music library and playback source.",
        "notes": [
            "Registration can continue after the initial request while the user authorizes Tater in Roon.",
            "Roon zones are not used as Music Core stream targets; Tater Tube handles the current music catalog and playback flow.",
            "Keep Roon configured only when you need direct external zone control outside the Tater Tube Music Core path.",
        ],
    },
    "shelly": {
        "category": "Smart home",
        "capabilities": ["light", "switch", "plug", "cover", "sensor", "temperature", "humidity", "illuminance", "energy"],
        "summary": "Discovers Shelly devices and exposes controls, covers, sensor readings, and power data through Tater's shared device catalog.",
        "notes": [
            "Shelly devices can be renamed, assigned to rooms, given Tater aliases, and controlled through the same Device Control Verba as other integrations.",
            "Read-only environment and energy measurements remain available to status Verbas and device-aware cores.",
        ],
    },
    "unifi_network": {
        "category": "Network",
        "capabilities": ["network_device", "client", "presence", "connectivity"],
        "summary": "Exposes UniFi Network clients and infrastructure devices for inventory and presence-aware flows.",
        "notes": [
            "Device and client inventory becomes available through generic integration device catalogs.",
            "Presence-style workflows no longer need UniFi-specific code in every consumer.",
        ],
    },
    "unifi_protect": {
        "category": "Security",
        "capabilities": ["camera", "snapshot", "motion", "doorbell", "entry_sensor", "speaker", "announcement_target"],
        "summary": "Exposes UniFi Protect cameras, sensors, and direct speaker announcement targets.",
        "notes": [
            "Awareness Core can build camera and sensor rule options from generic camera, motion, doorbell, and entry-sensor capabilities.",
            "Snapshot actions are exposed through the shared device-action hook.",
        ],
    },
    "weather_api": {
        "category": "Weather",
        "capabilities": ["weather", "forecast", "temperature", "humidity"],
        "summary": "Stores WeatherAPI.com credentials and defaults for weather forecast tools.",
        "notes": [
            "Weather providers stay optional and dormant until enabled.",
            "Forecast flows can use this integration without bundling WeatherAPI credentials into Tater itself.",
        ],
    },
}

WEB_SEARCH_GUIDES = [
    {
        "title": "Pick a provider",
        "summary": "The search_web kernel tool now discovers enabled web-search integrations.",
        "chips": ["SearXNG", "Brave Search", "Google", "Serper"],
        "details": [
            "Open Settings -> Integrations, download the provider you want, then enable it from Manage.",
            "Tater currently ships downloadable providers for SearXNG, Brave Search, Google Custom Search, and Serper.",
            "You can enable more than one provider; Tater tries enabled web_search integrations in configured order.",
        ],
        "links": [
            {
                "label": "Tater Integrations Repo",
                "href": "https://github.com/TaterTotterson/Tater_Integrations",
            },
        ],
    },
    {
        "title": "Provider settings",
        "summary": "Each provider owns its own settings and test action.",
        "chips": ["Settings -> Integrations", "Setup", "Test"],
        "details": [
            "SearXNG needs the instance URL and optional bearer token.",
            "Brave Search and Serper need their API keys.",
            "Google Custom Search needs both a Google API key and Programmable Search Engine CX value.",
        ],
        "links": [
            {
                "label": "Custom Search JSON API Docs",
                "href": "https://developers.google.com/custom-search/v1/overview",
            },
        ],
    },
    {
        "title": "How Tater chooses",
        "summary": "Search providers advertise the shared web_search capability.",
        "chips": ["Capability discovery", "Provider order", "Fallback"],
        "details": [
            "search_web asks the integration registry for enabled providers with the web_search capability.",
            "Providers are sorted by order, then stable provider name/id, so equal orders are deterministic.",
            "If a provider is not configured or fails, Tater can continue to the next enabled provider.",
        ],
        "links": [],
    },
    {
        "title": "What the kernel tool supports",
        "summary": "The search_web input shape stays the same even when providers change.",
        "chips": ["query", "site", "country", "language"],
        "details": [
            "query is required, while num_results, start, site, safe, country, and language are optional.",
            "site narrows results to one domain when the provider supports it.",
            "Hydra can keep using search_web without caring which provider integration is currently enabled.",
        ],
        "links": [],
    },
]

PLUGIN_OVERRIDES = {
    "events_query_brief": {
        "when_to_use": "Use this for short event rollups on dashboards, automations, and notifications when you want brief plain-text output instead of a long narrative.",
        "how_to_use": "Run it from an Awareness Core brief rule, choose a timeframe and optional area/query, then either set INPUT_TEXT_ENTITY once in WebUI or pass input_text_entity in the action to write straight into a Home Assistant helper.",
        "usage_example": """{
  "function": "events_query_brief",
  "arguments": {
    "timeframe": "today",
    "area": "front yard",
    "query": "brief summary",
    "input_text_entity": "input_text.event_brief"
  }
}""",
        "guides": [
            {
                "title": "Best fit",
                "summary": "This is one of the three automation brief plugins and is tuned for short event summaries.",
                "chips": ["Auto briefs", "Dashboard text", "Events"],
                "details": [
                    "Use it when cameras, doorbells, or sensors have already stored events through the automations event API.",
                    "The result stays short enough for dashboards and helper fields instead of producing a verbose explanation.",
                    "It is a good choice for daily summaries, front-yard activity recaps, and quick notification text.",
                ],
            },
            {
                "title": "Helper storage",
                "summary": "The plugin can write the summary directly to a Home Assistant input_text helper.",
                "chips": ["INPUT_TEXT_ENTITY", "input_text_entity", "No follow-up action"],
                "details": [
                    "Set INPUT_TEXT_ENTITY in WebUI to define a default helper target once.",
                    "Pass input_text_entity in the automation action when you want to override the default target.",
                    "No extra Home Assistant templating step is required after the plugin runs.",
                ],
            },
        ],
    },
    "camera_event": {
        "when_to_use": "Use this when a camera, motion sensor, door, or occupancy trigger should create a durable event that Tater can remember and answer questions about later.",
        "how_to_use": "In Home Assistant automations, use the native Camera Event action from the Tater Automations integration, then choose the Area dropdown and Camera entity selector. You usually do not need to type a raw tool name or raw JSON arguments.",
        "usage_example": """{
  "function": "camera_event",
  "arguments": {
    "area": "front yard",
    "camera": "camera.front_door_high"
  }
}""",
        "guides": [
            {
                "title": "UI-only action flow",
                "summary": "The current Home Assistant integration exposes Camera Event as a native action, not just a generic tool call.",
                "chips": ["Camera Event", "Dropdowns", "No YAML"],
                "details": [
                    "In Home Assistant, add an action and choose Tater Automations -> Camera Event.",
                    "The action now exposes a clean Area dropdown and Camera entity selector instead of requiring a typed tool name and raw arguments object.",
                    "That makes the common camera-event setup fully UI-driven.",
                ],
            },
            {
                "title": "What it stores",
                "summary": "Each run captures a snapshot, generates a short vision summary, and stores the result in Tater's event timeline.",
                "chips": ["Event timeline", "Vision summary", "Later queries"],
                "details": [
                    "When the automation fires, Tater captures a Home Assistant camera snapshot, describes it, and posts the event into the automations event API.",
                    "The area is normalized into a source key such as front_yard or front_door so later event queries stay grouped consistently.",
                    "That stored event can later feed direct questions in Tater or brief plugins such as Events Query Brief.",
                ],
            },
            {
                "title": "Common setup",
                "summary": "The most common setup is a motion or door trigger plus the native Camera Event action.",
                "chips": ["Motion trigger", "Door trigger", "Simple setup"],
                "details": [
                    "Create any trigger you want in Home Assistant, such as motion detected or a door opening.",
                    "Set Area to a human-friendly location like front yard or front door, then select the matching camera entity.",
                    "Tater handles the snapshot analysis, event logging, and optional notification behavior after that.",
                ],
            },
        ],
    },
    "doorbell_alert": {
        "description": "Automation-first doorbell workflow that captures a snapshot, generates a short vision-based description, speaks it over configured media players, and can optionally store an event or send Home Assistant notifications.",
        "when_to_use": "Use this for doorbell presses, front-door motion, or porch triggers when you want a spoken alert across the house and optional event storage for later questions.",
        "how_to_use": "In Home Assistant automations, use the native Doorbell Alert action from the Tater Automations integration and leave its fields empty. The normal path is zero-argument execution using defaults configured once in Tater WebUI.",
        "usage_example": """{
  "function": "doorbell_alert",
  "arguments": {}
}""",
        "guides": [
            {
                "title": "UI-only default flow",
                "summary": "The current Home Assistant integration exposes Doorbell Alert as a native no-field action.",
                "chips": ["Doorbell Alert", "No fields", "No YAML"],
                "details": [
                    "In Home Assistant, add an action and choose Tater Automations -> Doorbell Alert.",
                    "That action intentionally exposes no required fields because the plugin is designed to run from defaults already configured in Tater WebUI.",
                    "This keeps the common doorbell setup simple: trigger it and let Tater handle the rest.",
                ],
            },
            {
                "title": "What it does",
                "summary": "Each run captures the configured door camera, creates a short vision description, and speaks it over TTS players.",
                "chips": ["Snapshot", "Vision brief", "TTS"],
                "details": [
                    "When triggered, Tater fetches the latest snapshot from the configured Home Assistant camera and asks the vision model for one short spoken sentence.",
                    "That sentence is played through the configured TTS entity and one or more configured media players.",
                    "If the snapshot or vision step fails, the plugin falls back to a generic spoken line instead of hard-failing silently.",
                ],
            },
            {
                "title": "Events and notifications",
                "summary": "Notifications and durable events are optional and controlled by plugin settings or advanced overrides.",
                "chips": ["Optional notifications", "Per-area events", "Advanced overrides"],
                "details": [
                    "If notifications are enabled, the plugin can send Home Assistant API notifications, persistent notifications, and optional mobile-device notifications.",
                    "When it stores an event, the area label is normalized into a source key such as front_door so later event queries can group door activity consistently.",
                    "Advanced users can still override camera, players, area, notification flags, or device_service through the legacy generic tool path, but the default no-argument action is the recommended flow.",
                ],
            },
        ],
    },
    "mister_remote": {
        "description": "Control your MiSTer FPGA through the MiSTer Remote API with one natural-language request: launch games, check what is playing, return to the menu, or capture screenshots.",
        "when_to_use": "Use this when you want Tater to browse or control a MiSTer setup from chat, voice, or the WebUI without dealing with the MiSTer Remote API directly.",
        "how_to_use": "Set MISTER_HOST and MISTER_PORT in plugin settings, make sure MiSTer Remote and Search are installed on the MiSTer, then send one natural-language request in query such as play super mario on super nintendo or what is playing on mister.",
        "usage_example": """{
  "function": "mister_remote",
  "arguments": {
    "query": "play super mario on super nintendo"
  }
}""",
        "guides": [
            {
                "title": "Quick setup on MiSTer",
                "summary": "MiSTer Remote depends on the mrext Remote and Search tools running on the MiSTer box.",
                "chips": ["mrext", "Port 8182", "Search index"],
                "details": [
                    "Install the MiSTer Remote and Search scripts from the mrext release bundle and place them under /media/fat/Scripts on the MiSTer.",
                    "Run Search at least once so the game database exists before Tater tries to launch titles by search.",
                    "Start remote.sh and confirm the Remote UI is reachable from the Tater machine, usually at http://YOUR_MISTER_IP:8182.",
                ],
            },
            {
                "title": "Tater plugin settings",
                "summary": "Tater only needs the MiSTer host and port, but the Remote index must already be healthy.",
                "chips": ["MISTER_HOST", "MISTER_PORT", "Reachability"],
                "details": [
                    "Set MISTER_HOST to the MiSTer Remote host URL and MISTER_PORT to the API port if you changed it from 8182.",
                    "If MiSTer Remote can see your library and search it, Tater can search and launch it too, including CIFS-backed libraries that are already indexed.",
                    "If launch lookups fail or the library seems empty, rebuild the MiSTer Search index first before troubleshooting Tater.",
                ],
            },
            {
                "title": "Supported commands",
                "summary": "The plugin maps natural language into four main MiSTer actions.",
                "chips": ["play", "now_playing", "go_to_menu", "screenshot_take"],
                "details": [
                    "play launches the closest matching game on the chosen or inferred system, for example play mario on snes.",
                    "now_playing reports the current game and system, go_to_menu returns to the MiSTer menu, and screenshot_take captures a screenshot artifact.",
                    "The screenshot action returns image payload data when available so the current portal can display or attach the screenshot cleanly.",
                ],
            },
            {
                "title": "Troubleshooting",
                "summary": "Most setup failures come down to reachability or a missing search database.",
                "chips": ["gamesdb", "No systems", "Reindex"],
                "details": [
                    "If you see behavior like gamesdb does not exist or no systems are found, run Search once and refresh the MiSTer Remote index.",
                    "If Tater cannot talk to MiSTer at all, double-check MISTER_HOST and MISTER_PORT in plugin settings and verify the Remote web UI is reachable from the Tater box.",
                    "Natural-language launch requests work best after the Search index is current, because Tater relies on MiSTer Remote search results to pick the right game path.",
                ],
            },
        ],
    },
    "weather_brief": {
        "when_to_use": "Use this for short weather recaps in dashboards, notifications, and scheduled automations when you want a concise summary of recent conditions.",
        "how_to_use": "Run it from an Awareness Core brief rule, pick the recent hour window from the dropdown, optionally add a short query, and write the result into an input_text helper with INPUT_TEXT_ENTITY or input_text_entity.",
        "usage_example": """{
  "function": "weather_brief",
  "arguments": {
    "hours": 12,
    "query": "brief weather summary",
    "input_text_entity": "input_text.weather_brief"
  }
}""",
        "guides": [
            {
                "title": "Brief output by design",
                "summary": "Weather Brief is tuned for automation-safe text, not long-form forecasts.",
                "chips": ["Auto briefs", "Weather", "Short output"],
                "details": [
                    "It summarizes recent weather conditions over a selected hour window using Home Assistant weather sensor history.",
                    "The output is intentionally compact so it can land in helpers, dashboards, or notifications cleanly.",
                    "Home Assistant handles the state while Tater only produces the summary text.",
                ],
            },
            {
                "title": "Helper target pattern",
                "summary": "Use an input_text helper when you want the summary to persist on a dashboard or be reused elsewhere.",
                "chips": ["input_text", "Reusable state", "No YAML"],
                "details": [
                    "Set INPUT_TEXT_ENTITY in plugin settings for the default destination.",
                    "Pass input_text_entity in an individual automation to override the destination for one run.",
                    "This keeps automations simple because the plugin writes the final text directly to Home Assistant.",
                ],
            },
        ],
    },
    "voicepe_remote_timer": {
        "guides": [
            {
                "title": "Flash the right Voice PE firmware first",
                "summary": "This plugin expects a Voice PE build that exposes the remote timer entities in Home Assistant.",
                "chips": ["Voice PE", "Tater Voice", "Required firmware"],
                "details": [
                    "Before using this plugin, flash your Voice PE with the Tater timer configuration so the expected timer entities exist in Home Assistant.",
                    "The plugin works against entity patterns such as number.voicepe_*_remote_timer_seconds, button.voicepe_*_remote_timer_start, button.voicepe_*_remote_timer_cancel, sensor.voicepe_*_remote_timer_remaining_seconds, and binary_sensor.voicepe_*_remote_timer_running.",
                    "If those entities do not exist yet, the plugin will not be able to infer or control the device timer correctly.",
                ],
                "links": [
                    {
                        "label": "Voice PE Timer YAML",
                        "href": "https://github.com/TaterTotterson/microWakeWords/raw/refs/heads/main/voicePE-TaterTimer.yaml",
                    },
                ],
            },
            {
                "title": "Entity setup",
                "summary": "You can let the plugin infer the device entities from context, or set them explicitly in Tater.",
                "chips": ["Inference", "Entity IDs", "Home Assistant"],
                "details": [
                    "If your Voice PE entity IDs follow the normal naming pattern, the plugin can infer them from the speaking device name or an optional VOICEPE_ENTITY_PREFIX.",
                    "If your setup is custom, fill in TIMER_SECONDS_ENTITY, START_BUTTON_ENTITY, CANCEL_BUTTON_ENTITY, REMAINING_SENSOR_ENTITY, and RUNNING_SENSOR_ENTITY in plugin settings.",
                    "The plugin also respects MAX_SECONDS so unusually large timer requests can be clamped safely.",
                ],
                "links": [],
            },
        ],
    },
    "zen_greeting": {
        "when_to_use": "Use this for a short daily zen message, calm greeting, or dashboard-safe motivational line inside automation flows.",
        "how_to_use": "Run it from an Awareness Core brief rule, choose tone and include_date options from the Home Assistant action UI, and store the result in an input_text helper when you want the message to persist on a dashboard.",
        "usage_example": """{
  "function": "zen_greeting",
  "arguments": {
    "include_date": false,
    "tone": "zen",
    "prompt_hint": "focus on patience and gratitude",
    "input_text_entity": "input_text.zen_message"
  }
}""",
        "guides": [
            {
                "title": "Daily zen brief",
                "summary": "Zen Greeting is the third brief-style automation plugin and is designed for a short message of the day.",
                "chips": ["Auto briefs", "Dashboard text", "Daily message"],
                "details": [
                    "It produces a very short calming line instead of a conversational answer.",
                    "This makes it useful for morning dashboards, routine announcements, and lightweight daily automations.",
                    "The plugin also enforces a max character limit so the result stays safe for Home Assistant text helpers.",
                ],
            },
            {
                "title": "Dashboard storage",
                "summary": "Store the zen message in an input_text helper when you want the latest message visible on a dashboard.",
                "chips": ["input_text", "Daily output", "Persistent helper"],
                "details": [
                    "Use INPUT_TEXT_ENTITY in WebUI for the default helper or input_text_entity per automation for overrides.",
                    "That keeps the automation UI simple and avoids extra scripts or templating.",
                    "A helper such as input_text.zen_message works well for markdown cards and status views.",
                ],
            },
        ],
    },
}
PORTAL_DOCS_ORDER = [
    "webui",
    "discord",
    "telegram",
    "matrix",
    "irc",
    "meshtastic",
    "moltbook",
    "homekit",
    "macos",
    "xbmc",
]

CORE_DOCS_ORDER = [
    "ai_task",
    "automation",
    "awareness",
    "environment",
    "guardian",
    "memory",
    "music",
    "personal",
    "rss",
    "tater_tube",
]

PLATFORM_DOCS = {
    "webui": {
        "label": "WebUI",
        "description": "Local Vue 3 control center for the Dashboard, private chat, Music Core, Integrations, Verbas, Portals, Cores, Spudex, Voice, System Tasks, runtime telemetry, and settings.",
        "role": "Operator console",
        "source": None,
        "plugin_surface": "webui",
        "highlights": [
            "The Dashboard, Chat, Integrations, Verba, Portals, Cores, Spudex, Settings, Music Core, and live runtime popup now use Tater's locally bundled Vue 3 and TypeScript interface.",
            "The orange-and-gray UI keeps navigation, cards, dialogs, settings forms, and responsive layouts consistent without downloading a frontend from a third party.",
            "Dashboard is the default landing view, with alphabetized masonry sections for health, environment imagery, awareness snapshots, voice satellites, Speaker ID, and Emotion ID.",
            "Live surfaces update in place without replacing the selected tab, scroll position, open dropdown, or in-progress form values.",
            "Settings -> System Tasks shows Tater-owned and Core-owned jobs with run state, last and next run times, errors, and a Run Now control.",
            "Satellite inventory, integration devices, Dashboard briefs, hardware telemetry, loaded models, and context estimates rebuild in the background and on relevant change events.",
            "The installed Tater version appears at the bottom of the left menu and comes from the packaged build metadata on macOS, Docker, and local command-line installs.",
            "Adds the Spudex workbench for terminal-backed assistant sessions, direct Spudex chat, manual command runs, live logs, process control, and policy settings.",
            "First-run Redis setup is handled in-WebUI via popup and stored under .runtime so connection config persists.",
            "Redis settings include connection test/save plus live encryption and decryption controls for in-place data protection.",
            "Hydra settings cover base server pools, optional Beast Mode role routing, and runtime tuning values.",
            "The top runtime pill opens live model, Hydra, LLM, vision, context, Apple GPU/unified-memory, and unload controls without blocking Model Settings initialization.",
            "Integrations now have a Store/Manage split: Store downloads optional modules, Manage enables/disables installed modules, and Setup refreshes available provider settings.",
            "The integration runtime restores missing enabled integrations at boot and keeps disabled integrations unimported.",
            "Web search providers are modular integrations, with SearXNG, Brave Search, Google Custom Search, and Serper available from the integration catalog.",
            "Hugging Face token storage moved into the modular integration catalog so automatic model downloads can use authenticated Hub requests when enabled.",
            "Settings -> People creates master users that can link portal accounts, WebUI identities, and Tater Voice identities into one person record.",
            "WebUI password login can be enabled from Settings -> General and uses cookie-backed sessions.",
        ],
        "guides_eyebrow": "Identity layer",
        "guides_title": "People turns scattered accounts and devices into one known user.",
        "guides_intro": "The People panel is the human identity layer Tater uses when one person appears through multiple portals, devices, or voice identities.",
        "guides": [
            {
                "title": "Master users",
                "summary": "Create one master user per real person, then link all of their known identities to that record.",
                "chips": ["Settings -> People", "Master user", "Identity links"],
                "details": [
                    "A master user can represent the same person across WebUI, Discord, Telegram, Matrix, IRC, HomeKit, macOS, XBMC, Meshtastic, and Tater Voice identities.",
                    "Linked identities let Tater resolve a request origin into one person_id and person_name instead of treating every portal account as a separate user.",
                    "Speaker ID aliases from Tater Voice turns can also be linked, so a recognized voice can map back to the same master user as that person's chat accounts.",
                ],
            },
            {
                "title": "Per-person instructions",
                "summary": "Each master user can carry trusted response instructions that only apply when that user is resolved.",
                "chips": ["Instructions", "Prompt context", "Scoped"],
                "details": [
                    "Per-person instructions are useful for preferred names, tone preferences, accessibility needs, household roles, or other user-specific response style rules.",
                    "Tater injects those instructions only for the current resolved user and tells Hydra not to apply them to other people mentioned in the conversation.",
                    "These instructions are scoped under system and safety rules, so they personalize responses without overriding higher-priority behavior.",
                ],
            },
            {
                "title": "Discovered identities",
                "summary": "The People panel can surface identities Tater has seen but not yet linked.",
                "chips": ["Discovery", "Portals", "Speaker ID"],
                "details": [
                    "Tater discovers candidate identities from recent WebUI users, portal history, Memory Core identity docs, and Tater Voice Speaker ID aliases.",
                    "Operators can attach a discovered identity to an existing master user or create a new master user first.",
                    "Manual links keep matching explicit, which is safer than guessing when multiple people share devices or rooms.",
                ],
            },
            {
                "title": "Spudex workbench",
                "summary": "Run terminal-backed tasks from a dedicated WebUI tab while keeping sessions, logs, process controls, and policy settings visible.",
                "chips": ["Spudex", "Terminal", "Agent Lab"],
                "details": [
                    "The Spudex tab includes a console-style chat where an assistant can run commands, write files, inspect output, search when needed, and continue until the terminal task is complete.",
                    "Manual sessions let operators run one command directly, keep background processes visible, and stop model-started sessions from the UI.",
                    "Settings cover enabled platforms, the working folder under Agent Lab, approval behavior, command timeout, output caps, max task steps, and policy toggles for network, installs, shells, containers, host/admin commands, and other command classes.",
                ],
            },
        ],
        "apis": [
            {
                "method": "GET",
                "path": "/api/settings/people",
                "summary": "Load People settings, master users, and discovered identity rows.",
                "details": "Returns summary metrics, saved people, linked aliases, and discovered identities from WebUI, portals, Memory Core, and Tater Voice Speaker ID.",
            },
            {
                "method": "POST",
                "path": "/api/settings/people/action",
                "summary": "Create, edit, delete, link, and unlink People records.",
                "details": "Supports people_create, people_save, people_delete, people_alias_attach, and people_alias_detach actions for the Settings -> People panel.",
            },
            {
                "method": "GET",
                "path": "/api/spudex",
                "summary": "Load Spudex settings, sessions, logs, process state, and platform options.",
                "details": "Feeds the Spudex tab with current settings, active sessions, recent terminal history, tracked processes, and available platform toggles.",
            },
            {
                "method": "POST",
                "path": "/api/spudex/chat",
                "summary": "Run a direct Spudex chat turn.",
                "details": "Bypasses Hydra and sends the request into the Spudex console loop, where the model can run commands, write files, search, verify results, and report back in the same session.",
            },
            {
                "method": "POST",
                "path": "/api/spudex/run",
                "summary": "Start a manual Spudex command session.",
                "details": "Runs a single command from the configured Agent Lab working folder, optionally in the background, with live log streaming and stop controls.",
            },
        ],
    },
    "discord": {
        "label": "Discord",
        "description": "Full-featured Discord portal with rich interactions, media output, background jobs, trusted current-speaker identity, and Verba-backed actions.",
        "role": "Chat endpoint",
        "source": TATER_SHOP_DIR / "portals" / "discord_portal.py",
        "plugin_surface": "discord",
        "highlights": [
            "Supports channel allowlists, DMs, queued notifications, attachments, and slash-style server tooling.",
            "Runs Hydra turns per conversation so multi-step requests stay grounded.",
            "The latest Discord message is authoritative for speaker, Person, room, and admin permissions; names or tool access from older shared-channel history cannot carry into a new user's turn.",
            "Pairs well with admin-only Verbas and server management workflows.",
        ],
    },
    "telegram": {
        "label": "Telegram",
        "description": "Telegram bot integration with allowlists, DM restrictions, queued notifications, media delivery, and Verba execution.",
        "role": "Chat endpoint",
        "source": TATER_SHOP_DIR / "portals" / "telegram_portal.py",
        "plugin_surface": "telegram",
        "highlights": [
            "Supports rich formatting, inline media delivery, and per-chat restrictions.",
            "Good fit for direct bot conversations and push-style alert delivery.",
            "Uses the same Verba runtime model as the rest of Tater's chat surfaces.",
        ],
    },
    "matrix": {
        "label": "Matrix",
        "description": "Federated Matrix client with encryption support, Markdown rendering, and full Verba compatibility.",
        "role": "Chat endpoint",
        "source": TATER_SHOP_DIR / "portals" / "matrix_portal.py",
        "plugin_surface": "matrix",
        "highlights": [
            "Brings Tater to federated chat networks like Element and Cinny.",
            "Can operate with end-to-end encryption and persistent Matrix device state.",
            "Supports mention triggers, room response modes, and Verba-backed actions.",
        ],
    },
    "irc": {
        "label": "IRC",
        "description": "Lightweight IRC bot that responds to mentions and runs compatible Verbas.",
        "role": "Chat endpoint",
        "source": TATER_SHOP_DIR / "portals" / "irc_portal.py",
        "plugin_surface": "irc",
        "highlights": [
            "Simple low-overhead deployment for classic chat rooms and ZNC-style setups.",
            "Supports admin-user gating and Verba execution on mention.",
            "Keeps the interaction model intentionally lean and plain-text friendly.",
        ],
    },
    "meshtastic": {
        "label": "Meshtastic",
        "description": "Off-grid Meshtastic portal that connects Tater to direct and channel conversations through the local Tater Meshtastic Bridge.",
        "role": "Mesh radio endpoint",
        "source": TATER_SHOP_DIR / "portals" / "meshtastic_portal.py",
        "plugin_surface": "meshtastic",
        "highlights": [
            "Connects through the local Tater Meshtastic Bridge instead of requiring radio hardware inside the Tater process.",
            "Supports direct messages, selected mesh channels, mention-only or broader response policies, and per-node conversation sessions.",
            "Splits longer replies into compact numbered radio messages with configurable length and chunk limits.",
            "Rejects stale bridge backlog, remembers processed messages, and can resume either from now or from the last stored event.",
            "Uses the same current-speaker identity boundary and admin gating as Tater's other shared chat portals.",
        ],
    },
    "moltbook": {
        "label": "Moltbook",
        "description": "Social/research community portal that keeps Tater active on Moltbook with a structured, safety-first loop.",
        "role": "Social research endpoint",
        "source": TATER_SHOP_DIR / "portals" / "moltbook_portal.py",
        "plugin_surface": "moltbook",
        "highlights": [
            "Runs a /home-first check-in loop so replies and community activity are prioritized before new posting.",
            "Uses strict API-key safety rules: auth is only sent to https://www.moltbook.com/api/v1/* with redirect blocking and host checks.",
            "Handles challenge-based verification by solving and submitting /api/v1/verify only when verification is required by write responses.",
            "Tracks anti-repeat memory, agent radar, idea seeds, and experiment/discovery signals in Redis to stay present without becoming spammy.",
        ],
        "guides": [
            {
                "title": "Runtime flow",
                "summary": "Each cycle begins with account health and GET /api/v1/home, then processes replies before considering posting.",
                "chips": ["/home first", "Replies before posts", "Rate-aware"],
                "details": [
                    "The portal starts by confirming auth and claim status, then pulls /home as the primary decision surface.",
                    "Activity on Tater's own posts and outbound-thread replies are handled before broad feed exploration.",
                    "Posting is gated behind novelty checks, rate limits, cooldowns, and optional discovery/seed thresholds.",
                ],
            },
            {
                "title": "Security model",
                "summary": "Moltbook content is treated as untrusted input and cannot invoke general Verba tools.",
                "chips": ["www-only", "API key isolation", "Tool isolation"],
                "details": [
                    "Auth headers are never sent off-domain and are restricted to Moltbook API routes with explicit scheme/host/path checks.",
                    "The LLM behavior for this portal only gets one tool in-context: kernel.web_search.",
                    "Scheduling, memory updates, cooldown enforcement, and write decisions stay in backend portal logic.",
                ],
            },
        ],
        "apis": [
            {
                "method": "GET",
                "path": "/api/v1/home",
                "summary": "Primary dashboard endpoint used at the start of every check-in.",
                "details": "Returns account summary, activity on your posts, followed-account previews, suggested actions, and quick links in one call.",
            },
            {
                "method": "POST",
                "path": "/api/v1/agents/register",
                "summary": "Creates a Moltbook agent and returns API key + claim data.",
                "details": "The portal saves api_key and claim_url immediately, then waits for claim completion before treating the account as fully active.",
            },
            {
                "method": "POST",
                "path": "/api/v1/verify",
                "summary": "Completes challenge verification for posts/comments/submolts when required.",
                "details": "Used only when create responses include verification_required and a verification object with a challenge/code.",
            },
            {
                "method": "GET",
                "path": "/api/v1/feed",
                "summary": "Fetches personalized feed content for discovery.",
                "details": "Supports all and following filters, with sort options used alongside /posts scans and semantic search.",
            },
            {
                "method": "GET",
                "path": "/api/v1/search",
                "summary": "Semantic search endpoint used for novelty checks and discovery.",
                "details": "Query results support duplicate-topic detection before posting and thread discovery for higher-value replies.",
            },
        ],
    },
    "homekit": {
        "label": "HomeKit",
        "description": "Siri and Apple Shortcuts portal for a full Siri-to-Tater round-trip, with per-device sessions, Shortcut-friendly JSON, and optional auth protection.",
        "role": "Voice endpoint",
        "source": TATER_SHOP_DIR / "portals" / "homekit_portal.py",
        "plugin_surface": "homekit",
        "highlights": [
            "Provides lightweight Siri and Apple Shortcuts routes mounted inside the main Tater app.",
            "Designed for Shortcut-driven voice loops where Siri captures speech, posts JSON to Tater, then speaks the reply back aloud.",
            "Maintains per-device conversation sessions instead of treating every request as stateless.",
            "Supports optional API key protection so Shortcuts must send X-Tater-Token when enabled.",
            "Uses the default Tater port, so no separate HomeKit service port is needed.",
            "Good fit for Apple-first households that want voice access without a full chat client.",
        ],
        "guides": [
            {
                "title": "Premade shortcut",
                "summary": "A ready-made Apple Shortcut already exists for the HomeKit portal.",
                "chips": ["Shortcut", "Siri", "Quick start"],
                "details": [
                    "You can start from the premade Ask Tater shortcut instead of building the flow by hand.",
                    "It is a good baseline even if you later customize the session_id, endpoint IP, or auth header.",
                ],
                "links": [
                    {
                        "label": "Premade Shortcut",
                        "href": "https://www.icloud.com/shortcuts/9e1c8b3bd58745c9b0c0881c81a306a4",
                    },
                ],
            },
            {
                "title": "Build the shortcut",
                "summary": "The common Shortcut flow is Dictate Text -> Get Contents of URL -> Get Dictionary Value -> Speak Text.",
                "chips": ["Dictate Text", "POST JSON", "Speak Text"],
                "details": [
                    "Create a shortcut such as Ask Tater, then add Dictate Text with stop listening set to After Pause.",
                    "Use Get Contents of URL to POST JSON to http://YOUR-TATER-IP:8501/tater-homekit/v1/message with text and session_id fields.",
                    "Extract the reply key from the JSON response, then feed it into Speak Text so Siri or a HomePod reads it back.",
                ],
            },
            {
                "title": "Session IDs and auth",
                "summary": "Each device should use its own session_id, and protected routes can require the X-Tater-Token header.",
                "chips": ["session_id", "X-Tater-Token", "Per-device memory"],
                "details": [
                    "Use a stable session_id such as iphone, ipad, or bedroom_homepod so conversations do not mix between devices.",
                    "If API auth is enabled in Tater HomeKit settings, add an X-Tater-Token header inside the shortcut request.",
                    "The portal keeps short Siri-friendly session history in Redis using the configured session TTL and history limits.",
                ],
            },
            {
                "title": "HomePod behavior",
                "summary": "HomePods can use the same shortcut flow by handing off through the iPhone that owns the shortcut.",
                "chips": ["HomePod", "Handoff", "Siri phrase"],
                "details": [
                    "After adding the shortcut to Siri, phrases like Ask Tater or Talk to Tater can trigger the round-trip hands-free.",
                    "If the shortcut lives on the iPhone, a HomePod can hand off the shortcut execution and still speak Tater's reply.",
                    "This gives Apple households a practical voice surface without needing a separate Apple-native Tater app.",
                ],
            },
        ],
        "guides_eyebrow": "Shortcut guide",
        "guides_title": "How to connect Siri and Apple Shortcuts to this portal.",
        "guides_intro": "These notes focus on the Shortcut flow, session handling, optional auth, and the Siri voice round-trip.",
        "apis": [
            {
                "method": "POST",
                "path": "/tater-homekit/v1/message",
                "summary": "Main Siri / Shortcuts message endpoint.",
                "details": "Accepts JSON with text plus an optional session_id, enforces X-Tater-Token when API auth is enabled, and returns a plain reply field sized for Siri speech.",
            },
        ],
    },
    "macos": {
        "label": "macOS",
        "description": "Native desktop portal used by the Tater Menu status-bar app for chat, quick actions, notification polling, and attachment workflows.",
        "role": "Desktop endpoint",
        "source": TATER_SHOP_DIR / "portals" / "macos_portal.py",
        "plugin_surface": "macos",
        "highlights": [
            "Mounts /macos/... routes under the main Tater WebUI/API port for the Tater Menu app.",
            "Maintains scoped session history with configurable limits and TTL so desktop context stays stable but bounded.",
            "Supports long-poll notifications plus tool_wait status handling for menu-app feedback loops.",
            "Includes asset upload and download endpoints for screen captures, clipboard artifacts, and returned files.",
            "Supports optional API key protection through the X-Tater-Token header.",
        ],
        "companions": [
            MACOS_MENU_COMPANION,
        ],
        "companions_eyebrow": "Client app",
        "companions_title": "macOS app that connects to these Tater routes.",
        "companions_intro": "The menu-bar app is the main user-facing client for this portal and handles quick actions, chat UI, and attachment flows.",
        "guides": MACOS_APP_GUIDES,
        "guides_eyebrow": "App setup",
        "guides_title": "How to run and connect the Tater Menu app.",
        "guides_intro": "These notes are based on the current Tater-MacOS app README and the active macOS routes.",
        "apis": [
            {
                "method": "GET",
                "path": "/macos/health",
                "summary": "Health check for the desktop portal.",
                "details": "Returns ok, platform=macos, and version 1.0 so clients can confirm the route is alive.",
            },
            {
                "method": "GET",
                "path": "/macos/bootstrap",
                "summary": "Bootstrap assistant identity and recent history.",
                "details": "Returns assistant identity plus recent scoped history so the menu app can initialize quickly.",
            },
            {
                "method": "GET",
                "path": "/macos/notifications/next",
                "summary": "Long-poll next queued notification item.",
                "details": "Polls scoped notification queues with optional wait_seconds and returns the next pending notification payload.",
            },
            {
                "method": "POST",
                "path": "/macos/chat",
                "summary": "Main macOS chat endpoint.",
                "details": "Accepts user_text, clipboard context, optional assets, and scope/device context, then runs a Hydra turn.",
            },
            {
                "method": "POST",
                "path": "/macos/plugin",
                "summary": "Direct plugin call path for quick actions.",
                "details": "Executes a named plugin with args for deterministic quick-action flows, then returns narrated text plus attachments/actions.",
            },
            {
                "method": "POST",
                "path": "/macos/asset",
                "summary": "Upload one client asset into scoped artifact storage.",
                "details": "Stores an incoming asset payload and returns an attachment-ready artifact reference for later use.",
            },
            {
                "method": "GET",
                "path": "/macos/asset/{asset_id}",
                "summary": "Download a scoped artifact by asset_id.",
                "details": "Returns raw file bytes for stored artifacts so the app can save or open returned attachments.",
            },
            {
                "method": "GET",
                "path": "/macos/history",
                "summary": "Fetch scoped conversation history.",
                "details": "Returns client-safe history entries for a scope or device with server-side cap enforcement.",
            },
            {
                "method": "GET",
                "path": "/macos/assistant",
                "summary": "Fetch assistant identity metadata.",
                "details": "Returns assistant display-name identity data for app UI labels and chat headers.",
            },
        ],
    },
    "esphome": {
        "label": "Tater Voice",
        "description": "Built-in room-aware voice runtime for paired Tater Native satellites, local microWakeWord, secure trainer publishing, stereo pairs, intercom, synchronized playback, prebuilt firmware updates, and persistent voice statistics.",
        "role": "Native device runtime",
        "source": None,
        "plugin_surface": "voice_core",
        "hero_eyebrow": "Tater Voice",
        "hero_panel_eyebrow": "One local voice platform",
        "hero_panel_text": "Pair a satellite, assign its room, choose a local microWakeWord model, and manage voice, firmware, stereo, playback, intercom, and diagnostics from Tater's own UI.",
        "role_eyebrow": "Why it matters",
        "role_title": "Voice that understands where it is",
        "role_text": "Every voice turn carries the speaking satellite, room, resolved Person, and trusted permissions into Tater. That same room context drives device control, music playback, follow-up listening, intercom, and reply routing.",
        "highlights_eyebrow": "Current voice stack",
        "highlights_title": "Local wake detection, room context, and synchronized sound",
        "plugin_eyebrow": "Voice-aware Verbas",
        "plugin_title": "Actions can use the room and device that heard the request",
        "settings_eyebrow": "Operator controls",
        "settings_title": "Everything lives under Settings -> Voice",
        "highlights": [
            "Tater Voice is built into the main Tater runtime and uses secure Add Satellite pairing for supported Tater Native hardware.",
            "Voice PE, Satellite1, ReSpeaker XVF3800, S3 Box, and compatible Tater Native devices keep their saved name, room, hardware family, firmware revision, and per-device settings.",
            "Wake detection runs locally on each satellite with int8 microWakeWord models. Users can choose a built-in model, the shared Tater Wake Word Catalog, or a trainer-published custom JSON package.",
            "Wake Word Trainer pairing uses a short-lived one-use code and a trainer-scoped credential; publishing a model cannot grant general Tater API access.",
            "STT Wake Verification can run Disabled, Observe, or Enabled. Results fail open on timeout and now persist in Redis with a visible 30-day period and manual reset controls.",
            "Room arbitration prevents two satellites in the same room from answering one wake while still allowing independent conversations in different rooms.",
            "Stereo Pairs have their own Voice tab. Left and right members prebuffer one source, begin from a shared timestamp, preserve calibration, and remain one reusable playback destination.",
            "Persistent native media sessions support music, synchronized multi-satellite scenes, TTS overlays, ducking, drift correction, and continued playback after a temporary reply.",
            "Intercom can target a room, satellite, stereo pair, or broad group while using the same session state, playback routing, and TTS choices as normal voice replies.",
            "The Firmware tab downloads signed prebuilt Tater Native images for OTA or Browser USB flashing; local compiling is no longer required.",
            "Browser USB recovery can erase stale safe-mode state, flash the factory image, and keep USB logs visible through the restart.",
            "S3 Box displays can show environment readings, voice and tool states, camera snapshots, doorbell notices, and targeted display cards.",
            "Speaker ID can resolve an enrolled voice to a Person record, while optional Emotion ID adds bounded tone context without changing the trusted speaker boundary.",
            "Reply playback can stay on the listening satellite, use a preferred room player, target another announcement device, or remain display-only.",
            "Satellite inventory is cached and rebuilt on connect, disconnect, or settings changes with a periodic safety refresh, so the Voice UI opens quickly.",
        ],
        "guides": [
            {
                "title": "Pair and organize satellites",
                "summary": "Add Satellite creates a short-lived pairing code, then Tater remembers the device and its room.",
                "chips": ["Add Satellite", "Rooms", "Secure pairing"],
                "details": [
                    "Flash a supported Tater Native image, connect to its setup network, and enter the pairing code shown in Settings -> Voice -> Satellites.",
                    "After pairing, give the device a useful name and room. Room assignment becomes part of every trusted voice turn and can select devices or a preferred music player automatically.",
                    "Saved device identity and pairing credentials persist across Tater restarts and Docker image updates when the documented runtime volume is mounted.",
                ],
            },
            {
                "title": "Local microWakeWord and trainers",
                "summary": "Wake detection stays on the satellite and custom words publish through a scoped trainer link.",
                "chips": ["microWakeWord", "Wake catalog", "Trainer link"],
                "details": [
                    "Choose the active wake word from each satellite's settings popup: a built-in profile, a model from Tater-Wake-Words, or a custom trainer/GitHub JSON URL.",
                    "The Apple Silicon and NVIDIA trainers link with a short-lived code from Tater, then publish only their own trained package and active-word selection.",
                    "Sensitivity and room environment controls adjust acceptance around the model's JSON threshold, sliding window, and close-miss tuning.",
                ],
            },
            {
                "title": "Wake verification and persistent stats",
                "summary": "A fast STT check can observe or reject wake-word mismatches without becoming a new point of failure.",
                "chips": ["Observe", "Enabled", "30-day stats"],
                "details": [
                    "Observe records the transcript, match score, result, and latency while allowing the turn. Enabled rejects clear mismatches but fails open if verification errors or misses its deadline.",
                    "Per-satellite checks, rejections, fail-opens, latest results, and the broader voice summary are stored in Redis and remain visible while a device is offline.",
                    "Statistics automatically begin a new 30-day collection period and can be reset either for Wake Verification alone or for all voice statistics.",
                ],
            },
            {
                "title": "Stereo pairs and multi-room playback",
                "summary": "Two satellites can become one stereo destination, and larger groups can play in sync across rooms.",
                "chips": ["Stereo", "Multi-room", "Ducking"],
                "details": [
                    "Create a left/right pair under Voice -> Stereo Pairs. Music uses real channel routing, while speech stays centered across both members.",
                    "Music Core streams Tater Tube audio to individual satellites, stereo pairs, synchronized native groups, Sonos groups, AirPlay devices, and supported media-player outputs.",
                    "Active music keeps its persistent session while TTS plays as a temporary overlay, ducks the group together, and restores the previous level afterward.",
                    "Offline members are skipped safely, incomplete stereo pairs do not start, and playhead telemetry keeps synchronized members aligned.",
                ],
            },
            {
                "title": "Prebuilt firmware and recovery",
                "summary": "Update by OTA or recover over Browser USB without compiling firmware locally.",
                "chips": ["Prebuilt images", "OTA", "Browser USB"],
                "details": [
                    "Tater matches the selected satellite to the correct firmware family and board revision, then compares its installed version with the signed native release manifest.",
                    "OTA updates run one device at a time with progress and live logs. Browser USB downloads the factory image, optionally erases flash, writes it directly, and follows the device through restart.",
                    "Firmware currently covers Voice PE, Satellite1, ReSpeaker XVF3800, S3 Box, and the board variants published by Tater Native Firmware.",
                ],
            },
            {
                "title": "Identity, rooms, and reply routing",
                "summary": "The latest voice event decides who spoke, where they spoke, and what access applies to that turn.",
                "chips": ["People", "Room aware", "Preferred player"],
                "details": [
                    "Speaker ID aliases can link to a master Person alongside that person's WebUI and portal identities; older history cannot replace the current speaker or inherit their admin access.",
                    "Device Control can use the speaking room when a request says only 'turn on the lights,' while an explicitly named room overrides the satellite room.",
                    "Music Core follows the same rule and can honor the room's preferred player, preferring Sonos when several compatible automatic choices are available.",
                    "Replies can play locally, on a preferred external device, or silently on display-only hardware while follow-up listening remains attached to the original satellite.",
                ],
            },
            {
                "title": "Intercom, displays, and observability",
                "summary": "Tater Voice also carries targeted announcements, visual events, firmware status, and live diagnostics.",
                "chips": ["Intercom", "Displays", "Live logs"],
                "details": [
                    "Intercom resolves device and room names before starting a targeted announcement and can preserve the normal follow-up flow afterward.",
                    "Display APIs publish compact environment values and transient camera, doorbell, image, voice, tool-progress, status, or alert cards to selected Tater screens.",
                    "Voice tabs separate Satellites, Firmware, Stereo Pairs, Stats, and Settings, with live logs and direct entity controls where supported.",
                    "Satellite inventory and hardware state refresh through background System Tasks so opening the page does not perform a slow full-device scan.",
                ],
            },
        ],
        "guides_eyebrow": "Voice experience",
        "guides_title": "How current Tater Voice works from wake to playback",
        "guides_intro": "The current stack centers on paired Tater Native hardware, on-device microWakeWord, trusted room and Person context, prebuilt firmware, and synchronized audio.",
        "apis": [
            {
                "method": "GET",
                "path": "/api/settings/voice/runtime",
                "summary": "Load the complete Voice settings workspace.",
                "details": "Returns cached satellite inventory, firmware state, stereo pairs, settings, logs, and persistent voice-stat sections for the local WebUI.",
            },
            {
                "method": "POST",
                "path": "/api/settings/voice/runtime/action",
                "summary": "Run a Voice UI action.",
                "details": "Handles pairing, room and device settings, stereo-pair changes, firmware actions, intercom controls, live logs, direct entity actions, and voice-stat resets.",
            },
            {
                "method": "GET",
                "path": "/tater-ha/v1/voice/native/status",
                "summary": "Inspect current voice-pipeline and speech-backend state.",
                "details": "Reports the effective speech backends, local model roots, runtime availability, and current native voice state.",
            },
            {
                "method": "GET",
                "path": "/tater-ha/v1/voice/satellites",
                "summary": "List satellite playback and voice targets.",
                "details": "Returns connected and saved native satellites for room-aware routing and compatible companion clients.",
            },
            {
                "method": "GET/POST",
                "path": "/tater-ha/v1/voice/intercom/*",
                "summary": "Discover targets and control an intercom session.",
                "details": "Lists available destinations, reports current state, starts a targeted spoken intercom message, or cancels an active session.",
            },
            {
                "method": "GET/POST",
                "path": "/tater-ha/v1/display/feed",
                "summary": "Serve compact environment and status data to Tater displays.",
                "details": "Returns display-ready readings, labels, online state, and clock data sourced from Tater and enabled cores.",
            },
            {
                "method": "GET/POST",
                "path": "/tater-ha/v1/display/events",
                "summary": "Poll or publish targeted display cards.",
                "details": "Carries transient text, images, snapshot references, tool progress, voice states, and alert metadata to selected displays.",
            },
        ],
    },
    "automation": {
        "label": "Automation Core",
        "description": "Visual event-to-action automation builder powered by Tater's shared rooms, integration devices, notifications, cameras, and voice destinations.",
        "role": "Automation engine",
        "source": TATER_SHOP_DIR / "cores" / "automation_core.py",
        "plugin_surface": "",
        "highlights": [
            "Builds automations from the same integration categories, device actions, rooms, and aliases used throughout Tater.",
            "Triggers include state changes, on/off and open/close transitions, motion, people, vehicles, animals, packages, faces, license plates, doorbells, text matches, connection changes, and numeric thresholds.",
            "Actions can control devices or categories, send notifications, speak on satellites or announcement targets, and describe a camera image with Tater's vision model.",
            "Reusable message fields expose event context without requiring users to hand-write integration-specific payloads.",
            "Cooldowns, enable/disable controls, manual test runs, last-run state, and execution history make each rule observable from the Core UI.",
        ],
        "guides_eyebrow": "Automation builder",
        "guides_title": "Build useful home flows without tying them to one provider",
        "guides_intro": "Automation Core consumes Tater's generic device registry, so the same rule shape can work with Home Assistant, Hue, Shelly, UniFi Protect, and future integrations.",
        "guides": [
            {
                "title": "Choose a trigger",
                "summary": "Start with a device event or condition exposed by an enabled integration.",
                "chips": ["Devices", "Events", "Thresholds"],
                "details": [
                    "Pick a category and device from the shared catalog instead of entering provider-specific identifiers by hand.",
                    "Use event filters for camera detections or state filters for lights, doors, motion, connectivity, text, and numeric values.",
                    "A cooldown prevents repeated sensor chatter from firing the same actions too frequently.",
                ],
            },
            {
                "title": "Compose actions",
                "summary": "One rule can control the home, speak, notify, or ask vision what a camera sees.",
                "chips": ["Device control", "TTS", "Vision"],
                "details": [
                    "Control an individual device or a compatible room/category group using advertised integration actions.",
                    "Send a message through notifier portals or speak it on selected native satellites, stereo pairs, or announcement players.",
                    "Camera actions can capture a current image, generate a short description, then use that result in a notification or spoken announcement.",
                ],
            },
        ],
        "apis": [],
    },
    "environment": {
        "label": "Environment Core",
        "description": "Normalizes local weather and indoor sensor data for the Dashboard, Tater displays, voice answers, and other cores.",
        "role": "Environment telemetry",
        "source": TATER_SHOP_DIR / "cores" / "environment_core.py",
        "plugin_surface": "",
        "highlights": [
            "Combines supported weather stations and enabled sensor integrations into one normalized environment snapshot.",
            "Supplies current conditions and daily forecast cards to the Dashboard without making the page wait on every source.",
            "Publishes display-friendly values for temperature, humidity, rain, wind, lightning, and other available readings.",
            "Supports Ecowitt rain data, Ecobee remote sensors, and consistent Fahrenheit/Celsius conversion.",
            "Keeps source labels attached so the WebUI and Tater screens can show where each value came from.",
        ],
        "apis": [],
    },
    "awareness": {
        "label": "Awareness Core",
        "description": "Home awareness automation core for camera, doorbell, entry-sensor, snapshot, notification, and Redis-backed event history workflows across enabled integrations.",
        "role": "Home awareness engine",
        "source": TATER_SHOP_DIR / "cores" / "awareness_core.py",
        "plugin_surface": "",
        "highlights": [
            "Replaces the old HA automations bridge with an in-core awareness runtime.",
            "Builds camera, doorbell, motion, and entry-sensor options from enabled integration device capabilities.",
            "Existing rules that reference unavailable integrations report the missing integration/device until the provider is downloaded and enabled.",
            "Stores newest-first events in Redis with source area context, timestamps, and metadata for later querying.",
            "Camera and doorbell paths support snapshot + vision summaries, with optional notifications, display cards, and TTS routing.",
            "Entry sensors log both open and closed events, with open-only notifications and optional open-only TTS.",
            "The old Home Assistant-oriented brief system has moved out of Awareness Core; the Tater Dashboard now generates cached 12-hour awareness summaries from the Redis event timeline.",
            "Snapshot notification paths can send recent camera images and descriptions to Tater S3Box displays through the display event API.",
        ],
        "apis": [],
    },
    "guardian": {
        "label": "Guardian Core",
        "description": "Network guardian core for inventory, source health, posture scoring, AI review, and guided security confirmations.",
        "role": "Network security monitor",
        "source": TATER_SHOP_DIR / "cores" / "guardian_core.py",
        "plugin_surface": "",
        "highlights": [
            "Builds a network inventory from the selected network integration. UniFi Network is supported now, and the selector is ready for future network providers.",
            "Can also use local passive ARP cache discovery as an optional source when Tater runs on the same network.",
            "Tracks online, offline, untrusted, and critical devices, plus source health, scan freshness, and recent Guardian events.",
            "Records events for newly observed unknown devices and monitored devices going offline.",
            "Lets operators edit device names, notes, trust state, and critical-device flags from the Guardian WebUI tab.",
            "Runs optional TCP watch checks for important endpoints such as routers, DNS, servers, WAN dependencies, or local infrastructure.",
            "Computes a Guardian posture score from stale inventory data, source errors, offline critical devices, untrusted devices, unknown devices, and failed watch checks.",
            "Uses LLM calls where they improve the feature: posture interpretation, risk level, findings, device suggestions, watch-target suggestions, and follow-up questions.",
            "Does not use a local deterministic fallback for the AI analysis path; if model processing fails, the old analysis is preserved and the error is shown.",
            "Adds a guided Confirm tab where the user answers only Guardian's active questions with quick choices and optional typed context.",
            "Processes confirmations through the model, stores the human answers, and folds that context into the next Guardian analysis.",
            "Injects compact Guardian context into Hydra prompts, including stats, findings, offline/untrusted devices, source health, recent events, and human confirmations.",
            "Includes dark Tater-themed Guardian UI cards for Network Posture/Security Map, AI Threat Brief, and the Guardian Question Queue.",
            "Tunnel integrations were intentionally removed; Guardian does not manage Tailscale, WireGuard, or Cloudflare Tunnel.",
            "Inventory scans and AI security reviews publish through the Core task contract, including their current state, last/next run, errors, and Run Now action in Settings -> System Tasks.",
        ],
        "guides_eyebrow": "Guardian workflow",
        "guides_title": "How Guardian moves from discovery to guided review.",
        "guides_intro": "Guardian is meant to be an operator view for the home or small-business network: collect device facts, let the model interpret them, ask focused questions, then feed the useful context back into Tater.",
        "guides": [
            {
                "title": "Choose a network source",
                "summary": "Guardian starts from an explicit network provider choice instead of assuming one integration forever.",
                "chips": ["Provider selector", "UniFi now", "Future integrations"],
                "details": [
                    "The current provider path pulls clients and devices from the existing UniFi Network integration.",
                    "The settings model is built so future network integrations can appear as selectable sources without redesigning Guardian.",
                    "Passive ARP cache discovery can add local observations when Tater has network visibility.",
                ],
            },
            {
                "title": "Review posture and inventory",
                "summary": "The Guardian tab turns raw network state into an operator-friendly posture view.",
                "chips": ["Posture score", "Device trust", "Watch checks"],
                "details": [
                    "The page groups useful stats such as online, offline, untrusted, unknown, and critical devices.",
                    "Operators can mark devices as trusted or critical and add human-readable labels and notes.",
                    "TCP watch targets help verify infrastructure dependencies that matter even if they are not discovered as rich integration devices.",
                ],
            },
            {
                "title": "Answer Guardian questions",
                "summary": "Guardian questions are not just things to think about; they are prompts the model wants answered so it can refine the analysis.",
                "chips": ["Question cards", "Yes/no", "Typed context"],
                "details": [
                    "Questions appear in a centered, chat-like confirmation card instead of a free-form assistant chat.",
                    "The user can answer simple questions with quick choices and add detail when the answer needs context.",
                    "Save & Process sends only those answers back through Guardian's AI processing path.",
                ],
            },
            {
                "title": "Feed Hydra better context",
                "summary": "Guardian can make Tater's general assistant responses more network-aware without exposing an open-ended Guardian chat.",
                "chips": ["Prompt injection", "Recent findings", "Human confirmations"],
                "details": [
                    "Hydra receives a compact snapshot of Guardian stats, risk notes, source health, recent events, and selected findings.",
                    "User confirmations are included so future recommendations know what has already been recognized or explained.",
                    "The injected context stays bounded so Guardian helps the turn without flooding the prompt.",
                ],
            },
        ],
        "apis": [],
    },
    "ai_task": {
        "label": "AI Task Runner",
        "description": "Scheduled and recurring AI jobs with direct notifier delivery, whole-home broadcast destinations, stereo pairs, and optional generated background-audio scenes.",
        "role": "Scheduler",
        "source": TATER_SHOP_DIR / "cores" / "ai_task_core.py",
        "plugin_surface": "",
        "highlights": [
            "Executes recurring jobs without requiring an external scheduler around Tater.",
            "Routes the prepared result directly through supported notifier portals without asking a second model to rewrite it.",
            "Broadcast delivery can target everywhere, one native satellite, or a configured stereo pair.",
            "Optional generated or uploaded background audio can loop beneath TTS with volume, ducking, attack, release, and finish-fade controls.",
            "Persistent native audio scenes stop their background when the scheduled speech finishes and fall back clearly on older firmware.",
        ],
        "apis": [],
    },
    "memory": {
        "label": "Memory Core",
        "description": "Background memory extraction layer that scans chat history, stores user and room memory, and feeds Hydra context.",
        "role": "Background service",
        "source": TATER_SHOP_DIR / "cores" / "memory_core.py",
        "plugin_surface": "",
        "highlights": [
            "Incrementally mines durable facts from prior conversations instead of relying only on the active turn.",
            "Builds user and room summaries in Redis for later Hydra injection.",
            "Can write linked user memory to master People records so the same person keeps one durable memory profile across portals and Tater Voice identities.",
            "Includes confidence thresholds, identity linking options, and context-size limits.",
            "Memory scans publish as Core-owned System Tasks with schedule, run state, errors, and a manual Run Now control.",
        ],
        "apis": [],
    },
    "music": {
        "label": "Music Core",
        "description": "Tater Tube music library and live whole-home player with room-aware routing to stereo pairs, Sonos, AirPlay, and synchronized native satellites.",
        "role": "Music library + player",
        "source": TATER_SHOP_DIR / "cores" / "music_core.py",
        "plugin_surface": "",
        "highlights": [
            "Pairs securely with Tater Tube Server using a Player PIN, then keeps its artists, albums, genres, tracks, and artwork available in Tater.",
            "Browses Search, Genres, Artists, Albums, and AI-named Tater Recommendations in a responsive local Vue interface with provider artwork.",
            "Keeps a persistent player visible with play, stop, previous, next, synchronized volume, speaker selection, shuffle, and a collapsible current track list.",
            "Playback changes update live without loading screens, page refresh flicker, lost scroll position, or discarded in-progress settings.",
            "An explicitly named room overrides the speaking satellite; otherwise Music Core can use the voice room, saved preferred room player, defaults, and Sonos-first automatic selection.",
            "Tater Tube is the music catalog and playback source; Music Core streams those tracks to native satellites, stereo pairs, synchronized multi-satellite scenes, Sonos, AirPlay, and supported media-player destinations.",
            "Mixed Sonos/native groups use shared start timing plus an adjustable offset, while protected Tater Tube streams stay private and reachable on the LAN.",
            "Listening history feeds AI-named recommendation playlists and a compact selected-Person profile with favorite genres, artists, and recent tracks.",
            "Music context is injected only when a Person is selected and that Person is the current trusted speaker; no selection means no prompt injection.",
            "Continuous radio can extend a queue near its final tracks so a broad voice request keeps playing without stacking unrelated manual album queues.",
            "Catalog sync, recommendations, prompt-profile generation, and continuous-radio refill appear in Settings -> System Tasks with next-run state and Run Now controls.",
        ],
        "guides_eyebrow": "Whole-home music",
        "guides_title": "Browse once, then play naturally by voice or from the live player",
        "guides_intro": "Music Core keeps the Tater Tube library, room selection, active playback, history, and AI recommendations in one local surface.",
        "guides": [
            {
                "title": "Pair Tater Tube Server",
                "summary": "Pair once with a Player PIN and let Music Core build its local browse catalog.",
                "chips": ["Tater Tube Server", "Player PIN", "Background sync"],
                "details": [
                    "Create a six-digit Player PIN in Tater Tube Server, then enter the server URL and PIN in Music Core.",
                    "Catalog sync collects artists, albums, genres, tracks, and artwork, then refreshes in the background on the configured interval.",
                    "Tater Tube setup and the player remain available from the same Core tab, with connection state shown clearly.",
                ],
            },
            {
                "title": "Choose where it plays",
                "summary": "Room context removes the need to ask which speaker when Tater already knows.",
                "chips": ["Room aware", "Preferred player", "Sonos first"],
                "details": [
                    "If a request names a room, that room wins. Otherwise the speaking satellite's room is used when available.",
                    "A preferred player saved for the room is selected before global defaults, and Sonos is preferred when automatic selection finds several compatible players.",
                    "The player-bar speaker button opens Tater Tube stream destinations with readable labels, including native satellites, stereo pairs, Sonos speakers/groups, AirPlay devices, and supported media-player outputs.",
                ],
            },
            {
                "title": "Live queue and player",
                "summary": "The persistent player changes in place and keeps the active album or mix easy to navigate.",
                "chips": ["No reloads", "Track list", "Synced volume"],
                "details": [
                    "Playing another album replaces the active track list instead of appending it to the previous one.",
                    "The current song stays highlighted; double-click another row to jump directly to it, or use previous/next without leaving the page.",
                    "Live Core events update only when playback state changes, preserving the selected browse tab, open track list, forms, and scroll position.",
                ],
            },
            {
                "title": "Stereo and multi-room scenes",
                "summary": "One request can play through a calibrated stereo pair or a larger synchronized group.",
                "chips": ["Stereo pair", "Native sync", "Mixed groups"],
                "details": [
                    "Native members prebuffer the same media and start from a shared clock; stereo pairs retain left/right routing, level, and delay calibration.",
                    "Sonos groups can be formed temporarily, then restored without permanently disturbing the listener's queue or prior grouping.",
                    "Music remains a persistent session while voice replies play as ducked overlays and restore the original music level afterward.",
                ],
            },
            {
                "title": "Personalized music context",
                "summary": "A selected Person can receive better music suggestions without sharing that profile with everyone.",
                "chips": ["People", "Listening history", "Recommendations"],
                "details": [
                    "Music Core records recent listening and can generate favorite genres, favorite artists, recent tracks, and a short taste summary for one selected Person.",
                    "The prompt fragment is only added when Tater resolves the current speaker to that same Person; leaving the setting empty disables music prompt injection.",
                    "Tater Recommendations choose exact items from the current catalog and publish friendly AI-named mixes that can be played directly from the browser.",
                ],
            },
        ],
        "apis": [],
    },
    "personal": {
        "label": "Personal Core",
        "description": "Email intelligence core that scans inboxes, builds a structured personal profile, injects optional Hydra context, and supports cross-portal notifications.",
        "role": "Personal intelligence engine",
        "source": TATER_SHOP_DIR / "cores" / "personal_core.py",
        "plugin_surface": "",
        "highlights": [
            "Scans one or more IMAP inboxes on a configurable interval and stores normalized email history in Redis.",
            "Extracts structured signals such as spending habits, upcoming events, subscriptions, deliveries, action items, and important notes.",
            "Publishes personal kernel tools for search, summarization, spending, plans, subscriptions, deliveries, actions, notes, and favorite places.",
            "Can inject bounded personal context into Hydra prompts per portal, with Discord/IRC/Telegram/Matrix controls.",
            "Supports notification routing through notifier portals with destination controls and per-cycle limits.",
            "Includes a dedicated WebUI tab for stats, context previews, manual scans, notification tests, and safe data cleanup actions.",
            "Mailbox scans and profile refreshes appear as Core-owned System Tasks instead of running as invisible background work.",
        ],
        "apis": [],
    },
    "rss": {
        "label": "RSS",
        "description": "Background feed watcher that summarizes articles and dispatches updates through notifier portals.",
        "role": "Background service",
        "source": TATER_SHOP_DIR / "cores" / "rss_core.py",
        "plugin_surface": "",
        "highlights": [
            "Polls feeds, extracts article bodies, and creates digest-style summaries.",
            "Designed for automated broadcast and notification workflows rather than direct user chat.",
            "Lets Tater act as a content monitor in addition to an assistant.",
            "Feed polling publishes its schedule, latest run, next run, errors, and Run Now action through Settings -> System Tasks.",
        ],
        "apis": [],
    },
    "tater_tube": {
        "label": "Tater Tube Core",
        "description": "Connects Tater to Tater Tube Server for recent viewing context, AI-selected movie and series recommendations, and spoken Tater's Picks.",
        "role": "Media intelligence",
        "source": TATER_SHOP_DIR / "cores" / "tater_tube_core.py",
        "plugin_surface": "",
        "highlights": [
            "Pairs with Tater Tube Server and reads recent viewing activity without turning the general assistant into a media-server client.",
            "Can inject a bounded recent-viewing summary so Tater understands what the selected user has been watching.",
            "Builds AI-selected movie and series recommendations and publishes them as Tater's Picks.",
            "Uses the user's configured TTS path when a recommendation should be voiced.",
            "Recurring sync and recommendation work publishes through the Core task contract so it appears in Settings -> System Tasks.",
        ],
        "apis": [],
    },
    "xbmc": {
        "label": "XBMC4Xbox",
        "description": "Original Xbox integration through the custom Cortana-powered Tater skin and scripts for XBMC4Xbox.",
        "role": "Console endpoint",
        "source": TATER_SHOP_DIR / "portals" / "xbmc_portal.py",
        "plugin_surface": "xbmc",
        "highlights": [
            "Gives Tater a living-room interface on the OG Xbox.",
            "Maintains local conversation sessions and routes actions through the same Hydra core.",
            "Pairs well with media, smart-home, and utility Verbas for couch-side control.",
            "Supports optional API key protection on HTTP endpoints using X-Tater-Token.",
        ],
        "apis": [],
    },
}

PLATFORM_META = {
    key: {
        "label": value["label"],
        "description": value["description"],
    }
    for key, value in PLATFORM_DOCS.items()
}
PLATFORM_META["voice_core"] = {
    "label": "Tater Voice",
    "description": "Built-in room-aware Tater Native voice runtime with local microWakeWord, intercom, stereo pairs, synchronized playback, and trusted speaking-device context.",
}

INSTALL_METHODS = [
    {
        "slug": "macos",
        "title": "Tater for macOS",
        "eyebrow": "Native Mac app",
        "summary": "Install the complete Tater server as a native Apple Silicon Mac app with a private runtime, menu bar controls, and automatic updates.",
        "best_for": "Apple Silicon Macs running macOS 15 or newer that want the simplest native Tater setup.",
        "complexity": "Low",
        "highlights": [
            "The DMG includes Tater.app and an Applications shortcut for a standard drag-and-drop installation.",
            "First launch prepares a private managed runtime under ~/.taterassistant without changing a source checkout or system Python.",
            "Closing the main window keeps Tater running in the menu bar, where it can be opened, restarted, updated, inspected, or quit.",
            "The native window runs the same TaterOS WebUI and main Tater routes used by the other installation paths.",
        ],
        "steps": [
            "Download the latest Tater DMG for macOS.",
            "Open the DMG and drag Tater.app into Applications.",
            "Open Tater from Applications and allow the first launch to prepare its private Python 3.11 runtime and environment.",
            "Finish Redis, model, voice, integration, and Core setup in the TaterOS WebUI.",
            "Use the Tater menu bar item to reopen the app, view logs, restart Tater, check for updates, or quit.",
        ],
        "notes": [
            "The native app currently requires an Apple Silicon Mac running macOS 15.0 or newer.",
            "App data, downloaded models, Cores, Verbas, integrations, settings, logs, and updates stay under ~/.taterassistant.",
            "Use the DMG for a first installation. Existing supported app versions can install later releases from the built-in updater.",
        ],
        "snippets": [],
        "links": [
            {
                "label": "Latest Tater release",
                "href": "https://github.com/TaterTotterson/Tater/releases/latest",
            },
        ],
    },
    {
        "slug": "unraid",
        "title": "Unraid Community Apps",
        "eyebrow": "Recommended easy path",
        "summary": "Install Tater and Redis Stack from Unraid Community Apps with persistent storage for Agent Lab and runtime config.",
        "best_for": "Unraid users who want the smoothest packaged deployment.",
        "complexity": "Low",
        "highlights": [
            "Tater is available in the Unraid Community Apps store.",
            "The README recommends installing both Tater and Redis Stack from the app store templates.",
            "Persistent Agent Lab and .runtime storage matters so updates do not wipe workspace data, Spudex working files, Redis setup/encryption state, or auto-downloaded voice models.",
        ],
        "steps": [
            "Open Unraid Community Apps and install Redis Stack.",
            "Install Tater from the Community Apps store.",
            "Add persistent path mappings for /app/agent_lab and /app/.runtime inside the container (for example /mnt/user/appdata/tater/agent_lab and /mnt/user/appdata/tater/runtime).",
            "Optional but recommended: set TZ and map /etc/localtime + /etc/timezone for local container time.",
            "Start the containers and finish configuration in the WebUI.",
        ],
        "notes": [
            "Without /app/agent_lab mapping, Agent Lab data, Spudex workspace files, and downloaded STT/TTS voice models can be lost on rebuild/update.",
            "Without /app/.runtime mapping, Redis setup popup config and Redis encryption key/state can be lost on rebuild/update.",
        ],
        "snippets": [],
        "links": [],
    },
    {
        "slug": "home-assistant",
        "title": "Home Assistant Add-on",
        "eyebrow": "Smart-home path",
        "summary": "Install Tater through the dedicated Home Assistant add-on repository, with Redis Stack as the required companion service.",
        "best_for": "Home Assistant users who want Tater inside the supervisor/add-on workflow.",
        "complexity": "Low to medium",
        "highlights": [
            "The README points to a dedicated Home Assistant add-on repository for Tater.",
            "The add-on store exposes Redis Stack and Tater AI Assistant together.",
            "This path is for running the Tater container stack from Home Assistant's add-on workflow; Tater's current voice/display work is managed from the built-in WebUI.",
        ],
        "steps": [
            "Add the Tater add-on repository: https://github.com/TaterTotterson/hassio-addons-tater",
            "Install and start Redis Stack first.",
            "Install Tater AI Assistant second.",
            "Start Tater and open the WebUI ingress page.",
            "Complete Redis setup in the popup if prompted, then configure Hydra model settings in WebUI.",
            "Verify the WebUI loads through ingress and that Tater's main API routes are reachable.",
        ],
        "notes": [
            "Awareness automations now run in Awareness Core inside Tater rather than a separate automation bridge endpoint.",
            "Dashboard briefs, environment summaries, awareness snapshots, and Tater Voice display notifications are now Tater-native surfaces.",
            "Companion and smart-home routes can use the shared X-Tater-Token header when API auth is enabled.",
        ],
        "snippets": [
            {
                "label": "Add-on repository",
                "code": "https://github.com/TaterTotterson/hassio-addons-tater",
            },
        ],
        "links": [
            {
                "label": "Add-on Repository",
                "href": "https://github.com/TaterTotterson/hassio-addons-tater",
            },
        ],
    },
    {
        "slug": "local",
        "title": "Local Source Install",
        "eyebrow": "Setup script path",
        "summary": "Clone Tater, run the setup script for the right runtime profile, then start TaterOS with the local launcher.",
        "best_for": "Developers and operators who want direct source control and local customization.",
        "complexity": "Medium",
        "highlights": [
            "The setup script creates .venv, installs Tater's Python dependencies, and writes the selected runtime profile to .runtime/tater_profile.env.",
            "Profiles cover CPU, edge / remote-only, macOS Apple Silicon, NVIDIA CUDA, AMD ROCm / Strix Halo, Jetson, and Jetson Thor.",
            "Tater supports Python 3.11 through 3.13. On Linux, setup can install a checksum-verified private Python runtime when the system Python is unsupported.",
            "Normal local profiles use Tater's embedded Redis runtime. The edge / remote-only profile expects the operating system redis-server package.",
            "Model choices are finished inside TaterOS under Settings -> Models and Settings -> Voice Pipeline.",
        ],
        "steps": [
            "Clone the repository.",
            "Change into the Tater project directory.",
            "Run sh setup_tater.sh and choose the runtime profile for this machine, or pass a profile name for non-interactive setup.",
            "For edge / remote-only installs, install redis-server first, then run the edge profile.",
            "Start TaterOS with sh run_ui.sh.",
            "Open http://127.0.0.1:8501 from the same machine, or use the host's address from another device on your network.",
            "Finish setup in TaterOS by selecting your LLM, Vision, Spudex, voice, and optional Beast Mode model providers.",
        ],
        "notes": [
            "The setup profile prepares the runtime only; actual model choices are managed from TaterOS.",
            "run_ui.sh automatically loads .venv and .runtime/tater_profile.env when they exist, and listens on 0.0.0.0:8501 by default.",
            "Set HTMLUI_PORT before run_ui.sh if you need a different port.",
            "Set TATER_SETUP_INSTALL_MANAGED_PYTHON=0 to disable private Python downloads, or TATER_SETUP_INSTALL_SYSTEM_DEPS=0 to disable automatic Linux system-package installation.",
            "Downloaded models live under agent_lab/models, Spudex work starts under agent_lab/workspace, and runtime state is kept under .runtime.",
        ],
        "snippets": [
            {
                "label": "Clone and run setup",
                "code": """git clone https://github.com/TaterTotterson/Tater.git
cd Tater
sh setup_tater.sh""",
            },
            {
                "label": "Non-interactive profiles",
                "code": """sh setup_tater.sh cpu
sh setup_tater.sh edge
sh setup_tater.sh macos
sh setup_tater.sh nvidia
sh setup_tater.sh rocm
sh setup_tater.sh jetson
sh setup_tater.sh thor""",
            },
            {
                "label": "Start TaterOS",
                "code": """sh run_ui.sh

# Optional different port:
HTMLUI_PORT=8601 sh run_ui.sh""",
            },
        ],
        "links": [
            {
                "label": "Tater Repository",
                "href": "https://github.com/TaterTotterson/Tater",
            },
        ],
    },
    {
        "slug": "docker",
        "title": "Docker Image",
        "eyebrow": "Container path",
        "summary": "Run the published container image with persistent Agent Lab/.runtime volumes, then configure Redis + Hydra in WebUI.",
        "best_for": "Operators who want a direct container deployment outside packaged add-on/app-store flows.",
        "complexity": "Medium",
        "highlights": [
            "The README publishes the image at ghcr.io/tatertotterson/tater:latest.",
            "Container persistence warnings include both /app/agent_lab and /app/.runtime host mappings, preserving Spudex workspaces, downloaded models, Redis setup, and native satellite pairing credentials.",
            "The container exposes the WebUI/API on port 8501; portal routes mount under that same Tater port.",
            "Docker and local command-line runs read the same canonical packaged version as the macOS app, so the bottom-left WebUI label reports the installed build correctly.",
        ],
        "steps": [
            "Pull the published image.",
            "Start the container with the main Tater port and persistent volume mappings.",
            "Mount /app/agent_lab and /app/.runtime to host storage so runtime and Redis config persist across rebuilds.",
            "Open the WebUI and complete Redis setup popup if prompted.",
            "Configure Hydra base model settings and optional Beast Mode role routing in Settings.",
            "Open the WebUI at http://localhost:8501 after the container is running.",
        ],
        "notes": [
            "If /app/agent_lab is not mounted, runtime data, Spudex workspace files, and downloaded Faster Whisper/Vosk/Kokoro/Pocket TTS/Piper models can be lost on rebuild/update.",
            "If /app/.runtime is not mounted, Redis setup, encryption state, and Tater Native satellite pairing credentials can be lost on rebuild/update.",
            "The README also calls out Unraid-specific time-zone mappings for /etc/localtime and /etc/timezone.",
        ],
        "snippets": [
            {
                "label": "Pull the image",
                "code": "docker pull ghcr.io/tatertotterson/tater:latest",
            },
            {
                "label": "Docker run with persistent runtime paths",
                "code": """docker run -d --name tater_webui \\
  -p 8501:8501 \\
  -e TZ=America/Chicago \\
  -v /etc/localtime:/etc/localtime:ro \\
  -v /etc/timezone:/etc/timezone:ro \\
  -v /tater_agent_lab:/app/agent_lab \\
  -v /tater_runtime:/app/.runtime \\
  ghcr.io/tatertotterson/tater:latest""",
            },
            {
                "label": "Docker run (same port/volumes, alternate host paths)",
                "code": """docker run -d --name tater_webui \\
  -p 8501:8501 \\
  -e TZ=America/Chicago \\
  -v /etc/localtime:/etc/localtime:ro \\
  -v /etc/timezone:/etc/timezone:ro \\
  -v /tater_agent_lab:/app/agent_lab \\
  -v /tater_runtime:/app/.runtime \\
  ghcr.io/tatertotterson/tater:latest""",
            },
        ],
        "links": [],
    },
]

KERNEL_TOOL_GROUPS = {
    "Catalog and inspection": [
        "list_tools",
        "get_plugin_help",
        "list_platforms_for_plugin",
        "list_stable_plugins",
        "list_stable_platforms",
        "inspect_plugin",
        "validate_plugin",
        "test_plugin",
        "validate_platform",
    ],
    "Workspace and files": [
        "read_file",
        "search_files",
        "write_file",
        "list_directory",
        "delete_file",
        "download_file",
        "list_archive",
        "extract_archive",
        "write_workspace_note",
        "list_workspace",
        "attach_file",
    ],
    "Web and media": [
        "search_web",
        "inspect_webpage",
        "image_describe",
    ],
    "Memory and delivery": [
        "memory_get",
        "memory_set",
        "memory_list",
        "memory_explain",
        "memory_search",
        "send_message",
    ],
    "Terminal console": [
        "spudex_run",
        "spudex_task",
        "spudex_status",
        "spudex_stop",
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_install_readme_note() -> str:
    if not TATER_README.exists():
        return DEFAULT_INSTALL_README_NOTE

    try:
        lines = read_text(TATER_README).splitlines()
    except Exception:
        return DEFAULT_INSTALL_README_NOTE

    for raw in lines:
        line = str(raw or "").strip()
        if not line:
            continue
        line = line.lstrip(">").strip()
        if line.startswith("- "):
            line = line[2:].strip()
        line = " ".join(line.split())
        if "Tater currently recommends" in line:
            return line

    return DEFAULT_INSTALL_README_NOTE


def parse_module(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


def literal_value(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [literal_value(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return [literal_value(item) for item in node.elts]
    if isinstance(node, ast.Set):
        return [literal_value(item) for item in node.elts]
    if isinstance(node, ast.Dict):
        out: dict[str, Any] = {}
        for key, value in zip(node.keys, node.values):
            out[str(literal_value(key))] = literal_value(value)
        return out
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        value = literal_value(node.operand)
        return -value if isinstance(value, (int, float)) else value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = literal_value(node.left)
        right = literal_value(node.right)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        if isinstance(left, list) and isinstance(right, list):
            return left + right
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        left = literal_value(node.left)
        right = literal_value(node.right)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left * right
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def extract_named_literal(path: Path, name: str) -> Any:
    tree = parse_module(path)
    assignments: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            assignments[node.target.id] = node.value

    cache: dict[str, Any] = {}

    def resolve(node: ast.AST) -> Any:
        if isinstance(node, ast.Name):
            key = node.id
            if key in cache:
                return cache[key]
            if key in assignments:
                cache[key] = resolve(assignments[key])
                return cache[key]
            return None
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.List):
            return [resolve(item) for item in node.elts]
        if isinstance(node, ast.Tuple):
            return [resolve(item) for item in node.elts]
        if isinstance(node, ast.Set):
            return [resolve(item) for item in node.elts]
        if isinstance(node, ast.Dict):
            out: dict[str, Any] = {}
            for key, value in zip(node.keys, node.values):
                out[str(resolve(key))] = resolve(value)
            return out
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            value = resolve(node.operand)
            return -value if isinstance(value, (int, float)) else value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = resolve(node.left)
            right = resolve(node.right)
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, list) and isinstance(right, list):
                return left + right
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            left = resolve(node.left)
            right = resolve(node.right)
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left * right
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            args = [resolve(arg) for arg in node.args]
            if func_name == "int" and args:
                try:
                    return int(args[0])
                except Exception:
                    return None
            if func_name == "float" and args:
                try:
                    return float(args[0])
                except Exception:
                    return None
            if func_name == "str" and args:
                return str(args[0])
        try:
            return ast.literal_eval(node)
        except Exception:
            return None

    if name in assignments:
        return resolve(assignments[name])
    raise KeyError(f"{name} not found in {path}")


def extract_plugin_metadata(path: Path) -> dict[str, Any]:
    tree = parse_module(path)
    plugin_class: ast.ClassDef | None = None
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        base_names = {getattr(base, "id", "") for base in node.bases if isinstance(base, ast.Name)}
        if "ToolPlugin" in base_names:
            plugin_class = node
            break

    values: dict[str, Any] = {
        "id": path.stem,
        "name": path.stem,
        "plugin_name": "",
        "pretty_name": "",
        "description": "",
        "plugin_dec": "",
        "when_to_use": "",
        "how_to_use": "",
        "version": "",
        "usage": "",
        "platforms": [],
        "required_settings": {},
        "guides": [],
    }

    if plugin_class is None:
        return normalize_plugin(values)

    for node in plugin_class.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        key = node.targets[0].id
        if key not in values:
            continue
        values[key] = literal_value(node.value)

    return normalize_plugin(values)


def shop_manifest_plugins() -> list[dict[str, Any]]:
    if not TATER_SHOP_MANIFEST.exists():
        return []

    try:
        payload = json.loads(read_text(TATER_SHOP_MANIFEST))
    except Exception:
        return []

    items = payload.get("verbas") if isinstance(payload, dict) else []
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def manifest_fallback_plugin(entry: dict[str, Any]) -> dict[str, Any]:
    plugin_id = str(entry.get("id") or "").strip()
    display_name = str(entry.get("name") or plugin_id.replace("_", " ").title()).strip()
    return normalize_plugin(
        {
            "id": plugin_id,
            "name": plugin_id,
            "plugin_name": display_name,
            "pretty_name": display_name,
            "description": str(entry.get("description") or "").strip(),
            "plugin_dec": str(entry.get("description") or "").strip(),
            "when_to_use": "",
            "how_to_use": "",
            "version": str(entry.get("version") or "").strip(),
            "usage": "",
            "platforms": clean_platforms(entry.get("portals") or entry.get("platforms")),
            "required_settings": {},
            "guides": [],
        }
    )


def merge_shop_manifest(plugin: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    merged = dict(plugin)

    display_name = str(entry.get("name") or "").strip()
    if display_name:
        merged["title"] = display_name

    description = str(entry.get("description") or "").strip()
    if description:
        merged["description"] = " ".join(description.split())

    version = str(entry.get("version") or "").strip()
    if version:
        merged["version"] = version

    platforms = clean_platforms(entry.get("portals") or entry.get("platforms"))
    if platforms:
        merged["platforms"] = platforms

    merged["shop_entry"] = str(entry.get("entry") or "").strip()
    merged["min_tater_version"] = str(entry.get("min_tater_version") or "").strip()
    merged["settings_category"] = str(entry.get("settings_category") or "").strip()
    merged["sha256"] = str(entry.get("sha256") or "").strip()
    return merged


def build_plugins() -> list[dict[str, Any]]:
    manifest_entries = shop_manifest_plugins()
    if not manifest_entries:
        raise RuntimeError(
            f"No Verbas found in {TATER_SHOP_MANIFEST}. "
            "Expected a top-level 'verbas' list populated by Tater_Shop."
        )

    rows: list[dict[str, Any]] = []
    for entry in manifest_entries:
        plugin_id = str(entry.get("id") or "").strip()
        if plugin_id in LEGACY_MUSIC_PROVIDER_PLUGIN_IDS:
            continue
        relative_entry = str(entry.get("entry") or "").strip()
        source_path = (TATER_SHOP_DIR / relative_entry).resolve() if relative_entry else None
        if source_path and source_path.exists():
            plugin = extract_plugin_metadata(source_path)
        else:
            plugin = manifest_fallback_plugin(entry)
        rows.append(merge_shop_manifest(plugin, entry))
    return sorted(rows, key=lambda item: item["title"].lower())


def integration_manifest_entries() -> list[dict[str, Any]]:
    if not TATER_INTEGRATIONS_MANIFEST.exists():
        return []

    try:
        payload = json.loads(read_text(TATER_INTEGRATIONS_MANIFEST))
    except Exception:
        return []

    items = payload.get("integrations") if isinstance(payload, dict) else []
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def integration_metadata_for_entry(entry: dict[str, Any]) -> dict[str, Any]:
    relative_entry = str(entry.get("entry") or "").strip()
    if not relative_entry:
        return {}
    source_path = (TATER_INTEGRATIONS_DIR / relative_entry).resolve()
    if not source_path.exists():
        return {}
    try:
        meta = extract_named_literal(source_path, "INTEGRATION")
    except Exception:
        return {}
    return meta if isinstance(meta, dict) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        out.append(text)
        seen.add(text)
    return out


def build_integrations() -> list[dict[str, Any]]:
    manifest_entries = integration_manifest_entries()
    rows: list[dict[str, Any]] = []
    for index, entry in enumerate(manifest_entries):
        integration_id = str(entry.get("id") or "").strip()
        if not integration_id:
            continue
        meta = integration_metadata_for_entry(entry)
        override = INTEGRATION_DOC_OVERRIDES.get(integration_id, {})

        fields = meta.get("fields") if isinstance(meta.get("fields"), list) else []
        actions = meta.get("actions") if isinstance(meta.get("actions"), list) else []
        field_labels = [
            str(field.get("label") or field.get("key") or "").strip()
            for field in fields
            if isinstance(field, dict) and str(field.get("label") or field.get("key") or "").strip()
        ]
        action_labels = [
            str(action.get("label") or action.get("id") or "").strip()
            for action in actions
            if isinstance(action, dict) and str(action.get("label") or action.get("id") or "").strip()
        ]

        capabilities = (
            _string_list(override.get("capabilities"))
            or _string_list(entry.get("capabilities"))
            or _string_list(meta.get("capabilities"))
        )
        category = str(override.get("category") or ("Web search" if "web_search" in capabilities else "Device")).strip()
        description = str(override.get("description") or entry.get("description") or meta.get("description") or "").strip()
        summary = str(override.get("summary") or description).strip()
        rows.append(
            {
                "id": integration_id,
                "slug": integration_id,
                "title": str(entry.get("name") or meta.get("name") or integration_id.replace("_", " ").title()).strip(),
                "description": " ".join(description.split()),
                "summary": " ".join(summary.split()),
                "version": str(entry.get("version") or "").strip() or "unknown",
                "entry": str(entry.get("entry") or "").strip(),
                "required": bool(entry.get("required")),
                "category": category,
                "capabilities": capabilities,
                "fields": field_labels,
                "actions": action_labels,
                "order": int(meta.get("order") or 1000),
                "notes": _string_list(override.get("notes")),
                "source_index": index,
            }
        )

    category_order = {
        "Web search": 0,
        "Smart home": 1,
        "Security": 2,
        "Audio": 3,
        "Lighting": 4,
        "Climate": 5,
        "Access": 6,
        "Network": 7,
        "Weather": 8,
        "Models": 9,
        "Device": 10,
    }
    return sorted(
        rows,
        key=lambda item: (
            category_order.get(str(item.get("category") or ""), 99),
            int(item.get("order") or 1000),
            str(item.get("title") or "").lower(),
        ),
    )


def normalize_plugin(raw: dict[str, Any]) -> dict[str, Any]:
    plugin_id = str(raw.get("id") or "").strip()
    overrides = PLUGIN_OVERRIDES.get(plugin_id, {})
    pretty_name = str(raw.get("pretty_name") or "").strip()
    plugin_name = str(raw.get("plugin_name") or "").strip()
    title = str(overrides.get("title") or pretty_name or plugin_name or plugin_id.replace("_", " ").title()).strip()
    description = (
        str(overrides.get("description") or "").strip()
        or str(raw.get("description") or "").strip()
        or str(raw.get("plugin_dec") or "").strip()
        or "No description is present in the current Verba metadata."
    )
    when_to_use = str(overrides.get("when_to_use") or raw.get("when_to_use") or "").strip()
    if not when_to_use:
        when_to_use = first_sentence(description) or "Use this Verba when the user asks for this capability."
    how_to_use = str(overrides.get("how_to_use") or raw.get("how_to_use") or "").strip()
    if not how_to_use:
        how_to_use = "Use the example call shape below and provide only the fields the plugin expects."
    usage = str(raw.get("usage") or "").strip()
    version = str(raw.get("version") or "").strip() or "unknown"
    platforms = clean_platforms(raw.get("portals") or raw.get("platforms"))
    required_settings = raw.get("required_settings") if isinstance(raw.get("required_settings"), dict) else {}

    usage_example = str(overrides.get("usage_example") or canonical_usage(plugin_id, usage)).strip()
    arguments = usage_arguments(usage_example)

    return {
        "id": plugin_id,
        "slug": plugin_id,
        "title": title,
        "description": " ".join(description.split()),
        "when_to_use": " ".join(when_to_use.split()),
        "how_to_use": " ".join(how_to_use.split()),
        "version": version,
        "platforms": platforms,
        "required_settings": normalize_required_settings(required_settings),
        "usage_example": usage_example,
        "arguments": arguments,
        "guides": list(overrides.get("guides") or []),
    }


def normalize_required_settings(source: dict[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for key in sorted(source):
        meta = source.get(key)
        label = str(key)
        item = {
            "key": label,
            "label": label,
            "type": "",
            "description": "",
            "default": "",
            "options": "",
        }
        if isinstance(meta, dict):
            item["label"] = portalize_copy(str(meta.get("label") or key).strip())
            item["type"] = str(meta.get("type") or "").strip()
            item["description"] = portalize_copy(str(meta.get("description") or meta.get("label") or "").strip())
            default = meta.get("default")
            item["default"] = "" if default in (None, "") else str(default)
            options = meta.get("options")
            if isinstance(options, list):
                opt_values: list[str] = []
                for option in options:
                    if isinstance(option, dict):
                        value = option.get("label") or option.get("value")
                        if value not in (None, ""):
                            opt_values.append(str(value))
                    elif option not in (None, ""):
                        opt_values.append(str(option))
                item["options"] = ", ".join(opt_values)
        items.append(item)
    return items


def first_sentence(text: str) -> str:
    cleaned = " ".join(str(text or "").split())
    if not cleaned:
        return ""
    for mark in (". ", "! ", "? "):
        if mark in cleaned:
            return cleaned.split(mark, 1)[0].strip() + mark.strip()
    return cleaned


def find_json_object(text: str) -> str | None:
    raw = str(text or "").strip()
    start = raw.find("{")
    if start < 0:
        return None
    depth = 0
    for index in range(start, len(raw)):
        char = raw[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return raw[start : index + 1]
    return None


def canonical_usage(plugin_id: str, usage: str) -> str:
    snippet = find_json_object(usage)
    if snippet:
        try:
            data = json.loads(snippet)
        except Exception:
            data = {}
    else:
        data = {}

    if not isinstance(data, dict):
        data = {}
    data["function"] = plugin_id
    if not isinstance(data.get("arguments"), dict):
        data["arguments"] = {}
    return json.dumps(data, indent=2, ensure_ascii=True)


def usage_arguments(usage_text: str) -> list[dict[str, str]]:
    try:
        parsed = json.loads(usage_text)
    except Exception:
        parsed = {}
    arguments = parsed.get("arguments") if isinstance(parsed, dict) else {}
    if not isinstance(arguments, dict):
        return []

    rows: list[dict[str, str]] = []
    for key, value in arguments.items():
        if str(key) == "origin":
            continue
        rows.append(
            {
                "name": str(key),
                "type": infer_type(value),
                "example": "" if value in (None, "") else str(value),
            }
        )
    return rows


def infer_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def portalize_copy(text: Any) -> str:
    value = str(text or "").strip()
    if not value:
        return value
    return (
        value
        .replace("current platform", "current portal")
        .replace("cross-platform", "cross-portal")
        .replace("notifier platforms", "notifier portals")
        .replace("platform endpoints", "portal endpoints")
        .replace("automation platform", "automation portal")
        .replace("through platform config", "through portal config")
        .replace("this platform", "this portal")
        .replace("platform notification endpoint", "portal notification endpoint")
        .replace("Platform notification endpoint", "Portal notification endpoint")
        .replace(" across platforms ", " across portals ")
    )


def extract_kernel_tools() -> list[dict[str, str]]:
    tool_ids = extract_named_literal(TOOL_RUNTIME_SOURCE, "META_TOOLS")
    purposes = extract_named_literal(TOOL_RUNTIME_SOURCE, "_KERNEL_TOOL_PURPOSE_HINTS")
    usage_hints = extract_named_literal(CERBERUS_SOURCE, "_KERNEL_TOOL_USAGE_HINTS")
    spudex_rows: list[dict[str, str]] = []
    if SPUDEX_TOOLS_SOURCE.exists():
        try:
            extracted = extract_named_literal(SPUDEX_TOOLS_SOURCE, "SPUDEX_TOOL_ROWS")
        except Exception:
            extracted = []
        if isinstance(extracted, list):
            for item in extracted:
                if isinstance(item, dict) and item.get("id"):
                    spudex_rows.append(
                        {
                            "id": str(item.get("id") or "").strip(),
                            "purpose": str(item.get("description") or "").strip(),
                            "usage": str(item.get("usage") or "").strip(),
                        }
                    )

    ids = sorted({str(item) for item in (tool_ids or [])} | {row["id"] for row in spudex_rows if row.get("id")})
    spudex_by_id = {row["id"]: row for row in spudex_rows}
    rows: list[dict[str, str]] = []
    for tool_id in ids:
        overrides = KERNEL_TOOL_OVERRIDES.get(tool_id, {})
        spudex_row = spudex_by_id.get(tool_id, {})
        rows.append(
            {
                "id": tool_id,
                "purpose": str(
                    overrides.get("purpose")
                    or spudex_row.get("purpose")
                    or (purposes or {}).get(tool_id)
                    or tool_id.replace("_", " ")
                ).strip(),
                "usage": pretty_json_string(
                    str(
                        overrides.get("usage")
                        or spudex_row.get("usage")
                        or (usage_hints or {}).get(tool_id)
                        or json.dumps({"function": tool_id, "arguments": {}})
                    )
                ),
                "group": kernel_group(tool_id),
            }
        )
        rows[-1]["purpose"] = portalize_copy(rows[-1]["purpose"])
    return rows


def pretty_json_string(text: str) -> str:
    try:
        parsed = json.loads(text)
    except Exception:
        return str(text or "").strip()
    return json.dumps(parsed, indent=2, ensure_ascii=True)


def kernel_group(tool_id: str) -> str:
    for group, tool_ids in KERNEL_TOOL_GROUPS.items():
        if tool_id in tool_ids:
            return group
    return "Other"


def extract_cerberus_defaults() -> list[dict[str, str]]:
    keys = [
        ("DEFAULT_MAX_ROUNDS", "Max rounds", ""),
        ("DEFAULT_MAX_TOOL_CALLS", "Max tool calls", ""),
        ("DEFAULT_MAX_LEDGER_ITEMS", "Max ledger items", ""),
        ("DEFAULT_ASTRAEUS_PLAN_REVIEW_ENABLED", "Astraeus second plan check", ""),
        ("DEFAULT_AUTO_CONTINUE_INCOMPLETE_FINAL_ENABLED", "Head auto-continue", ""),
    ]
    rows: list[dict[str, str]] = []
    for constant_name, label, unit in keys:
        value = extract_named_literal(CERBERUS_SOURCE, constant_name)
        rows.append(
            {
                "label": label,
                "value": format_default_value(constant_name, value, unit),
            }
        )
    return rows


def extract_platform_version(source_path: Path | None) -> str:
    if source_path is None:
        return "bundled"

    for symbol in ("__version__", "VERSION"):
        try:
            value = extract_named_literal(source_path, symbol)
        except Exception:
            continue
        version = str(value or "").strip()
        if version:
            return version

    return "unknown"


def extract_platform_settings(
    source_path: Path | None,
    *,
    surface_kind: str = "portal",
) -> tuple[str, list[dict[str, str]], bool]:
    if source_path is None:
        return ("WebUI modules", [], False)
    kind = str(surface_kind or "portal").strip().lower()
    settings_symbol = "CORE_SETTINGS" if kind == "core" else "PORTAL_SETTINGS"
    default_category = "Core settings" if kind == "core" else "Portal settings"

    try:
        settings = extract_named_literal(source_path, settings_symbol)
    except Exception:
        return (default_category, [], False)

    if not isinstance(settings, dict):
        return (default_category, [], False)
    category = str(settings.get("category") or default_category).strip()
    category = category.replace("Platform Settings", "Core Settings" if kind == "core" else "Portal Settings")
    category = category.replace("platform settings", "core settings" if kind == "core" else "portal settings")
    required = settings.get("required") if isinstance(settings.get("required"), dict) else {}
    return (category, normalize_required_settings(required), True)


def build_platforms(
    plugins: list[dict[str, Any]],
    *,
    docs_order: list[str],
    surface_kind: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for slug in docs_order:
        meta = PLATFORM_DOCS[slug]
        category, settings, has_settings_schema = extract_platform_settings(
            meta.get("source"),
            surface_kind=surface_kind,
        )
        surface = str(meta.get("plugin_surface") or "").strip().lower()
        matching_plugins = [plugin for plugin in plugins if surface and surface in plugin["platforms"]]
        rows.append(
            {
                "slug": slug,
                "surface_kind": surface_kind,
                "title": meta["label"],
                "description": meta["description"],
                "role": meta["role"],
                "version": extract_platform_version(meta.get("source")),
                "highlights": list(meta.get("highlights") or []),
                "companions": list(meta.get("companions") or []),
                "companions_eyebrow": str(meta.get("companions_eyebrow") or ""),
                "companions_title": str(meta.get("companions_title") or ""),
                "companions_intro": str(meta.get("companions_intro") or ""),
                "guides": list(meta.get("guides") or []),
                "guides_eyebrow": str(meta.get("guides_eyebrow") or ""),
                "guides_title": str(meta.get("guides_title") or ""),
                "guides_intro": str(meta.get("guides_intro") or ""),
                "apis": list(meta.get("apis") or []),
                "settings_category": category,
                "settings": settings,
                "setting_count": len(settings),
                "has_settings_schema": has_settings_schema,
                "plugin_surface": surface,
                "plugin_count": len(matching_plugins),
                "plugin_examples": matching_plugins[:6],
                "source_path": str(meta.get("source") or ""),
                **{
                    key: meta.get(key)
                    for key in (
                        "hero_eyebrow",
                        "hero_panel_eyebrow",
                        "hero_panel_text",
                        "role_eyebrow",
                        "role_title",
                        "role_text",
                        "highlights_eyebrow",
                        "highlights_title",
                        "plugin_eyebrow",
                        "plugin_title",
                        "settings_eyebrow",
                        "settings_title",
                    )
                    if meta.get(key)
                },
            }
        )
    return rows


def format_default_value(constant_name: str, value: Any, unit: str) -> str:
    if unit and isinstance(value, (int, float)):
        return f"{int(value)} {unit}"
    if isinstance(value, (int, float)):
        return str(int(value))
    return str(value)


def prefix(depth: int) -> str:
    return "../" * depth


def escape(text: Any) -> str:
    return html.escape(str(text or ""), quote=True)


def page_template(*, title: str, description: str, body: str, depth: int, nav_key: str) -> str:
    base = prefix(depth)

    def nav_link(key: str, label: str, href: str, class_name: str = "nav-link", external: bool = False) -> str:
        active_class = " is-active" if key == nav_key else ""
        external_attrs = ' target="_blank" rel="noreferrer"' if external else ""
        return f'<a class="{escape(class_name)}{active_class}" href="{escape(href)}"{external_attrs}>{escape(label)}</a>'

    primary_nav = [
        ("install", "Install Tater", f"{base}install/index.html"),
        ("esphome", "Tater Voice", f"{base}tater-voice/index.html"),
        ("usb-flasher", "USB Flasher", f"{base}usb-flasher/index.html"),
    ]
    nav_groups = [
        (
            "Start",
            [
                ("home", "Home", f"{base}index.html"),
                ("spud-hub", "Spud Hub", f"{base}spud-hub/index.html"),
                ("github", "GitHub", "https://github.com/TaterTotterson/Tater"),
            ],
        ),
        (
            "Build",
            [
                ("cerberus", "Hydra", f"{base}cerberus/index.html"),
                ("spudex", "Spudex", f"{base}spudex/index.html"),
                ("llms", "LLMs", f"{base}llms/index.html"),
                ("api", "API", f"{base}api/index.html"),
            ],
        ),
        (
            "Connect",
            [
                ("portals", "Portals", f"{base}portals/index.html"),
                ("integrations", "Integrations", f"{base}integrations/index.html"),
                ("cores", "Cores", f"{base}cores/index.html"),
                ("kernel", "Kernel Tools", f"{base}kernel-tools/index.html"),
                ("plugins", "Verbas", f"{base}plugins/index.html"),
            ],
        ),
    ]
    primary_html = "\n".join(
        nav_link(key, label, href, "nav-link nav-link-primary")
        for key, label, href in primary_nav
    )
    group_html = "\n".join(
        textwrap.dedent(
            f"""\
            <section class="nav-group" aria-label="{escape(group_label)}">
              <span class="nav-group-label">{escape(group_label)}</span>
              <div class="nav-group-links">
                {chr(10).join(nav_link(key, label, href, "nav-link nav-link-github" if key == "github" else "nav-link", key == "github") for key, label, href in links)}
              </div>
            </section>"""
        )
        for group_label, links in nav_groups
    )
    nav_html = f"""
                <div class="nav-primary">
                  {primary_html}
                </div>
                <div class="nav-groups">
                  {group_html}
                </div>"""
    return textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <meta name="description" content="{escape(description)}">
          <meta name="theme-color" content="#151515">
          <meta property="og:type" content="website">
          <meta property="og:title" content="{escape(title)}">
          <meta property="og:description" content="{escape(description)}">
          <meta property="og:image" content="https://taterassistant.com/assets/images/tater-logo-primary.png">
          <meta name="twitter:card" content="summary_large_image">
          <title>{escape(title)}</title>
          <link rel="icon" href="{base}assets/images/tater-logo-primary.png">
          <link rel="stylesheet" href="{base}assets/site.css">
          <script src="{base}assets/site.js" defer></script>
        </head>
        <body data-page="{escape(nav_key)}">
          <div class="page-shell">
            <header class="site-header">
              <a class="brand" href="{base}index.html" aria-label="Tater Assistant home">
                <img class="brand-wordmark" src="{base}assets/images/tater-logo-primary.png" alt="Tater Assistant">
                <span class="brand-pill">Docs</span>
              </a>
              <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
              <nav class="site-nav" id="site-nav">
                {nav_html}
              </nav>
            </header>
            <main class="page-main">
              {body}
            </main>
            <footer class="page-footer">
              <div class="footer-row">
                <p>Generated from current Tater, Tater Shop, and Tater Integrations source.</p>
                <a class="footer-contact" href="mailto:tater@tatertottersonai.com?subject=Tater%20Assistant%20contact" data-contact-open>Contact us</a>
              </div>
            </footer>
          </div>
        </body>
        </html>
        """
    )


def chip(text: str) -> str:
    return f'<span class="chip">{escape(text)}</span>'


def button(label: str, href: str, ghost: bool = False) -> str:
    class_name = "button button-ghost" if ghost else "button"
    return f'<a class="{class_name}" href="{href}">{escape(label)}</a>'


def format_bytes(value: int) -> str:
    size = float(max(0, int(value or 0)))
    units = ["B", "KB", "MB", "GB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{int(value or 0)} B"


def version_key(value: str) -> tuple[int, ...]:
    parts = [int(part) for part in re.findall(r"\d+", str(value or ""))]
    return tuple(parts or [0])


def load_release_notes_summary() -> dict[str, str]:
    notes_path = TATER_DIR / "macos" / "Tater" / "RELEASE_NOTES.md"
    try:
        notes_text = notes_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    match = re.search(r"^#\s+Tater\s+v?([0-9]+(?:\.[0-9]+)*)\s*$", notes_text, flags=re.MULTILINE)
    if not match:
        return {}

    summary = ""
    remainder = notes_text[match.end() :].strip()
    for paragraph in re.split(r"\n\s*\n", remainder):
        candidate = " ".join(line.strip() for line in paragraph.splitlines()).strip()
        if candidate and not candidate.startswith(("#", "-")):
            summary = candidate
            break

    return {"version": match.group(1), "summary": summary}


def load_macos_release() -> dict[str, str]:
    manifest_path = TATER_DIR / "macos" / "Tater" / "update-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        manifest = {}
    if not isinstance(manifest, dict):
        manifest = {}

    version = str(manifest.get("version") or "").strip()
    build = str(manifest.get("build") or "").strip()
    zip_url = str(manifest.get("url") or "").strip()
    sha256 = str(manifest.get("sha256") or "").strip()
    notes = str(manifest.get("notes") or "").strip()
    release_notes = load_release_notes_summary()
    notes_version = release_notes.get("version", "")
    if notes_version and version_key(notes_version) > version_key(version):
        version = notes_version
        build = ""
        version_tag = f"v{version}"
        zip_url = f"https://github.com/TaterTotterson/Tater/releases/download/{version_tag}/Tater-{version_tag}.zip"
        sha256 = ""
        notes = release_notes.get("summary", "")

    if not version:
        return {}

    version_label = version if version.lower().startswith("v") else f"v{version}"
    if not zip_url:
        zip_url = f"https://github.com/TaterTotterson/Tater/releases/download/{version_label}/Tater-{version_label}.zip"
    dmg_url = zip_url[:-4] + ".dmg" if zip_url.lower().endswith(".zip") else zip_url
    dmg_path = manifest_path.parent / "releases" / f"Tater-{version_label}.dmg"
    zip_path = manifest_path.parent / "releases" / f"Tater-{version_label}.zip"
    dmg_size = format_bytes(dmg_path.stat().st_size) if dmg_path.exists() else ""
    zip_size = format_bytes(zip_path.stat().st_size) if zip_path.exists() else ""

    return {
        "version": version,
        "version_label": version_label,
        "build": build,
        "zip_url": zip_url,
        "dmg_url": dmg_url,
        "sha256": sha256,
        "notes": notes,
        "dmg_size": dmg_size,
        "zip_size": zip_size,
    }


def render_macos_release_card() -> str:
    release = load_macos_release()
    if not release:
        return ""
    version_label = release["version_label"]
    build = release.get("build") or ""
    dmg_size = release.get("dmg_size") or ""
    notes = release.get("notes") or f"Tater macOS release {version_label}."
    note_label = "macOS package note" if "macos" in notes.lower() else "Release note"
    sha_short = release.get("sha256", "")[:12]
    release_chips = "".join(
        chip(item)
        for item in [
            f"Release {version_label}",
            f"Build {build}" if build else "",
            dmg_size,
            "5 install paths",
        ]
        if item
    )
    release_url = f"https://github.com/TaterTotterson/Tater/releases/tag/{version_label}"

    return f"""
    <section class="release-card" aria-label="Current Tater release, install paths, and companion apps">
      <aside class="release-visual" aria-hidden="true">
        <img class="release-mascot" src="assets/images/tater-mascot-excited-pointer.png" alt="">
      </aside>
      <div class="release-copy">
        <span class="eyebrow">Current Tater release</span>
        <h2>Install Tater {escape(version_label)} your way.</h2>
        <p>
          Tater runs as the same assistant stack whether you use the native macOS app,
          install from source, run Docker, or set it up through Home Assistant or Unraid.
        </p>
        <p>
          The macOS download is the quick desktop route with a menu bar app,
          private runtime, first-run setup, and automatic update checks. The install
          guide covers every supported server path.
        </p>
        <p><strong>{escape(note_label)}:</strong> {escape(notes)}</p>
        <div class="chip-row">
          {release_chips}
        </div>
        <div class="action-row release-actions">
          <a class="button" href="{escape(release['dmg_url'])}" target="_blank" rel="noreferrer">Download macOS app</a>
          <a class="button button-ghost" href="install/index.html#server-install-paths">Compare install paths</a>
          <a class="button button-ghost" href="{escape(release_url)}" target="_blank" rel="noreferrer">Release notes</a>
        </div>
        <div class="little-spud-attach">
          <div class="little-spud-copy">
            <span class="little-spud-title">Little Spud</span>
            <span class="little-spud-kicker">iPhone + iPad + Android companion</span>
            <p>Pair by QR code, chat with your private Tater, control your Home and Music Core, use voice and TTS, and open notification snapshots or video clips.</p>
            <div class="chip-row">
              {chip("iOS + Android")}
              {chip("Chat + voice")}
              {chip("Home + Music")}
            </div>
          </div>
          <div class="little-spud-store-links" aria-label="Download Little Spud">
            <a class="store-badge store-badge-apple" href="https://apps.apple.com/app/little-spud/id6781400718" target="_blank" rel="noreferrer" aria-label="Download Little Spud on the App Store">
              <span class="store-badge-platform" aria-hidden="true">iOS</span>
              <span class="store-badge-copy"><small>Download on the</small><strong>App Store</strong></span>
            </a>
            <a class="store-badge store-badge-play" href="https://play.google.com/store/apps/details?id=com.tatertotterson.littlespud.android" target="_blank" rel="noreferrer" aria-label="Get Little Spud on Google Play">
              <span class="store-badge-platform" aria-hidden="true">Play</span>
              <span class="store-badge-copy"><small>Get it on</small><strong>Google Play</strong></span>
            </a>
          </div>
        </div>
        <small class="release-meta">Pulled from the current Tater release source{escape(f" • SHA {sha_short}" if sha_short else "")}.</small>
      </div>
    </section>
    """


def render_platform_badges(platforms: list[str]) -> str:
    visible_platforms = clean_platforms(platforms)
    if not visible_platforms:
        return '<span class="chip">No portals listed</span>'
    return "".join(chip(PLATFORM_META.get(name, {"label": name.replace("_", " ").title()})["label"]) for name in visible_platforms)


def platform_settings_chip(platform: dict[str, Any]) -> str:
    if platform["slug"] == "webui":
        return "Configured in app"
    if platform["slug"] == "esphome":
        return "Settings -> Voice"
    if platform.get("has_settings_schema"):
        if int(platform["setting_count"]) == 0:
            return "No required fields"
        return f"{int(platform['setting_count'])} settings"
    return "No settings form"


def platform_runtime_chip(platform: dict[str, Any]) -> str:
    if platform["slug"] == "esphome":
        return "Voice device runtime"
    if int(platform["plugin_count"]) > 0:
        return f"{platform['plugin_count']} Verbas"
    if platform["slug"] == "macos":
        return "Desktop portal"
    if platform["slug"] == "ai_task":
        return "Scheduler runtime"
    if platform["slug"] == "awareness":
        return "Awareness engine"
    if platform["slug"] == "memory":
        return "Memory service"
    if platform["slug"] == "personal":
        return "Email intelligence"
    if platform["slug"] == "rss":
        return "Feed watcher"
    return "Internal runtime"


def platform_version_chip(platform: dict[str, Any]) -> str:
    version = str(platform.get("version") or "").strip()
    if not version or version.lower() == "unknown":
        return "Version unknown"
    if version.lower() == "bundled":
        return "Bundled"
    return f"v{version}"


def platform_settings_text(platform: dict[str, Any]) -> str:
    surface_kind = str(platform.get("surface_kind") or "portal").strip().lower()
    settings_symbol = "CORE_SETTINGS" if surface_kind == "core" else "PORTAL_SETTINGS"
    surface_label = "core" if surface_kind == "core" else ("runtime" if platform["slug"] == "esphome" else "portal")
    if platform["slug"] == "webui":
        return (
            "The WebUI is itself the configuration portal, so this page documents behavior and role rather than "
            f"a separate {settings_symbol} form."
        )
    if platform["slug"] == "ai_task":
        return (
            "The scheduler declares a settings block, but it does not currently require explicit fields. "
            "Its behavior is driven by scheduled task data, targets, and notifier routing."
        )
    if platform["slug"] == "esphome":
        return (
            "Tater Voice is configured through Settings -> Voice, with separate Satellites, Firmware, Stereo Pairs, Stats, and Settings tabs. "
            "Each satellite owns its local microWakeWord profile, room, playback, brightness, and supported live controls, while shared STT/TTS and SpeechBrain choices live in Settings -> Models. "
            "Prebuilt OTA and Browser USB firmware, secure trainer pairing, wake verification, intercom, persistent statistics, and live logs are managed from the same local UI."
        )
    if platform.get("has_settings_schema"):
        return (
            f"This {surface_label} declares a {settings_symbol} schema, but it does not currently require any explicit fields."
        )
    return (
        f"This {surface_label} does not expose a standalone {settings_symbol} form in the current source snapshot."
    )


def platform_plugin_text(platform: dict[str, Any]) -> str:
    if platform["slug"] == "macos":
        return (
            "macOS is a desktop portal used by the Tater Menu app on the main Tater port. It can execute compatible Verbas "
            "through /macos/plugin even when plugin inventory tags for macos are sparse."
        )
    if platform["slug"] == "esphome":
        return (
            "Tater Voice is a built-in runtime surface. Verbas advertise speaking-device support through the voice_core platform tag, which Tater maps onto trusted Person and room context, native satellite identity, playback routing, stereo/intercom targets, and follow-up mic handling."
        )
    if platform["slug"] == "ai_task":
        return (
            "AI Task Runner is a scheduler core. It executes scheduled prompts and routes results through notifier "
            "portals rather than acting as a direct Verba target."
        )
    if platform["slug"] == "memory":
        return (
            "Memory Core is background infrastructure. It scans chat history, extracts durable facts, and injects "
            "memory context back into Hydra instead of acting like a direct Verba surface."
        )
    if platform["slug"] == "personal":
        return (
            "Personal Core is background email intelligence. It scans connected inboxes, extracts structured profile "
            "signals, and exposes personal kernel tools plus optional prompt-context injection rather than acting like a direct Verba surface."
        )
    if platform["slug"] == "rss":
        return (
            "RSS is a background feed watcher. It polls feeds, summarizes content, and dispatches updates through "
            "notifier portals rather than serving as a direct Verba target."
        )
    return (
        "This runtime component mainly handles orchestration rather than exposing its own direct Verba target."
    )


def plugin_arguments_text(plugin: dict[str, Any]) -> str:
    return (
        "This Verba does not require named arguments in its published usage example. Hydra usually triggers "
        "it directly from the user's request or from recent conversation context."
    )


def plugin_settings_text(plugin: dict[str, Any]) -> str:
    return (
        "This Verba does not declare plugin-specific settings in its metadata. Any dependencies are handled "
        "through portal config, environment variables, or the backing service itself."
    )


def render_home_page(
    plugins: list[dict[str, Any]],
    kernel_tools: list[dict[str, Any]],
    portals: list[dict[str, Any]],
    cores: list[dict[str, Any]],
    integrations: list[dict[str, Any]],
) -> str:
    plugin_count = len(plugins)
    kernel_count = len(kernel_tools)
    portal_count = len(portals)
    integration_count = len(integrations)
    install_count = len(INSTALL_METHODS)

    hero = f"""
    <section class="hero hero-home">
      <div class="hero-copy">
        <span class="eyebrow">Local AI, throughout your home</span>
        <h1>One private assistant for every room.</h1>
        <p>
          Talk from a Tater satellite, the WebUI, Little Spud, or your favorite chat portal.
          Tater carries the right Person, room, devices, music, memory, and permissions into every turn.
        </p>
        <div class="action-row">
          {button("Install Tater", "install/index.html")}
          {button("Explore Music Core", "cores/music.html")}
          {button("Meet Tater Voice", "tater-voice/index.html")}
          {button("Browse all docs", "cores/index.html", ghost=True)}
        </div>
      </div>
      <aside class="hero-art mascot-stage">
        <img class="hero-wordmark" src="assets/images/tater-logo-primary.png" alt="Tater Assistant">
        <img class="mascot mascot-wave" src="assets/images/tater-mascot-wave.png" alt="" aria-hidden="true">
      </aside>
      <div class="hero-stats" aria-label="Tater documentation counts">
        <div class="stat-card"><strong>{plugin_count}</strong><span>documented Verbas</span></div>
        <div class="stat-card"><strong>{kernel_count}</strong><span>kernel tools</span></div>
        <div class="stat-card"><strong>{portal_count}</strong><span>portals</span></div>
        <div class="stat-card"><strong>{integration_count}</strong><span>integrations</span></div>
        <div class="stat-card"><strong>{install_count}</strong><span>install paths</span></div>
      </div>
    </section>
    """

    macos_release = render_macos_release_card()

    mascot_intro = """
    <section class="section mascot-band">
      <div class="mascot-band-copy">
        <span class="eyebrow">Tater today</span>
        <h2>Private AI, a whole-home music player, and one polished local control center.</h2>
        <p>
          The current Tater brings voice, media, devices, automations, people, cores,
          and live system work together without turning the WebUI into a collection of separate apps.
        </p>
        <ul class="stack-list">
          <li>Pair Music Core with Tater Tube Server, then browse your Tater Tube library and play it in a room, stereo pair, synchronized satellite group, Sonos zone, AirPlay destination, or supported media-player output.</li>
          <li>Use the locally bundled Vue WebUI for the Dashboard, Chat, Music, Integrations, Verbas, Portals, Cores, Spudex, Voice, Settings, and live runtime state.</li>
          <li>Pair Tater Native satellites securely, run microWakeWord on-device, verify wakes with fast STT, and keep 30 days of voice statistics in Redis.</li>
          <li>Let cached System Tasks refresh devices, satellites, models, hardware, Dashboard briefs, recommendations, memory, security, feeds, and other Core work in the background.</li>
          <li>Control devices through one room- and alias-aware Device Control Verba, with dedicated Camera Control and Reachy Vision for current visual questions.</li>
        </ul>
        <div class="action-row">
          <a class="button" href="https://github.com/TaterTotterson/Tater/releases" target="_blank" rel="noreferrer">Latest releases</a>
          <a class="button button-ghost" href="tater-voice/index.html">Voice docs</a>
        </div>
      </div>
      <img class="mascot mascot-present" src="assets/images/tater-mascot-present.png" alt="" aria-hidden="true">
    </section>
    """

    spotlight_cards = [
        (
            "Private local speech",
            "Run experimental Qwen3-ASR locally for speech recognition, then answer with managed Qwen3-TTS, OmniVoice, Pocket TTS, or another configured voice backend.",
        ),
        (
            "Audio + video understanding",
            "Give audio files and short video clips to dedicated understanding models while camera events return playable clips with clean snapshot previews.",
        ),
        (
            "Face ID + People",
            "Keep face matching private, link recognized identities to Tater People, and use recent camera context in Awareness and Automation flows.",
        ),
        (
            "A clearer model workspace",
            "Browse Hugging Face models from the Models screen and configure MTP, DFlash, or DSpark speculative decoding with task-aware downloads and runtime status.",
        ),
        (
            "Music and voice stay together",
            "Readable speaker cards, persistent volume, synchronized targets, and stereo TTS overlays keep music playing at the intended level before, during, and after replies.",
        ),
        (
            "Satellites stay in sync",
            "Compact WebUI volume controls and physical satellite buttons share one saved level, while board-aware firmware routing keeps production and Beta.1 hardware on the right update path.",
        ),
    ]
    spotlight_html = "".join(
        f"""
        <article class="feature-card feature-card-spotlight">
          <span class="card-index">{index:02d}</span>
          <h3>{escape(title)}</h3>
          <p>{escape(text)}</p>
        </article>
        """
        for index, (title, text) in enumerate(spotlight_cards, start=1)
    )

    feature_cards = [
        (
            "Local-first by design",
            "Tater, its modern WebUI, enabled cores, speech models, and device state run on the system you control, with local command-line, Docker, Home Assistant, Unraid, and macOS paths.",
        ),
        (
            "Modular integrations",
            "Integrations live in Tater_Integrations and download only when enabled, so new providers can expose devices, actions, and web search without editing Tater core.",
        ),
        (
            "Capability-driven devices",
            "Cores can ask for all cameras, speakers, garage doors, sensors, lights, weather sources, or search providers across every enabled integration.",
        ),
        (
            "Search provider choice",
            "search_web can use enabled providers such as SearXNG, Brave Search, Google Custom Search, or Serper instead of one baked-in backend.",
        ),
        (
            "Smart chaining",
            "Hydra breaks work into steps, picks the next tool, and keeps going until the task is done.",
        ),
        (
            "Spudex terminal workbench",
            "Spudex gives Tater a console-style tab for direct assistant chat, manual commands, tracked sessions, policy controls, and Hydra-accessible terminal tools.",
        ),
        (
            "Guardian Core",
            "Guardian watches network inventory, source health, posture scoring, AI findings, device trust, watch checks, and guided security confirmations from a dark Tater-themed UI.",
        ),
        (
            "Fast, cached Dashboard",
            "The default Dashboard uses background snapshots and masonry sections for health, environment imagery, awareness events, voice devices, Speaker ID, and Emotion ID without blocking page load.",
        ),
        (
            "Tater Voice",
            "Tater Voice is built into Tater, powering paired native satellites with local microWakeWord, trusted room context, intercom, wake arbitration, live controls, reply routing, logs, and native operator screens.",
        ),
        (
            "Tater S3Box displays",
            "ESP32-S3-BOX-3 displays can run a Tater LVGL firmware with sensor bubbles, weather history bars, voice states, tool-call visuals, and camera snapshot notifications.",
        ),
        (
            "Firmware recovery",
            "The Voice firmware tab matches prebuilt signed images by board and revision, then supports OTA, Browser USB, live logs, and safe-mode recovery without a local compile.",
        ),
        (
            "Voice identity and tone",
            "Speaker ID and Emotion ID can warm SpeechBrain models, detect enrolled speakers or tone, and pass useful context into voice turns.",
        ),
        (
            "People identity layer",
            "Settings -> People creates master users that link portal accounts and Tater Voice identities, with scoped per-person response instructions.",
        ),
        (
            "Display notifications",
            "Tater apps and cores can publish display events with text, images, snapshots, and tool-progress metadata to targeted Tater Voice screens.",
        ),
        (
            "Local wake and intercom",
            "Satellites run microWakeWord locally with built-in, catalog, or securely trainer-published models, while intercom can target individual devices, rooms, stereo pairs, or broader groups.",
        ),
        (
            "Environment-aware sensors",
            "Environment Core supplies normalized readings for displays and dashboard briefs, including Ecowitt rain, Ecobee remote sensors, and Fahrenheit/Celsius conversion.",
        ),
        (
            "Local LLMs and vision",
            "Tater can run Base, Hydra, and vision models through llama.cpp GGUF, Hugging Face Transformers, and MLX Engine, with runtime tuning, chat templates, and live debug output.",
        ),
        (
            "OpenAI-compatible API",
            "External apps can call Tater through /v1/models and /v1/chat/completions in Direct or Hydra mode, protected by a local API key.",
        ),
        (
            "Hugging Face integration",
            "A saved Hugging Face token can be injected into model download environments for private, gated, or higher-rate model pulls.",
        ),
        (
            "Beast Mode routing",
            "Base servers can run normal AI calls while Chat/Astraeus/Thanatos/Minos/Hermes optionally route to per-head models.",
        ),
        (
            "Redis control + encryption",
            "Redis setup, connectivity checks, live encrypt/decrypt controls, persistent voice statistics, and runtime caches are managed directly in WebUI settings.",
        ),
        (
            "API key protection",
            "Portal routes on the main Tater port can be locked behind X-Tater-Token so companion apps and integrations use shared API keys.",
        ),
        (
            "Core layer",
            "Downloadable cores add automation, awareness, environment, Guardian, memory, music, personal intelligence, RSS, scheduling, and Tater Tube without bloating the base runtime.",
        ),
        (
            "Verbas",
            "Actions speak louder than words. Standalone Verbas extend Tater into smart-home, media, camera, vision, note, download, and admin workflows.",
        ),
    ]
    feature_html = "".join(
        f"""
        <article class="feature-card">
          <h3>{escape(title)}</h3>
          <p>{escape(text)}</p>
        </article>
        """
        for title, text in feature_cards
    )

    home_cores = list(cores)
    featured_integration_slugs = {
        "homeassistant",
        "hue",
        "shelly",
        "sonos",
        "unifi_network",
        "unifi_protect",
        "weather_api",
    }
    home_integrations = [
        integration
        for integration in integrations
        if integration.get("slug") in featured_integration_slugs
    ]

    portal_cards = "".join(
        f"""
        <article class="platform-card">
          <div class="chip-row">
            {chip(platform['role'])}
            {chip(platform_version_chip(platform))}
            {chip(platform_settings_chip(platform))}
          </div>
          <h3>{escape(platform['title'])}</h3>
          <p>{escape(platform['description'])}</p>
          <div class="plugin-links">
            {button("Read portal page", f"portals/{platform['slug']}.html", ghost=True)}
          </div>
        </article>
        """
        for platform in portals
    )

    core_cards = "".join(
        f"""
        <article class="platform-card">
          <div class="chip-row">
            {chip(platform['role'])}
            {chip(platform_version_chip(platform))}
            {chip(platform_settings_chip(platform))}
          </div>
          <h3>{escape(platform['title'])}</h3>
          <p>{escape(platform['description'])}</p>
          <div class="plugin-links">
            {button("Read core page", f"cores/{platform['slug']}.html", ghost=True)}
          </div>
        </article>
        """
        for platform in home_cores
    )

    integration_cards = "".join(
        f"""
        <article class="platform-card">
          <div class="chip-row">
            {chip(integration['category'])}
            {chip(f"v{integration['version']}")}
            {chip("Optional" if not integration.get("required") else "Required")}
          </div>
          <h3>{escape(integration['title'])}</h3>
          <p>{escape(integration['summary'])}</p>
          <div class="plugin-links">
            {button("Read integration page", f"integrations/{integration['slug']}.html", ghost=True)}
          </div>
        </article>
        """
        for integration in home_integrations
    )

    page_links = f"""
    <div class="grid grid-3">
      <article class="panel">
        <h3>Overview</h3>
        <p>Start with the core story and the docs map.</p>
        {button("Stay here", "index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Install docs</h3>
        <p>Unraid, Home Assistant, local Python, and Docker.</p>
        {button("Open install guide", "install/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Portal docs</h3>
        <p>See every portal, its role, and its settings.</p>
        {button("Open portals", "portals/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Integration docs</h3>
        <p>Browse optional downloaded integrations, device capabilities, and search providers.</p>
        {button("Open integrations", "integrations/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Tater Voice</h3>
        <p>Built-in voice runtime docs for satellites, live entities, and playback flows.</p>
        {button("Open Tater Voice", "tater-voice/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Local LLMs</h3>
        <p>Model downloads, llama.cpp, Transformers, MLX Engine, vision, runtime tuning, chat templates, and live LLM debug tools.</p>
        {button("Open LLM docs", "llms/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>OpenAI API</h3>
        <p>Use Tater from external apps through /v1/models and /v1/chat/completions in Direct or Hydra mode.</p>
        {button("Open API docs", "api/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Spudex</h3>
        <p>Open the terminal workbench docs for direct chat, controlled commands, sessions, policy, and Hydra tools.</p>
        {button("Open Spudex", "spudex/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Core docs</h3>
        <p>Automation, awareness, environment, Guardian, scheduling, memory, music, personal intelligence, RSS, and Tater Tube.</p>
        {button("Open cores", "cores/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Hydra core</h3>
        <p>Astraeus -> Thanatos -> Minos -> Hermes loop, Beast Mode routing, and guardrails.</p>
        {button("Open Hydra", "cerberus/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Tools + Verbas</h3>
        <p>Browse built-in tools and the current Verba snapshot.</p>
        {button("Open Verbas", "plugins/index.html", ghost=True)}
      </article>
    </div>
    """

    screenshot = """
    <div class="showcase-grid">
      <div class="panel panel-tight">
        <span class="eyebrow">The local control center</span>
        <h2>One UI for the whole assistant.</h2>
        <p>
          Dashboard, Chat, Music, Integrations, Verbas, Portals, Cores, Spudex,
          Voice, Settings, System Tasks, and runtime telemetry now share one
          responsive orange-and-gray interface bundled with Tater itself.
        </p>
        <div class="chip-row">
          <span class="chip">Vue 3 + TypeScript</span>
          <span class="chip">Local assets</span>
          <span class="chip">Live updates</span>
          <span class="chip">No forced refresh</span>
        </div>
      </div>
      <div class="webui-preview" aria-label="Stylized preview of Tater's current local WebUI">
        <div class="webui-preview-sidebar">
          <div class="webui-preview-brand"><span class="webui-preview-mark">+</span><strong>Tater</strong></div>
          <span class="webui-preview-nav is-active">Dashboard</span>
          <span class="webui-preview-nav">Chat</span>
          <span class="webui-preview-nav">Music</span>
          <span class="webui-preview-nav">Integrations</span>
          <span class="webui-preview-nav">Voice</span>
          <span class="webui-preview-version">Installed build</span>
        </div>
        <div class="webui-preview-main">
          <div class="webui-preview-topline"><span>Dashboard</span><span class="webui-preview-status">Systems healthy</span></div>
          <div class="webui-preview-grid">
            <div class="webui-preview-card webui-preview-card-wide">
              <span class="webui-preview-label">Now playing · Family Room</span>
              <strong>Tater Recommendations</strong>
              <div class="webui-preview-wave"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
            </div>
            <div class="webui-preview-card"><span class="webui-preview-label">Voice</span><strong>8 satellites</strong><small>Office Stereo ready</small></div>
            <div class="webui-preview-card"><span class="webui-preview-label">System Tasks</span><strong>All caught up</strong><small>Next refresh in 3m</small></div>
            <div class="webui-preview-card webui-preview-card-wide"><span class="webui-preview-label">Home</span><strong>Devices, people, rooms, and cores</strong><small>Live local state without page reloads</small></div>
          </div>
        </div>
      </div>
    </div>
    """

    music_showcase = """
    <section class="section product-story">
      <div class="product-story-copy">
        <span class="eyebrow">Music Core</span>
        <h2>Your library. The right room. Still playing after Tater speaks.</h2>
        <p>
          Ask for an album, artist, genre, song, or recommendation and let room context choose the destination.
          The same live player stays available for browsing, queue changes, speaker selection, and synchronized volume.
        </p>
        <div class="chip-row">
          <span class="chip">Tater Tube Server</span>
          <span class="chip">Tater Native</span>
          <span class="chip">Stereo pairs</span>
          <span class="chip">Sonos</span>
          <span class="chip">AirPlay</span>
          <span class="chip">Tater Tube audio</span>
        </div>
        <div class="action-row">
          <a class="button" href="cores/music.html">Read Music Core</a>
          <a class="button button-ghost" href="tater-voice/index.html">Stereo + voice</a>
        </div>
      </div>
      <div class="music-stage" aria-label="Decorative Tater Music player preview">
        <img class="mascot mascot-music" src="assets/images/tater-mascot-sit.png" alt="" aria-hidden="true">
        <div class="music-player-demo">
          <div class="music-now-playing">
            <span class="music-kicker">Now playing · Family Room</span>
            <strong>Whole-home, your way</strong>
            <span>Tater Recommendations</span>
          </div>
          <div class="music-controls" aria-hidden="true">
            <span>−</span><span>‹</span><span class="music-play">▶</span><span>›</span><span>＋</span>
          </div>
          <div class="music-destinations">
            <span>Office Stereo</span><span>Family Room Sonos</span><span>Kitchen Sat</span>
          </div>
        </div>
      </div>
    </section>
    """

    body = f"""
    {hero}
    {macos_release}
    <section class="section">
      <div class="section-head section-head-wide">
        <span class="eyebrow">Latest in Tater</span>
        <h2>Local voice, media, models, and multi-room playback keep getting better.</h2>
        <p>A compact look at the most useful additions from the latest Tater releases.</p>
      </div>
      <div class="grid spotlight-grid">
        {spotlight_html}
      </div>
    </section>
    {music_showcase}
    {mascot_intro}
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">What Tater does</span>
        <h2>Tater plans, acts, and connects across your stack.</h2>
      </div>
      <div class="grid capability-grid">
        {feature_html}
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Portals + integrations + cores</span>
        <h2>One assistant. Verbas, portals, integrations, and cores.</h2>
      </div>
      <h3>Portals</h3>
      <div class="grid grid-3">
        {portal_cards}
      </div>
      <h3>Integrations</h3>
      <div class="grid grid-3">
        {integration_cards}
      </div>
      <h3>Cores</h3>
      <div class="grid grid-3">
        {core_cards}
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Documentation map</span>
        <h2>Start broad, then drill into the details.</h2>
      </div>
      {page_links}
    </section>
    <section class="section">
      {screenshot}
    </section>
    """
    return page_template(
        title="Tater | Home",
        description="Meet Tater Assistant: private local AI with room-aware voice, Music Core, stereo pairs, multi-room playback, smart-home control, and a modern local WebUI.",
        body=body,
        depth=0,
        nav_key="home",
    )


def render_usb_flasher_page() -> str:
    body = """
    <section class="hero hero-subpage usb-flasher-hero">
      <div class="hero-copy">
        <span class="eyebrow">Tater Browser USB</span>
        <h1>Flash a Tater satellite from this browser.</h1>
        <p>
          Select your satellite, connect it over USB, and install the latest official firmware
          directly from this secure Tater page. No firmware files to find or upload.
        </p>
        <div class="chip-row">
          <span class="chip">Chrome or Edge</span>
          <span class="chip">ESP32-S3 satellites</span>
          <span class="chip">Factory + keep settings</span>
        </div>
      </div>
      <aside class="panel hero-panel usb-flasher-hero-panel">
        <img
          class="usb-flasher-mascot"
          src="../assets/images/tater-mascot-firmware-flasher.png"
          alt="Tater holding a USB cable and presenting a glowing firmware chip"
          width="1536"
          height="1024"
        >
        <div class="usb-flasher-hero-overlay">
          <div class="usb-flasher-hero-copy">
            <span class="eyebrow">Firmware, the Tater way</span>
            <h2>Plug in. Pick your sat. Flash.</h2>
            <p>Use a data-capable USB cable and connect one satellite at a time.</p>
          </div>
          <div class="usb-browser-state" data-usb-browser-state data-tone="checking">
            Checking browser USB support…
          </div>
        </div>
      </aside>
    </section>

    <section class="section" data-usb-flasher>
      <div class="section-head section-head-wide">
        <div>
          <span class="eyebrow">Tater USB Flasher</span>
          <h2>Select the satellite, choose how to install it, then connect.</h2>
        </div>
        <p>Tater automatically loads and verifies the correct latest firmware before anything is written.</p>
      </div>

      <div class="usb-flasher-layout">
        <div class="usb-flasher-steps">
          <article class="panel usb-flasher-step">
            <div class="usb-step-heading">
              <span class="usb-step-number">1</span>
              <div>
                <span class="eyebrow">Satellite model</span>
                <h3>Which Tater satellite is connected?</h3>
              </div>
            </div>
            <div class="usb-source-panel">
              <label class="usb-field usb-device-field">
                <span>Satellite</span>
                <select data-usb-device disabled>
                  <option value="">Loading latest firmware…</option>
                </select>
              </label>
              <div class="usb-firmware-summary" data-usb-firmware-summary>
                <strong>Loading latest firmware…</strong>
                <span>Checking the official Tater release.</span>
              </div>
              <p class="usb-inline-note">The exact firmware version and flash size are chosen automatically for this satellite.</p>
            </div>
          </article>

          <article class="panel usb-flasher-step">
            <div class="usb-step-heading">
              <span class="usb-step-number">2</span>
              <div>
                <span class="eyebrow">Install type</span>
                <h3>Factory install or keep settings.</h3>
              </div>
            </div>
            <div class="usb-mode-grid" role="radiogroup" aria-label="USB install type">
              <button class="usb-mode-card is-active" type="button" role="radio" aria-checked="true" data-usb-mode="factory">
                <span class="usb-mode-mark" aria-hidden="true"></span>
                <strong>Factory Install</strong>
                <small>Erases the device and installs a clean Tater image.</small>
              </button>
              <button class="usb-mode-card" type="button" role="radio" aria-checked="false" data-usb-mode="ota">
                <span class="usb-mode-mark" aria-hidden="true"></span>
                <strong>OTA · Keep Settings</strong>
                <small>Updates the app while preserving Wi-Fi, pairing, and saved settings.</small>
              </button>
            </div>
            <div class="usb-mode-warning" data-usb-mode-warning>
              Factory Install removes Wi-Fi, pairing, and saved settings. The device will need setup again afterward.
            </div>
          </article>

          <article class="panel usb-flasher-step usb-connect-step">
            <div class="usb-step-heading">
              <span class="usb-step-number">3</span>
              <div>
                <span class="eyebrow">Connect and flash</span>
                <h3>Choose the satellite’s USB port.</h3>
              </div>
            </div>
            <p class="usb-ready-summary" data-usb-ready-summary>Loading the latest official Tater firmware…</p>
            <button class="button usb-flash-button" type="button" data-usb-flash disabled>Connect &amp; Flash Latest</button>
            <p class="usb-inline-note">Chrome will show its own USB device picker. Tater cannot access any device you do not select.</p>
          </article>
        </div>

        <aside class="panel usb-flasher-console" aria-live="polite">
          <div class="usb-console-heading">
            <div>
              <span class="eyebrow">Flash status</span>
              <h3 data-usb-status-title>Ready when you are.</h3>
            </div>
            <span class="usb-status-dot" data-usb-status-dot data-tone="idle" aria-hidden="true"></span>
          </div>
          <p data-usb-status-detail>Loading the latest official Tater firmware.</p>
          <div class="usb-progress" role="progressbar" aria-label="Firmware flash progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" data-usb-progress>
            <span data-usb-progress-bar></span>
          </div>
          <div class="usb-progress-copy"><span data-usb-progress-label>Waiting</span><strong data-usb-progress-value>0%</strong></div>
          <div class="usb-console-log" data-usb-log tabindex="0">
            <div class="usb-log-line tone-info">Loading the latest Tater firmware catalog.</div>
          </div>
          <button class="button button-ghost usb-clear-log" type="button" data-usb-clear-log>Clear log</button>
        </aside>
      </div>
    </section>

    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Factory Install</span>
          <h2>Use it for recovery or a clean setup.</h2>
          <p>The complete factory image is written from address zero after the device is erased. Existing setup data will be removed.</p>
        </article>
        <article class="panel">
          <span class="eyebrow">OTA · Keep Settings</span>
          <h2>Use it for a wired update.</h2>
          <p>The application image is written to Tater’s app slots without erasing setup storage. This requires a matching Tater OTA image.</p>
        </article>
      </div>
    </section>
    <script type="module" src="../assets/usb-flasher.js"></script>
    """
    return page_template(
        title="Tater Assistant | USB Flasher",
        description="Automatically install the latest official Tater satellite firmware over USB with Factory and OTA Keep Settings modes.",
        body=body,
        depth=1,
        nav_key="usb-flasher",
    )


def render_little_spud_privacy_page() -> str:
    body = """
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Little Spud</span>
        <h1>Privacy Policy</h1>
        <p>
          Little Spud is a companion app for Tater, a local-first assistant platform.
          It is designed to connect to a Tater instance that you control.
        </p>
        <div class="chip-row">
          <span class="chip">No Little Spud cloud</span>
          <span class="chip">No ads</span>
          <span class="chip">No third-party tracking</span>
          <span class="chip">Local-first</span>
        </div>
      </div>
      <aside class="panel hero-panel">
        <span class="eyebrow">Effective date</span>
        <h2>August 23, 2026</h2>
        <p>This policy covers the Little Spud app for iOS, iPadOS, and Android.</p>
      </aside>
    </section>

    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Data we do not collect</span>
          <h2>No cloud account, ads, or analytics.</h2>
          <p>
            Little Spud does not operate a Little Spud cloud account service,
            advertising system, analytics service, or third-party tracking system.
          </p>
        </article>
        <article class="panel">
          <span class="eyebrow">On-device storage</span>
          <h2>Settings stay on your device.</h2>
          <p>
            Little Spud stores app settings on your device, including preferences
            such as notification and TTS settings. Pairing tokens for your Tater
            instance are stored using secure operating-system storage. Recent chat
            messages may be stored locally so the app can show conversation history.
          </p>
        </article>
      </div>
    </section>

    <section class="section">
      <article class="panel">
        <span class="eyebrow">Push delivery</span>
        <h2>Push services deliver a wake-up, not your private alert content.</h2>
        <p>
          If you enable push notifications, Apple Push Notification service on
          iOS and iPadOS or Firebase Cloud Messaging on Android can deliver a
          wake-up notification. Little Spud then retrieves the alert details from
          your paired Tater instance. Push registration tokens are used only to
          route those notifications and are not used for advertising or tracking.
        </p>
      </article>
    </section>

    <section class="section">
      <article class="panel">
        <span class="eyebrow">Your Tater</span>
        <h2>Messages go to the Tater URLs you configure.</h2>
        <p>
          When you pair Little Spud with Tater, the app sends messages directly
          to the Tater URLs you configure. Depending on what you choose to do in
          the app, this may include chat text, voice input audio, voice transcripts,
          selected media, device name, user name, and app status information needed
          for pairing, notifications, and sync.
        </p>
        <p>
          This data is sent to your configured Tater instance, not to a Little Spud
          cloud service.
        </p>
      </article>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Permissions</span>
        <h2>Little Spud asks only for the device access needed for app features.</h2>
      </div>
      <div class="grid grid-3">
        <article class="feature-card">
          <h3>Camera</h3>
          <p>Used to scan Tater pairing QR codes.</p>
        </article>
        <article class="feature-card">
          <h3>Microphone</h3>
          <p>Used for voice input when you choose to speak to Tater.</p>
        </article>
        <article class="feature-card">
          <h3>Local network</h3>
          <p>Used to connect to your Tater instance on your private network.</p>
        </article>
        <article class="feature-card">
          <h3>Notifications</h3>
          <p>Used to show local device notifications from your paired Tater.</p>
        </article>
        <article class="feature-card">
          <h3>Photos</h3>
          <p>Used only if you choose to attach media from your photo library.</p>
        </article>
        <article class="feature-card">
          <h3>Controls</h3>
          <p>You can manage these permissions in your device's Settings app.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Demo mode</span>
          <h2>Demo mode runs locally.</h2>
          <p>
            Little Spud includes a local demo mode so users can preview the app
            before pairing with Tater. Demo mode runs on the device and does not
            connect to a private Tater server.
          </p>
        </article>
        <article class="panel">
          <span class="eyebrow">Contact</span>
          <h2>Privacy questions</h2>
          <p>
            For support or privacy questions, contact
            <a class="chip-link" href="mailto:tater@tatertottersonai.com?subject=Little%20Spud%20privacy">tater@tatertottersonai.com</a>.
          </p>
        </article>
      </div>
    </section>
    """
    return page_template(
        title="Little Spud Privacy Policy | Tater Assistant",
        description="Privacy policy for the Little Spud companion app for Tater Assistant.",
        body=body,
        depth=2,
        nav_key="privacy",
    )


def render_llms_page() -> str:
    body = """
    <section class="hero hero-subpage hero-plugin">
      <div class="hero-copy">
        <span class="eyebrow">Local model runtime</span>
        <h1>LLMs, vision, and model tools</h1>
        <p>Tater can run local models through llama.cpp, Hugging Face Transformers, and MLX Engine, or connect to remote OpenAI-compatible providers when you want an external server.</p>
        <div class="chip-row">
          <span class="chip">llama.cpp GGUF</span>
          <span class="chip">Transformers</span>
          <span class="chip">MLX Engine</span>
          <span class="chip">Vision</span>
          <span class="chip">Chat templates</span>
        </div>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">Where to configure</span>
        <p>WebUI Settings -&gt; Models, Hugging Face, and Advanced.</p>
        <div class="action-row">
          <a class="button button-ghost" href="../api/index.html">OpenAI API docs</a>
          <a class="button button-ghost" href="../spud-hub/index.html">Spud Hub docs</a>
        </div>
      </aside>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Provider choices</span>
        <h2>Choose the local runtime that matches the model and machine.</h2>
        <p>The Base model controls normal chat, Hydra planning, Memory Core extraction, briefs, and most internal AI calls. Vision can use the Base model when supported or a dedicated vision model.</p>
      </div>
      <div class="responsive-table-wrap">
        <table class="spec-table">
          <thead>
            <tr><th>Provider</th><th>Best for</th><th>Model shape</th><th>Notes</th></tr>
          </thead>
          <tbody>
            <tr>
              <td><code>llama_cpp</code></td>
              <td>Fast GGUF text and vision on NVIDIA, Apple Metal, CPU, and other llama.cpp-supported backends.</td>
              <td>Single GGUF file, or GGUF plus matching <code>mmproj</code> for vision.</td>
              <td>Supports context, batch, micro-batch, GPU KV offload, Flash Attention, MTP settings, and chat template overrides.</td>
            </tr>
            <tr>
              <td><code>hf_transformers</code></td>
              <td>Transformers models that need PyTorch, custom architectures, or Hugging Face-native loading.</td>
              <td>Full Hugging Face repo with config, tokenizer, and weights.</td>
              <td>Supports device, dtype, device map, attention implementation, trust remote code, context, and chat template overrides.</td>
            </tr>
            <tr>
              <td><code>mlx_lm</code></td>
              <td>Apple Silicon local text and vision through Tater's MLX Engine path.</td>
              <td>Full MLX repo, including sharded safetensors, tokenizer, config, and processor files when needed.</td>
              <td>MLX Engine is always used for MLX text and vision. There is no fallback to the older plain MLX-LM or MLX-VLM runtime.</td>
            </tr>
            <tr>
              <td><code>openai_compatible</code></td>
              <td>Remote or external local servers such as OpenAI-compatible chat endpoints.</td>
              <td>Provider model name served by the external endpoint.</td>
              <td>Useful when another service owns model loading, GPU scheduling, or hosted inference.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Model browser</span>
          <h2>Hugging Face downloads</h2>
          <p>The Hugging Face tab can browse, filter, and download local models for each runtime.</p>
          <ul class="stack-list">
            <li>llama.cpp uses the Hub <code>apps=llama.cpp</code> filter and downloads individual GGUF files, including matching projectors when needed.</li>
            <li>MLX downloads the full repo instead of one file, because tokenizer, config, safetensors shards, and processor files must stay together.</li>
            <li>Transformers downloads the full repo for PyTorch/Transformers loading.</li>
            <li>Download cards show repo/file progress, bytes, speed, ETA, and cancellation state across refreshes and tab changes.</li>
            <li>A Hugging Face token can be saved through the Hugging Face integration for gated/private models and higher Hub rate limits.</li>
          </ul>
        </article>
        <article class="panel">
          <span class="eyebrow">Runtime state</span>
          <h2>Loading and monitoring</h2>
          <p>Save &amp; Load warms selected local models. The runtime pill and popup show loaded models, CPU/GPU/RAM/VRAM, LLM calls, vision calls, context estimates, and recent activity.</p>
          <ul class="stack-list">
            <li>The Debug mini-tab shows live prompt and generation events for local model calls.</li>
            <li>Context cards estimate model fit without forcing dashboard refreshes or expensive reloads.</li>
            <li>Local vision workers isolate crash-prone llama.cpp vision calls so Tater stays online if a native backend fails.</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Local tuning</span>
        <h2>The settings are runtime-specific.</h2>
      </div>
      <div class="grid grid-3">
        <article class="tool-card">
          <div class="chip-row"><span class="chip">llama.cpp</span><span class="chip">GGUF</span></div>
          <h3>Context and GPU controls</h3>
          <p>Set text context separately from vision context, then tune eval batch, micro-batch, Flash Attention, GPU KV offload, and Multi-Token Prediction draft tokens.</p>
        </article>
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Transformers</span><span class="chip">PyTorch</span></div>
          <h3>Device and precision</h3>
          <p>Select device, dtype, device map, attention implementation, trust remote code, and context length for Transformers models.</p>
        </article>
        <article class="tool-card">
          <div class="chip-row"><span class="chip">MLX Engine</span><span class="chip">Apple Silicon</span></div>
          <h3>Engine-backed MLX</h3>
          <p>Tater routes MLX text and vision through MLX Engine with context length, lazy load, trust remote code, prefill step, and quantized KV settings.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Vision</span>
          <h2>Image understanding</h2>
          <p>Vision calls are separate from text chat. If a core, Verba, or chat attachment asks for image understanding, Tater routes the request through the configured vision path.</p>
          <ul class="stack-list">
            <li>llama.cpp vision needs a compatible model GGUF and matching <code>mmproj</code> projector.</li>
            <li>MLX vision uses the MLX Engine path and expects the selected model/repo to include the required vision processor and weights.</li>
            <li>Dedicated vision models can be selected when the Base text model is not vision-capable.</li>
          </ul>
        </article>
        <article class="panel">
          <span class="eyebrow">Thinking control</span>
          <h2>Templates and response shape</h2>
          <p>Tater strips visible thinking blocks where possible, supports provider-specific chat template overrides, and keeps the prompt separate from the model chat template.</p>
          <ul class="stack-list">
            <li>Use the Chat Template button beside local models to inspect embedded templates and save overrides.</li>
            <li>Overrides persist in Redis and are reused after restart until reset to the embedded template.</li>
            <li>For models whose template supports thinking flags, edit the template itself rather than injecting extra system prompt text.</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">How calls flow</span>
        <h2>Hydra and direct calls share the same configured model layer.</h2>
      </div>
      <div class="grid grid-2">
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Direct</span><span class="chip">Base model</span></div>
          <h3>Normal LLM calls</h3>
          <p>Dashboard briefs, Memory Core extraction, Guardian checks, direct chat, and API direct mode use the active Base model unless a feature explicitly selects a dedicated local model.</p>
        </article>
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Hydra</span><span class="chip">Tools</span></div>
          <h3>Reasoning and orchestration</h3>
          <p>Hydra uses the configured model to plan, validate tool calls, run Verbas, and return final answers. Beast Mode can assign different models to Hydra heads while Base remains available for normal AI calls.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="action-row">
        <a class="button" href="../api/index.html">OpenAI-compatible API</a>
        <a class="button button-ghost" href="../spud-hub/index.html">Spud Hub</a>
        <a class="button button-ghost" href="../portals/webui.html">WebUI docs</a>
        <a class="button button-ghost" href="../integrations/huggingface.html">Hugging Face integration</a>
        <a class="button button-ghost" href="../index.html">Home</a>
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | Local LLMs",
        description="Tater local LLM, vision, model download, runtime tuning, chat template, and debug console documentation.",
        body=body,
        depth=1,
        nav_key="llms",
    )


def render_spud_hub_page() -> str:
    body = """
    <section class="hero hero-subpage hero-plugin">
      <div class="hero-copy">
        <span class="eyebrow">Spud Link</span>
        <h1>Spud Hub links Tater nodes with a native Tater protocol.</h1>
        <p>
          Spud Hub lets one full Tater install become the main model and tool server for paired Spudlets
          and Little Spud clients. Pairing uses a QR code or manual sync code, then each linked device
          receives a saved node token for native Tater API calls.
        </p>
        <div class="chip-row">
          <span class="chip">QR pairing</span>
          <span class="chip">Manual code</span>
          <span class="chip">Native Tater API</span>
          <span class="chip">Spudlet</span>
          <span class="chip">Little Spud</span>
        </div>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">Where to configure</span>
        <p>Open WebUI Settings -&gt; Spud Hub to enable Hub or Spudlet mode, create pairing codes, link devices, and revoke nodes.</p>
        <div class="action-row">
          <a class="button button-ghost" href="../llms/index.html">Local LLM docs</a>
          <a class="button button-ghost" href="../api/index.html">API docs</a>
        </div>
      </aside>
    </section>

    <section class="app-store-banner" aria-label="Little Spud app">
      <div class="app-store-copy">
        <span class="eyebrow">Little Spud app</span>
        <h2>Take your Tater with you on iPhone, iPad, and Android.</h2>
        <p>
          Little Spud pairs to Spud Hub with a QR code, keeps home and away Tater URLs,
          streams tool progress, controls Home and Music Core, shows notification
          snapshots and full-screen video, and uses the Hub's voice settings for STT,
          TTS, notifications, and follow-up mic behavior.
        </p>
        <div class="chip-row">
          <span class="chip">iOS + Android</span>
          <span class="chip">QR pairing</span>
          <span class="chip">Home + Music</span>
          <span class="chip">No Little Spud cloud</span>
        </div>
      </div>
      <div class="app-store-actions">
        <div class="store-button-row">
          <a class="store-badge store-badge-apple" href="https://apps.apple.com/app/little-spud/id6781400718" target="_blank" rel="noreferrer" aria-label="Download Little Spud on the App Store">
            <span class="store-badge-platform" aria-hidden="true">iOS</span>
            <span class="store-badge-copy"><small>Download on the</small><strong>App Store</strong></span>
          </a>
          <a class="store-badge store-badge-play" href="https://play.google.com/store/apps/details?id=com.tatertotterson.littlespud.android" target="_blank" rel="noreferrer" aria-label="Get Little Spud on Google Play">
            <span class="store-badge-platform" aria-hidden="true">Play</span>
            <span class="store-badge-copy"><small>Get it on</small><strong>Google Play</strong></span>
          </a>
        </div>
        <a class="button button-ghost" href="../privacy/little-spud/index.html">Privacy policy</a>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Roles</span>
        <h2>One Hub can power full Tater nodes and lightweight clients.</h2>
        <p>Spud Link has explicit roles so the Hub knows whether the paired device needs raw model calls or full Hydra chat with tools, media, voice, and progress events.</p>
      </div>
      <div class="grid grid-3">
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Server</span><span class="chip">GPU/model host</span></div>
          <h3>Spud Hub</h3>
          <p>The main Tater install. It owns the configured local or remote model stack, Hydra, Verbas, People records, history, TTS/STT settings, and linked-node management.</p>
        </article>
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Full Tater</span><span class="chip">Borrowed model power</span></div>
          <h3>Spudlet</h3>
          <p>A full Tater node that pairs to the Hub. In Spudlet mode its Base model becomes <strong>Spudlet via Spud Hub</strong>, so LLM calls route through the Hub instead of local model settings.</p>
        </article>
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Light client</span><span class="chip">Hydra chat</span></div>
          <h3>Little Spud</h3>
          <p>A lightweight chat client that sends user name and device name to the Hub, then receives native Tater chat events, tool notices, artifacts, TTS/STT behavior, and follow-up mic decisions.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Pairing flow</span>
          <h2>QR code or manual sync code</h2>
          <p>The Hub creates a temporary pairing code and encodes the connection details into a Tater Spud Link QR payload. Clients can scan it or paste the manual code with the Hub URL.</p>
          <ul class="stack-list">
            <li>The QR payload includes the Hub URL, pair URL, temporary pairing code, allowed roles, Hub name, and expiration time.</li>
            <li>A camera-capable client can scan the QR code. Clients without a camera can paste the manual pairing code and Tater URL.</li>
            <li>When pairing succeeds, the Hub returns a node token. Future requests use that token through <code>Authorization: Bearer</code> and <code>X-Spudlink-Token</code>.</li>
            <li>The Hub stores only token hashes for linked nodes and never shows the node token back after pairing.</li>
          </ul>
        </article>
        <article class="panel">
          <span class="eyebrow">Linked devices</span>
          <h2>Hub-side visibility and revoke</h2>
          <p>Spud Hub keeps a live list of linked nodes so operators can see what is connected and remove access when needed.</p>
          <ul class="stack-list">
            <li>Linked-node rows include role, node/device name, remote network information, last activity, and sanitized activity details.</li>
            <li>Little Spud clients pass user and device information so history can be scoped like <code>little_spud:user:device</code> and mapped later in People.</li>
            <li>The revoke button removes a node from the Hub. The client must pair again to regain access.</li>
            <li>Heartbeat calls let the Hub show connection/activity state even when the client is not actively chatting.</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Native protocol</span>
        <h2>Spud Link is not the OpenAI-compatible API.</h2>
        <p>Spud Link uses Tater-native endpoints because Tater needs more than plain chat completions: tool progress, generated media, active-run status, TTS, STT, follow-up mic decisions, identity, and linked-device telemetry.</p>
      </div>
      <div class="responsive-table-wrap">
        <table class="spec-table">
          <thead><tr><th>Endpoint</th><th>Used by</th><th>What it does</th></tr></thead>
          <tbody>
            <tr><td><code>POST /api/spudlink/pairing-code</code></td><td>Hub WebUI</td><td>Creates a temporary pairing code plus QR payload for Spudlets and Little Spuds.</td></tr>
            <tr><td><code>POST /api/spudlink/pair</code></td><td>Clients</td><td>Exchanges the pairing code for a linked node record and node token.</td></tr>
            <tr><td><code>POST /api/spudlink/heartbeat</code></td><td>Clients</td><td>Updates device presence, role, metadata, and current activity on the Hub.</td></tr>
            <tr><td><code>POST /api/spudlink/v1/tater/llm</code></td><td>Spudlets</td><td>Runs native raw model calls on the Hub for a paired full Tater node.</td></tr>
            <tr><td><code>POST /api/spudlink/v1/tater/chat</code></td><td>Little Spud</td><td>Streams Hydra chat events, tool notices, final text, artifacts, and follow-up decisions.</td></tr>
            <tr><td><code>GET /api/spudlink/v1/history</code></td><td>Little Spud</td><td>Fetches scoped chat history and active-run state for reconnects.</td></tr>
            <tr><td><code>POST /api/spudlink/v1/tts/speech</code></td><td>Little Spud</td><td>Uses the Hub's configured TTS voice to synthesize reply audio.</td></tr>
            <tr><td><code>WS /api/spudlink/v1/stt/stream</code></td><td>Little Spud</td><td>Streams microphone audio to server-side STT with VAD-style turn ending.</td></tr>
            <tr><td><code>GET /api/spudlink/v1/files/{file_id}</code></td><td>Little Spud</td><td>Serves generated images, videos, audio, and other returned artifacts to the paired client.</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Spudlet model routing</span>
          <h2>A full Tater can use the Hub model stack.</h2>
          <p>When a Tater install is switched to Spudlet mode and paired with a Hub, the Base model dropdown shows <strong>Spudlet via Spud Hub</strong>.</p>
          <ul class="stack-list">
            <li>Hydra and normal LLM calls resolve to the Hub's native <code>/api/spudlink/v1/tater/llm</code> endpoint.</li>
            <li>The Spudlet ignores its internal local LLM rows for Base model routing while paired in Spudlet mode.</li>
            <li>The Hub still decides which actual model provider runs the call: llama.cpp, Transformers, MLX Engine, or an external provider configured on the Hub.</li>
            <li>This keeps a lighter machine useful as a full Tater UI/node while the stronger Hub handles GPU and model work.</li>
          </ul>
        </article>
        <article class="panel">
          <span class="eyebrow">Little Spud experience</span>
          <h2>Native chat with Tater-specific events</h2>
          <p>Little Spud is designed as a lightweight client for phones, tablets, laptops, and future apps. It does not need to run Tater locally.</p>
          <ul class="stack-list">
            <li>Tool-call messages are streamed as soon as a tool starts, before the final answer.</li>
            <li>Generated images and media return as artifacts, so the client can display the file and then animate the reply text below it.</li>
            <li>TTS can use the Hub's configured voice, and STT can stream microphone audio to the Hub for transcription.</li>
            <li>If the Hub decides the assistant should keep listening, it tells Little Spud to reopen the mic after the reply text and TTS playback finish.</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Network notes</span>
        <h2>Use matching HTTP/HTTPS paths for browser clients.</h2>
      </div>
      <div class="grid grid-2">
        <article class="tool-card">
          <div class="chip-row"><span class="chip">LAN</span><span class="chip">HTTP</span></div>
          <h3>Local network pairing</h3>
          <p>For LAN testing, the QR payload can use the Hub's local HTTP URL such as <code>http://tater.local:8501</code> or an IP address. Browser private-network rules can still require the Hub to allow CORS for Spud Link routes.</p>
        </article>
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Remote</span><span class="chip">HTTPS</span></div>
          <h3>Reverse proxy and remote use</h3>
          <p>If Little Spud is opened over HTTPS, the Hub URL should also be HTTPS. Put the Hub behind the same public HTTPS route or configure Public / LAN URL so QR payloads point at the reachable address.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="action-row">
        <a class="button" href="../llms/index.html">Local LLMs</a>
        <a class="button button-ghost" href="../api/index.html">OpenAI-compatible API</a>
        <a class="button button-ghost" href="../portals/webui.html">WebUI docs</a>
        <a class="button button-ghost" href="../index.html">Home</a>
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | Spud Hub",
        description="Spud Hub and Spud Link documentation for native Tater pairing, QR codes, Spudlets, Little Spud clients, node tokens, and native endpoints.",
        body=body,
        depth=1,
        nav_key="spud-hub",
    )


def render_openai_api_page() -> str:
    body = """
    <section class="hero hero-subpage hero-plugin">
      <div class="hero-copy">
        <span class="eyebrow">External app access</span>
        <h1>OpenAI-compatible API</h1>
        <p>Tater can expose a local OpenAI-compatible chat API so other apps can use the active Tater model directly or route requests through Hydra and Verbas.</p>
        <div class="chip-row">
          <span class="chip">/v1/models</span>
          <span class="chip">/v1/chat/completions</span>
          <span class="chip">Direct mode</span>
          <span class="chip">Hydra mode</span>
        </div>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">Security</span>
        <p>Enable the API and set an API key in WebUI Settings -&gt; Advanced before external clients can connect.</p>
        <div class="action-row">
          <a class="button button-ghost" href="../llms/index.html">Local LLM docs</a>
          <a class="button button-ghost" href="../spud-hub/index.html">Spud Hub docs</a>
        </div>
      </aside>
    </section>

    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Configuration</span>
          <h2>Enable and authenticate</h2>
          <p>The API is off until enabled. Requests must include the configured key as a bearer token, <code>X-API-Key</code>, or <code>api_key</code> query parameter.</p>
          <ul class="stack-list">
            <li><code>Authorization: Bearer YOUR_KEY</code> is the recommended header.</li>
            <li><code>X-API-Key: YOUR_KEY</code> is also accepted.</li>
            <li>If the API is disabled, Tater returns 404. If no key is configured, it returns 403. Invalid keys return 401.</li>
          </ul>
        </article>
        <article class="panel">
          <span class="eyebrow">Modes</span>
          <h2>Direct or Hydra</h2>
          <p>The API mode controls whether external calls use the active Base model directly or go through Hydra orchestration.</p>
          <ul class="stack-list">
            <li><strong>Direct</strong> sends the normalized chat messages to the active configured LLM client.</li>
            <li><strong>Hydra</strong> gives the latest user message and history to Hydra, optionally with Verba tool access enabled.</li>
            <li>The request model aliases <code>tater/base</code> and <code>tater/direct</code> force Direct mode. <code>tater/hydra</code> forces Hydra mode.</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Endpoints</span>
        <h2>The API speaks the common chat completion shape.</h2>
      </div>
      <div class="grid grid-2">
        <article class="tool-card">
          <div class="chip-row"><span class="chip">GET</span><span class="chip">/v1/models</span></div>
          <h3>List available aliases</h3>
          <p>Returns <code>tater/base</code>, <code>tater/direct</code>, <code>tater/hydra</code>, and configured local/remote model rows for discovery.</p>
        </article>
        <article class="tool-card">
          <div class="chip-row"><span class="chip">POST</span><span class="chip">/v1/chat/completions</span></div>
          <h3>Run a chat completion</h3>
          <p>Accepts OpenAI-style messages and returns an OpenAI-style response with <code>choices</code>, <code>message.content</code>, and usage fields when available.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Model routing</span>
        <h2>API calls use Tater's configured model layer.</h2>
        <p>The API advertises provider-qualified model IDs for visibility, but chat completions currently route through the active configured LLM provider selected in Tater settings.</p>
      </div>
      <div class="responsive-table-wrap">
        <table class="spec-table">
          <thead><tr><th>Requested model</th><th>Effect</th><th>Runtime used</th></tr></thead>
          <tbody>
            <tr><td><code>tater/base</code> or <code>tater/direct</code></td><td>Forces direct chat mode.</td><td>The active Base provider in Settings -&gt; Models.</td></tr>
            <tr><td><code>tater/hydra</code></td><td>Forces Hydra mode.</td><td>The active configured LLM client behind Hydra.</td></tr>
            <tr><td><code>mlx_lm::repo/model</code></td><td>Listed for discovery of configured MLX rows.</td><td>Current chat route still uses the active configured provider; MLX rows run through MLX Engine when selected as active.</td></tr>
            <tr><td><code>llama_cpp::repo::file.gguf</code></td><td>Listed for discovery of configured llama.cpp rows.</td><td>Current chat route still uses the active configured provider; llama.cpp rows run through llama.cpp when selected as active.</td></tr>
            <tr><td><code>hf_transformers::repo/model</code></td><td>Listed for discovery of configured Transformers rows.</td><td>Current chat route still uses the active configured provider; Transformers rows run through Hugging Face Transformers when selected as active.</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Request example</span>
          <h2>Direct chat</h2>
          <pre class="code-block"><code>curl http://localhost:8501/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_TATER_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "tater/base",
    "messages": [
      {"role": "system", "content": "You are concise."},
      {"role": "user", "content": "What is Tater?"}
    ],
    "temperature": 0.7,
    "max_tokens": 256
  }'</code></pre>
        </article>
        <article class="panel">
          <span class="eyebrow">Request example</span>
          <h2>Hydra with tools</h2>
          <pre class="code-block"><code>curl http://localhost:8501/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_TATER_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "tater/hydra",
    "user": "external-app",
    "messages": [
      {"role": "user", "content": "Turn on the office lights."}
    ]
  }'</code></pre>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Compatibility notes</span>
        <h2>Useful details for external clients.</h2>
      </div>
      <div class="grid grid-3">
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Streaming</span></div>
          <h3>Streaming shape</h3>
          <p>When <code>stream</code> is true, Tater returns a server-sent event stream with a single completion chunk followed by <code>[DONE]</code>.</p>
        </article>
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Messages</span></div>
          <h3>Text content</h3>
          <p>Tater normalizes string message content and OpenAI-style text parts. Non-text multimodal parts are ignored by this endpoint.</p>
        </article>
        <article class="tool-card">
          <div class="chip-row"><span class="chip">Tools</span></div>
          <h3>Hydra tool access</h3>
          <p>Hydra mode can expose enabled Verbas to external requests when the API setting allows Hydra tools.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="action-row">
        <a class="button" href="../llms/index.html">Local LLMs</a>
        <a class="button button-ghost" href="../spud-hub/index.html">Spud Hub</a>
        <a class="button button-ghost" href="../cerberus/index.html">Hydra docs</a>
        <a class="button button-ghost" href="../portals/webui.html">WebUI docs</a>
        <a class="button button-ghost" href="../index.html">Home</a>
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | OpenAI-Compatible API",
        description="Tater OpenAI-compatible API endpoint documentation for /v1/models and /v1/chat/completions.",
        body=body,
        depth=1,
        nav_key="api",
    )


def render_install_index() -> str:
    readme_note = extract_install_readme_note()
    macos_release = load_macos_release()
    macos_version = macos_release.get("version_label", "")
    macos_download_url = macos_release.get("dmg_url") or "https://github.com/TaterTotterson/Tater/releases/latest"
    macos_download_label = f"Download Tater {macos_version}" if macos_version else "Download Tater for macOS"
    macos_version_chip = chip(f"Current release {macos_version}") if macos_version else chip("Latest release")
    cards = "".join(
        f"""
        <article class="platform-card platform-card-detail{' install-card-featured' if method['slug'] == 'macos' else ''}">
          <div class="chip-row">
            {chip(method['complexity'])}{chip("Apple Silicon") if method['slug'] == 'macos' else ''}
          </div>
          <h3>{escape(method['title'])}</h3>
          <p>{escape(method['summary'])}</p>
          <p><strong>Best for:</strong> {escape(method['best_for'])}</p>
          <div class="plugin-links">
            {button("Read install path", f"{method['slug']}.html", ghost=True)}
          </div>
        </article>
        """
        for method in INSTALL_METHODS
    )

    body = f"""
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Install Tater</span>
        <h1>Pick the install path that fits your stack.</h1>
        <p>
          Start with the native macOS app, or run Tater through Unraid, Home Assistant,
          local Python, or Docker. After Tater is running, Little Spud can pair as its
          iPhone, iPad, or Android companion.
        </p>
        <div class="chip-row">
          {macos_version_chip}
          {chip("5 install paths")}
          {chip("iOS + Android companion")}
        </div>
        <div class="action-row">
          <a class="button" href="{escape(macos_download_url)}" target="_blank" rel="noreferrer">{escape(macos_download_label)}</a>
          <a class="button button-ghost" href="#server-install-paths">Compare install paths</a>
        </div>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">README note</span>
        <p>{escape(readme_note)}</p>
        <div class="action-row">
          {button("Tater Voice", "../tater-voice/index.html", ghost=True)}
        </div>
      </aside>
    </section>
    <section class="section install-section-anchor" id="server-install-paths">
      <div class="section-head section-head-wide">
        <span class="eyebrow">Ways to run Tater</span>
        <h2>Choose the host that already fits your home.</h2>
        <p>The macOS app is the quickest native path. The other options run the same TaterOS experience on a server or container you control.</p>
      </div>
      <div class="grid grid-2">
        {cards}
      </div>
    </section>

    <section class="app-store-banner" aria-label="Little Spud companion apps">
      <div class="app-store-copy">
        <span class="eyebrow">Companion apps</span>
        <h2>Run Tater first, then pair Little Spud.</h2>
        <p>
          Little Spud does not replace the Tater server. It pairs to your Tater through
          Spud Hub and brings chat, voice, Home controls, Music Core, notifications,
          snapshots, and video clips to your phone or tablet.
        </p>
        <div class="chip-row">
          <span class="chip">iPhone + iPad</span>
          <span class="chip">Android</span>
          <span class="chip">QR pairing</span>
          <span class="chip">Self-hosted Tater</span>
        </div>
      </div>
      <div class="app-store-actions">
        <div class="store-button-row">
          <a class="store-badge store-badge-apple" href="https://apps.apple.com/app/little-spud/id6781400718" target="_blank" rel="noreferrer" aria-label="Download Little Spud on the App Store">
            <span class="store-badge-platform" aria-hidden="true">iOS</span>
            <span class="store-badge-copy"><small>Download on the</small><strong>App Store</strong></span>
          </a>
          <a class="store-badge store-badge-play" href="https://play.google.com/store/apps/details?id=com.tatertotterson.littlespud.android" target="_blank" rel="noreferrer" aria-label="Get Little Spud on Google Play">
            <span class="store-badge-platform" aria-hidden="true">Play</span>
            <span class="store-badge-copy"><small>Get it on</small><strong>Google Play</strong></span>
          </a>
        </div>
        <div class="action-row">
          <a class="button button-ghost" href="../spud-hub/index.html">Pairing guide</a>
          <a class="button button-ghost" href="../privacy/little-spud/index.html">Privacy</a>
        </div>
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | Install",
        description="Install Tater for macOS, Unraid, Home Assistant, local Python, or Docker, then pair Little Spud on iOS or Android.",
        body=body,
        depth=1,
        nav_key="install",
    )


def render_companion_section(items: list[dict[str, Any]], eyebrow: str, title: str, intro: str = "") -> str:
    if not items:
        return ""

    cards = ""
    for item in items:
        chips_html = "".join(chip(text) for text in item.get("chips") or [])
        detail_html = "".join(f"<li>{escape(detail)}</li>" for detail in item.get("details") or [])
        links_html = "".join(
            button(link["label"], link["href"], ghost=True)
            for link in item.get("links") or []
        )
        links_block = f'<div class="action-row">{links_html}</div>' if links_html else ""
        cards += f"""
        <article class="tool-card">
          <div class="chip-row">{chips_html}</div>
          <h3>{escape(item['title'])}</h3>
          <p>{escape(item['summary'])}</p>
          <ul class="stack-list">{detail_html}</ul>
          {links_block}
        </article>
        """

    intro_html = f"<p>{escape(intro)}</p>" if intro else ""
    return f"""
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">{escape(eyebrow)}</span>
        <h2>{escape(title)}</h2>
        {intro_html}
      </div>
      <div class="grid grid-2">
        {cards}
      </div>
    </section>
    """


def render_install_detail(method: dict[str, Any]) -> str:
    highlight_html = "".join(f"<li>{escape(item)}</li>" for item in method["highlights"])
    step_html = "".join(f"<li>{escape(item)}</li>" for item in method["steps"])
    note_html = "".join(f"<li>{escape(item)}</li>" for item in method["notes"])
    snippets_html = "".join(
        f"""
        <article class="panel">
          <span class="eyebrow">{escape(snippet['label'])}</span>
          <pre class="code-block"><code>{escape(snippet['code'])}</code></pre>
        </article>
        """
        for snippet in method["snippets"]
    )
    companion_section = render_companion_section(
        method.get("companions") or [],
        "Companion apps",
        "Optional companion pieces for this install path.",
        "After Tater is running, companion apps can connect back to the portal routes mounted on the main Tater port when they are supported.",
    )
    guide_section = render_companion_section(
        method.get("guides") or [],
        "Workflow setup",
        "Patterns for connecting this install path to Tater workflows.",
        "These patterns matter most when you want companion apps, dashboards, and routines to use Tater's main WebUI/API routes.",
    )
    links_html = "".join(
        button(link["label"], link["href"], ghost=True)
        for link in method["links"]
    )
    detail_chips = chip(method["complexity"])

    primary_action = ""
    if method["slug"] == "macos":
        detail_chips += chip("Apple Silicon")
        macos_release = load_macos_release()
        macos_version = macos_release.get("version_label", "")
        macos_download_url = macos_release.get("dmg_url") or "https://github.com/TaterTotterson/Tater/releases/latest"
        macos_download_label = f"Download Tater {macos_version}" if macos_version else "Download Tater for macOS"
        primary_action = f"""
        <div class="action-row">
          <a class="button" href="{escape(macos_download_url)}" target="_blank" rel="noreferrer">{escape(macos_download_label)}</a>
        </div>
        """

    links_section = ""
    if links_html:
        links_section = f"""
        <section class="section">
          <article class="panel">
            <span class="eyebrow">Related links</span>
            <div class="action-row">{links_html}</div>
          </article>
        </section>
        """

    snippet_section = ""
    if snippets_html:
        snippet_section = f"""
        <section class="section">
          <div class="section-head">
            <span class="eyebrow">Commands and config</span>
            <h2>README snippets for this install path.</h2>
          </div>
          <div class="grid grid-2">
            {snippets_html}
          </div>
        </section>
        """

    body = f"""
    <section class="hero hero-subpage hero-plugin">
      <div class="hero-copy">
        <span class="eyebrow">{escape(method['eyebrow'])}</span>
        <h1>{escape(method['title'])}</h1>
        <p>{escape(method['summary'])}</p>
        <div class="chip-row">
          {detail_chips}
        </div>{primary_action}
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">Best for</span>
        <p>{escape(method['best_for'])}</p>
      </aside>
    </section>
    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Why choose this</span>
          <h2>Key points</h2>
          <ul class="stack-list">{highlight_html}</ul>
        </article>
        <article class="panel">
          <span class="eyebrow">Install flow</span>
          <h2>Steps</h2>
          <ol class="stack-list">{step_html}</ol>
        </article>
      </div>
    </section>
    <section class="section">
      <article class="panel">
        <span class="eyebrow">Important notes</span>
        <ul class="stack-list">{note_html}</ul>
      </article>
    </section>
    {companion_section}
    {guide_section}
    {snippet_section}
    {links_section}
    <section class="section">
      <div class="action-row">
        {button("Back to install guide", "index.html", ghost=True)}
        {button("Home", "../index.html", ghost=True)}
        {button("Portals", "../portals/index.html", ghost=True)}
        {button("Cores", "../cores/index.html", ghost=True)}
      </div>
    </section>
    """
    return page_template(
        title=f"Tater Assistant | {method['title']}",
        description=method["summary"],
        body=body,
        depth=1,
        nav_key="install",
    )


def render_platforms_page(platforms: list[dict[str, Any]]) -> str:
    cards = "".join(
        f"""
        <article class="platform-card platform-card-detail">
          <div class="chip-row">
            {chip(platform['role'])}
            {chip(platform_version_chip(platform))}
            {chip(platform_settings_chip(platform))}
            {chip(platform_runtime_chip(platform))}
          </div>
          <h3>{escape(platform['title'])}</h3>
          <p>{escape(platform['description'])}</p>
          <div class="plugin-links">
            {button("Read portal page", f"{platform['slug']}.html", ghost=True)}
          </div>
        </article>
        """
        for platform in platforms
    )

    body = f"""
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Portal reference</span>
        <h1>Tater runs across purpose-built portals.</h1>
        <p>
          Portals are chat, voice, and app entry points that route requests into Hydra and Verbas through the main Tater WebUI/API port.
        </p>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">What is documented</span>
        <p>{len(platforms)} portals with current descriptions, settings snapshots, API notes, and related Verba context.</p>
      </aside>
    </section>
    <section class="section">
      <div class="grid grid-3">
        {cards}
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | Portals",
        description="Reference for Tater Assistant portals and their integration behavior.",
        body=body,
        depth=1,
        nav_key="portals",
    )


def render_cores_page(cores: list[dict[str, Any]]) -> str:
    cards = "".join(
        f"""
        <article class="platform-card platform-card-detail">
          <div class="chip-row">
            {chip(core['role'])}
            {chip(platform_version_chip(core))}
            {chip(platform_settings_chip(core))}
            {chip(platform_runtime_chip(core))}
          </div>
          <h3>{escape(core['title'])}</h3>
          <p>{escape(core['description'])}</p>
          <div class="plugin-links">
            {button("Read core page", f"{core['slug']}.html", ghost=True)}
          </div>
        </article>
        """
        for core in cores
    )

    body = f"""
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Core reference</span>
        <h1>Cores give Tater persistent skills and background work.</h1>
        <p>
          Install only the services you want: automation, awareness, environment, network security, scheduling, memory, music, personal intelligence, feeds, and Tater Tube recommendations.
        </p>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">What is documented</span>
        <p>{len(cores)} cores with current descriptions, settings snapshots, and runtime behavior notes.</p>
      </aside>
    </section>
    <section class="section">
      <div class="grid grid-3">
        {cards}
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | Cores",
        description="Reference for Tater Assistant core runtime services.",
        body=body,
        depth=1,
        nav_key="cores",
    )


def render_integrations_page(integrations: list[dict[str, Any]]) -> str:
    web_search_count = sum(1 for item in integrations if "web_search" in item.get("capabilities", []))
    categories = sorted({str(item.get("category") or "Device") for item in integrations})
    cards = "".join(
        f"""
        <article class="platform-card platform-card-detail">
          <div class="chip-row">
            {chip(integration['category'])}
            {chip(f"v{integration['version']}")}
            {chip("Downloaded when enabled")}
          </div>
          <h3>{escape(integration['title'])}</h3>
          <p>{escape(integration['summary'])}</p>
          <div class="chip-row platform-row">
            {"".join(chip(capability) for capability in integration.get("capabilities", [])[:5]) or chip("settings")}
          </div>
          <div class="plugin-links">
            {button("Read integration page", f"{integration['slug']}.html", ghost=True)}
          </div>
        </article>
        """
        for integration in integrations
    )

    category_chips = "".join(chip(category) for category in categories)
    body = f"""
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Integration reference</span>
        <h1>Tater integrations are optional downloaded providers.</h1>
        <p>
          Integrations live in the Tater_Integrations repo and download into Tater only when enabled. They expose settings, devices, actions, runtime events, and web-search providers through shared hooks.
        </p>
        <div class="action-row">
          {button("Tater Integrations repo", "https://github.com/TaterTotterson/Tater_Integrations")}
          {button("Kernel search", "../kernel-tools/index.html", ghost=True)}
        </div>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">Current catalog</span>
        <p>{len(integrations)} integrations are documented from the current manifest, including {web_search_count} web-search providers.</p>
        <div class="chip-row">{category_chips}</div>
      </aside>
    </section>
    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Runtime model</span>
          <h2>Disabled means dormant.</h2>
          <ul class="stack-list">
            <li>Store buttons download integrations, while the Manage tab enables, disables, updates, and removes installed modules.</li>
            <li>On boot, Tater restores missing enabled integrations but leaves disabled integrations unimported.</li>
            <li>Provider code stays self-contained, so a new integration can add devices or actions without changing Tater core.</li>
          </ul>
        </article>
        <article class="panel">
          <span class="eyebrow">Shared contracts</span>
          <h2>Cores consume capabilities.</h2>
          <ul class="stack-list">
            <li>Device-aware flows ask for capabilities such as camera, snapshot, speaker, garage_door, temperature, motion, web_search, and announcement_target.</li>
            <li>Awareness and Environment Core can build choices from all enabled integrations instead of hard-coded provider lists.</li>
            <li>search_web discovers enabled integrations with the web_search capability and tries them in provider order.</li>
          </ul>
        </article>
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Catalog</span>
        <h2>Available integrations.</h2>
      </div>
      <div class="grid grid-3">
        {cards}
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | Integrations",
        description="Reference for optional Tater integrations, device capabilities, and web-search providers.",
        body=body,
        depth=1,
        nav_key="integrations",
    )


def render_integration_detail(integration: dict[str, Any]) -> str:
    capability_html = "".join(chip(capability) for capability in integration.get("capabilities", [])) or chip("settings")
    settings_html = "".join(f"<li>{escape(field)}</li>" for field in integration.get("fields", []))
    if not settings_html:
        settings_html = "<li>No Settings UI fields are declared in the module metadata.</li>"
    actions_html = "".join(f"<li>{escape(action)}</li>" for action in integration.get("actions", []))
    if not actions_html:
        actions_html = "<li>No shop/settings actions are declared in the module metadata.</li>"
    notes_html = "".join(f"<li>{escape(note)}</li>" for note in integration.get("notes", []))
    if not notes_html:
        notes_html = "<li>This integration follows the shared optional integration runtime and stays dormant until enabled.</li>"

    body = f"""
    <section class="hero hero-subpage hero-plugin">
      <div class="hero-copy">
        <span class="eyebrow">Integration profile</span>
        <h1>{escape(integration['title'])}</h1>
        <p>{escape(integration['summary'])}</p>
        <div class="chip-row">
          {chip(integration['category'])}
          {chip(f"v{integration['version']}")}
          {chip("Optional" if not integration.get("required") else "Required")}
        </div>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">Source module</span>
        <p>{escape(integration.get("entry") or "No entry listed")}</p>
      </aside>
    </section>
    <section class="section">
      <div class="platform-detail-stack">
        <article class="panel platform-detail-lead">
          <span class="eyebrow">Description</span>
          <h2>What it provides</h2>
          <p>{escape(integration['description'] or integration['summary'])}</p>
          <div class="chip-row">{capability_html}</div>
        </article>
        <article class="panel platform-detail-main">
          <span class="eyebrow">Behavior</span>
          <h2>Operational notes</h2>
          <ul class="stack-list">{notes_html}</ul>
        </article>
        <div class="detail-grid platform-detail-support">
          <article class="panel">
            <span class="eyebrow">Settings</span>
            <h2>Declared fields</h2>
            <ul class="stack-list">{settings_html}</ul>
          </article>
          <article class="panel">
            <span class="eyebrow">Actions</span>
            <h2>Declared setup actions</h2>
            <ul class="stack-list">{actions_html}</ul>
          </article>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="action-row">
        {button("Back to integrations", "index.html", ghost=True)}
        {button("Kernel tools", "../kernel-tools/index.html", ghost=True)}
        {button("Cores", "../cores/index.html", ghost=True)}
        {button("Home", "../index.html", ghost=True)}
      </div>
    </section>
    """
    return page_template(
        title=f"Tater Assistant | {integration['title']}",
        description=integration["description"] or integration["summary"],
        body=body,
        depth=1,
        nav_key="integrations",
    )


def render_platform_detail(
    platform: dict[str, Any],
    *,
    nav_key_override: str | None = None,
    back_href: str = "index.html",
    back_label: str | None = None,
) -> str:
    surface_kind = str(platform.get("surface_kind") or "portal").strip().lower()
    is_core = surface_kind == "core"
    is_esphome_runtime = str(platform.get("slug") or "").strip().lower() == "esphome"
    surface_label = "core" if is_core else ("runtime" if is_esphome_runtime else "portal")
    surface_title = "Core" if is_core else ("Runtime" if is_esphome_runtime else "Portal")
    highlight_html = "".join(f"<li>{escape(item)}</li>" for item in platform["highlights"])
    companion_section = render_companion_section(
        platform.get("companions") or [],
        platform.get("companions_eyebrow") or "Companion setup",
        platform.get("companions_title") or f"Related app and integration pieces for this {surface_label}.",
        platform.get("companions_intro") or f"These components connect external clients or service layers back to this {surface_label}.",
    )
    guide_section = render_companion_section(
        platform.get("guides") or [],
        platform.get("guides_eyebrow") or "Usage guide",
        platform.get("guides_title") or f"How to connect to this {surface_label}.",
        platform.get("guides_intro") or f"These notes focus on the setup and runtime behavior that matter most for this {surface_label}.",
    )
    api_items = platform.get("apis") or []
    api_section = ""
    if api_items:
        api_auth_note = ""
        if not is_core and str(platform.get("slug") or "").strip().lower() in {
            "homekit",
            "macos",
            "xbmc",
        }:
            api_auth_note = """
            <article class="panel">
              <span class="eyebrow">API auth</span>
              <p>When API auth is enabled, requests must include <code>X-Tater-Token</code> with the configured portal API key.</p>
            </article>
            """
        api_cards = "".join(
            f"""
            <article class="tool-card">
              <div class="chip-row">
                {chip(api['method'])}
                {chip(api['path'])}
              </div>
              <h3>{escape(api['summary'])}</h3>
              <p>{escape(api['details'])}</p>
            </article>
            """
            for api in api_items
        )
        api_section = f"""
        <section class="section">
          <div class="section-head">
            <span class="eyebrow">Built-in APIs</span>
            <h2>HTTP endpoints exposed by this {surface_label}.</h2>
          </div>
          {api_auth_note}
          <div class="grid grid-2">
            {api_cards}
          </div>
        </section>
        """

    settings = platform["settings"]
    if settings:
        settings_html = "".join(
            f"""
            <li>
              <strong>{escape(item['label'])}</strong>
              <span>{escape(item['type'] or 'setting')}</span>
              <p>{escape(item['description'] or 'No description is present in the current settings schema.')}</p>
              <small>Key: {escape(item['key'])}</small>
              {"<small>Default: " + escape(item['default']) + "</small>" if item['default'] else ""}
              {"<small>Options: " + escape(item['options']) + "</small>" if item['options'] else ""}
            </li>
            """
            for item in settings
        )
        settings_block = f'<ul class="argument-list">{settings_html}</ul>'
    else:
        settings_block = f"<p>{escape(platform_settings_text(platform))}</p>"

    example_plugins = platform["plugin_examples"]
    if example_plugins:
        plugin_links = "".join(
            f'<a class="chip-link" href="../plugins/{escape(plugin["slug"])}.html">{escape(plugin["title"])}</a>'
            for plugin in example_plugins
        )
        plugin_block = f"""
        <p>{escape(platform['plugin_count'])} current Verbas advertise direct support for this {surface_label}.</p>
        <div class="chip-row">{plugin_links}</div>
        """
    else:
        plugin_block = f"<p>{escape(platform_plugin_text(platform))}</p>"

    source_note = ""
    if platform["source_path"]:
        source_name = Path(platform['source_path']).name
        source_note = f"<p>Settings extracted from <code>{escape(source_name)}</code>.</p>"

    webui_showcase = ""
    if platform["slug"] == "webui":
        webui_showcase = """
        <section class="section">
          <div class="webui-preview" aria-label="Stylized preview of Tater's current local WebUI">
            <div class="webui-preview-sidebar">
              <div class="webui-preview-brand"><span class="webui-preview-mark">+</span><strong>Tater</strong></div>
              <span class="webui-preview-nav is-active">Dashboard</span>
              <span class="webui-preview-nav">Chat</span>
              <span class="webui-preview-nav">Music</span>
              <span class="webui-preview-nav">Integrations</span>
              <span class="webui-preview-nav">Voice</span>
              <span class="webui-preview-version">Installed build</span>
            </div>
            <div class="webui-preview-main">
              <div class="webui-preview-topline"><span>Dashboard</span><span class="webui-preview-status">Systems healthy</span></div>
              <div class="webui-preview-grid">
                <div class="webui-preview-card webui-preview-card-wide">
                  <span class="webui-preview-label">Now playing · Family Room</span>
                  <strong>Tater Recommendations</strong>
                  <div class="webui-preview-wave"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
                </div>
                <div class="webui-preview-card"><span class="webui-preview-label">Voice</span><strong>8 satellites</strong><small>Office Stereo ready</small></div>
                <div class="webui-preview-card"><span class="webui-preview-label">System Tasks</span><strong>All caught up</strong><small>Next refresh in 3m</small></div>
                <div class="webui-preview-card webui-preview-card-wide"><span class="webui-preview-label">Home</span><strong>Devices, people, rooms, and cores</strong><small>Live local state without page reloads</small></div>
              </div>
            </div>
          </div>
        </section>
        """

    hero_eyebrow = platform.get("hero_eyebrow") or f"{surface_title} profile"
    hero_panel_eyebrow = platform.get("hero_panel_eyebrow") or "Configuration category"
    hero_panel_text = platform.get("hero_panel_text") or platform["settings_category"]
    role_eyebrow = platform.get("role_eyebrow") or f"{surface_title} role"
    role_title = platform.get("role_title") or f"What this {surface_label} is for"
    role_text = platform.get("role_text") or platform["role"]
    highlights_eyebrow = platform.get("highlights_eyebrow") or "Highlights"
    highlights_title = platform.get("highlights_title") or "Behavior in the current codebase"
    plugin_eyebrow = platform.get("plugin_eyebrow") or "Related Verbas"
    plugin_title = platform.get("plugin_title") or f"Direct {surface_label} support"
    settings_eyebrow = platform.get("settings_eyebrow") or "Settings"
    settings_title = platform.get("settings_title") or "Configuration schema"

    body = f"""
    <section class="hero hero-subpage hero-plugin">
      <div class="hero-copy">
        <span class="eyebrow">{escape(hero_eyebrow)}</span>
        <h1>{escape(platform['title'])}</h1>
        <p>{escape(platform['description'])}</p>
        <div class="chip-row">
          {chip(platform['role'])}
          {chip(platform_version_chip(platform))}
          {chip(platform_settings_chip(platform))}
          {chip(platform_runtime_chip(platform))}
        </div>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">{escape(hero_panel_eyebrow)}</span>
        <p>{escape(hero_panel_text)}</p>
        {source_note}
      </aside>
    </section>
    <section class="section">
      <div class="platform-detail-stack">
        <article class="panel platform-detail-lead">
          <span class="eyebrow">{escape(role_eyebrow)}</span>
          <h2>{escape(role_title)}</h2>
          <p>{escape(role_text)}</p>
        </article>
        <article class="panel platform-detail-main">
          <span class="eyebrow">{escape(highlights_eyebrow)}</span>
          <h2>{escape(highlights_title)}</h2>
          <ul class="stack-list">{highlight_html}</ul>
        </article>
        <div class="detail-grid platform-detail-support">
          <article class="panel">
            <span class="eyebrow">{escape(plugin_eyebrow)}</span>
            <h2>{escape(plugin_title)}</h2>
            {plugin_block}
          </article>
          <article class="panel">
            <span class="eyebrow">{escape(settings_eyebrow)}</span>
            <h2>{escape(settings_title)}</h2>
            {settings_block}
          </article>
        </div>
      </div>
    </section>
    {webui_showcase}
    {companion_section}
    {guide_section}
    {api_section}
    <section class="section">
      <div class="action-row">
        {button(back_label or f"Back to {'cores' if is_core else 'portals'}", back_href, ghost=True)}
        {button("Verbas", "../plugins/index.html", ghost=True)}
        {button("Portals", "../portals/index.html", ghost=True)}
        {button("Tater Voice", "../tater-voice/index.html", ghost=True)}
        {button("Cores", "../cores/index.html", ghost=True)}
        {button("Home", "../index.html", ghost=True)}
      </div>
    </section>
    """
    return page_template(
        title=f"Tater Assistant | {platform['title']}",
        description=platform["description"],
        body=body,
        depth=1,
        nav_key=nav_key_override or ("cores" if is_core else "portals"),
    )


def render_cerberus_page(defaults: list[dict[str, str]]) -> str:
    loop_cards = [
        (
            "1. Astraeus (The Seer)",
            "Astraeus turns a user request into an ordered atomic plan and decides whether the turn is chat-only or execution.",
        ),
        (
            "2. Thanatos (The executor)",
            "Thanatos executes the active atomic step and selects the exact next tool call needed for that step.",
        ),
        (
            "3. Validation and repair",
            "Tool calls are forced into strict JSON, checked against the tool catalog, repaired if malformed, and blocked if the tool is unsupported or disabled.",
        ),
        (
            "4. Thanatos state update",
            "After each tool run, state is updated with goal, plan, facts, open questions, next step, and tool history so current-turn execution stays grounded.",
        ),
        (
            "5. Minos (The Arbiter)",
            "Minos returns one validation decision (CONTINUE, RETRY, ASK_USER, FAIL, or FINAL) and checks whether the turn still needs another atomic step.",
        ),
        (
            "6. Hermes (The voice)",
            "Hermes renders the final user-facing response after execution and validation have converged.",
        ),
    ]
    loop_html = "".join(
        f"""
        <article class="timeline-card">
          <h3>{escape(title)}</h3>
          <p>{escape(text)}</p>
        </article>
        """
        for title, text in loop_cards
    )

    default_cards = "".join(
        f"""
        <article class="stat-card stat-card-wide">
          <strong>{escape(item['value'])}</strong>
          <span>{escape(item['label'])}</span>
        </article>
        """
        for item in defaults
    )

    guardrails = [
        "Tool-first router: execution, retrieval, setting changes, add/remove requests, and system diagnostics route to tools.",
        "Beast Mode routing: base servers can handle AI Calls while Chat/Astraeus/Thanatos/Minos/Hermes can route to per-head models.",
        "Smart chaining: kernel tools and Verbas can be mixed across steps to finish a task instead of stopping after one tool result.",
        "Spudex bridge: when enabled for a platform, Hydra can use terminal console tools for command-line work that does not fit a Verba.",
        "Head-level auto-continue: final Chat and Hermes replies that promise to do the next step can trigger an internal continue turn without putting that check inside the core Hydra loop.",
        "Atomic execution lock: Thanatos and Minos both focus on one next step instead of merging unrelated actions.",
        "Fresh-run behavior: ASK_USER ends the current run and a new user message starts a fresh run.",
        "Recovery text path: validation failures can trigger a short recovery message instead of a broken tool call.",
        "Ledger and metrics: Redis-backed state keeps history, limits, and validation outcomes visible to operators.",
        "Memory context: user and room memory summaries can be injected into Minos decisions without bloating the turn.",
    ]
    guardrail_html = "".join(f"<li>{escape(item)}</li>" for item in guardrails)

    state_fields = ["goal", "plan", "facts", "open_questions", "next_step", "tool_history"]
    state_html = "".join(chip(field) for field in state_fields)
    chaining_cards = [
        (
            "Kernel tools first",
            "Hydra can read files, search the web, inspect pages, search local code, manage memory, attach artifacts, or hand command-line work to Spudex before it ever needs a custom extension.",
        ),
        (
            "Verbas where action lives",
            "When the task needs smart-home control, media workflows, image generation, camera events, or app-specific logic, Hydra switches to the right Verba.",
        ),
        (
            "One step at a time",
            "The chain stays deliberate: choose one action, validate it, run it, update state, then decide whether the next step should continue the task.",
        ),
    ]
    chaining_html = "".join(
        f"""
        <article class="feature-card">
          <h3>{escape(title)}</h3>
          <p>{escape(text)}</p>
        </article>
        """
        for title, text in chaining_cards
    )

    body = f"""
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Hydra AI core</span>
        <h1>Hydra plans, chains, and completes tasks.</h1>
        <p>
          It runs a guarded Astraeus -> Thanatos -> Minos -> Hermes loop that validates actions, repairs bad calls, and mixes kernel tools with Verbas one step at a time.
        </p>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <img class="cerberus-badge" src="../assets/images/cerberus-badge.png" alt="Hydra AI Core badge">
        <span class="eyebrow">State fields</span>
        <div class="chip-row">{state_html}</div>
      </aside>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Task completion</span>
        <h2>Smart chaining is the real feature.</h2>
      </div>
      <div class="grid grid-3">
        {chaining_html}
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Execution loop</span>
        <h2>Each round commits to one next action.</h2>
      </div>
      <div class="timeline">
        {loop_html}
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Guardrails</span>
        <h2>Why Hydra stays controlled.</h2>
      </div>
      <div class="panel">
        <ul class="stack-list">
          {guardrail_html}
        </ul>
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Default runtime budgets</span>
        <h2>Defaults pulled from the current source.</h2>
      </div>
      <div class="runtime-grid">
        {default_cards}
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | Hydra",
        description="Overview of the Hydra AI core that powers Tater Assistant.",
        body=body,
        depth=1,
        nav_key="cerberus",
    )


def render_spudex_page() -> str:
    try:
        settings_defaults = extract_named_literal(SPUDEX_SETTINGS_SOURCE, "DEFAULT_SPUDEX_SETTINGS")
    except Exception:
        settings_defaults = {}
    if not isinstance(settings_defaults, dict):
        settings_defaults = {}

    default_items = [
        ("Enabled by default", "enabled"),
        ("Default platforms", "allowed_platforms"),
        ("Policy enabled", "policy_enabled"),
        ("Approval required", "require_approval"),
        ("File approval required", "require_file_approval"),
        ("Working folder", "default_cwd"),
        ("Max task steps", "max_task_steps"),
        ("Command timeout", "command_timeout_sec"),
        ("Output cap", "max_output_chars"),
    ]

    def format_spudex_default(value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value)

    default_cards = "".join(
        f"""
        <article class="stat-card stat-card-wide">
          <strong>{escape(format_spudex_default(value))}</strong>
          <span>{escape(label)}</span>
        </article>
        """
        for label, key in default_items
        for value in [settings_defaults.get(key, "")]
    )

    feature_cards = [
        (
            "Direct Spudex chat",
            "A console-style chat tab bypasses Hydra and talks directly to the Spudex loop, so the model can run commands, write files, inspect output, search when needed, verify work, and keep context across turns.",
            ["Chat", "Commands", "Context"],
        ),
        (
            "Hydra terminal tools",
            "When enabled for a platform, Hydra can call spudex_run for one command, spudex_task for multi-step terminal work, spudex_status for live state, and spudex_stop to stop a session.",
            ["spudex_run", "spudex_task", "spudex_stop"],
        ),
        (
            "Manual sessions",
            "Operators can run a command manually, choose background execution, watch the log stream, inspect the working folder, and stop the session from the WebUI.",
            ["Manual", "Background", "Logs"],
        ),
        (
            "Tracked processes",
            "Model-started sessions are visible in the Spudex header and details drawer so long-running tasks, small servers, and stuck commands can be reviewed or killed.",
            ["Processes", "Kill", "Details"],
        ),
        (
            "Agent Lab working folder",
            "Spudex resolves its configured working folder under Agent Lab by default, with workspace as the default folder name and file helpers constrained to Agent Lab paths.",
            ["Agent Lab", "workspace", "Files"],
        ),
        (
            "Separate model routing",
            "Settings -> Models can define a dedicated Spudex LLM endpoint and model, letting terminal work use a coding-oriented model without changing the normal Hydra model mix.",
            ["Models", "Endpoint", "Coding"],
        ),
    ]
    feature_html = "".join(
        f"""
        <article class="feature-card">
          <div class="chip-row">{"".join(chip(item) for item in chips)}</div>
          <h3>{escape(title)}</h3>
          <p>{escape(text)}</p>
        </article>
        """
        for title, text, chips in feature_cards
    )

    policy_items = [
        "Enable or disable Spudex globally, then choose which platforms expose the Hydra-facing terminal tools.",
        "Keep the policy layer on for normal use, or tune specific allowances for shells, network commands, installs, containers, host package managers, remote-control tools, host/admin commands, inline eval, and absolute executables.",
        "Require approval for Hydra-triggered command runs, and separately require approval before file changes are accepted.",
        "Limit max task steps, command timeout, output size, retained log entries, and retained sessions from the Spudex settings tab.",
        "The Spudex chat loop receives system information so it can choose Linux, macOS, or Windows-style commands correctly.",
    ]
    policy_html = "".join(f"<li>{escape(item)}</li>" for item in policy_items)

    api_cards = [
        ("GET", "/api/spudex", "Load Spudex state", "Returns settings, platform options, sessions, active counts, tracked processes, and current log metadata for the Spudex tab."),
        ("POST", "/api/spudex/settings", "Save Spudex settings", "Persists enabled state, platform toggles, policy options, approval options, working folder, task limits, timeout, and output limits."),
        ("POST", "/api/spudex/chat/session", "Create a Spudex chat", "Creates a draft chat session with the configured Agent Lab working folder so users can switch between Spudex chats."),
        ("POST", "/api/spudex/chat", "Run a Spudex chat turn", "Runs the direct Spudex loop with conversation context, command execution, file writes, web research, verification, and live session logs."),
        ("POST", "/api/spudex/run", "Run a manual command", "Starts one manual command session from the configured working folder, optionally as a background process."),
        ("GET", "/api/spudex/sessions/{session_id}/logs", "Read session logs", "Streams terminal, assistant, command, system, and verification entries for the selected session."),
        ("POST", "/api/spudex/sessions/{session_id}/stop", "Stop a session", "Requests termination for a running Spudex session or model-started process."),
        ("DELETE", "/api/spudex/sessions/{session_id}", "Close a session", "Removes a retained Spudex session from the visible session list."),
    ]
    api_html = "".join(
        f"""
        <article class="tool-card">
          <div class="chip-row">{chip(method)}{chip(path)}</div>
          <h3>{escape(title)}</h3>
          <p>{escape(text)}</p>
        </article>
        """
        for method, path, title, text in api_cards
    )

    workflow_cards = [
        (
            "Hydra call",
            "A normal chat, voice, or portal turn can expose Spudex tools only when Spudex is enabled for that platform.",
        ),
        (
            "Direct chat",
            "The Spudex tab can talk directly to the Spudex loop, which is useful for iterative command-line work like creating a small website and hosting it.",
        ),
        (
            "Operator review",
            "The same tab shows logs, process state, file-change approvals, session details, and stop controls without needing to leave the WebUI.",
        ),
    ]
    workflow_html = "".join(
        f"""
        <article class="timeline-card">
          <h3>{escape(title)}</h3>
          <p>{escape(text)}</p>
        </article>
        """
        for title, text in workflow_cards
    )

    body = f"""
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Spudex</span>
        <h1>Spudex gives Tater terminal console access with operator controls.</h1>
        <p>
          It is a built-in WebUI workbench and Hydra tool bridge for command-line tasks, scripts, local diagnostics, small hosted apps, and workspace automation.
        </p>
        <div class="action-row">
          {button("Kernel tools", "../kernel-tools/index.html")}
          {button("Hydra", "../cerberus/index.html", ghost=True)}
        </div>
      </div>
      <aside class="panel hero-panel">
        <span class="eyebrow">Default scope</span>
        <p>Spudex starts from an Agent Lab working folder, tracks sessions, and exposes policy toggles so operators decide how much terminal freedom it gets.</p>
      </aside>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Capabilities</span>
        <h2>What Spudex adds to Tater.</h2>
      </div>
      <div class="grid grid-3">
        {feature_html}
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Runtime flow</span>
        <h2>There are two ways into the same console layer.</h2>
      </div>
      <div class="timeline">
        {workflow_html}
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Policy and settings</span>
        <h2>Operators can keep it narrow or open it up.</h2>
      </div>
      <div class="panel">
        <ul class="stack-list">
          {policy_html}
        </ul>
      </div>
      <div class="runtime-grid">
        {default_cards}
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">API surface</span>
        <h2>The WebUI talks to Spudex through local Tater routes.</h2>
      </div>
      <div class="grid grid-2">
        {api_html}
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | Spudex",
        description="Overview of Spudex terminal console access, direct chat, Hydra tools, policies, sessions, and WebUI APIs.",
        body=body,
        depth=1,
        nav_key="spudex",
    )


def render_kernel_page(kernel_tools: list[dict[str, str]]) -> str:
    grouped: dict[str, list[dict[str, str]]] = {}
    for item in kernel_tools:
        grouped.setdefault(item["group"], []).append(item)

    sections: list[str] = []
    for group_name, _tool_ids in KERNEL_TOOL_GROUPS.items():
        rows = grouped.get(group_name, [])
        cards = "".join(
            f"""
            <article class="tool-card">
              <div class="chip-row">{chip(group_name)}</div>
              <h3>{escape(item['id'])}</h3>
              <p>{escape(item['purpose'])}</p>
            </article>
            """
            for item in rows
        )
        sections.append(
            f"""
            <section class="tool-section">
              <div class="section-head">
                <span class="eyebrow">Kernel tools</span>
                <h2>{escape(group_name)}</h2>
              </div>
              <div class="grid grid-2">
                {cards}
              </div>
            </section>
            """
        )

    intro = """
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Built-in capabilities</span>
        <h1>Kernel tools are Tater's native action layer.</h1>
        <p>
          They handle files, web inspection, memory, artifacts, delivery, and optional Spudex terminal console work before Hydra reaches for a Verba.
        </p>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">Why they matter</span>
        <p>Kernel tools let Tater inspect the workspace, search live information, move files, coordinate delivery, and run controlled terminal work through Spudex.</p>
      </aside>
    </section>
    """

    guide_section = render_companion_section(
        WEB_SEARCH_GUIDES,
        "Web search setup",
        "How to enable modular search providers for the search_web kernel tool.",
        "This is a core capability, not a Verba. Download and enable providers from Settings -> Integrations.",
    )

    spudex_note = f"""
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Terminal console</span>
        <h2>Spudex tools are conditional kernel tools.</h2>
      </div>
      <div class="panel">
        <p>
          The spudex_run, spudex_task, spudex_status, and spudex_stop tools appear to Hydra only when Spudex is enabled for the active platform.
          Configure them from the Spudex tab, then use the dedicated Spudex docs for policy, session, and direct-chat behavior.
        </p>
        <div class="action-row">{button("Read Spudex", "../spudex/index.html")}</div>
      </div>
    </section>
    """

    body = intro + "\n".join(sections) + spudex_note + guide_section
    return page_template(
        title="Tater Assistant | Kernel Tools",
        description="Reference for Tater Assistant kernel tools and their purposes.",
        body=body,
        depth=1,
        nav_key="kernel",
    )


def render_plugins_page(plugins: list[dict[str, Any]]) -> str:
    cards = "".join(render_plugin_card(plugin) for plugin in plugins)
    source_copy = (
        "This index reflects the current Tater Shop manifest and Verba files. "
        "Each entry links to a source-backed detail page with usage, portals, and current behavior."
    )
    body = f"""
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Verba reference</span>
        <h1>Actions speak louder then words. {len(plugins)} Verbas are documented here.</h1>
        <p>
          {source_copy}
        </p>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">Filter the list</span>
        <div class="plugins-toolbar">
          <input class="search-input" type="search" placeholder="Search Verbas" data-plugin-search>
          <div class="chip-row filter-row">
            <button class="filter-chip is-active" type="button" data-platform-filter="all">All</button>
            <button class="filter-chip" type="button" data-platform-filter="webui">WebUI</button>
            <button class="filter-chip" type="button" data-platform-filter="discord">Discord</button>
            <button class="filter-chip" type="button" data-platform-filter="telegram">Telegram</button>
          </div>
          <p class="results-copy"><span data-results-count>{len(plugins)}</span> Verbas shown</p>
        </div>
      </aside>
    </section>
    <section class="section">
      <div class="plugin-grid" data-plugin-grid>
        {cards}
      </div>
      <p class="empty-state" data-plugin-empty hidden>No Verbas match the current search and portal filter.</p>
    </section>
    """
    return page_template(
        title="Tater Assistant | Verbas",
        description="Index of Tater Assistant Verbas documented from the current repository snapshot.",
        body=body,
        depth=1,
        nav_key="plugins",
    )


def render_plugin_card(plugin: dict[str, Any]) -> str:
    visible_platforms = clean_platforms(plugin["platforms"])
    platform_label = " ".join(visible_platforms)
    return f"""
    <article
      class="plugin-card"
      data-plugin-card
      data-name="{escape(plugin['title'].lower())}"
      data-description="{escape(plugin['description'].lower())}"
      data-platforms="{escape(platform_label)}"
    >
      <div class="plugin-meta">
        <div class="chip-row">
          {chip(f"v{plugin['version']}")}
          {chip(plugin['id'])}
        </div>
        <h3>{escape(plugin['title'])}</h3>
        <p>{escape(plugin['description'])}</p>
      </div>
      <div class="chip-row platform-row">{render_platform_badges(visible_platforms)}</div>
      <div class="plugin-links">
        {button("Read Verba", f"{plugin['slug']}.html", ghost=True)}
      </div>
    </article>
    """


def render_plugin_detail(plugin: dict[str, Any]) -> str:
    argument_rows = plugin["arguments"]
    if argument_rows:
        argument_html = "".join(
            f"""
            <li>
              <strong>{escape(item['name'])}</strong>
              <span>{escape(item['type'])}</span>
              <p>{escape(item['example'])}</p>
            </li>
            """
            for item in argument_rows
        )
        argument_block = f'<ul class="argument-list">{argument_html}</ul>'
    else:
        argument_block = f"<p>{escape(plugin_arguments_text(plugin))}</p>"

    settings = plugin["required_settings"]
    if settings:
        settings_html = "".join(
            f"""
            <li>
              <strong>{escape(item['key'])}</strong>
              <span>{escape(item['type'] or 'setting')}</span>
              <p>{escape(item['description'] or 'No setting description is present in the current metadata.')}</p>
              {"<small>Default: " + escape(item['default']) + "</small>" if item['default'] else ""}
            </li>
            """
            for item in settings
        )
        settings_block = f'<ul class="argument-list">{settings_html}</ul>'
    else:
        settings_block = f"<p>{escape(plugin_settings_text(plugin))}</p>"

    guide_section = render_companion_section(
        plugin.get("guides") or [],
        "Usage guide",
        "How this plugin fits real-world workflows.",
        "These notes focus on the setup, calling pattern, and runtime behavior that matter most for this plugin.",
    )

    body = f"""
    <section class="hero hero-subpage hero-plugin">
      <div class="hero-copy">
        <span class="eyebrow">Verba profile</span>
        <h1>{escape(plugin['title'])}</h1>
        <p>{escape(plugin['description'])}</p>
        <div class="chip-row">
          {chip(plugin['id'])}
          {chip(f"Version {plugin['version']}")}
        </div>
      </div>
      <aside class="panel hero-panel mascot-panel">
        <span class="eyebrow">Supported portals</span>
        <div class="chip-row">{render_platform_badges(plugin['platforms'])}</div>
      </aside>
    </section>
    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">When to use</span>
          <h2>Best-fit scenarios</h2>
          <p>{escape(plugin['when_to_use'])}</p>
        </article>
        <article class="panel">
          <span class="eyebrow">How to call it</span>
          <h2>Execution guidance</h2>
          <p>{escape(plugin['how_to_use'])}</p>
        </article>
      </div>
    </section>
    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Arguments</span>
          <h2>Input shape</h2>
          {argument_block}
        </article>
        <article class="panel">
          <span class="eyebrow">Settings</span>
          <h2>Required configuration</h2>
          {settings_block}
        </article>
      </div>
    </section>
    {guide_section}
    <section class="section">
      <article class="panel">
        <span class="eyebrow">Example call</span>
        <h2>Canonical usage JSON</h2>
        <pre class="code-block"><code>{escape(plugin['usage_example'])}</code></pre>
      </article>
    </section>
    <section class="section">
      <div class="action-row">
        {button("Back to Verbas", "index.html", ghost=True)}
        {button("Portals", "../portals/index.html", ghost=True)}
        {button("Cores", "../cores/index.html", ghost=True)}
        {button("Kernel tools", "../kernel-tools/index.html", ghost=True)}
        {button("Hydra", "../cerberus/index.html", ghost=True)}
      </div>
    </section>
    """
    return page_template(
        title=f"Tater Assistant | {plugin['title']}",
        description=plugin["description"],
        body=body,
        depth=1,
        nav_key="plugins",
    )


def write_page(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_redirect_page(*, title: str, target: str, label: str) -> str:
    return textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <meta http-equiv="refresh" content="0; url={escape(target)}">
          <link rel="canonical" href="{escape(target)}">
          <title>{escape(title)}</title>
        </head>
        <body>
          <p>{escape(label)} moved to <a href="{escape(target)}">{escape(target)}</a>.</p>
        </body>
        </html>
        """
    )


def cleanup_section_pages(section_dir: Path, keep_slugs: list[str]) -> None:
    if not section_dir.exists():
        return
    keep_files = {"index.html", *[f"{slug}.html" for slug in keep_slugs]}
    for path in section_dir.glob("*.html"):
        if path.name not in keep_files:
            path.unlink(missing_ok=True)


def build() -> None:
    plugins = build_plugins()
    integrations = build_integrations()
    portals = build_platforms(plugins, docs_order=PORTAL_DOCS_ORDER, surface_kind="portal")
    esphome_runtime = build_platforms(plugins, docs_order=["esphome"], surface_kind="runtime")[0]
    cores = build_platforms(plugins, docs_order=CORE_DOCS_ORDER, surface_kind="core")
    kernel_tools = extract_kernel_tools()
    cerberus_defaults = extract_cerberus_defaults()

    firmware_catalog = mirror_latest_firmware(SITE_ROOT)
    print(
        f"Mirrored {firmware_catalog['release']} firmware for "
        f"{len(firmware_catalog['devices'])} satellites."
    )

    write_page(SITE_ROOT / "index.html", render_home_page(plugins, kernel_tools, portals, cores, integrations))
    write_page(SITE_ROOT / "install" / "index.html", render_install_index())
    write_page(SITE_ROOT / "usb-flasher" / "index.html", render_usb_flasher_page())
    write_page(SITE_ROOT / "portals" / "index.html", render_platforms_page(portals))
    write_page(SITE_ROOT / "integrations" / "index.html", render_integrations_page(integrations))
    write_page(
        SITE_ROOT / "tater-voice" / "index.html",
        render_platform_detail(
            esphome_runtime,
            nav_key_override="esphome",
            back_href="../portals/index.html",
            back_label="Back to portals",
        ),
    )
    write_page(
        SITE_ROOT / "esphome" / "index.html",
        render_redirect_page(
            title="Tater Voice moved",
            target="../tater-voice/index.html",
            label="Tater Voice",
        ),
    )
    write_page(SITE_ROOT / "cores" / "index.html", render_cores_page(cores))
    write_page(SITE_ROOT / "cerberus" / "index.html", render_cerberus_page(cerberus_defaults))
    write_page(SITE_ROOT / "spudex" / "index.html", render_spudex_page())
    write_page(SITE_ROOT / "spud-hub" / "index.html", render_spud_hub_page())
    write_page(SITE_ROOT / "llms" / "index.html", render_llms_page())
    write_page(SITE_ROOT / "api" / "index.html", render_openai_api_page())
    write_page(
        SITE_ROOT / "privacy" / "index.html",
        render_redirect_page(
            title="Little Spud privacy policy",
            target="little-spud/index.html",
            label="Little Spud privacy policy",
        ),
    )
    write_page(SITE_ROOT / "privacy" / "little-spud" / "index.html", render_little_spud_privacy_page())
    write_page(SITE_ROOT / "kernel-tools" / "index.html", render_kernel_page(kernel_tools))
    write_page(SITE_ROOT / "plugins" / "index.html", render_plugins_page(plugins))

    cleanup_section_pages(SITE_ROOT / "install", [method["slug"] for method in INSTALL_METHODS])
    cleanup_section_pages(SITE_ROOT / "usb-flasher", [])
    cleanup_section_pages(SITE_ROOT / "portals", [platform["slug"] for platform in portals])
    cleanup_section_pages(SITE_ROOT / "integrations", [integration["slug"] for integration in integrations])
    cleanup_section_pages(SITE_ROOT / "tater-voice", [])
    cleanup_section_pages(SITE_ROOT / "esphome", [])
    cleanup_section_pages(SITE_ROOT / "spudex", [])
    cleanup_section_pages(SITE_ROOT / "spud-hub", [])
    cleanup_section_pages(SITE_ROOT / "llms", [])
    cleanup_section_pages(SITE_ROOT / "api", [])
    cleanup_section_pages(SITE_ROOT / "cores", [core["slug"] for core in cores])
    cleanup_section_pages(SITE_ROOT / "plugins", [plugin["slug"] for plugin in plugins])

    for method in INSTALL_METHODS:
        write_page(SITE_ROOT / "install" / f"{method['slug']}.html", render_install_detail(method))
    for platform in portals:
        write_page(SITE_ROOT / "portals" / f"{platform['slug']}.html", render_platform_detail(platform))
    for integration in integrations:
        write_page(SITE_ROOT / "integrations" / f"{integration['slug']}.html", render_integration_detail(integration))
    for core in cores:
        write_page(SITE_ROOT / "cores" / f"{core['slug']}.html", render_platform_detail(core))
    for plugin in plugins:
        write_page(SITE_ROOT / "plugins" / f"{plugin['slug']}.html", render_plugin_detail(plugin))


if __name__ == "__main__":
    build()
