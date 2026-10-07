#!/usr/bin/env bash
# Publishes the agentic-pm scaffold to your public GitHub repo.
# Run:  bash publish-agentic-pm.sh
# Uses YOUR git login (nothing of Muse's). Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")"

# 1. Noreply identity so your personal email never lands in public history
git config user.name  "${GIT_NAME:-malagasr}"
git config user.email "${GIT_EMAIL:-66905324+malagasr@users.noreply.github.com}"

# 2. Fresh repo pointing at the public GitHub repo (created via browser)
if [ ! -d .git ]; then git init -b main; fi
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/malagasr/agentic-pm.git"

# 3. Commit & push
git add -A
git commit -m "v0.1 scaffold: release-train agent + repo skeleton" --allow-empty
git push -u origin main --force

echo "Published: https://github.com/malagasr/agentic-pm"
