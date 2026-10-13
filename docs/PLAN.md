# Vùng Xanh Cuối Cùng · Kế hoạch xây dựng

Kế hoạch này được lập sau khi đọc toàn bộ gói bàn giao (`CLAUDE.md`, `README.md`, `docs/level_design.md`,
`docs/CREDITS.md`, 10 file `data/*.json`, 38 file `assets/`, 26 script `tools/`, `prototype/build_hub.html`).
Mục tiêu trước mắt theo `CLAUDE.md`: **màn 1 "Đường Mòn Sương" chơi được**, sau đó mở rộng ra 12 màn.

Thứ tự thực hiện: **Giai đoạn A** refactor toàn bộ art thành "vẽ bằng code, ánh xạ lên ma trận 2048×2048"
(mục 3) → **Giai đoạn B** dựng game màn 1 trên nền art đó (mục 4) → **Giai đoạn C** 12 màn (mục 5).

---

## 1. Hiện trạng gói bàn giao

### 1.1 Đã có (dùng được ngay)

| Nhóm | Nội dung | Ghi chú kỹ thuật |
| --- | --- | --- |
| Nhân vật | 3 sheet 64×64: `anim_core` (30 hàng, 228 khung), `anim_more` (24 hàng, 183 khung), `anim_actions` (28 hàng, 248 khung) cho Dương, Hùng, Ny, Sơn + Biến Thể cơ bản | Mỗi hàng = 1 hoạt ảnh; `[tên, hoạt ảnh, số khung]` trong JSON cùng tên. Sheet rộng 704 = tối đa 11 khung/hàng |
| Kẻ thù | `wanderer_walk_knockdown.png` (đi trái 8 + bị hạ 11) cho màn 1; `zombies.png` 6 loại × 4 hoạt ảnh, 209 khung (màn 3–8) | Kẻ Lang Thang màn 1 chỉ có hướng trái, lật ngang để đi phải |
| NPC | Mai, Ông Tư, Bác sĩ Lan, Lính Nhiễm (`npcs.png`, 20 hàng, 149 khung) | Mai có "Lơ lửng", "Hiện ra" cho ánh sáng xanh |
| Vũ khí | `weapons.json` v2 chốt 18 món; sheet hoạt ảnh 54 hàng, 288 khung (đi/ngắm/bắn); atlas 479×12, icon; dao ngắn + dao rựa (`melee_anim`, 59 khung) | Mỗi vũ khí ≤ 34×12 px, rất hợp để định nghĩa bằng ma trận ký tự |
| Vật phẩm | 33 icon 16×16, thứ tự icon = thứ tự trong `items.json` | |
| Hiệu ứng | 12 FX 64×64, 98 khung (`fx.json`) | Phần lớn là hình học (vòng, khói, lửa) → sinh bằng hàm theo thời gian |
| UI | 5 mockup v10 1600×900 + token màu và hàm vẽ khung/tab/ô/thanh trong `tools/locked.py` | `locked.py` đã là "UI bằng code": frame, title, slot, card, tabs, choice, bar, scrollbar |
| Bản đồ | `level1_bridge_bg.png` 800×450 | Sinh bằng `tools/lpcscene.py`: lưới 25×15 tile 32 px, autotile từ `terrain-v7.png` |
| Font | Be Vietnam Pro 4 độ đậm (OFL) | |
| Prototype | `build_hub.html`: vòng lặp canvas, vẽ khung LPC, y-sort, lật hướng, Biến Thể tuần tra + nón nhìn thô | Tham chiếu cho renderer |

Tổng cộng **1.481 khung 64 px** (1.521 nếu thêm "Đi lên" cho 4 nhân vật và Biến Thể). Một trang ma trận
2048×2048 chứa tối đa 1.024 ô 64 px khi chưa cắt viền.

### 1.2 Còn thiếu (phải làm hoặc quyết định)

1. **Art đang là ảnh tĩnh rải trong 9 sheet + 5 atlas**, mỗi sheet một quy ước; script sinh trỏ đến `/home/claude/...` và cần thư viện LPC gốc không có trong gói. Không sinh lại được từ repo.
2. **Chưa có mã game thật**: chưa có build tool, lưới va chạm, AI, HUD trong game, lưu game.
3. **Bản đồ màn 1 chỉ có 1 màn hình** trong khi thiết kế cần 4 khu vực, 8–10 phút chơi.
4. **Thiếu hoạt ảnh "Đi lên"** cho 4 nhân vật chính và Biến Thể.
5. **Không có âm thanh.**
6. **Chưa có kịch bản hội thoại và dữ liệu màn** ở dạng máy đọc được.
7. Tuyến Mai bệnh nhân số 0 và bí mật của Sơn chưa đối chiếu kịch bản gốc (không ảnh hưởng màn 1).

---

## 2. Quyết định kỹ thuật

### 2.1 Art: mọi pixel sinh từ code, ánh xạ lên ma trận

- **Ma trận** = texture **2048×2048**, chia lưới **128×128 ô đơn vị 16 px**. Mọi asset chiếm một hình chữ nhật ô
  `(col, row, w, h)` tính theo đơn vị 16 px: nhân vật 4×4 ô, item 1×1, mảnh UI 1×1 đến 4×4, FX 4×4.
  Chọn 2048 vì đây là cỡ texture mọi thiết bị WebGL đều hỗ trợ (kể cả điện thoại 2010–2013), là lũy thừa của 2
  nên GPU dùng bộ nhớ hiệu quả (16 MB/trang), và là mặc định của Phaser, PixiJS, Godot, Unity. 4096 chỉ an toàn
  từ khoảng 2014, 2560 không phải lũy thừa của 2. Độ phân giải màn hình **giữ nguyên 800×450 phóng ×2**.
