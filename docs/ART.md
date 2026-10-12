# Art bằng code trên ma trận · quy ước

Mọi pixel của game (trừ tile LPC gốc, font và mockup tham chiếu) được sinh bằng code trong `art/` và
đặt lên **ma trận atlas**: các trang `public/assets/atlas_N.png` 2048×2048, mỗi trang là lưới
**128×128 ô 16 px**. Game chỉ biết `id`, không bao giờ biết tọa độ pixel.

## Lệnh

| Lệnh | Việc |
| --- | --- |
| `npm run art` | sinh `atlas_0.png`, `atlas_1.png`, `public/data/atlas.json`, `anims.json`, `atlas.js` |
| `npm run art:check` | kiểm tra chồng lấn, id, vùng, màu UI, tất định (ảnh trên đĩa = sinh lại) |
| `npm run art:review` | gộp viewer/gallery + ảnh thành `prototype/atlas_review.html` (ma trận) và `prototype/gallery_review.html` (gallery + sân thử tương tác), mỗi file mở được ở bất kỳ máy nào |
| `npm run art:view` rồi mở `http://127.0.0.1:8080/prototype/atlas_viewer.html` | xem ma trận, rê chuột xem ô, phát hoạt ảnh. Mở thẳng file cũng được vì viewer đọc `atlas.js` |

Yêu cầu: Python 3.11+, Pillow, numpy. Không sửa tay các file sinh ra; `art:check` sẽ báo lỗi.

## Id

`nhóm/tên/hoạt-ảnh/khung`, chữ ASCII không dấu, gạch nối. Tên tiếng Việt vẫn giữ trong `anims.json` (`name`, `actor`).

| Nhóm | Ví dụ | Neo |
| --- | --- | --- |
| `char/<nhân vật>` | `char/duong/di-xuong/3` | chân (32, 60) trong khung 64 |
| `enemy/<loại>` | `enemy/ke-lang-thang/bi-ha/10`, `enemy/bien-the/vo/2` | chân |
| `npc/<tên>` | `npc/mai/lo-lung/0` | chân |
| `weapon/<id>` | `weapon/pistol/fire/2`, `weapon/pistol/icon`, `weapon/pistol/sprite` | chân / tâm / điểm cầm |
| `melee/<knife\|machete>` | `melee/knife/dam/4` | chân |
| `fx` | `fx/no/5` | tâm (32, 32) |
| `item` | `item/tui-cuu-thuong` | tâm (8, 8) |
| `ui/<thành phần>` | `ui/panel/tl` (A4) | góc trên trái |

Hoạt ảnh = id không có số khung: `char/duong/di-xuong`. `anims.json[id]` cho `frames`, `fps`, `loop`, `anchor`.

## Ma trận và vùng

- Mỗi khung được **cắt viền** theo hộp bao pixel thật, làm tròn lên bội số 16, ghi độ lệch trong
  `spriteSourceSize` và kích thước gốc trong `sourceSize` (chuẩn TexturePacker, Phaser `load.multiatlas` đọc thẳng).
- Mỗi nhóm nằm trong một **vùng** là dải hàng cố định của một trang (bảng trong `art/build.py`), để tọa độ ổn
  định giữa các lần sinh và diff ảnh nhỏ. Trong vùng, khung xếp theo dải (shelf) theo đúng thứ tự id.
- Vùng đầy → `ZoneFull`; mở rộng vùng trong `build.py` hoặc thêm trang `atlas_2.png` (chuẩn N trang, code game
  không đổi).

## Thêm một asset mới

1. **Asset nhỏ** (vũ khí, item, mảnh UI): viết ma trận ký tự, ví dụ `art/items/den_pin.py`:
   ```python
   from pixel import parse
   from palette import MATERIAL as M
   PAL = {'.': None, 'k': M['outline'], 's': M['steel'], 'h': M['steel_hi'], 'y': (255, 240, 160)}
   IMG, MARKS = parse('''
   ....kkkk........
   ...kshhsk.......
   ..kshhhhsk......
   ''', PAL)
   ```
   rồi đăng ký trong `build.py`: `m.place('item/den-pin', IMG, 'items', 'item', anchor=(8, 8), trim=False)`.
2. **Hoạt ảnh**: tạo danh sách khung (ảnh) rồi `place` từng khung với id `…/<i>` và ghi `anims[id]`
   (`Importer._anim` là mẫu).
3. Chạy `npm run art && npm run art:check`, mở viewer kiểm tra, commit cả nguồn lẫn ảnh sinh ra.

Ký tự đặc biệt trong ma trận: `G` điểm cầm, `M` đầu nòng, `A` neo; khai báo trong tham số `markers` của `parse`
để vừa tô màu vừa ghi tọa độ. `pixel.to_text` chuyển sprite có sẵn thành ma trận để port asset cũ.

## Bảng màu

`art/palette.py`: `UI` token v10 (đã chốt), `CHARACTERS` bảng màu 4 nhân vật + Biến Thể, `MATERIAL` vật liệu
vũ khí và item. Nhóm `ui/` chỉ được dùng màu trong `UI`; `art:check` chặn màu lạ.

## Trạng thái nhập tạm

`art/legacy_import.py` đang cắt khung từ các sheet bàn giao trong `assets/` để atlas có đủ khung ngay.
Khi một nhóm được thay bằng nguồn code (A2–A5), bỏ nhóm đó khỏi `Importer.all()` và xóa sheet tương ứng.
Hoạt ảnh trùng giữa 3 sheet nhân vật (8 cặp, pixel giống hệt) chỉ nhập một lần.

## Giấy phép

Sprite nhân vật, NPC, Biến Thể và tile dẫn xuất từ Liberated Pixel Cup: CC-BY-SA 3.0 / GPL 3.0, xem
`docs/CREDITS.md` và `LICENSE-ASSETS`. Atlas sinh ra vì thế cũng theo giấy phép này.
