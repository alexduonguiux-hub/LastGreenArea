"""Weapon database — original pixel sprites (muzzle points left), drawn as character maps.
Each entry: held sprite (game scale), grip + muzzle offsets, animation class used to pick the pose set,
and an item icon (sprite x2 with hard drop shadow). export() writes an atlas PNG + weapons.json so the game can
load the right sprite/anim set for whatever weapon a character picks up."""
import json
from PIL import Image, ImageDraw

PAL = {'d': (46, 48, 56), 'm': (86, 90, 100), 'l': (138, 144, 156), 'w': (204, 210, 218), 'c': (226, 230, 236),
       'b': (104, 60, 38), 'B': (150, 88, 54), 'o': (118, 120, 82), 'O': (168, 168, 120), 'g': (214, 170, 82),
       'r': (180, 50, 40), 'k': (18, 18, 22)}
OUT = (16, 16, 20, 255)

W = {
 'pistol': dict(name='Súng ngắn', cls='pistol', grip=(7, 4), muzzle=(0, 1), dmg=2, rng=2, noise=3, rate=3, map=[
  '.wwwwwwww.',
  'lmmmmmmmmm',
  '.ddddddmmm',
  '......dmm.',
  '.....dmm..',
  '.....ddd..']),
 'silenced': dict(name='Súng giảm thanh', cls='pistol', grip=(15, 4), muzzle=(0, 1), dmg=2, rng=2, noise=1, rate=3, map=[
  '.........wwwwwwww.',
  'mmmmmmmmlmmmmmmmmm',
  'dddddddd.ddddddmmm',
  '..............dmm.',
  '.............dmm..',
  '.............ddd..']),
 'heavy_pistol': dict(name='Súng ngắn crôm', cls='pistol', grip=(9, 4), muzzle=(0, 1), dmg=3, rng=2, noise=4, rate=2, map=[
  'cccccccccccw',
  'wcccccccccwc',
  'dddddddmmccc',
  '........dcc.',
  '.......dcc..',
  '.......ddd..']),
 'uzi': dict(name='Tiểu liên nhỏ', cls='smg', grip=(6, 5), muzzle=(0, 2), dmg=1, rng=2, noise=4, rate=5, map=[
  '..m......m..',
  'mmmmmmmmmmmm',
  'dlllllllmmmd',
  'dddddmmmmddd',
  '.....mm.....',
  '.....lm.....',
  '.....mm.....',
  '.....lm.....',
  '.....dd.....']),
 'smg': dict(name='Tiểu liên', cls='smg', grip=(13, 5), muzzle=(0, 2), dmg=2, rng=3, noise=4, rate=5, map=[
  '..m...........m.....',
  'mmmmmmmmmmmmmmmmmm..',
  'dlllmmmlllllmmmmmmmd',
  '.dmmmmmmmmmmmmmmmmdd',
  '....dmm..mmd..m...dd',
  '....dm...md...md..dd',
  '.........mm...md....',
  '.........dd.........']),
 'bullpup': dict(name='Súng trường bullpup', cls='rifle', grip=(10, 4), muzzle=(0, 1), dmg=3, rng=4, noise=4, rate=4, map=[
  '......mmmmmmmmmmmmm...',
  'mmmmmmmgggggmmggggggm.',
  'ddmmmmmmmmmmmmmmmmmmmd',
  '..dmmmmmmmmmmmmmmmmmmd',
  '....dmm....mmd.....dd.',
  '....dm......md........']),
 'shotgun': dict(name='Súng săn bơm', cls='shotgun', grip=(20, 3), muzzle=(0, 0), dmg=4, rng=1, noise=5, rate=1, map=[
  'llllllllllllllllllllll......',
  'mmmmmmmmmmmmmmmmmmmmmmmmm...',
  '.dddd.d.d.d.ddddmmmmmmmmmmm.',
  '.................ddmmmmmmmmm',
  '.....................dmmmmmm',
  '........................ddd.']),
 'ak': dict(name='Súng trường báng gỗ', cls='rifle', grip=(13, 4), muzzle=(0, 1), dmg=3, rng=4, noise=5, rate=4, map=[
  '..m........................',
  'mmmmmmBBBBBBmmmmmmBBBBBBBB.',
  'dddmmmbbbbbbmmmmmmmBBBBBBBB',
  '.......dmmd..BB.....bbbbbbb',
  '.......dmm...B.............',
  '.......dm..................']),
 'sniper': dict(name='Súng bắn tỉa', cls='sniper', grip=(19, 4), muzzle=(0, 2), dmg=5, rng=5, noise=5, rate=1, map=[
  '...........mmmmmmmm...........',
  '...........ddmmmmd............',
  'lllllllllllllllllllllllll.....',
  'mmmmmmmmmmOOOOOOOOOOOOOOOOOOO.',
  'ddddddddddooo.oooo..ooooooooo.',
  '..........oo..........ooo.oooo',
  '.......................o...ooo']),
 'm4': dict(name='Súng trường', cls='rifle', grip=(13, 5), muzzle=(0, 2), dmg=3, rng=4, noise=4, rate=4, map=[
  '...........mmmmm........',
  '.....m....mlllllm.......',
  'mmmmmmmmmmmmmmmmmmmmmmm.',
  'dlllmmmmmmmmmmmmmmmmmmmm',
  '..dddddmmmmmmmmmmdddmmmm',
  '........mmd..mm.....dmmm',
  '........mm...md.........',
  '.........d...md.........']),
}

