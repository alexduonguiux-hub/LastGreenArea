# Khảo sát nguồn UI và nhà cửa mã nguồn mở (2026-10-13)

Mạng chỉ mở GitHub, nên mọi gói lấy qua repo GitHub có chứa gói (clone thưa + tải LFS bằng `tools/fetch_ui_kits.sh`).
Mock HUD kỹ (bố cục v11, 9-slice đo theo file theme/viền thật, chân dung và icon thật từ atlas) sinh bằng
`scratchpad/mock/build_mock.py`; ảnh so sánh `compare_bottom.png`, `compare_top.png`, `mock{B,C,E,F,G}_full.png`.

## Ứng viên UI
| Mã | Bộ | Giấy phép | Kích cỡ | Nhận xét |
|---|---|---|---|---|
| A | v11 "đá và gỗ" hiện tại (vẽ bằng code, `art/ui/components.py`) | của dự án | 1 px game | Khớp màu thế giới nhất; thiếu chất liệu tay. |
| B | Pixel UI Fantasy – parchment (heyheythere) | CC BY 4.0 | 1 px game, lề 9-slice trong `parchment.tres` | Giấy da + gỗ, đinh tán; ribbon đỏ cần đổi màu; chất lượng cao, đủ thành phần (slot theo bậc, thanh, tab, cửa sổ). |
| C | Kenney UI Pack Pixel Adventure 16 px | CC0 | 1 px game | Đơn giản, phẳng; phải đổi đỏ→gỗ, xanh→xám ấm; ít chất liệu. |
| D | Golden UI – Buch | CC BY-SA 3.0 | 1 px game | Kim loại cam, hợp sci-fi hơn; cần đổi màu toàn bộ. |
| E | Fantasy Minimal Pixel Art GUI – ETA | "commercial-free" (kèm txt) | 1 px game | Viền nâu vàng, lòng tím than, hoa văn thắt nút; trầm, sạch, đủ hộp tiêu đề/phím/thanh. |
| F | Tiny Swords – Pixel Frog | Free (không phân phối lại) | vẽ ở độ phân giải hiển thị (ô 64 px) | Gỗ chạm + giấy, nét vẽ tay; lệch "tỷ lệ pixel" với thế giới. |
| G | Cryo's Mini GUI khung gỗ + nền đá v11 | kiểm tra lại trang itch | 1 px game | Khung ván gỗ nhỏ gọn ghép với nền đá v11; gần A nhất. |
| – | Kenney Fantasy UI Borders | CC0 | 48 px nét mảnh | Viền một màu, tô được; không "pixel dày". |
| – | BDragon1727 Border/Panels, Ribbons | free (itch) | 64 px | 16 bảng màu viền hoa văn mảnh + ruy băng nhiều màu; bộ 12 màu khaki hợp. |
| – | Sprout Lands UI | free (Cup Nooble) | 1 px game | Dễ thương kiểu nông trại, không hợp giọng sinh tồn. |

## Ứng viên nhà cửa (chuẩn bị cho màn 2–12)
| Nguồn | Giấy phép | Có gì | Dùng cho |
|---|---|---|---|
| Kenney Roguelike City | CC0, 16 px | tường gạch đỏ/xám/kem theo mô-đun, cửa kính, mái hiên, xe hơi, cột đèn, thùng rác, biển báo, đường | bệnh viện, trường THPT, chung cư, phố chợ, quốc lộ kẹt xe, ga tàu |
| Kenney Roguelike Base | CC0, 16 px | nhà có mái (kem/xám/gỗ), lều xanh và lều bạt, hàng rào, cọc, đồ trại, giếng | trạm kiểm lâm, bản làng, trại lính |
| Kenney Tiny Town | CC0, 16 px | mái, tường, cổng đá, rào | phụ |
| Stendhal | CC BY-SA 3.0 | lều bạt 160 px, lều xanh, chòi gỗ, nhà tranh, tàn tích đá, cọc rào, nhà gỗ 3 | bản làng dưới đầm, trại lính, khu bảo hộ |
| LPC Sharm building-exterior | CC BY-SA 3.0 | tường gạch, đá, cửa, cửa sổ | ghép nhà |
| Cainos wall/struct | gói gốc | tường đá, bệ, cầu thang | tham chiếu màu; khu bảo hộ |
| Tiny Swords Buildings | free | lâu đài, nhà fantasy vẽ tay | không hợp bối cảnh hiện đại |

