import math
from PIL import Image, ImageDraw
from icons8 import finish, new, C, STEEL, WOOD, RED, GRN, BLU, GOLDR, PAPER, SKIN, TEAL, PURP

def it_medkit():
    im, d = new(); d.rectangle((1, 4, 14, 13), fill=RED[1]); d.rectangle((1, 4, 14, 5), fill=RED[2]); d.rectangle((5, 2, 10, 4), fill=STEEL[1])
    d.rectangle((6, 6, 9, 11), fill=C(250, 250, 250)); d.rectangle((4, 7, 11, 10), fill=C(250, 250, 250)); d.rectangle((1, 12, 14, 13), fill=RED[0]); return finish(im)
def it_pills():
    im, d = new(); d.rectangle((4, 4, 11, 14), fill=C(236, 236, 228)); d.rectangle((4, 4, 5, 14), fill=C(255, 255, 255)); d.rectangle((3, 1, 12, 4), fill=RED[1])
    d.rectangle((5, 8, 10, 11), fill=BLU[1]); return finish(im)
def it_antidote():
    im, d = new(); d.line([(3, 13), (11, 5)], fill=STEEL[2], width=3); d.line([(4, 12), (9, 7)], fill=TEAL[2], width=1); d.line([(11, 5), (14, 2)], fill=STEEL[1]); d.line([(1, 15), (3, 13)], fill=STEEL[3])
    d.rectangle((9, 8, 11, 10), fill=STEEL[0]); return finish(im)
def it_can():
    im, d = new(); d.rectangle((3, 3, 12, 14), fill=STEEL[1]); d.rectangle((3, 6, 12, 11), fill=RED[1]); d.rectangle((3, 3, 12, 4), fill=STEEL[2]); d.rectangle((5, 7, 10, 10), fill=GOLDR[2]); return finish(im)
def it_water():
    im, d = new(); d.rectangle((5, 1, 10, 3), fill=BLU[0]); d.polygon([(4, 4), (11, 4), (12, 7), (12, 14), (3, 14), (3, 7)], fill=BLU[2]); d.rectangle((4, 7, 11, 13), fill=BLU[1]); d.rectangle((5, 8, 6, 12), fill=C(200, 236, 255)); return finish(im)
def it_noodles():
    im, d = new(); d.rectangle((1, 3, 14, 13), fill=GOLDR[1]); d.rectangle((1, 3, 14, 5), fill=RED[1]); d.ellipse((4, 6, 11, 12), fill=C(250, 236, 180))
    for y in (8, 10): d.line([(5, y), (10, y)], fill=GOLDR[0])
    d.point((8, 7), fill=GRN[1]); return finish(im)
def it_banhmi():
    im, d = new(); d.polygon([(1, 10), (4, 6), (12, 4), (15, 6), (12, 10), (4, 12)], fill=GOLDR[1]); d.line([(4, 7), (12, 5)], fill=GOLDR[2]); d.line([(5, 9), (7, 7), (9, 8), (11, 6)], fill=GRN[1]); return finish(im)
def it_flashlight():
    im, d = new(); d.rectangle((5, 5, 14, 10), fill=STEEL[0]); d.rectangle((5, 5, 14, 6), fill=STEEL[1]); d.polygon([(1, 3), (5, 5), (5, 10), (1, 12)], fill=STEEL[2]); d.rectangle((0, 4, 1, 11), fill=C(255, 240, 160)); d.rectangle((9, 7, 10, 8), fill=RED[2]); return finish(im)
def it_battery():
    im, d = new(); d.rectangle((3, 3, 12, 14), fill=C(40, 44, 56)); d.rectangle((6, 1, 9, 3), fill=STEEL[2]); d.rectangle((4, 9, 11, 13), fill=GRN[1]); d.rectangle((4, 4, 11, 8), fill=C(40, 44, 56)); d.polygon([(8, 4), (6, 8), (8, 8), (7, 12), (10, 7), (8, 7)], fill=GOLDR[2]); return finish(im)
