from __future__ import annotations

import ast
import html
import json
import os
import textwrap
from pathlib import Path
from typing import Any


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
TATER_SHOP_MANIFEST = TATER_SHOP_DIR / "manifest.json"
TATER_README = TATER_DIR / "README.md"

LOGO_SOURCE = TATER_DIR / "images" / "tater-new-logo.png"
WEBUI_SOURCE = TATER_DIR / "images" / "webui.png"
LOGO_TARGET = SITE_ROOT / "assets" / "images" / "tater-logo.png"
WEBUI_TARGET = SITE_ROOT / "assets" / "images" / "webui.png"
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
PLUGIN_DIR = resolve_path("TATER_WIKI_VERBA_DIR", TATER_DIR / "verba")

HOME_ASSISTANT_COMPANIONS = {
    "tater_conversation": {
        "title": "Tater Conversation Agent",
        "summary": "HACS conversation integration that makes Tater selectable as a Home Assistant Assist conversation agent.",
        "chips": ["HACS integration", "Assist pipeline", "Port 8787"],
        "details": [
            "Install the Tater-HomeAssistant repository through HACS as an Integration, then add Tater Conversation in Devices & Services.",
            "The config flow asks for host/IP, port, and an optional API key (when the Home Assistant portal has API auth enabled).",
            "After setup, choose Tater Conversation as the conversation agent in Settings -> Voice Assistants.",
            "The component forwards text plus user, device, area, session, and language context so Tater can keep room-aware and device-aware sessions.",
        ],
        "links": [
            {
                "label": "Tater-HomeAssistant Repo",
                "href": "https://github.com/TaterTotterson/Tater-HomeAssistant",
            },
        ],
    },
}

