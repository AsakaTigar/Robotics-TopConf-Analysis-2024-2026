#!/bin/bash
# push_to_github.sh — convenience helper for *nix hosts with git + gh in PATH.
#
# Usage:
#   ./push_to_github.sh <YOUR_GITHUB_PAT>
#
# Or:
#   export GITHUB_TOKEN=ghp_xxxx; ./push_to_github.sh
set -euo pipefail

REPO_USER="AsakaTigar"
REPO_NAME="Robotics-TopConf-Analysis-2024-2026"
BRANCH="main"

TOKEN="${1:-${GITHUB_TOKEN:-}}"
if [[ -z "$TOKEN" ]]; then
  echo "ERROR: GitHub token missing. Pass as argument or set GITHUB_TOKEN."
  echo "  ./push_to_github.sh <token>"
  exit 1
fi

cd "$(dirname "$0")"

if [[ ! -d .git ]]; then
  echo "[1/4] Initializing git repository..."
  git init -q -b "$BRANCH"
fi

echo "[2/4] Staging all changes..."
git add -A

if git diff --cached --quiet; then
  echo "  Nothing to commit. Working tree clean."
else
  echo "[3/4] Committing..."
  git -c user.email="aoduo@local" -c user.name="Aoduo Bot" \
      commit -q -m "auto: README rebuild + research track extensions + audit markers" \
      || echo "  (commit skipped)"
fi

AUTH_URL="https://${TOKEN}@github.com/${REPO_USER}/${REPO_NAME}.git"
echo "[4/4] Pushing to ${REPO_USER}/${REPO_NAME} (branch ${BRANCH})..."

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$AUTH_URL"
else
  git remote add origin "$AUTH_URL"
fi

if git push -u origin "$BRANCH"; then
  :
else
  echo "  Regular push failed; trying --force-with-lease..."
  git push -u origin "$BRANCH" --force-with-lease
fi

# Clear token from remote URL for local safety
git remote set-url origin "https://github.com/${REPO_USER}/${REPO_NAME}.git"
echo "Done."
