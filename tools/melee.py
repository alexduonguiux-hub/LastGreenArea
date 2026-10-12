"""Short knife / long machete held in the front hand. The blade is drawn as a pixel line from the hand along the
shoulder->hand direction (slash), straight forward (stab) or pointing down-forward (walk), handle behind the hand."""
import sys, math; sys.path.insert(0, '/home/claude/gen')
from PIL import Image, ImageDraw
from anim2 import fr
from knock import lying
STEEL = [(70, 78, 96), (150, 158, 176), (220, 228, 238)]; WOODC = (104, 60, 38); OUT = (16, 16, 20)
SLASH_HAND = [(30, 46), (19, 49), (21, 47), (14, 44), (11, 34), (13, 33)]
THRUST_HAND = [(29, 46), (21, 45), (21, 45), (26, 44), (19, 44), (15, 44), (19, 44), (25, 44)]
SHOULDER = (31, 38)

def blade(d, hx, hy, ux, uy, L, handle, wide):
    px, py = -uy, ux
    ex, ey = hx + ux * L, hy + uy * L; bx, by = hx - ux * handle, hy - uy * handle
    d.line([(bx, by), (hx, hy)], fill=OUT, width=4); d.line([(hx, hy), (ex, ey)], fill=OUT, width=wide + 2)
    d.line([(bx, by), (hx, hy)], fill=WOODC, width=2)
    d.line([(hx, hy), (ex, ey)], fill=STEEL[1], width=wide)
    d.line([(hx + px * (wide / 2 - 0.5), hy + py * (wide / 2 - 0.5)), (ex + px * (wide / 2 - 0.5), ey + py * (wide / 2 - 0.5))], fill=STEEL[2], width=1)
    d.line([(hx - ux * 0.5 + px * 2, hy - uy * 0.5 + py * 2), (hx - ux * 0.5 - px * 2, hy - uy * 0.5 - py * 2)], fill=(60, 60, 70), width=1)

def frame_with(f, hx, hy, ux, uy, kind, dx=8, trail=None):
    c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(f, (dx, 0)); d = ImageDraw.Draw(c)
    L, handle, wide = (6, 2, 2) if kind == 'knife' else (12, 3, 3)
    if trail:
        for k, (tx, ty) in enumerate(trail): d.point((tx + dx, ty), fill=(220, 236, 255, 160 - k * 40))
    blade(d, hx + dx, hy, ux, uy, L, handle, wide)
    return c

def norm(x, y):
    l = math.hypot(x, y) or 1; return x / l, y / l

def walk(name, kind):
    out = []
    for i in range(8):
        f = fr(name, 'walk', 1, 1 + i); bb = f.getbbox()
        hx, hy = bb[0] + 4 + (1 if i in (2, 3, 6, 7) else 0), bb[1] + 35
        out.append(frame_with(f, hx, hy, *norm(-0.35, 1), kind))
    return out

def slash(name, kind):
    """Chop: ready -> blade raised forward-up -> swing down (LPC slash frames played 0,5,4,3,2,1)."""
    out = []
    for i in (0, 5, 4, 3, 2, 1):
        hx, hy = SLASH_HAND[i]
        f = fr(name, 'slash', 1, i); ux, uy = norm(hx - SHOULDER[0], hy - SHOULDER[1])
        if i == 0: ux, uy = norm(0.2, 1)
        trail = None
        if i in (3, 2, 1):
            L = 6 if kind == 'knife' else 12
            trail = [(int(hx + ux * L - k * 2), int(hy + uy * L - k * 3)) for k in range(3)]
        out.append(frame_with(f, hx, hy, ux, uy, kind, trail=trail))
    return out

def stab(name, kind):
    out = []
    for i, (hx, hy) in enumerate(THRUST_HAND):
        f = fr(name, 'thrust', 1, i); out.append(frame_with(f, hx, hy, -1, 0.05, kind))
    return out

def takedown(name):
    out = []; L = lying('Biến Thể')
    for i in range(3):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(fr('Biến Thể', 'walk', 1, 0), (-4, 0))
        f = fr(name, 'walk', 1, 1 + i * 2); c2 = frame_with(f, f.getbbox()[0] + 4, f.getbbox()[1] + 35, *norm(-0.35, 1), 'knife', dx=10 - i * 3); c.alpha_composite(c2); out.append(c)
    for i in range(3):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(fr('Biến Thể', 'hurt', 0, min(i, 1)), (-4, 0))
        hx, hy = THRUST_HAND[4 + (i % 2)]; c.alpha_composite(frame_with(fr(name, 'thrust', 1, 4 + (i % 2)), hx, hy, -1, 0.05, 'knife', dx=6)); out.append(c)
    for i in range(3):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(c); d.ellipse((2, 55, 2 + L.width, 60), fill=(0, 0, 0, 80)); c.alpha_composite(L, (2, 58 - L.height))
        f = fr(name, 'walk', 1, 0); c.alpha_composite(frame_with(f, f.getbbox()[0] + 4, f.getbbox()[1] + 35, *norm(-0.35, 1), 'knife', dx=12)); out.append(c)
    return out

def sets():
    N = 'Dương'
    return [('knife', [('Đi cầm dao', walk(N, 'knife')), ('Đâm', stab(N, 'knife')), ('Chém', slash(N, 'knife')), ('Hạ gục từ sau', takedown(N))]),
            ('machete', [('Đi cầm dao rựa', walk(N, 'machete')), ('Chém', slash(N, 'machete')), ('Đâm', stab(N, 'machete')), ('Hùng chém', slash('Hùng', 'machete'))])]
