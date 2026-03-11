#!/usr/bin/env bash
# =============================================================
# push_to_github.sh
# Push Robotics-TopConf-Analysis-2024-2026 to GitHub
# Remote: https://github.com/AsakaTigar/Robotics-TopConf-Analysis-2024-2026
# =============================================================
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTE_URL="https://github.com/AsakaTigar/Robotics-TopConf-Analysis-2024-2026.git"
REMOTE_SSH="git@github.com:AsakaTigar/Robotics-TopConf-Analysis-2024-2026.git"

echo "========================================================"
echo "  Robotics TopConf Analysis 2024-2026 — GitHub Push"
echo "========================================================"
echo ""
echo "Repo dir : $REPO_DIR"
echo "Remote   : $REMOTE_URL"
echo ""

cd "$REPO_DIR"

# --- Git init (if not already done) ---
if [ ! -d ".git" ]; then
    echo "[1/6] Initializing git repository..."
    git init
    git checkout -b main 2>/dev/null || git checkout -b master 2>/dev/null || true
else
    echo "[1/6] Git repo already initialized."
fi

# --- Configure user (skip if already set) ---
git config user.name  "$(git config --global user.name  2>/dev/null || echo 'Robotics Paper Bot')"
git config user.email "$(git config --global user.email 2>/dev/null || echo 'bot@example.com')"

# --- Stage all files ---
echo "[2/6] Staging files..."
git add README.md
git add robotics_papers_2024_2026_analysis.csv
git add build_readme.py
git add push_to_github.sh
git add LICENSE 2>/dev/null || true
git add .gitignore 2>/dev/null || true

# --- Commit ---
echo "[3/6] Committing..."
git diff --cached --quiet && echo "  (nothing new to commit)" || \
    git commit -m "Initial commit: Robotics TopConf Paper Analysis 2024-2026

- 120 paper/trend entries from ICRA, IROS, RSS, CoRL
- Years: 2024 (60 papers), 2025 (40 papers), 2026 (20 trend entries)
- Robot type classification & GitHub code search results
- Structured README with badges and Markdown tables
- Inspired by: https://github.com/Songwxuan/Embodied-AI-Paper-TopConf"

# --- Add remote ---
echo "[4/6] Adding remote..."
if git remote | grep -q "origin"; then
    echo "  Remote 'origin' already exists — skipping."
    git remote -v
else
    # Try SSH first; fall back to HTTPS
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "  SSH key detected — using SSH remote."
        git remote add origin "$REMOTE_SSH"
    else
        echo "  Using HTTPS remote (token auth)."
        git remote add origin "$REMOTE_URL"
    fi
fi

# --- Push ---
echo "[5/6] Pushing to GitHub..."
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push -u origin "$BRANCH" && echo "" && echo "[6/6] Push successful!" || {
    echo ""
    echo "========================================================"
    echo "  PUSH FAILED — Possible reasons:"
    echo "  1. Repo not yet created on GitHub. Go to:"
    echo "     https://github.com/new"
    echo "     Create repo named: Robotics-TopConf-Analysis-2024-2026"
    echo "     (do NOT initialize with README)"
    echo "  2. Authentication not set up. Options:"
    echo "     a) SSH:   ssh-keygen -t ed25519; copy ~/.ssh/id_ed25519.pub to GitHub"
    echo "     b) Token: git remote set-url origin https://TOKEN@github.com/AsakaTigar/Robotics-TopConf-Analysis-2024-2026.git"
    echo "  3. Re-run this script after fixing auth."
    echo "========================================================"
    exit 1
}

echo ""
echo "========================================================"
echo "  Done! Repository is live at:"
echo "  https://github.com/AsakaTigar/Robotics-TopConf-Analysis-2024-2026"
echo "========================================================"
