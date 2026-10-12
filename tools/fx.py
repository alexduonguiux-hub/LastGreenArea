import math, random
import numpy as np
from PIL import Image, ImageDraw

S = 64
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) / 16.0
YY, XX = np.mgrid[0:S, 0:S].astype(np.float32)
B = BAYER[(YY % 4).astype(int), (XX % 4).astype(int)]

def ramp_img(v, ramp, alpha_cut=0.16):
    """v: 0..1 field -> posterised palette image with ordered dither (pixel-art look)."""
    n = len(ramp)
    q = np.clip(np.floor(v * n + B - 0.5), -1, n - 1).astype(int)
    out = np.zeros((S, S, 4), np.uint8)
    for i, c in enumerate(ramp):
        out[q == i] = c + (255,)
    out[v < alpha_cut] = 0
    return Image.fromarray(out)

def noise(seed, scale=8):
    r = np.random.RandomState(seed); g = r.rand(S // scale + 2, S // scale + 2)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((S + 2 * scale, S + 2 * scale), Image.BICUBIC)
    return np.array(im).astype(np.float32)[:S, :S] / 255

FIRE = [(90, 20, 14), (178, 40, 22), (232, 92, 30), (252, 160, 50), (255, 226, 120), (255, 250, 214)]
SMOKE = [(40, 40, 44), (70, 70, 76), (110, 110, 116), (150, 150, 156)]
SPORE = [(90, 24, 24), (168, 44, 36), (232, 85, 61), (255, 150, 120)]
WATER = [(30, 80, 120), (70, 140, 190), (150, 210, 235), (235, 250, 255)]
TEAL = [(20, 90, 80), (40, 170, 140), (63, 217, 180), (190, 255, 236)]
GOLD = [(120, 80, 20), (200, 150, 40), (242, 193, 78), (255, 240, 180)]

def fire(n=8):
    out = []
    for i in range(n):
        nz = noise(10 + i, 6) * 0.6 + noise(40 + i * 3, 3) * 0.4
        h = np.clip((YY - 12) / 46, 0, 1)                     # hotter at the bottom
        w = np.clip(1 - np.abs(XX - 32 - 3 * math.sin(i)) / (6 + 16 * h), 0, 1)
        v = np.clip(w * (h * 1.15) - (nz - 0.5) * 0.55 - (1 - h) * 0.2, 0, 1)
        im = ramp_img(v, FIRE, 0.12)
        d = ImageDraw.Draw(im)
        for k in range(10): d.line([(24 + 2 * k - (k % 3), 58), (30 + k % 5, 54)], fill=(60, 40, 24, 255), width=2) if k < 3 else None
        r = random.Random(i)
        for _ in range(3): d.point((r.randint(20, 44), r.randint(4, 24)), fill=(255, 210, 120, 255))
        out.append(im)
    return out

def explosion(n=10):
    out = []
    for i in range(n):
        t = i / (n - 1); r = 6 + 26 * math.sqrt(t)
        dd = np.sqrt((XX - 32) ** 2 + (YY - 34) ** 2)
        nz = noise(70 + i, 5)
        core = np.clip(1 - dd / r, 0, 1) * (1.4 - 1.2 * t) + (nz - 0.5) * 0.35
        if t < 0.6: im = ramp_img(np.clip(core, 0, 1), FIRE, 0.1)
        else:
            sm = np.clip(1 - dd / r, 0, 1) * (1.3 - t) + (nz - 0.5) * 0.4
            im = ramp_img(np.clip(sm, 0, 1), SMOKE, 0.12)
            fl = ramp_img(np.clip(core - 0.3, 0, 1), FIRE[:4], 0.15); im.alpha_composite(fl)
        d = ImageDraw.Draw(im); rr = random.Random(5)
        for k in range(10):
            a = rr.uniform(0, math.tau); L = 6 + 30 * t * rr.uniform(0.6, 1.1)
            x, y = 32 + math.cos(a) * L, 34 + math.sin(a) * L * 0.8
            if t > 0.1: d.rectangle((x, y, x + 1, y + 1), fill=(255, 200, 90, 255) if t < 0.6 else (90, 80, 70, 255))
        if i == 0: d.ellipse((22, 24, 42, 44), fill=(255, 250, 220, 255))
        out.append(im)
    return out

def smoke(n=8):
    out = []
    for i in range(n):
        t = i / n; v = np.zeros((S, S), np.float32)
        for k, (ox, oy, rad) in enumerate([(0, 0, 9), (6, -4, 7), (-6, -3, 7), (2, -10, 6)]):
            cy = 46 - 22 * t + oy; cx = 32 + ox + 4 * math.sin(t * 3 + k)
            v = np.maximum(v, np.clip(1 - np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2) / (rad * (1 + t)), 0, 1))
        v = np.clip(v * (1.1 - t * 0.9) + (noise(90 + i, 4) - 0.5) * 0.3, 0, 1)
        out.append(ramp_img(v, SMOKE, 0.1))
    return out

