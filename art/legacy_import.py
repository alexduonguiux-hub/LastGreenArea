"""Nhập các sheet bàn giao (assets/) vào ma trận theo JSON mô tả cũ.

Đây là bước "nhập tạm" của A1: mọi khung cũ có mặt trong atlas ngay, game chạy được;
A2–A5 thay dần từng nhóm bằng nguồn code trong art/, nhóm nào đã thay thì bỏ khỏi đây.

Quy ước id: nhóm/tên/hoạt-ảnh/khung, slug ASCII, ví dụ char/duong/di-xuong/3.
"""
import json
from pathlib import Path
from PIL import Image
from slug import slug

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
DATA = ROOT / 'data'
LEGACY = Path(__file__).resolve().parent / 'legacy'

MAIN = ('Dương', 'Hùng', 'Ny', 'Sơn')
FOOT = (32, 60)      # neo chân nhân vật trong khung 64
CENTER64 = (32, 32)  # neo FX

# fps mặc định theo tên hoạt ảnh (A5 sẽ tinh chỉnh và thêm sự kiện theo khung)
FPS_RULES = (('chạy', 12), ('bị hạ', 11), ('trúng đòn', 11), ('đứng thở', 2), ('nghe ngóng', 6),
             ('lơ lửng', 6), ('hiện ra', 8), ('ngồi nghỉ', 4))
NO_LOOP = ('bị hạ', 'trúng đòn', 'hiện ra', 'hạ gục', 'ám sát', 'khóa siết', 'phá cửa', 'mở khóa', 'băng bó',
           'ném đá', 'nhảy', 'leo trèo', 'vồ', 'rơi xuống', 'lao tới', 'húc', 'phun', 'giả giọng', 'bị lửa')


def fps_for(anim: str) -> int:
    a = anim.lower()
    for k, v in FPS_RULES:
        if k in a:
            return v
    return 10


def loop_for(anim: str) -> bool:
    a = anim.lower()
    return not any(k in a for k in NO_LOOP)


