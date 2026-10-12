import sys, math, random; sys.path.insert(0, '.')
import numpy as np
from PIL import Image, ImageDraw
import lpc, npcs
Z = lambda col: ('head/heads/undead/heads_zombie.json', col, 'body')
lpc.CHARS.update({
    'Kẻ Thính': ('male', [('body/body.json', 'zombie', 'body'), Z('zombie'), ('legs/pants/legs_pants.json', 'gray', 'cloth'),
                          ('torso/torso_bandages.json', 'white', None), ('headwear/accessories/eyepatch/facial_eyepatch_ambi.json', 'white', None)]),
    'Kẻ Phun': ('pregnant', [('body/body.json', 'zombie_green', 'body'), Z('zombie_green'), ('legs/pants/legs_pants.json', 'brown', 'cloth')]),
    'Kẻ Bám Trần': ('teen', [('body/body.json', 'zombie', 'body'), Z('zombie'), ('legs/pants/legs_pants.json', 'black', 'cloth'), ('hair/long/hair_long_messy.json', 'black', 'hair')]),
    'Kẻ Mang Vỏ': ('male', [('body/body.json', 'zombie', 'body'), Z('zombie'), ('legs/pants/legs_pants.json', 'walnut', 'cloth'), ('torso/armour/torso_armour_plate.json', None, 'tint:6a5038')]),
    'Kẻ Bắt Chước': ('female', [('body/body.json', 'zombie', 'body'), Z('zombie'), ('torso/dresses/dress_slit.json', 'white', None), ('hair/long/hair_long_messy.json', 'black', 'hair')]),
})
from anim2 import fr
def post(name, f, seed=0):
    A = np.array(f).astype(np.float32)
    if name == 'Kẻ Bám Trần':
        m = A[..., 3] > 0; A[m, :3] = A[m, :3] * np.array([0.62, 0.55, 0.72])
    if name == 'Kẻ Phun':
        sk = (A[..., 3] > 0) & (A[..., 1] > A[..., 0]) & (A[..., 1] > 90)
        ys, xs = np.nonzero(sk)
        for y, x in zip(ys, xs):
            if (x * 7 + y * 13) % 23 == 0: A[y, x, :3] = (214, 60, 44)
            elif (x * 7 + y * 13) % 23 == 1: A[y, x, :3] = (255, 140, 110)
    if name == 'Kẻ Bắt Chước':
        m = A[..., 3] > 0; A[m, :3] = A[m, :3] * 0.85 + np.array([200, 205, 210]) * 0.15
    return Image.fromarray(A.clip(0, 255).astype(np.uint8))

def F(name, anim, row, col, dx=0, dy=0):
    c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(post(name, fr(name, anim, row, col)), (dx, dy)); return c
def seqz(name, anim, row, cols, dx=0): return [F(name, anim, row, c, dx) for c in cols]
from fx import spores, noise_ring, dust, sparks, fire
from knock import knockdown, lying

def kd(name):
    out = knockdown(name, zombie=True)
    return [post(name, f) for f in out]

def listen(name):
    rings = noise_ring(); out = []
    for i in range(8):
        c = F(name, 'walk', 2, 0); c.alpha_composite(rings[i], (0, -20)); out.append(c)
    return out

def spit(name):
    sp = spores(); out = []
    for i in range(8):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        c.alpha_composite(F(name, 'slash', 1, min(5, i)), (10, 0))
        if i >= 3: c.alpha_composite(sp[min(7, (i - 3) * 2)].resize((48, 48), Image.NEAREST), (-6, 6))
        out.append(c)
    return out

