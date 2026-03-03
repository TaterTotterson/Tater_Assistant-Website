#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
SITE_ROOT = ((BASE_DIR / "public_html") if (BASE_DIR / "public_html").exists() else BASE_DIR).resolve()
BUILD_SCRIPT = SCRIPT_DIR / "build_wiki.py"
STATE_FILE = SCRIPT_DIR / ".wiki-sync-state.json"

DEFAULT_TATER_URL = "https://github.com/TaterTotterson/Tater.git"
DEFAULT_TATER_SHOP_URL = "https://github.com/TaterTotterson/Tater_Shop.git"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def log(message: str) -> None:
    print(f"[{utc_now()}] {message}", flush=True)


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        capture_output=True,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        detail = stderr or stdout or f"command exited with {completed.returncode}"
        raise RuntimeError(f"{' '.join(args)} failed: {detail}")
    return completed


def git(repo_dir: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], cwd=repo_dir, check=check)


def git_stdout(repo_dir: Path, *args: str, check: bool = True) -> str:
    return git(repo_dir, *args, check=check).stdout.strip()


def repo_head(repo_dir: Path) -> str:
    return git_stdout(repo_dir, "rev-parse", "HEAD")


def repo_branch(repo_dir: Path) -> str:
    return git_stdout(repo_dir, "branch", "--show-current")


def repo_dirty(repo_dir: Path) -> bool:
    return bool(git_stdout(repo_dir, "status", "--porcelain"))


def can_fast_forward(repo_dir: Path, local_ref: str, remote_ref: str) -> bool:
    completed = git(repo_dir, "merge-base", "--is-ancestor", local_ref, remote_ref, check=False)
    return completed.returncode == 0


def local_ahead_of_remote(repo_dir: Path, local_ref: str, remote_ref: str) -> bool:
    completed = git(repo_dir, "merge-base", "--is-ancestor", remote_ref, local_ref, check=False)
    return completed.returncode == 0


def clone_repo(url: str, target_dir: Path) -> dict[str, Any]:
    log(f"Cloning {url} -> {target_dir}")
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--depth", "1", url, str(target_dir)])
    head = repo_head(target_dir)
    return {
        "path": str(target_dir),
        "head_before": "",
        "head_after": head,
        "changed": True,
        "cloned": True,
        "dirty": False,
        "status": "cloned",
    }


def sync_repo(name: str, url: str, target_dir: Path, *, skip_fetch: bool) -> dict[str, Any]:
    if not target_dir.exists():
        return clone_repo(url, target_dir)

    if not (target_dir / ".git").exists():
        raise RuntimeError(f"{name} path exists but is not a git repository: {target_dir}")

    head_before = repo_head(target_dir)
    branch = repo_branch(target_dir)
    dirty = repo_dirty(target_dir)

    result = {
        "path": str(target_dir),
        "head_before": head_before,
        "head_after": head_before,
        "changed": False,
        "cloned": False,
        "dirty": dirty,
        "status": "unchanged",
    }

    if dirty:
        result["status"] = "dirty"
        return result

    if not branch:
        result["status"] = "detached"
        return result

    if skip_fetch:
        result["status"] = "checked-local"
        return result

    log(f"Fetching {name} ({branch})")
    git(target_dir, "fetch", "--quiet", "origin", branch)

    remote_ref = f"origin/{branch}"
    remote_head = git_stdout(target_dir, "rev-parse", remote_ref)
    if remote_head == head_before:
        return result

    if can_fast_forward(target_dir, head_before, remote_head):
        log(f"Fast-forwarding {name} to {remote_head[:12]}")
        git(target_dir, "merge", "--ff-only", remote_ref)
        result["head_after"] = repo_head(target_dir)
        result["changed"] = result["head_after"] != head_before
        result["status"] = "updated" if result["changed"] else "unchanged"
        return result

    if local_ahead_of_remote(target_dir, head_before, remote_head):
        result["status"] = "local-ahead"
        return result

    result["status"] = "diverged"
    return result


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def missing_outputs(root: Path) -> bool:
    expected = [
        root / "index.html",
        root / "plugins" / "index.html",
        root / "platforms" / "index.html",
        root / "kernel-tools" / "index.html",
        root / "cerberus" / "index.html",
    ]
    return any(not path.exists() for path in expected)


