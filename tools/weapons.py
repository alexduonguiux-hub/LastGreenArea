import sys, json, math, random; sys.path.insert(0, '.')
from PIL import Image, ImageDraw
import lpc, polish
from anim2 import fr
OUTD = '/mnt/user-data/outputs/artifacts/c82b9169-ee10-4565-aca3-4592040c933d'
MET = (58, 60, 66); MET2 = (92, 96, 104); HI = (150, 156, 164); WOOD = (110, 72, 42); WOOD2 = (140, 96, 58); OUT = (18, 16, 18)

def cls(kind):
    import weapons_db
    return weapons_db.W[kind]['cls'] if kind in weapons_db.W else kind

def gun(kind):
    """Left-facing weapon sprites, muzzle on the left. Returns (image, grip_offset, muzzle_offset).
    Weapons in weapons_db are loaded from the database (already outlined: callers' outline() adds a harmless 1px pad)."""
    import weapons_db
    if kind in weapons_db.W:
        im, g, m = weapons_db.held(kind)
        return im.crop((1, 1, im.width - 1, im.height - 1)), (g[0] - 1, g[1] - 1), (m[0] - 1, m[1] - 1)
    if kind == 'pistol':
        im = Image.new('RGBA', (10, 7), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 8, 2), fill=MET); d.line([(1, 0), (7, 0)], fill=HI); d.rectangle((5, 2, 8, 6), fill=MET2); d.point((4, 3), fill=MET)
        return im, (7, 4), (0, 1)
    if kind == 'sling':
        im = Image.new('RGBA', (8, 9), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.line([(4, 8), (4, 4), (1, 0)], fill=WOOD2, width=2); d.line([(4, 4), (7, 0)], fill=WOOD2, width=2); d.line([(1, 1), (6, 1)], fill=(200, 160, 120))
        return im, (4, 7), (3, 0)
    if kind == 'shotgun':
        im = Image.new('RGBA', (24, 7), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle((0, 1, 14, 2), fill=MET); d.line([(0, 1), (13, 1)], fill=HI); d.rectangle((6, 3, 12, 4), fill=WOOD2)
        d.polygon([(14, 1), (23, 2), (23, 6), (18, 6), (14, 3)], fill=WOOD); d.line([(15, 2), (22, 3)], fill=WOOD2)
        return im, (16, 4), (0, 1)
    if kind == 'smg':
        BLK = (40, 42, 46); BLK2 = (66, 70, 76)
        im = Image.new('RGBA', (22, 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle((0, 3, 3, 4), fill=BLK)                                  # muzzle
        d.rectangle((3, 2, 9, 5), fill=BLK2); [d.point((x, 3), fill=BLK) for x in (4, 6, 8)]   # perforated shroud
        d.rectangle((9, 1, 16, 5), fill=BLK); d.line([(9, 1), (16, 1)], fill=HI)              # receiver
        d.polygon([(10, 6), (13, 6), (12, 11), (9, 11)], fill=BLK2)                           # long angled magazine
        d.line([(10, 6), (9, 11)], fill=BLK)
        d.rectangle((14, 6, 15, 8), fill=BLK)                                                  # pistol grip
        d.rectangle((16, 3, 21, 3), fill=BLK2); d.rectangle((21, 2, 21, 6), fill=BLK2); d.line([(16, 5), (21, 5)], fill=BLK2)  # folding wire stock
        return im, (14, 7), (0, 3)
    if kind == 'lmg':
        im = Image.new('RGBA', (26, 11), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle((0, 2, 17, 4), fill=MET); d.line([(0, 2), (16, 2)], fill=HI); d.rectangle((9, 1, 15, 6), fill=MET2)
        d.rectangle((10, 6, 14, 9), fill=(70, 80, 56)); d.line([(3, 5), (1, 10)], fill=MET); d.line([(3, 5), (5, 10)], fill=MET)
        d.polygon([(17, 2), (25, 3), (25, 7), (20, 7), (17, 5)], fill=WOOD)
        return im, (17, 6), (0, 3)
    if kind == 'hmg':
        im = Image.new('RGBA', (30, 18), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle((0, 3, 20, 5), fill=MET); d.line([(0, 3), (19, 3)], fill=HI)
        d.rectangle((4, 2, 14, 6), fill=MET2)
        for x in range(5, 14, 2): d.point((x, 4), fill=OUT)
        d.rectangle((18, 1, 26, 7), fill=MET2); d.line([(26, 3), (29, 1)], fill=MET); d.line([(26, 5), (29, 7)], fill=MET)
        d.line([(20, 7), (14, 17)], fill=MET, width=2); d.line([(20, 7), (27, 17)], fill=MET, width=2); d.line([(20, 7), (20, 17)], fill=MET2, width=1)
        for k in range(5): d.rectangle((16 + k * 2, 8 + k, 17 + k * 2, 9 + k), fill=(196, 160, 60))
        return im, (27, 4), (0, 4)
    raise ValueError(kind)

def outline(im):
    W, H = im.size; px = im.load(); o = Image.new('RGBA', (W + 2, H + 2), (0, 0, 0, 0)); po = o.load()
    for y in range(-1, H + 1):
        for x in range(-1, W + 1):
            inside = 0 <= x < W and 0 <= y < H and px[x, y][3]
            if not inside and any(0 <= x + dx < W and 0 <= y + dy < H and px[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): po[x + 1, y + 1] = OUT + (255,)
    o.alpha_composite(im, (1, 1)); return o

def front_hand(f):
    a = f.split()[3].load(); bb = f.getbbox(); top = bb[1]
    lo, hi = top + 17, top + 30
    for x in range(64):
        ys = [y for y in range(lo, hi) if a[x, y]]
        if ys: return x, sum(ys) // len(ys)
    return 22, 34

def muzzle(d, x, y, big=False):
    c1, c2 = (255, 240, 170, 255), (255, 170, 60, 255)
    r = 5 if big else 3
    d.polygon([(x, y - r), (x - 2 * r, y), (x, y + r), (x - r // 2, y)], fill=c2); d.ellipse((x - r, y - r // 2, x, y + r // 2), fill=c1)

def casing(d, x, y): d.rectangle((x, y, x + 1, y), fill=(220, 180, 70, 255))

def held(name, kind, pose_frames, aim=True, fire=False):
    g, grip, mz = gun(kind); g = outline(g); grip = (grip[0] + 1, grip[1] + 1); mz = (mz[0] + 1, mz[1] + 1)
    out = []
    for i, f in enumerate(pose_frames):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(f)
        hx, hy = front_hand(f) if aim else (24, 38)
        rec = 1 if fire and i % 2 == 0 else 0
        gx, gy = hx - grip[0] + (grip[0] // 2 if cls(kind) in ('shotgun', 'smg', 'lmg', 'rifle', 'sniper') else 0) + rec, hy - grip[1] + 1
        if cls(kind) == 'pistol': gx, gy = hx - grip[0] + 2 + rec, hy - grip[1] + 2
        c.alpha_composite(g, (gx, gy))
        if fire and i % 2 == 0:
            d = ImageDraw.Draw(c); muzzle(d, gx + mz[0], gy + mz[1], big=cls(kind) in ('lmg', 'hmg', 'shotgun', 'sniper', 'rifle'))
        if fire and kind not in ('sling',):
            d = ImageDraw.Draw(c); casing(d, gx + grip[0] + 2, gy - 2 + (i % 4))
        out.append(c)
    return out

def hands_over(c, f, box):
    """Re-draw the character's skin pixels (hands) that fall inside the gun box on top of the gun, so the hands grip it."""
    px = f.load(); pc = c.load(); x0, y0, x1, y1 = box
    for y in range(max(0, y0), min(64, y1)):
        for x in range(max(0, x0), min(64, x1)):
            r, g, b, a = px[x, y]
            if a and r > 150 and r > g > b and r - b > 45: pc[x, y] = (r, g, b, a)

def body_front(f, row):
    a = f.split()[3].load()
    return next((x for x in range(64) if any(a[x, y] for y in range(max(0, row - 3), min(64, row + 4)))), 20)

def skin_of(f):
    px = f.load()
    for y in range(64):
        for x in range(64):
            r, g, b, a = px[x, y]
            if a and r > 170 and r > g > b and r - b > 50: return (r, g, b)
    return (232, 172, 128)

def support_hand(c, f, gx, gy, g):
    """Gun sits behind the body (stock on the far shoulder); the near hand is drawn in front, under the barrel, just ahead of the chest."""
    a = f.split()[3].load(); bb = f.getbbox()
    row = gy + g.height // 2
    front = next((x for x in range(64) if any(a[x, y] for y in range(max(0, row - 3), min(64, row + 4)))), bb[0])
    hx, hy = front - 3, row
    d = ImageDraw.Draw(c); sk = skin_of(f)
    d.rectangle((hx - 1, hy - 1, hx + 3, hy + 2), fill=(30, 20, 18, 255)); d.rectangle((hx, hy, hx + 2, hy + 1), fill=sk + (255,))
    d.point((hx, hy), fill=tuple(min(255, v + 25) for v in sk) + (255,))

def long_aim(name, kind, n=8, fire=False):
    """Shouldered long gun: both hands together in front of the chest (spellcast frames), stock at the shoulder,
    barrel forward at chest height, hands drawn over the gun."""
    g, grip, mz = gun(kind); g = outline(g); mz = (mz[0] + 1, mz[1] + 1)
    out = []
    for i in range(n):
        f = fr(name, 'spellcast', 1, 1 + (i % 2 if not fire else 0))
        bb = f.getbbox(); cx = (bb[0] + bb[2]) // 2; top = bb[1]
        rec = 1 if fire and i % 2 == 0 else 0
        gy = top + 26 - g.height // 2 - (10 if cls(kind) == 'launcher' else 0); gx = body_front(f, gy + g.height // 2 + (8 if cls(kind) == 'launcher' else 0)) - int(g.width * (0.75 if cls(kind) == 'smg' else 0.55 if cls(kind) == 'launcher' else 0.62)) + rec
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(g, (gx, gy)); c.alpha_composite(f)
        support_hand(c, f, gx, gy, g)
        d = ImageDraw.Draw(c)
        if fire and i % 2 == 0: muzzle(d, gx + mz[0], gy + mz[1], big=cls(kind) in ('lmg', 'shotgun', 'sniper', 'rifle'))
        if fire: casing(d, cx + 4, gy - 2 + (i % 4))
        out.append(c)
    return out

def aim_frames(name, n=8, idx=(7, 8)):
    if name == 'Hùng' and idx == (7, 8): idx = (4, 4)
    return [fr(name, 'shoot', 1, idx[i % len(idx)]) for i in range(n)]

def walk_armed(name, kind):
    g, grip, _ = gun(kind); g = outline(g)
    out = []
    for i in range(8):
        f = fr(name, 'walk', 1, 1 + i); c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(f)
        bb = f.getbbox(); cx = (bb[0] + bb[2]) // 2; bob = 1 if i % 4 in (1, 2) else 0
        top = bb[1]
        if cls(kind) in ('pistol', 'sling'):
            c.alpha_composite(g.rotate(-35, expand=True, resample=Image.NEAREST), (cx - 10, top + 25 + bob))
        else:
            gy = top + 27 - g.height // 2 + bob - (11 if cls(kind) == 'launcher' else 0); gx = body_front(f, gy + g.height // 2 + (8 if cls(kind) == 'launcher' else 0)) - int(g.width * (0.75 if cls(kind) == 'smg' else 0.55 if cls(kind) == 'launcher' else 0.62))
            c2 = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c2.alpha_composite(g, (gx, gy)); c2.alpha_composite(f); support_hand(c2, f, gx, gy, g); c = c2
        out.append(c)
    return out

def hmg_set(name):
    g, grip, mz = gun('hmg'); g = outline(g)
    def base(i, fire):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        c.alpha_composite(fr(name, 'sit', 1, 0), (14, -2))
        rec = 1 if fire and i % 2 == 0 else 0
        c.alpha_composite(g, (6 + rec, 38)); d = ImageDraw.Draw(c)
        if fire and i % 2 == 0: muzzle(d, 7, 43, big=True)
        if fire:
            for k in range(3): casing(d, 34 + k * 2, 46 + ((i + k) % 4) * 2)
        return c
    return [base(i, False) for i in range(2)], [base(i, True) for i in range(8)]

def knife_set(name):
    src = 'B_' + name
    bt, parts = lpc.CHARS[src]
    lpc.CHARS[src + '_k'] = (bt, parts + [('weapons/sword/weapon_sword_dagger.json', None, None)])
    def frames(anim, row, cols):
        s = lpc.sheet(src + '_k', anim)
        return [polish.polish(s.crop((c * 64, row * 64, c * 64 + 64, row * 64 + 64))) for c in cols]
    return frames('walk', 1, range(1, 9)), frames('slash', 1, range(6)), frames('thrust', 1, range(8))
