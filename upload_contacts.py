#!/usr/bin/env python3
"""
Update HTML files in AntonButov/wordstat (branch main) with contact info.
Uses gh CLI if authenticated, else curl+GITHUB_TOKEN, else prints base64 content.
"""
import base64
import json
import os
import subprocess
import sys

SITE_DIR = "/mnt/thousand/EXAMPLESS/ai/site"
REPO = "AntonButov/wordstat"
BRANCH = "main"
FILES = ["sales.html", "1c.html", "bitrix24.html", "cases.html", "faq.html"]
COMMIT_MSG = "Контакты cleardocs"


def file_content_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def use_gh_cli() -> bool:
    """Try gh api to update each file. Return True if used."""
    try:
        subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False
    os.chdir(SITE_DIR)
    for f in FILES:
        path = os.path.join(SITE_DIR, f)
        if not os.path.isfile(path):
            print(f"Skip (missing): {f}", file=sys.stderr)
            continue
        b64 = file_content_b64(path)
        r = subprocess.run(
            [
                "gh", "api", f"repos/{REPO}/contents/{f}",
                "-X", "PUT",
                "-f", f"message={COMMIT_MSG}",
                "-f", f"branch={BRANCH}",
                "-f", f"content={b64}",
            ],
            capture_output=True,
            text=True,
            cwd=SITE_DIR,
        )
        if r.returncode == 0:
            print(f"OK {f}")
        else:
            print(f"FAIL {f}: {r.stderr or r.stdout}", file=sys.stderr)
            return True  # we used gh but had a failure
    return True


def get_sha(token: str, path: str) -> str | None:
    """GET file from GitHub; return sha if exists else None."""
    import urllib.request
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{path}?ref={BRANCH}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except Exception:
        return None


def use_curl(token: str) -> bool:
    """Update via curl. Return True if used."""
    import urllib.request
    for f in FILES:
        path = os.path.join(SITE_DIR, f)
        if not os.path.isfile(path):
            print(f"Skip (missing): {f}", file=sys.stderr)
            continue
        b64 = file_content_b64(path)
        sha = get_sha(token, f)
        body = {
            "message": COMMIT_MSG,
            "branch": BRANCH,
            "content": b64,
        }
        if sha:
            body["sha"] = sha
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            f"https://api.github.com/repos/{REPO}/contents/{f}",
            data=data,
            method="PUT",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                print(f"OK {f}")
        except urllib.error.HTTPError as e:
            print(f"FAIL {f}: {e.code} {e.read().decode()}", file=sys.stderr)
            return True
    return True


def output_contents():
    """Print base64 content for each file for manual use."""
    print("# Base64 file contents for manual GitHub update (branch=main, message=%s)" % COMMIT_MSG)
    for f in FILES:
        path = os.path.join(SITE_DIR, f)
        if not os.path.isfile(path):
            print(f"# Skip (missing): {f}")
            continue
        b64 = file_content_b64(path)
        print(f"# --- {f} ---")
        print(f"{f}:{b64}")
    print("# Example: gh api repos/%s/contents/FILENAME -X PUT -f message=%s -f branch=%s -f content=\"$(echo PASTE_B64_HERE | base64 -d | base64 -w0)\"" % (REPO, COMMIT_MSG, BRANCH))


def main():
    if use_gh_cli():
        return
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token and use_curl(token):
        return
    print("Neither 'gh' (authenticated) nor GITHUB_TOKEN available. Outputting file contents.", file=sys.stderr)
    output_contents()


if __name__ == "__main__":
    main()
