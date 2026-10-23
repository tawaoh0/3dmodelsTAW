#!/usr/bin/env bash
# Recopie la boîte à outils du repo dans la skill partageable
# (.claude/skills/roblox-skeleton-monster/toolkit). À lancer après toute modif de lib/ ou build.py.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/.claude/skills/roblox-skeleton-monster/toolkit"
rm -rf "$DEST" && mkdir -p "$DEST/lib" "$DEST/models"
cp "$ROOT/build.py" "$DEST/"
cp "$ROOT"/lib/{__init__.py,roblox.py,creature.py,anatomy.py,CreatureEffects.server.lua} "$DEST/lib/"
cp "$ROOT"/models/{__init__.py,skeleton_trex.py,skeleton_dragon.py} "$DEST/models/"
echo "Toolkit synchronisé dans $DEST"
