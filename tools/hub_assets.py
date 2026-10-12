"""Assets for the new 'build hub' page: v2 weapon set (locked) + melee, sandbox background, zombie target, atlases."""
import sys, json, math, base64, io; sys.path.insert(0, '/home/claude/gen')
from PIL import Image, ImageDraw
import weapons_db2, weapons_db
weapons_db2.install()                     # v2 = locked set (17 + knife/machete)
import lpcframe, anim2
from weapons import *
import weapons_build3 as WB               # reuses anim_set/throw_set (re-installs v3 on import -> fix below)
weapons_db2.install()
import melee, knock, items, icons8
OUT = '/home/claude/gen/hub'; import os; os.makedirs(OUT, exist_ok=True)

ids = [k for k in weapons_db.W]
rows = []; meta = {}
for w in ids:
    c = weapons_db.W[w]['cls']
    if c.startswith('melee'):
        kind = 'knife' if w == 'knife' else 'machete'
        sets = [('walk', melee.walk('Dương', kind)), ('aim', melee.walk('Dương', kind)[:2]), ('fire', melee.slash('Dương', kind) if kind == 'machete' else melee.stab('Dương', kind))]
    else:
        a = WB.anim_set(w)
        sets = [('walk', a[0][1]), ('aim', a[1][1]), ('fire', a[2][1])]
    meta[w] = {}
    for key, fs in sets:
        meta[w][key] = {'row': len(rows), 'n': len(fs)}; rows.append(fs)
Wd = 64 * max(len(r) for r in rows)
sheet = Image.new('RGBA', (Wd, 64 * len(rows)), (0, 0, 0, 0))
for i, fs in enumerate(rows):
    for j, f in enumerate(fs): sheet.alpha_composite(f, (j * 64, i * 64))
sheet.save(OUT + '/weapons_sheet.png', optimize=True)
# zombie target: walk left 8 + knockdown 11
zw = [anim2.fr('Biến Thể', 'walk', 1, 1 + i) for i in range(8)]; zk = knock.knockdown('Biến Thể', zombie=True)
zs = Image.new('RGBA', (64 * 11, 128), (0, 0, 0, 0))
for i, f in enumerate(zw): zs.alpha_composite(f, (i * 64, 0))
for i, f in enumerate(zk): zs.alpha_composite(f, (i * 64, 64))
zs.save(OUT + '/zombie_sheet.png', optimize=True)
# weapon icon atlas (x2 with shadow), item icon atlas
icons = {w: weapons_db.icon(w, 2, 2) for w in ids}
x = 0; atlas = Image.new('RGBA', (sum(i.width + 2 for i in icons.values()), max(i.height for i in icons.values())), (0, 0, 0, 0)); irect = {}
for w, im in icons.items(): atlas.alpha_composite(im, (x, 0)); irect[w] = [x, 0, im.width, im.height]; x += im.width + 2
atlas.save(OUT + '/weapon_icons.png')
flat = [(g, n, fn, desc) for g, lst in items.GROUPS.items() for n, fn, desc in lst]
ia = Image.new('RGBA', (16 * len(flat), 16), (0, 0, 0, 0))
for i, (g, n, fn, desc) in enumerate(flat): ia.alpha_composite(fn(), (i * 16, 0))
ia.save(OUT + '/item_icons.png')
# background: level 1 without characters
blank = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
lpcframe.frame = lambda *a: blank.copy()
img, squad, e1 = lpcframe.build()
img = lpcframe.postfx(img); img.convert('RGB').save(OUT + '/level_bg.png', optimize=True)
man = weapons_db.export(OUT + '/weapons_atlas.png', OUT + '/weapons_v2_locked.json')
data = {'weapons': [{'id': w, 'name': weapons_db.W[w]['name'], 'cls': weapons_db.W[w]['cls'], 'pose': weapons_db.POSE[weapons_db.W[w]['cls']],
                     'stats': man[w]['stats'], 'anim': meta[w], 'icon': irect[w]} for w in ids],
        'items': [{'group': g, 'name': n, 'desc': desc} for g, n, fn, desc in flat], 'squad': {k: list(v) for k, v in squad.items()}, 'enemy': list(e1)}
json.dump(data, open(OUT + '/hub_data.json', 'w'), ensure_ascii=False)
print(sheet.size, len(ids), len(flat))