def it_rope():
    im, d = new()
    for r, c in ((6, WOOD[2]), (4, WOOD[1]), (2, WOOD[2])): d.ellipse((8 - r, 8 - r, 7 + r, 7 + r), outline=c, width=2)
    d.line([(13, 9), (15, 14)], fill=WOOD[1], width=2); return finish(im)
def it_crowbar():
    im, d = new(); d.line([(3, 14), (12, 3)], fill=RED[1], width=2); d.line([(12, 3), (14, 2), (15, 4)], fill=RED[1], width=2); d.line([(3, 14), (1, 13)], fill=RED[1], width=2); d.line([(4, 12), (11, 4)], fill=RED[2]); return finish(im)
def it_lighter():
    im, d = new(); d.rectangle((5, 6, 11, 14), fill=BLU[1]); d.rectangle((5, 6, 6, 14), fill=BLU[2]); d.rectangle((5, 4, 11, 6), fill=STEEL[2]); d.polygon([(8, 0), (10, 4), (6, 4)], fill=GOLDR[2]); d.point((8, 2), fill=C(255, 255, 220)); return finish(im)
def it_radio():
    im, d = new(); d.rectangle((4, 4, 11, 15), fill=C(40, 44, 56)); d.rectangle((9, 0, 10, 4), fill=STEEL[1]); d.rectangle((5, 5, 10, 8), fill=GRN[2]); d.point((6, 6), fill=C(255, 255, 255))
    for y in (10, 12): d.line([(5, y), (10, y)], fill=STEEL[0])
    d.point((10, 14), fill=RED[2]); return finish(im)
def it_gasmask():
    im, d = new(); d.ellipse((2, 2, 13, 12), fill=C(60, 70, 60)); d.ellipse((3, 4, 7, 8), fill=TEAL[1]); d.ellipse((8, 4, 12, 8), fill=TEAL[1]); d.point((4, 5), fill=TEAL[2]); d.point((9, 5), fill=TEAL[2])
    d.ellipse((5, 9, 10, 14), fill=STEEL[1]); d.ellipse((6, 10, 9, 13), fill=STEEL[0]); return finish(im)
def it_compass():
    im, d = new(); d.ellipse((1, 1, 14, 14), fill=GOLDR[1]); d.ellipse((3, 3, 12, 12), fill=PAPER[2]); d.polygon([(7.5, 3), (9, 7.5), (7.5, 8), (6, 7.5)], fill=RED[1]); d.polygon([(7.5, 12), (9, 7.5), (6, 7.5)], fill=STEEL[1]); return finish(im)
def it_keycard():
    im, d = new(); d.rectangle((1, 4, 14, 12), fill=C(230, 236, 240)); d.rectangle((1, 4, 14, 6), fill=TEAL[1]); d.rectangle((3, 8, 6, 11), fill=GOLDR[1]); d.line([(8, 8), (12, 8)], fill=STEEL[0]); d.line([(8, 10), (11, 10)], fill=STEEL[1]); return finish(im)
def it_ammo9():
    im, d = new(); d.rectangle((1, 6, 14, 14), fill=GRN[0]); d.rectangle((1, 6, 14, 7), fill=GRN[1]); d.rectangle((4, 9, 11, 11), fill=GOLDR[2])
    for x in (3, 6, 9, 12): d.rectangle((x - 1, 2, x, 6), fill=GOLDR[1]); d.point((x - 1, 2), fill=GOLDR[2])
    return finish(im)
def it_mag():
    im, d = new(); d.polygon([(5, 1), (10, 1), (12, 14), (7, 14)], fill=C(50, 54, 64)); d.line([(5, 1), (10, 1)], fill=STEEL[2]); d.rectangle((6, 0, 8, 1), fill=GOLDR[2]); d.line([(7, 4), (10, 12)], fill=STEEL[1]); return finish(im)
def it_shells():
    im, d = new()
    for k, x in enumerate((2, 6, 10)): d.rectangle((x, 3, x + 3, 11), fill=RED[1]); d.rectangle((x, 11, x + 3, 14), fill=GOLDR[1]); d.line([(x, 3), (x, 10)], fill=RED[2])
    return finish(im)