def sprite(wid):
    rows = W[wid]['map']; h = len(rows); w = max(len(r) for r in rows)
    im = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0)); px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.': px[x + 1, y + 1] = PAL[ch] + (255,)
    sol = [[px[x, y][3] > 0 for x in range(w + 2)] for y in range(h + 2)]
    for y in range(h + 2):
        for x in range(w + 2):
            if not sol[y][x] and any(0 <= x + dx < w + 2 and 0 <= y + dy < h + 2 and sol[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): px[x, y] = OUT
    return im

def held(wid):
    e = W[wid]; im = sprite(wid)
    return im, (e['grip'][0] + 1, e['grip'][1] + 1), (e['muzzle'][0] + 1, e['muzzle'][1] + 1)

def icon(wid, k=2, shadow=2):
    s = sprite(wid); s = s.resize((s.width * k, s.height * k), Image.NEAREST)
    out = Image.new('RGBA', (s.width + shadow, s.height + shadow), (0, 0, 0, 0))
    sh = Image.new('RGBA', s.size, (0, 0, 0, 0)); sh.putalpha(s.split()[3].point(lambda v: 150 if v else 0))
    out.alpha_composite(sh, (shadow, shadow)); out.alpha_composite(s); return out

POSE = {'pistol': 'one_hand', 'smg': 'shoulder', 'rifle': 'shoulder', 'shotgun': 'shoulder', 'sniper': 'shoulder'}

def export(png, js):
    ids = list(W); x = 0; rects = {}; sprites = {i: sprite(i) for i in ids}
    atlas = Image.new('RGBA', (sum(s.width + 2 for s in sprites.values()), max(s.height for s in sprites.values())), (0, 0, 0, 0))
    for i in ids:
        atlas.alpha_composite(sprites[i], (x, 0)); rects[i] = [x, 0, sprites[i].width, sprites[i].height]; x += sprites[i].width + 2
    atlas.save(png)
    man = {i: {'name': W[i]['name'], 'class': W[i]['cls'], 'pose_set': POSE[W[i]['cls']], 'atlas_rect': rects[i],
               'grip': [W[i]['grip'][0] + 1, W[i]['grip'][1] + 1], 'muzzle': [W[i]['muzzle'][0] + 1, W[i]['muzzle'][1] + 1],
               'stats': {'damage': W[i]['dmg'], 'range': W[i]['rng'], 'noise': W[i]['noise'], 'rate': W[i]['rate']},
               'anims': {'walk': f'{POSE[W[i]["cls"]]}_walk', 'aim': f'{POSE[W[i]["cls"]]}_aim', 'fire': f'{POSE[W[i]["cls"]]}_fire'}} for i in ids}
    json.dump(man, open(js, 'w'), ensure_ascii=False, indent=1)
    return man
