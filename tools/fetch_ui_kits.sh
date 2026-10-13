#!/bin/bash
# Tải lại các bộ UI / nhà cửa mã nguồn mở đã khảo sát (2026-10-13) từ GitHub.
# Nhiều repo Unity dùng Git LFS: clone thưa chỉ cho con trỏ; nội dung thật lấy qua media.githubusercontent.com.
# Dùng: tools/fetch_ui_kits.sh /đường/dẫn/đích
set -e
DST=${1:-/home/user/ui2}; mkdir -p "$DST"; cd "$DST"
clone() { r=$1; d=$2; shift 2; [ -d "$d/.git" ] && return
  GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 --filter=blob:none --sparse "https://github.com/$r" "$d"
  (cd "$d" && git sparse-checkout set "$@"); }
# --- UI ---
clone Spyridon-Pikoulas/godot-pixel-ui-fantasy-free pixel_ui_fantasy addons        # B parchment, CC BY 4.0 (heyheythere)
clone miramidev/Turn-Based-RPG tinyswords "Assets/Content/Imports/Tiny Swords/UI"   # F Tiny Swords (Pixel Frog, free, không phân phối lại)
clone Raveneer-o1/adepts-of-establishment bdragon "Arts/itch assets"                # E ETA Fantasy Minimal GUI (commercial-free), BDragon1727, ELV Retro Inventory
clone Udaya-X2/castle-chase cryo "Assets/Art/Cryo's Mini GUI"                       # G Cryo's Mini GUI
clone maxhimmel/minipede goldenui "Assets/Art/UI/OpenGameArt"                       # D Golden UI (Buch, CC BY-SA 3.0)
clone SAE-Geneve/924-UnityCourse-Platformer kenney_fantasy "Assets/Packs/kenney_fantasy-ui-borders"  # Kenney Fantasy UI Borders (CC0)
clone so-andrew/DIG3878_Final sprout "Assets/Sprout Lands - UI Pack - Basic pack"   # Sprout Lands UI (Cup Nooble)
# C Kenney UI Pack Pixel Adventure: project2D/Assets/Art/Kenney/PixelAdventureUI (xem /home/user/ui/project2D)
# --- nhà cửa ---
clone series-ai/jam-ready-assets jam kenney-roguelike-city-pack kenney-roguelike-base-pack kenney-tiny-town kenney-roguelike-interior-pack kenney-topdown-shooter  # CC0
clone NeirizaBagas/Technical-Test-Toge tinyswords_b "Assets/Tiny Swords/Buildings"
clone arianne/stendhal stendhal "data/maps/tileset/building" "data/maps/tileset/object" "data/maps/tileset/item"  # CC BY-SA 3.0 / GPL
# --- lấy nội dung LFS ---
python3 "$(dirname "$0")/lfs_media_fetch.py" pixel_ui_fantasy tinyswords bdragon cryo goldenui kenney_fantasy sprout jam tinyswords_b
