# Vùng Xanh Cuối Cùng · Kế hoạch xây dựng

Kế hoạch này được lập sau khi đọc toàn bộ gói bàn giao (`CLAUDE.md`, `README.md`, `docs/level_design.md`,
`docs/CREDITS.md`, 10 file `data/*.json`, 38 file `assets/`, 26 script `tools/`, `prototype/build_hub.html`).
Mục tiêu trước mắt theo `CLAUDE.md`: **màn 1 "Đường Mòn Sương" chơi được**, sau đó mở rộng ra 12 màn.

---

## 1. Hiện trạng gói bàn giao

### 1.1 Đã có (dùng được ngay)

| Nhóm | Nội dung | Ghi chú kỹ thuật |
| --- | --- | --- |
| Nhân vật | 3 sheet 64×64: `anim_core` (30 hàng), `anim_more` (24 hàng), `anim_actions` (28 hàng) cho Dương, Hùng, Ny, Sơn + Biến Thể cơ bản | Mỗi hàng = 1 hoạt ảnh; `[tên, hoạt ảnh, số khung]` trong JSON cùng tên. Sheet rộng 704 = tối đa 11 khung/hàng |
| Kẻ thù | `wanderer_walk_knockdown.png` (đi trái 8 + bị hạ 11) dùng cho màn 1; `zombies.png` 6 loại × 4 hoạt ảnh (màn 3–8) | Kẻ Lang Thang màn 1 chỉ có hướng trái, lật ngang để đi phải |
| NPC | Mai, Ông Tư, Bác sĩ Lan, Lính Nhiễm (`npcs.png`, 20 hàng) | Mai có "Lơ lửng", "Hiện ra" cho ánh sáng xanh |
| Vũ khí | `weapons.json` v2 chốt 18 món; sheet hoạt ảnh 54 hàng (đi/ngắm/bắn), atlas, icon; dao ngắn + dao rựa (`melee_anim`) | Màn 1 **không có súng**, hệ thống súng chỉ cần từ màn 2+ (prototype đã có logic bắn tái dùng được) |
| Vật phẩm | 33 icon 16×16, thứ tự icon = thứ tự trong `items.json` | Màn 1 dùng: đá, Mảnh Ký Ức, Đá khắc, Ảnh bốn người, túi cứu thương |
| Hiệu ứng | 12 FX 64×64 (`fx.json`), có "Tiếng động (ném đá)" và "Bị phát hiện" | Dùng trực tiếp cho vòng tiếng động và báo động |
| UI | 5 mockup v10 1600×900 (HUD, menu, kho vũ khí, ba lô, vật phẩm) + token màu trong `tools/locked.py` và CSS của prototype | HUD mockup đã vẽ đủ: nhiệm vụ, đội, thanh hành động Q/W/E/R, ba lô, bản đồ nhỏ, đồng hồ, thông báo |
| Bản đồ | `level1_bridge_bg.png` 800×450 (cảnh cầu gỗ) | Sinh bằng `tools/lpcscene.py`: lưới 25×15 tile 32px, sông x≈13, đường mòn y≈8.6 |
| Font | Be Vietnam Pro 4 độ đậm (OFL) | |
| Prototype | `build_hub.html`: vòng lặp canvas, vẽ khung LPC, y-sort, lật hướng, Biến Thể tuần tra + nón nhìn thô + nghe tiếng động, 18 vũ khí | Là điểm xuất phát tốt cho renderer và pose vũ khí |

### 1.2 Còn thiếu (phải làm hoặc quyết định)

