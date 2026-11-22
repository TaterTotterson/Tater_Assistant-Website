"""Visitor-facing pages, separate from the generated technical reference."""

from html import escape


def icon(name: str) -> str:
    paths = {
        "download": '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
        "home": '<path d="m3 10 9-7 9 7v11h-7v-7h-4v7H3Z"/>',
        "music": '<path d="M9 18V5l12-2v13M9 8l12-2"/><ellipse cx="6" cy="18" rx="3" ry="3"/><ellipse cx="18" cy="16" rx="3" ry="3"/>',
        "chat": '<path d="M21 11a9 9 0 0 1-9 9H4l-2 2V11a9 9 0 0 1 19 0Z"/><path d="M7 10h10M7 14h6"/>',
        "lock": '<rect x="5" y="10" width="14" height="11" rx="3"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>',
        "code": '<path d="m8 6-6 6 6 6m8-12 6 6-6 6M14 3l-4 18"/>',
        "spark": '<path d="m12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3Z"/>',
        "book": '<path d="M12 5v16M2 3h5a5 5 0 0 1 5 3 5 5 0 0 1 5-3h5v16h-5a5 5 0 0 0-5 2 5 5 0 0 0-5-2H2Z"/>',
        "github": '<path d="M9 19c-5 2-5-3-7-3m14 6v-4a4 4 0 0 0-1-3c4-.5 6-2 6-6a5 5 0 0 0-1-3 5 5 0 0 0 0-4s-2-.5-4 1a14 14 0 0 0-8 0C6 1.5 4 2 4 2a5 5 0 0 0 0 4 5 5 0 0 0-1 3c0 4 2 5.5 6 6a4 4 0 0 0-1 3v4"/>',
    }
    return f'<svg class="ui-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def render_get_started(release: dict[str, str], base: str = "") -> str:
    version = escape(release["version_label"])
    download = escape(release["dmg_url"], quote=True)
    options = [
        ("macos", "macOS", "A happy home on your Mac.", "Apple Silicon · macOS 15 or newer", ["Download the Tater app.", "Drag Tater into Applications and open it.", "Choose your models and finish setup in Tater."], "Download for macOS", download),
        ("docker", "Docker", "Your server. Your little spud.", "For an existing Docker host", ["Open the Docker setup guide.", "Create the container with persistent storage.", "Open Tater in your browser and finish setup."], "Docker setup guide", f"{base}install/docker.html"),
        ("home-assistant", "Home Assistant", "Make yourself at home.", "For an existing Home Assistant installation", ["Open the add-on installation guide.", "Add the Tater repository and install the add-on.", "Start Tater and choose your models."], "Home Assistant guide", f"{base}install/home-assistant.html"),
        ("unraid", "Unraid", "Another good reason for a home server.", "For an existing Unraid server", ["Find Tater in Community Applications.", "Configure storage and install the container.", "Open the WebUI to finish setup."], "Unraid setup guide", f"{base}install/unraid.html"),
        ("local", "From source", "For the hands-on potato enthusiast.", "Python setup · Linux, macOS & supported hardware", ["Clone the Tater repository.", "Run the setup script and select your hardware profile.", "Start Tater, then finish setup in your browser."], "Source installation guide", f"{base}install/local.html"),
    ]
    tabs = "".join(f'<a class="setup-tab" href="#setup-{key}" role="tab" id="tab-{key}" aria-controls="setup-{key}" aria-selected="{str(i == 0).lower()}">{label}</a>' for i, (key, label, *_rest) in enumerate(options))
    panels = ""
    for key, label, title, requirements, steps, action, href in options:
        step_html = "".join(f"<li>{step}</li>" for step in steps)
        extra = f'<a class="text-link" href="{base}install/macos.html">Read the macOS guide</a>' if key == "macos" else ""
        panels += f'''<section class="setup-panel" id="setup-{key}" role="tabpanel" aria-labelledby="tab-{key}" tabindex="0">
          <div class="setup-panel-copy"><span class="setup-platform">{label}{' · ' + version if key == 'macos' else ''}</span><h3>{title}</h3><p>{requirements}</p>
          <div class="action-row"><a class="button" href="{href}">{icon('download') if key == 'macos' else icon('book')}{action}</a>{extra}</div></div>
          <ol class="setup-steps">{step_html}</ol></section>'''
    return f'''<section class="start-section" id="get-started" aria-labelledby="start-title">
      <div class="section-intro"><span class="eyebrow">Plant your first Tater</span><h2 id="start-title">A little setup.<br>A lot of possibilities.</h2><p>Start with the computer or server you already have.</p></div>
      <div class="setup-picker" data-tabs><div class="setup-tabs" role="tablist" aria-label="Installation platform">{tabs}</div>{panels}</div>
      <p class="setup-footnote">Tater needs an AI model to think with. Use a local model or connect a provider. <a href="{base}llms/index.html">Explore model options</a>.</p>
    </section>'''


