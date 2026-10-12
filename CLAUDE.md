# Vùng Xanh Cuối Cùng — hướng dẫn cho Claude Code

Game chiến thuật ẩn nấp góc nhìn 3/4 (top-down), pixel art, tiếng Việt. Bốn nhân vật: Dương, Hùng, Ny, Sơn.
12 màn, 6 kết thúc, 1 bí mật. Thiết kế màn: `docs/level_design.md`. Mục tiêu trước mắt: build màn 1 chơi được.

## Quy ước bắt buộc
- **Độ phân giải gốc 800×450**, phóng nguyên lần (×2 = 1600×900). Không làm mượt ảnh (nearest-neighbour).
- **Sprite nhân vật 64×64/khung** (chuẩn LPC). Hàng trong sheet gốc LPC: 0 = lên, 1 = trái, 2 = xuống, 3 = phải.
  Các sheet đã dựng trong `assets/` mỗi hàng là MỘT hoạt ảnh; số khung và thứ tự hàng nằm trong file JSON cùng tên ở `data/`.
- **Vũ khí quay mặt sang trái** (đầu nòng bên trái). Nhân vật đi sang phải = lật ngang khung hình.
- **Chân nhân vật** nằm ở y = 60 trong khung 64 (vẽ tại `x-32, y-60`). Sắp xếp vẽ theo y của chân.
- **Vũ khí nạp theo dữ liệu**: `data/weapons.json` (bản v2 ĐÃ CHỐT, 18 món). Mỗi món có `class`, `pose_set`
  (one_hand / shoulder / throw / blade_short / blade_long), `atlas_rect`, `grip`, `muzzle`, `stats`, `anims`.
  Bộ 11 tiểu liên mới chỉ là bản lưu: `data/weapons_v3_smg_backup.json` — không dùng trừ khi được yêu cầu.
- **UI đã chốt là v10 (cyberpunk nhà máy)** — xem `assets/ui/v10_*.png` và token màu ở `tools/locked.py`:
  nền #080A10 lưới ô, khung #121620 có vạch quét, viền #186078, vạch thước #3EECFF, bảng tên hình bình hành
  #6E144A mép #FF3AA8, LED đỏ/vàng/xanh, ô có ngoặc góc, ô đang chọn ngoặc tím hồng.
- **Chữ**: Be Vietnam Pro (`assets/fonts/`, OFL). Chữ pixel nhỏ làm mất dấu tiếng Việt → luôn vẽ chữ ở độ phân giải hiển thị.
- **Ghi công bắt buộc**: sprite nhân vật/Biến Thể và tile lấy từ Liberated Pixel Cup (CC-BY-SA 3.0 / GPL 3.0). Xem `docs/CREDITS.md`.

## Cấu trúc
- `assets/characters/` hoạt ảnh 4 nhân vật (bản C) · `assets/enemies/` 8 loại Biến Thể · `assets/npcs/` Mai, Ông Tư, Bác sĩ Lan, Lính Nhiễm
- `assets/weapons/` sheet hoạt ảnh vũ khí v2 (đi cầm / ngắm / bắn cho từng món), atlas sprite, icon · `assets/items/` 33 icon vật phẩm 16×16
- `assets/fx/` 12 hiệu ứng 64×64 · `assets/maps/` nền màn 1 không nhân vật · `assets/tiles/` tile LPC gốc (rừng, suối, cầu, cây)
- `data/` JSON mô tả mọi sheet · `prototype/build_hub.html` bản chạy thử (sân thử vũ khí) — mở thẳng trên trình duyệt
- `tools/` script Python đã dùng để sinh asset (Pillow, numpy). Đường dẫn trong script trỏ tới `/home/claude/...` của môi trường cũ;
  cần sửa lại nếu muốn sinh lại. Thư viện sprite LPC gốc: https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator

## Việc tiếp theo (màn 1)
Kế hoạch xây dựng đầy đủ (stack, kiến trúc, mốc M0–M15, quyết định cần chốt): `docs/PLAN.md`.
Xem mục "Build màn 1" trong `docs/level_design.md`: lưới va chạm, Biến Thể tuần tra + nón nhìn, đồng hồ phát hiện 3 mức,
ném đá tạo tiếng động, đổi nhân vật 1–4 + chế độ kế hoạch, trigger mục tiêu, nhặt đồ, điểm lưu, màn thắng/thua.
