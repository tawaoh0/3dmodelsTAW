#!/usr/bin/env bash
# Prépare un projet pour générer des monstres squelettes Roblox.
#   bash setup_project.sh [dossier-du-projet]   (défaut : dossier courant)
# - copie la boîte à outils (build.py, lib/, exemples) SANS écraser les fichiers existants ;
# - crée .venv-blender et installe bpy (Blender en module Python, headless).
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="$(cd "${1:-.}" && pwd)"

mkdir -p "$PROJECT/lib" "$PROJECT/models" "$PROJECT/exports" "$PROJECT/previews"
cp -rn "$SKILL_DIR/toolkit/." "$PROJECT/" 2>/dev/null || cp -r --update=none "$SKILL_DIR/toolkit/." "$PROJECT/"
echo "Boîte à outils présente dans $PROJECT"

PY="$PROJECT/.venv-blender/bin/python"
if [ -x "$PY" ] && "$PY" -c "import bpy" 2>/dev/null; then
  echo "bpy déjà installé : $("$PY" -c 'import bpy; print(bpy.app.version_string)')"
else
  BASE_PY="$(command -v python3.13 || command -v python3)"
  echo "Création du venv avec $BASE_PY ($("$BASE_PY" --version))"
  "$BASE_PY" -m venv "$PROJECT/.venv-blender"
  if ! "$PY" -m pip install -q bpy; then
    echo "pip install bpy a échoué : bpy 5.x demande Python 3.13 (4.x : Python 3.11)." >&2
    echo "Alternative : installer Blender et lancer « blender -b -P build.py -- <modele> »." >&2
    exit 1
  fi
  echo "bpy installé : $("$PY" -c 'import bpy; print(bpy.app.version_string)')"
fi
grep -qx '.venv-blender/' "$PROJECT/.gitignore" 2>/dev/null || echo '.venv-blender/' >> "$PROJECT/.gitignore"
echo "Prêt. Lancer : $PY build.py <modele>"
