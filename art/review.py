"""Sinh bản review đứng độc lập: python3 art/review.py  (hoặc npm run art:review)

Gộp prototype/atlas_viewer.html + atlas.js + 2 trang PNG (base64) thành MỘT file
prototype/atlas_review.html, mở trực tiếp trên bất kỳ máy nào, không cần repo hay server.
"""
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
SRC = ROOT / 'prototype' / 'atlas_viewer.html'
OUT = ROOT / 'prototype' / 'atlas_review.html'


def main():
    html = SRC.read_text(encoding='utf-8')
    js = (build.OUT_DATA / 'atlas.js').read_text(encoding='utf-8')
    imgs = {}
    for name in build.PAGES:
        data = (build.OUT_IMG / name).read_bytes()
        imgs[name] = 'data:image/png;base64,' + base64.b64encode(data).decode('ascii')
    js += 'window.ATLAS_IMG=' + repr(imgs).replace("'", '"') + ';\n'
    tag = '<script src="../public/data/atlas.js"></script>'
    assert tag in html, 'không tìm thấy thẻ atlas.js trong viewer'
    html = html.replace(tag, '<script>\n' + js + '</script>')
    old = "im.src = '../public/assets/' + t.image;"
    assert old in html
    html = html.replace(old, "im.src = window.ATLAS_IMG[t.image];")
    html = html.replace('<title>Vùng Xanh · Xem ma trận atlas</title>',
                        '<title>Vùng Xanh · Review ma trận atlas (bản độc lập)</title>')
    OUT.write_text(html, encoding='utf-8')
    print(f'{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