def render_home_body(release: dict[str, str]) -> str:
    return f'''
    <section class="welcome" aria-labelledby="welcome-title">
      <div class="welcome-copy"><span class="welcome-tag">Homegrown AI. Extra personality.</span>
        <h1 id="welcome-title">Small spud.<br><span>Big possibilities.</span></h1>
        <p>Meet Tater, your own AI assistant. Chat, play music, and make your home a little smarter. All from a place you control.</p>
        <div class="action-row"><a class="button button-primary" href="#get-started">{icon('download')}Get Tater</a><a class="button button-outline" href="#meet-tater">Meet your new spud</a></div>
        <div class="welcome-notes"><span>{icon('code')}Open source</span><span>{icon('home')}Self-hosted</span><span>{icon('spark')}Made to be yours</span></div>
      </div>
      <div class="welcome-art"><div class="tater-orbit" aria-hidden="true"></div><span class="art-spark spark-one" aria-hidden="true">✳</span><span class="art-spark spark-two" aria-hidden="true">✦</span>
        <img class="welcome-mascot" src="assets/images/tater-mascot-wave.png" alt="Tater, a smiling potato robot with orange headphones, waving hello" width="1024" height="1536" fetchpriority="high">
        <div class="hello-sticker">Oh, hey there!<span>Your new favorite spud.</span></div>
      </div>
    </section>
    <div class="values-strip"><p>A little more local.</p><span aria-hidden="true">✳</span><p>A lot more personal.</p><span aria-hidden="true">✳</span><p>Entirely your Tater.</p><span aria-hidden="true">✳</span></div>
    <section class="meet-section" id="meet-tater" aria-labelledby="meet-title">
      <div class="section-intro"><span class="eyebrow">Less tapping. More asking.</span><h2 id="meet-title">Life's better with<br>a helpful little spud.</h2><p>One assistant for the everyday things.<br>Make it as simple or as clever as you like.</p></div>
      <div class="tater-demo" data-tabs>
        <div class="demo-tabs" role="tablist" aria-label="Example conversations">
          <a role="tab" id="tab-home" class="demo-tab" href="#demo-home" aria-controls="demo-home" aria-selected="true">{icon('home')}At home</a>
          <a role="tab" id="tab-music" class="demo-tab" href="#demo-music" aria-controls="demo-music" aria-selected="false">{icon('music')}Music time</a>
          <a role="tab" id="tab-everyday" class="demo-tab" href="#demo-everyday" aria-controls="demo-everyday" aria-selected="false">{icon('chat')}Everyday help</a>
        </div>
        <div class="conversation" id="demo-home" role="tabpanel" aria-labelledby="tab-home"><span class="example-label">An example with smart-home devices connected</span><p class="chat-question">Hey Tater, turn on the living room lights.</p><div class="chat-answer"><span class="tater-avatar" aria-hidden="true">t.</span><p>Lights on. Time to get comfy.</p></div><div class="demo-result">{icon('home')}Living room<span>Lights on</span></div></div>
        <div class="conversation" id="demo-music" role="tabpanel" aria-labelledby="tab-music"><span class="example-label">An example with music and speakers connected</span><p class="chat-question">Hey Tater, play some jazz in the kitchen.</p><div class="chat-answer"><span class="tater-avatar" aria-hidden="true">t.</span><p>A little jazz for the kitchen. Coming right up.</p></div><div class="demo-result">{icon('music')}Kitchen speaker<span>Jazz time</span></div></div>
        <div class="conversation" id="demo-everyday" role="tabpanel" aria-labelledby="tab-everyday"><span class="example-label">An example of a chat with Tater</span><p class="chat-question">What can I make with potatoes and cheese?</p><div class="chat-answer"><span class="tater-avatar" aria-hidden="true">t.</span><p>Cheesy baked potatoes sound like a very good start. Want a simple recipe?</p></div><div class="demo-result">{icon('chat')}A little inspiration<span>Dinner, sorted</span></div></div>
      </div>
    </section>
    <section class="why-section" aria-label="Why Tater"><article>{icon('lock')}<h3>Your home. Your control.</h3><p>Run Tater on your own hardware. Choose local AI models, or connect the providers you prefer.</p></article><article>{icon('spark')}<h3>A spud of many talents.</h3><p>Add the music, smart-home connections, and extra skills you actually want.</p></article><article>{icon('code')}<h3>Open from the start.</h3><p>Explore the code, make something new, or help Tater grow. The project lives on GitHub.</p></article></section>
    <section class="grow-section" aria-labelledby="grow-title"><div class="section-intro"><span class="eyebrow">Room to grow</span><h2 id="grow-title">Start small. Sprout everywhere.</h2><p>A chat in your browser is just the beginning.</p></div>
      <div class="grow-grid"><article class="grow-card grow-voice"><div class="grow-copy"><span class="card-kicker">Around the house</span><h3>A friendly voice.<br>In your favorite rooms.</h3><p>Add a supported voice satellite to talk to Tater, set timers, and bring your music along.</p><a class="button button-dark" href="satellites/index.html">Meet the satellites</a></div><div class="satellite-display"><span class="room-label">Hey Tater!</span><img src="assets/images/satellites/voice-pe.webp" alt="Home Assistant Voice Preview Edition, a supported Tater voice satellite" loading="lazy" width="900" height="900"></div></article>
      <article class="grow-card grow-phone"><div class="grow-copy"><span class="card-kicker">Meet Little Spud</span><h3>Your Tater.<br>A little more pocket-sized.</h3><p>Pair your phone with your Tater for chat, voice, music, and home controls.</p><a class="button button-dark" href="little-spud/index.html">Get to know Little Spud</a></div><div class="phone-illustration" aria-label="Illustrative Little Spud chat"><div class="phone-speaker"></div><div class="phone-heading">little spud<span>Your Tater, to go.</span></div><div class="phone-chat">Hey, Tater! 👋</div><div class="phone-reply">Hey, you. What are we<br>doing today?</div><img src="assets/images/tater-mascot-sit.png" alt="" loading="lazy" aria-hidden="true" width="1024" height="1536"></div></article></div>
    </section>
    {render_get_started(release)}
    <section class="faq-section" aria-labelledby="faq-title"><div class="section-intro"><span class="eyebrow">A few good questions</span><h2 id="faq-title">Curious potatoes<br>welcome.</h2></div><div class="faq-list">
      <details><summary>What do I need to run Tater?</summary><p>A supported computer or home server, plus an AI model. You can run a model locally or connect a remote provider. The <a href="install/index.html">setup guide</a> helps you choose a starting point.</p></details>
      <details><summary>Do I need special hardware?</summary><p>You can start with Tater's browser interface. Voice satellites are optional, and Little Spud pairs your phone with a running Tater server.</p></details>
      <details><summary>Does everything stay local?</summary><p>Tater runs on hardware you control and supports local AI models. Remote model providers and online integrations send the requests they need to those services. You choose which ones to connect.</p></details>
      <details><summary>Does it work with my smart home?</summary><p>Tater supports optional integrations including Home Assistant, Philips Hue, and other services. Check the <a href="integrations/index.html">integration directory</a> for your devices.</p></details>
      <details><summary>Where are the technical docs?</summary><p>Right here. The <a href="docs/index.html">Tater docs</a> cover setup, voice, integrations, skills, and the pieces under the hood.</p></details>
    </div></section>
    <section class="community-band"><span class="community-flower" aria-hidden="true">✳</span><div><span class="eyebrow">Good things grow together</span><h2>Help this little spud grow.</h2><p>Have an idea, found a bug, or built something fun? Come say hello.</p></div><a class="button button-outline" href="https://github.com/TaterTotterson/Tater">{icon('github')}Find Tater on GitHub</a></section>
    '''


