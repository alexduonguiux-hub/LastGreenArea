"""Bảng màu dùng chung cho mọi asset sinh bằng code.

UI: token v11 "đá và gỗ" (chốt theo hệ màu Cainos; v10 cyberpunk đã bỏ).
Nhân vật: bảng màu từng người (lấy từ tools/crawl.py), dùng cho rig ghép lớp ở A2.
Mọi màu là tuple RGB; alpha thêm khi vẽ.
"""

# ---- UI v11 "đá và gỗ" (chốt 2026-10-13, màu lấy từ đá, bệ, tường, thùng gỗ của Cainos) ---------------
# Tên khóa giữ nguyên từ v10 để CSS và thành phần không đổi; nghĩa mới ghi bên cạnh.
UI = {
    'bg': (36, 34, 28),          # nền trang (ngoài sân khấu)
    'grid': (44, 42, 34),        # lưới ô trên nền trang
    'panel': (135, 133, 121),    # phiến đá (thân khung)
    'scan': (128, 127, 114),     # đá tối hơn một bậc (vân, nút vô hiệu)
    'edge': (87, 82, 72),        # viền đá tối
    'tick': (152, 150, 142),     # cạnh đá sáng (bevel)
    'mag': (79, 41, 19),         # ván gỗ (thẻ tiêu đề, phím, nút bấm)
    'mag_hi': (196, 150, 60),    # hổ phách: ô đang chọn, vạch chọn
    'mag_lo': (58, 30, 14),      # gỗ tối (bóng ván)
    'slot': (100, 94, 82),       # ô lõm (vật phẩm, chân dung)
    'ink': (40, 36, 30),         # chữ chính trên đá
    'dim': (78, 74, 64),         # chữ phụ trên đá
    'warn': (196, 150, 60),      # hổ phách: sức lực, nhiệm vụ, đồng hồ
    'ok': (139, 134, 50),        # ô-liu sáng: máu, vật phẩm
    'bad': (160, 62, 46),        # đỏ gạch: báo động
    'bracket_dim': (112, 108, 96),
    'tab_off': (118, 116, 105),  # tab/nút thường (đá tối)
    'bar_off': (112, 108, 96),   # ô thanh chưa đầy
    'shadow': (60, 56, 48),      # bóng dưới khung
    'black': (30, 28, 24),       # viền glyph
    'mag_line': (120, 84, 52),   # cạnh sáng ván gỗ
    'card_sel': (124, 120, 98),  # thẻ đang chọn (đá ngả ô-liu)
    'card_stripe': (130, 126, 104),
    'choice': (118, 116, 105),   # dòng lựa chọn
    'choice_sel': (110, 108, 60),  # dòng đang chọn (ô-liu tối)
    'track': (100, 94, 82),      # rãnh thanh cuộn
    'btn_hover': (142, 140, 129),
    'edge_hi': (152, 150, 142),
    'speed': (140, 110, 150),    # thanh Nhanh (tím xám)
    'paper': (205, 200, 178),    # chữ trên gỗ và trên ô đang chọn
    # viền sáng trên thanh phân đoạn
    'bad_hi': (190, 90, 70), 'warn_hi': (225, 185, 95), 'ok_hi': (170, 165, 80), 'tick_hi': (170, 168, 160), 'speed_hi': (170, 140, 180),
}
LED = (UI['bad'], UI['warn'], UI['ok'])

# Thanh chỉ số (HUD v11): máu ô-liu, sức lực hổ phách, ẩn nấp đá sáng, nhanh tím xám
STAT = {'hp': UI['ok'], 'sl': UI['warn'], 'stealth': UI['tick'], 'speed': UI['speed']}

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