def spores(n=8):
    out = []
    rr = random.Random(3); parts = [(rr.uniform(0, math.tau), rr.uniform(0.5, 1.0), rr.randint(1, 2)) for _ in range(40)]
    for i in range(n):
        t = (i + 1) / n
        dd = np.sqrt((XX - 32) ** 2 + ((YY - 40) * 1.3) ** 2)
        v = np.clip(1 - dd / (8 + 22 * t), 0, 1) * (1.2 - t) + (noise(120 + i, 4) - 0.5) * 0.3
        im = ramp_img(np.clip(v, 0, 1), SPORE, 0.12); d = ImageDraw.Draw(im)
        for a, sp, sz in parts:
            L = 26 * t * sp; x, y = 32 + math.cos(a) * L, 40 + math.sin(a) * L * 0.7 - 10 * t
            d.rectangle((x, y, x + sz, y + sz), fill=(255, 140, 110, 255))
        out.append(im)
    return out

def sparks(n=8):
    out = []
    for i in range(n):
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); r = random.Random(200 + i)
        if i % 3 != 2:
            x, y = 32, 30; pts = [(x, y)]
            for k in range(5): x += r.randint(-5, 5); y += r.randint(-6, 6); pts.append((x, y))
            d.line(pts, fill=(170, 230, 255, 255), width=2); d.line(pts, fill=(255, 255, 255, 255), width=1)
            for _ in range(8):
                a = r.uniform(0, math.tau); L = r.uniform(4, 16)
                d.point((32 + math.cos(a) * L, 30 + math.sin(a) * L), fill=(255, 230, 120, 255))
            d.ellipse((28, 26, 36, 34), fill=(255, 255, 240, 255))
        else:
            for _ in range(4): d.point((32 + r.randint(-10, 10), 30 + r.randint(0, 14)), fill=(255, 200, 90, 255))
        out.append(im)
    return out

def splash(n=8):
    out = []
    for i in range(n):
        t = i / (n - 1); im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        rx = 6 + 22 * t; d.ellipse((32 - rx, 50 - rx * 0.3, 32 + rx, 50 + rx * 0.3), outline=WATER[2] + (255,), width=2 if t < 0.7 else 1)
        if t < 0.8:
            r = random.Random(9)
            for k in range(9):
                a = math.pi + k / 8 * math.pi; L = 4 + 16 * math.sin(t * math.pi) * r.uniform(0.7, 1.1)
                x = 32 + math.cos(a) * L * 1.2; y = 48 + math.sin(a) * L * 1.4 + 14 * t * t
                d.rectangle((x, y, x + 1, y + 2), fill=WATER[3] + (255,))
            col_h = 18 * math.sin(t * math.pi)
            d.rectangle((30, 48 - col_h, 33, 48), fill=WATER[1] + (255,)); d.rectangle((31, 48 - col_h, 32, 48 - col_h + 3), fill=WATER[3] + (255,))
        out.append(im)
    return out

def noise_ring(n=8):
    out = []
    for i in range(n):
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for k in range(3):
            t = ((i / n) + k / 3) % 1; r = 4 + 26 * t
            a = int(255 * (1 - t))
            d.ellipse((32 - r, 40 - r * 0.5, 32 + r, 40 + r * 0.5), outline=GOLD[2] + (a,), width=2)
        d.rectangle((30, 38, 33, 41), fill=(138, 142, 130, 255))
        out.append(im)
    return out

def dust(n=8):
    out = []
    rr = random.Random(11); puffs = [(rr.uniform(-1, 1), rr.uniform(0.5, 1)) for _ in range(6)]
    for i in range(n):
        t = i / (n - 1); v = np.zeros((S, S), np.float32)
        for dx, sp in puffs:
            cx = 32 + dx * 20 * t; cy = 52 - 6 * t * sp
            v = np.maximum(v, np.clip(1 - np.sqrt((XX - cx) ** 2 + ((YY - cy) * 1.6) ** 2) / (3 + 8 * t), 0, 1))
        im = ramp_img(np.clip(v * (1.2 - t), 0, 1), [(110, 96, 74), (150, 132, 100), (190, 172, 136)], 0.12)
        if i < 3: ImageDraw.Draw(im).rectangle((30, 50 - (2 - i) * 6, 33, 53 - (2 - i) * 6), fill=(138, 142, 130, 255))
        out.append(im)
    return out