# --- story items
def it_sketchbook():
    im, d = new(); d.rectangle((2, 1, 13, 14), fill=GRN[1]); d.rectangle((2, 1, 3, 14), fill=GRN[0]); d.rectangle((5, 3, 12, 12), fill=PAPER[2])
    d.line([(6, 10), (8, 6), (10, 9), (11, 5)], fill=C(60, 60, 70)); d.line([(12, 13), (15, 7)], fill=GOLDR[1], width=1); d.point((15, 7), fill=C(40, 40, 40)); return finish(im)
def it_medbag():
    im, d = new(); d.rectangle((1, 5, 14, 14), fill=RED[1]); d.rectangle((1, 5, 14, 6), fill=RED[2]); d.arc((4, 1, 11, 8), 180, 360, fill=C(60, 30, 30), width=2)
    d.rectangle((6, 8, 9, 12), fill=C(255, 255, 255)); d.rectangle((5, 9, 10, 11), fill=C(255, 255, 255)); return finish(im)
def it_dragonfly():
    im, d = new(); d.line([(8, 2), (8, 14)], fill=TEAL[1], width=2); d.ellipse((6, 1, 10, 5), fill=TEAL[2]); d.point((7, 2), fill=RED[2]); d.point((9, 2), fill=RED[2])
    for (a, b) in ((1, 5), (1, 8)): d.polygon([(7, a + 1), (1, a), (1, a + 2), (7, a + 3)], fill=C(180, 230, 250))
    for (a, b) in ((9, 5), (9, 8)): d.polygon([(9, b - 3), (15, b - 4), (15, b - 2), (9, b - 1)], fill=C(180, 230, 250))
    return finish(im)
def it_headband():
    im, d = new(); d.ellipse((1, 4, 14, 12), outline=BLU[1], width=3); d.arc((1, 4, 14, 12), 200, 340, fill=BLU[2], width=1); d.line([(12, 10), (15, 15)], fill=BLU[1], width=2); d.line([(11, 11), (12, 15)], fill=BLU[0], width=2); return finish(im)
def it_shard():
    im, d = new(); d.polygon([(8, 0), (13, 6), (10, 15), (5, 15), (2, 7)], fill=TEAL[1]); d.polygon([(8, 0), (10, 7), (8, 15), (5, 15), (2, 7)], fill=TEAL[2]); d.line([(8, 1), (7, 12)], fill=C(230, 255, 250))
    for (x, y) in ((1, 2), (14, 3), (13, 12)): d.point((x, y), fill=C(200, 255, 240)); return finish(im)
def it_stone_carved():
    im, d = new(); d.polygon([(2, 14), (1, 6), (5, 1), (11, 2), (14, 7), (13, 14)], fill=STEEL[1]); d.polygon([(2, 14), (1, 6), (5, 1), (8, 2), (6, 14)], fill=STEEL[2])
    d.line([(5, 5), (10, 5), (7, 8), (10, 11)], fill=TEAL[2]); d.point((6, 11), fill=TEAL[2]); return finish(im)
def it_hairclip():
    im, d = new(); d.polygon([(1, 8), (6, 4), (6, 12)], fill=TEAL[2]); d.polygon([(14, 8), (9, 4), (9, 12)], fill=TEAL[2]); d.ellipse((6, 6, 9, 10), fill=TEAL[1]); d.line([(2, 13), (13, 13)], fill=STEEL[2])
    d.point((3, 7), fill=C(240, 255, 250)); d.point((12, 7), fill=C(240, 255, 250)); return finish(im)
def it_journal():
    im, d = new(); d.rectangle((2, 1, 13, 14), fill=WOOD[0]); d.rectangle((2, 1, 13, 2), fill=WOOD[1]); d.rectangle((4, 4, 11, 7), fill=GRN[1]); d.point((7, 5), fill=GOLDR[2]); d.rectangle((12, 6, 14, 9), fill=GOLDR[1]); return finish(im)