1. **Chưa có mã game thật**: chưa có build tool, module, lưới va chạm, AI, HUD trong game, lưu game.
2. **Bản đồ màn 1 chỉ có 1 màn hình** (800×450) trong khi thiết kế cần 4 khu vực (trại → rừng thông → đầu cầu → bên kia suối, 8–10 phút chơi). Cần bản đồ lớn hơn và camera cuộn.
3. **Thiếu hoạt ảnh "Đi lên"** cho 4 nhân vật chính và Biến Thể (chỉ có đi xuống, đi trái, chạy lên). Game 3/4 cần đủ 4 hướng đi bộ.
4. **Không có âm thanh** (nhạc nền, bước chân, đá rơi, báo động). Không có file audio nào trong gói.
5. **Script `tools/` trỏ đến `/home/claude/...`** và cần thư viện LPC gốc (`lpct/`, generator) không có trong gói; muốn sinh lại asset phải clone LPC và sửa đường dẫn.
6. **Chưa có kịch bản hội thoại** màn 1 (chỉ có nhịp truyện trong bảng thiết kế).
7. **Chưa có dữ liệu màn** (điểm tuần tra, trigger, vị trí vật phẩm, điểm lưu) ở dạng máy đọc được.
8. Tuyến Mai là bệnh nhân số 0 và bí mật của Sơn còn là đề xuất, chưa đối chiếu kịch bản gốc (ảnh hưởng màn 8, 11, 12, không ảnh hưởng màn 1).

---

## 2. Quyết định kỹ thuật

### 2.1 Stack: **Phaser 3 + TypeScript + Vite**, HUD bằng DOM overlay

Lý do chọn Phaser 3 thay vì Godot 4:
- Toàn bộ asset, prototype và mockup đã là web; mở thẳng trên trình duyệt, deploy GitHub Pages / itch.io không cần export.
- Claude Code chạy, test (Vitest) và chụp màn hình (Playwright) được ngay trong phiên làm việc; Godot cần editor và không kiểm thử tự động được trong môi trường này.
- Phaser có sẵn: scene, camera cuộn, spritesheet nhiều hàng, tilemap Tiled (cho màn 2–12), tween, audio, input bàn phím/chuột/gamepad.

Lý do HUD/menu dùng DOM (HTML/CSS) đè lên canvas thay vì vẽ trong Phaser:
- Quy ước bắt buộc: chữ tiếng Việt phải vẽ ở độ phân giải hiển thị. Canvas 800×450 phóng ×2 sẽ làm vỡ dấu. DOM overlay vẽ chữ ở 1600×900 nét, còn sprite vẫn nearest-neighbour.
- CSS token v10 đã có sẵn trong prototype (`--bg`, `--panel`, `--edge`, `--tick`, `--mag-hi`...), tái dùng trực tiếp.
- Game và HUD giao tiếp qua một `EventBus` (Phaser `EventEmitter`), HUD không đụng vào state game.

Cấu hình Phaser: `width: 800, height: 450, zoom: 2, pixelArt: true, roundPixels: true`, `Scale.FIT` giữ tỉ lệ 16:9, nền `#080A10`.

### 2.2 Kiến trúc thư mục (sau M0)