Mọi sprite ngoài Cainos đi qua `art/maps/grade.py:cainos_grade` (bảng `buildings_candidates.png` cho thấy gốc và sau grade).

## Khảo sát nguồn isometric (2026-10-14)
Bản nháp iso: `scratchpad/iso/iso_draft.py` (chiếu bản đồ top-down màn 1 sang 2:1) và `scratchpad/iso/iso_v2.py` (tile iso pixel thật, `GRADE=0/1`).

| Nguồn | Giấy phép | Kiểu | Có gì | Nhận xét |
|---|---|---|---|---|
| Yar iso-64x64-outside / -building (qua repo `phaserjs/examples`) | CC BY 3.0 | pixel art iso 64×64, ô 64×32 | cỏ, vách đá, đá, thác, nước + bờ, bụi, thông, cây to, gỗ; tường gạch, mái ngói, sàn, cửa, bàn ghế | Hợp nhất: đúng tỷ lệ với nhân vật LPC 64 px; cả màu gốc lẫn grade đều dùng được. Thiếu đường mòn, cầu, nhà hiện đại. |
| Tanks of Freedom (P1X) | MIT (cả hình) | pixel iso nhỏ (ô 64×32, đơn vị 16 px) | địa hình đường/nước/đất, nhà dân, nhà máy, công trình quân sự, rào, xe tăng, lính | Tỷ lệ chiến thuật, quá nhỏ so với nhân vật 64 px. Dùng tham khảo bố cục trại lính. |
| Simutrans pak128 | Artistic License 2.0 | pixel iso ô 128×64 | trường tiểu học/trung học, trạm cứu hoả, chợ, nhà dân, xe cứu thương, cây | Có đúng loại công trình hiện đại cần; nhà hơi nhỏ so với nhân vật (1,5 tầng ≈ 1 người), tên tác giả ghi ngay trên sheet. |
| OpenGFX (OpenTTD) | GPL v2 | pixel iso 8bpp, ô 64×31 | nhà, chung cư, văn phòng, xe, ga, cây | Quá nhỏ (nhà 66×87), nền xanh dương phải tách. |
| Flare (flare-game) | CC BY-SA 3.0 | 3D render iso, ô 64×32, nhân vật 128 px 8 hướng | tileset đồng cỏ/hang/hầm/tuyết, zombie, skeleton, goblin, avatar ghép trang bị | Nguồn nhân vật 8 hướng duy nhất tìm được; phong cách 3D tối, không khớp pixel LPC. |
| Phaser tests/iso (zombie.png, skeleton8.png, rem_0002) | chưa rõ (giống Reiner's Tilesets) | 3D render 8 hướng | zombie, skeleton, nhà tranh | Chỉ tham khảo. |
| Lincity-NG | GPL (data) | 3D render iso ~256 px | trường học, bệnh viện (health), trạm cứu hoả, chợ, đại học, sân bóng, nhà ổ chuột | Đúng loại công trình, đúng tỷ lệ với nhân vật, nhưng là 3D render; cần posterize để thành pixel. |
| Unknown Horizons | CC BY-SA 3.0 | 3D render iso | nhà trung cổ, quảng trường, cây | Không hợp bối cảnh. |
| Kenney isometric (23 gói trong `series-ai/jam-ready-assets`) | CC0 | vector / 3D phẳng | blocks, miniature, nature, city, buildings, vehicles, tower defense | Không phải pixel art; CC0 nên dùng làm prototype khối. |
| screamingbrain Iso Town | CC0 | 3D render chi tiết | 8 toà nhà phố | Không hợp pixel. |
| Tiled examples (isometric_grass_and_water, Yar) | CC BY 3.0 | 3D render tối | cỏ, nước | Tham khảo. |