def build_wiki(*, root: Path, tater_dir: Path, tater_shop_dir: Path, python_bin: str) -> None:
    env = os.environ.copy()
    env["TATER_WIKI_SITE_DIR"] = str(root)
    env["TATER_WIKI_TATER_DIR"] = str(tater_dir)
    env["TATER_WIKI_TATER_SHOP_DIR"] = str(tater_shop_dir)
    log("Running build_wiki.py")
    run([python_bin, str(BUILD_SCRIPT)], cwd=SCRIPT_DIR, env=env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clone/sync Tater sources and rebuild the wiki when source heads change.")
    parser.add_argument("--tater-url", default=DEFAULT_TATER_URL, help="Git URL for the core Tater repo.")
    parser.add_argument("--shop-url", default=DEFAULT_TATER_SHOP_URL, help="Git URL for the Tater Shop repo.")
    parser.add_argument("--site-dir", default=str(SITE_ROOT), help="Output directory for the generated website.")
    parser.add_argument("--tater-dir", default=str(SCRIPT_DIR / "Tater"), help="Checkout path for the Tater repo.")
    parser.add_argument("--shop-dir", default=str(SCRIPT_DIR / "Tater_Shop"), help="Checkout path for the Tater Shop repo.")
    parser.add_argument("--python", default=sys.executable or "python3", help="Python interpreter used to run build_wiki.py.")
    parser.add_argument("--skip-fetch", action="store_true", help="Do not contact remotes; only inspect local checkouts and state.")
    parser.add_argument("--force-build", action="store_true", help="Run build_wiki.py even if the repo heads did not change.")
    parser.add_argument(
        "--allow-dirty-build",
        action="store_true",
        help="Allow a rebuild even when a source checkout has uncommitted changes. Default is to block the rebuild.",
    )
    parser.add_argument("--state-file", default=str(STATE_FILE), help="Path to the sync state file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    tater_dir = Path(args.tater_dir).expanduser().resolve()
    shop_dir = Path(args.shop_dir).expanduser().resolve()
    state_path = Path(args.state_file).expanduser().resolve()
    site_root = Path(args.site_dir).expanduser().resolve()

    state = load_state(state_path)
    previous_heads = state.get("heads") if isinstance(state.get("heads"), dict) else {}

    sources = {
        "tater": sync_repo("Tater", args.tater_url, tater_dir, skip_fetch=args.skip_fetch),
        "shop": sync_repo("Tater_Shop", args.shop_url, shop_dir, skip_fetch=args.skip_fetch),
    }

    blocked = {name: info for name, info in sources.items() if info["status"] in {"dirty", "diverged"}}
    if blocked and not args.allow_dirty_build:
        for name, info in blocked.items():
            log(f"Build blocked: {name} source is {info['status']} at {info['path']}")
        return 2

    current_heads = {name: info["head_after"] for name, info in sources.items()}
    changed_heads = {
        name
        for name, head in current_heads.items()
        if head and head != str(previous_heads.get(name) or "")
    }
    remote_updates = {name for name, info in sources.items() if info["changed"]}

    needs_build = bool(
        args.force_build
        or missing_outputs(site_root)
        or changed_heads
        or remote_updates
    )

    if not needs_build:
        log("No source changes detected. Wiki rebuild skipped.")
        return 0

    build_wiki(root=site_root, tater_dir=tater_dir, tater_shop_dir=shop_dir, python_bin=args.python)

    save_state(
        state_path,
        {
            "last_build_at": utc_now(),
            "site_root": str(site_root),
            "heads": current_heads,
            "sources": {name: {"status": info["status"], "path": info["path"]} for name, info in sources.items()},
        },
    )
    log("Wiki rebuild complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
