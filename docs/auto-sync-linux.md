# Linux Auto Sync

The wiki can keep itself updated from the `Tater` and `Tater_Shop` repositories.

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

Useful flags:

```bash
python3 scripts/sync_wiki_sources.py --force-build
python3 scripts/sync_wiki_sources.py --skip-fetch
python3 scripts/sync_wiki_sources.py --allow-dirty-build
```

## Force rebuild

Force a rebuild immediately:

```bash
python3 /home/taterassistant/scripts/sync_wiki_sources.py --force-build
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
0 4,16 * * * /bin/bash -lc '/usr/bin/python3 /home/taterassistant/scripts/sync_wiki_sources.py >> /home/taterassistant/scripts/wiki-sync.log 2>&1'
```

Webmin cron job settings:

- user: `taterassistant`
- minute: `0`
- hour: `4,16`
- command: `/bin/bash -lc '/usr/bin/python3 /home/taterassistant/scripts/sync_wiki_sources.py >> /home/taterassistant/scripts/wiki-sync.log 2>&1'`