def render_docs_body() -> str:
    groups = [
        ("Start here", "Get up and growing.", [("Install Tater", "Choose a setup for your Mac, server, or container.", "install/index.html"), ("Choose an AI model", "Find a local model or connect a model provider.", "llms/index.html"), ("Connect Little Spud", "Pair the phone and tablet companion with Tater.", "spud-hub/index.html")]),
        ("Make yourself at home", "Connect the things you use.", [("Voice satellites", "Find supported hardware for voice in your rooms.", "satellites/index.html"), ("Voice setup", "Wake words, speakers, and room-aware voice.", "tater-voice/index.html"), ("USB Flasher", "Install firmware on a supported satellite.", "usb-flasher/index.html"), ("Integrations", "Connect smart-home devices, music, and services.", "integrations/index.html"), ("Chat connections", "Use Tater in Discord, Telegram, and other portals.", "portals/index.html")]),
        ("Go a little deeper", "Build a Tater that's yours.", [("Extra skills · Verbas", "Browse add-on skills and their settings.", "plugins/index.html"), ("Background features · Cores", "Explore music, automations, awareness, and more.", "cores/index.html"), ("Task planning · Hydra", "How Tater plans and carries out requests.", "cerberus/index.html"), ("Agent workspace · Spudex", "Set up Tater's workspace for larger tasks.", "spudex/index.html"), ("Built-in tools", "Reference for the kernel's available tools.", "kernel-tools/index.html"), ("API", "Connect apps using the OpenAI-compatible API.", "api/index.html")]),
    ]
    sections = ""
    for title, subtitle, links in groups:
        cards = "".join(f'<a class="guide-link" href="../{href}" data-guide data-guide-keywords="{"Docker macOS Unraid Home Assistant source Python setup" if href == "install/index.html" else ""}"><h3>{title}</h3><p>{description}</p><span class="guide-label">Read guide</span></a>' for title, description, href in links)
        sections += f'<section class="guide-group" data-guide-group><div class="guide-group-head"><h2>{title}</h2><p>{subtitle}</p></div><div class="guide-grid">{cards}</div></section>'
    return f'''<section class="docs-intro"><span class="eyebrow">The Tater field guide</span><h1>A little guidance.<br><span>A lot you can grow.</span></h1><p>From your first install to your next big idea. Find what you need, one guide at a time.</p><label class="guide-search"><span>Find a guide</span><input class="search-input" type="search" placeholder="Try voice, Docker, music…" data-guide-search></label><p class="guide-count" role="status" data-guide-count>14 guides to help you get growing.</p></section>{sections}<p class="guide-empty" data-guide-empty hidden>No guides match that search. Try a device, feature, or setup method.</p>'''


