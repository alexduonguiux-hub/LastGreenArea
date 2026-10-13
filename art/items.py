"""Vật phẩm màn 1 vẽ bằng code theo kiểu Cainos: viền tối ấm (58,50,40), 3 tông sáng/giữa/tối, bóng dưới.

Mỗi hàm trả ảnh 16×16 RGBA (id item/<slug>); A3 sẽ thay dần toàn bộ 33 icon bàn giao bằng nguồn code ở đây.
"""
from PIL import Image, ImageDraw

OUT = (58, 50, 40)
STONE = {'hi': (168, 166, 156), 'mid': (135, 133, 121), 'lo': (100, 94, 82)}
PAPER = {'hi': (226, 222, 204), 'mid': (205, 200, 178), 'lo': (160, 152, 128)}
AMBER = (196, 150, 60)
GLOW = {'hi': (236, 246, 236), 'mid': (150, 196, 184), 'lo': (86, 132, 126)}
SHADOW = (40, 36, 30, 90)


def _new():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))


def _shadow(d, x0, x1, y):
    d.ellipse((x0, y - 1, x1, y + 1), fill=SHADOW)


def da_khac_ky_hieu():
    """Phiến đá dẹt, mặt trên sáng, khắc ký hiệu mũi tên hổ phách."""
    im = _new()
    d = ImageDraw.Draw(im)
    _shadow(d, 2, 14, 13)
    d.polygon([(3, 5), (12, 3), (14, 6), (13, 12), (4, 13), (2, 9)], fill=OUT)
    d.polygon([(4, 6), (11, 4), (13, 7), (12, 11), (5, 12), (3, 9)], fill=STONE['mid'])
    d.polygon([(4, 6), (11, 4), (12, 6), (6, 8), (4, 8)], fill=STONE['hi'])
    d.polygon([(6, 11), (12, 9), (12, 11), (5, 12)], fill=STONE['lo'])
    # ký hiệu: mũi tên chỉ hướng + chấm
    d.line([(6, 10), (10, 7)], fill=AMBER)
    d.line([(8, 7), (10, 7), (10, 9)], fill=AMBER)
    d.point((6, 7), fill=AMBER)
    return im


def manh_ky_uc():
    """Mảnh tinh thể phát sáng: lõi trắng, thân teal nhạt, viền tối; cắm nghiêng trên đất."""
    im = _new()
    d = ImageDraw.Draw(im)
    _shadow(d, 4, 12, 14)
    d.polygon([(8, 1), (12, 6), (11, 13), (7, 14), (4, 8)], fill=OUT)
    d.polygon([(8, 2), (11, 6), (10, 12), (7, 13), (5, 8)], fill=GLOW['mid'])
    d.polygon([(8, 2), (11, 6), (9, 7), (7, 5)], fill=GLOW['hi'])
    d.polygon([(9, 7), (10, 12), (7, 13), (8, 9)], fill=GLOW['lo'])
    d.line([(8, 3), (8, 6)], fill=GLOW['hi'])
    # tia sáng nhỏ
    for (x, y) in ((2, 5), (14, 10), (13, 3)):
        d.point((x, y), fill=GLOW['hi'])
    return im


def anh_bon_nguoi():
    """Ảnh chụp giấy cũ hơi nghiêng: khung giấy, nền trời, bốn người nhỏ."""
    im = _new()
    d = ImageDraw.Draw(im)
    _shadow(d, 2, 14, 14)
    d.polygon([(2, 3), (14, 2), (14, 13), (2, 14)], fill=OUT)
    d.polygon([(3, 4), (13, 3), (13, 12), (3, 13)], fill=PAPER['mid'])
    d.line([(3, 4), (13, 3)], fill=PAPER['hi'])
    d.line([(3, 13), (13, 12)], fill=PAPER['lo'])
    d.rectangle((5, 5, 11, 10), fill=(150, 170, 150))
    d.rectangle((5, 9, 11, 10), fill=(110, 112, 60))
    for i, c in enumerate(((98, 110, 56), (70, 66, 60), (205, 200, 178), (60, 110, 120))):
        x = 5 + i * 2
        d.point((x, 7), fill=(200, 160, 120))
        d.point((x, 8), fill=c)
    return im


def da_nem():
    """Viên đá cuội tròn, 3 tông, bóng dưới."""
    im = _new()
    d = ImageDraw.Draw(im)
    _shadow(d, 3, 13, 13)
    d.ellipse((3, 5, 13, 13), fill=OUT)
    d.ellipse((4, 6, 12, 12), fill=STONE['mid'])
    d.ellipse((5, 7, 9, 9), fill=STONE['hi'])
    d.arc((4, 6, 12, 12), 20, 160, fill=STONE['lo'])
    return im


ITEMS = {
    'da-khac-ky-hieu': da_khac_ky_hieu,
    'manh-ky-uc': manh_ky_uc,
    'anh-bon-nguoi': anh_bon_nguoi,
    'da-nem': da_nem,
}


def all_items() -> dict[str, Image.Image]:
    return {k: f() for k, f in ITEMS.items()}
