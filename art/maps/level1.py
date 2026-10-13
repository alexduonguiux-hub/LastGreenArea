"""Màn 1 · Đường Mòn Sương: bản đồ cuộn 50×30 tile (1600×960), 4 khu theo docs/level_design.md.

Khu 1 trại (trái dưới, đường mòn hình số 8) → khu 2 rừng thông (giữa) → khu 3 đầu cầu (suối dọc, cầu gỗ là lối
duy nhất) → khu 4 bên kia suối, lối ra ở góc trên phải (Mai dẫn ra khỏi rừng).

Xuất:
  ground   PNG nền (địa hình + cầu) đã hậu kỳ bình minh; cây, bụi, lều là sprite riêng (env/*) để game xếp lớp
  mask     PNG lưới va chạm 100×60 ô 16 px (màu theo loại) để xem/soi
  level    dict -> public/data/levels/level1.json: grid (chuỗi), objects, spawn, zones, patrol, pickups
Loại ô: '.' đi được · '#' chặn và chắn tầm nhìn · 'o' bụi: đi được, khom/bò trong đó thì ẩn · '~' nước · '=' cầu
"""
import math
import random

from PIL import Image, ImageDraw

from maps import lpc
from maps.grade import grade, rays

MW, MH = 50, 30
TS = lpc.TS
CELL = 16
GW, GH = MW * TS // CELL, MH * TS // CELL  # 100×60
W, H = MW * TS, MH * TS

CAMP = (10.0, 22.0)            # tile: giữa trại
LOOP_A, LOOP_B = (10.0, 22.0), (19.5, 22.0)  # hai vòng của hình số 8
RIVER_X0 = 31.5
BRIDGE_TY = 14.0               # tile y của tim cầu
EXIT = (47.5, 3.0)


def river_x(y):
    return RIVER_X0 + 0.9 * math.sin(y / 3.2)


def forest_path_y(x):
    """Khu 2: từ đỉnh vòng B (x≈19.5, y≈17) lên đầu cầu (x≈29, y=14)."""
    t = (x - 19.5) / (29.0 - 19.5)
    return 17.0 - 3.0 * t + 0.6 * math.sin(x * 1.1)


def far_path_y(x):
    """Khu 4: từ đầu cầu đông (x≈34) lên lối ra (47.5, 3)."""
    t = (x - 34.0) / (EXIT[0] - 34.0)
    return BRIDGE_TY - (BRIDGE_TY - EXIT[1]) * t + 0.5 * math.sin(x / 1.7)


def masks():
    water = [[abs(x + 0.5 - river_x(y + 0.5)) < 1.8 for x in range(MW)] for y in range(MH)]
    dirt = [[False] * MW for _ in range(MH)]
    for y in range(MH):
        for x in range(MW):
            cx, cy = x + 0.5, y + 0.5
            on = False
            for (lx, ly) in (LOOP_A, LOOP_B):
                if abs(math.hypot(cx - lx, (cy - ly) * 1.25) - 4.3) < 1.15:
                    on = True
            if 19.5 <= cx <= 29.5 and abs(cy - forest_path_y(cx)) < 1.1:
                on = True
            if 29.0 <= cx <= 34.5 and abs(cy - BRIDGE_TY) < 1.1:
                on = True
            if 34.0 <= cx <= EXIT[0] + 1 and abs(cy - far_path_y(cx)) < 1.1:
                on = True
            if math.hypot(cx - CAMP[0], (cy - CAMP[1]) * 1.25) < 2.2:
                on = True  # sân trại
            dirt[y][x] = on and not water[y][x]
    rng = random.Random(5)
    # mảng cỏ tối (dưới tán rừng dày, khu 2 và rìa bản đồ) và mảng nắng (gần trại, ven suối)
    dark = [[False] * MW for _ in range(MH)]
    sun = [[False] * MW for _ in range(MH)]
    for _ in range(40):
        cx, cy, r = rng.uniform(0, MW), rng.uniform(0, MH), rng.uniform(2.5, 5.0)
        dense = 18 <= cx <= 30 and 9 <= cy <= 24
        if not dense and rng.random() < 0.5:
            continue
        for y in range(MH):
            for x in range(MW):
                if math.hypot(x - cx, (y - cy) * 1.2) < r and not water[y][x]:
                    dark[y][x] = True
    return water, dirt, dark, sun  # sun: dự phòng, hiện không vẽ (khối 'sun' viền gắt trên nền cỏ)


