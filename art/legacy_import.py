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
            for i in range(n):
                fr = sheet.crop((i * fw, r * fh, i * fw + fw, r * fh + fh))
                fid = f'{aid}/{i}'
                self.m.place(fid, fr, zone_of(actor), group, anchor)
                ids.append(fid)
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
        self.wanderer()
        self.zombies()
        self.npcs()
        self.weapons()
        self.melee()
        self.fx()
        self.items()
        return self
