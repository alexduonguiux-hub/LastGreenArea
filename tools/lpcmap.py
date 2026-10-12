import math, random
from PIL import Image, ImageFilter

T = '/home/claude/lpct'
TER = Image.open(f'{T}/terrain-v7.png').convert('RGBA')
CON = Image.open(f'{T}/conifers.png').convert('RGBA')
PLA = Image.open(f'{T}/plants.png').convert('RGBA')
OUT = Image.open(f'{T}/Outside Objects.png').convert('RGBA')
TS = 32; Q = 16

def block(c, r): return (c * 96, r * 224)
BLK = {'forest': block(2, 1), 'grass': block(0, 1), 'dirt': block(1, 0), 'water': block(1, 2)}

def tile(b, tx, ty):
    x0, y0 = BLK[b]
    return TER.crop((x0 + tx*TS, y0 + ty*TS, x0 + tx*TS + TS, y0 + ty*TS + TS))

def quad(b, tx, ty, qx, qy):
    x0, y0 = BLK[b]
    x = x0 + tx*TS + qx*Q; y = y0 + ty*TS + qy*Q
    return TER.crop((x, y, x + Q, y + Q))

def autotile(img, mask, b, rng):
    H = len(mask); W = len(mask[0])
    m = lambda x, y: (0 <= x < W and 0 <= y < H and mask[y][x]) or (not (0 <= x < W and 0 <= y < H))
    for y in range(H):
        for x in range(W):
            if not mask[y][x]: continue
            allin = all(m(x+dx, y+dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if allin:
                img.alpha_composite(tile(b, rng.choice((0, 1, 2)), 5) if rng.random() < 0.5 else tile(b, 1, 3), (x*TS, y*TS)); continue
            for qy in (0, 1):
                for qx in (0, 1):
                    sx = -1 if qx == 0 else 1; sy = -1 if qy == 0 else 1
                    h = m(x+sx, y); v = m(x, y+sy); dg = m(x+sx, y+sy)
                    if not h and not v: src = (0 if qx == 0 else 2, 2 if qy == 0 else 4, qx, qy)
                    elif h and not v: src = (1, 2 if qy == 0 else 4, qx, qy)
                    elif v and not h: src = (0 if qx == 0 else 2, 3, qx, qy)
                    elif not dg:
                        src = {(0, 0): (2, 1, 0, 0), (1, 0): (1, 1, 1, 0), (0, 1): (2, 0, 0, 1), (1, 1): (1, 0, 1, 1)}[(qx, qy)]
                    else: src = (1, 3, qx, qy)
                    img.alpha_composite(quad(b, *src), (x*TS + qx*Q, y*TS + qy*Q))

def comp_at(sheet, px, py, pad=0):
    """bounding box of the opaque connected component containing (px,py)"""
    a = sheet.split()[3]; A = a.load(); W, H = a.size
    if not A[px, py]:
        # search nearby
        for r in range(1, 12):
            for dx in range(-r, r+1):
                for dy in (-r, r):
                    if 0 <= px+dx < W and 0 <= py+dy < H and A[px+dx, py+dy]: px, py = px+dx, py+dy; break
                else: continue
                break
            if A[px, py]: break
    st = [(px, py)]; seen = {(px, py)}; x0 = x1 = px; y0 = y1 = py
    while st:
        cx, cy = st.pop(); x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
        for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and A[nx, ny] > 8:
                seen.add((nx, ny)); st.append((nx, ny))
    return sheet.crop((x0 - pad, y0 - pad, x1 + 1 + pad, y1 + 1 + pad))

# sprites
TREES = [CON.crop(b) for b in [(391, 2, 473, 191), (487, 2, 561, 160), (641, 2, 768, 217), (302, 3, 376, 157), (224, 8, 288, 224)]]
SMALLTREES = [CON.crop(b) for b in [(580, 11, 636, 89), (590, 101, 628, 181)]]
BUSHES = [PLA.crop(b) for b in [(192, 704, 256, 756), (256, 704, 320, 756), (192, 776, 256, 820), (256, 776, 320, 820)]]