- **Một chuẩn, N trang**: `atlas_0.png`, `atlas_1.png`, … cùng định dạng, thêm trang khi cần. Bắt đầu với 2 trang:
  trang 0 = 4 nhân vật + Biến Thể + Kẻ Lang Thang (927 ô 64 px, đầy 90 % nếu không cắt viền),
  trang 1 = NPC, vũ khí, dao, FX, item, UI (≈ 600 ô + UI, trống ≈ 25–35 %).
- **Cắt viền khung (trim) ngay từ A1**: mỗi khung chỉ lưu hộp bao quanh pixel thật (nhân vật đứng ≈ 24×50 thay vì
  64×64) kèm độ lệch neo trong manifest; tiết kiệm 40–50 % chỗ, nhờ đó trang 0 còn dư cho hoạt ảnh các màn sau.
- **Manifest** `data/atlas.json` sinh tự động: `id → {page, col, row, w, h, anchor, …}`. Code game chỉ biết `id`,
  không bao giờ biết tọa độ pixel.
- **Nguồn art là code Python** trong thư mục `art/` (Pillow, numpy, tái dùng 26 script hiện có), chạy bằng
  `npm run art`. Ba kiểu nguồn:
  1. **Ma trận ký tự + bảng màu** cho asset nhỏ (vũ khí, item, icon, mảnh UI): mỗi ký tự = 1 màu trong palette,
     ký tự đặc biệt đánh dấu điểm cầm `G`, đầu nòng `M`, neo `A`. `weapons.json` (`atlas_rect`, `grip`, `muzzle`)
     được **sinh ra từ ma trận**, không còn sửa tay.
  2. **Hàm vẽ theo tham số** cho FX, UI 9-slice, bản đồ (autotile), bóng đổ, viền: `draw(t, palette) → ảnh`.
  3. **Rig ghép lớp** cho nhân vật: thân/đầu/tóc/áo/quần/giày lấy từ LPC theo cấu hình, ánh xạ bảng màu từng
     nhân vật (`COL` trong `crawl.py` đã có), rồi ghép pose. Giữ LPC làm lớp gốc vì tự vẽ 1.500 khung người
     bằng ma trận không khả thi về chất lượng; xem câu hỏi 1 mục 6.
- **Hoạt ảnh là dữ liệu sinh bằng code**: `data/anims.json` ghi cho mỗi hoạt ảnh danh sách `id` khung, fps,
  lặp hay không, neo chân (y = 60), sự kiện theo khung (bước chân, chạm đòn, thả đá), quy tắc lật. Hoạt ảnh
  "thủ tục" (LED nháy, vạch quét, ngoặc nhấp nháy, vòng tiếng động nở ra) là hàm theo thời gian trong game,
  không lưu khung.
- **UI trong game dùng đúng mảnh từ ma trận**: khung, nút, tab, ô, thanh là 9-slice hoặc sprite từ `atlas_1`,
  hiển thị qua CSS `border-image` + `image-rendering: pixelated` trên lớp DOM; chữ Be Vietnam Pro vẫn là DOM nét.
  Nhờ vậy **100 % pixel đến từ ma trận**, chỉ có chữ là vector.

### 2.2 Stack game: **Phaser 3 + TypeScript + Vite**, HUD bằng DOM overlay

- Asset, prototype, mockup đã là web; chạy, test (Vitest) và chụp màn hình (Playwright) được ngay trong
  phiên Claude Code; deploy GitHub Pages không cần export. Godot không kiểm thử tự động được trong môi trường này.
- Phaser nạp 2 trang ma trận + `atlas.json` thành texture atlas; `anims.json` → `AnimationManager`.
- Cấu hình: `800×450, zoom 2, pixelArt, roundPixels, Scale.FIT`, nền `#080A10`.
- Chữ tiếng Việt chỉ vẽ trên DOM ở độ phân giải hiển thị (quy ước `CLAUDE.md`).

### 2.3 Kiến trúc thư mục (sau giai đoạn A và B0)

