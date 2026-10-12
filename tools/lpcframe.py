import math, random
from PIL import Image, ImageDraw, ImageFont
from lpcmap import *
from lpcscene import base_map, river_x, path_y, MW, MH
from lpc import sheet

FD = '/usr/share/fonts/truetype/dejavu/'
F9 = ImageFont.truetype(FD + 'DejaVuSans.ttf', 9); F9B = ImageFont.truetype(FD + 'DejaVuSans-Bold.ttf', 9)
F13 = ImageFont.truetype(FD + 'DejaVuSans-Bold.ttf', 13)
F8 = ImageFont.truetype(FD + 'DejaVuSans.ttf', 8)
INK = (233, 228, 214); DIM = (170, 165, 150); BRASS = (184, 162, 106); TEAL = (63, 217, 180); RED = (232, 85, 61); GOLD = (242, 193, 78)
PANEL = (14, 18, 15); EDGE = (74, 88, 64); EDGE2 = (32, 40, 30)
TEAM = {'Dương': (111, 143, 78), 'Hùng': (224, 123, 57), 'Ny': (237, 235, 228), 'Sơn': (94, 122, 134)}
W, H, OFFY = 800, 450, 20

def frame(name, anim, row, col):
    s = sheet(name, anim)
    return s.crop((col*64, row*64, col*64 + 64, row*64 + 64))

def dither_poly(im, pts, col, phase=0):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    px = m.load(); ip = im.load()
    x0 = max(0, int(min(p[0] for p in pts))); x1 = min(im.width, int(max(p[0] for p in pts)) + 1)
    y0 = max(0, int(min(p[1] for p in pts))); y1 = min(im.height, int(max(p[1] for p in pts)) + 1)
    for y in range(y0, y1):
        for x in range(x0, x1):
            if px[x, y] and (x + y + phase) % 2 == 0: ip[x, y] = col + (255,)

def cone(x, y, ang, span, R, n=18):
    return [(x, y)] + [(x + math.cos(ang - span/2 + span*k/n)*R, y + math.sin(ang - span/2 + span*k/n)*R) for k in range(n+1)]

