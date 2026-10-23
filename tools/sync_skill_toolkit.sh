#!/usr/bin/env bash
# Recopie la boîte à outils du repo dans la skill partageable
# (.claude/skills/roblox-skeleton-monster/toolkit). À lancer après toute modif de lib/ ou build.py.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/.claude/skills/roblox-skeleton-monster/toolkit"
rm -rf "$DEST" && mkdir -p "$DEST/lib" "$DEST/models"
cp "$ROOT/build.py" "$DEST/"
cp "$ROOT"/lib/{__init__.py,roblox.py,creature.py,anatomy.py,marine.py,CreatureEffects.server.lua} "$DEST/lib/"
cp "$ROOT"/models/{__init__.py,skeleton_trex.py,skeleton_dragon.py,skeleton_raptor.py,skeleton_triceratops.py,skeleton_hydra.py,abyss_kraken.py,abyss_megalodon.py,abyss_leviathan.py,abyss_crab.py,abyss_angler.py,forest_werewolf.py,hell_cerberus.py,hell_phoenix.py,hell_golem.py,hell_salamander.py,hell_bull.py,ice_mammoth.py,ice_sabertooth.py,ice_wendigo.py,ice_bear.py,ice_dragon.py,jungle_gorilla.py,jungle_serpent.py,jungle_jaguar.py,jungle_mantis.py,jungle_crocodile.py,grave_lich_dragon.py} "$DEST/models/"
echo "Toolkit synchronisé dans $DEST"