def draw_bridge(img: Image.Image):
    d = ImageDraw.Draw(img)
    by = int(BRIDGE_TY * TS)
    rx = int(river_x(BRIDGE_TY) * TS)
    bx0, bx1 = rx - 78, rx + 78
    bt, bb = by - 26, by + 26
    d.rectangle((bx0, bb + 2, bx1, bb + 8), fill=(10, 30, 40, 255))
    for x in range(bx0, bx1, 8):
        c = [(122, 90, 56), (108, 80, 50), (134, 100, 64)][(x // 8) % 3]
        d.rectangle((x, bt, x + 6, bb), fill=c + (255,))
        d.line([(x + 7, bt), (x + 7, bb)], fill=(58, 40, 26, 255))
        d.point((x + 2, bt + 3), fill=(70, 50, 32, 255))
        d.point((x + 3, bb - 4), fill=(70, 50, 32, 255))
    for yy in (bt - 4, bb + 1):
        d.rectangle((bx0 - 2, yy, bx1 + 2, yy + 3), fill=(84, 60, 38, 255))
        d.line([(bx0 - 2, yy), (bx1 + 2, yy)], fill=(150, 112, 72, 255))
        for x in range(bx0, bx1 + 1, 39):
            d.rectangle((x - 2, yy - 4, x + 2, yy + 4), fill=(60, 42, 28, 255))
    return (bx0, bt - 4, bx1, bb + 4)


def build(env: dict[str, Image.Image]):
    rng = random.Random(11)
    img = Image.new('RGBA', (W, H))
    full = [[True] * MW for _ in range(MH)]
    lpc.autotile(img, full, 'grass', rng)
    water, dirt, dark, sun = masks()
    lpc.autotile(img, dark, 'forest', rng)
    lpc.autotile(img, dirt, 'dirt', rng)
    # nước: lớp riêng 3 khung (ô lõi cuộn dọc = sóng trôi), khung 0 cũng in vào nền
    water_frames = []
    for k in range(3):
        wl = Image.new('RGBA', (W, H))
        # ô lõi có vệt sóng (hàng 5 của khối), cuộn dọc 11 px mỗi khung → sóng trôi xuôi dòng
        lpc.autotile(wl, water, 'water', random.Random(1), interior=lambda x, y, k=k: lpc.roll_v(lpc.tile('water', (x + y) % 3, 5), k * 11))
        water_frames.append(wl)
    img.alpha_composite(water_frames[0])
    bridge = draw_bridge(img)
    for wl in water_frames:
        draw_bridge(wl)  # lớp nước nằm trên nền nên phải mang cả cầu

    def blocked_tile(x, y, pad=1):
        tx, ty = int(x // TS), int(y // TS)
        for dy in range(-pad, pad + 1):
            for dx in range(-pad, pad + 1):
                xx, yy = tx + dx, ty + dy
                if 0 <= xx < MW and 0 <= yy < MH and (water[yy][xx] or dirt[yy][xx]):
                    return True
        return False

    def covers_path(x, y, w, h):
        """Tán cây (hình chữ nhật phía trên chân) có đè lên đường hoặc nước không: giữ đường mòn đọc được."""
        for ty in range(max(0, int((y - h) // TS)), min(MH, int(y // TS) + 1)):
            for tx in range(max(0, int((x - w / 2) // TS)), min(MW, int((x + w / 2) // TS) + 1)):
                if water[ty][tx] or dirt[ty][tx]:
                    return True
        return False

    camp_px = (CAMP[0] * TS, CAMP[1] * TS)
    keep = [camp_px, (EXIT[0] * TS, EXIT[1] * TS), (bridge[0] - 40, (bridge[1] + bridge[3]) / 2), (bridge[2] + 40, (bridge[1] + bridge[3]) / 2)]
    objects = []  # (y_sort, id, x, y_base)

    # cây: rừng dày ở khu 2 (x 600–950), thưa hơn nơi khác; không đè đường, nước, trại
    placed = []
    tries = 0
    while tries < 30000 and len(placed) < 260:
        tries += 1
        x, y = rng.uniform(10, W - 10), rng.uniform(10, H + 40)
        dense = 580 < x < 960 and 300 < y < 760
        if not dense and rng.random() < 0.6:
            continue
        if blocked_tile(x, y, 1):
            continue
        if any(math.hypot(x - kx, y - ky) < 120 for kx, ky in keep):
            continue
        mind = 58 if dense else 84
        if any(math.hypot(x - px, (y - py) * 1.4) < mind for px, py in placed):
            continue
        # hai cỡ cây: thông (rừng dày nhiều thông hơn) và tán tròn như moodboard
        kind = rng.choice(['conifer-0', 'conifer-1', 'conifer-2']) if rng.random() < (0.5 if dense else 0.35) else rng.choice(['tree-0', 'tree-1', 'tree-2', 'tree-3'])
        im = env[kind]
        if covers_path(x, y, min(im.width, 56), im.height * 0.8):
            continue
        placed.append((x, y))
        objects.append((y, f'env/{kind}', int(x), int(y)))
    # bụi: nơi nấp, ưu tiên ven đường khu 2 và hai đầu cầu
    bushes = 0
    tries = 0
    while tries < 20000 and bushes < 40:
        tries += 1
        x, y = rng.uniform(10, W - 10), rng.uniform(10, H - 10)
        if blocked_tile(x, y, 0):
            continue
        if any(math.hypot(x - kx, y - ky) < 90 for kx, ky in keep[:2]):
            continue
        if any(math.hypot(x - px, (y - py) * 1.4) < 44 for px, py in placed):
            continue
        near_path = blocked_tile(x, y, 1)
        if not near_path and rng.random() < 0.7:
            continue
        placed.append((x, y))
        bushes += 1
        objects.append((y, f'env/bush-{rng.randrange(4)}', int(x), int(y)))
    # bụi nấp cố định cho bài học: trước đầu cầu tây và cạnh đường rừng
    for (x, y) in ((bridge[0] - 70, bridge[3] + 40), (bridge[0] - 150, bridge[1] - 30), (760, 470), (690, 560), (bridge[2] + 60, bridge[3] + 50)):
        objects.append((y, 'env/bush-1', int(x), int(y)))
    # đá và gỗ đổ: vật cản nhỏ rải trong rừng và ven đường, không đè đường/nước
    rocks = 0
    tries = 0
    while tries < 20000 and rocks < 9:
        tries += 1
        x, y = rng.uniform(20, W - 20), rng.uniform(20, H - 20)
        if blocked_tile(x, y, 0) or any(math.hypot(x - kx, y - ky) < 100 for kx, ky in keep):
            continue
        if any(math.hypot(x - px, (y - py) * 1.4) < 40 for px, py in placed):
            continue
        kind = 'log-fallen' if rocks % 4 == 3 else rng.choice(['rock-0', 'rock-1', 'rock-2'])
        placed.append((x, y))
        rocks += 1
        objects.append((y, f'env/{kind}', int(x), int(y)))
    # trại: lều, củi, gốc cây làm ghế
    cx, cy = camp_px
    objects.append((cy - 46, 'env/tent', int(cx - 70), int(cy - 46)))
    objects.append((cy + 30, 'env/logs', int(cx + 6), int(cy + 30)))
    objects.append((cy + 2, 'env/stump', int(cx + 62), int(cy + 2)))
    objects.sort(key=lambda o: (o[0], o[1], o[2]))

    # ---- lưới va chạm 100×60 ----
    grid = [['.'] * GW for _ in range(GH)]
    for ty in range(MH):
        for tx in range(MW):
            if water[ty][tx]:
                for dy in (0, 1):
                    for dx in (0, 1):
                        grid[ty * 2 + dy][tx * 2 + dx] = '~'
    bx0, by0, bx1, by1 = bridge
    for cy_ in range(by0 // CELL, by1 // CELL + 1):
        for cx_ in range(bx0 // CELL, bx1 // CELL + 1):
            if 0 <= cy_ < GH and 0 <= cx_ < GW:
                grid[cy_][cx_] = '='

    def fill(x0, y0, x1, y1, ch, only_dot=True):
        for cy_ in range(max(0, int(y0 // CELL)), min(GH, int(y1 // CELL) + 1)):
            for cx_ in range(max(0, int(x0 // CELL)), min(GW, int(x1 // CELL) + 1)):
                if not only_dot or grid[cy_][cx_] == '.':
                    grid[cy_][cx_] = ch

    for (_, oid, x, y) in objects:
        im = env[oid.split('/', 1)[1]]
        w, h = im.size
        if oid.startswith('env/conifer') or oid.startswith('env/tree-'):
            fill(x - 9, y - 10, x + 8, y - 1, '#')           # gốc cây chặn + chắn tầm nhìn
        elif oid.startswith('env/rock') or oid == 'env/log-fallen':
            fill(x - w / 2 + 3, y - h * 0.45, x + w / 2 - 4, y - 1, '#')
        elif oid.startswith('env/bush'):
            fill(x - w / 2 + 2, y - h + 6, x + w / 2 - 3, y - 1, 'o')
        else:
            fill(x - w / 2 + 2, y - h * 0.55, x + w / 2 - 3, y - 1, '#')
    for cx_ in range(GW):
        grid[0][cx_] = grid[GH - 1][cx_] = '#'
    for cy_ in range(GH):
        grid[cy_][0] = grid[cy_][GW - 1] = '#'
    # lối ra: mở mép trên phải
    for cx_ in range(int((EXIT[0] - 1.5) * 2), int((EXIT[0] + 1.5) * 2)):
        if 0 < cx_ < GW - 1:
            grid[0][cx_] = '.'

    # ---- trang trí nướng vào nền: hoa ven đường, nấm trong rừng, sậy/súng ven suối, cỏ cao (ô 'o' núp được) ----
    decor = lpc.ground_decor()

    def near_water(tx, ty):
        return any(0 <= tx + dx < MW and 0 <= ty + dy < MH and water[ty + dy][tx + dx] for dx in (-1, 0, 1) for dy in (-1, 0, 1))

    def paste(name, x, y):
        im = decor[name]
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height)))

    # cỏ cao: mảng 64×64 đặt có chủ ý ở lối tiếp cận cầu (lấp khoảng trống giữa các bụi) và ven lối ra, cộng ngẫu nhiên trong rừng
    patches = [(760, 528), (826, 508), (700, 468), (1200, 420), (1262, 318), (1392, 262), (1462, 206), (1120, 540)]
    tries = 0
    while tries < 4000 and len(patches) < 12:
        tries += 1
        x, y = rng.uniform(40, W - 40), rng.uniform(40, H - 40)
        tx, ty = int(x // TS), int(y // TS)
        if water[ty][tx] or dirt[ty][tx] or any(math.hypot(x - kx, y - ky) < 110 for kx, ky in keep):
            continue
        if any(math.hypot(x - px, y - py) < 120 for px, py in patches):
            continue
        patches.append((int(x), int(y)))
    # mỗi mảng = nhiều cụm cỏ rải trong hình elip (mép tự nhiên, không cắt vuông); ô lưới trong lõi elip thành 'o'
    for (x, y) in patches:
        rx, ry = 36, 24
        clumps = []
        for _ in range(60):
            if len(clumps) >= 16:
                break
            u, v = rng.uniform(-1, 1), rng.uniform(-1, 1)
            if u * u + v * v > 1:
                continue
            cx_, cy_ = x + u * rx, y + v * ry
            tx, ty = int(cx_ // TS), int(cy_ // TS)
            if not (0 <= tx < MW and 0 <= ty < MH) or water[ty][tx] or dirt[ty][tx]:
                continue
            clumps.append((cx_, cy_ + 14))
        for (cx_, cy_) in sorted(clumps, key=lambda c: c[1]):
            paste('reeds', cx_, cy_)
        for gy in range(int((y - ry) // CELL), int((y + ry) // CELL) + 1):
            for gx in range(int((x - rx) // CELL), int((x + rx) // CELL) + 1):
                px_, py_ = gx * CELL + 8, gy * CELL + 8
                if ((px_ - x) / (rx - 4)) ** 2 + ((py_ - y) / (ry - 4)) ** 2 <= 1 and not dirt[py_ // TS][px_ // TS]:
                    fill(px_, py_, px_, py_, 'o')
    # hoa ven đường mòn, nấm trong rừng dày, sậy và súng ven suối
    for _ in range(24):
        x, y = rng.uniform(10, W - 10), rng.uniform(10, H - 10)
        if blocked_tile(x, y, 0) or not blocked_tile(x, y, 1):
            continue
        paste(f'flower-{rng.randrange(3)}', x, y)
    for _ in range(6):
        x, y = rng.uniform(580, 960), rng.uniform(300, 760)
        if blocked_tile(x, y, 0):
            continue
        paste('mush-1', x, y)
    for _ in range(220):
        x, y = rng.uniform(10, W - 10), rng.uniform(10, H - 10)
        tx, ty = int(x // TS), int(y // TS)
        if water[ty][tx] or dirt[ty][tx] or not near_water(tx, ty):
            continue
        paste(rng.choice(['reeds', 'reeds', 'cattail']), x, y)
    # súng: in vào cả 3 khung nước, chỉ khi cả bốn góc lá nằm trong nước (không cắt bờ), tránh gầm cầu
    lily = decor['lily']
    for _ in range(300):
        x, y = rng.uniform(10, W - 10), rng.uniform(10, H - 10)
        if abs(y - BRIDGE_TY * TS) < 70:
            continue
        corners = [(x - lily.width / 2, y - lily.height), (x + lily.width / 2, y - lily.height), (x - lily.width / 2, y), (x + lily.width / 2, y)]
        if not all(0 <= cx_ < W and 0 <= cy_ < H and water[int(cy_ // TS)][int(cx_ // TS)] for cx_, cy_ in corners):
            continue
        for wl in water_frames:
            wl.alpha_composite(lily, (int(x - lily.width / 2), int(y - lily.height)))

    ground = rays(grade(img))
    # hộp nước (ô) → dải khung ngang; nền in lại khung 0 đã grade (không vệt nắng dither trên mặt nước)
    wx = [x for y in range(MH) for x in range(MW) if water[y][x]]
    wy = [y for y in range(MH) for x in range(MW) if water[y][x]]
    wbox = (min(wx) * TS, min(wy) * TS, (max(wx) + 1) * TS, (max(wy) + 1) * TS)
    frames = [grade(wl.crop(wbox)) for wl in water_frames]
    fw, fh = frames[0].size
    water_strip = Image.new('RGBA', (fw * len(frames), fh))
    for k, fr in enumerate(frames):
        water_strip.paste(fr, (k * fw, 0))
    ground.alpha_composite(frames[0], (wbox[0], wbox[1]))
    mask = Image.new('RGBA', (GW, GH))
    COL = {'.': (0, 0, 0, 0), '#': (240, 70, 80, 255), 'o': (80, 220, 120, 255), '~': (62, 150, 255, 255), '=': (240, 200, 60, 255)}
    mp = mask.load()
    for y in range(GH):
        for x in range(GW):
            mp[x, y] = COL[grid[y][x]]
    mask = mask.resize((GW * 4, GH * 4), Image.NEAREST)

    bridge_mid_y = (bridge[1] + bridge[3]) // 2
    level = {
        'name': 'Đường Mòn Sương',
        'size': [W, H],
        'cell': CELL,
        'ground': 'assets/maps/level1_ground.png',
        'water': {'image': 'assets/maps/level1_water.png', 'x': wbox[0], 'y': wbox[1], 'w': fw, 'h': fh, 'frames': len(frames), 'fps': 3},
        'grid': [''.join(r) for r in grid],
        'objects': [{'id': oid, 'x': x, 'y': y} for (_, oid, x, y) in objects],
        'spawn': {'duong': [int(cx - 20), int(cy + 56)], 'hung': [int(cx + 28), int(cy + 66)], 'ny': [int(cx - 56), int(cy + 70)], 'son': [int(cx + 60), int(cy + 48)]},
        'zones': {
            'trai': [0, 480, 560, 960],
            'rung': [560, 280, 960, 960],
            'dau-cau': [bridge[0] - 200, bridge[1] - 160, bridge[2] + 40, bridge[3] + 160],
            'ben-kia': [bridge[2] + 40, 0, W, 760],
        },
        'bridge': list(bridge),
        'patrol': {
            # canh cầu: tuần tra sát đầu cầu; đường mòn rừng và điểm lưu nhịp 1–2 nằm ngoài tầm nhìn 144 px của nó
            'canh-cau': {'type': 'ke-lang-thang', 'points': [[bridge[0] - 120, bridge_mid_y + 2], [bridge[0] - 30, bridge_mid_y + 2]]},
            'canh-loi-ra': {'type': 'ke-lang-thang', 'points': [[int(41.5 * TS), int(far_path_y(41.5) * TS)], [int(45.5 * TS), int(far_path_y(45.5) * TS)]]},
        },
        'mai': {
            'appear': [int(20.5 * TS), int(forest_path_y(20.5) * TS) - 10],
            'path': [[int(25 * TS), int(forest_path_y(25) * TS) - 12], [bridge[2] + 60, bridge_mid_y - 14], [int(39 * TS), int(far_path_y(39) * TS) - 12], [int(EXIT[0] * TS), int(EXIT[1] * TS) + 24]],
        },
        'exit': [int(EXIT[0] * TS), int(EXIT[1] * TS)],
        # vùng kích hoạt 4 nhịp hướng dẫn (x0, y0, x1, y1)
        'triggers': {
            'vong-xa': [int((LOOP_B[0] + 3.0) * TS), int((LOOP_B[1] - 5.5) * TS), int((LOOP_B[0] + 6.0) * TS), int((LOOP_B[1] + 5.5) * TS)],
            'trai-ve': [int((CAMP[0] - 3.0) * TS), int((CAMP[1] - 3.0) * TS), int((CAMP[0] + 3.0) * TS), int((CAMP[1] + 3.0) * TS)],
            'rung': [int(18.5 * TS), int(13 * TS), int(19.8 * TS), int(20 * TS)],
            'dau-cau': [bridge[0] - 250, bridge[1] - 120, bridge[0] - 190, bridge[3] + 120],
            'qua-cau': [bridge[2] + 10, bridge[1] - 20, bridge[2] + 70, bridge[3] + 20],
            'loi-ra': [int((EXIT[0] - 2.5) * TS), 0, int((EXIT[0] + 2.5) * TS), int((EXIT[1] + 1.5) * TS)],
        },
        # điểm lưu: vị trí thủ lĩnh ở đầu mỗi nhịp (đội xếp quanh)
        'checkpoints': {
            'trai': [int(cx - 20), int(cy + 56)],
            'rung': [int(19.0 * TS), int(forest_path_y(19.0) * TS) + 10],
            'dau-cau': [bridge[0] - 282, bridge_mid_y + 50],
            'ben-kia': [bridge[2] + 44, bridge_mid_y + 30],
        },
        # hằng số ẩn nấp của màn (B2); chỉnh ở đây rồi npm run art, không sửa trong code game
        'stealth': {
            # Nón nhìn kiểu Commandos: vùng gần (near) thấy là báo động ngay, vùng xa đầy đồng hồ theo tư thế.
            'vision': {'angle': 100, 'range': 144, 'near': 64},
            'detect': {'suspect': 0.3, 'fillBase': 2.0, 'stance': {'chay': 1.4, 'dung': 1.0, 'khom': 0.55, 'bo': 0.25}, 'decay': 0.3},
            # Tiếng động (px): đá ném; bước chân theo tư thế (chạy 10 ô, đi 3.5 ô, khom 1 ô, bò im) phát mỗi stepEvery giây.
            'noise': {'rock': 120, 'step': {'chay': 160, 'dung': 56, 'khom': 16, 'bo': 0},
                      'stepEvery': {'chay': 0.3, 'dung': 0.45, 'khom': 0.6, 'bo': 1.0}},
            'speed': {'patrol': 16, 'investigate': 24, 'alert': 34},
            'listenEvery': 3.0, 'listenFor': 1.6, 'lookFor': 3.0, 'downFor': 30.0,
            'takedown': {'dist': 22},
            'rocks': 2,
        },
        'pickups': [
            {'item': 'da-khac-ky-hieu', 'x': int(LOOP_B[0] * TS + 4.3 * TS), 'y': int(LOOP_B[1] * TS)},
            {'item': 'da-khac-ky-hieu', 'x': int(25 * TS), 'y': int(forest_path_y(25) * TS) + 20},
            {'item': 'da-khac-ky-hieu', 'x': int(42 * TS), 'y': int(far_path_y(42) * TS) - 24},
            {'item': 'manh-ky-uc', 'x': int(cx + 96), 'y': int(cy + 10)},
            {'item': 'anh-bon-nguoi', 'x': int(cx - 40), 'y': int(cy + 20)},
            {'item': 'da-nem', 'x': int(cx + 40), 'y': int(cy + 70)},
            {'item': 'da-nem', 'x': int((LOOP_B[0] + 4.3) * TS) + 10, 'y': int((LOOP_B[1] - 2) * TS)},
            {'item': 'da-nem', 'x': int(22.5 * TS), 'y': int(forest_path_y(22.5) * TS) + 24},
            {'item': 'da-nem', 'x': int(26.5 * TS), 'y': int(forest_path_y(26.5) * TS) - 20},
            {'item': 'da-nem', 'x': bridge[0] - 200, 'y': bridge_mid_y + 60},
        ],
    }
    return ground, mask, level, water_strip