```
/
├─ index.html · package.json · vite.config.ts · tsconfig.json
├─ art/                       ← NGUỒN art bằng code (Python)
│  ├─ matrix.py               lớp Matrix 128×128 ô (trang 2048): cấp phát vùng, trim, đặt asset, kiểm tra chồng lấn, xuất PNG + JSON
│  ├─ palette.py              bảng màu chung: token UI v10 (từ locked.py) + bảng màu nhân vật + vật liệu
│  ├─ pixel.py                parser ma trận ký tự → ảnh; ký tự đặc biệt G/M/A → điểm neo
│  ├─ characters/             rig LPC: parts.py (cấu hình bộ phận), rig.py (ghép lớp), anims.py (danh sách pose)
│  ├─ enemies/                8 loại Biến Thể: tint + lớp phủ ma trận (vỏ, bụng, chuột…)
│  ├─ npcs/                   Mai, Ông Tư, Bác sĩ Lan, Lính Nhiễm
│  ├─ weapons/                18 vũ khí + 2 dao, mỗi món 1 file ma trận ký tự; poses.py ghép vào tay
│  ├─ items/                  33 item, mỗi item 1 ma trận 16×16
│  ├─ fx/                     12 FX = hàm draw(t)
│  ├─ ui/                     panel, button, tab, slot, bar, led, scrollbar, dialog, cursor, keycap (9-slice)
│  ├─ maps/                   autotile LPC (từ lpcmap/lpcscene), xuất nền + mask va chạm
│  ├─ build.py                lệnh chính: sinh atlas_0/1.png, atlas.json, anims.json, weapons.json, items.json
│  └─ check.py                kiểm tra: không chồng lấn, mọi id tồn tại, màu UI chỉ từ token, tất định (hash)
├─ public/
│  ├─ assets/atlas_0.png · atlas_1.png · maps/ · fonts/ · tiles/ (LPC gốc giữ riêng, không vào ma trận)
│  └─ data/atlas.json · anims.json · weapons.json · items.json · levels/ · dialogue/
├─ src/                       mã game TypeScript (xem B0–B6)
│  ├─ core/   atlas.ts (nạp ma trận) · anims.ts · events.ts · input.ts · save.ts
│  ├─ world/  CollisionGrid · Triggers · Pickups
│  ├─ entities/ Actor · Player · Squad · Enemy · Npc · Rock
│  ├─ stealth/ VisionCone · Noise · Detection · PlanMode
│  ├─ scenes/ Boot · Preload · Level · Result · Pause
│  ├─ ui/     hud.ts · dialogue.ts · menus.ts · tokens.css (border-image từ atlas_1)
│  └─ levels/ level1.ts
├─ docs/      level_design.md · CREDITS.md · PLAN.md · ART.md (quy ước ma trận, cách thêm asset)
├─ tools/     script cũ, giữ để đối chiếu cho đến khi art/ thay thế hết rồi xóa
└─ prototype/ build_hub.html (tham chiếu) · atlas_viewer.html (xem ma trận, soi từng ô)
```

### 2.4 Quy ước code bắt buộc (bám `CLAUDE.md`)

- Code game chỉ tham chiếu asset bằng `id` dạng `nhóm/tên/hoạt-ảnh/khung` (ví dụ `char/duong/di-xuong/3`,
  `weapon/pistol/icon`, `ui/panel/tl`). Không hard-code tọa độ.
- Vẽ actor với neo chân `(32, 60)`, `depth = y` chân. Hướng phải = `flipX` của khung hướng trái.
- `weapons.json`, `items.json`, `anims.json`, `atlas.json` là **file sinh**, không sửa tay; sửa ở `art/`.
- Màu UI chỉ từ `art/palette.py` (token v10). `art/check.py` chặn màu lạ.
- Mọi chuỗi hiển thị là tiếng Việt có dấu, nằm trong `data/` hoặc `src/ui/strings.ts`.
- Mỗi lần đổi art: chạy `npm run art && npm run art:check`, commit cả nguồn `art/` lẫn ảnh sinh ra.

---

## 3. Giai đoạn A · Refactor art thành code trên ma trận (các bước đầu)

Mỗi bước có tiêu chí nghiệm thu. Ước lượng theo ngày làm việc với Claude Code.

### A1 · Dựng ma trận 2048×2048 và pipeline (1 ngày)

- [x] `art/matrix.py`: lớp `Matrix(page, 128, 128)`; `alloc(w, h, zone)` cấp phát theo vùng; `place(id, img, anchor)`;
      cắt viền khung (trim) và ghi độ lệch neo; phát hiện chồng lấn; xuất `atlas_{page}.png` + `atlas.json`.
- [x] Phân vùng cố định theo hàng đơn vị 16 px (để tọa độ ổn định giữa các lần sinh, tránh đổi hash vô cớ), tính
      cho trường hợp chưa trim, mỗi dải 4 hàng = 32 khung 64 px:
      trang 0: hàng 0–83 bốn nhân vật (21 dải, 642 khung kể cả "Đi lên"), 84–95 Biến Thể + Kẻ Lang Thang (3 dải),
      96–123 sáu loại Biến Thể màn 3–8 (7 dải), 124–127 dự phòng;
      trang 1: hàng 0–19 NPC (5 dải), 20–55 vũ khí (9 dải), 56–63 dao (2 dải), 64–79 FX (4 dải), 80–83 item + icon
      vũ khí, 84–107 UI (6 dải), 108–127 dự phòng (5 dải). Sau khi trim, phần dự phòng tăng lên đáng kể.
- [x] `art/pixel.py`: parser ma trận ký tự; `art/palette.py`: token v10 + bảng màu nhân vật.
- [x] `art/build.py`, `art/check.py`, `npm run art`, `npm run art:check`; `prototype/atlas_viewer.html` xem ma trận,
      rê chuột hiện `id`, tọa độ ô, neo.
- [x] **Nhập tạm** toàn bộ sheet hiện có vào ma trận (cắt khung từ 9 sheet theo JSON cũ) để game chạy được ngay
      bằng ma trận trong khi A2–A5 thay dần từng nhóm bằng nguồn code.
- [x] `docs/ART.md`: quy ước ma trận, cách thêm 1 asset mới trong 5 phút.

**Nghiệm thu (đạt 2026-10-12)**: `npm run art` sinh 2 trang + `atlas.json` với 1.482 khung (1.413 khung hoạt ảnh sau
khi bỏ 8 cặp trùng, 33 item, 18 icon + 18 sprite vũ khí), 194 hoạt ảnh; `art:check` xanh và tất định; viewer soi được
từng ô và phát hoạt ảnh. Nhờ trim, vùng nhân vật dùng 46 %, các vùng khác 31–64 %.

### A2 · Set lại sprite nhân vật, NPC, Biến Thể bằng rig code (3 ngày)

- [ ] Khôi phục pipeline LPC: biến môi trường `LPC_ROOT`, script `art/characters/fetch_lpc.sh` clone generator,
      bỏ mọi đường dẫn `/home/claude`.
