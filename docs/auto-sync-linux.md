# Linux Auto Sync

The wiki can keep itself updated from this website repository plus the `Tater` and `Tater_Shop` repositories.

Recommended layout:

```text
/home/taterassistant/
  public_html/
    assets/
    index.html
    ...
  scripts/
    build_wiki.py
    sync_wiki_sources.py
    Tater/
    Tater_Shop/
```

Default behavior with that layout:

- the website is generated into `public_html`
- the website checkout can fast-forward itself before building when `--self-update` is used
- `Tater` is cloned into `scripts/Tater`
- `Tater_Shop` is cloned into `scripts/Tater_Shop`
- sync state is stored in `scripts/.wiki-sync-state.json`
- keep the existing `public_html/assets` folder in place because the generator writes HTML pages but does not rebuild CSS, JS, or image assets

## Manual sync

Run:

```bash
python3 /home/taterassistant/scripts/sync_wiki_sources.py
```

What it does:

- clones `Tater` into `./Tater` if missing
- clones `Tater_Shop` into `./Tater_Shop` if missing
- fast-forwards clean checkouts when the remote branch changes
- blocks the rebuild if a source checkout is dirty or diverged
- runs `scripts/build_wiki.py` only when source heads changed or outputs are missing

For the production cron job, use self-update mode:

```bash
python3 /home/taterassistant/scripts/sync_wiki_sources.py --self-update
```

With `--self-update`, the script fetches the website repo first. If the checkout can fast-forward, it updates the repo and re-executes the freshly pulled copy of `sync_wiki_sources.py` before syncing `Tater` and `Tater_Shop`. This means pushing `Tater_Assistant-Website` to GitHub is enough for the next cron run to pick up CSS, asset, template, and script changes.

Useful flags:

```bash
python3 scripts/sync_wiki_sources.py --force-build
python3 scripts/sync_wiki_sources.py --skip-fetch
python3 scripts/sync_wiki_sources.py --allow-dirty-build
python3 scripts/sync_wiki_sources.py --self-update
python3 scripts/sync_wiki_sources.py --self-update --no-self-update-autostash
```

## Force rebuild

Force a rebuild immediately:

```bash
python3 /home/taterassistant/scripts/sync_wiki_sources.py --self-update --force-build
```

Reset the saved sync state so the next normal run rebuilds:

```bash
rm -f /home/taterassistant/scripts/.wiki-sync-state.json
```

## Cron

For a headless server, cron is the simplest option.

Open your cron:

```bash
crontab -e
```

Add this entry to run twice a day and log output:

```bash
0 4,16 * * * /bin/bash -lc '/usr/bin/python3 /home/taterassistant/scripts/sync_wiki_sources.py --self-update >> /home/taterassistant/scripts/wiki-sync.log 2>&1'
```

Webmin cron job settings:

- user: `taterassistant`
- minute: `0`
- hour: `4,16`
- command: `/bin/bash -lc '/usr/bin/python3 /home/taterassistant/scripts/sync_wiki_sources.py --self-update >> /home/taterassistant/scripts/wiki-sync.log 2>&1'`

## Notes

- Self-update uses a fast-forward-only merge, so it will not create merge commits on the server.
- By default it uses Git autostash so generated `public_html` changes from a previous build do not block a clean fast-forward.
- If a previous autostash left unresolved conflicts only in generated `public_html` files, the next self-update restores those generated files from `HEAD` and continues.
- If the website repo has conflicting local edits or has diverged from GitHub, the script stops and logs the reason instead of guessing.