def bloat(name):
    out = []
    for i in range(8):
        f = post(name, fr(name, 'idle', 2, i % 2)); k = 1 + 0.06 * math.sin(i / 8 * math.tau)
        w = int(64 * k); g = f.resize((w, 64), Image.NEAREST)
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(g, ((64 - w) // 2, 0)); out.append(c)
    return out

def ceiling_crawl(name):
    out = []
    for i in range(8):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        d.rectangle((0, 0, 63, 5), fill=(70, 62, 54, 255)); d.line([(0, 5), (63, 5)], fill=(40, 34, 30, 255))
        f = post(name, fr(name, 'walk', 1, 1 + i)).transpose(Image.FLIP_TOP_BOTTOM)
        c.alpha_composite(f, (-(i % 8), -8)); out.append(c)
    return out

def drop(name):
    out = []; d0 = dust()
    for i in range(10):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        d.rectangle((0, 0, 63, 5), fill=(70, 62, 54, 255))
        if i < 4:
            f = post(name, fr(name, 'walk', 2, 0)).transpose(Image.FLIP_TOP_BOTTOM); c.alpha_composite(f, (0, -8 + i * 3))
            d.line([(32, 6), (32, 10 + i * 3)], fill=(150, 40, 30, 255))
        elif i < 6:
            f = post(name, fr(name, 'slash', 2, 2 + (i - 4))); c.alpha_composite(f, (0, (6 - i) * 6))
        else:
            c.alpha_composite(post(name, fr(name, 'slash', 2, 5)), (0, 0)); c.alpha_composite(d0[min(7, (i - 6) * 2)], (0, 4))
        out.append(c)
    return out

def charge(name):
    out = []; ds = dust()
    for i in range(8):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        c.alpha_composite(ds[(i * 2) % 8].transpose(Image.FLIP_LEFT_RIGHT), (14, 4))
        c.alpha_composite(F(name, 'run', 1, i), (2 - i, 0)); out.append(c)
    return out

def block(name):
    sp = sparks(); out = []
    for i in range(8):
        c = F(name, 'walk', 1, 0)
        if i in (1, 2, 3):
            c.alpha_composite(sp[i - 1].resize((40, 40), Image.NEAREST), (2, 8))
            d = ImageDraw.Draw(c); d.text((6, 4), 'KENG', fill=(255, 230, 120, 255))
        out.append(c)
    return out

def mimic_voice(name):
    out = []
    for i in range(8):
        c = F(name, 'idle', 2, i % 2); d = ImageDraw.Draw(c)
        for k in range(3):
            t = ((i / 8) + k / 3) % 1; r = 6 + 18 * t; a = int(255 * (1 - t))
            d.arc((32 - r, 22 - r, 32 + r, 22 + r), 200, 340, fill=(242, 193, 78, a), width=2)
        if i % 2 == 0: d.rectangle((31, 26, 33, 27), fill=(255, 220, 120, 255))
        out.append(c)
    return out

def rats(mode='run'):
    out = []; rr = random.Random(4); base = [(rr.uniform(4, 56), rr.uniform(30, 58), rr.uniform(0.7, 1.3)) for _ in range(12)]
    fl = fire()
    for i in range(8):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        if mode == 'fire': c.alpha_composite(fl[i].resize((40, 40), Image.NEAREST), (12, 20))
        for k, (x, y, sp) in enumerate(base):
            if mode == 'run': px = (x - i * 4 * sp) % 64; py = y + (1 if (i + k) % 2 else 0); dirx = -1
            else:
                ang = math.atan2(y - 44, x - 32) + 0.2; L = 4 + i * 3.5 * sp
                px = 32 + math.cos(ang) * L; py = 44 + math.sin(ang) * L * 0.6; dirx = 1 if math.cos(ang) > 0 else -1
            d.ellipse((px - 4, py - 2, px + 4, py + 2), fill=(122, 46, 36, 255), outline=(50, 18, 14, 255))
            hx = px + 5 * dirx; d.ellipse((hx - 2, py - 2, hx + 2, py + 1), fill=(150, 60, 46, 255))
            d.point((hx + dirx, py - 1), fill=(255, 140, 110, 255))
            tail = [(px - 4 * dirx, py), (px - 8 * dirx, py + (1 if (i + k) % 2 else -1))]; d.line(tail, fill=(90, 30, 24, 255))
        out.append(c)
    return out

def get_rows():
  return [
    ('Kẻ Thính', 'Mù, nghe cực nhạy · màn 3', [('Lê bước', seqz('Kẻ Thính', 'walk', 2, range(1, 9))), ('Nghe ngóng', listen('Kẻ Thính')), ('Bò sát đất', None), ('Bị hạ', kd('Kẻ Thính'))]),
    ('Kẻ Phun', 'Phun mây bào tử · màn 4', [('Lê bước', seqz('Kẻ Phun', 'walk', 2, range(1, 9))), ('Phình bụng', bloat('Kẻ Phun')), ('Phun bào tử', spit('Kẻ Phun')), ('Bị hạ', kd('Kẻ Phun'))]),
    ('Kẻ Bám Trần', 'Bò trên trần, rơi xuống tóm · màn 6', [('Lê bước', seqz('Kẻ Bám Trần', 'walk', 2, range(1, 9))), ('Bò trên trần', ceiling_crawl('Kẻ Bám Trần')), ('Rơi xuống tóm', drop('Kẻ Bám Trần')), ('Bị hạ', kd('Kẻ Bám Trần'))]),
    ('Kẻ Mang Vỏ', 'Vỏ cứng, miễn cận chiến · màn 7', [('Lê bước', seqz('Kẻ Mang Vỏ', 'walk', 2, range(1, 9))), ('Húc tới', charge('Kẻ Mang Vỏ')), ('Đỡ đòn', block('Kẻ Mang Vỏ')), ('Bị hạ', kd('Kẻ Mang Vỏ'))]),
    ('Kẻ Bắt Chước', 'Giả giọng người thân · màn 8', [('Lê bước', seqz('Kẻ Bắt Chước', 'walk', 2, range(1, 9))), ('Giả giọng', mimic_voice('Kẻ Bắt Chước')), ('Lao tới', seqz('Kẻ Bắt Chước', 'walk', 1, range(1, 9))), ('Bị hạ', kd('Kẻ Bắt Chước'))]),
    ('Bầy Chuột Đỏ', 'Đi thành đàn theo cống · màn 5', [('Chạy theo đàn', rats('run')), ('Tản ra', rats('scatter')), ('Sợ lửa', rats('fire')), ('Chạy theo đàn', rats('run'))]),
]
if __name__ == '__main__':
    ROWS = get_rows()
    import crawl
    crawl.COL['Kẻ Thính'] = dict(top=(226, 222, 210), sleeve=(160, 170, 150), skin=(160, 170, 150), pants=(120, 120, 124), shoes=(110, 100, 92))
    ROWS[0][2][2] = ('Bò sát đất', crawl.crawl('Kẻ Thính'))
    ROWS[5][2][3] = ('Bị lửa đốt', rats('fire'))
    flat = [(n, lab, fs) for n, role, items in ROWS for lab, fs in items]
    Wd = 64 * max(len(fs) for _, _, fs in flat)
    sh = Image.new('RGBA', (Wd, 64 * len(flat)), (0, 0, 0, 0))
    for i, (_, _, fs) in enumerate(flat):
        for j, f in enumerate(fs): sh.alpha_composite(f, (j * 64, i * 64))
    sh.save('/mnt/user-data/outputs/artifacts/c82b9169-ee10-4565-aca3-4592040c933d/zombies_sheet.png', optimize=True)
    import json
    json.dump({'w': Wd, 'h': sh.height, 'rows': [(n, role) for n, role, _ in ROWS], 'meta': [(n, lab, len(fs)) for n, lab, fs in flat]}, open('zombies_meta.json', 'w'), ensure_ascii=False)
    bg = Image.new('RGBA', sh.size, (50, 66, 52, 255)); bg.alpha_composite(sh); bg.save('/tmp/zsheet.png'); print(sh.size)