- [ ] `art/characters/parts.py`: mỗi nhân vật = cấu hình bộ phận LPC + bảng màu (thân, tóc, áo, quần, giày, phụ kiện:
      băng đầu Hùng, túi đỏ Ny, ba lô Sơn). Đổi màu áo = sửa 1 dòng, sinh lại toàn bộ khung.
- [ ] `art/characters/anims.py`: danh sách pose cho 4 người, gộp 3 sheet cũ thành một bảng duy nhất; **thêm "Đi lên"**
      và "Đứng yên" 4 hướng; các pose vẽ riêng (bò, nấp, hạ gục, ném đá, băng bó, mở khóa, phá cửa) port từ
      `anim2.py`, `crawl.py`, `knock.py`, `melee.py`, `polish.py` thành hàm có tham số.
- [ ] `art/enemies/`: Biến Thể cơ bản = rig người + tint; 7 loại còn lại = tint + lớp phủ ma trận (vỏ cứng, bụng
      phình, chuột) port từ `zombies.py`; Kẻ Lang Thang có đủ 4 hướng đi.
- [ ] `art/npcs/`: 4 NPC port từ `npcs.py`; Mai thêm pose "Lơ lửng" phát sáng xanh (glow sinh bằng hàm).
- [ ] So khớp pixel với sheet cũ cho các pose đã có (chênh lệch chỉ do sửa chủ ý), ghi vào `check`.
- [ ] **Bản review LPC** `prototype/review_lpc.html`, sinh tự động mỗi lần `npm run art`, để chủ dự án duyệt mắt:
      1. Mỗi nhân vật một trang: bảng bộ phận LPC đã chọn (thân, tóc, áo, quần, giày, phụ kiện) kèm tên file gốc
         trong LPC và tác giả (phục vụ `CREDITS.md`), bảng màu trước/sau khi ánh xạ.
      2. Mỗi hoạt ảnh một hàng: **khung cũ (sheet bàn giao) đặt cạnh khung mới (sinh từ rig)**, phóng ×3, ô nào
         lệch pixel thì tô viền đỏ và ghi số pixel khác; nút phát để xem hoạt ảnh chạy ở 1× và 2×.
      3. Hoạt ảnh mới chưa có bản cũ ("Đi lên", "Đứng yên") hiện 4 hướng cạnh nhau để kiểm tra dáng và màu.
      4. Trang tổng: lưới 4 nhân vật × mọi hoạt ảnh, đánh dấu ✔ đã duyệt / ✖ cần sửa, xuất danh sách cần sửa ra
         `docs/review/lpc_<ngày>.md` để ghi chú và đối chiếu lần sau.
      Biến Thể và NPC dùng cùng trang review.

**Nghiệm thu**: bản review LPC được chủ dự án duyệt ✔ toàn bộ; sau đó mới xóa 6 sheet nhân vật/NPC/kẻ thù cũ,
game vẫn chạy từ `atlas_0`; có "Đi lên"; đổi màu áo Dương trong `parts.py` → sinh lại → thấy ngay trong review.

### A3 · Set lại vũ khí, dao, item bằng ma trận ký tự (2 ngày)

- [ ] Chuyển 18 vũ khí v2 từ `weapons_db2.py` sang 18 file ma trận ký tự `art/weapons/*.txt` (đầu nòng bên trái),
      đánh dấu `G` (tay cầm), `M` (đầu nòng) ngay trong ma trận. Bộ 11 tiểu liên v3 chuyển sang `art/weapons/backup/`,
      không build.
- [ ] `art/weapons/poses.py`: 5 `pose_set` (one_hand, shoulder, throw, blade_short, blade_long) = hàm ghép vũ khí vào
      tay theo khung (port `weapons_build3.py`, `melee.py`), sinh 54 hoạt ảnh đi/ngắm/bắn + 8 hoạt ảnh dao.
- [ ] Icon vũ khí (×2 có bóng) và atlas sprite sinh từ cùng ma trận; **`weapons.json` sinh tự động** với
      `atlas_rect`, `grip`, `muzzle`, giữ nguyên `stats` và `anims` từ file cấu hình `art/weapons/stats.py`.
- [ ] 33 item → 33 ma trận 16×16 trong `art/items/`, nhóm và mô tả trong `art/items/catalog.py` → sinh `items.json`.
- [ ] Kiểm tra: mọi vũ khí đúng kích thước cũ ±1 px, điểm cầm không đổi, so khớp với `weapons_atlas_v2.png`.

**Nghiệm thu**: xóa 5 ảnh vũ khí và `item_icons.png` cũ; `weapons.json` sinh ra bằng với bản chốt v2 về id, stats,
grip, muzzle; prototype kho vũ khí chạy từ `atlas_1`.

### A4 · Set lại khung thành phần UI v10 (2 ngày)

- [x] `art/ui/components.py`: port 8 hàm trong `locked.py` thành bộ thành phần 9-slice và sprite: **Panel** (khung vạch quét, viền
      teal, vạch thước, LED), **Button** (thường / rê / nhấn / khóa), **Tab** hình bình hành (thường / đang chọn),
      **Slot** ngoặc góc (thường / đang chọn tím hồng), **Card**, **Choice** (dòng lựa chọn), **Bar** phân đoạn
      (4 màu HP/SL/Ẩn nấp/Nhanh), **Scrollbar**, **Title tab** bình hành, **Dialog** (hộp thoại + khung chân dung),
      **Keycap** Q/W/E/R/1–4, **Toggle**, **Cursor**, **Minimap frame**, dấu `?` `!`.