def it_key():
    im, d = new(); d.ellipse((1, 4, 7, 10), outline=GOLDR[1], width=2); d.line([(7, 7), (14, 7)], fill=GOLDR[1], width=2); d.rectangle((11, 8, 12, 11), fill=GOLDR[1]); d.rectangle((13, 8, 14, 10), fill=GOLDR[1]); d.point((3, 6), fill=GOLDR[2]); return finish(im)
def it_fuse():
    im, d = new(); d.rectangle((3, 5, 12, 10), fill=C(220, 230, 236)); d.rectangle((1, 5, 3, 10), fill=STEEL[2]); d.rectangle((12, 5, 14, 10), fill=STEEL[2]); d.line([(4, 8), (6, 6), (8, 9), (11, 7)], fill=GOLDR[1]); return finish(im)
def it_photo():
    im, d = new(); d.rectangle((1, 2, 14, 13), fill=C(248, 246, 240)); d.rectangle((2, 3, 13, 10), fill=C(120, 170, 200)); d.rectangle((2, 8, 13, 10), fill=GRN[1])
    for k, c in enumerate(((111, 143, 78), (224, 123, 57), (226, 222, 210), (40, 160, 190))): d.rectangle((3 + k * 3, 6, 4 + k * 3, 9), fill=C(*c)); d.point((3 + k * 3, 5), fill=SKIN[1])
    return finish(im)
def it_vial():
    im, d = new(); d.rectangle((5, 1, 10, 3), fill=STEEL[1]); d.rectangle((5, 3, 10, 14), fill=C(220, 230, 236)); d.rectangle((6, 7, 9, 13), fill=RED[1]); d.point((7, 9), fill=RED[2]); d.point((8, 11), fill=C(255, 160, 140)); return finish(im)
def it_notes():
    im, d = new(); d.rectangle((3, 2, 14, 14), fill=PAPER[1]); d.rectangle((1, 1, 12, 13), fill=PAPER[2])
    for y in (4, 6, 8, 10): d.line([(3, y), (10, y)], fill=STEEL[1])
    d.ellipse((7, 8, 11, 12), outline=RED[1]); return finish(im)
def it_dogtag():
    im, d = new(); d.line([(3, 1), (8, 6), (13, 1)], fill=STEEL[1]); d.rectangle((4, 6, 11, 14), fill=STEEL[2]); d.rectangle((4, 6, 5, 14), fill=STEEL[3]); d.line([(6, 9), (10, 9)], fill=STEEL[0]); d.line([(6, 11), (9, 11)], fill=STEEL[0]); return finish(im)