```
/
├─ index.html · package.json · vite.config.ts · tsconfig.json
├─ public/
│  ├─ assets/          ← chuyển từ assets/ (Vite phục vụ tĩnh, không bundle 7 MB ảnh)
│  └─ data/            ← chuyển từ data/ + thêm levels/level1.json, dialogue/level1.json
├─ src/
│  ├─ main.ts                 cấu hình Phaser, khởi động scene
│  ├─ core/
│  │  ├─ anims.ts             đọc data/*.json → đăng ký animation (key = "Dương/Đi xuống")
│  │  ├─ events.ts            EventBus game ↔ HUD
│  │  ├─ input.ts             ánh xạ phím (WASD, 1–4, Q/W/E/R, Space, Tab, Esc)
│  │  └─ save.ts              checkpoint JSON → localStorage
│  ├─ world/
│  │  ├─ CollisionGrid.ts     lưới 16px: đi được / chặn / che khuất / nước / cầu
│  │  ├─ Triggers.ts          vùng kích hoạt mục tiêu, hội thoại, điểm lưu
│  │  └─ Pickups.ts           vật phẩm trên bản đồ
│  ├─ entities/
│  │  ├─ Actor.ts             sprite LPC: chân ở y-60, lật khi quay phải, depth = y chân
│  │  ├─ Player.ts / Squad.ts 4 nhân vật, đổi 1–4, đi theo thủ lĩnh
│  │  ├─ Enemy.ts             Kẻ Lang Thang (FSM) + lớp cơ sở cho 8 loại
│  │  ├─ Npc.ts               Mai (ánh sáng xanh dẫn đường)
│  │  └─ Rock.ts              đá ném, quỹ đạo parabol, tạo tiếng động
│  ├─ stealth/
│  │  ├─ VisionCone.ts        nón nhìn + raycast qua lưới che khuất
│  │  ├─ Noise.ts             vòng tiếng động, truyền sự kiện cho Enemy
│  │  ├─ Detection.ts         đồng hồ 3 mức: Ẩn mình / Nghi ngờ / Báo động
│  │  └─ PlanMode.ts          tạm dừng, xếp lệnh cho từng người, thực thi đồng loạt
│  ├─ scenes/  Boot · Preload · Level · Result (thắng/thua) · Pause
│  ├─ ui/      hud.ts · dialogue.ts · menus.ts · tokens.css (DOM overlay v10)
│  └─ levels/  level1.ts (nạp level1.json, kịch bản 4 nhịp hướng dẫn)
├─ docs/       level_design.md · CREDITS.md · PLAN.md · (sau) ARCHITECTURE.md
├─ tools/      script Python sinh asset (sửa đường dẫn, thêm README)
└─ prototype/  giữ làm tham chiếu, không phát triển tiếp
```

### 2.3 Quy ước code bắt buộc (bám `CLAUDE.md`)

- Mọi hoạt ảnh nạp từ JSON, **không hard-code chỉ số hàng** trong code. Khung = `row * 11 + col` với sheet rộng 704, `row * 10 + col` với sheet rộng 640.
- Vẽ actor tại `(x - 32, y - 60)`, `depth = y` (y của chân). Hướng phải = `flipX = true` của khung hướng trái.
- Vũ khí nạp từ `weapons.json` v2; không đụng `weapons_v3_smg_backup.json`.
- Màu UI chỉ lấy từ token v10; không thêm màu mới ngoài bảng.
- Mọi chuỗi hiển thị là tiếng Việt có dấu, nằm trong `data/` hoặc `src/ui/strings.ts`, không rải trong logic.

---

## 3. Lộ trình: màn 1 chơi được

Mỗi mốc có **tiêu chí nghiệm thu** để biết khi nào xong. Ước lượng tính theo ngày làm việc với Claude Code.

### M0 · Khởi tạo dự án (0.5 ngày)

- [ ] `npm create vite` + TypeScript + Phaser 3.80+; ESLint, Prettier, Vitest; script `dev`, `build`, `test`, `lint`.
- [ ] Chuyển `assets/` → `public/assets/`, `data/` → `public/data/`; `@font-face` Be Vietnam Pro từ file local.
- [ ] Viết `core/anims.ts` đọc 7 file JSON hoạt ảnh và đăng ký animation; unit test kiểm tra số hàng khớp chiều cao sheet.
- [ ] Scene `Preload` hiện thanh nạp theo phong cách v10; scene `Level` vẽ `level1_bridge_bg.png` và Dương đi 4 hướng.
- [ ] GitHub Actions: lint + test + build mỗi push; deploy `dist/` lên GitHub Pages từ nhánh chính.
- [ ] Viết lại `README.md` thành README dự án (cách chạy, cấu trúc, giấy phép); đổi nội dung bàn giao cũ vào `docs/HANDOFF.md`.

**Nghiệm thu**: `npm run dev` mở game 1600×900, Dương đi bằng WASD, lật đúng hướng, chữ tiếng Việt nét trên overlay.

