"""Sinh atlas: python3 art/build.py  (hoặc npm run art)

Đầu ra (đều là file sinh, không sửa tay):
  public/assets/atlas_0.png, atlas_1.png   trang ma trận 2048×2048
  public/data/atlas.json                   manifest TexturePacker multiatlas + cell/zone/group/anchor
  public/data/atlas.js                     bản JS của manifest + anims để viewer mở từ file://
  public/data/anims.json                   hoạt ảnh: khung, fps, lặp, neo
"""
import hashlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from matrix import Matrix, Zone  # noqa: E402
from legacy_import import Importer  # noqa: E402
from maps import lpc as lpc_tiles  # noqa: E402
from maps import level1  # noqa: E402
from maps.grade import grade  # noqa: E402
from ui.components import all_components  # noqa: E402
from ui.css import css as ui_css  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_IMG = ROOT / 'public' / 'assets'
OUT_DATA = ROOT / 'public' / 'data'
PAGES = ['atlas_0.png', 'atlas_1.png']

# Phân vùng cố định theo hàng 16 px (xem docs/PLAN.md A1). Dải 4 hàng = 32 khung 64 px chưa trim.
ZONES = [
    Zone('char', 0, 0, 83),       # 4 nhân vật chính
    Zone('bienthe', 0, 84, 95),   # Biến Thể cơ bản + Kẻ Lang Thang
    Zone('zombies', 0, 96, 123),  # 6 loại Biến Thể màn 3–8
    Zone('spare0', 0, 124, 127),
    Zone('npc', 1, 0, 19),
    Zone('weapons', 1, 20, 55),   # hoạt ảnh đi/ngắm/bắn 18 vũ khí
    Zone('melee', 1, 56, 63),
    Zone('fx', 1, 64, 79),
    Zone('items', 1, 80, 83),     # 33 item + icon và sprite vũ khí
    Zone('ui', 1, 84, 107),       # thành phần UI 9-slice (A4)
    Zone('env', 1, 108, 127),      # cây, bụi, lều, củi (sprite môi trường, xếp lớp theo y trong game)
]


def png_bytes(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


def build():
    """Sinh mọi file đầu ra trong bộ nhớ. Trả về (matrix, outputs{đường dẫn tương đối: bytes}, manifest, anims, log)."""
    m = Matrix(ZONES)
    imp = Importer(m).all()
    env = {k: grade(v) for k, v in lpc_tiles.env_sprites().items()}
    for name, im in env.items():
        # neo = chân vật thể: giữa đáy; cây có bóng nên nhích lên 6 px
        foot = im.height - (6 if name.startswith('conifer') else 2)
        m.place(f'env/{name}', im, 'env', 'env', (im.width // 2, foot), trim=False)
    # thành phần UI v10 (A4): vào vùng ui, kèm slice/outset trong manifest; cắt ra sprite riêng cho CSS border-image
    comps = all_components()
    for name, spec in comps.items():
        f = m.place(f'ui/{name}', spec['img'], 'ui', 'ui', (0, 0), trim=False)
        if spec['slice']:
            f.extra = {'slice': list(spec['slice']), 'outset': spec['outset']}
    manifest = m.manifest(PAGES)
    anims = imp.anims
    manifest['meta']['frames'] = len(m.frames)
    manifest['meta']['anims'] = len(anims)
    ground, mask, level = level1.build(env)
    outputs = {}
    for name, im in zip(PAGES, m.pages):
        outputs[f'public/assets/{name}'] = png_bytes(im)
    outputs['public/assets/maps/level1_ground.png'] = png_bytes(ground)
    outputs['public/assets/maps/level1_mask.png'] = png_bytes(mask)
    outputs['public/data/atlas.json'] = dumps(manifest).encode('utf-8')
    outputs['public/data/anims.json'] = dumps(anims).encode('utf-8')
    outputs['public/data/levels/level1.json'] = dumps(level).encode('utf-8')
    outputs['public/data/atlas.js'] = atlas_js(manifest, anims).encode('utf-8')
    page1 = m.pages[1]
    for f in m.frames:
        if f.group == 'ui':
            crop = page1.crop((f.x, f.y, f.x + f.w, f.y + f.h))
            outputs[f'src/ui/sprites/{f.id.split("/", 1)[1]}.png'] = png_bytes(crop)
    outputs['src/ui/v10.css'] = ui_css(comps).encode('utf-8')
    return m, outputs, manifest, anims, imp.log


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + '\n'


def atlas_js(manifest, anims):
    """Bản JS cho viewer/gallery mở từ file://, kèm dữ liệu mô tả để hiển thị tên, nhóm, chỉ số."""
    data_dir = ROOT / 'data'
    extras = {
        'ITEMS': json.loads((data_dir / 'items.json').read_text(encoding='utf-8')),
        'WEAPONS': json.loads((data_dir / 'weapons.json').read_text(encoding='utf-8')),
        'ZOMBIE_INFO': json.loads((data_dir / 'zombies.json').read_text(encoding='utf-8'))['rows'],
    }
    js = 'window.ATLAS=' + json.dumps(manifest, ensure_ascii=False) + ';\nwindow.ANIMS=' + \
         json.dumps(anims, ensure_ascii=False) + ';\n'
    for k, v in extras.items():
        js += f'window.{k}=' + json.dumps(v, ensure_ascii=False) + ';\n'
    return js


def write(outputs):
    for rel, data in outputs.items():
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)


def main():
    m, outputs, manifest, anims, log = build()
    write(outputs)
    for line in log:
        print('  ', line)
    print(f'khung: {len(m.frames)}  hoạt ảnh: {len(anims)}')
    for z in manifest['meta']['zones']:
        pct = 100 * z['used'] / z['capacity']
        print(f"  trang {z['page']} {z['name']:8s} hàng {z['row0']:3d}–{z['row1']:3d}  dùng {z['used']:5d}/{z['capacity']:5d} ô ({pct:4.1f} %)")
    for rel, data in outputs.items():
        if rel.endswith('.png'):
            print(f'  {rel}: {len(data) // 1024} KB  sha256 {hashlib.sha256(data).hexdigest()[:12]}')


if __name__ == '__main__':
    main()
