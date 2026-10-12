import sys, math, random; sys.path.insert(0, '.')
import numpy as np
from PIL import Image, ImageDraw
import lpc, npcs
from anim2 import fr
from fx import dust

def tint(im, col, k):
    A = np.array(im).astype(np.float32); m = A[..., 3] > 0
    A[m, :3] = A[m, :3] * (1 - k) + np.array(col) * k
    return Image.fromarray(A.clip(0, 255).astype(np.uint8))

def lying(name, zombie=False):
    """Knocked out on the back, seen from the side (3/4 view): right-facing pose turned 90°, face up, head on the left."""
    f = fr(name, 'walk', 3, 0).transpose(Image.ROTATE_90)
    return f.crop(f.getbbox())

def stars(d, cx, cy, t):
    for k in range(3):
        a = t * math.tau + k * math.tau / 3
        x, y = cx + math.cos(a) * 8, cy + math.sin(a) * 3
        d.point((x, y), fill=(255, 230, 120, 255)); d.point((x + 1, y), fill=(255, 250, 200, 255)); d.point((x, y - 1), fill=(255, 230, 120, 255))

def knockdown(name, zombie=False, n_hold=4):
    out = []; ground = 58
    base = fr(name, 'walk', 3, 0)
    def put(im, dx=0, dy=0):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); c.alpha_composite(im, (dx, dy)); return c
    out.append(put(base, 4))
    out.append(put(tint(base, (255, 255, 255), 0.75), 2))          # hit flash
    out.append(put(tint(base, (232, 70, 50), 0.45), 0))            # red flash, knocked back
    if zombie: mid = fr(name, 'hurt', 0, 1)
    else: mid = fr(name, 'sit', 3, 0)                                 # sits down hard
    out.append(put(mid, -2, 2))
    L = lying(name)
    dfr = dust()
    for k in range(3 + n_hold):
        c = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        x = 32 - L.width // 2 - 2; y = ground - L.height
        d.ellipse((x + 2, ground - 3, x + L.width - 2, ground + 2), fill=(0, 0, 0, 80))
        c.alpha_composite(L, (x, y + (1 if k == 0 else 0)))
        if k < 3: c.alpha_composite(dfr[min(7, 2 + k * 2)], (0, 6))
        if not zombie and k >= 2: stars(d, x + 8, y - 4, k / 4)
        if zombie and k >= 1:
            for j in range(3): d.point((x + 6 + j * 10, y - 2 - ((k + j) % 3)), fill=(232, 85, 61, 255))
        out.append(c)
    return out

if __name__ == '__main__':
    names = ['Dương', 'Hùng', 'Ny', 'Sơn', 'Biến Thể', 'Lính Nhiễm']
    W = Image.new('RGBA', (64 * 11, 64 * len(names)), (50, 66, 52, 255))
    for r, n in enumerate(names):
        for c, f in enumerate(knockdown(n, zombie=n in ('Biến Thể', 'Lính Nhiễm'))): W.alpha_composite(f, (c * 64, r * 64))
    W.resize((W.width * 2, W.height * 2), Image.NEAREST).save('/tmp/knock.png'); print('ok')