MACOS_MENU_COMPANION = {
    "title": "Tater Menu (macOS app)",
    "summary": "Lightweight menu-bar app that connects to the Tater macOS bridge for chat, quick actions, clipboard workflows, screen captures, and attachment handling.",
    "chips": ["Status bar app", "Port 8791", "Quick actions"],
    "details": [
        "Install with python3.11 -m pip install -e . inside the Tater-MacOS repo, then run python3.11 tater_menu.py.",
        "It can also run in the background with python3.11 tater_menu.py --background and stays as a menu-bar-only app.",
        "Set Server URL, optional API key/Auth Token, and Quick Action Plugin from the app Settings menu.",
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
        "summary": "Point the app at the macOS bridge and verify bootstrap and polling are healthy.",
        "chips": ["Server URL", "Auth token", "Bootstrap"],
        "details": [
            "Default bridge URL is http://127.0.0.1:8791, but the app can target any reachable Tater host.",
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
        "purpose": "Search the public web through Google's Programmable Search backend after Web Search is configured in Tater WebUI.",
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

WEB_SEARCH_GUIDES = [
    {
        "title": "Create a Google API key",
        "summary": "The search_web kernel tool uses Google's Custom Search JSON API credentials.",
        "chips": ["Google Cloud", "Custom Search JSON API", "API key"],
        "details": [
            "Open Google Cloud Console, create or select a project, then enable Custom Search API under APIs and Services -> Library.",
            "After the API is enabled, go to APIs and Services -> Credentials and create an API key for Tater.",
            "Keep that key handy because Tater's WebUI expects it as the Google API Key for web search.",
        ],
        "links": [
            {
                "label": "Google Cloud Console",
                "href": "https://console.cloud.google.com/",
            },
            {
                "label": "Custom Search JSON API Docs",
                "href": "https://developers.google.com/custom-search/v1/overview",
            },
        ],
    },
    {
        "title": "Create a Search Engine ID (CX)",
        "summary": "Google also requires a Programmable Search Engine and its Search Engine ID.",
        "chips": ["Programmable Search Engine", "CX", "Entire web"],
        "details": [
            "Create a Programmable Search Engine, then open its control panel and enable Search the entire web if you want broad public-web results.",
            "Open the generated search page URL and copy the value after cx=, because that is the Search Engine ID Tater stores.",
            "Tater's core search flow is only ready once both the API key and the CX value are saved.",
        ],
        "links": [
            {
                "label": "Programmable Search Engine",
                "href": "https://programmablesearchengine.google.com/",
            },
        ],
    },
    {
        "title": "Enter the keys in Tater",
        "summary": "Web search is configured from Integrations because it powers a kernel tool, not a Verba.",
        "chips": ["Settings -> Integrations", "Web Search", "Kernel tool"],
        "details": [
            "Open Tater WebUI and go to Settings -> Integrations -> Web Search.",
            "Paste Google API Key and Google Search Engine ID (CX), then save the settings.",
            "The current code stores those values as tater:web_search:google_api_key and tater:web_search:google_cx, with a legacy fallback for older plugin-style settings.",
            "After that, Hydra can call search_web for current web research and article lookup tasks.",
        ],
        "links": [],
    },
    {
        "title": "What the kernel tool supports",
        "summary": "The current search_web implementation accepts a few focused filters on top of the main query.",
        "chips": ["query", "site", "country", "language"],
        "details": [
            "query is required, while num_results, start, site, safe, country, and language are optional.",
            "site narrows results to one domain, country maps to Google's gl parameter, and language maps to lr.",
            "If the Google credentials are missing, the tool returns a configuration error that points operators back to WebUI settings.",
        ],
        "links": [
            {
                "label": "API Reference",
                "href": "https://developers.google.com/custom-search/v1",
            },
        ],
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
                "chips": ["Voice PE", "ESPHome", "Required firmware"],
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
    "moltbook",
    "homeassistant",
    "homekit",
    "macos",
    "xbmc",
]

CORE_DOCS_ORDER = [
    "awareness",
    "ai_task",
    "memory",
    "personal",
    "rss",
]

PLATFORM_DOCS = {
    "webui": {
        "label": "WebUI",
        "description": "FastAPI + static control center for setup, private chat, Verba/Portal/Core management, Hydra tuning, and Redis operations.",
        "role": "Operator console",
        "source": None,
        "plugin_surface": "webui",
        "highlights": [
            "Hosts private chat, Verba browsing, settings, and runtime controls in one place.",
            "First-run Redis setup is handled in-WebUI via popup and stored under .runtime so connection config persists.",
            "Redis settings include connection test/save plus live encryption and decryption controls for in-place data protection.",
            "Hydra settings cover base server pools, optional Beast Mode role routing, and runtime tuning values.",
            "WebUI password login can be enabled from Settings -> General and uses cookie-backed sessions.",
        ],
    },
    "discord": {
        "label": "Discord",
        "description": "Full-featured Discord bot with rich interactions, media output, background jobs, and Verba-backed actions.",
        "role": "Chat endpoint",
        "source": TATER_SHOP_DIR / "portals" / "discord_portal.py",
        "plugin_surface": "discord",
        "highlights": [
            "Supports channel allowlists, DMs, queued notifications, attachments, and slash-style server tooling.",
            "Runs Hydra turns per conversation so multi-step requests stay grounded.",
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
    "homeassistant": {
        "label": "Home Assistant",
        "description": "Voice and text assistant endpoint for Home Assistant Assist, paired with the Tater Conversation Agent integration plus direct smart-home control and a built-in notifications API that can queue alerts and light configured Voice PE indicators.",
        "role": "Voice and smart-home endpoint",
        "source": TATER_SHOP_DIR / "portals" / "homeassistant_portal.py",
        "plugin_surface": "homeassistant",
        "highlights": [
            "Designed for Assist pipeline conversations and direct smart-home control.",
            "Includes session history, follow-up mic behavior, satellite lookup caching, and notification bridging.",
            "Pairs with the Tater Conversation Agent HACS integration, which points Home Assistant Assist at /tater-ha/v1/message and forwards device and area context.",
            "Ships with a built-in notifications API that queues notification payloads in Redis and can light configured Voice PE indicators when new notifications arrive.",
            "Awareness automations now live in Awareness Core instead of a separate automation bridge surface.",
            "Supports optional API key protection for HTTP endpoints using X-Tater-Token.",
        ],
        "companions": [
            HOME_ASSISTANT_COMPANIONS["tater_conversation"],
        ],
        "companions_eyebrow": "Companion setup",
        "companions_title": "Home Assistant integrations that connect to this portal.",
        "companions_intro": "This component lives inside Home Assistant and points Assist conversations back at Tater's runtime bridge.",
        "apis": [
            {
                "method": "GET",
                "path": "/tater-ha/v1/health",
                "summary": "Basic health endpoint for the Home Assistant bridge.",
                "details": "Returns bridge status and version 2.0 so Home Assistant or external checks can confirm the service is up.",
            },
            {
                "method": "POST",
                "path": "/tater-ha/v1/notifications/add",
                "summary": "Queue a Home Assistant-facing notification item.",
                "details": "Accepts source, title, type, message, entity_id, ha_time, level, and data, stores the item in Redis, attempts to turn on configured Voice PE light entities, and enforces X-Tater-Token when API auth is enabled.",
            },
            {
                "method": "GET",
                "path": "/tater-ha/v1/notifications",
                "summary": "Pull and clear queued notifications.",
                "details": "Reads queued notifications from Redis, clears the list after delivery, turns Voice PE indicators off once notifications are consumed (or immediately if none are present), and enforces X-Tater-Token when API auth is enabled.",
            },
            {
                "method": "POST",
                "path": "/tater-ha/v1/message",
                "summary": "Main Assist/chat message endpoint.",
                "details": "Receives Home Assistant conversation requests, preserves stable session context, and runs Hydra turns with Home Assistant-scoped system prompting and plugin gating.",
            },
        ],
    },
    "homekit": {
        "label": "HomeKit",
        "description": "Siri and Apple Shortcuts bridge for a full Siri-to-Tater round-trip, with per-device sessions, Shortcut-friendly JSON, and optional auth protection.",
        "role": "Voice endpoint",
        "source": TATER_SHOP_DIR / "portals" / "homekit_portal.py",
        "plugin_surface": "homekit",
        "highlights": [
            "Provides a lightweight HTTP bridge for Siri and Apple Shortcuts workflows.",
            "Designed for Shortcut-driven voice loops where Siri captures speech, posts JSON to Tater, then speaks the reply back aloud.",
            "Maintains per-device conversation sessions instead of treating every request as stateless.",
            "Supports optional API key protection so Shortcuts must send X-Tater-Token when enabled.",
            "Good fit for Apple-first households that want voice access without a full chat client.",
        ],
        "guides": [
            {
                "title": "Premade shortcut",
                "summary": "A ready-made Apple Shortcut already exists for the HomeKit bridge.",
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
                    "Use Get Contents of URL to POST JSON to http://YOUR-TATER-IP:8789/tater-homekit/v1/message with text and session_id fields.",
                    "Extract the reply key from the JSON response, then feed it into Speak Text so Siri or a HomePod reads it back.",
                ],
            },
            {
                "title": "Session IDs and auth",
                "summary": "Each device should use its own session_id, and protected bridges can require the X-Tater-Token header.",
                "chips": ["session_id", "X-Tater-Token", "Per-device memory"],
                "details": [
                    "Use a stable session_id such as iphone, ipad, or bedroom_homepod so conversations do not mix between devices.",
                    "If API auth is enabled in Tater HomeKit settings, add an X-Tater-Token header inside the shortcut request.",
                    "The bridge keeps short Siri-friendly session history in Redis using the configured session TTL and history limits.",
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
        "description": "Native desktop bridge used by the Tater Menu status-bar app for chat, quick actions, notification polling, and attachment workflows.",
        "role": "Desktop endpoint",
        "source": TATER_SHOP_DIR / "portals" / "macos_portal.py",
        "plugin_surface": "macos",
        "highlights": [
            "Runs a FastAPI bridge on port 8791 by default for the Tater Menu app.",
            "Maintains scoped session history with configurable limits and TTL so desktop context stays stable but bounded.",
            "Supports long-poll notifications plus tool_wait status handling for menu-app feedback loops.",
            "Includes asset upload and download endpoints for screen captures, clipboard artifacts, and returned files.",
            "Supports optional API key protection through the X-Tater-Token header.",
        ],
        "companions": [
            MACOS_MENU_COMPANION,
        ],
        "companions_eyebrow": "Client app",
        "companions_title": "macOS app that connects to this bridge.",
        "companions_intro": "The menu-bar app is the main user-facing client for this portal and handles quick actions, chat UI, and attachment flows.",
        "guides": MACOS_APP_GUIDES,
        "guides_eyebrow": "App setup",
        "guides_title": "How to run and connect the Tater Menu app.",
        "guides_intro": "These notes are based on the current Tater-MacOS app README and the active macOS bridge endpoints.",
        "apis": [
            {
                "method": "GET",
                "path": "/macos/health",
                "summary": "Health check for the desktop bridge.",
                "details": "Returns ok, platform=macos, and version 1.0 so clients can confirm the bridge is alive.",
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
        "label": "ESPHome",
        "description": "Built-in ESPHome device runtime inside Tater for VoicePE, Sat1, and future native devices, with satellites, live entities, logs, stats, and the full voice pipeline on the main app port.",
        "role": "Native device runtime",
        "source": None,
        "plugin_surface": "voice_core",
        "hero_eyebrow": "Native ESPHome",
        "hero_panel_eyebrow": "What it powers",
        "hero_panel_text": "ESPHome is now a built-in Tater runtime. It owns Tater Voice devices, ESPHome satellites, the live voice pipeline, and the operator controls under Settings -> ESPHome.",
        "role_eyebrow": "Why it matters",
        "role_title": "What native ESPHome unlocks",
        "role_text": "Tater now owns the full ESPHome voice experience directly: discovery, room-aware voice sessions, live device state, and on-device playback all run inside the main app instead of a downloadable core.",
        "highlights_eyebrow": "Feature set",
        "highlights_title": "What makes the built-in ESPHome stack feel like a real voice system",
        "plugin_eyebrow": "Voice-aware verbas",
        "plugin_title": "Verbas that can act on the speaking device",
        "settings_eyebrow": "Operator controls",
        "settings_title": "How operators use it in Tater",
        "highlights": [
            "Built into Tater itself, always on, and served from the main app port rather than a separate external voice service.",
            "Settings -> ESPHome now owns Satellites, Settings, and Stats so operators can manage discovery, pairing, rooms, logs, live entities, and voice metrics in one place.",
            "Shared speech backends live in Settings -> Models, with Faster Whisper, Vosk, Wyoming, Kokoro, Pocket TTS, Piper, and Home Assistant announcement TTS available where they make sense.",
            "Runtime model files auto-download into agent_lab/models/stt and agent_lab/models/tts so rebuilds do not require hand-seeding models.",
            "Live entity views expose sensors plus writable controls such as switches, buttons, numbers, selects, lights, and RGB color when the device supports it.",
            "Per-device logs, stats, room awareness, and direct playback make Tater Voice hardware feel local to the room instead of remote to the browser.",
        ],
        "guides": [
            {
                "title": "Native ESPHome runtime",
                "summary": "ESPHome is no longer a shop core. It is part of the main Tater app and starts with Tater.",
                "chips": ["Built in", "One app", "Main port"],
                "details": [
                    "The old external voice runtime has been folded into Tater's built-in ESPHome runtime so the voice stack no longer depends on a separate downloadable core or its own HTTP listener.",
                    "That keeps the device lifecycle simpler: discovery, session handling, playback URLs, and operator screens now all live inside the same main application.",
                    "This built-in shape also leaves room for future ESPHome device types beyond the current voice-pipeline hardware.",
                ],
            },
            {
                "title": "Voice pipeline and shared models",
                "summary": "The live voice loop uses shared STT/TTS choices from the Models tab while keeping ESPHome-specific controls in one native screen.",
                "chips": ["Models tab", "STT", "TTS"],
                "details": [
                    "STT can use Faster Whisper, Vosk, or Wyoming depending on the install and hardware, while TTS can use Wyoming, Kokoro, Pocket TTS, or Piper.",
                    "Announcement flows can still bridge to Home Assistant API TTS when that is the right delivery path, but device-local voice replies stay inside Tater's built-in runtime.",
                    "Because models auto-download into agent_lab/models, first-run setup is much smoother on fresh installs and bind-mounted Docker deployments.",
                ],
            },
            {
                "title": "Runtime observability",
                "summary": "The ESPHome screen now separates devices, settings, and stats so tuning is based on real behavior instead of guesswork.",
                "chips": ["Satellites", "Stats", "Live logs"],
                "details": [
                    "Satellites shows discovered devices, saved room assignments, live entity state, device facts, and an ESPHome-style live log console.",
                    "Stats surfaces wake behavior, no-op rates, false wakes, backend latency, fallback usage, and per-device voice summaries for tuning.",
                    "Writable entity controls are available inline for things like switches, lights, numbers, buttons, and select options.",
                ],
            },
            {
                "title": "Experimental voice features",
                "summary": "Optional experimental toggles let operators test more aggressive voice behavior on hardware that can support it.",
                "chips": ["Experimental", "Partial STT", "Early-start TTS"],
                "details": [
                    "Experimental Partial STT can keep partial transcript state during live capture so the system gets earlier visibility into what the user is saying.",
                    "Experimental Early-Start TTS can begin speaking long replies sooner by preparing smaller response chunks before the whole answer is finished.",
                    "Experimental Live Tool Progress Speech lets Tater speak Hydra tool-progress lines during the thinking phase instead of waiting until the final answer.",
                ],
            },
        ],
        "guides_eyebrow": "Voice experience",
        "guides_title": "How native ESPHome makes Tater feel like a real device assistant.",
        "guides_intro": "These notes focus on the built-in ESPHome runtime, the live voice pipeline, shared speech backends, and the operator tools now living directly inside Tater.",
        "apis": [
            {
                "method": "GET",
                "path": "/api/settings/esphome/runtime",
                "summary": "Load the native ESPHome runtime view used by Settings -> ESPHome.",
                "details": "Returns the current Satellites, Settings, and Stats payload so the WebUI can render discovery state, device cards, voice metrics, and runtime controls.",
            },
            {
                "method": "POST",
                "path": "/api/settings/esphome/runtime/action",
                "summary": "Run a native ESPHome runtime action from the WebUI.",
                "details": "Handles refresh, connect/disconnect, save/forget satellite actions, live log lifecycle, and direct entity-control actions from the ESPHome settings screen.",
            },
            {
                "method": "GET",
                "path": "/tater-ha/v1/voice/native/status",
                "summary": "Inspect current voice-pipeline runtime state and backend availability.",
                "details": "Returns selected speech backends, effective fallback state, model roots, discovery state, selector sessions, and availability of local STT/TTS backends.",
            },
            {
                "method": "POST",
                "path": "/tater-ha/v1/voice/esphome/entities",
                "summary": "Fetch live ESPHome entity rows for one connected satellite.",
                "details": "Returns the live entity snapshot so verbas and operators can inspect sensors, buttons, numbers, switches, lights, and other exposed device entities.",
            },
            {
                "method": "POST",
                "path": "/tater-ha/v1/voice/esphome/entities/command",
                "summary": "Command a writable ESPHome entity on one satellite.",
                "details": "Supports button, number, switch, select, text, and light-control actions so device-local flows can act directly on the speaking device.",
            },
            {
                "method": "POST",
                "path": "/tater-ha/v1/voice/esphome/play",
                "summary": "Queue direct audio playback on a selected ESPHome satellite.",
                "details": "Used for device-local playback flows such as announcements, generated audio, and other responses that should play on the speaking satellite itself.",
            },
        ],
    },
    "awareness": {
        "label": "Awareness Core",
        "description": "Home awareness automation core for camera, doorbell, entry-sensor, and brief workflows with Redis-backed event history.",
        "role": "Home awareness engine",
        "source": TATER_SHOP_DIR / "cores" / "awareness_core.py",
        "plugin_surface": "",
        "highlights": [
            "Replaces the old HA automations bridge with an in-core awareness runtime.",
            "Connects to Home Assistant state changes and runs camera, doorbell, and entry-sensor rules directly.",
            "Stores newest-first events in Redis with source area context, timestamps, and metadata for later querying.",
            "Camera and doorbell paths support snapshot + vision summaries, with optional notifications and TTS routing.",
            "Entry sensors log both open and closed events, with open-only notifications and optional open-only TTS.",
            "Brief jobs generate compact text updates (events/weather/greetings) on schedules for dashboard-style use.",
        ],
        "apis": [],
    },
    "ai_task": {
        "label": "AI Task Runner",
        "description": "Built-in scheduled task runner for timed and recurring AI jobs with delivery routed through notifier portals.",
        "role": "Scheduler",
        "source": TATER_SHOP_DIR / "cores" / "ai_task_core.py",
        "plugin_surface": "",
        "highlights": [
            "Executes recurring jobs without requiring an external scheduler around Tater.",
            "Routes output through supported notifier portals so scheduled results can land where users already are.",
            "Best paired with concise task prompts and target-specific delivery rules.",
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
            "Includes confidence thresholds, identity linking options, and context-size limits.",
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
    "label": "ESPHome Voice",
    "description": "Built-in ESPHome voice runtime inside Tater.",
}

INSTALL_METHODS = [
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
            "Persistent Agent Lab and .runtime storage matters so updates do not wipe workspace data, Redis setup/encryption state, or auto-downloaded voice models.",
        ],
        "steps": [
            "Open Unraid Community Apps and install Redis Stack.",
            "Install Tater from the Community Apps store.",
            "Add persistent path mappings for /app/agent_lab and /app/.runtime inside the container (for example /mnt/user/appdata/tater/agent_lab and /mnt/user/appdata/tater/runtime).",
            "Optional but recommended: set TZ and map /etc/localtime + /etc/timezone for local container time.",
            "Start the containers and finish configuration in the WebUI.",
        ],
        "notes": [
            "Without /app/agent_lab mapping, Agent Lab data and downloaded STT/TTS voice models can be lost on rebuild/update.",
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
            "Optional HACS integration: Tater Conversation Agent for Assist conversations.",
        ],
        "steps": [
            "Add the Tater add-on repository: https://github.com/TaterTotterson/hassio-addons-tater",
            "Install and start Redis Stack first.",
            "Install Tater AI Assistant second.",
            "Start Tater and open the WebUI ingress page.",
            "Complete Redis setup in the popup if prompted, then configure Hydra model settings in WebUI.",
            "Verify the WebUI and Home Assistant bridges are reachable.",
        ],
        "notes": [
            "Tater-HomeAssistant is the Home Assistant conversation component that points Assist at Tater's /tater-ha/v1/message bridge endpoint.",
            "Awareness automations now run in Awareness Core inside Tater rather than a separate automation bridge endpoint.",
            "Home Assistant integration supports optional API key entry when portal API auth is enabled.",
            "For brief-style automation output, input_text helpers are the recommended storage target inside Home Assistant.",
        ],
        "companions": [
            HOME_ASSISTANT_COMPANIONS["tater_conversation"],
        ],
        "snippets": [
            {
                "label": "Conversation integration target",
                "code": "host: YOUR_TATER_HOST\nport: 8787\napi_key: OPTIONAL_PORTAL_API_KEY",
            },
            {
                "label": "Dashboard markdown card",
                "code": """### Front Yard Activity
{{ states('input_text.event_brief') or 'No activity yet.' }}

### Weather
{{ states('input_text.weather_brief') or 'No weather summary yet.' }}

### Zen Message
{{ states('input_text.zen_message') or 'Take a breath.' }}""",
            },
        ],
        "links": [
            {
                "label": "Add-on Repository",
                "href": "https://github.com/TaterTotterson/hassio-addons-tater",
            },
            {
                "label": "Tater-HomeAssistant",
                "href": "https://github.com/TaterTotterson/Tater-HomeAssistant",
            },
        ],
    },
    {
        "slug": "local",
        "title": "Local Python Install",
        "eyebrow": "Advanced local setup",
        "summary": "Run Tater from source with Python 3.11 and Redis Stack, then configure Redis/Hydra in WebUI.",
        "best_for": "Developers and operators who want direct source control and local customization.",
        "complexity": "Medium",
        "highlights": [
            "Requires Python 3.11, Redis Stack, and an OpenAI-compatible LLM backend such as Ollama, LocalAI, LM Studio, Lemonade, or OpenAI API.",
            "The README recommends running inside a virtual environment to keep dependencies isolated.",
            "Redis is no longer configured in .env; connection setup is handled in-WebUI and saved in .runtime.",
        ],
        "steps": [
            "Clone the repository.",
            "Change into the Tater project directory.",
            "Create and activate a Python virtual environment.",
            "Install dependencies from requirements.txt.",
            "Launch TaterOS and complete Redis setup in the popup (host/port/auth/TLS).",
            "Configure Hydra LLM base server(s) and optional Beast Mode role routing in Settings.",
        ],
        "notes": [
            "Redis connection settings are saved locally in .runtime/redis_connection.json, while downloaded speech models live under agent_lab/models.",
            "Redis encryption keys and live-encryption state are stored under .runtime when Redis encryption is enabled in Settings.",
            "This path is the best fit when you want to inspect or modify the source directly.",
        ],
        "snippets": [
            {
                "label": "Clone and prepare environment",
                "code": """git clone https://github.com/TaterTotterson/Tater.git
cd Tater
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt""",
            },
            {
                "label": "Run TaterOS backend + WebUI",
                "code": "uvicorn tateros_app:app --host 0.0.0.0 --port 8501 --reload --no-access-log",
            },
            {
                "label": "Alternative launcher",
                "code": "sh run_ui.sh",
            },
        ],
        "links": [],
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
            "Container persistence warnings now include both /app/agent_lab and /app/.runtime host mappings, which also preserve downloaded voice models.",
            "The container exposes the WebUI on port 8501 and several Tater service ports in the README example.",
        ],
        "steps": [
            "Pull the published image.",
            "Start the container with required port and volume mappings.",
            "Mount /app/agent_lab and /app/.runtime to host storage so runtime and Redis config persist across rebuilds.",
            "Open the WebUI and complete Redis setup popup if prompted.",
            "Configure Hydra base model settings and optional Beast Mode role routing in Settings.",
            "Open the WebUI at http://localhost:8501 after the container is running.",
        ],
        "notes": [
            "If /app/agent_lab is not mounted, runtime data and downloaded Faster Whisper/Vosk/Kokoro/Pocket TTS/Piper models can be lost on rebuild/update.",
            "If /app/.runtime is not mounted, Redis setup popup config and Redis encryption key/state can be lost on rebuild/update.",
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
  -p 8787:8787 \\
  -p 8788:8788 \\
  -p 8789:8789 \\
  -p 8790:8790 \\
  -e TZ=America/Chicago \\
  -v /etc/localtime:/etc/localtime:ro \\
  -v /etc/timezone:/etc/timezone:ro \\
  -v /tater_agent_lab:/app/agent_lab \\
  -v /tater_runtime:/app/.runtime \\
  ghcr.io/tatertotterson/tater:latest""",
            },
            {
                "label": "Docker run (same ports/volumes, alternate host paths)",
                "code": """docker run -d --name tater_webui \\
  -p 8501:8501 \\
  -p 8787:8787 \\
  -p 8788:8788 \\
  -p 8789:8789 \\
  -p 8790:8790 \\
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
            "platforms": list(entry.get("portals") or []),
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

    platforms = [str(item).strip().lower() for item in entry.get("portals") or [] if str(item).strip()]
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
        relative_entry = str(entry.get("entry") or "").strip()
        source_path = (TATER_SHOP_DIR / relative_entry).resolve() if relative_entry else None
        if source_path and source_path.exists():
            plugin = extract_plugin_metadata(source_path)
        else:
            plugin = manifest_fallback_plugin(entry)
        rows.append(merge_shop_manifest(plugin, entry))
    return sorted(rows, key=lambda item: item["title"].lower())


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
    platforms = [str(item).strip().lower() for item in raw.get("portals") or [] if str(item).strip()]
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

    ids = sorted(str(item) for item in (tool_ids or []))
    rows: list[dict[str, str]] = []
    for tool_id in ids:
        overrides = KERNEL_TOOL_OVERRIDES.get(tool_id, {})
        rows.append(
            {
                "id": tool_id,
                "purpose": str(
                    overrides.get("purpose")
                    or (purposes or {}).get(tool_id)
                    or tool_id.replace("_", " ")
                ).strip(),
                "usage": pretty_json_string(
                    str(
                        overrides.get("usage")
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
        ("DEFAULT_STEP_RETRY_LIMIT", "Step retry limit", ""),
        ("DEFAULT_MAX_LEDGER_ITEMS", "Max ledger items", ""),
        ("DEFAULT_ASTRAEUS_PLAN_REVIEW_ENABLED", "Astraeus second plan check", ""),
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
    nav_items = [
        ("home", "Home", f"{base}index.html"),
        ("install", "Install", f"{base}install/index.html"),
        ("cerberus", "Hydra", f"{base}cerberus/index.html"),
        ("portals", "Portals", f"{base}portals/index.html"),
        ("esphome", "ESPHome", f"{base}esphome/index.html"),
        ("cores", "Cores", f"{base}cores/index.html"),
        ("kernel", "Kernel Tools", f"{base}kernel-tools/index.html"),
        ("plugins", "Verbas", f"{base}plugins/index.html"),
    ]
    nav_html = "\n".join(
        f'<a class="nav-link{" is-active" if key == nav_key else ""}" href="{href}">{label}</a>'
        for key, label, href in nav_items
    )
    nav_html += "\n" + '<a class="nav-link nav-link-github" href="https://github.com/TaterTotterson/Tater" target="_blank" rel="noreferrer">GitHub</a>'
    return textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <meta name="description" content="{escape(description)}">
          <title>{escape(title)}</title>
          <link rel="stylesheet" href="{base}assets/site.css">
          <script src="{base}assets/site.js" defer></script>
        </head>
        <body data-page="{escape(nav_key)}">
          <div class="page-shell">
            <header class="site-header">
              <a class="brand" href="{base}index.html">
                <img src="{base}assets/images/tater-logo.png" alt="Tater Assistant logo">
                <span class="brand-copy">
                  <strong>Tater Assistant</strong>
                  <small>Source-backed docs</small>
                </span>
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
              <p>Built from the current Tater source snapshot in this repository.</p>
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


def render_platform_badges(platforms: list[str]) -> str:
    if not platforms:
        return '<span class="chip">No portals listed</span>'
    return "".join(chip(PLATFORM_META.get(name, {"label": name.replace("_", " ").title()})["label"]) for name in platforms)


def platform_settings_chip(platform: dict[str, Any]) -> str:
    if platform["slug"] == "webui":
        return "Configured in app"
    if platform["slug"] == "esphome":
        return "Settings -> ESPHome"
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
        return "Desktop bridge"
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
            "ESPHome is configured through Settings -> ESPHome for Satellites, Settings, and Stats, while shared STT/TTS model choices live in Settings -> Models. "
            "The runtime is built into the main Tater app rather than a separate downloadable core."
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
            "macOS is a desktop bridge portal used by the Tater Menu app. It can execute compatible Verbas "
            "through /macos/plugin even when plugin inventory tags for macos are sparse."
        )
    if platform["slug"] == "esphome":
        return (
            "ESPHome is a built-in runtime surface. Verbas currently advertise speaking-device support through the voice_core platform tag, which Tater now maps onto the native ESPHome speaking-device context, room assignment, and live entity access."
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
) -> str:
    plugin_count = len(plugins)
    kernel_count = len(kernel_tools)
    portal_count = len(portals)
    surface_count = portal_count
    install_count = len(INSTALL_METHODS)

    hero = f"""
    <section class="hero hero-home">
      <div class="hero-copy">
        <span class="eyebrow">Source-backed wiki</span>
        <h1>Tater is an AI assistant built to act.</h1>
        <p>
          Hydra plans the work, chains kernel tools with Verbas, and finishes tasks across chat,
          smart-home, direct voice devices, media, and automation workflows.
        </p>
        <div class="action-row">
          {button("Install Tater", "install/index.html")}
          {button("Explore portals", "portals/index.html")}
          {button("ESPHome", "esphome/index.html", ghost=True)}
          {button("Explore cores", "cores/index.html")}
          {button("Explore Verbas", "plugins/index.html")}
          {button("Read Hydra", "cerberus/index.html", ghost=True)}
        </div>
      </div>
      <aside class="hero-art">
        <div class="orbital-frame">
          <img src="assets/images/tater-logo.png" alt="Tater Assistant emblem">
        </div>
        <div class="hero-stats">
          <div class="stat-card"><strong>{plugin_count}</strong><span>documented Verbas</span></div>
          <div class="stat-card"><strong>{kernel_count}</strong><span>kernel tools</span></div>
          <div class="stat-card"><strong>{surface_count}</strong><span>portals</span></div>
          <div class="stat-card"><strong>{install_count}</strong><span>install paths</span></div>
        </div>
      </aside>
    </section>
    """

    feature_cards = [
        (
            "Smart chaining",
            "Hydra breaks work into steps, picks the next tool, and keeps going until the task is done.",
        ),
        (
            "Native ESPHome voice",
            "ESPHome is now built into Tater, powering VoicePE and Sat1 devices with room-aware voice sessions, live entities, direct playback, logs, and native operator screens.",
        ),
        (
            "Shared STT and TTS",
            "The Models tab now holds the shared speech stack: Faster Whisper, Vosk, Wyoming, Kokoro, Pocket TTS, Piper, plus Home Assistant announcement TTS when needed.",
        ),
        (
            "Voice pipeline experiments",
            "Optional experimental toggles can enable live partial STT, early-start TTS, and live Hydra tool-progress speech on hardware that can support them.",
        ),
        (
            "Beast Mode routing",
            "Base servers can run normal AI calls while Chat/Astraeus/Thanatos/Minos/Hermes optionally route to per-head models.",
        ),
        (
            "Redis control + encryption",
            "Redis setup, connectivity checks, and live encrypt/decrypt controls are managed directly in WebUI settings.",
        ),
        (
            "API key protection",
            "Portal HTTP bridges can be locked behind X-Tater-Token so companion apps and integrations use shared API keys.",
        ),
        (
            "Core layer",
            "Built-in tools handle files, web research, memory, images, notes, attachments, and delivery.",
        ),
        (
            "Verbas",
            "Actions speak louder then words. Verbas extend Tater into smart-home, media, camera, note, download, and admin workflows.",
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

    home_cores = [core for core in cores if core.get("slug") != "awareness"]

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
        <h3>ESPHome tab</h3>
        <p>Built-in voice runtime docs for satellites, live entities, and playback flows.</p>
        {button("Open ESPHome", "esphome/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Core docs</h3>
        <p>Built-in runtime services such as awareness automation, scheduling, memory, personal email intelligence, and RSS monitoring.</p>
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
        <span class="eyebrow">WebUI snapshot</span>
        <h2>The operator side is live.</h2>
        <p>
          The WebUI handles setup, chat, plugin browsing, settings, Hydra runtime controls, and Redis encryption in one place.
        </p>
      </div>
      <div class="screenshot-frame">
        <img src="assets/images/webui.png" alt="Tater WebUI screenshot">
      </div>
    </div>
    """

    body = f"""
    {hero}
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">What Tater does</span>
        <h2>Tater plans, acts, and connects across your stack.</h2>
      </div>
      <div class="grid grid-4">
        {feature_html}
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <span class="eyebrow">Portals + cores</span>
        <h2>One assistant. Verbas, portals, and cores.</h2>
      </div>
      <h3>Portals</h3>
      <div class="grid grid-3">
        {portal_cards}
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
        description="Overview of Tater Assistant, supported portals, and the current wiki structure.",
        body=body,
        depth=0,
        nav_key="home",
    )


def render_install_index() -> str:
    readme_note = extract_install_readme_note()
    cards = "".join(
        f"""
        <article class="platform-card platform-card-detail">
          <div class="chip-row">
            {chip(method['complexity'])}
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
          Tater ships with four main setup paths: Unraid, Home Assistant, local Python, and Docker.
        </p>
      </div>
      <aside class="panel hero-panel">
        <span class="eyebrow">README note</span>
        <p>{escape(readme_note)}</p>
        <div class="action-row">
          {button("ESPHome tab", "../esphome/index.html", ghost=True)}
        </div>
      </aside>
    </section>
    <section class="section">
      <div class="grid grid-2">
        {cards}
      </div>
    </section>
    """
    return page_template(
        title="Tater Assistant | Install",
        description="Installation paths for Tater Assistant from the current README.",
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
        "Home Assistant extras",
        "Optional HACS integrations for Assist conversations.",
        "After the add-on is running, these Home Assistant-side integrations connect Assist flows back to Tater's portal endpoints.",
    )
    guide_section = render_companion_section(
        method.get("guides") or [],
        "Workflow setup",
        "Patterns for storing brief helper output in Home Assistant.",
        "These patterns matter most when you want compact text summaries to stay visible in helpers, dashboards, and routines.",
    )
    links_html = "".join(
        button(link["label"], link["href"], ghost=True)
        for link in method["links"]
    )

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
          {chip(method['complexity'])}
        </div>
      </div>
      <aside class="panel hero-panel">
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
          Portals are chat, voice, and integration entry points that route requests into Hydra and Verbas.
        </p>
      </div>
      <aside class="panel hero-panel">
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
        <h1>Tater cores power built-in runtime services.</h1>
        <p>
          Cores are always-on internal services like awareness automation, scheduling, memory extraction, personal email intelligence, and feed monitoring.
        </p>
      </div>
      <aside class="panel hero-panel">
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
            "homeassistant",
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
          <div class="screenshot-frame">
            <img src="../assets/images/webui.png" alt="Tater WebUI screenshot">
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
      <aside class="panel hero-panel">
        <span class="eyebrow">{escape(hero_panel_eyebrow)}</span>
        <p>{escape(hero_panel_text)}</p>
        {source_note}
      </aside>
    </section>
    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">{escape(role_eyebrow)}</span>
          <h2>{escape(role_title)}</h2>
          <p>{escape(role_text)}</p>
        </article>
        <article class="panel">
          <span class="eyebrow">{escape(highlights_eyebrow)}</span>
          <h2>{escape(highlights_title)}</h2>
          <ul class="stack-list">{highlight_html}</ul>
        </article>
      </div>
    </section>
    <section class="section">
      <div class="detail-grid">
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
        {button("ESPHome", "../esphome/index.html", ghost=True)}
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
            "Hydra can read files, search the web, inspect pages, search local code, manage memory, and attach artifacts before it ever needs a custom extension.",
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
      <aside class="panel hero-panel">
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
          They handle files, web inspection, memory, artifacts, and delivery before Hydra reaches for a Verba.
        </p>
      </div>
      <aside class="panel hero-panel">
        <span class="eyebrow">Why they matter</span>
        <p>Kernel tools let Tater inspect the workspace, search live information, move files, and coordinate delivery on its own.</p>
      </aside>
    </section>
    """

    guide_section = render_companion_section(
        WEB_SEARCH_GUIDES,
        "Web search setup",
        "How to enable Google's search backend for the search_web kernel tool.",
        "This is a core capability, not a Verba. The current Tater WebUI path is Settings -> Integrations -> Web Search.",
    )

    body = intro + "\n".join(sections) + guide_section
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
      <aside class="panel hero-panel">
        <span class="eyebrow">Filter the list</span>
        <div class="plugins-toolbar">
          <input class="search-input" type="search" placeholder="Search Verbas" data-plugin-search>
          <div class="chip-row filter-row">
            <button class="filter-chip is-active" type="button" data-platform-filter="all">All</button>
            <button class="filter-chip" type="button" data-platform-filter="webui">WebUI</button>
            <button class="filter-chip" type="button" data-platform-filter="discord">Discord</button>
            <button class="filter-chip" type="button" data-platform-filter="homeassistant">Home Assistant</button>
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
    platform_label = " ".join(plugin["platforms"])
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
      <div class="chip-row platform-row">{render_platform_badges(plugin['platforms'])}</div>
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
      <aside class="panel hero-panel">
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


def cleanup_section_pages(section_dir: Path, keep_slugs: list[str]) -> None:
    if not section_dir.exists():
        return
    keep_files = {"index.html", *[f"{slug}.html" for slug in keep_slugs]}
    for path in section_dir.glob("*.html"):
        if path.name not in keep_files:
            path.unlink(missing_ok=True)


def build() -> None:
    plugins = build_plugins()
    portals = build_platforms(plugins, docs_order=PORTAL_DOCS_ORDER, surface_kind="portal")
    esphome_runtime = build_platforms(plugins, docs_order=["esphome"], surface_kind="runtime")[0]
    cores = build_platforms(plugins, docs_order=CORE_DOCS_ORDER, surface_kind="core")
    kernel_tools = extract_kernel_tools()
    cerberus_defaults = extract_cerberus_defaults()

    write_page(SITE_ROOT / "index.html", render_home_page(plugins, kernel_tools, portals, cores))
    write_page(SITE_ROOT / "install" / "index.html", render_install_index())
    write_page(SITE_ROOT / "portals" / "index.html", render_platforms_page(portals))
    write_page(
        SITE_ROOT / "esphome" / "index.html",
        render_platform_detail(
            esphome_runtime,
            nav_key_override="esphome",
            back_href="../portals/index.html",
            back_label="Back to portals",
        ),
    )
    write_page(SITE_ROOT / "cores" / "index.html", render_cores_page(cores))
    write_page(SITE_ROOT / "cerberus" / "index.html", render_cerberus_page(cerberus_defaults))
    write_page(SITE_ROOT / "kernel-tools" / "index.html", render_kernel_page(kernel_tools))
    write_page(SITE_ROOT / "plugins" / "index.html", render_plugins_page(plugins))

    cleanup_section_pages(SITE_ROOT / "install", [method["slug"] for method in INSTALL_METHODS])
    cleanup_section_pages(SITE_ROOT / "portals", [platform["slug"] for platform in portals])
    cleanup_section_pages(SITE_ROOT / "esphome", [])
    cleanup_section_pages(SITE_ROOT / "cores", [core["slug"] for core in cores])
    cleanup_section_pages(SITE_ROOT / "plugins", [plugin["slug"] for plugin in plugins])

    for method in INSTALL_METHODS:
        write_page(SITE_ROOT / "install" / f"{method['slug']}.html", render_install_detail(method))
    for platform in portals:
        write_page(SITE_ROOT / "portals" / f"{platform['slug']}.html", render_platform_detail(platform))
    for core in cores:
        write_page(SITE_ROOT / "cores" / f"{core['slug']}.html", render_platform_detail(core))
    for plugin in plugins:
        write_page(SITE_ROOT / "plugins" / f"{plugin['slug']}.html", render_plugin_detail(plugin))


if __name__ == "__main__":
    build()
