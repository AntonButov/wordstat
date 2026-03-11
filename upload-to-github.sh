#!/bin/bash
# Upload site/*.html to AntonButov/wordstat (branch main) via GitHub API.
# Usage: export GITHUB_TOKEN=your_token; ./upload-to-github.sh

set -e
cd "$(dirname "$0")"
: "${GITHUB_TOKEN:?Set GITHUB_TOKEN (e.g. export GITHUB_TOKEN=ghp_...)}"

for f in sales.html 1c.html bitrix24.html cases.html faq.html; do
  content_b64=$(base64 -w 0 "$f")
  resp=$(curl -s -w "\n%{http_code}" -X PUT \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/AntonButov/wordstat/contents/$f" \
    -d "{\"message\":\"Add $f\",\"content\":\"$(echo "$content_b64" | sed 's/"/\\"/g')\",\"branch\":\"main\"}")
  code=$(echo "$resp" | tail -n1)
  if [ "$code" = "200" ] || [ "$code" = "201" ]; then
    echo "OK $f (HTTP $code)"
  else
    echo "FAIL $f HTTP $code"
    echo "$resp" | sed '$d'
    exit 1
  fi
done
echo "All files uploaded."