- [x] 34 thành phần vào vùng `ui` của atlas với `slice`/`outset` trong `atlas.json`; glyph ?, !, ✔, con trỏ là ma trận ký tự; màu chỉ từ `palette.UI` (check chặn màu lạ).
- [x] `src/ui/v10.css` + `src/ui/sprites/*.png` sinh từ build (`art/ui/css.py`): biến CSS token, lớp `.v10-panel`, `.v10-button-*`, `.v10-tab-*`, `.v10-slot`, `.v10-card`, `.v10-choice`, `.v10-seg-*`, `.v10-keycap`… dùng `border-image`. Vì CSS không cắt vùng trong atlas nên sprite được cắt ra từ trang atlas (pixel giống hệt), `--px` = 1 px game do JS đặt theo cỡ cửa sổ.
- [x] Trang `prototype/ui_kit.html` trưng bày mọi thành phần ở ×2.

**Nghiệm thu (đạt 2026-10-12)**: HUD trong game dựng từ thành phần + chữ DOM (B5), bố cục khớp `v10_hud.png`. Chưa chồng pixel lên mockup.

### A5 · Code animation cho từng asset (2 ngày)

- [ ] `art/anims.py` → `data/anims.json`: mỗi hoạt ảnh `{id, frames[], fps, loop, anchor, flip, events}`;
      fps mặc định: đi 10, chạy 12, đòn 14, bị hạ 11 khung ở 11 fps, nghe ngóng 6; `events`: bước chân (khung 2, 6),
      thả đá (khung 5), chạm đòn (khung 3), ngã xong (khung cuối).
- [ ] Hoạt ảnh FX = hàm `draw(t)` trong `art/fx/`: vòng tiếng động, nổ, khói, bào tử, chập điện, nước bắn, bụi, sét,
      hồi máu, drone quét, bị phát hiện; sinh 8–10 khung, đồng thời xuất tham số để game vẽ thủ tục khi cần mượt hơn.
- [ ] Hoạt ảnh UI thủ tục trong `src/ui/motion.ts`: LED nháy theo trạng thái phát hiện, vạch quét trôi, ngoặc ô đang
      chọn nhấp nháy, thông báo trượt vào, thanh phân đoạn đầy dần, nón nhìn đổi màu theo mức.
- [ ] `src/core/anims.ts`: nạp `anims.json` vào Phaser `AnimationManager`, phát `events` qua `EventBus`.
- [ ] Viewer hoạt ảnh trong `atlas_viewer.html`: chọn id, xem phát ở 1×/2×, hiện sự kiện theo khung.

**Nghiệm thu**: mọi hoạt ảnh trong 3 sheet cũ + NPC + Biến Thể + vũ khí + FX phát được từ `anims.json`; sự kiện
bước chân bắn đúng khung.

### A6 · Chốt pipeline, dọn dẹp, tối ưu (1 ngày)

- [ ] CI: job `art` chạy `build` + `check` và so hash với ảnh đã commit (chống chỉnh tay ảnh sinh ra).
- [ ] Xóa `assets/characters|enemies|npcs|weapons|items|fx` và `tools/` cũ sau khi `art/` thay thế đủ; cập nhật
      `CLAUDE.md`, `CREDITS.md`, `ART.md`.
- [ ] Đo bộ nhớ GPU và thời gian nạp trên điện thoại tầm trung; nếu cần, gom về 1 trang nhờ trim.
- [ ] Bản đồ: `art/maps/` port `lpcmap.py`/`lpcscene.py`, xuất nền màn 1 + mask va chạm (chuẩn bị cho B1).

**Nghiệm thu**: clone repo mới, `npm run art` tái tạo byte-giống ảnh đã commit; không còn ảnh tĩnh nào ngoài tile LPC
gốc, font và mockup tham chiếu.

Tổng giai đoạn A: **~11 ngày làm việc**.

---

## 4. Giai đoạn B · Màn 1 chơi được

### B0 · Khởi tạo game (0.5 ngày)

- [x] Vite 7 + TypeScript 5.9 + Phaser 3.90; ESLint, Prettier, Vitest 3; script `dev`, `build`, `test`, `lint`, `typecheck`, `art`.
- [x] `core/atlas.ts` nạp N trang qua `load.multiatlas`; `core/anims.ts` đăng ký `anims.json` (neo chân đi theo khung nhờ `anchor` trong manifest); `@font-face` Be Vietnam Pro.
- [x] Scene `Preload` (thanh nạp v10) → `Level` vẽ nền cầu và Dương đi 4 hướng từ ma trận; `entities/Actor` (lật, depth = y), `entities/Player` (3 tư thế, trượt dọc tường).
- [x] GitHub Actions: art:check + lint + typecheck + test + build; deploy GitHub Pages khi push `main`. `scripts/bundle_artifact.py` đóng gói `dist/` thành trang artifact để xem trực tiếp.
- [x] Viết lại `README.md` thành README dự án; nội dung bàn giao cũ → `docs/HANDOFF.md`.

**Nghiệm thu (đạt 2026-10-12)**: build chạy trong Chromium, Dương đi WASD trên nền cầu, chữ tiếng Việt nét trên lớp DOM; test Vitest 4/4, lint và typecheck xanh. Thứ tự đã đổi: B0–B2 làm trước A2–A5 vì game chỉ phụ thuộc id trong atlas.

### B1 · Nền tảng thế giới (2 ngày)

