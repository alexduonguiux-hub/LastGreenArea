"""Ma trận atlas: trang 2048×2048 chia lưới 128×128 ô 16 px.

Mọi asset chiếm một hình chữ nhật ô (col, row, w, h) tính theo đơn vị 16 px, nằm trong một
"vùng" (zone) là một dải hàng cố định của trang, để tọa độ ổn định giữa các lần sinh.
Khung được cắt viền (trim) theo hộp bao pixel thật, làm tròn lên bội số 16, và ghi độ lệch
so với khung gốc (spriteSourceSize) để game đặt neo đúng chỗ.

Xuất: PNG mỗi trang + manifest dạng TexturePacker multiatlas (Phaser `load.multiatlas`),
có thêm các khóa riêng: cell, zone, group, anchor.
"""
from dataclasses import dataclass, field
from PIL import Image

UNIT = 16
PAGE = 2048
CELLS = PAGE // UNIT  # 128


class ZoneFull(Exception):
    pass


@dataclass
class Zone:
    name: str
    page: int
    row0: int
    row1: int  # inclusive
    _x: int = 0
    _shelf_row: int = field(default=-1)
    _shelf_h: int = 0
    used: int = 0

    @property
    def capacity(self):
        return (self.row1 - self.row0 + 1) * CELLS

    def alloc(self, cw: int, ch: int):
        if cw > CELLS:
            raise ValueError(f'asset rộng {cw} ô, quá bề rộng trang')
        if self._shelf_row < 0:
            self._shelf_row, self._x, self._shelf_h = self.row0, 0, ch
        if self._x + cw > CELLS:
            self._shelf_row += self._shelf_h
            self._x, self._shelf_h = 0, ch
        # dải hiện tại luôn là dải cuối nên nới cao thêm là an toàn (phía dưới chưa có gì)
        if ch > self._shelf_h:
            self._shelf_h = ch
        if self._shelf_row + self._shelf_h - 1 > self.row1:
            raise ZoneFull(f'vùng {self.name} (trang {self.page}) đầy khi đặt asset {cw}×{ch} ô')
        col, row = self._x, self._shelf_row
        self._x += cw
        self.used += cw * ch
        return col, row


@dataclass
class Frame:
    id: str
    page: int
    x: int
    y: int
    w: int
    h: int
    ox: int
    oy: int
    sw: int
    sh: int
    cell: tuple
    zone: str
    group: str
    anchor: tuple  # pixel trong khung gốc
    trimmed: bool
    empty: bool = False

    def to_json(self):
        return {
            'filename': self.id,
            'frame': {'x': self.x, 'y': self.y, 'w': self.w, 'h': self.h},
            'rotated': False,
            'trimmed': self.trimmed,
            'spriteSourceSize': {'x': self.ox, 'y': self.oy, 'w': self.w, 'h': self.h},
            'sourceSize': {'w': self.sw, 'h': self.sh},
            'anchor': {'x': round(self.anchor[0] / self.sw, 5), 'y': round(self.anchor[1] / self.sh, 5)},
            'cell': list(self.cell),
            'zone': self.zone,
            'group': self.group,
            **({'empty': True} if self.empty else {}),
        }


def _cells(px: int) -> int:
    return max(1, -(-px // UNIT))


class Matrix:
    def __init__(self, zones: list[Zone]):
        pages = sorted({z.page for z in zones})
        assert pages == list(range(len(pages))), 'trang phải đánh số liên tục từ 0'
        self.pages = [Image.new('RGBA', (PAGE, PAGE), (0, 0, 0, 0)) for _ in pages]
        self.occ = [bytearray(CELLS * CELLS) for _ in pages]
        self.zones = {z.name: z for z in zones}
        self.frames: list[Frame] = []
        self.ids = set()
        self._check_zones(zones)

    @staticmethod
    def _check_zones(zones):
        by_page = {}
        for z in zones:
            by_page.setdefault(z.page, []).append(z)
        for p, zs in by_page.items():
            zs.sort(key=lambda z: z.row0)
            for a, b in zip(zs, zs[1:]):
                if a.row1 >= b.row0:
                    raise ValueError(f'vùng {a.name} và {b.name} chồng hàng trên trang {p}')
            for z in zs:
                assert 0 <= z.row0 <= z.row1 < CELLS, z

    def place(self, id: str, img: Image.Image, zone: str, group: str, anchor=(0, 0), trim=True) -> Frame:
        if id in self.ids:
            raise ValueError(f'id trùng: {id}')
        z = self.zones[zone]
        img = img.convert('RGBA')
        sw, sh = img.size
        bbox = img.split()[3].getbbox() if trim else (0, 0, sw, sh)
        empty = bbox is None
        if empty:
            bbox = (0, 0, 1, 1)
        ox, oy, x1, y1 = bbox
        crop = img.crop(bbox)
        w, h = crop.size
        cw, ch = _cells(w), _cells(h)
        col, row = z.alloc(cw, ch)
        occ = self.occ[z.page]
        for r in range(row, row + ch):
            for c in range(col, col + cw):
                if occ[r * CELLS + c]:
                    raise RuntimeError(f'chồng lấn tại trang {z.page} ô ({c},{r}) khi đặt {id}')
                occ[r * CELLS + c] = 1
        px, py = col * UNIT, row * UNIT
        if not empty:
            self.pages[z.page].alpha_composite(crop, (px, py))
        f = Frame(id, z.page, px, py, w, h, ox, oy, sw, sh, (col, row, cw, ch), zone, group, tuple(anchor),
                  trimmed=(w, h) != (sw, sh), empty=empty)
        self.frames.append(f)
        self.ids.add(id)
        return f

    def manifest(self, image_names: list[str], extra: dict | None = None) -> dict:
        textures = []
        for p, im in enumerate(self.pages):
            textures.append({
                'image': image_names[p],
                'format': 'RGBA8888',
                'size': {'w': im.width, 'h': im.height},
                'scale': 1,
                'frames': [f.to_json() for f in self.frames if f.page == p],
            })
        zones = [{'name': z.name, 'page': z.page, 'row0': z.row0, 'row1': z.row1,
                  'used': z.used, 'capacity': z.capacity} for z in self.zones.values()]
        meta = {'app': 'vung-xanh/art', 'version': '1', 'unit': UNIT, 'page': PAGE, 'cells': CELLS, 'zones': zones}
        if extra:
            meta.update(extra)
        return {'textures': textures, 'meta': meta}
