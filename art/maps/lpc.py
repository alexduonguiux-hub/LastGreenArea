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
BLK = {'forest': block(2, 1), 'grass': block(0, 1), 'sun': block(1, 1), 'dirt': block(1, 0), 'water-t7': block(1, 2)}


@lru_cache(maxsize=None)
def water_block() -> Image.Image:
    """Khối 3×7 tổng hợp cho 'water': bộ "nước trong cỏ" 3×3 + 2×2 của Terrain and Outside (mép cỏ phủ lên nước,
    bờ nâu chỉ lộ ở cạnh trên/dưới) xếp theo bố cục autotile: hàng 0–1 cột 1–2 góc lõm, hàng 2–4 viền 3×3, hàng 5 ô lõi."""
    ter = sheet('Terrain and Outside.png')
    blk = Image.new('RGBA', (96, 224), (0, 0, 0, 0))
    blk.paste(ter.crop((480, 576, 544, 640)), (32, 0))
    blk.paste(ter.crop((480, 640, 576, 736)), (0, 64))
    for i in range(3):
        blk.paste(ter.crop((512, 672, 544, 704)), (i * 32, 160))
    return blk


def _src(b):
    """(ảnh, x0, y0) của khối b: khối tổng hợp hoặc khối trong terrain-v7."""
    if b == 'water':
        return water_block(), 0, 0
    x0, y0 = BLK[b]
    return sheet('terrain-v7.png'), x0, y0


def tile(b, tx, ty):
    im, x0, y0 = _src(b)
    return im.crop((x0 + tx * TS, y0 + ty * TS, x0 + tx * TS + TS, y0 + ty * TS + TS))


def quad(b, tx, ty, qx, qy):
    im, x0, y0 = _src(b)
    x = x0 + tx * TS + qx * Q
    y = y0 + ty * TS + qy * Q
    return im.crop((x, y, x + Q, y + Q))


def roll_v(im: Image.Image, dy: int) -> Image.Image:
    """Cuộn ảnh theo chiều dọc (ô lõi liền mạch nên cuộn vẫn khớp mép): dùng làm khung sóng nước."""
    dy %= im.height
    if not dy:
        return im
    out = Image.new('RGBA', im.size)
    out.paste(im.crop((0, 0, im.width, im.height - dy)), (0, dy))
    out.paste(im.crop((0, im.height - dy, im.width, im.height)), (0, 0))
    return out


def autotile(img: Image.Image, mask, b: str, rng: random.Random, interior=None):
    """Vẽ địa hình b lên img tại mọi ô mask=True, viền chuyển tiếp theo 8 ô lân cận (quarter-tile).
    interior(x, y) -> ảnh ô lõi (mặc định: trộn ngẫu nhiên các ô lõi của khối)."""
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
                t = interior(x, y) if interior else (tile(b, rng.choice((0, 1, 2)), 5) if rng.random() < 0.5 else tile(b, 1, 3))
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
def _split_v(im: Image.Image):
    """Tách một thành phần gồm hai vật xếp dọc (hàng alpha trống ở giữa) thành (trên, dưới)."""
    a = im.split()[3]
    rows = [any(a.getpixel((x, y)) > 8 for x in range(im.width)) for y in range(im.height)]
    gaps = [y for y in range(1, im.height) if rows[y - 1] and not rows[y]]
    cut = gaps[0] if gaps else im.height // 2
    top = im.crop((0, 0, im.width, cut))
    bot = im.crop((0, cut, im.width, im.height))
    return top.crop(top.getbbox()), bot.crop(bot.getbbox())


def _tree(canopy: Image.Image, trunk: Image.Image, overlap=34) -> Image.Image:
    """Cây tán tròn LPC: tán đặt chồng lên thân (Outside Objects tách tán và thân riêng)."""
    w = max(canopy.width, trunk.width)
    h = canopy.height + trunk.height - overlap
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    im.alpha_composite(trunk, ((w - trunk.width) // 2, canopy.height - overlap))
    im.alpha_composite(canopy, ((w - canopy.width) // 2, 0))
    return im


def env_sprites() -> dict[str, Image.Image]:
    """Vật thể có xếp lớp theo y trong game (cây, bụi, đá, gỗ, lều, củi)."""
    con = sheet('conifers.png')
    pla = sheet('plants.png')
    out = sheet('Outside Objects.png')
    ter = sheet('Terrain and Outside.png')
    s = {}
    # hai cỡ cây thống nhất: thông 154–189 px và tán tròn ~118 px (bỏ thông 216 px và cây nhỏ 45–60 px cho đồng bộ tỷ lệ)
    for i, b in enumerate([(391, 2, 473, 191), (487, 2, 561, 160), (302, 3, 376, 157)]):
        s[f'conifer-{i}'] = con.crop(b)
    # cây tán tròn: 2 tán × 2 thân (Outside Objects)
    canopies = [comp_at(out, 240, 50), comp_at(out, 335, 50)]
    trunks = [comp_at(out, 45, 490), comp_at(out, 140, 490)]
    for i, (c, t) in enumerate(((0, 0), (1, 1), (0, 1), (1, 0))):
        s[f'tree-{i}'] = _tree(canopies[c], trunks[t])
    for i, b in enumerate([(192, 704, 256, 756), (256, 704, 320, 756), (192, 776, 256, 820), (256, 776, 320, 820)]):
        s[f'bush-{i}'] = pla.crop(b)
    # đá (Terrain and Outside): đá dựng xám, đá trắng, đá nâu
    s['rock-0'] = comp_at(ter, 1000, 640)
    white, brown = _split_v(comp_at(ter, 975, 545))
    s['rock-1'] = white
    s['rock-2'] = brown
    s['log-fallen'] = comp_at(pla, 60, 880)
    s['tent'] = comp_at(out, 60, 790)
    s['logs'] = comp_at(out, 420, 470)
    s['stump'] = pla.crop((0, 760, 64, 820))
    return s


def ground_decor() -> dict[str, Image.Image]:
    """Trang trí nướng thẳng vào nền (không xếp lớp): hoa, nấm, sậy, súng, cỏ cao (ô 'o' núp được)."""
    pla = sheet('plants.png')
    ter = sheet('Terrain and Outside.png')
    s = {}
    for i, (px, py) in enumerate(((140, 230), (60, 160), (120, 110), (30, 300))):
        s[f'flower-{i}'] = comp_at(pla, px, py)
    s['mush-0'] = comp_at(pla, 45, 690)
    s['mush-1'] = comp_at(pla, 140, 690)
    s['reeds'] = comp_at(pla, 150, 470)
    s['cattail'] = comp_at(pla, 60, 450)
    s['lily'] = comp_at(pla, 80, 510)
    s['grass-tall-0'] = ter.crop((0, 736, 64, 800))
    s['grass-tall-1'] = ter.crop((64, 736, 128, 800))
    return s
