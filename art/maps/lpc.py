"""Tile LPC: autotile địa hình 32 px và cắt sprite cây, bụi, đồ vật từ tileset trong assets/tiles.

Port từ tools/lpcmap.py, bỏ đường dẫn /home/claude. Chỉ đọc file, không ghi.
"""
import random
from functools import lru_cache
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
TILES = ROOT / 'assets' / 'tiles'
TS = 32  # tile
Q = 16   # quarter tile


@lru_cache(maxsize=None)
def sheet(name: str) -> Image.Image:
    return Image.open(TILES / name).convert('RGBA')


def block(c, r):
    return (c * 96, r * 224)


# Khối địa hình trong terrain-v7.png: mỗi khối 3×7 tile (lõi + viền chuyển tiếp)
BLK = {'forest': block(2, 1), 'grass': block(0, 1), 'dirt': block(1, 0), 'water': block(1, 2)}


def tile(b, tx, ty):
    x0, y0 = BLK[b]
    return sheet('terrain-v7.png').crop((x0 + tx * TS, y0 + ty * TS, x0 + tx * TS + TS, y0 + ty * TS + TS))


def quad(b, tx, ty, qx, qy):
    x0, y0 = BLK[b]
    x = x0 + tx * TS + qx * Q
    y = y0 + ty * TS + qy * Q
    return sheet('terrain-v7.png').crop((x, y, x + Q, y + Q))


def autotile(img: Image.Image, mask, b: str, rng: random.Random):
    """Vẽ địa hình b lên img tại mọi ô mask=True, viền chuyển tiếp theo 8 ô lân cận (quarter-tile)."""
    H = len(mask)
    W = len(mask[0])

    def m(x, y):
        return (0 <= x < W and 0 <= y < H and mask[y][x]) or not (0 <= x < W and 0 <= y < H)

    for y in range(H):
        for x in range(W):
            if not mask[y][x]:
                continue
            allin = all(m(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if allin:
                t = tile(b, rng.choice((0, 1, 2)), 5) if rng.random() < 0.5 else tile(b, 1, 3)
                img.alpha_composite(t, (x * TS, y * TS))
                continue
            for qy in (0, 1):
                for qx in (0, 1):
                    sx = -1 if qx == 0 else 1
                    sy = -1 if qy == 0 else 1
                    h = m(x + sx, y)
                    v = m(x, y + sy)
                    dg = m(x + sx, y + sy)
                    if not h and not v:
                        src = (0 if qx == 0 else 2, 2 if qy == 0 else 4, qx, qy)
                    elif h and not v:
                        src = (1, 2 if qy == 0 else 4, qx, qy)
                    elif v and not h:
                        src = (0 if qx == 0 else 2, 3, qx, qy)
                    elif not dg:
                        src = {(0, 0): (2, 1, 0, 0), (1, 0): (1, 1, 1, 0), (0, 1): (2, 0, 0, 1), (1, 1): (1, 0, 1, 1)}[(qx, qy)]
                    else:
                        src = (1, 3, qx, qy)
                    img.alpha_composite(quad(b, *src), (x * TS + qx * Q, y * TS + qy * Q))


def comp_at(im: Image.Image, px, py, pad=0):
    """Hộp bao của thành phần liên thông (pixel đục) chứa (px, py) trong tileset."""
    a = im.split()[3]
    A = a.load()
    W, H = a.size
    if not A[px, py]:
        for r in range(1, 12):
            found = False
            for dx in range(-r, r + 1):
                for dy in (-r, r):
                    if 0 <= px + dx < W and 0 <= py + dy < H and A[px + dx, py + dy]:
                        px, py = px + dx, py + dy
                        found = True
                        break
                if found:
                    break
            if found:
                break
    st = [(px, py)]
    seen = {(px, py)}
    x0 = x1 = px
    y0 = y1 = py
    while st:
        cx, cy = st.pop()
        x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and A[nx, ny] > 8:
                seen.add((nx, ny))
                st.append((nx, ny))
    return im.crop((x0 - pad, y0 - pad, x1 + 1 + pad, y1 + 1 + pad))


# ---- sprite môi trường (id trong atlas: env/<tên>) ---------------------------------
def env_sprites() -> dict[str, Image.Image]:
    con = sheet('conifers.png')
    pla = sheet('plants.png')
    out = sheet('Outside Objects.png')
    s = {}
    for i, b in enumerate([(391, 2, 473, 191), (487, 2, 561, 160), (641, 2, 768, 217), (302, 3, 376, 157), (224, 8, 288, 224)]):
        s[f'conifer-{i}'] = con.crop(b)
    for i, b in enumerate([(580, 11, 636, 89), (590, 101, 628, 181)]):
        s[f'conifer-small-{i}'] = con.crop(b)
    for i, b in enumerate([(192, 704, 256, 756), (256, 704, 320, 756), (192, 776, 256, 820), (256, 776, 320, 820)]):
        s[f'bush-{i}'] = pla.crop(b)
    s['tent'] = comp_at(out, 60, 790)
    s['logs'] = comp_at(out, 420, 470)
    s['stump'] = pla.crop((0, 760, 64, 820))
    return s