### M1 · Nền tảng thế giới (2 ngày)

- [ ] **Quyết định bản đồ màn 1** (xem mục 5.1). Đề xuất: bản đồ 50×30 tile (1600×960) sinh bằng `tools/lpcscene.py` đã sửa đường dẫn, gồm 4 khu theo thiết kế; camera cuộn theo thủ lĩnh, `roundPixels`.
- [ ] `CollisionGrid` 16px với 5 loại ô: đi được, chặn (thân cây, đá), **che khuất** (tán cây, bụi: đi được nhưng chắn tầm nhìn), nước (chặn), cầu (lối duy nhất qua suối). Xuất từ mask PNG kèm bản đồ (mỗi màu = 1 loại) để chỉnh bằng công cụ vẽ ảnh.
- [ ] Di chuyển có va chạm trượt dọc tường; 3 tư thế **Đứng / Khom / Bò** (tốc độ 58 / 34 / 18 px/s, ảnh hưởng độ lộ diện).
- [ ] Y-sort toàn bộ actor và vật thể cao (cây) bằng `depth`.
- [ ] Sinh hoạt ảnh **"Đi lên"** cho 4 nhân vật + Biến Thể từ LPC hàng 0 (cần clone LPC generator, sửa `tools/`), cập nhật JSON.
- [ ] Debug overlay (phím F3): vẽ lưới va chạm, nón nhìn, vòng tiếng động.

**Nghiệm thu**: đi hết 4 khu màn 1, không lọt nước, cầu là đường duy nhất qua suối, cây che người khi đứng sau.

### M2 · Lõi ẩn nấp (3 ngày)

- [ ] `Enemy` FSM: **Tuần tra** (đi theo điểm, dừng ở mỗi điểm và "Quay đầu nghe ngóng" mỗi 4 giây theo thiết kế) → **Nghi ngờ** (đi tới điểm nghi) → **Điều tra** (nhìn quanh 3 giây) → **Báo động** (đuổi theo, tốc độ 30 px/s) → **Mất dấu** (về điểm cuối thấy, rồi về tuần tra) → **Bị hạ**.
- [ ] `VisionCone`: góc 90°, tầm 140 px, raycast qua lưới che khuất; người ở tư thế Khom/Bò trong ô "che khuất" không bị thấy; vẽ nón mờ đỏ như mockup HUD.
- [ ] `Detection` 3 mức, mỗi Biến Thể một đồng hồ: 0–40 % Ẩn mình, 40–99 % Nghi ngờ (hiện `?`), 100 % Báo động (hiện `!`, FX "Bị phát hiện"). Tốc độ đầy tỉ lệ nghịch khoảng cách, nhân hệ số tư thế (Đứng 1.0 / Khom 0.6 / Bò 0.35); tự giảm khi ra khỏi nón.
- [ ] `Noise`: ném đá (hoạt ảnh "Ném đá" 8 khung, quỹ đạo parabol, rơi tạo vòng 120 px + FX "Tiếng động"); Biến Thể trong vòng chuyển sang Điều tra tại điểm rơi. Chạy cũng tạo vòng nhỏ 48 px.
- [ ] **Hạ từ sau** (Dương): đứng sau lưng trong 20 px, ngoài nón nhìn, bấm W → "Khóa siết từ sau" 10 khung + Biến Thể "Bị hạ" 11 khung; nằm 30 giây rồi dậy (cấu hình trong level JSON).
- [ ] Bị tóm (Báo động và chạm người) → Result "Bị phát hiện", nạp lại điểm lưu.

**Nghiệm thu**: sân thử 1 Biến Thể ở đầu cầu: có thể vượt bằng ném đá đánh lạc hướng **hoặc** hạ từ sau; bị thấy khi đứng, không bị thấy khi khom sau bụi.

### M3 · Đội 4 người và chế độ kế hoạch (2 ngày)

