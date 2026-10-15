#!/usr/bin/env bash
# Sync the seen list with the jobhunt-state branch.
#   scripts/state.sh pull   copy state/seen.json from origin/jobhunt-state
#   scripts/state.sh push   commit state/seen.json to jobhunt-state and push
set -euo pipefail
cd "$(dirname "$0")/.."
BRANCH=jobhunt-state
FILE=state/seen.json

case "${1:-}" in
  pull)
    if git fetch -q origin "$BRANCH" 2>/dev/null; then
      git show "origin/$BRANCH:$FILE" > "$FILE"
      echo "pulled seen list: $(python3 -c "import json;print(len(json.load(open('$FILE'))['roles']))") roles"
    else
      echo "no $BRANCH branch yet, starting from $FILE as committed"
    fi
    ;;
  push)
    tmp=$(mktemp -d)
    if git fetch -q origin "$BRANCH" 2>/dev/null; then
      git worktree add -q "$tmp" "origin/$BRANCH"
      git -C "$tmp" checkout -q -B "$BRANCH"
    else
      git worktree add -q --detach "$tmp"
      git -C "$tmp" checkout -q --orphan "$BRANCH"
      git -C "$tmp" rm -rq --cached . && find "$tmp" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
    fi
    mkdir -p "$tmp/state" && cp "$FILE" "$tmp/$FILE"
    git -C "$tmp" add "$FILE"
    if git -C "$tmp" diff --cached --quiet; then
      echo "seen list unchanged"
    else
      git -C "$tmp" commit -qm "Seen list update $(date -u +%F)"
      for d in 2 4 8 16; do git -C "$tmp" push -q -u origin "$BRANCH" && break || sleep $d; done
      echo "seen list pushed"
    fi
    git worktree remove --force "$tmp"
    ;;
  *) echo "usage: $0 pull|push"; exit 2 ;;
esac