def lightning(n=8):
    out = []
    for i in range(n):
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        if i in (1, 2, 4):
            d.rectangle((0, 0, S, S), fill=(200, 220, 255, 60 if i != 1 else 120))
            r = random.Random(30 + (i == 4)); x = 34; pts = [(x, 0)]
            for y in range(6, 60, 6): x += r.randint(-6, 6); pts.append((x, y))
            d.line(pts, fill=(200, 230, 255, 255), width=3); d.line(pts, fill=(255, 255, 255, 255), width=1)
            bx, by = pts[4]; d.line([(bx, by), (bx + 10, by + 12), (bx + 8, by + 20)], fill=(200, 230, 255, 255), width=1)
        out.append(im)
    return out

def heal(n=8):
    out = []
    rr = random.Random(5); ps = [(rr.uniform(12, 52), rr.uniform(0, 1), rr.choice((0, 1))) for _ in range(9)]
    for i in range(n):
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        t = i / n
        d.ellipse((14, 50, 50, 60), outline=TEAL[2] + (int(200 * (1 - t)),), width=1)
        for x, ph, kind in ps:
            y = 56 - ((t + ph) % 1) * 44
            if kind: d.line([(x - 2, y), (x + 2, y)], fill=TEAL[3] + (255,)); d.line([(x, y - 2), (x, y + 2)], fill=TEAL[3] + (255,))
            else: d.point((x, y), fill=TEAL[2] + (255,))
        out.append(im)
    return out

def scan(n=8):
    out = []
    for i in range(n):
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        t = i / n; r = 4 + 26 * t
        d.ellipse((32 - r, 44 - r * 0.45, 32 + r, 44 + r * 0.45), outline=TEAL[2] + (int(255 * (1 - t)),), width=2)
        d.ellipse((32 - 30, 44 - 13, 32 + 30, 44 + 13), outline=TEAL[0] + (255,), width=1)
        y = 16 + math.sin(i / n * math.tau) * 2
        for (a, b) in ((-7, -3), (4, -3), (-7, 3), (4, 3)): d.ellipse((32 + a, y + b, 35 + a, y + b + 2), fill=(180, 196, 204, 255))
        d.rectangle((29, y - 1, 35, y + 3), fill=(70, 96, 110, 255)); d.point((34, y + 1), fill=TEAL[3] + (255,))
        d.line([(32, y + 4), (32 - r * 0.5, 44), (32 + r * 0.5, 44), (32, y + 4)], fill=TEAL[1] + (90,))
        out.append(im)
    return out

def alert(n=8):
    out = []
    for i in range(n):
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        s = [0.4, 0.9, 1.25, 1.0, 1.0, 1.0, 1.0, 1.0][i]; y0 = 30 - [0, 4, 8, 6, 6, 6, 5, 6][i]
        w, h = 10 * s, 22 * s
        d.rectangle((32 - w / 2 - 2, y0 - h / 2 - 2, 32 + w / 2 + 2, y0 + h / 2 + 2), fill=(30, 10, 8, 255))
        d.rectangle((32 - w / 2, y0 - h / 2, 32 + w / 2, y0 + h / 2), fill=(232, 60, 44, 255) if i % 2 == 0 or i < 3 else (255, 214, 92, 255))
        if h > 12: d.rectangle((31, y0 - h / 2 + 3, 33, y0 + h / 2 - 7), fill=(255, 255, 255, 255)); d.rectangle((31, y0 + h / 2 - 5, 33, y0 + h / 2 - 3), fill=(255, 255, 255, 255))
        out.append(im)
    return out

EFFECTS = [('Lửa cháy', fire), ('Nổ', explosion), ('Khói', smoke), ('Bào tử phun', spores), ('Chập điện', sparks), ('Nước bắn', splash),
           ('Tiếng động (ném đá)', noise_ring), ('Bụi đá rơi', dust), ('Sét đánh', lightning), ('Hồi máu', heal), ('Drone quét', scan), ('Bị phát hiện', alert)]