- [ ] `Squad`: phím 1–4 đổi thủ lĩnh; người còn lại đi theo hàng dọc cách 24 px, copy tư thế, tự nấp khi thủ lĩnh nấp; mỗi người có đồng hồ phát hiện riêng.
- [ ] Kỹ năng riêng nạp từ `data/characters.json` (mới): Dương hạ từ sau, Hùng phá cửa / khiêng, Ny nhảy qua / chế thuốc, Sơn mở khóa / drone. Màn 1 chỉ bật Dương + Ny (nhịp 4).
- [ ] `PlanMode` (Tab): tạm dừng, chọn từng người, xếp tối đa 3 lệnh (Đi tới, Chờ, Ném đá, Hạ gục), vẽ đường đi dự kiến, Enter thực thi đồng loạt; Esc hủy.
- [ ] Pathfinding A* trên lưới 16px cho lệnh Đi tới và cho Biến Thể điều tra.

**Nghiệm thu**: ở nhịp 4 màn 1, lên kế hoạch cho 2 người cùng lúc ném đá và hạ gục, thực thi đúng thứ tự.

### M4 · Nội dung màn 1 (3 ngày)

- [ ] `public/data/levels/level1.json`: vị trí xuất phát, điểm tuần tra, vật phẩm (3 đá khắc, 1 Mảnh Ký Ức, ảnh bốn người, 5 viên đá ném), trigger, điểm lưu, lời nhắc hướng dẫn.
- [ ] 4 nhịp theo `level_design.md`: (1) trại: dạy đi + khom, vòng lặp đường mòn đưa về trại lần 1 (trigger đổi sương, Mai hiện ra); (2) rừng thông: dạy ném đá; (3) đầu cầu: dạy nón nhìn + hạ từ sau; (4) bên kia suối: dạy kế hoạch 2 người, đi theo Mai ra khỏi rừng.
- [ ] Hội thoại `dialogue/level1.json` (người nói, câu, lựa chọn nếu có); hộp thoại v10 với chân dung; viết lời thoại nháp cho 4 nhịp để nhóm kịch bản duyệt.
- [ ] Nhặt đồ (E), ba lô cập nhật, mục tiêu phụ "Đá khắc 1/3".
- [ ] Điểm lưu ở đầu mỗi nhịp; `save.ts` ghi vị trí, vật phẩm, cờ; tự lưu + nạp từ menu.
- [ ] Màn **Hoàn thành** (thời gian, số lần bị phát hiện, đá khắc) và **Bị phát hiện** (thử lại từ điểm lưu) theo bố cục v10.

**Nghiệm thu**: chơi từ đầu đến cuối 8–10 phút không cần debug, qua được bằng cả 2 cách, thắng/thua hiển thị đúng.

### M5 · HUD và menu v10 (3 ngày)

- [ ] `ui/tokens.css` từ token v10; thành phần: khung có vạch quét, ngoặc góc, tab hình bình hành, thanh phân đoạn, LED.
- [ ] HUD theo mockup `v10_hud.png`: Nhiệm vụ (trái trên), Bản đồ nhỏ (phải trên, vẽ từ lưới va chạm), Đồng hồ, thông báo trượt vào, Đội (4 thẻ HP/SL), thanh hành động Q/W/E/R + tư thế, Ba lô nhanh, nhãn "Ném đá ×3".
- [ ] Menu Esc: Thông tin nhân vật, Ba lô (lưới vật phẩm, màn 1 chưa cần kéo thả 18×18), Nhiệm vụ, Lưu game, Cài đặt (âm thanh, phụ đề, tự lưu).
- [ ] Hỗ trợ chuột cho menu, bàn phím cho game; gamepad để sau.

**Nghiệm thu**: so khớp từng vùng với mockup ở 1600×900; chữ nét, không vỡ dấu ở mọi cỡ cửa sổ.

### M6 · Hoàn thiện và phát hành màn 1 (2 ngày)