- [x] Bản đồ màn 1: 50×30 tile (1600×960) sinh từ `art/maps/level1.py` (autotile LPC port từ tools/), 4 khu: trại với đường mòn số 8, rừng thông dày, đầu cầu, bên kia suối lên lối ra; cây/bụi/lều/củi là sprite `env/*` trong atlas, game xếp lớp theo y; nền có hậu kỳ bình minh, sprite môi trường cùng tông màu. Camera cuộn theo thủ lĩnh.
- [x] UI v11 "đá và gỗ" (2026-10-13): token và 9-slice vẽ lại theo đá/gỗ Cainos, HUD dưới gộp thành một dải 64 px (Đội 4 thẻ ngang | Hành động | Ba lô) không chồng nhau; 4 vật phẩm màn 1 vẽ bằng code kiểu Cainos trong `art/items.py`, 29 icon bàn giao còn lại qua `cainos_grade`.
- [x] Hệ màu chốt theo Cainos "Pixel Art Top Down - Basic" (2026-10-13): nền cỏ, cây tán tròn, bụi, đá, thùng, biển lấy thẳng từ `assets/tiles/cainos/`; mọi sprite LPC (nhân vật, Biến Thể, NPC, thông, đất, nước, cầu, trang trí) kéo về hệ màu đó bằng `art/maps/grade.py:cainos_grade` (xanh lá → ô-liu 56–68°, lam → teal xám, da/gỗ giữ ấm, dải sáng nén 0.2–0.65); bỏ split-tone bình minh, chỉ còn vệt nắng nhẹ.
- [x] Làm đẹp theo moodboard (2026-10-13): nền cỏ sạch + mảng cỏ tối dưới rừng dày; cây hai cỡ đồng bộ (thông 154–189 px, tán tròn LPC ghép tán + thân ~118 px); đá, gỗ đổ, hoa, nấm, sậy ven suối (nướng vào nền, mật độ thấp); cỏ cao = cụm bụi rải elip, ô `o` núp được, đặt có chủ ý ở lối tiếp cận cầu và lối ra; mặt nước là lớp riêng `level1_water.png` 3 khung (ô sóng cuộn dọc) phát 3 fps trong game, súng chỉ đặt trọn trong nước, cầu vẽ vào cả khung nước.
- [x] `CollisionGrid` 16 px trong `levels/level1.json` (`.` `#` `o` `~` `=`), kèm `level1_mask.png` để soi; test: cầu là lối duy nhất qua suối, BFS từ trại tới lối ra, mọi điểm đặt đứng được.
- [x] Di chuyển trượt dọc tường; 4 tư thế kiểu Commandos Chạy / Đi / Khom / Bò (96 / 58 / 34 / 18 px/s); `Shift` bật/tắt Chạy (bấm một lần), `C` xoay Đi → Khom → Bò.
- [x] Y-sort actor và vật thể môi trường bằng depth = y chân; debug overlay F3 vẽ lưới va chạm (nón nhìn, vòng tiếng động thêm ở B2).
- [ ] Hoạt ảnh "Đi lên" (việc A2, cần clone LPC); tạm dùng "Chạy lên" chậm.
- [x] Tư thế Khom có hoạt ảnh riêng: `khom-trai`, `khom-xuong`, `khom-len` dẫn xuất bằng code từ khung đi (ép chân, hạ thân) trong `art/legacy_import.crouch_anims`; A2 thay bằng pose LPC thật nếu cần.

**Nghiệm thu (đạt 2026-10-12, trừ "Đi lên")**: đi hết 4 khu trong build Chromium, không lọt nước, cầu là lối duy nhất (test), cây và bụi che người theo depth.

### B2 · Lõi ẩn nấp (3 ngày)

- [x] `Enemy` FSM (`src/entities/Enemy.ts`): Tuần tra (quay đầu nghe ngóng mỗi 4 s) → Nghi ngờ → Điều tra (3 s) → Báo động (30 px/s) →
      Mất dấu → Tuần tra; Bị hạ.
- [x] `VisionCone` 100°, 144 px, raycast qua ô `#`; vùng gần 64 px: lộ mặt là báo động ngay (Commandos); Khom/Bò trong ô bụi `o` thì không bị thấy; Bò nằm im ở vùng xa không bị thấy; mắt mở cả khi đứng nghe. Vẽ nón hai vùng bị cắt bởi vật chắn, màu theo mức.
- [x] `Detection` 3 mức (test): 0–30 % Ẩn mình, 30–99 % Nghi ngờ (`?`), 100 % Báo động (`!` + FX); hệ số tư thế
      Chạy 1.4 / Đi 1.0 / Khom 0.55 / Bò 0.25; tự giảm 0.3/s khi ra khỏi nón.
- [x] `Noise`: ném đá (parabol, vòng 120 px, FX tiếng động); tiếng bước chân theo tư thế cho cả đội: Chạy 160 px (10 ô, nghe được ngoài tầm nhìn) / Đi 56 px / Khom 16 px / Bò im; Biến Thể đi điều tra.
- [x] Hạ từ sau (Dương): sau lưng 20 px, ngoài nón, phím W; nằm 30 s rồi dậy (cấu hình trong level JSON).
- [x] Bị tóm → hộp "Bị phát hiện" trên lớp DOM, Enter nạp lại màn (điểm lưu thật ở B4). Mọi hằng số nằm trong `stealth` của `levels/level1.json` (sinh từ `art/maps/level1.py`). Dấu ?/! là marker DOM bám thế giới.

