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

LOGO_SOURCE = TATER_DIR / "images" / "tater-new-logo.png"
WEBUI_SOURCE = TATER_DIR / "images" / "webui.png"
LOGO_TARGET = SITE_ROOT / "assets" / "images" / "tater-logo.png"
WEBUI_TARGET = SITE_ROOT / "assets" / "images" / "webui.png"

CERBERUS_SOURCE = TATER_DIR / "cerberus" / "__init__.py"
TOOL_RUNTIME_SOURCE = TATER_DIR / "tool_runtime.py"
PLUGIN_DIR = TATER_DIR / "plugins"

HOME_ASSISTANT_COMPANIONS = {
    "tater_conversation": {
        "title": "Tater Conversation Agent",
        "summary": "HACS conversation integration that makes Tater selectable as a Home Assistant Assist conversation agent.",
        "chips": ["HACS integration", "Assist pipeline", "Port 8787"],
        "details": [
            "Install the Tater-HomeAssistant repository through HACS as an Integration, then add Tater Conversation in Devices & Services.",
            "The config flow asks for a display name and a full endpoint URL, defaulting to http://127.0.0.1:8787/tater-ha/v1/message.",
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
    "tater_automations": {
        "title": "Tater Automations",
        "summary": "HACS integration that registers native Home Assistant automation actions for direct calls into Tater's automations bridge.",
        "chips": ["HACS integration", "Automation actions", "Port 8788"],
        "details": [
            "Install the tater_automations repository through HACS as an Integration, then add Tater Automations in Devices & Services.",
            "The config flow asks only for host and port, with 8788 as the default automations bridge port.",
            "It registers native actions for Camera Event, Doorbell Alert, Events Query Brief, Weather Brief, and Zen Greeting, plus a legacy generic tool call.",
            "Doorbell Alert is exposed as a simple no-field action because it is meant to run from defaults configured once in Tater WebUI.",
            "Those actions use Home Assistant selectors and dropdowns for common fields, so operators usually do not need to type raw tool names or raw JSON arguments.",
            "Calls still post directly to /tater-ha/v1/tools/{tool_name} with validated arguments and no AI routing in the middle.",
        ],
        "links": [
            {
                "label": "tater_automations Repo",
                "href": "https://github.com/TaterTotterson/tater_automations",
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
        "Set Server URL, Auth Token, and Quick Action Plugin from the app Settings menu.",
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
            "If AUTH_TOKEN is set in macOS portal settings, the app must send that same token as X-Tater-Token.",
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
            "This keeps menu actions fast while still allowing broader Cerberus-driven behavior when needed.",
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

HOME_ASSISTANT_AUTOMATION_GUIDES = [
    {
        "title": "Auto briefs",
        "summary": "Three automation-safe brief plugins are built for short summaries and dashboard-friendly output.",
        "chips": ["Events Query Brief", "Weather Brief", "Zen Greeting"],
        "details": [
            "Events Query Brief, Weather Brief, and Zen Greeting are the three brief-style automation plugins in the current stack.",
            "They are designed to return short plain-text summaries instead of long conversational replies.",
            "That makes them a good fit for dashboards, notifications, routines, and other machine-triggered flows.",
        ],
    },
    {
        "title": "Store results in input_text helpers",
        "summary": "Brief plugins can write directly into Home Assistant text helpers so automations stay simple and UI-driven.",
        "chips": ["input_text", "No YAML required", "Dashboard-safe"],
        "details": [
            "Create input_text helpers in Home Assistant for summaries such as input_text.event_brief, input_text.weather_brief, or input_text.zen_message.",
            "Set Maximum length to 255 when creating the helper so it has enough room for short Tater summaries.",
            "These plugins can write straight to input_text.set_value, so Home Assistant owns the state while Tater only generates the summary text.",
        ],
    },
    {
        "title": "Default once or override per automation",
        "summary": "Result targets can live in Tater plugin settings or be overridden inside an individual automation action.",
        "chips": ["INPUT_TEXT_ENTITY", "input_text_entity", "Override support"],
        "details": [
            "Option A: set INPUT_TEXT_ENTITY once in Tater WebUI plugin settings to make a helper the default output target.",
            "Option B: pass input_text_entity in the Home Assistant action to override the default for that one automation.",
            "This keeps common automations clean while still allowing special cases to route output somewhere else.",
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
        "summary": "The search_web core tool uses Google's Custom Search JSON API credentials.",
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
        "summary": "Web search is configured from Integrations because it powers a core tool, not a Verba.",
        "chips": ["Settings -> Integrations", "Web Search", "Core tool"],
        "details": [
            "Open Tater WebUI and go to Settings -> Integrations -> Web Search.",
            "Paste Google API Key and Google Search Engine ID (CX), then save the settings.",
            "The current code stores those values as tater:web_search:google_api_key and tater:web_search:google_cx, with a legacy fallback for older plugin-style settings.",
            "After that, Cerberus can call search_web for current web research and article lookup tasks.",
        ],
        "links": [],
    },
    {
        "title": "What the core tool supports",
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
        "how_to_use": "Run it from the automation portal, choose a timeframe and optional area/query, then either set INPUT_TEXT_ENTITY once in WebUI or pass input_text_entity in the action to write straight into a Home Assistant helper.",
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
        "how_to_use": "Run it from the automation portal, pick the recent hour window from the dropdown, optionally add a short query, and write the result into an input_text helper with INPUT_TEXT_ENTITY or input_text_entity.",
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
        "how_to_use": "Run it from the automation portal, choose tone and include_date options from the Home Assistant action UI, and store the result in an input_text helper when you want the message to persist on a dashboard.",
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
    "homeassistant",
    "ha_automations",
    "homekit",
    "macos",
    "xbmc",
]

CORE_DOCS_ORDER = [
    "ai_task",
    "memory",
    "rss",
]

PLATFORM_DOCS = {
    "webui": {
        "label": "WebUI",
        "description": "Streamlit-based control center for setup, private chat, Verba browsing, and Cerberus tuning.",
        "role": "Operator console",
        "source": None,
        "plugin_surface": "webui",
        "highlights": [
            "Hosts private chat, Verba browsing, settings, and Cerberus runtime controls in one place.",
            "Acts as the easiest way to inspect available tools and manage the Verba ecosystem.",
            "Ships with dedicated views for chat, Verba's, settings, Cerberus, portals, and AI task workflows.",
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
            "Runs Cerberus turns per conversation so multi-step requests stay grounded.",
            "Pairs well with admin-only Verba's and server management workflows.",
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
        "description": "Lightweight IRC bot that responds to mentions and runs compatible Verba's.",
        "role": "Chat endpoint",
        "source": TATER_SHOP_DIR / "portals" / "irc_portal.py",
        "plugin_surface": "irc",
        "highlights": [
            "Simple low-overhead deployment for classic chat rooms and ZNC-style setups.",
            "Supports admin-user gating and Verba execution on mention.",
            "Keeps the interaction model intentionally lean and plain-text friendly.",
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
            "Forms the conversational half of the Home Assistant integration story alongside automation actions.",
        ],
        "companions": [
            HOME_ASSISTANT_COMPANIONS["tater_conversation"],
            HOME_ASSISTANT_COMPANIONS["tater_automations"],
        ],
        "companions_eyebrow": "Companion setup",
        "companions_title": "Home Assistant integrations that connect to this portal.",
        "companions_intro": "These components live inside Home Assistant and point user-facing conversations or automation actions back at Tater's runtime bridges.",
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
                "details": "Accepts source, title, type, message, entity_id, ha_time, level, and data, stores the item in the Redis notifications list, and attempts to turn on configured Voice PE light entities.",
            },
            {
                "method": "GET",
                "path": "/tater-ha/v1/notifications",
                "summary": "Pull and clear queued notifications.",
                "details": "Reads queued notifications from Redis, clears the list after delivery, and turns Voice PE indicators off once notifications are consumed, or immediately if none are present.",
            },
            {
                "method": "POST",
                "path": "/tater-ha/v1/message",
                "summary": "Main Assist/chat message endpoint.",
                "details": "Receives Home Assistant conversation requests, preserves stable session context, and runs Cerberus turns with Home Assistant-scoped system prompting and plugin gating.",
            },
        ],
    },
    "ha_automations": {
        "label": "HA Automations",
        "description": "Automation-only Home Assistant endpoint that pairs with the Tater Automations integration for direct tool execution, built-in event storage, and brief plugins that can write clean summary text straight into Home Assistant helpers.",
        "role": "Automation bridge",
        "source": TATER_SHOP_DIR / "portals" / "ha_automations_portal.py",
        "plugin_surface": "automation",
        "highlights": [
            "Built for fast one-shot execution from Home Assistant automations rather than open-ended chat.",
            "Includes an event API that stores newest-first event records per source in Redis for camera, doorbell, motion, garage, and other house-event timelines.",
            "Fits camera events, doorbell alerts, dashboard summaries, and deterministic tool calls.",
            "The current automation brief trio is Events Query Brief, Weather Brief, and Zen Greeting.",
            "Pairs with the Tater Automations HACS integration, which exposes native Home Assistant actions instead of requiring raw REST or YAML calls.",
            "Those Home Assistant actions now use clean selectors and dropdowns for common fields, so most flows no longer require typing raw arguments.",
            "Works naturally with automation-only Verba's that expose short machine-oriented outputs and with a direct tool endpoint that skips AI routing.",
        ],
        "companions": [
            HOME_ASSISTANT_COMPANIONS["tater_automations"],
        ],
        "companions_eyebrow": "Companion setup",
        "companions_title": "Home Assistant integrations that connect to this portal.",
        "companions_intro": "These components live inside Home Assistant and point user-facing conversations or automation actions back at Tater's runtime bridges.",
        "guides": HOME_ASSISTANT_AUTOMATION_GUIDES,
        "guides_eyebrow": "Automation patterns",
        "guides_title": "How this portal handles brief outputs and Home Assistant state.",
        "guides_intro": "These patterns are useful when a Home Assistant automation needs clean short text instead of a conversational reply.",
        "apis": [
            {
                "method": "GET",
                "path": "/tater-ha/v1/health",
                "summary": "Basic health endpoint for the automations bridge.",
                "details": "Returns ok plus the current bridge version so Home Assistant can verify the service is alive.",
            },
            {
                "method": "POST",
                "path": "/tater-ha/v1/events/add",
                "summary": "Store a structured event record.",
                "details": "Accepts source, title, ha_time, type, message, entity_id, level, and data, normalizes ha_time to naive ISO format, then stores the event in a newest-first Redis list keyed by source.",
            },
            {
                "method": "GET",
                "path": "/tater-ha/v1/events/search",
                "summary": "Query stored events by source and time window.",
                "details": "Supports source, limit, since, and until parameters, trims old items by the configured retention window, and returns filtered event items for a single source bucket such as front_yard.",
            },
            {
                "method": "POST",
                "path": "/tater-ha/v1/tools/{tool_name}",
                "summary": "Run an automation-only tool directly.",
                "details": "Calls an enabled plugin on the automation portal with a JSON arguments payload, without any AI router in the middle, which makes it useful for deterministic Home Assistant automations.",
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
            "Can require an AUTH_TOKEN so Shortcuts must send the X-Tater-Token header when the bridge is protected.",
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
                    "If AUTH_TOKEN is set in Tater HomeKit settings, add an X-Tater-Token header inside the shortcut request.",
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
                "details": "Accepts JSON with text plus an optional session_id, enforces X-Tater-Token when AUTH_TOKEN is configured, and returns a plain reply field sized for Siri speech.",
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
            "Can enforce AUTH_TOKEN protection through the X-Tater-Token header.",
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
                "details": "Accepts user_text, clipboard context, optional assets, and scope/device context, then runs a Cerberus turn.",
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
        "description": "Background memory extraction layer that scans chat history, stores user and room memory, and feeds Cerberus context.",
        "role": "Background service",
        "source": TATER_SHOP_DIR / "cores" / "memory_core.py",
        "plugin_surface": "",
        "highlights": [
            "Incrementally mines durable facts from prior conversations instead of relying only on the active turn.",
            "Builds user and room summaries in Redis for later Cerberus injection.",
            "Includes confidence thresholds, identity linking options, and context-size limits.",
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
            "Maintains local conversation sessions and routes actions through the same Cerberus core.",
            "Pairs well with media, smart-home, and utility Verba's for couch-side control.",
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
PLATFORM_META["automation"] = {
    "label": "Automation",
    "description": "Plugin runtime surface for automation-only tools triggered by machine workflows.",
}

INSTALL_METHODS = [
    {
        "slug": "unraid",
        "title": "Unraid Community Apps",
        "eyebrow": "Recommended easy path",
        "summary": "Install Tater and Redis Stack from Unraid Community Apps with persistent storage for Agent Lab data.",
        "best_for": "Unraid users who want the smoothest packaged deployment.",
        "complexity": "Low",
        "highlights": [
            "Tater is available in the Unraid Community Apps store.",
            "The README recommends installing both Tater and Redis Stack from the app store templates.",
            "Persistent Agent Lab storage matters so updates do not wipe logs, downloads, documents, or workspace data.",
        ],
        "steps": [
            "Open Unraid Community Apps and install Redis Stack.",
            "Install Tater from the Community Apps store.",
            "Add a persistent path mapping for /app/agent_lab inside the container to a host path such as /mnt/user/appdata/tater/agent_lab.",
            "Start the containers and finish configuration in the WebUI.",
        ],
        "notes": [
            "Without the /app/agent_lab mapping, Agent Lab data can be lost when the container is rebuilt or updated.",
            "This path mirrors the Docker persistence advice in the README, but packaged for Unraid users.",
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
            "Two optional HACS integrations complete the Home Assistant side: Tater Conversation Agent for Assist and Tater Automations for native automation actions.",
        ],
        "steps": [
            "Add the Tater add-on repository: https://github.com/TaterTotterson/hassio-addons-tater",
            "Install and start Redis Stack first.",
            "Install Tater AI Assistant second.",
            "Configure your LLM and Redis settings in the Tater add-on.",
            "Start Tater and verify the WebUI and Home Assistant bridge are reachable.",
        ],
        "notes": [
            "Tater-HomeAssistant is the Home Assistant conversation component that points Assist at Tater's /tater-ha/v1/message bridge endpoint.",
            "tater_automations is the Home Assistant automation integration that calls Tater's automations bridge on port 8788 with plugin-specific actions.",
            "For brief-style automation output, input_text helpers are the recommended storage target inside Home Assistant.",
        ],
        "companions": [
            HOME_ASSISTANT_COMPANIONS["tater_conversation"],
            HOME_ASSISTANT_COMPANIONS["tater_automations"],
        ],
        "guides": HOME_ASSISTANT_AUTOMATION_GUIDES,
        "snippets": [
            {
                "label": "Conversation agent endpoint",
                "code": "http://YOUR_TATER_HOST:8787/tater-ha/v1/message",
            },
            {
                "label": "Automations integration target",
                "code": "host: YOUR_TATER_HOST\nport: 8788",
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
            {
                "label": "tater_automations",
                "href": "https://github.com/TaterTotterson/tater_automations",
            },
        ],
    },
    {
        "slug": "local",
        "title": "Local Python Install",
        "eyebrow": "Advanced local setup",
        "summary": "Run Tater from source with Python 3.11, Redis Stack, and an OpenAI-compatible model backend.",
        "best_for": "Developers and operators who want direct source control and local customization.",
        "complexity": "Medium",
        "highlights": [
            "Requires Python 3.11, Redis Stack, and an OpenAI-compatible LLM backend such as Ollama, LocalAI, LM Studio, Lemonade, or OpenAI API.",
            "The README recommends running inside a virtual environment to keep dependencies isolated.",
            "The Streamlit WebUI is started directly from the source tree.",
        ],
        "steps": [
            "Clone the repository.",
            "Change into the Tater project directory.",
            "Create and activate a Python virtual environment.",
            "Install dependencies from requirements.txt.",
            "Create a .env file with your LLM and Redis configuration.",
            "Launch the Streamlit WebUI.",
        ],
        "notes": [
            "When using ChatGPT/OpenAI API, leave LLM_PORT blank so Tater uses HTTPS without appending a port.",
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
                "label": "Example .env for local backend",
                "code": """LLM_HOST=127.0.0.1
LLM_PORT=11434
LLM_MODEL=gemma3-27b-abliterated
REDIS_HOST=127.0.0.1
REDIS_PORT=6379""",
            },
            {
                "label": "Example .env for ChatGPT/OpenAI API",
                "code": """LLM_HOST=https://api.openai.com
LLM_PORT=
LLM_MODEL=gpt-4o
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
REDIS_HOST=127.0.0.1
REDIS_PORT=6379""",
            },
            {
                "label": "Run the WebUI",
                "code": "streamlit run webui.py",
            },
        ],
        "links": [],
    },
    {
        "slug": "docker",
        "title": "Docker Image",
        "eyebrow": "Container path",
        "summary": "Run the published container image with explicit LLM, Redis, time-zone, and Agent Lab volume settings.",
        "best_for": "Operators who want a direct container deployment outside packaged add-on/app-store flows.",
        "complexity": "Medium",
        "highlights": [
            "The README publishes the image at ghcr.io/tatertotterson/tater:latest.",
            "The main container persistence warning is that /app/agent_lab should be mounted to host storage.",
            "The container exposes the Streamlit WebUI on port 8501 and several Tater service ports in the README example.",
        ],
        "steps": [
            "Pull the published image.",
            "Start the container with your chosen LLM and Redis environment variables.",
            "Mount /app/agent_lab to host storage so Agent Lab data persists across rebuilds.",
            "Open the WebUI at http://localhost:8501 after the container is running.",
        ],
        "notes": [
            "If you do not mount /app/agent_lab, runtime data can be lost when the container is rebuilt or updated.",
            "The README also calls out Unraid-specific time-zone mappings for /etc/localtime and /etc/timezone.",
        ],
        "snippets": [
            {
                "label": "Pull the image",
                "code": "docker pull ghcr.io/tatertotterson/tater:latest",
            },
            {
                "label": "Docker run with local backend",
                "code": """docker run -d --name tater_webui \\
  -p 8501:8501 \\
  -p 8787:8787 \\
  -p 8788:8788 \\
  -p 8789:8789 \\
  -p 8790:8790 \\
  -e TZ=America/Chicago \\
  -v /etc/localtime:/etc/localtime:ro \\
  -v /etc/timezone:/etc/timezone:ro \\
  -e LLM_HOST=127.0.0.1 \\
  -e LLM_PORT=11434 \\
  -e LLM_MODEL=gemma3-27b-abliterated \\
  -e REDIS_HOST=127.0.0.1 \\
  -e REDIS_PORT=6379 \\
  -v /agent_lab:/app/agent_lab \\
  ghcr.io/tatertotterson/tater:latest""",
            },
            {
                "label": "Docker run with ChatGPT/OpenAI API",
                "code": """docker run -d --name tater_webui \\
  -p 8501:8501 \\
  -p 8787:8787 \\
  -p 8788:8788 \\
  -p 8789:8789 \\
  -p 8790:8790 \\
  -e TZ=America/Chicago \\
  -v /etc/localtime:/etc/localtime:ro \\
  -v /etc/timezone:/etc/timezone:ro \\
  -e LLM_HOST=https://api.openai.com \\
  -e LLM_PORT= \\
  -e LLM_MODEL=gpt-4o \\
  -e LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx \\
  -e REDIS_HOST=127.0.0.1 \\
  -e REDIS_PORT=6379 \\
  -v /agent_lab:/app/agent_lab \\
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
        "read_url",
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

    items = payload.get("plugins") if isinstance(payload, dict) else []
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
    if manifest_entries:
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

    return sorted(
        (extract_plugin_metadata(path) for path in PLUGIN_DIR.glob("*.py") if path.name != "__init__.py"),
        key=lambda item: item["title"].lower(),
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
        ("DEFAULT_PLANNER_MAX_TOKENS", "Planner max tokens", ""),
        ("DEFAULT_DOER_MAX_TOKENS", "Doer max tokens", ""),
        ("DEFAULT_CHECKER_MAX_TOKENS", "Checker max tokens", ""),
        ("DEFAULT_TOOL_REPAIR_MAX_TOKENS", "Tool repair max tokens", ""),
        ("DEFAULT_RECOVERY_MAX_TOKENS", "Recovery max tokens", ""),
        ("DEFAULT_MAX_LEDGER_ITEMS", "Max ledger items", ""),
        ("DEFAULT_AGENT_STATE_TTL_SECONDS", "Agent state TTL", "seconds"),
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
    settings = extract_named_literal(source_path, settings_symbol)
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
            }
        )
    return rows


def format_default_value(constant_name: str, value: Any, unit: str) -> str:
    if constant_name == "DEFAULT_AGENT_STATE_TTL_SECONDS" and isinstance(value, (int, float)):
        days = int(value) // 86400
        return f"{int(value)} seconds ({days} days)"
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
        ("cerberus", "Cerberus", f"{base}cerberus/index.html"),
        ("portals", "Portals", f"{base}portals/index.html"),
        ("cores", "Cores", f"{base}cores/index.html"),
        ("kernel", "Core Tools", f"{base}kernel-tools/index.html"),
        ("plugins", "Verba's", f"{base}plugins/index.html"),
    ]
    nav_html = "\n".join(
        f'<a class="nav-link{" is-active" if key == nav_key else ""}" href="{href}">{label}</a>'
        for key, label, href in nav_items
    )
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
    if platform.get("has_settings_schema"):
        if int(platform["setting_count"]) == 0:
            return "No required fields"
        return f"{int(platform['setting_count'])} settings"
    return "No settings form"


def platform_runtime_chip(platform: dict[str, Any]) -> str:
    if int(platform["plugin_count"]) > 0:
        return f"{platform['plugin_count']} Verba's"
    if platform["slug"] == "macos":
        return "Desktop bridge"
    if platform["slug"] == "ai_task":
        return "Scheduler runtime"
    if platform["slug"] == "memory":
        return "Memory service"
    if platform["slug"] == "rss":
        return "Feed watcher"
    return "Internal runtime"


def platform_settings_text(platform: dict[str, Any]) -> str:
    surface_kind = str(platform.get("surface_kind") or "portal").strip().lower()
    settings_symbol = "CORE_SETTINGS" if surface_kind == "core" else "PORTAL_SETTINGS"
    if platform["slug"] == "webui":
        return (
            "The WebUI is itself the configuration surface, so this page documents behavior and role rather than "
            f"a separate {settings_symbol} form."
        )
    if platform["slug"] == "ai_task":
        return (
            "The scheduler declares a settings block, but it does not currently require explicit fields. "
            "Its behavior is driven by scheduled task data, targets, and notifier routing."
        )
    if platform.get("has_settings_schema"):
        return (
            f"This runtime surface declares a {settings_symbol} schema, but it does not currently require any explicit fields."
        )
    return (
        f"This surface does not expose a standalone {settings_symbol} form in the current source snapshot."
    )


def platform_plugin_text(platform: dict[str, Any]) -> str:
    if platform["slug"] == "macos":
        return (
            "macOS is a desktop bridge surface used by the Tater Menu app. It can execute compatible Verba's "
            "through /macos/plugin even when plugin inventory tags for macos are sparse."
        )
    if platform["slug"] == "ai_task":
        return (
            "AI Task Runner is a scheduler surface. It executes scheduled prompts and routes results through notifier "
            "portals rather than acting as a direct Verba target."
        )
    if platform["slug"] == "memory":
        return (
            "Memory Core is background infrastructure. It scans chat history, extracts durable facts, and injects "
            "memory context back into Cerberus instead of acting like a direct Verba surface."
        )
    if platform["slug"] == "rss":
        return (
            "RSS is a background feed watcher. It polls feeds, summarizes content, and dispatches updates through "
            "notifier portals rather than serving as a direct Verba target."
        )
    return (
        "This surface mainly handles runtime orchestration rather than exposing its own direct Verba target."
    )


def plugin_arguments_text(plugin: dict[str, Any]) -> str:
    return (
        "This Verba does not require named arguments in its published usage example. Cerberus usually triggers "
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
    core_count = len(cores)
    surface_count = portal_count + core_count
    install_count = len(INSTALL_METHODS)

    hero = f"""
    <section class="hero hero-home">
      <div class="hero-copy">
        <span class="eyebrow">Source-backed wiki</span>
        <h1>Tater is a portal-and-core AI assistant built to act.</h1>
        <p>
          Cerberus plans the work, chains core tools with Verba's, and finishes tasks across chat,
          smart-home, media, and automation workflows.
        </p>
        <div class="action-row">
          {button("Install Tater", "install/index.html")}
          {button("Explore portals", "portals/index.html")}
          {button("Explore cores", "cores/index.html")}
          {button("Explore Verba's", "plugins/index.html")}
          {button("Read Cerberus", "cerberus/index.html", ghost=True)}
        </div>
      </div>
      <aside class="hero-art">
        <div class="orbital-frame">
          <img src="assets/images/tater-logo.png" alt="Tater Assistant emblem">
        </div>
        <div class="hero-stats">
          <div class="stat-card"><strong>{plugin_count}</strong><span>documented Verba's</span></div>
          <div class="stat-card"><strong>{kernel_count}</strong><span>core tools</span></div>
          <div class="stat-card"><strong>{surface_count}</strong><span>runtime surfaces</span></div>
          <div class="stat-card"><strong>{install_count}</strong><span>install paths</span></div>
        </div>
      </aside>
    </section>
    """

    feature_cards = [
        (
            "Smart chaining",
            "Cerberus breaks work into steps, picks the next tool, and keeps going until the task is done.",
        ),
        (
            "Core layer",
            "Built-in tools handle files, web research, memory, images, notes, attachments, and delivery.",
        ),
        (
            "Verba's",
            "Actions speak louder then words. Verba's extend Tater into smart-home, media, camera, note, download, and admin workflows.",
        ),
        (
            "Control surface",
            "The WebUI handles setup, chat, plugin management, and runtime tuning while portals and cores run communication and background services.",
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

    portal_cards = "".join(
        f"""
        <article class="platform-card">
          <div class="chip-row">
            {chip(platform['role'])}
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
            {chip(platform_settings_chip(platform))}
          </div>
          <h3>{escape(platform['title'])}</h3>
          <p>{escape(platform['description'])}</p>
          <div class="plugin-links">
            {button("Read core page", f"cores/{platform['slug']}.html", ghost=True)}
          </div>
        </article>
        """
        for platform in cores
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
        <p>See every runtime surface, its role, and its settings.</p>
        {button("Open portals", "portals/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Core docs</h3>
        <p>Built-in runtime services such as scheduling, memory, and RSS monitoring.</p>
        {button("Open cores", "cores/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Cerberus core</h3>
        <p>Planner loop, validation path, guardrails, and budgets.</p>
        {button("Open Cerberus", "cerberus/index.html", ghost=True)}
      </article>
      <article class="panel">
        <h3>Tools + Verba's</h3>
        <p>Browse built-in tools and the current Verba snapshot.</p>
        {button("Open Verba's", "plugins/index.html", ghost=True)}
      </article>
    </div>
    """

    screenshot = """
    <div class="showcase-grid">
      <div class="panel panel-tight">
        <span class="eyebrow">WebUI snapshot</span>
        <h2>The operator side is live.</h2>
        <p>
          The WebUI handles setup, chat, plugin browsing, settings, and Cerberus runtime controls in one place.
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
        <span class="eyebrow">Runtime surfaces</span>
        <h2>One assistant. Portals and cores.</h2>
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
        title="Tater Assistant | Home",
        description="Overview of Tater Assistant, supported surfaces, and the current wiki structure.",
        body=body,
        depth=0,
        nav_key="home",
    )


def render_install_index() -> str:
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
        <p>Tater currently recommends models such as qwen3-coder-next, qwen3-next-80b, gpt-oss-120b, qwen3-coder-30b, or Gemma3-27b.</p>
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
        "Optional HACS integrations for Assist conversations and native automation actions.",
        "After the add-on is running, these Home Assistant-side integrations connect Assist and automation flows back to Tater's portal endpoints.",
    )
    guide_section = render_companion_section(
        method.get("guides") or [],
        "Automation setup",
        "Patterns for storing brief automation results in Home Assistant.",
        "These patterns matter most when you want automation-safe text summaries to stay visible in helpers, dashboards, and routines.",
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
        <h1>Tater runs across purpose-built runtime surfaces.</h1>
        <p>
          Some surfaces are chat or voice endpoints. Others are operator tools or background services that feed data back into Tater.
        </p>
      </div>
      <aside class="panel hero-panel">
        <span class="eyebrow">What is documented</span>
        <p>{len(platforms)} portal surfaces with current descriptions, settings snapshots, and related Verba context.</p>
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
        description="Reference for Tater Assistant runtime portals and integration surfaces.",
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
          Cores are always-on internal services like scheduling, memory extraction, and feed monitoring.
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


def render_platform_detail(platform: dict[str, Any]) -> str:
    surface_kind = str(platform.get("surface_kind") or "portal").strip().lower()
    is_core = surface_kind == "core"
    surface_label = "core" if is_core else "portal"
    surface_title = "Core" if is_core else "Portal"
    highlight_html = "".join(f"<li>{escape(item)}</li>" for item in platform["highlights"])
    companion_section = render_companion_section(
        platform.get("companions") or [],
        platform.get("companions_eyebrow") or "Companion setup",
        platform.get("companions_title") or f"Related app and integration pieces for this {surface_label}.",
        platform.get("companions_intro") or "These components connect external clients or service layers back to this runtime surface.",
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
        <p>{escape(platform['plugin_count'])} current Verba's advertise direct support for this surface.</p>
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

    body = f"""
    <section class="hero hero-subpage hero-plugin">
      <div class="hero-copy">
        <span class="eyebrow">{surface_title} profile</span>
        <h1>{escape(platform['title'])}</h1>
        <p>{escape(platform['description'])}</p>
        <div class="chip-row">
          {chip(platform['role'])}
          {chip(platform_settings_chip(platform))}
          {chip(platform_runtime_chip(platform))}
        </div>
      </div>
      <aside class="panel hero-panel">
        <span class="eyebrow">Configuration category</span>
        <p>{escape(platform['settings_category'])}</p>
        {source_note}
      </aside>
    </section>
    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Runtime role</span>
          <h2>What this surface is for</h2>
          <p>{escape(platform['role'])}</p>
        </article>
        <article class="panel">
          <span class="eyebrow">Highlights</span>
          <h2>Behavior in the current codebase</h2>
          <ul class="stack-list">{highlight_html}</ul>
        </article>
      </div>
    </section>
    <section class="section">
      <div class="detail-grid">
        <article class="panel">
          <span class="eyebrow">Related Verba's</span>
          <h2>Direct {surface_label} support</h2>
          {plugin_block}
        </article>
        <article class="panel">
          <span class="eyebrow">Settings</span>
          <h2>Configuration schema</h2>
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
        {button(f"Back to {'cores' if is_core else 'portals'}", "index.html", ghost=True)}
        {button("Verba's", "../plugins/index.html", ghost=True)}
        {button("Portals", "../portals/index.html", ghost=True)}
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
        nav_key="cores" if is_core else "portals",
    )


def render_cerberus_page(defaults: list[dict[str, str]]) -> str:
    loop_cards = [
        (
            "1. Plan Builder",
            "Cerberus turns a user request into ordered atomic steps so multi-action requests become a clean chain instead of one oversized tool call.",
        ),
        (
            "2. Planner",
            "The planner chooses exactly one next action, selecting the best core tool or Verba for the current step with a strict current-message tool gate.",
        ),
        (
            "3. Validation and repair",
            "Tool calls are forced into strict JSON, checked against the tool catalog, repaired if malformed, and blocked if the tool is unsupported or disabled.",
        ),
        (
            "4. Doer state update",
            "After a tool runs, Cerberus updates goal, plan, facts, open questions, next step, and tool history so the next round stays grounded.",
        ),
        (
            "5. Checker",
            "The checker returns exactly one of FINAL_ANSWER, RETRY_TOOL, or NEED_USER_INFO and decides whether another atomic step is still required.",
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
        "Current-message tool gate: Cerberus does not continue past work unless the current turn explicitly asks it to.",
        "Smart chaining: core tools and Verba's can be mixed across steps to finish a task instead of stopping after one tool result.",
        "Atomic execution lock: the planner and checker both focus on one next step instead of merging unrelated actions.",
        "Recovery text path: validation failures can trigger a short recovery message instead of a broken tool call.",
        "Ledger and metrics: Redis-backed state keeps history, limits, and validation outcomes visible to operators.",
        "Memory context: user and room memory summaries can be injected into checker decisions without bloating the turn.",
    ]
    guardrail_html = "".join(f"<li>{escape(item)}</li>" for item in guardrails)

    state_fields = ["goal", "plan", "facts", "open_questions", "next_step", "tool_history"]
    state_html = "".join(chip(field) for field in state_fields)
    chaining_cards = [
        (
            "Core tools first",
            "Cerberus can read files, search the web, inspect pages, search local code, manage memory, and attach artifacts before it ever needs a custom extension.",
        ),
        (
            "Verba's where action lives",
            "When the task needs smart-home control, media workflows, image generation, camera events, or app-specific logic, Cerberus switches to the right Verba.",
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
        <span class="eyebrow">Cerberus AI core</span>
        <h1>Cerberus plans, chains, and completes tasks.</h1>
        <p>
          It runs a guarded Planner -> Doer -> Checker loop that validates actions, repairs bad calls, and mixes core tools with Verba's one step at a time.
        </p>
      </div>
      <aside class="panel hero-panel">
        <img class="cerberus-badge" src="../assets/images/cerberus-badge.png" alt="Cerberus AI Core badge">
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
        <h2>Why Cerberus stays controlled.</h2>
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
        title="Tater Assistant | Cerberus",
        description="Overview of the Cerberus AI core that powers Tater Assistant.",
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
                <span class="eyebrow">Core tools</span>
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
        <h1>Core tools are Tater's native action layer.</h1>
        <p>
          They handle files, web inspection, memory, artifacts, and delivery before Cerberus reaches for a Verba.
        </p>
      </div>
      <aside class="panel hero-panel">
        <span class="eyebrow">Why they matter</span>
        <p>Core tools let Tater inspect the workspace, search live information, move files, and coordinate delivery on its own.</p>
      </aside>
    </section>
    """

    guide_section = render_companion_section(
        WEB_SEARCH_GUIDES,
        "Web search setup",
        "How to enable Google's search backend for the search_web core tool.",
        "This is a core capability, not a Verba. The current Tater WebUI path is Settings -> Integrations -> Web Search.",
    )

    body = intro + "\n".join(sections) + guide_section
    return page_template(
        title="Tater Assistant | Core Tools",
        description="Reference for Tater Assistant core tools and their purposes.",
        body=body,
        depth=1,
        nav_key="kernel",
    )


def render_plugins_page(plugins: list[dict[str, Any]]) -> str:
    cards = "".join(render_plugin_card(plugin) for plugin in plugins)
    source_copy = (
        "This index reflects the current Tater Shop manifest and plugin files. Each entry links to a source-backed detail page with usage, portals, and current behavior."
        if shop_manifest_plugins()
        else "This index reflects the modules currently present in <code>Tater/plugins</code>. Each entry links to a source-backed detail page with usage, portals, and current behavior."
    )
    body = f"""
    <section class="hero hero-subpage">
      <div class="hero-copy">
        <span class="eyebrow">Verba reference</span>
        <h1>Actions speak louder then words. {len(plugins)} Verba's are documented here.</h1>
        <p>
          {source_copy}
        </p>
      </div>
      <aside class="panel hero-panel">
        <span class="eyebrow">Filter the list</span>
        <div class="plugins-toolbar">
          <input class="search-input" type="search" placeholder="Search Verba's" data-plugin-search>
          <div class="chip-row filter-row">
            <button class="filter-chip is-active" type="button" data-platform-filter="all">All</button>
            <button class="filter-chip" type="button" data-platform-filter="webui">WebUI</button>
            <button class="filter-chip" type="button" data-platform-filter="discord">Discord</button>
            <button class="filter-chip" type="button" data-platform-filter="homeassistant">Home Assistant</button>
            <button class="filter-chip" type="button" data-platform-filter="automation">Automation</button>
          </div>
          <p class="results-copy"><span data-results-count>{len(plugins)}</span> Verba's shown</p>
        </div>
      </aside>
    </section>
    <section class="section">
      <div class="plugin-grid" data-plugin-grid>
        {cards}
      </div>
      <p class="empty-state" data-plugin-empty hidden>No Verba's match the current search and portal filter.</p>
    </section>
    """
    return page_template(
        title="Tater Assistant | Verba's",
        description="Index of Tater Assistant Verba's documented from the current repository snapshot.",
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
        {button("Back to Verba's", "index.html", ghost=True)}
        {button("Portals", "../portals/index.html", ghost=True)}
        {button("Cores", "../cores/index.html", ghost=True)}
        {button("Core tools", "../kernel-tools/index.html", ghost=True)}
        {button("Cerberus", "../cerberus/index.html", ghost=True)}
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
    cores = build_platforms(plugins, docs_order=CORE_DOCS_ORDER, surface_kind="core")
    kernel_tools = extract_kernel_tools()
    cerberus_defaults = extract_cerberus_defaults()

    write_page(SITE_ROOT / "index.html", render_home_page(plugins, kernel_tools, portals, cores))
    write_page(SITE_ROOT / "install" / "index.html", render_install_index())
    write_page(SITE_ROOT / "portals" / "index.html", render_platforms_page(portals))
    write_page(SITE_ROOT / "cores" / "index.html", render_cores_page(cores))
    write_page(SITE_ROOT / "cerberus" / "index.html", render_cerberus_page(cerberus_defaults))
    write_page(SITE_ROOT / "kernel-tools" / "index.html", render_kernel_page(kernel_tools))
    write_page(SITE_ROOT / "plugins" / "index.html", render_plugins_page(plugins))

    cleanup_section_pages(SITE_ROOT / "install", [method["slug"] for method in INSTALL_METHODS])
    cleanup_section_pages(SITE_ROOT / "portals", [platform["slug"] for platform in portals])
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