- [ ] Âm thanh: cần nguồn (tự thu / CC0 freesound / kenney). Tối thiểu: nền rừng + suối, bước chân (cỏ/gỗ), ném và rơi đá, "?" và "!", bị hạ, nhạc menu. Ghi công vào `CREDITS.md`.
- [ ] Ánh sáng bình minh + sương: lớp overlay gradient và particle sương nhẹ; ánh sáng xanh của Mai bằng sprite "Lơ lửng" + glow.
- [ ] Test: Vitest cho `CollisionGrid`, `Detection`, `Noise`, `anims`; Playwright chụp HUD và chạy kịch bản "qua cầu bằng ném đá" để chống hồi quy.
- [ ] Hiệu năng: 60 fps trên laptop tích hợp; không rò rỉ listener khi nạp lại màn.
- [ ] Deploy GitHub Pages; chơi thử 3–5 người, ghi thời gian hoàn thành và số lần bị phát hiện; chỉnh số (tầm nhìn, tốc độ đầy đồng hồ).

**Nghiệm thu**: link công khai chơi được màn 1; checklist "Build màn 1" trong `level_design.md` tích hết.

Tổng cho màn 1: **~15–16 ngày làm việc**.

---

## 4. Lộ trình sau màn 1 (12 màn, 6 kết thúc)

| Mốc | Nội dung | Phụ thuộc |
| --- | --- | --- |
| M7 · Pipeline màn | Chuyển sang Tiled: tileset LPC trong `assets/tiles/`, lớp `collision`/`occlude`/`water`, object layer cho tuần tra, trigger, vật phẩm; loader chung; công cụ xuất mask | M1 |
| M8 · Hệ thống chiến đấu | Port logic 18 vũ khí từ prototype (pose, tiếng ồn theo `stats.noise`, băng đạn), dao, ném lựu/khói; đạn trong ba lô; kho vũ khí v2 UI | M2, M5 |
| M9 · 8 loại Biến Thể | Kẻ Thính (nghe, mù), Kẻ Phun (mây bào tử theo gió), Kẻ Bám Trần (đèn pin), Kẻ Mang Vỏ (miễn cận chiến), Kẻ Bắt Chước (tiếng gọi giả), Bầy Chuột (cống, sợ lửa), Lính Nhiễm (súng, trạm gác). Mỗi loại một FSM kế thừa `Enemy` | M2 |
| M10 · Hồi I (màn 2–4) | Trạm kiểm lâm (máy phát, drone Sơn, phá cửa Hùng), Bản làng (nước gây ồn, khiêng Ông Tư), Quốc lộ (gió, mặt nạ, kháng bào tử) | M7–M9 |
| M11 · Hồi II (màn 5–8) | Phố chợ (2 tầng cống), Trường (3 tầng, đèn pin), Nhà máy nước (bẫy máy ép, sửa máy), Chung cư (ngụy trang, lựa chọn tin Sơn) | M10 |
| M12 · Hồi III (màn 9–12) | Hộ tống Bác sĩ Lan, Ga tàu (kế hoạch đồng loạt + súng), B3 (thẻ từ, camera, laser, tha thứ Sơn), Khu Bảo Hộ (3 lối vào) | M11 |
| M13 · Hệ thống truyện | Cờ toàn cục: số người sống, tha thứ Sơn (màn 8, 11), Ny có thuốc (màn 9), lối vào (màn 12); 6 kết thúc + bí mật Mai (6/6 Mảnh Ký Ức, 12/12 đá khắc); đếm sưu tập trên HUD | M4 |
| M14 · Ba lô lưới 18×18 | Kéo thả theo kích thước ô (mockup `v10_backpack.png`), tải trọng, đưa đồng đội | M5 |
| M15 · Phát hành | Tối ưu tải (atlas, nén), lưu nhiều slot, cài đặt phím, gamepad, bản mobile (nếu cần), trang itch.io | tất cả |

---

## 5. Quyết định cần chốt với chủ dự án

