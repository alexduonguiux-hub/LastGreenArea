"""Bảng màu dùng chung cho mọi asset sinh bằng code.

UI: token v10 "cyberpunk nhà máy" (đã chốt, lấy từ tools/locked.py và CSS của prototype).
Nhân vật: bảng màu từng người (lấy từ tools/crawl.py), dùng cho rig ghép lớp ở A2.
Mọi màu là tuple RGB; alpha thêm khi vẽ.
"""

# ---- UI v10 (chốt) -------------------------------------------------------
UI = {
    'bg': (8, 10, 16),          # nền
    'grid': (14, 18, 28),       # lưới ô trên nền
    'panel': (18, 22, 32),      # khung
    'scan': (16, 20, 30),       # vạch quét trong khung
    'edge': (24, 96, 120),      # viền teal
    'tick': (62, 236, 255),     # vạch thước cyan
    'mag': (110, 20, 74),       # bảng tên hình bình hành
    'mag_hi': (255, 58, 168),   # mép bảng tên, ô đang chọn
    'mag_lo': (56, 16, 44),     # bóng bảng tên
    'slot': (22, 28, 40),       # ô vật phẩm
    'ink': (216, 244, 255),     # chữ chính
    'dim': (120, 150, 176),     # chữ phụ
    'warn': (240, 200, 60),     # LED vàng, sức lực
    'ok': (80, 220, 120),       # LED xanh
    'bad': (240, 70, 80),       # LED đỏ, máu
    'bracket_dim': (40, 56, 76),
    'tab_off': (30, 38, 54),
    'bar_off': (30, 36, 52),
    'shadow': (4, 6, 10),
    'black': (0, 0, 0),
}
LED = (UI['bad'], UI['warn'], UI['ok'])

# Thanh chỉ số (HUD v10): máu đỏ, sức lực vàng, ẩn nấp cyan, nhanh tím
STAT = {'hp': UI['bad'], 'sl': UI['warn'], 'stealth': UI['tick'], 'speed': (190, 120, 255)}

# ---- Nhân vật (bản C) ----------------------------------------------------
CHARACTERS = {
    'duong': dict(top=(62, 98, 50), sleeve=(62, 98, 50), skin=(232, 172, 128), pants=(46, 66, 128), shoes=(106, 70, 40)),
    'hung': dict(top=(52, 52, 56), sleeve=(176, 118, 80), skin=(176, 118, 80), pants=(178, 152, 102), shoes=(30, 28, 26)),
    'ny': dict(top=(236, 232, 224), sleeve=(236, 232, 224), skin=(246, 204, 172), pants=(52, 52, 60), shoes=(240, 238, 230)),
    'son': dict(top=(30, 140, 170), sleeve=(30, 140, 170), skin=(232, 172, 128), pants=(42, 44, 50), shoes=(110, 116, 124), pack=(32, 38, 42)),
    'bien-the': dict(top=(112, 112, 118), sleeve=(112, 112, 118), skin=(204, 198, 168), pants=(196, 196, 190), shoes=(150, 120, 100)),
}

# ---- Vật liệu chung cho vũ khí, item (A3) ---------------------------------
MATERIAL = {
    'steel': (120, 128, 140), 'steel_hi': (190, 198, 210), 'steel_lo': (60, 66, 76),
    'gun': (52, 56, 64), 'gun_hi': (96, 102, 112), 'gun_lo': (24, 26, 32),
    'wood': (140, 96, 56), 'wood_hi': (190, 140, 88), 'wood_lo': (90, 58, 32),
    'tan': (178, 152, 102), 'tan_lo': (120, 98, 60),
    'red': (200, 48, 48), 'olive': (94, 122, 52), 'olive_lo': (58, 78, 34),
    'outline': (16, 14, 20), 'white': (248, 248, 248),
}


def hexs(rgb) -> str:
    return '#%02X%02X%02X' % tuple(rgb)


def css_tokens() -> str:
    """Biến CSS cho src/ui/tokens.css (sinh ở A4)."""
    lines = [':root{'] + [f'  --{k.replace("_", "-")}:{hexs(v)};' for k, v in UI.items()] + ['}']
    return '\n'.join(lines)


UI_COLORS = set(UI.values())
