import sys, json, math; sys.path.insert(0, '.')
from PIL import Image, ImageDraw
import weapons_db2, weapons_db
weapons_db2.install_v3()
from weapons import *
from anim2 import fr
OUTD = '/mnt/user-data/outputs/artifacts/c82b9169-ee10-4565-aca3-4592040c933d'
N = 'Dương'

def skin_pts(f, y0, y1):
    px = f.load(); pts = []
    for y in range(max(0, y0), min(64, y1)):
        for x in range(64):
            r, g_, b, a = px[x, y]
            if a and r > 150 and r > g_ > b and r - b > 45: pts.append((x, y))
    return pts

def hand_at(f, side='left'):
    """Centroid of the hand: skin pixels below the head, on the requested side."""
    top = f.getbbox()[1]; pts = skin_pts(f, top + 23, top + 42)
    if not pts: return (32, top + 28)
    edge = min(p[0] for p in pts) if side == 'left' else max(p[0] for p in pts)
    sel = [p for p in pts if abs(p[0] - edge) <= 3]
    return (sum(p[0] for p in sel) // len(sel), sum(p[1] for p in sel) // len(sel))

def grip_over(c, f, dx, box):
    """Redraw the hand's skin pixels on top of the grenade so the fingers wrap it."""
    px = f.load(); pc = c.load(); x0, y0, x1, y1 = box
    for y in range(max(0, y0), min(64, y1)):
        for x in range(max(0, x0 - dx), min(64, x1 - dx)):
            r, g_, b, a = px[x, y]
            if a and r > 150 and r > g_ > b and r - b > 45 and 0 <= x + dx < 64: pc[x + dx, y] = (r, g_, b, a)

def throw_set(w):
    """Grenades. Hold: both hands together in front of the belly (spellcast f2) with the grenade in them.
    Pull pin: hands spread (spellcast f3) - grenade stays in the front hand, the rear hand pulls the ring away.
    Throw: grenade raised behind the head on the wind-up, released on the forward swing."""
    g = weapons_db.sprite(w); DX = 8
    def ring(d, x, y):
        d.ellipse((x - 2, y - 2, x + 1, y + 1), outline=(236, 206, 110, 255)); d.point((x - 1, y - 1), fill=(255, 240, 170, 255))
    def put_g(c, hx, hy): c.alpha_composite(g, (hx - g.width // 2, hy - g.height + 2))
    hold = []
    for i in range(2):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); f = fr(N, 'spellcast', 1, 2); c.alpha_composite(f, (DX, 0))
        put_g(c, 24 + DX, 43 + (i % 2)); hands_over(c, Image.new('RGBA', (64, 64)).__class__.__call__ if False else _shift(f, DX), (0, 40, 64, 48)); hold.append(c)
    pin = []
    for i in range(4):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        if i < 2:
            f = fr(N, 'spellcast', 1, 2); c.alpha_composite(f, (DX, 0)); put_g(c, 24 + DX, 43)
            d = ImageDraw.Draw(c); ring(d, 27 + DX, 37); hands_over(c, _shift(f, DX), (0, 40, 64, 48))
        else:
            f = fr(N, 'spellcast', 1, 3); c.alpha_composite(f, (DX, 0)); put_g(c, 22 + DX, 42)
            d = ImageDraw.Draw(c); rx = 40 + DX + (i - 2) * 3; ring(d, rx, 41 - (i - 2))
            d.line([(24 + DX, 37), (rx - 2, 40 - (i - 2))], fill=(160, 160, 172, 255)) if i == 2 else None
        pin.append(c)
    th = []
    for k in range(6):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); f = fr(N, 'halfslash', 1, k); c.alpha_composite(f, (DX, 0)); bb = f.getbbox()
        if k < 3: c.alpha_composite(g, (bb[2] + DX - 6 - k * 3, bb[1] + 10 + k * 2))
        else:
            t = (k - 2) / 4; x = 22 - 26 * t; y = 30 - 14 * math.sin(t * math.pi)
            c.alpha_composite(g.rotate(-90 * t, expand=True), (int(x), int(y)))
        th.append(c)
    return [('Cầm', hold), ('Rút chốt', pin), ('Ném', th)]

def _shift(f, dx):
    c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(f, (dx, 0)); return c

def anim_set(w):
    c = weapons_db.W[w]['cls']
    if c == 'throw': return throw_set(w)
    if c == 'pistol':
        return [('Đi cầm', walk_armed(N, w)), ('Ngắm', held(N, w, [fr(N, 'shoot', 1, 4)] * 2)), ('Bắn', held(N, w, [fr(N, 'shoot', 1, 4)] * 4, fire=True))]
    n = {'smg': 8, 'rifle': 8, 'shotgun': 6, 'sniper': 6, 'launcher': 6}[c]
    return [('Đi cầm', walk_armed(N, w)), ('Ngắm', long_aim(N, w, 2)), ('Bắn' if c in ('shotgun', 'sniper', 'launcher') else 'Bắn loạt', long_aim(N, w, n, fire=True))]

A = ['pistol', 'revolver', 'silenced', 'ar_tan', 'ar_scope', 'ar_red', 'lmg', 'sniper_tan']
B = ['sniper_black', 'shotgun', 'sawed', 'rpg', 'grenade', 'smoke']
SM = [k for k in weapons_db.W if k.startswith('smg_')]
for part, chunk in (('a', A), ('b', B), ('c', SM)):
    rows = [(w, anim_set(w)[1:] if part == 'c' else anim_set(w)) for w in chunk]
    flat = [(w, lab, fs) for w, items in rows for lab, fs in items]
    Wd = 64 * max(len(fs) for _, _, fs in flat)
    sh = Image.new('RGBA', (Wd, 64 * len(flat)), (0, 0, 0, 0))
    for i, (_, _, fs) in enumerate(flat):
        for j, f in enumerate(fs): sh.alpha_composite(f, (j * 64, i * 64))
    sh.save(f'{OUTD}/weapons3{part}.png', optimize=True)
    json.dump({'w': Wd, 'h': sh.height, 'ids': chunk, 'meta': [(w, lab, len(fs)) for w, lab, fs in flat]}, open(f'weapons3{part}.json', 'w'), ensure_ascii=False)
    bg = Image.new('RGBA', sh.size, (40, 44, 56, 255)); bg.alpha_composite(sh); bg.save(f'/tmp/wp3{part}.png')
weapons_db.export(OUTD + '/weapons_atlas.png', '/home/claude/gen/weapons.json')
print('ok')