**Nghiệm thu (đạt 2026-10-12)**: kịch bản Chromium: ném đá → Biến Thể đi kiểm tra; chạy vào nón → báo động → bị tóm → màn Bị phát hiện. Hạ từ sau và khom sau bụi chạy theo cùng logic (test đơn vị cho đồng hồ, nón, tiếng động). Cân bằng số sẽ chỉnh sau khi chơi thử.

### B3 · Đội 4 người và chế độ kế hoạch (2 ngày)

- [x] `Squad` (`src/squad/Squad.ts`): 1–4 đổi thủ lĩnh, camera đổi theo; người còn lại bám vệt đường của thủ lĩnh cách 24 px, copy tư thế. Biến Thể theo dõi cả 4 người, lấy người lộ nhất; tóm bất kỳ ai.
- [x] Kỹ năng riêng từ `public/data/characters.json` (tên, vai, kỹ năng, màu); hạ từ sau chỉ Dương (`ha-tu-sau`), ném đá ai cũng được.
- [x] `PlanMode` (Tab): tạm dừng thế giới, chọn người 1–4, bấm bản đồ thêm Đi tới, T đổi sang Ném đá vào điểm, H hạ gục, G chờ 2 s, Backspace xóa, tối đa 3 lệnh/người; vẽ đường đi dự kiến và nhãn lệnh; Enter thực thi đồng loạt theo thời gian thực, Esc hủy.
- [x] A* 8 hướng trên lưới 16 px (`src/world/Pathfind.ts`, test: vòng tường, không xuyên góc, trại → lối ra qua cầu). Đá ném nhắm điểm (`Rock` tính vận tốc theo thời gian bay).

**Nghiệm thu (đạt 2026-10-12)**: kịch bản Chromium ở đầu cầu: Dương đi tới điểm, Ny ném đá rồi chờ, cùng lúc; Kẻ Lang Thang đi kiểm tra tiếng đá. Bài học nhịp 4 với 2 người sẽ dựng ở B4.

### B4 · Nội dung màn 1 (3 ngày)

- [x] `levels/level1.json` (sinh từ `art/maps/level1.py`): xuất phát, 2 Biến Thể tuần tra (đầu cầu, lối ra), vật phẩm (3 đá khắc, Mảnh Ký Ức, ảnh bốn người, 5 đá ném), 6 vùng kích hoạt, 4 điểm lưu, lộ trình Mai.
- [x] 4 nhịp theo `level_design.md` (`src/levels/level1.ts`, máy trạng thái thuần có test): vòng số 8 đưa về trại → sương tan, Mai hiện ra; rừng (ném đá); đầu cầu; bên kia suối với Biến Thể thứ hai cho bài kế hoạch 2 người; Mai đi trước và chờ đội.
- [x] `public/data/dialogue/level1.json` (6 đoạn, lời nháp cần chủ dự án duyệt) + hộp thoại DOM với chân dung vẽ từ atlas, Enter/Space/bấm để tiếp; thế giới dừng khi thoại.
- [x] Nhặt đồ (E, ưu tiên hạ từ sau nếu có thể), bảng nhiệm vụ chính + phụ (Đá khắc x/3…); `core/save.ts` localStorage lưu ở đầu mỗi nhịp (nhịp, kho đồ, đá, thủ lĩnh, thống kê); Bị phát hiện → Enter nạp điểm lưu; Hoàn thành với thời gian, số lần bị phát hiện, sưu tập; F5 chơi lại, F6 nhịp kế (thử).

**Nghiệm thu (đạt kỹ thuật 2026-10-12)**: kịch bản Chromium đi qua thoại mở đầu, nhặt ảnh, nhảy nhịp bằng điểm lưu tới bên kia suối không lỗi. Chưa chơi thử trọn 8–10 phút bằng tay; cân bằng và thời lượng chỉnh ở B6.

### B5 · HUD và menu v10 (2 ngày, rút ngắn nhờ A4)

- [x] `src/ui/hud.ts`: Nhiệm vụ (mục tiêu chính + phụ với ô ✔), tên màn, Đồng hồ, Bản đồ nhỏ vẽ từ lưới với chấm đội/Biến Thể/Mai/lối ra, thông báo trượt vào (nhiệm vụ, nhặt đồ, cảnh báo), Đội (4 thẻ chân dung từ atlas, HP/SL), thanh hành động (tư thế, Space/E/Tab/C, đồng hồ phát hiện), Ba lô (icon từ atlas). Hộp giữa, hộp thoại, bảng kế hoạch dùng khung 9-slice.
- [ ] Menu Esc: Thông tin, Ba lô, Nhiệm vụ, Lưu, Cài đặt (chưa làm; lưu tự động đã có).

**Nghiệm thu (đạt phần HUD 2026-10-12)**: bố cục khớp mockup ở 1600×900, chữ nét; menu Esc còn lại.

### B6 · Hoàn thiện và phát hành màn 1 (2 ngày)

- [ ] Âm thanh (nguồn CC0 hoặc tự thu), ánh sáng bình minh + sương, test Vitest + Playwright, 60 fps, deploy,
      chơi thử 3–5 người, chỉnh số.

**Nghiệm thu**: link công khai chơi được màn 1; checklist "Build màn 1" tích hết.

Tổng giai đoạn B: **~14–15 ngày**. Tổng A + B: **~25–26 ngày làm việc**.

---

## 5. Giai đoạn C · 12 màn, 6 kết thúc