GROUPS = {
 'Y tế': [('Hộp cứu thương', it_medkit, 'Hồi 3 máu cho một người.'), ('Thuốc giảm đau', it_pills, 'Giảm run tay khi ngắm.'), ('Kháng bào tử', it_antidote, 'Chữa nhiễm bào tử từ Kẻ Phun.')],
 'Đồ ăn': [('Đồ hộp', it_can, 'Hồi sức lực.'), ('Nước suối', it_water, 'Hồi sức lực, giảm khát.'), ('Mì gói', it_noodles, 'Nấu ở lửa trại cho cả đội.'), ('Bánh mì', it_banhmi, 'Ăn ngay, hồi ít sức lực.')],
 'Công cụ': [('Đèn pin', it_flashlight, 'Làm choáng Kẻ Bám Trần.'), ('Pin', it_battery, 'Nạp cho đèn pin và drone.'), ('Dây thừng', it_rope, 'Leo xuống vách, trói Biến Thể.'),
            ('Xà beng', it_crowbar, 'Phá cửa, cạy nắp cống.'), ('Bật lửa', it_lighter, 'Đốt lửa, đuổi bầy chuột.'), ('Bộ đàm', it_radio, 'Gọi đồng đội ở xa.'),
            ('Mặt nạ phòng độc', it_gasmask, 'Đi qua mây bào tử.'), ('La bàn', it_compass, 'Định hướng khi sương dày.'), ('Thẻ từ', it_keycard, 'Mở cửa phòng thí nghiệm.')],
 'Đạn': [('Hộp đạn 9mm', it_ammo9, 'Cho súng ngắn, tiểu liên.'), ('Băng đạn 5.56', it_mag, 'Cho súng trường.'), ('Đạn ghém', it_shells, 'Cho súng săn.')],
 'Cốt truyện': [('Sổ phác thảo của Dương', it_sketchbook, 'Những trang vẽ con đường trở về.'), ('Túi y tế đỏ của Ny', it_medbag, 'Không bao giờ rời Ny.'),
               ('Drone Chuồn Chuồn', it_dragonfly, 'Sơn tự lắp từ đồ chơi cũ.'), ('Băng đầu xanh của Hùng', it_headband, 'Quà của em gái Hùng.'),
               ('Mảnh Ký Ức', it_shard, 'Phát sáng khi đến gần Mai.'), ('Đá khắc ký hiệu', it_stone_carved, 'Ai đó đã đánh dấu đường mòn.'),
               ('Kẹp tóc của Mai', it_hairclip, 'Vẫn còn ấm.'), ('Nhật ký kiểm lâm', it_journal, 'Ghi chép của ông Tư.'), ('Chìa khóa kho', it_key, 'Kho của trạm kiểm lâm.'),
               ('Cầu chì máy phát', it_fuse, 'Thiếu nó trạm không có điện.'), ('Ảnh bốn người', it_photo, 'Chụp ngày đầu đi cắm trại.'), ('Mẫu bào tử', it_vial, 'Ny cần phân tích.'),
               ('Ghi chép của Bác sĩ Lan', it_notes, 'Nghiên cứu về Vùng Xanh.'), ('Thẻ bài quân nhân', it_dogtag, 'Của một Lính Nhiễm.')],
}
def icon(fn, k=1):
    im = fn(); return im.resize((16 * k, 16 * k), Image.NEAREST) if k > 1 else im

# ---- v2 redraws: bigger, clearer medical + food silhouettes (full 16x16, 3-4 tone ramps)
def it_medkit():
    im, d = new()
    d.arc((5, 0, 10, 6), 180, 360, fill=C(60, 26, 26), width=2)                       # handle
    d.rounded_rectangle((0, 3, 15, 15), 3, fill=RED[1]); d.rounded_rectangle((0, 3, 15, 8), 3, fill=RED[2])
    d.rectangle((0, 12, 15, 15), fill=RED[0]); d.rounded_rectangle((0, 3, 15, 15), 3, outline=None)
    d.line([(1, 8), (14, 8)], fill=C(120, 24, 30))                                        # zip
    d.rectangle((6, 5, 9, 14), fill=C(255, 255, 255)); d.rectangle((3, 8, 12, 11), fill=C(255, 255, 255))
    d.line([(6, 14), (9, 14)], fill=C(210, 210, 216)); d.line([(12, 11), (3, 11)], fill=C(210, 210, 216))
    d.point((2, 5), fill=C(255, 170, 160)); return finish(im)
def it_pills():
    im, d = new(); d.rectangle((3, 0, 12, 3), fill=RED[1]); d.line([(3, 0), (12, 0)], fill=RED[2]); d.rectangle((4, 4, 11, 15), fill=C(240, 240, 232))
    d.rectangle((4, 4, 5, 15), fill=C(255, 255, 255)); d.rectangle((4, 7, 11, 12), fill=BLU[1]); d.rectangle((6, 8, 9, 11), fill=C(255, 255, 255)); d.rectangle((7, 8, 8, 11), fill=RED[1]); d.rectangle((6, 9, 9, 10), fill=RED[1])
    d.rectangle((10, 4, 11, 15), fill=C(200, 200, 196)); return finish(im)
def it_antidote():
    im, d = new(); d.rectangle((2, 6, 11, 10), fill=C(230, 236, 240)); d.rectangle((3, 7, 9, 9), fill=TEAL[1]); d.point((4, 7), fill=TEAL[2])
    d.rectangle((11, 5, 12, 11), fill=STEEL[1]); d.rectangle((13, 7, 15, 9), fill=STEEL[2]); d.line([(0, 8), (2, 8)], fill=STEEL[3])
    for x in (4, 6, 8): d.point((x, 6), fill=STEEL[0])
    return finish(im)
