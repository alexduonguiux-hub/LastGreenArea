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