1. **Kích thước bản đồ màn 1**: (a) giữ 1 màn hình 800×450 và cắt bớt 4 nhịp xuống 2, hay (b) bản đồ cuộn ~1600×960 sinh lại bằng `tools/lpcscene.py` với 4 khu theo thiết kế. **Đề xuất (b)**; nền hiện tại trở thành khu 3 (đầu cầu).
2. **Bị hạ có dậy lại không**: prototype cho dậy sau 4 giây; đề xuất màn 1 dậy sau 30 giây để giữ áp lực nhưng vẫn là màn hướng dẫn.
3. **Nguồn âm thanh**: tự sản xuất hay dùng CC0. Cần quyết định trước M6.
4. **Giấy phép**: sprite dẫn xuất từ LPC là CC-BY-SA 3.0 / GPL 3.0, nên toàn bộ asset dẫn xuất phải phát hành cùng giấy phép; mã nguồn có thể giấy phép riêng. Cần thêm `LICENSE` (mã) và `LICENSE-ASSETS` ở M0.
5. **Hoạt ảnh "Đi lên"**: sinh lại từ LPC (đúng chuẩn, cần clone generator ~1 GB) hay tạm dùng "Chạy lên" chậm lại (nhanh nhưng dáng không khớp). Đề xuất sinh lại ở M1.
6. **Lời thoại màn 1**: ai viết? Claude Code viết nháp theo nhịp truyện, chủ dự án duyệt.
7. **Nền tảng mục tiêu**: chỉ desktop web cho màn 1; mobile để M15.

---

## 6. Rủi ro

| Rủi ro | Ảnh hưởng | Giảm thiểu |
| --- | --- | --- |
| Pipeline sinh asset Python gãy (đường dẫn `/home/claude`, thiếu LPC gốc) | Không sinh được "Đi lên", bản đồ mới, Biến Thể mới | M1 dành 0.5 ngày khôi phục `tools/`: biến môi trường `LPC_ROOT`, README cách chạy, clone LPC generator |
| Chữ tiếng Việt vỡ dấu trên canvas phóng ×2 | Vi phạm quy ước, UI xấu | Toàn bộ chữ trên DOM overlay; cấm `Phaser.GameObjects.Text` cho chữ có dấu |
| AI ẩn nấp khó cân bằng (quá dễ / quá ức chế) | Màn 1 không vui | Mọi hằng số (góc, tầm, tốc độ đầy đồng hồ) nằm trong `level1.json`; debug overlay F3; chơi thử sớm ở M2 |
| Bản đồ pre-render PNG khó sửa về sau | Chỉnh bố cục tốn công | Chuyển sang Tiled ở M7; màn 1 giữ PNG + mask để ra bản chơi được sớm |
| Phạm vi 12 màn lớn | Kéo dài vô hạn | Chỉ cam kết màn 1 đến M6; màn 2–12 lập kế hoạch lại sau khi chơi thử |

---

## 7. Việc làm ngay trong phiên tiếp theo

1. Chốt câu hỏi 1, 2, 5 ở mục 5 (bản đồ, dậy lại, "Đi lên").
2. Chạy M0: khởi tạo Vite + Phaser + TypeScript, chuyển asset, viết `core/anims.ts` và test, Dương đi 4 hướng trên nền cầu.
3. Chạy M1 phần lưới va chạm trên nền hiện có (mask PNG cho vùng cầu) để có sân thử cho M2 sớm nhất.

Câu lệnh gợi ý cho Claude Code:
- "Thực hiện M0 trong docs/PLAN.md: khởi tạo Vite + Phaser 3 + TypeScript, chuyển assets/data vào public/, viết core/anims.ts nạp JSON hoạt ảnh, scene Level vẽ nền cầu và Dương đi 4 hướng."
- "Thực hiện M1: tạo CollisionGrid từ mask PNG, 3 tư thế, y-sort, debug overlay F3."
