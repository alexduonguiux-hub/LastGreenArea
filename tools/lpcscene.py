import math, random
from PIL import Image
from lpcmap import *

MW, MH = 25, 15
def river_x(y): return 13.0 + 0.9 * math.sin(y / 3.2)
def path_y(x): return 8.6 + 0.45 * math.sin(x / 4.5)

def masks():
    water = [[abs(x + 0.5 - river_x(y + 0.5)) < 1.8 for x in range(MW)] for y in range(MH)]
    dirt = [[abs(y + 0.5 - path_y(x + 0.5)) < 1.3 and not water[y][x] for x in range(MW)] for y in range(MH)]
    rng = random.Random(5)
    grass = [[False]*MW for _ in range(MH)]
    for _ in range(7):
        cx, cy, r = rng.uniform(0, MW), rng.uniform(0, MH), rng.uniform(1.5, 3)
        for y in range(MH):
            for x in range(MW):
                if math.hypot(x - cx, (y - cy) * 1.2) < r and not water[y][x]: grass[y][x] = True
    return water, dirt, grass

def base_map(seed=3):
    rng = random.Random(seed)
    img = Image.new('RGBA', (MW*TS, MH*TS))
    full = [[True]*MW for _ in range(MH)]
    autotile(img, full, 'forest', rng)
    water, dirt, grass = masks()
    autotile(img, grass, 'grass', rng)
    autotile(img, dirt, 'dirt', rng)
    autotile(img, water, 'water', rng)
    return img, water, dirt, grass

if __name__ == '__main__':
    img, *_ = base_map()
    img.save('/home/claude/gen/lpc_out/map.png')
    print(img.size)