def it_can():
    im, d = new(); d.ellipse((2, 1, 13, 5), fill=STEEL[2]); d.rectangle((2, 3, 13, 13), fill=STEEL[1]); d.ellipse((2, 11, 13, 15), fill=STEEL[1])
    d.rectangle((2, 5, 13, 11), fill=C(214, 64, 40)); d.rectangle((2, 5, 4, 11), fill=C(240, 110, 80))
    d.ellipse((6, 6, 11, 10), fill=C(250, 214, 120)); d.polygon([(10, 8), (12, 6), (12, 10)], fill=C(250, 214, 120)); d.point((7, 7), fill=C(40, 30, 20))   # fish label
    d.ellipse((5, 2, 10, 4), outline=STEEL[0]); d.rectangle((8, 2, 10, 3), fill=STEEL[3]); return finish(im)
def it_water():
    im, d = new(); d.rectangle((6, 0, 9, 2), fill=BLU[0]); d.line([(6, 0), (9, 0)], fill=BLU[2]); d.rectangle((6, 3, 9, 4), fill=C(200, 230, 250))
    d.polygon([(5, 5), (10, 5), (12, 8), (12, 15), (3, 15), (3, 8)], fill=C(170, 220, 250))
    d.rectangle((3, 9, 12, 12), fill=BLU[1]); d.line([(5, 10), (10, 10)], fill=C(255, 255, 255)); d.line([(4, 6), (4, 14)], fill=C(235, 250, 255))
    d.rectangle((3, 13, 12, 15), fill=C(120, 190, 240)); return finish(im)
def it_noodles():
    im, d = new(); d.polygon([(0, 2), (15, 2), (14, 15), (1, 15)], fill=C(240, 190, 40)); d.rectangle((0, 2, 15, 5), fill=C(214, 44, 40)); d.line([(0, 2), (15, 2)], fill=C(250, 110, 90))
    d.point((3, 3), fill=C(255, 255, 255)); d.point((5, 3), fill=C(255, 255, 255)); d.point((7, 3), fill=C(255, 255, 255))
    d.chord((3, 6, 12, 14), 0, 180, fill=C(250, 250, 244)); d.line([(3, 10), (12, 10)], fill=C(200, 60, 40))     # bowl
    for x in (5, 7, 9): d.arc((x - 1, 6, x + 2, 11), 180, 360, fill=C(250, 226, 150))                             # noodles
    d.point((10, 8), fill=GRN[1]); d.point((6, 8), fill=C(220, 90, 70)); return finish(im)
def it_banhmi():
    im, d = new(); d.polygon([(0, 9), (3, 5), (11, 3), (15, 5), (13, 9), (4, 12)], fill=C(214, 150, 70)); d.line([(3, 5), (11, 3), (15, 5)], fill=C(240, 190, 110))
    for x in (5, 8, 11): d.line([(x, 5), (x + 1, 4)], fill=C(250, 214, 150))
    d.polygon([(1, 10), (13, 7), (14, 9), (4, 13)], fill=C(250, 236, 200))                 # cut face
    d.line([(2, 10), (13, 8)], fill=GRN[1]); d.line([(3, 11), (13, 9)], fill=C(200, 70, 60)); d.point((7, 10), fill=C(250, 150, 80))
    return finish(im)
GROUPS['Y tế'] = [('Túi cứu thương', it_medkit, 'Hồi 3 máu cho một người.'), ('Thuốc giảm đau', it_pills, 'Giảm run tay khi ngắm.'), ('Kháng bào tử', it_antidote, 'Chữa nhiễm bào tử từ Kẻ Phun.')]
GROUPS['Đồ ăn'] = [('Cá hộp', it_can, 'Hồi sức lực.'), ('Nước suối', it_water, 'Hồi sức lực, giảm khát.'), ('Mì gói', it_noodles, 'Nấu ở lửa trại cho cả đội.'), ('Bánh mì', it_banhmi, 'Ăn ngay, hồi ít sức lực.')]