| Mốc | Nội dung | Phụ thuộc |
| --- | --- | --- |
| C1 · Pipeline màn | Tiled với tileset LPC, lớp collision/occlude/water, object layer; hoặc mở rộng `art/maps/` | B1 |
| C2 · Chiến đấu | Port 18 vũ khí từ prototype (pose, tiếng ồn theo `stats.noise`, băng đạn), dao, lựu; kho vũ khí UI | A3, B2 |
| C3 · 8 loại Biến Thể | FSM riêng từng loại kế thừa `Enemy`; art từ A2 | A2, B2 |
| C4 · Hồi I (màn 2–4) | Trạm kiểm lâm, Bản làng, Quốc lộ | C1–C3 |
| C5 · Hồi II (màn 5–8) | Phố chợ, Trường, Nhà máy nước, Chung cư | C4 |
| C6 · Hồi III (màn 9–12) | Bệnh viện, Ga tàu, B3, Khu Bảo Hộ | C5 |
| C7 · Hệ thống truyện | Cờ toàn cục, 6 kết thúc, bí mật Mai, đếm sưu tập | B4 |
| C8 · Ba lô lưới 18×18 | Kéo thả theo kích thước ô, tải trọng | A4, B5 |
| C9 · Phát hành | Tối ưu tải, nhiều slot lưu, gamepad, mobile, itch.io | tất cả |

---

## 6. Quyết định cần chốt với chủ dự án

1. **Nhân vật: đã chốt giữ LPC làm lớp gốc**, rig ghép lớp bằng code, đổi màu/bộ phận bằng cấu hình; vũ khí,
   item, UI, FX tự vẽ hoàn toàn bằng ma trận. Điều kiện kèm theo: mỗi lần sinh sprite phải có **bản review LPC**
   (A2) để chủ dự án duyệt mắt trước khi xóa sheet cũ.
2. **Cỡ ma trận: đã chốt 2048×2048, N trang cùng chuẩn, trim từ A1.** Giữ 800×450 phóng ×2; không theo hướng
   256×192 ×4 kiểu DS vì phải vẽ lại toàn bộ sprite ở 16–32 px, tỉ lệ 4:3 và tầm nhìn quá hẹp cho game ẩn nấp.
3. **Kích thước bản đồ màn 1**: 1 màn hình (cắt bớt nhịp) hay cuộn 1600×960 với 4 khu. Đề xuất cuộn.
4. **Bị hạ có dậy lại không**: đề xuất 30 giây ở màn 1.
5. **Nguồn âm thanh**: tự sản xuất hay CC0. Cần trước B6.
6. **Giấy phép**: asset dẫn xuất LPC là CC-BY-SA 3.0 / GPL 3.0; thêm `LICENSE` (mã) và `LICENSE-ASSETS` ở A1.
7. **Lời thoại màn 1**: Claude Code viết nháp theo nhịp truyện, chủ dự án duyệt.
8. **Nền tảng**: desktop web cho màn 1; mobile để C9.

---

## 7. Rủi ro

| Rủi ro | Ảnh hưởng | Giảm thiểu |
| --- | --- | --- |
| Refactor art kéo dài, game chưa chạy được trong 2 tuần | Mất động lực, khó thấy tiến độ | A1 nhập tạm sheet cũ vào ma trận ngay ngày đầu; B0 có thể chạy song song từ ngày 2 trên ma trận "tạm", A2–A5 thay dần từng nhóm |
| Trang 0 đầy 90 % nếu không trim | Không còn chỗ cho hoạt ảnh màn sau | Trim ngay từ A1; chuẩn N trang nên thêm `atlas_2` không đổi code game |
| Tọa độ ô đổi mỗi lần sinh → diff ảnh lớn, khó review | Lịch sử Git nặng | Phân vùng cố định + cấp phát tất định theo thứ tự id; `check` so hash |
| Pipeline LPC (clone ~1 GB, đường dẫn cũ) | A2 chậm | Script fetch tự động, cache trong CI, đóng gói phần LPC cần dùng vào `art/characters/lpc_cache/` nếu giấy phép cho phép |
| Rig code không tái tạo đúng pose vẽ tay cũ (bò, hạ gục) | Mất chất lượng | So khớp pixel với sheet cũ trong `check`; pose nào lệch thì giữ ảnh cũ làm "override" có ghi chú |
| Chữ tiếng Việt vỡ dấu | Vi phạm quy ước | Chữ chỉ trên DOM; cấm `Phaser.Text` cho chữ có dấu |
| AI ẩn nấp khó cân bằng | Màn 1 không vui | Hằng số trong `level1.json`, overlay F3, chơi thử sớm ở B2 |

---

## 8. Việc làm ngay trong phiên tiếp theo

1. Câu 1 và 2 ở mục 6 đã chốt (LPC làm gốc + bản review; 2048×2048). Còn lại chốt dần theo mốc.
2. Chạy **A1**: `art/matrix.py`, `pixel.py`, `palette.py`, `build.py`, `check.py`; nhập tạm 9 sheet cũ vào 2 trang;
   `atlas_viewer.html`; `docs/ART.md`.
3. Chạy **A3** trước A2 nếu muốn thấy kết quả "ma trận ký tự" sớm: 18 vũ khí + 33 item là nhóm nhỏ, dễ duyệt mắt.

Câu lệnh gợi ý cho Claude Code:
- "Thực hiện A1 trong docs/PLAN.md: dựng art/matrix.py với lưới 128×128 ô 16 px (trang 2048×2048), trim khung,
  nhập toàn bộ sheet cũ vào atlas_0/atlas_1, sinh atlas.json, viết atlas_viewer.html và docs/ART.md."
- "Thực hiện A3: chuyển 18 vũ khí v2 sang ma trận ký tự có đánh dấu G/M, sinh lại weapons.json và so khớp với bản chốt."