def _lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def panel(d, x, y, w, h, edge=EDGE):
    """Bevelled pixel frame: drop shadow, gradient fill, light top-left bevel, dark bottom-right, rivets, optional accent."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    accent = edge if edge != EDGE else None
    d.rectangle((x + 2, y + 2, x + w + 1, y + h + 1), fill=(4, 5, 5))
    for i in range(h - 2):
        d.line([(x + 1, y + 1 + i), (x + w - 2, y + 1 + i)], fill=_lerp((30, 35, 31), (15, 18, 16), i / max(1, h - 3)))
    # outer line without corner pixels (rounded look)
    o = (6, 8, 7)
    d.line([(x + 1, y), (x + w - 2, y)], fill=o); d.line([(x + 1, y + h - 1), (x + w - 2, y + h - 1)], fill=o)
    d.line([(x, y + 1), (x, y + h - 2)], fill=o); d.line([(x + w - 1, y + 1), (x + w - 1, y + h - 2)], fill=o)
    hi = accent or (92, 98, 78); lo = (10, 12, 11)
    d.line([(x + 1, y + 1), (x + w - 2, y + 1)], fill=hi); d.line([(x + 1, y + 1), (x + 1, y + h - 2)], fill=_lerp(hi, (20, 24, 21), 0.45))
    d.line([(x + 2, y + h - 2), (x + w - 2, y + h - 2)], fill=lo); d.line([(x + w - 2, y + 2), (x + w - 2, y + h - 2)], fill=lo)
    d.line([(x + 2, y + 2), (x + w - 3, y + 2)], fill=_lerp(hi, (30, 35, 31), 0.7))
    if accent:
        d.line([(x, y + 1), (x, y + h - 2)], fill=accent); d.line([(x + w - 1, y + 1), (x + w - 1, y + h - 2)], fill=accent)
        d.line([(x + 1, y), (x + w - 2, y)], fill=accent); d.line([(x + 1, y + h - 1), (x + w - 2, y + h - 1)], fill=accent)
    if w > 60 and h > 40:
        for cx, cy in ((x + 4, y + 4), (x + w - 6, y + 4), (x + 4, y + h - 6), (x + w - 6, y + h - 6)):
            d.rectangle((cx, cy, cx + 1, cy + 1), fill=(120, 106, 70)); d.point((cx, cy), fill=(206, 186, 128))

def tape(d, x, y, w, h=11, col=(184, 162, 106)):
    d.rectangle((x, y, x + w, y + h), fill=col)
    d.line([(x, y), (x + w, y)], fill=_lerp(col, (255, 255, 255), 0.35)); d.line([(x, y + h), (x + w, y + h)], fill=_lerp(col, (0, 0, 0), 0.4))
    for k in range(0, h + 1, 2): d.point((x - 1, y + k), fill=col); d.point((x + w + 1, y + k + 1), fill=col)

def keycap(d, x, y, w=12):
    d.rectangle((x, y, x + w, y + 12), fill=(30, 28, 24)); d.rectangle((x + 1, y + 1, x + w - 1, y + 11), fill=(130, 122, 104))
    d.rectangle((x + 1, y + 1, x + w - 1, y + 9), fill=(226, 218, 196)); d.line([(x + 2, y + 1), (x + w - 2, y + 1)], fill=(252, 248, 236))

def bottom_fade(im, y0, y1=None):
    import numpy as np
    y1 = y1 or im.height
    A = np.array(im).astype(np.float32)
    t = np.clip((np.arange(im.height) - y0) / max(1, (y1 - y0) * 0.55), 0, 1)[:, None, None] * 0.88
    A[..., :3] = A[..., :3] * (1 - t) + np.array([6, 9, 8]) * t
    im.paste(Image.fromarray(A.clip(0, 255).astype(np.uint8)))

CHIBI = False
def build():
    rng = random.Random(11)
    img, water, dirt, grass = base_map()
    by = int(path_y(13) * TS)  # bridge y (centre of path)
    rx = int(river_x(by / TS) * TS)
    # wooden bridge: draw planks across the river
    d = ImageDraw.Draw(img)
    bx0, bx1 = rx - 78, rx + 78; bt, bb = by - 26, by + 26
    d.rectangle((bx0, bb + 2, bx1, bb + 8), fill=(10, 30, 40, 255))  # shadow on water
    for x in range(bx0, bx1, 8):
        c = [(122, 90, 56), (108, 80, 50), (134, 100, 64)][(x // 8) % 3]
        d.rectangle((x, bt, x + 6, bb), fill=c + (255,)); d.line([(x + 7, bt), (x + 7, bb)], fill=(58, 40, 26, 255))
        d.point((x + 2, bt + 3), fill=(70, 50, 32, 255)); d.point((x + 3, bb - 4), fill=(70, 50, 32, 255))
    for yy in (bt - 4, bb + 1):
        d.rectangle((bx0 - 2, yy, bx1 + 2, yy + 3), fill=(84, 60, 38, 255)); d.line([(bx0 - 2, yy), (bx1 + 2, yy)], fill=(150, 112, 72, 255))
        for x in range(bx0, bx1 + 1, 39): d.rectangle((x - 2, yy - 4, x + 2, yy + 4), fill=(60, 42, 28, 255))
    objs = []
    def occupied(x, y, r=40):
        tx, ty = int(x // TS), int(y // TS)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                xx, yy = tx + dx, ty + dy
                if 0 <= xx < MW and 0 <= yy < MH and (water[yy][xx] or dirt[yy][xx]): return True
        return False
    # positions
    squad = {'Dương': (bx1 + 30, by + 2), 'Hùng': (bx1 + 78, by + 30), 'Ny': (bx1 + 118, by + 58), 'Sơn': (bx1 + 60, by + 84)}
    enemy1 = (bx0 - 24, by - 4); enemy2 = (160, int(path_y(5) * TS) - 6)
    camp = (bx1 + 190, by + 120)
    keep = list(squad.values()) + [enemy1, enemy2, camp, (40, int(path_y(1) * TS))]
    # trees
    tries = 0; placed = []
    while tries < 4000 and len(placed) < 70:
        tries += 1
        x, y = rng.uniform(-20, W + 20), rng.uniform(OFFY - 10, OFFY + H + 60)
        if occupied(x, y): continue
        if any(math.hypot(x - kx, y - ky) < 85 for kx, ky in keep): continue
        zones = [(bx0 - 120, by - 150, bx1 + 30, by + 60), (bx1 - 10, by - 110, bx1 + 200, by + 130), (camp[0] - 90, camp[1] - 120, camp[0] + 90, camp[1] + 40)]
        if any(z[0] < x < z[2] and z[1] < y < z[3] + 150 for z in zones) and y > by - 150 and any(z[0] - 40 < x < z[2] + 40 and y - 160 < z[3] and y > z[1] for z in zones): continue
        if any(math.hypot(x - px, (y - py) * 1.4) < 58 for px, py in placed): continue
        placed.append((x, y))
        t = rng.choice(TREES if rng.random() < 0.75 else SMALLTREES)
        objs.append((y, t, int(x - t.width / 2), int(y - t.height + 6)))
    for _ in range(40):
        x, y = rng.uniform(0, W), rng.uniform(OFFY, OFFY + H)
        if occupied(x, y): continue
        if any(math.hypot(x - kx, y - ky) < 70 for kx, ky in keep[:6]): continue
        b = rng.choice(BUSHES); objs.append((y, b, int(x - b.width / 2), int(y - b.height + 4)))
    # cover bushes in front of the squad
    for (cx_, cy_) in ((bx1 - 5, by + 160), (bx1 + 175, by + 18)):
        b = BUSHES[1]; objs.append((cy_, b, int(cx_ - b.width / 2), int(cy_ - b.height + 4)))
    # campsite: tent + fire + log
    fire = Image.new('RGBA', (40, 26), (0, 0, 0, 0)); fd = ImageDraw.Draw(fire)
    for k in range(9):
        a_ = k / 9 * math.tau; fd.ellipse((20 + math.cos(a_) * 14 - 3, 13 + math.sin(a_) * 8 - 2, 20 + math.cos(a_) * 14 + 3, 13 + math.sin(a_) * 8 + 2), fill=(110, 106, 96, 255), outline=(60, 58, 52, 255))
    fd.line([(12, 15), (28, 11)], fill=(60, 40, 24, 255), width=2); fd.line([(13, 10), (27, 16)], fill=(70, 48, 28, 255), width=2)
    fd.point((20, 13), fill=(240, 120, 60, 255)); fd.point((19, 12), fill=(255, 190, 90, 255))
    objs.append((camp[1], fire, camp[0] - 20, camp[1] - 20))
    logs = comp_at(OUT, 420, 470)
    objs.append((camp[1] + 24, logs, camp[0] - 64, camp[1] + 24 - logs.height))
    mat = Image.new('RGBA', (40, 16), (0, 0, 0, 0)); ImageDraw.Draw(mat).rectangle((0, 0, 39, 15), fill=(94, 122, 134, 255), outline=(50, 66, 74, 255))
    objs.append((camp[1] - 30, mat, camp[0] + 26, camp[1] - 40))
    # characters
    cones = [(enemy1, math.radians(160), math.radians(56), 170), (enemy2, math.radians(10), math.radians(56), 140)]
    for (ex, ey), a, sp, R in cones:
        dither_poly(img, cone(ex, ey - 10, a, sp, R), (200, 70, 50))
        dither_poly(img, cone(ex, ey - 10, a, sp, R * 0.5), (240, 110, 80), 1)
        ImageDraw.Draw(img).line(cone(ex, ey - 10, a, sp, R)[1:], fill=(240, 110, 80, 255))
    # ghost cone (next facing, toward the bridge)
    gp = cone(enemy1[0], enemy1[1] - 10, math.radians(5), math.radians(56), 170)
    d = ImageDraw.Draw(img)
    for i, p in enumerate(gp[1:]):
        if i % 2 == 0: d.point(p, fill=GOLD + (255,))
    sx, sy = squad['Dương']
    # selection ring + waypoint
    d.ellipse((sx - 14, sy - 6, sx + 14, sy + 6), outline=TEAL + (255,))
    for k in range(12):
        if k % 2 == 0:
            t = k / 11; d.point((sx + (bx1 - 10 - sx) * t, sy + (by - sy) * t), fill=TEAL + (255,))
    d.line([(bx1 - 14, by - 4), (bx1 - 6, by + 4)], fill=TEAL + (255,)); d.line([(bx1 - 6, by - 4), (bx1 - 14, by + 4)], fill=TEAL + (255,))
    if CHIBI:
        import chibi
        for n, (x, y) in squad.items():
            sp = chibi.sprite(n, 'side', 1 if n == 'Dương' else 0); objs.append((y, sp, x - sp.width // 2, y - sp.height + 2))
        for (x, y), flip in ((enemy1, False), (enemy2, True)):
            sp = chibi.sprite('Biến Thể', 'side', 0)
            if flip: sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
            objs.append((y, sp, x - sp.width // 2, y - sp.height + 2))
    else:
        for n, (x, y) in squad.items():
            fr = frame(n, 'walk', 1, 1) if n == 'Dương' else frame(n, 'sit', 1, 0)
            objs.append((y, fr, x - 32, y - 60))
        for (x, y), row in ((enemy1, 1), (enemy2, 3)):
            objs.append((y, frame('Biến Thể', 'walk', row, 0), x - 32, y - 60))
    # glowing Mai at the far end of the trail
    mx, my = 30, int(path_y(1) * TS) + 4
    glow = Image.new('RGBA', (90, 90), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for r in range(40, 0, -4): gd.ellipse((45 - r, 45 - r, 45 + r, 45 + r), fill=(63, 217, 180, int(70 * (1 - r / 40)) + 8))
    img.alpha_composite(glow, (mx - 45, my - 70))
    ghost = frame('Ny', 'idle', 3, 0)
    if CHIBI:
        import chibi; g2 = chibi.sprite('Ny', 'front', 0); ghost = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); ghost.alpha_composite(g2, (32 - g2.width // 2, 62 - g2.height))
    gpx = ghost.load()
    for yy in range(64):
        for xx in range(64):
            r, g, b, a = gpx[xx, yy]
            if a: gpx[xx, yy] = (150, 245, 220, 210)
    objs.append((my, ghost, mx - 32, my - 60))
    objs.sort(key=lambda o: o[0])
    shadow = Image.new('L', img.size, 0)
    for _, im_, x, y in objs:
        a = im_.split()[3].point(lambda v: 255 if v > 100 else 0)
        h_ = max(1, int(a.height * 0.45))
        sq = a.resize((a.width, h_), Image.NEAREST)
        sh = sq.transform((a.width + h_, h_), Image.AFFINE, (1, 0.9, -h_ * 0.9, 0, 1, 0), Image.NEAREST)
        shadow.paste(255, (x - h_ + 6, y + a.height - h_ - 2), sh)
    import numpy as np
    A = np.array(img).astype(np.float32); S = (np.array(shadow) > 0)[..., None]
    A[..., :3] = np.where(S, A[..., :3] * np.array([0.52, 0.56, 0.68]), A[..., :3])
    img = Image.fromarray(A.clip(0, 255).astype(np.uint8))
    for _, im_, x, y in objs: img.alpha_composite(im_, (x, y))
    # spores + dawn fog (dithered)
    px = img.load()
    for _ in range(70):
        cx, cy = rng.choice([enemy1, enemy2]) if rng.random() < 0.6 else (rng.uniform(0, W), rng.uniform(OFFY, OFFY + H))
        x, y = int(cx + rng.gauss(0, 50)), int(cy - 30 + rng.gauss(0, 30))
        if 1 <= x < W - 1 and 1 <= y < img.height - 1:
            px[x, y] = (255, 156, 114, 255)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if rng.random() < 0.6: px[x + dx, y + dy] = (232, 85, 61, 255)
    for y in range(img.height):
        t = max(0.0, 0.18 - (y - OFFY) / 500)
        for x in range(W):
            if t > 0 and ((x * 7 + y * 13) % 16) / 16 < t and (x + y) % 2 == 0:
                r, g, b, a = px[x, y]; px[x, y] = (int(r * 0.5 + 200 * 0.5), int(g * 0.5 + 210 * 0.5), int(b * 0.5 + 205 * 0.5), 255)
    out = img.crop((0, OFFY, W, OFFY + H))
    return out, squad, (enemy1[0], enemy1[1] - OFFY)

TEXTS = []
class W_:
    def __init__(self, d): self._d = d
    def text(self, xy, s, font=None, fill=None): TEXTS.append((xy, s, font, fill))
    def __getattr__(self, k): return getattr(self._d, k)

FB = '/home/claude/fonts/BeVietnamPro-'
HF = {}
def hfont(f):
    key = {id(F9): ('Medium', 19), id(F9B): ('Bold', 19), id(F13): ('Bold', 27), id(F8): ('SemiBold', 15)}[id(f)]
    if key not in HF: HF[key] = ImageFont.truetype(FB + key[0] + '.ttf', key[1])
    return HF[key]

def draw_texts(big, k=2):
    d = ImageDraw.Draw(big)
    for (x, y), s, f, fill in TEXTS:
        hf = hfont(f)
        X, Y = x * k, y * k - (5 if f is F13 else 3)
        d.text((X + 1, Y + 2), s, font=hf, fill=(0, 0, 0, 160))
        d.text((X, Y), s, font=hf, fill=fill)
    TEXTS.clear()
    return big

def hud(im, squad, e1):
    d = W_(ImageDraw.Draw(im))
    panel(d, 8, 8, 176, 80)
    tape(d, 12, 11, 62); d.text((15, 11), 'Màn 1 · Hồi I', font=F8, fill=(28, 22, 12))
    d.text((14, 25), 'ĐƯỜNG MÒN SƯƠNG', font=F13, fill=INK)
    for i, (s, col) in enumerate([('Thoát khỏi vòng lặp đường mòn', INK), ('Đi theo ánh sáng xanh qua cầu', INK), ('Phụ: Đá khắc ký hiệu 1/3', DIM), ('Mảnh Ký Ức 0/2', DIM)]):
        yy = 44 + i * 10; d.rectangle((14, yy + 2, 19, yy + 7), fill=(10, 12, 11), outline=BRASS); d.text((24, yy), s, font=F9, fill=col)
    # tooltip
    ex, ey = e1
    tx, ty = int(ex - 40), int(ey - 112)
    panel(d, tx, ty, 132, 32, edge=(122, 58, 46))
    d.line([(ex, ey - 62), (ex, ty + 32)], fill=RED)
    d.arc((tx + 5, ty + 6, tx + 24, ty + 25), 0, 360, fill=(58, 42, 36), width=2)
    d.arc((tx + 5, ty + 6, tx + 24, ty + 25), -90, 180, fill=GOLD, width=2)
    d.text((tx + 9, ty + 10), '4s', font=F9B, fill=GOLD)
    d.text((tx + 30, ty + 4), 'Kẻ Lang Thang', font=F9, fill=(240, 160, 144))
    d.text((tx + 30, ty + 17), 'sắp quay sang cầu', font=F9, fill=INK)
    # minimap
    mx, my, mw, mh = W - 104, 8, 96, 70
    panel(d, mx, my, mw, mh)
    d.rectangle((mx + 3, my + 3, mx + mw - 4, my + 54), fill=(24, 52, 38))
    sx_, sy_ = (mw - 8) / W, 50 / H
    d.line([(mx + 4 + river_x(y / 10) * TS * sx_, my + 4 + (y / 10 * TS - OFFY) * sy_) for y in range(0, 150, 5) if 0 <= (y / 10 * TS - OFFY) <= H], fill=(40, 100, 140), width=3)
    d.line([(mx + 4 + x / 10 * TS * sx_, my + 4 + (path_y(x / 10) * TS - OFFY) * sy_) for x in range(0, 251, 10)], fill=(130, 98, 62), width=2)
    for n, (x, y) in squad.items(): d.rectangle((mx + 4 + x * sx_, my + 4 + (y - OFFY) * sy_, mx + 5 + x * sx_, my + 5 + (y - OFFY) * sy_), fill=TEAM[n])
    d.rectangle((mx + 3 + ex * sx_, my + 3 + ey * sy_, mx + 5 + ex * sx_, my + 5 + ey * sy_), fill=RED)
    d.text((mx + 5, my + 57), '05:42 · Sương dày', font=F9, fill=DIM)
    # bottom bar
    by = H - 50
    bottom_fade(im, by - 40); d = W_(ImageDraw.Draw(im))
    hp = {'Dương': .86, 'Hùng': 1, 'Ny': .72, 'Sơn': .9}
    for i, n in enumerate(TEAM):
        x0 = 8 + i * 42; sel = n == 'Dương'
        panel(d, x0, by - 2, 38, 48, edge=TEAL if sel else EDGE)
        r, g, b = TEAM[n]; d.rectangle((x0 + 3, by + 1, x0 + 34, by + 30), fill=(r // 3, g // 3, b // 3))
        face = frame(n, 'idle', 2, 0).crop((16, 6, 48, 36))
        im.alpha_composite(face, (x0 + 3, by + 1)); d = W_(ImageDraw.Draw(im))
        if sel: d.rectangle((x0, by - 2, x0 + 37, by + 45), outline=TEAL)
        d.rectangle((x0 + 3, by + 31, x0 + 34, by + 33), fill=(26, 28, 22)); d.rectangle((x0 + 3, by + 31, x0 + 3 + int(31 * hp[n]), by + 33), fill=TEAM[n])
        d.text((x0 + 4, by + 35), n, font=F8, fill=INK); keycap(d, x0 + 24, by + 2, 11); d.text((x0 + 27, by + 2), str(i + 1), font=F8, fill=(30, 28, 24))
    sx0 = 196
    d.text((sx0, by - 3), 'Dương · ngồi thấp, bước chân im', font=F9, fill=DIM)
    labels = [('Leo', 'Q'), ('Hạ', 'W'), ('Ném', 'E'), ('Bản đồ', 'R')]
    for i, (lab, k) in enumerate(labels):
        x0 = sx0 + i * 46; panel(d, x0, by + 10, 42, 34)
        c = INK; X, Y = x0 + 6, by + 13
        if i == 0:
            d.line([(X + 3, Y + 1), (X + 3, Y + 14)], fill=c); d.line([(X + 11, Y + 1), (X + 11, Y + 14)], fill=c)
            for yy in (4, 8, 12): d.line([(X + 3, Y + yy), (X + 11, Y + yy)], fill=c)
        elif i == 1:
            d.line([(X + 2, Y + 13), (X + 10, Y + 5)], fill=c); d.line([(X + 10, Y + 5), (X + 13, Y + 1)], fill=c); d.rectangle((X + 1, Y + 12, X + 3, Y + 14), fill=c)
        elif i == 2:
            for kk in range(11): d.point((X + 1 + kk, Y + 13 - int(10 * math.sin(kk / 10 * math.pi * 0.8))), fill=c)
            d.ellipse((X + 11, Y + 2, X + 14, Y + 5), outline=c)
        else:
            d.line([(X + 1, Y + 3), (X + 5, Y + 1), (X + 9, Y + 3), (X + 13, Y + 1), (X + 13, Y + 12), (X + 9, Y + 14), (X + 5, Y + 12), (X + 1, Y + 14), (X + 1, Y + 3)], fill=c)
        keycap(d, x0 + 27, by + 13); d.text((x0 + 30, by + 13), k, font=F8, fill=(30, 28, 24)); d.text((x0 + 5, by + 31), lab, font=F9, fill=INK)
    ix0 = W - 134
    d.text((ix0, by - 3), 'Ba lô', font=F9, fill=DIM)
    for i in range(4):
        x0 = ix0 + i * 32; panel(d, x0, by + 10, 29, 29)
        if i == 0: d.ellipse((x0 + 8, by + 16, x0 + 19, by + 27), fill=(138, 142, 130)); d.text((x0 + 20, by + 27), '3', font=F9B, fill=INK)
        if i == 1: d.ellipse((x0 + 7, by + 15, x0 + 20, by + 28), fill=(184, 176, 160)); d.ellipse((x0 + 11, by + 19, x0 + 16, by + 24), fill=PANEL); d.text((x0 + 20, by + 27), '2', font=F9B, fill=INK)
    return im


def postfx(im, glows=()):
    """'256-bit' pass: split-toned dawn grading, posterised god rays, bloom, haze and vignette — all at native pixel resolution."""
    import numpy as np
    from PIL import ImageFilter
    A = np.array(im.convert('RGB')).astype(np.float32) / 255.0
    Hh, Ww = A.shape[:2]
    yy, xx = np.mgrid[0:Hh, 0:Ww].astype(np.float32)
    lum = (A @ np.array([0.299, 0.587, 0.114], dtype=np.float32))[..., None]
    # split toning: cool teal shadows, warm amber highlights
    shadow_tint = np.array([0.80, 0.95, 1.10]); high_tint = np.array([1.12, 1.00, 0.82])
    t = np.clip((lum - 0.25) / 0.5, 0, 1)
    A = A * (shadow_tint * (1 - t) + high_tint * t) * 1.08
    # contrast curve
    A = np.clip((A - 0.5) * 1.12 + 0.5, 0, 1)
    # god rays from the top-right (posterised to 4 levels, ordered dither)
    ang = math.radians(118); dx, dy = math.cos(ang), math.sin(ang)
    u = (xx - Ww) * (-dy) + yy * dx  # distance across the ray direction
    rays = (np.sin(u / 23.0) * 0.5 + 0.5) ** 6 + (np.sin(u / 9.0 + 1.7) * 0.5 + 0.5) ** 10 * 0.5
    fall = np.clip(1.1 - (yy / Hh) * 1.0 - ((Ww - xx) / Ww) * 0.45, 0, 1)
    R = rays * fall * 0.55
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) / 16.0
    B = bayer[(yy % 4).astype(int), (xx % 4).astype(int)]
    Rq = np.floor(R * 4 + B) / 4.0
    A = A + Rq[..., None] * np.array([1.0, 0.80, 0.50]) * 0.42
    # haze toward the top of the frame
    hz = np.clip(0.20 - yy / Hh * 0.45, 0, 1)[..., None]
    hzq = np.floor(hz * 6 + B[..., None]) / 6.0
    A = A * (1 - hzq) + np.array([0.80, 0.84, 0.82]) * hzq
    # bloom on bright/saturated pixels (spores, glow, highlights)
    img8 = Image.fromarray((np.clip(A, 0, 1) * 255).astype(np.uint8))
    bright = img8.point(lambda v: 255 if v > 215 else 0)
    bl = np.array(bright.filter(ImageFilter.GaussianBlur(4))).astype(np.float32) / 255.0
    A = A + np.floor(bl * 3) / 3 * 0.18
    for (gx, gy, gr, col) in glows:
        d = np.sqrt((xx - gx) ** 2 + (yy - gy) ** 2)
        g = np.clip(1 - d / gr, 0, 1) ** 2
        A = A + (np.floor(g * 5 + B) / 5)[..., None] * np.array(col) * 0.45
    # vignette
    vx = (xx / Ww - 0.5) * 2; vy = (yy / Hh - 0.55) * 2
    v = np.clip(1.05 - (vx ** 2 * 0.25 + vy ** 2 * 0.3), 0.72, 1)
    vq = np.floor(v * 10 + B) / 10
    A = A * vq[..., None]
    return Image.fromarray((np.clip(A, 0, 1) * 255).astype(np.uint8)).convert('RGBA')


if __name__ == '__main__':
    im, squad, e1 = build()
    squad2 = {n: (x, y) for n, (x, y) in squad.items()}
    im = postfx(im, glows=[(30, int(path_y(1) * TS) - OFFY - 30, 70, (0.25, 0.85, 0.7))])
    im = hud(im, squad2, e1)
    big = draw_texts(im.resize((1600, 900), Image.NEAREST))
    big.save('/home/claude/gen/lpc_out/frame_x2.png')
    print('ok')
