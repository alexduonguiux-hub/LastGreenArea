"""Kiểm tra atlas: python3 art/check.py  (hoặc npm run art:check). Thoát mã 1 nếu có lỗi.

1. id duy nhất, khung nằm trong trang, không chồng lấn ô, ô nằm đúng vùng.
2. Mọi hoạt ảnh trỏ tới khung có thật; mọi khung thuộc nhóm hoạt ảnh đều được một hoạt ảnh dùng.
3. Pixel ngoài ô đã cấp phát phải trong suốt (ảnh và manifest khớp nhau).
4. Nhóm ui/ chỉ dùng màu trong bảng token v10.
5. Tất định: sinh lại trong bộ nhớ phải ra đúng byte như file đã commit.
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
from matrix import CELLS, UNIT  # noqa: E402
from palette import UI_COLORS  # noqa: E402

errors = []


def err(msg):
    errors.append(msg)


def main():
    atlas = json.loads((build.OUT_DATA / 'atlas.json').read_text(encoding='utf-8'))
    anims = json.loads((build.OUT_DATA / 'anims.json').read_text(encoding='utf-8'))
    zones = {z['name']: z for z in atlas['meta']['zones']}
    ids = set()
    occ = {}
    pages = []
    for p, tex in enumerate(atlas['textures']):
        im = Image.open(build.OUT_IMG / tex['image']).convert('RGBA')
        pages.append(im)
        if im.size != (tex['size']['w'], tex['size']['h']):
            err(f'{tex["image"]}: kích thước {im.size} khác manifest')
        grid = occ.setdefault(p, bytearray(CELLS * CELLS))
        for f in tex['frames']:
            fid = f['filename']
            if fid in ids:
                err(f'id trùng {fid}')
            ids.add(fid)
            fr = f['frame']
            if fr['x'] + fr['w'] > im.width or fr['y'] + fr['h'] > im.height:
                err(f'{fid} vượt ngoài trang')
            col, row, cw, ch = f['cell']
            z = zones[f['zone']]
            if z['page'] != p or not (z['row0'] <= row and row + ch - 1 <= z['row1']):
                err(f'{fid} nằm ngoài vùng {f["zone"]}')
            if (fr['x'], fr['y']) != (col * UNIT, row * UNIT) or fr['w'] > cw * UNIT or fr['h'] > ch * UNIT:
                err(f'{fid} khung không khớp ô')
            for r in range(row, row + ch):
                for c in range(col, col + cw):
                    if grid[r * CELLS + c]:
                        err(f'{fid} chồng lấn ô ({c},{r})')
                    grid[r * CELLS + c] = 1
            if f['group'].startswith('ui'):
                colors = {px[:3] for px in im.crop((fr['x'], fr['y'], fr['x'] + fr['w'], fr['y'] + fr['h'])).getdata() if px[3]}
                bad = colors - UI_COLORS
                if bad:
                    err(f'{fid} dùng màu ngoài token v10: {sorted(bad)[:3]}')
    # 3. pixel ngoài ô đã cấp phát
    for p, im in enumerate(pages):
        alpha = im.split()[3]
        grid = occ[p]
        for r in range(CELLS):
            for c in range(CELLS):
                if not grid[r * CELLS + c]:
                    if alpha.crop((c * UNIT, r * UNIT, c * UNIT + UNIT, r * UNIT + UNIT)).getbbox():
                        err(f'trang {p} ô ({c},{r}) có pixel nhưng không được cấp phát')
    # 2. hoạt ảnh
    used = set()
    for aid, a in anims.items():
        if not a['frames']:
            err(f'hoạt ảnh {aid} không có khung')
        for fid in a['frames']:
            if fid not in ids:
                err(f'hoạt ảnh {aid} trỏ tới khung không tồn tại {fid}')
            if not fid.startswith(aid + '/'):
                err(f'hoạt ảnh {aid} chứa khung lạ {fid}')
            used.add(fid)
    for fid in ids:
        if fid.count('/') >= 3 and fid.rsplit('/', 1)[1].isdigit() and fid not in used:
            err(f'khung {fid} không thuộc hoạt ảnh nào')
    # 5. tất định
    m, pngs, manifest, anims2, _ = build.build()
    for name, data in zip(build.PAGES, pngs):
        if (build.OUT_IMG / name).read_bytes() != data:
            err(f'{name} trên đĩa khác bản sinh lại (ảnh bị sửa tay hoặc build không tất định)')
    if build.dumps(manifest) != (build.OUT_DATA / 'atlas.json').read_text(encoding='utf-8'):
        err('atlas.json trên đĩa khác bản sinh lại')
    if build.dumps(anims2) != (build.OUT_DATA / 'anims.json').read_text(encoding='utf-8'):
        err('anims.json trên đĩa khác bản sinh lại')

    if errors:
        print(f'LỖI ({len(errors)}):')
        for e in errors[:50]:
            print('  -', e)
        sys.exit(1)
    print(f'OK: {len(ids)} khung, {len(anims)} hoạt ảnh, {len(pages)} trang, tất định.')


if __name__ == '__main__':
    main()