class Importer:
    def __init__(self, matrix):
        self.m = matrix
        self.anims = {}  # anim_id -> dict
        self.log = []
        self.frames = {}  # anim_id -> [Image] (để sinh pose dẫn xuất)

    # ---- tiện ích -----------------------------------------------------
    def _sheet(self, rel: str):
        return Image.open(ASSETS / rel).convert('RGBA')

    def _anim(self, aid, name, actor, frames, anchor, fps=None, loop=None, source=None):
        self.anims[aid] = {'name': name, 'actor': actor, 'frames': frames, 'fps': fps or fps_for(name),
                           'loop': loop_for(name) if loop is None else loop, 'anchor': list(anchor), 'source': source}

    def _rows(self, sheet, meta, group_of, zone_of, anchor=FOOT, fw=64, fh=64, seen=None, source=''):
        """meta: [[actor, anim, n], ...] mỗi hàng một hoạt ảnh."""
        cols = sheet.width // fw
        for r, (actor, anim, n) in enumerate(meta):
            key = (actor, anim)
            if seen is not None:
                if key in seen:
                    self.log.append(f'bỏ qua trùng: {actor} / {anim} ({source})')
                    continue
                seen.add(key)
            assert n <= cols, (actor, anim, n, cols)
            group = group_of(actor)
            aid = f'{group}/{slug(anim)}'
            ids = []
            imgs = []
            for i in range(n):
                fr = sheet.crop((i * fw, r * fh, i * fw + fw, r * fh + fh))
                if anim.startswith('Bò') and fw == 64:
                    fr = self.strip_grass(fr)
                fid = f'{aid}/{i}'
                self.m.place(fid, fr, zone_of(actor), group, anchor)
                ids.append(fid)
                imgs.append(fr)
            self.frames[aid] = imgs
            self._anim(aid, anim, actor, ids, anchor, source=source)

    # ---- nhóm ---------------------------------------------------------
    def characters(self):
        seen = set()

        def group_of(actor):
            return f'char/{slug(actor)}' if actor in MAIN else f'enemy/{slug(actor)}'

        def zone_of(actor):
            return 'char' if actor in MAIN else 'bienthe'

        for name in ('anim_core', 'anim_more', 'anim_actions'):
            meta = json.load(open(DATA / f'{name}.json', encoding='utf-8'))['meta']
            self._rows(self._sheet(f'characters/{name}.png'), meta, group_of, zone_of, seen=seen, source=name)

    # ---- dọn khung bàn giao ------------------------------------------------
    GRASS = {(58, 104, 52), (74, 128, 60), (46, 86, 44)}       # cỏ do tools/crawl.py vẽ thêm
    DARK = {(12, 7, 15), (24, 14, 21), (0, 0, 0), (24, 18, 16)}  # viền tối polish vẽ quanh lá cỏ

    @classmethod
    def strip_grass(cls, im, y0=55):
        """Bỏ cỏ nướng sẵn dưới khung bò: xóa 3 màu cỏ, rồi xóa viền tối ở hàng dưới không chạm thân."""
        im = im.copy()
        px = im.load()
        for y in range(y0, 64):
            for x in range(64):
                if px[x, y][3] and px[x, y][:3] in cls.GRASS:
                    px[x, y] = (0, 0, 0, 0)
        for _ in range(3):
            for y in range(y0, 64):
                for x in range(64):
                    p = px[x, y]
                    if not p[3] or p[:3] not in cls.DARK:
                        continue
                    body = False
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            xx, yy = x + dx, y + dy
                            if (dx or dy) and 0 <= xx < 64 and 0 <= yy < 64:
                                q = px[xx, yy]
                                if q[3] and q[:3] not in cls.DARK and q[:3] not in cls.GRASS:
                                    body = True
                    if not body:
                        px[x, y] = (0, 0, 0, 0)
        return im

    # ---- pose dẫn xuất bằng code ---------------------------------------
    @staticmethod
    def crouch(fr, hip=46, foot=61, legs_h=8):
        """Khom: ép phần chân (hip→foot) còn legs_h px rồi hạ thân xuống; chân vẫn ở y=60."""
        out = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        shift = (foot - hip) - legs_h
        out.alpha_composite(fr.crop((0, 0, 64, hip)), (0, shift))
        out.alpha_composite(fr.crop((0, hip, 64, foot)).resize((64, legs_h), Image.NEAREST), (0, hip + shift))
        out.alpha_composite(fr.crop((0, foot, 64, 64)), (0, foot))
        return out

    def crouch_anims(self):
        """Tư thế Khom cho 4 nhân vật: khom-trai, khom-xuong, khom-len dẫn xuất từ đi trái, đi xuống, chạy lên."""
        for name in MAIN:
            g = f'char/{slug(name)}'
            for src, dst, label in (('di-sang-trai', 'khom-trai', 'Khom đi trái'), ('di-xuong', 'khom-xuong', 'Khom đi xuống'), ('chay-len', 'khom-len', 'Khom đi lên')):
                imgs = self.frames.get(f'{g}/{src}')
                if not imgs:
                    self.log.append(f'thiếu {g}/{src} để sinh {dst}')
                    continue
                aid = f'{g}/{dst}'
                ids = []
                for i, fr in enumerate(imgs):
                    fid = f'{aid}/{i}'
                    self.m.place(fid, self.crouch(fr), 'char', g, FOOT)
                    ids.append(fid)
                self._anim(aid, label, name, ids, FOOT, fps=8, loop=True, source='derived:crouch')

    def wanderer(self):
        sheet = self._sheet('enemies/wanderer_walk_knockdown.png')
        meta = [['Kẻ Lang Thang', 'Lê bước trái', 8], ['Kẻ Lang Thang', 'Bị hạ', 11]]
        self._rows(sheet, meta, lambda a: 'enemy/ke-lang-thang', lambda a: 'bienthe', source='wanderer')

    def zombies(self):
        meta = json.load(open(DATA / 'zombies.json', encoding='utf-8'))['meta']
        self._rows(self._sheet('enemies/zombies.png'), meta, lambda a: f'enemy/{slug(a)}', lambda a: 'zombies',
                   source='zombies')

    def npcs(self):
        meta = json.load(open(DATA / 'npcs.json', encoding='utf-8'))['meta']
        self._rows(self._sheet('npcs/npcs.png'), meta, lambda a: f'npc/{slug(a)}', lambda a: 'npc', source='npcs')

    def fx(self):
        meta = json.load(open(DATA / 'fx.json', encoding='utf-8'))['meta']
        self._rows(self._sheet('fx/fx.png'), meta, lambda a: 'fx', lambda a: 'fx', anchor=CENTER64, source='fx')

    def melee(self):
        d = json.load(open(DATA / 'melee_anim.json', encoding='utf-8'))
        self._rows(self._sheet('weapons/melee_anim.png'), d['meta'], lambda a: f'melee/{a}', lambda a: 'melee',
                   source='melee_anim')

    def weapons(self):
        W = json.load(open(DATA / 'weapons.json', encoding='utf-8'))
        rows = json.load(open(LEGACY / 'weapons_rows.json', encoding='utf-8'))
        sheet = self._sheet('weapons/weapons_anim_v2.png')
        icons = self._sheet('weapons/weapon_icons_v2.png')
        atlas = self._sheet('weapons/weapons_atlas_v2.png')
        cols = sheet.width // 64
        for wid, w in W.items():
            info = rows[wid]
            for key in ('walk', 'aim', 'fire'):
                r, n = info['anim'][key]['row'], info['anim'][key]['n']
                assert n <= cols
                aid = f'weapon/{wid}/{key}'
                ids = []
                for i in range(n):
                    fr = sheet.crop((i * 64, r * 64, i * 64 + 64, r * 64 + 64))
                    fid = f'{aid}/{i}'
                    self.m.place(fid, fr, 'weapons', f'weapon/{wid}', FOOT)
                    ids.append(fid)
                label = {'walk': 'Đi cầm', 'aim': 'Ngắm', 'fire': 'Bắn'}[key]
                self._anim(aid, f'{label} · {w["name"]}', 'Dương', ids, FOOT,
                           fps={'walk': 10, 'aim': 4, 'fire': 14}[key], loop=key != 'fire', source='weapons_anim_v2')
            x, y, iw, ih = info['icon']
            self.m.place(f'weapon/{wid}/icon', icons.crop((x, y, x + iw, y + ih)), 'items', f'weapon/{wid}',
                         (iw // 2, ih // 2), trim=False)
            x, y, aw, ah = w['atlas_rect']
            self.m.place(f'weapon/{wid}/sprite', atlas.crop((x, y, x + aw, y + ah)), 'items', f'weapon/{wid}',
                         tuple(w['grip']), trim=False)

    def items(self):
        items = json.load(open(DATA / 'items.json', encoding='utf-8'))
        sheet = self._sheet('items/item_icons.png')
        assert sheet.width == 16 * len(items), (sheet.width, len(items))
        for i, it in enumerate(items):
            self.m.place(f'item/{slug(it["name"])}', sheet.crop((i * 16, 0, i * 16 + 16, 16)), 'items', 'item',
                         (8, 8), trim=False)

    def all(self):
        self.characters()
        self.crouch_anims()
        self.wanderer()
        self.zombies()
        self.npcs()
        self.weapons()
        self.melee()
        self.fx()
        self.items()
        return self