def render_install_body(release: dict[str, str]) -> str:
    return f'''<section class="install-intro"><span class="eyebrow">Make yourself at home</span><h1>Let's get your<br><span>Tater growing.</span></h1><p>Pick where Tater will live. Then choose an AI model and make it your own.</p></section>{render_get_started(release, '../')}<section class="install-next"><div>{icon('spark')}<h2>Next, give it a little personality.</h2><p>Once Tater is running, choose a model, connect your favorite services, or pair Little Spud.</p></div><div class="next-links"><a href="../llms/index.html">Choose your AI model</a><a href="../integrations/index.html">Connect your home & services</a><a href="../spud-hub/index.html">Pair your phone</a><a href="../docs/index.html">Explore all the docs</a></div></section>'''


def render_little_spud_body() -> str:
    return f'''<section class="companion-hero"><div class="section-intro"><span class="eyebrow">Meet Little Spud</span><h1>Your Tater.<br><span>To go.</span></h1><p>A little companion for your own Tater. Chat, talk, play music, and control your home from your phone or tablet.</p><div class="action-row"><a class="button" href="https://apps.apple.com/app/little-spud/id6781400718">Get it for iPhone &amp; iPad</a><a class="button button-outline" href="https://play.google.com/store/apps/details?id=com.tatertotterson.littlespud.android">Get it for Android</a></div><p class="companion-note">Little Spud connects to a running Tater server.<br>New here? <a class="text-link" href="../install/index.html">Get Tater first</a>.</p></div><div class="companion-art"><span class="companion-art-title">little spud<span>A familiar face. A little closer.</span></span><img src="../assets/images/tater-mascot-sit.png" alt="Tater sitting down with a friendly smile" width="1024" height="1536"></div></section>
    <section class="companion-setup"><div class="section-intro"><span class="eyebrow">Hello, pocket potato</span><h2>A little pairing.<br>Then you're together.</h2></div><ol class="setup-steps"><li>Start Tater on your computer or server.</li><li>Install Little Spud on your phone or tablet.</li><li>Open Spud Hub in Tater and scan the pairing QR code with Little Spud.</li></ol></section>
    <section class="why-section companion-features"><article>{icon('chat')}<h3>A familiar conversation.</h3><p>Chat or use voice with the Tater you've already set up.</p></article><article>{icon('home')}<h3>A little home control.</h3><p>Reach your connected home controls without opening another dashboard.</p></article><article>{icon('music')}<h3>Your music, close by.</h3><p>Control Music Core and keep your favorite sounds within reach.</p></article></section>
    <section class="community-band"><div><span class="eyebrow">Need a hand?</span><h2>Let's get you connected.</h2><p>Find connection settings, pairing help, and more in the Spud Hub guide.</p></div><div class="action-row"><a class="button" href="../spud-hub/index.html">Read the pairing guide</a><a class="text-link" href="../privacy/little-spud/index.html">App privacy</a></div></section>'''
