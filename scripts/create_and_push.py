#!/usr/bin/env python3
"""
create_and_push.py
==================
1. Creates the GitHub repository via API (if it doesn't exist)
2. Updates the git remote to use the token for auth
3. Pushes the local repo to GitHub

Usage:
    python create_and_push.py <YOUR_GITHUB_TOKEN>

Example:
    python create_and_push.py ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Token requirements:
    - Scope: repo  (full repo access)
    - Create at: https://github.com/settings/tokens/new
      ✓ Check "repo" → "Full control of private repositories"
      (works for public repos too)
"""

import sys, os, subprocess, json, urllib.request, urllib.error

# ── Config ───────────────────────────────────────────────────────────────────
REPO_NAME  = "Robotics-TopConf-Analysis-2024-2026"
REPO_DESC  = "Curated robotics papers from ICRA, IROS, RSS, CoRL (2024-2026). Robot type classification, code links, trend analysis."
REPO_PRIVATE = False          # Set True if you want a private repo
GITHUB_USER = "AsakaTigar"    # Change if your GitHub username differs
BRANCH     = "main"
REPO_DIR   = os.path.dirname(os.path.abspath(__file__))
# ─────────────────────────────────────────────────────────────────────────────

def api_request(endpoint, token, method="GET", body=None):
    url = f"https://api.github.com{endpoint}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept":        "application/vnd.github.v3+json",
            "Content-Type":  "application/json",
            "User-Agent":    "robotics-paper-bot/1.0",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def run(cmd, **kw):
    print(f"  $ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    if r.stdout.strip(): print("   ", r.stdout.strip()[:300])
    if r.stderr.strip(): print("   [err]", r.stderr.strip()[:300])
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n" + "="*60)
        print("ERROR: No token provided.")
        print("Run:  python create_and_push.py <YOUR_TOKEN>")
        print("="*60)
        sys.exit(1)

    token = sys.argv[1].strip()
    if not (token.startswith("ghp_") or token.startswith("github_pat_") or len(token) >= 20):
        print("WARNING: Token format looks unusual. Continuing anyway...")

    print("\n" + "="*60)
    print(f"  GitHub Repo Creator + Pusher")
    print(f"  Repo: {GITHUB_USER}/{REPO_NAME}")
    print("="*60 + "\n")

    # ── Step 1: Verify token / whoami ────────────────────────────────────────
    print("[1/5] Verifying token...")
    status, user_data = api_request("/user", token)
    if status != 200:
        print(f"  ERROR: Token verification failed (HTTP {status})")
        print(f"  Response: {user_data}")
        sys.exit(1)
    actual_user = user_data.get("login", GITHUB_USER)
    print(f"  Authenticated as: @{actual_user}")

    # ── Step 2: Check if repo already exists ────────────────────────────────
    print(f"\n[2/5] Checking if repo '{REPO_NAME}' exists...")
    status, repo_data = api_request(f"/repos/{actual_user}/{REPO_NAME}", token)
    if status == 200:
        repo_url = repo_data["html_url"]
        clone_url = repo_data["clone_url"]
        print(f"  Repo already exists: {repo_url}")
    elif status == 404:
        # ── Step 3: Create repo ──────────────────────────────────────────────
        print(f"\n[3/5] Creating repository '{REPO_NAME}'...")
        status, repo_data = api_request("/user/repos", token, method="POST", body={
            "name":        REPO_NAME,
            "description": REPO_DESC,
            "private":     REPO_PRIVATE,
            "auto_init":   False,
            "has_issues":  True,
            "has_wiki":    False,
        })
        if status not in (200, 201):
            print(f"  ERROR: Failed to create repo (HTTP {status})")
            print(f"  Response: {repo_data}")
            sys.exit(1)
        repo_url  = repo_data["html_url"]
        clone_url = repo_data["clone_url"]
        print(f"  Created: {repo_url}")
    else:
        print(f"  ERROR: Unexpected status {status}: {repo_data}")
        sys.exit(1)

    # ── Step 4: Set authenticated remote ────────────────────────────────────
    print(f"\n[4/5] Configuring git remote with token auth...")
    os.chdir(REPO_DIR)
    # Build authenticated URL: https://TOKEN@github.com/user/repo.git
    auth_url = f"https://{token}@github.com/{actual_user}/{REPO_NAME}.git"
    run(f'git remote set-url origin "{auth_url}"')

    # Ensure we're on the right branch
    code, branch, _ = run("git rev-parse --abbrev-ref HEAD")
    current_branch = branch.strip() or BRANCH
    print(f"  Current branch: {current_branch}")

    # ── Step 5: Push ─────────────────────────────────────────────────────────
    print(f"\n[5/5] Pushing to GitHub...")
    code, out, err = run(f"git push -u origin {current_branch}")
    if code != 0:
        # Try force-push if remote has diverged (e.g. auto-init created a commit)
        print("  Regular push failed, trying force push...")
        code, out, err = run(f"git push -u origin {current_branch} --force")

    if code == 0:
        # Restore clean remote URL (without token embedded)
        run(f'git remote set-url origin "https://github.com/{actual_user}/{REPO_NAME}.git"')
        print("\n" + "="*60)
        print("  SUCCESS!")
        print(f"  Repository: {repo_url}")
        print(f"  Branch:     {current_branch}")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("  PUSH FAILED. Common fixes:")
        print("  1. Make sure the token has 'repo' scope")
        print("  2. Check your GitHub username in GITHUB_USER variable")
        print("  3. Try running: git push -u origin main --force")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
