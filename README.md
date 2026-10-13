# Vùng Xanh Cuối Cùng

Game chiến thuật ẩn nấp góc nhìn 3/4, pixel art, tiếng Việt. Bốn nhân vật Dương, Hùng, Ny, Sơn đi tìm
đường về sau đợt bùng phát; 12 màn, 6 kết thúc, 1 bí mật. Mục tiêu hiện tại: **màn 1 "Đường Mòn Sương" chơi được**.

- Kế hoạch và tiến độ: `docs/PLAN.md` · Thiết kế 12 màn: `docs/level_design.md` · Quy ước art: `docs/ART.md`
- Hướng dẫn cho Claude Code: `CLAUDE.md` · Gói bàn giao gốc: `docs/HANDOFF.md`

## Chạy

Cần Node 22+, Python 3.11+ với Pillow và numpy (chỉ để sinh lại art).

```
npm ci
npm run dev        # http://127.0.0.1:5173 · game 800×450 phóng ×2
npm run build      # dist/ tĩnh, mở được ở GitHub Pages hoặc bất kỳ máy chủ tĩnh nào
npm test           # Vitest
npm run lint && npm run typecheck
```

Phím: `WASD` hoặc mũi tên đi, `Shift` bật/tắt chạy (bấm một lần), `C` xoay tư thế đi / khom / bò, `Space` ném đá, `E` nhặt / hạ gục, `1`–`4` đổi người, `Tab` kế hoạch.

Luật ẩn nấp (kiểu Commandos, hằng số trong `stealth` của `public/data/levels/level1.json`): tiếng bước chân lan Chạy 160 px (10 ô) · Đi 56 px · Khom 16 px · Bò im;
nón nhìn 110° / 176 px, lộ mặt trong vùng gần 72 px là báo động ngay; khom / bò trong bụi thì không bị thấy, bò nằm im ở xa cũng không.

## Art bằng code trên ma trận

Mọi sprite nằm trong các trang atlas 2048×2048 (`public/assets/atlas_N.png`) sinh bởi `art/`:

```
npm run art          # sinh atlas, atlas.json, anims.json
npm run art:check    # kiểm tra chồng lấn, id, vùng, tất định
npm run art:review   # prototype/atlas_review.html và gallery_review.html: mở thẳng để duyệt
```

## Cấu trúc

| Thư mục | Nội dung |
| --- | --- |
| `src/` | mã game TypeScript + Phaser 3: `core/` (atlas, hoạt ảnh, phím), `entities/`, `scenes/`, `ui/` (lớp DOM, token v10) |
| `art/` | nguồn art bằng code (Python): ma trận, bảng màu, ma trận ký tự, nhập sheet cũ, build, check, review |
| `public/` | file sinh ra và tài nguyên tĩnh: atlas, manifest, bản đồ |
| `assets/`, `data/` | sheet và JSON bàn giao, đang được nhập tạm vào atlas; sẽ xóa dần khi `art/` thay thế |
| `prototype/` | trang xem ma trận, gallery hoạt ảnh và sân thử, prototype cũ |
| `tools/` | script sinh asset đời đầu, giữ để đối chiếu |

## Giấy phép

Sprite nhân vật, Biến Thể và tile dẫn xuất từ Liberated Pixel Cup (CC-BY-SA 3.0 / GPL 3.0), font Be Vietnam Pro
(OFL). Xem `LICENSE-ASSETS` và `docs/CREDITS.md`.
