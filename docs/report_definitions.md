# Định nghĩa mẫu sổ — Các sổ ra/vào

| Thuộc tính | Giá trị |
|---|---|
| Mã tài liệu | QLCBCS-RPT-SO |
| Phiên bản | 0.2 — **Dự thảo để thống nhất** (bổ sung theo bản triển khai Excel/Word/PDF) |
| Ngày lập | 26/10/2026 |
| Tính chất | Mẫu nghiệp vụ nội bộ thiết kế mới; **không** phải biểu mẫu pháp lý (`requirements.md` §2). Mọi tên gọi, chức danh, bố cục là đề xuất, chờ đơn vị xác nhận (`XN-xx`). |
| Liên quan | [`requirements.md`](requirements.md), [`business_rules.md`](business_rules.md), [`test_plan.md`](test_plan.md) |

Cách đọc: mục 2 là quy định chung áp dụng cho cả bốn sổ; mục 3–6 là định nghĩa riêng của từng sổ, chỉ nêu phần khác hoặc bổ sung so với mục 2; mục 7 là bản mẫu bố cục dựng từ bộ dữ liệu DS-01 (`test_plan.md` §5).

---

## 1. Danh mục sổ

| Mã sổ | Tên sổ (đề xuất, `XN-04`) | Tên ngắn (tên file) | Khổ / hướng | Một dòng là | Yêu cầu |
|---|---|---|---|---|---|
| SO-01 | SỔ THEO DÕI CBCS RA/VÀO | `CBCS` | A4 ngang | Một lượt của một CBCS | REQ-SO1-* |
| SO-02 | SỔ THEO DÕI KHÁCH RA/VÀO | `Khach` | A4 ngang | Một lượt của một khách | REQ-SO2-* |
| SO-03 | SỔ THEO DÕI PHƯƠNG TIỆN RA/VÀO | `PhuongTien` | A4 ngang | Một lượt của một phương tiện | REQ-SO3-* |
| SO-04 | SỔ TỔNG HỢP RA/VÀO | `TongHop` | A4 dọc | Một chỉ tiêu / một nhóm / một ngày (theo từng phần) | REQ-SO4-* |

---

## 2. Quy định chung (RPT-00)

### 2.1. Nguyên tắc thiết kế

1. **Một dòng — một lượt** ở sổ chi tiết; người đọc không phải ghép sự kiện Ra với sự kiện Vào.
2. **Đọc được khi in đen trắng**: trạng thái bằng chữ, chưa hoàn tất in đậm, không dùng màu để truyền thông tin (BR-TT-03, BR-TT-04).
3. **Không gây hiểu nhầm về số liệu**: mỗi chỉ tiêu ghi đơn vị tính ("lượt", "đối tượng", "sự kiện"); không cộng chéo nhóm (BR-TONG-04).
4. **Tự giải thích**: mỗi bản in có kỳ, thời điểm chốt, điều kiện lọc, chú giải ký hiệu, thông tin trích xuất.
5. **Truy vết được**: mã trích xuất trên mọi trang; đính chính có phụ lục.
6. Cột ít nhưng đủ: thông tin phụ đặt ở dòng thứ hai trong ô; thông tin chi tiết hơn chỉ có trong Excel.

### 2.2. Định danh sổ

Góc trên bên phải trang 1: "Mã sổ: SO-0x" và "Mẫu nội bộ — phiên bản 1.0" (BR-IN-01).

### 2.3. Khối đầu sổ (trang 1)

```
[CƠ QUAN CHỦ QUẢN]                                                        Mã sổ: SO-01
[TÊN ĐƠN VỊ] (in đậm)                                           Mẫu nội bộ — phiên bản 1.0

                              SỔ THEO DÕI CBCS RA/VÀO
                Từ 00:00 ngày 25/10/2026 đến hết ngày 25/10/2026

Điểm kiểm soát: Tất cả các cổng        Điều kiện lọc: Không
Số liệu tính đến: 00:00:00 ngày 26/10/2026
```

| Dòng | Nội dung | Nguồn | Ghi chú |
|---|---|---|---|
| 1 | Cơ quan chủ quản (chữ in hoa, thường) | Cấu hình | `XN-03`; bỏ dòng nếu để trống |
| 2 | Tên đơn vị (chữ in hoa, đậm) | Cấu hình | `XN-03` |
| 3 | Tên sổ (in hoa, đậm, 14 pt, căn giữa) | Mục 1 | `XN-04` |
| 4 | Kỳ (căn giữa) | Bộ chọn kỳ | Cách ghi theo BR-KY-02 |
| 5 | Điểm kiểm soát | Bộ lọc cổng | "Tất cả các cổng" hoặc danh sách cổng |
| 6 | Điều kiện lọc | Bộ lọc | "Không" hoặc liệt kê "Tên lọc: giá trị; …". Có lọc thì thêm dòng in nghiêng "Sổ đã lọc — không phải toàn bộ dữ liệu của kỳ" |
| 7 | Số liệu tính đến | Thời điểm chốt | Thêm "(kỳ chưa kết thúc)" nếu Chốt < Đến |
| 8 (khi có) | "Có hiển thị bản ghi đã huỷ (không tính vào số liệu)" | Tuỳ chọn | BR-DC-06 |
| 8 (khi có) | "Dữ liệu cá nhân: hiển thị đầy đủ" | Tuỳ chọn | BR-BM-02 |

Khối đầu sổ **không** có Quốc hiệu, tiêu ngữ, số/ký hiệu văn bản.

### 2.4. Đầu trang rút gọn (từ trang 2)

Một dòng, 8 pt: `[TÊN ĐƠN VỊ] — [Tên sổ] — [Kỳ rút gọn, ví dụ 25/10/2026 hoặc 01/10–31/10/2026]`. Ngay dưới là **dòng tiêu đề bảng lặp lại** (BR-IN-04).

### 2.5. Chân trang (mọi trang)

`SO-01 · Mã trích xuất SO01-20261027-0003 · Trích xuất lúc 09:00:12 27/10/2026 · Mẫu nghiệp vụ nội bộ · Trang 1/3`

Trên màn hình (chưa trích xuất): `Xem lúc 09:00:12 27/10/2026 — chưa phải bản trích xuất` (BR-TX-06).

### 2.6. Định dạng ô dùng chung

| Kiểu dữ liệu | Hiển thị trên màn hình/PDF/Word | Excel |
|---|---|---|
| Thời điểm sự kiện | Dòng 1 `HH:mm dd/mm`; dòng 2 cổng; dòng 3 (nếu có) "(từ kỳ trước)" / "(sau kỳ)" (BR-ND-02…04) | Tách 3 cột: thời điểm (ngày giờ thực, có giây), cổng, chú thích kỳ |
| Chưa có sự kiện đóng | `—` | Ô trống |
| Thời lượng | `hh:mm`; chưa hoàn tất `≥ hh:mm` (BR-ND-05) | Kiểu thời lượng `[h]:mm` + cột "Là thời lượng tối thiểu" |
| Họ tên | Dạng chuẩn NFC, viết hoa chữ cái đầu như đã ghi nhận | Như trên |
| Số giấy tờ | Đã che theo BR-BM-01 | Chuỗi đã che |
| Trạng thái | Nhãn chữ BR-TT-01; chưa hoàn tất in đậm | Hai cột: mã trạng thái, nhãn |
| Ghi chú | Ký hiệu BR-TT-02, cách nhau "; " | Như trên |
| Số liệu tổng | Số nguyên, phân cách hàng nghìn bằng dấu chấm, kèm đơn vị tính | Kiểu số |

**Nội dung dài trong bản Word/PDF.** Nội dung một ô dài hơn 300 ký tự được in đầy đủ ở "Phụ lục nội dung dài" (PL-n) cuối sổ; ô trong bảng in 100 ký tự đầu kèm "… (đầy đủ: PL-n)". Nhờ vậy một dòng bảng không cao quá một trang (BR-IN-09) mà không cắt bỏ dữ liệu. Excel luôn ghi đủ nội dung trong ô.

**Khổ và hướng giấy của bản Word/PDF** được chọn theo bảng rộng nhất của từng phần: mỗi cột có độ rộng tối thiểu (mm); phần mềm chọn khổ đầu tiên đủ rộng theo thứ tự A4 dọc → A4 ngang → A3 ngang (vùng in sau lề 175 / 262 / 385 mm). Với bộ cột hiện tại: SO-01…SO-03 ra A4 ngang; các phần của SO-04 ra A4 dọc.

### 2.7. Khối cuối sổ (sổ chi tiết SO-01…SO-03)

Thứ tự cố định (BR-IN-09):

**(1) TỔNG HỢP SỐ LIỆU** — tiêu đề kèm "(tại thời điểm chốt hh:mm:ss dd/mm/yyyy)". Bảng hai cột "Chỉ tiêu | Số liệu (đơn vị)":

| Chỉ tiêu | Ví dụ SO-01, DS-01, kỳ 25/10 |
|---|---|
| Số lượt trong sổ | 7 lượt |
| — Từ kỳ trước | 1 lượt |
| — Phát sinh trong kỳ | 6 lượt |
| Hoàn tất trong kỳ | 5 lượt |
| Chưa hoàn tất tại thời điểm chốt | 2 lượt (đang mở: 1; hoàn tất sau kỳ: 1) |
| — Trong đó quá hạn | 1 lượt |
| *(chỉ tiêu riêng của sổ, xem mục 3.7, 4.7, 5.7)* | |
| Số lượt có đính chính | 1 lượt |
| Số bản ghi đã huỷ trong kỳ (không tính vào các chỉ tiêu trên) | 1 bản ghi |

Dòng kiểm tra in nhỏ: "Cân đối: Từ kỳ trước + Phát sinh = Hoàn tất + Chưa hoàn tất (1 + 6 = 5 + 2)".
Nếu có lọc: "Số liệu theo điều kiện lọc đã nêu ở đầu sổ."

**(2) CHÚ GIẢI KÝ HIỆU** — chỉ liệt kê ký hiệu xuất hiện trong sổ, kèm câu: "Thời lượng có dấu ≥ là thời lượng tính đến thời điểm chốt của lượt chưa hoàn tất."

**(3) PHỤ LỤC ĐÍNH CHÍNH** (BR-DC-04)

| (n) | STT dòng | Đối tượng | Trường | Giá trị cũ | Giá trị mới | Lý do | Người đính chính | Thời điểm đính chính |
|---|---|---|---|---|---|---|---|---|
| (1) | 4 | CB005 Hoàng Văn Đức | Thời điểm vào | 09:14 25/10/2026 | 09:40 25/10/2026 | Nhập nhầm giờ | Lê Thị Y (trucban02) | 20:00 25/10/2026 |

Không có đính chính: "Không có đính chính."

**(4) THÔNG TIN TRÍCH XUẤT**

```
Mã trích xuất: SO01-20261027-0003          Định dạng: PDF
Thời điểm trích xuất: 09:00:12 ngày 27/10/2026 (giờ máy chủ)
Người trích xuất: Nguyễn Văn X (tài khoản: trucban01)
Kỳ: [Từ, Đến) như đầu sổ — Số liệu tính đến: 00:00:00 ngày 26/10/2026
Số liệu phản ánh dữ liệu đã ghi nhận trong hệ thống tại thời điểm trích xuất.
```

**(5) KHỐI KÝ** (chỉ in khi đơn vị đã phê duyệt cấu hình, `XN-14`)

Phần mềm chỉ in khối ký khi quản trị bật "Khối ký đã được đơn vị phê duyệt" và ghi căn cứ phê duyệt. Danh sách ô ký (chức danh, ô nào ghi tên người lập sổ, áp dụng cho sổ nào) và việc điền sẵn ngày ký lấy từ cấu hình đó. Chưa phê duyệt thì mọi định dạng (Excel, Word, PDF) chỉ in "— Hết sổ —", không in mẫu ký mặc định. Bố cục dưới đây là đề xuất cấu hình ban đầu.

```
                                                   [Địa danh], ngày ..... tháng ..... năm ..........
          NGƯỜI LẬP SỔ                                          [CHỨC DANH XÁC NHẬN]
       (Ký, ghi rõ họ tên)                                       (Ký, ghi rõ họ tên)



        [Họ tên người lập sổ]                               ...............................

                                        — Hết sổ —
```

- Người lập sổ: theo BR-TX-04 (mặc định người trích xuất; "Để trống — ký tay" thì in dòng chấm).
- Chức danh xác nhận, số ô ký, địa danh: cấu hình (REQ-GEN-21). Ngày ký để trống mặc định.

### 2.8. Giao diện màn hình (chung)

```
┌ Bộ lọc ────────────────────────────────────────────────────────────────────────────┐
│ Kỳ: [Hôm nay ▾] Từ [25/10/2026 00:00] Đến [26/10/2026 00:00]   Cổng: [Tất cả ▾]      │
│ (bộ lọc riêng của sổ …)                      [Xem]  [Đặt lại]                       │
└────────────────────────────────────────────────────────────────────────────────────┘
 Xem lúc 09:00:12 27/10/2026 — chưa phải bản trích xuất
 ┌ Tóm tắt ──────────────────────────────────────────────────────────────────────────┐
 │ 7 lượt trong sổ · 5 hoàn tất · 2 chưa hoàn tất (1 quá hạn) · 6 CBCS               │
 └───────────────────────────────────────────────────────────────────────────────────┘
 [In] [Xuất PDF] [Xuất Word] [Xuất Excel]      Sắp xếp: [Thời điểm mở ▾]  [□ Hiện bản ghi đã huỷ]
 ┌ Bảng (tiêu đề cố định khi cuộn; cùng cột với bản in) ─────────────────────────────┐
 └───────────────────────────────────────────────────────────────────────────────────┘
 Khối tổng hợp, phụ lục đính chính (thu gọn được)
```

- Phân trang 100 dòng/trang màn hình (không ảnh hưởng STT).
- Cùng nội dung với bản in (BR-IN-08); nhãn trạng thái có thể có màu nền nhưng luôn có chữ.
- Hộp thoại xuất: chọn Người lập sổ (BR-TX-04); với SO-02, chọn mức hiển thị dữ liệu cá nhân nếu có quyền.

---

## 3. SO-01 — Sổ theo dõi CBCS ra/vào

### 3.1. Mục đích và đối tượng sử dụng

- **Mục đích:** ghi lại đầy đủ từng lượt CBCS ra khỏi/vào đơn vị qua các điểm kiểm soát trong một kỳ; nắm CBCS chưa về (hoặc chưa ra) tại thời điểm chốt; làm căn cứ giao ca, kiểm tra.
- **Đối tượng sử dụng:** trực ban/bảo vệ cổng (lập, in theo ca), chỉ huy trực/chỉ huy đơn vị (kiểm tra, ký xác nhận), cán bộ tổ chức/hành chính (tra cứu).

### 3.2. Tên sổ và tiêu đề

- Tên sổ: **SỔ THEO DÕI CBCS RA/VÀO** (`XN-04`).
- Tiêu đề và đầu trang: theo mục 2.3–2.5.

### 3.3. Thông tin đầu trang riêng

Không có dòng riêng ngoài mục 2.3. Điều kiện lọc có thể gồm: Đơn vị/bộ phận, CBCS, Chiều lượt, Lý do, Trạng thái, Chỉ dòng có đính chính.

### 3.4. Danh sách cột

| TT | Mã cột | Tiêu đề cột | Nội dung và ý nghĩa | Độ rộng (%) |
|---|---|---|---|---|
| 1 | SO1-C01 | STT | Dòng 1: số thứ tự liên tục toàn sổ (BR-IN-07), dòng huỷ "—"; dòng 2: "#<mã lượt>" để đối chiếu với bản ghi gốc (in cỡ 7,5 pt để mã nhiều chữ số không bị ngắt) | 6 |
| 2 | SO1-C02 | Mã CBCS | Mã CBCS nội bộ (định danh, BR-DN-01) | 6 |
| 3 | SO1-C03 | Họ và tên | Dòng 1: họ tên; dòng 2: cấp bậc, chức vụ (`XN-06`) | 11 |
| 4 | SO1-C04 | Đơn vị / bộ phận | Đơn vị/bộ phận công tác tại thời điểm mở lượt | 9 |
| 5 | SO1-C05 | Chiều lượt | "Ra–Vào" hoặc "Vào–Ra" (BR-LT-02) | 6 |
| 6 | SO1-C06 | Ra | Thời điểm, cổng, chú thích kỳ của sự kiện Ra (mục 2.6) | 9 |
| 7 | SO1-C07 | Vào | Thời điểm, cổng, chú thích kỳ của sự kiện Vào | 9 |
| 8 | SO1-C08 | Thời lượng (giờ:phút) | Khoảng giữa hai sự kiện (BR-ND-05); với Ra–Vào là thời gian vắng mặt, với Vào–Ra là thời gian có mặt | 5 |
| 9 | SO1-C09 | Lý do / nội dung | Theo danh mục `XN-07` và ghi chú lý do; dòng 2: "Hạn về hh:mm dd/mm" nếu có | 10 |
| 10 | SO1-C10 | Phương tiện đi kèm | Biển số phương tiện liên kết (BR-LT-05); không có: "—" | 8 |
| 11 | SO1-C11 | Người ghi nhận | Dòng 1 "R: <người ghi sự kiện Ra>"; dòng 2 "V: <người ghi sự kiện Vào>" (họ tên viết tắt hoặc tên đăng nhập) | 8 |
| 12 | SO1-C12 | Trạng thái | Nhãn BR-TT-01 | 7 |
| 13 | SO1-C13 | Ghi chú | Ký hiệu BR-TT-02 | 6 |
| | | | **Tổng** | **100** |

Thứ tự "Ra" trước "Vào" vì phần lớn lượt CBCS là Ra–Vào (đề xuất, `XN-05`). Với lượt Vào–Ra, cột "Chiều lượt" giúp đọc đúng trình tự.

Cột chỉ có trong Excel: thời điểm ghi nhận từng sự kiện; mã bản ghi lượt; mã trạng thái; thời lượng tính bằng phút.

### 3.5. Bộ lọc

| Bộ lọc | Kiểu | Mặc định |
|---|---|---|
| Kỳ | Lựa chọn nhanh / Từ–Đến (BR-KY-02, BR-KY-03) | Hôm nay |
| Cổng | Chọn nhiều (BR-KY-07) | Tất cả |
| Đơn vị / bộ phận | Chọn nhiều, gồm đơn vị con | Tất cả |
| CBCS | Tìm theo mã hoặc họ tên | Tất cả |
| Chiều lượt | Ra–Vào / Vào–Ra / Tất cả | Tất cả |
| Lý do | Chọn nhiều theo danh mục | Tất cả |
| Trạng thái | Hoàn tất / Chưa hoàn tất / Quá hạn / Hoàn tất sau kỳ / Tất cả | Tất cả |
| Chỉ dòng có đính chính | Có / Không | Không |
| Hiện bản ghi đã huỷ | Có / Không (theo quyền) | Không |

### 3.6. Khoảng thời gian và sắp xếp

- Tập lượt theo BR-KY-05; thời điểm chốt theo BR-KY-04; giới hạn kỳ BR-KY-06.
- Sắp xếp mặc định: thời điểm mở lượt ↑, mã bản ghi ↑.
- Sắp xếp tuỳ chọn: (a) Họ tên ↑ (theo tên, rồi họ và tên đệm; thứ tự chữ cái tiếng Việt), thời điểm mở ↑; (b) Đơn vị ↑, họ tên ↑, thời điểm mở ↑; (c) Trạng thái (chưa hoàn tất trước), thời điểm mở ↑. Khoá phụ cuối luôn là mã bản ghi ↑.

### 3.7. Quy tắc tính tổng

Chỉ tiêu chung mục 2.7 (1) và chỉ tiêu riêng:

| Chỉ tiêu riêng | Định nghĩa | DS-01, kỳ 25/10 |
|---|---|---|
| Số CBCS duy nhất | Số mã CBCS khác nhau trong tập lượt (BR-DN-01, BR-DN-04) | 6 đối tượng |
| Số lượt theo chiều | Ra–Vào; Vào–Ra | 6 lượt; 1 lượt |
| Số lượt theo lý do | Mỗi lý do một dòng (bỏ lý do có 0 lượt) | Công tác 4; Việc riêng có phép 2; Không ghi 1 |

### 3.8. Hiển thị trạng thái

Theo BR-TT-01. Lượt Ra–Vào chưa đóng: "Chưa về"; Vào–Ra chưa đóng: "Chưa ra"; kèm "– Quá hạn" khi quá "Hạn về" (BR-CHT-04).

### 3.9. Khổ giấy, tiêu đề lặp, ký xác nhận

- A4 ngang, lề và phông theo BR-IN-02.
- Lặp đầu trang rút gọn và dòng tiêu đề bảng từ trang 2 (BR-IN-04).
- Khối ký: "Người lập sổ" và chức danh xác nhận (đề xuất "Chỉ huy đơn vị", `XN-14`).

### 3.10. Lượt chưa hoàn tất, qua nửa đêm, dữ liệu đính chính

| Tình huống | Cách thể hiện | Quy tắc |
|---|---|---|
| Đang mở tại chốt | Ô Vào (hoặc Ra với Vào–Ra) "—"; thời lượng "≥ hh:mm"; dòng in đậm; "Chưa về"/"Chưa ra" | BR-CHT-01…04 |
| Mở trước kỳ | Ô sự kiện mở thêm "(từ kỳ trước)"; đếm "Từ kỳ trước" | BR-ND-03 |
| Đóng sau chốt | Ô sự kiện đóng thêm "(sau kỳ)"; "Hoàn tất sau kỳ"; đếm "Chưa hoàn tất" | BR-ND-04 |
| Qua nửa đêm trong kỳ | Một dòng; ô thời điểm có ngày | BR-ND-01, BR-ND-02 |
| Có đính chính | Giá trị hiện hành; `ĐC(n)`; Phụ lục đính chính | BR-DC-03, BR-DC-04 |
| Ghi bổ sung | `GBS` | BR-DC-08 |
| Bản ghi huỷ | Ẩn; khi hiện: STT "—", "ĐÃ HUỶ", lý do huỷ | BR-DC-06 |

### 3.11. Thời điểm trích xuất và người lập sổ

Theo mục 2.5, 2.7 (4), (5) và BR-TX-01…BR-TX-05.

---

## 4. SO-02 — Sổ theo dõi khách ra/vào

### 4.1. Mục đích và đối tượng sử dụng

- **Mục đích:** ghi lại từng lượt khách vào/ra; biết khách nào còn trong đơn vị, thẻ khách nào chưa thu hồi tại thời điểm chốt; làm căn cứ kiểm tra công tác tiếp khách.
- **Đối tượng sử dụng:** trực ban/bảo vệ cổng, chỉ huy trực, bộ phận tiếp khách (tra cứu khách của mình).

### 4.2. Tên sổ và tiêu đề

**SỔ THEO DÕI KHÁCH RA/VÀO** (`XN-04`); đầu trang theo mục 2.3–2.5.

### 4.3. Thông tin đầu trang riêng

Thêm dòng "Dữ liệu cá nhân: số giấy tờ đã che" (hoặc "hiển thị đầy đủ", BR-BM-01, BR-BM-02).

### 4.4. Danh sách cột

| TT | Mã cột | Tiêu đề cột | Nội dung và ý nghĩa | Độ rộng (%) |
|---|---|---|---|---|
| 1 | SO2-C01 | STT | Như SO-01 | 6 |
| 2 | SO2-C02 | Khách | Dòng 1: họ tên; dòng 2: cơ quan/địa chỉ; dòng 3 (nếu có): "Đoàn <mã đoàn>" | 13 |
| 3 | SO2-C03 | Giấy tờ | Loại và số giấy tờ (đã che theo BR-BM-01); không có: "Không xuất trình" | 9 |
| 4 | SO2-C04 | Mục đích | Nội dung làm việc | 9 |
| 5 | SO2-C05 | Người / bộ phận tiếp | Họ tên CBCS tiếp (kèm mã) hoặc bộ phận | 10 |
| 6 | SO2-C06 | Số thẻ | Số thẻ khách đã cấp; không cấp: "—" | 4 |
| 7 | SO2-C07 | Vào | Thời điểm, cổng, chú thích kỳ của sự kiện Vào | 9 |
| 8 | SO2-C08 | Ra | Thời điểm, cổng, chú thích kỳ của sự kiện Ra | 9 |
| 9 | SO2-C09 | Thời lượng (giờ:phút) | Thời gian khách ở trong đơn vị (BR-ND-05) | 5 |
| 10 | SO2-C10 | Phương tiện | Biển số phương tiện của khách (BR-LT-05) | 6 |
| 11 | SO2-C11 | Người ghi nhận | "V: …" / "R: …" | 7 |
| 12 | SO2-C12 | Trạng thái | Nhãn BR-TT-01 (khách luôn Vào–Ra: "Chưa ra") | 7 |
| 13 | SO2-C13 | Ghi chú | Ký hiệu BR-TT-02 | 6 |
| | | | **Tổng** | **100** |

Thứ tự "Vào" trước "Ra" vì lượt khách luôn là Vào–Ra.

Cột chỉ có trong Excel: số điện thoại (chỉ khi `XN-08` đồng ý), giờ ra dự kiến, thời điểm ghi nhận, mã bản ghi, mã trạng thái.

### 4.5. Bộ lọc

Kỳ; Cổng; Mục đích; Người/bộ phận tiếp; Đoàn; Khách (tìm theo họ tên hoặc số giấy tờ — tìm theo số giấy tờ chỉ khớp chính xác); Số thẻ; Trạng thái; Chỉ khách quá hạn; Chỉ dòng có đính chính; Hiện bản ghi đã huỷ. Mặc định như SO-01.

### 4.6. Khoảng thời gian và sắp xếp

- Như SO-01 (mục 3.6).
- Sắp xếp tuỳ chọn: (a) Người/bộ phận tiếp ↑, thời điểm vào ↑; (b) Đoàn ↑, họ tên ↑; (c) Trạng thái (chưa ra trước), thời điểm vào ↑.

### 4.7. Quy tắc tính tổng

| Chỉ tiêu riêng | Định nghĩa | DS-01, kỳ 25/10 |
|---|---|---|
| Số khách có định danh duy nhất | BR-DN-02 | 4 đối tượng |
| Số lượt khách không định danh | Ghi riêng, **không cộng** vào dòng trên | 1 lượt |
| Số đoàn | Số mã đoàn khác nhau | 1 đoàn |
| Thẻ khách chưa thu hồi tại thời điểm chốt | Số lượt có thẻ và chưa có sự kiện Ra trước chốt | 2 thẻ (K05, K06) |

### 4.8. Hiển thị trạng thái

"Hoàn tất", "**Chưa ra**", "**Chưa ra – Quá hạn**" (quá giờ ra dự kiến, `XN-09`), "Hoàn tất sau kỳ".

### 4.9. Khổ giấy, tiêu đề lặp, ký xác nhận

Như SO-01 (mục 3.9).

### 4.10. Lượt chưa hoàn tất, qua nửa đêm, dữ liệu đính chính

Như SO-01 (mục 3.10). Bổ sung: đính chính số giấy tờ được ghi trong phụ lục với giá trị cũ/mới **đã che** theo cùng mức hiển thị của bản xuất.

### 4.11. Thời điểm trích xuất và người lập sổ

Như SO-01. Khối "Thông tin trích xuất" ghi thêm mức hiển thị dữ liệu cá nhân.

---

## 5. SO-03 — Sổ theo dõi phương tiện ra/vào

### 5.1. Mục đích và đối tượng sử dụng

- **Mục đích:** ghi lại từng lượt phương tiện qua điểm kiểm soát; biết phương tiện nào chưa về/chưa ra tại thời điểm chốt; đối chiếu với lệnh điều xe (nếu có).
- **Đối tượng sử dụng:** trực ban/bảo vệ cổng, chỉ huy trực, bộ phận quản lý xe.

### 5.2. Tên sổ và tiêu đề

**SỔ THEO DÕI PHƯƠNG TIỆN RA/VÀO** (`XN-04`); đầu trang theo mục 2.3–2.5.

### 5.3. Thông tin đầu trang riêng

Điều kiện lọc có thể gồm: Biển số, Loại phương tiện, Nguồn, Người điều khiển, Chiều lượt, Trạng thái.

### 5.4. Danh sách cột

| TT | Mã cột | Tiêu đề cột | Nội dung và ý nghĩa | Độ rộng (%) |
|---|---|---|---|---|
| 1 | SO3-C01 | STT | Như SO-01 | 6 |
| 2 | SO3-C02 | Biển số | Như đã ghi nhận; xe không biển: "Không biển — <mã tạm>" | 8 |
| 3 | SO3-C03 | Loại phương tiện | Ô tô, xe máy, xe chuyên dùng, … (danh mục) | 7 |
| 4 | SO3-C04 | Nguồn | "Cơ quan"; "CBCS — <họ tên>"; "Khách — <họ tên>"; "Khác — <ghi rõ>" | 8 |
| 5 | SO3-C05 | Người điều khiển | Họ tên (kèm mã CBCS nếu có) (REQ-SO3-03) | 11 |
| 6 | SO3-C06 | Chiều lượt | "Ra–Vào" / "Vào–Ra" | 6 |
| 7 | SO3-C07 | Ra | Thời điểm, cổng, chú thích kỳ | 9 |
| 8 | SO3-C08 | Vào | Thời điểm, cổng, chú thích kỳ | 9 |
| 9 | SO3-C09 | Thời lượng (giờ:phút) | BR-ND-05 | 5 |
| 10 | SO3-C10 | Lý do / lệnh điều xe | Lý do; dòng 2: số lệnh điều xe, hạn về (`XN-26`) | 10 |
| 11 | SO3-C11 | Người ghi nhận | "R: …" / "V: …" | 7 |
| 12 | SO3-C12 | Trạng thái | Nhãn BR-TT-01 | 7 |
| 13 | SO3-C13 | Ghi chú | Ký hiệu BR-TT-02 | 7 |
| | | | **Tổng** | **100** |

Cột chỉ có trong Excel: biển số chuẩn hoá (BR-DN-03), hàng hoá/tài sản, số người trên xe (`XN-26`), thời điểm ghi nhận, mã bản ghi.

### 5.5. Bộ lọc

Kỳ; Cổng; Biển số (tìm theo biển số chuẩn hoá, khớp một phần); Loại phương tiện; Nguồn; Người điều khiển; Chiều lượt; Trạng thái; Chỉ dòng có đính chính; Hiện bản ghi đã huỷ.

### 5.6. Khoảng thời gian và sắp xếp

- Như SO-01.
- Sắp xếp tuỳ chọn: (a) Biển số chuẩn hoá ↑, thời điểm mở ↑; (b) Nguồn ↑, biển số ↑; (c) Trạng thái (chưa hoàn tất trước), thời điểm mở ↑.

### 5.7. Quy tắc tính tổng

| Chỉ tiêu riêng | Định nghĩa | DS-01, kỳ 25/10 |
|---|---|---|
| Số phương tiện có biển duy nhất | BR-DN-03 | 3 đối tượng |
| Số lượt phương tiện không biển | Ghi riêng, không cộng vào dòng trên | 1 lượt |
| Số lượt theo loại phương tiện | Mỗi loại một dòng | Ô tô 3; Xe máy 1; Xe chuyên dùng 1 |
| Số lượt theo nguồn | Mỗi nguồn một dòng | Cơ quan 2; CBCS 1; Khách 1; Khác 1 |

### 5.8. Hiển thị trạng thái

Như SO-01: "Chưa về" (Ra–Vào), "Chưa ra" (Vào–Ra), "– Quá hạn" theo hạn về của lệnh điều xe (`XN-09`).

### 5.9. – 5.11.

Khổ giấy, tiêu đề lặp, ký xác nhận; lượt chưa hoàn tất, qua nửa đêm, đính chính; thời điểm trích xuất và người lập sổ: như SO-01 (mục 3.9–3.11). Đính chính biển số: sổ dùng biển số hiện hành, đếm duy nhất theo biển số hiện hành (BR-DN-06).

---

## 6. SO-04 — Sổ tổng hợp ra/vào

### 6.1. Mục đích và đối tượng sử dụng

- **Mục đích:** cung cấp số liệu tổng hợp của ba nhóm đối tượng trong một kỳ (ca, ngày, tuần, tháng) mà **không trộn lẫn** các nhóm; nêu các lượt chưa hoàn tất cần xử lý khi giao ca; tóm tắt đính chính/huỷ.
- **Đối tượng sử dụng:** chỉ huy trực, chỉ huy và lãnh đạo đơn vị; trực ban khi giao ca.

### 6.2. Tên sổ và tiêu đề

**SỔ TỔNG HỢP RA/VÀO** (`XN-04`); đầu trang theo mục 2.3–2.5.

### 6.3. Thông tin đầu trang riêng

Thêm dòng: "Nhóm đối tượng: CBCS, Khách, Phương tiện" (theo bộ lọc nhóm) và "Phân bổ: theo ngày lịch" (hoặc "theo ca trực", `XN-25`).

### 6.4. Cấu trúc và danh sách cột

Ghi chú đầu bảng Phần A (in nghiêng): *"Số liệu của từng nhóm đối tượng được tính riêng và không cộng gộp giữa các nhóm."*

**Phần A — Chỉ tiêu theo nhóm đối tượng** (một dòng mỗi nhóm; **không có dòng tổng cộng**)

| TT | Mã cột | Tiêu đề cột | Đơn vị | Định nghĩa |
|---|---|---|---|---|
| 1 | SO4A-C01 | Nhóm đối tượng | — | CBCS / Khách / Phương tiện |
| 2 | SO4A-C02 | Từ kỳ trước | lượt | BR-TONG-01 (1) |
| 3 | SO4A-C03 | Phát sinh trong kỳ | lượt | BR-TONG-01 (2) |
| 4 | SO4A-C04 | Hoàn tất trong kỳ | lượt | BR-TONG-01 (3) |
| 5 | SO4A-C05 | Chưa hoàn tất tại thời điểm chốt | lượt | BR-TONG-01 (4) |
| 6 | SO4A-C06 | Trong đó quá hạn | lượt | BR-TONG-01 (4a) |
| 7 | SO4A-C07 | Đối tượng duy nhất (có định danh) | đối tượng | BR-DN-01…04 |
| 8 | SO4A-C08 | Lượt không định danh | lượt | BR-DN-02, BR-DN-03; CBCS: "—" |
| 9 | SO4A-C09 | Lượt có đính chính | lượt | BR-DC-04 |
| 10 | SO4A-C10 | Bản ghi đã huỷ (không tính) | bản ghi | BR-TONG-02 |
| 11 | SO4A-C11 | Đối chiếu sổ riêng | — | Mã sổ riêng tương ứng (SO-01/02/03) |

Tiêu đề cột hai tầng: tầng 1 nhóm "SỐ LƯỢT" (C02–C06, C08, C09) và "SỐ ĐỐI TƯỢNG" (C07), để người đọc thấy rõ hai loại đơn vị.

**Phần B — Phân bổ theo ngày** (hoặc theo ca)

| Cột | Tiêu đề | Đơn vị | Dòng cuối |
|---|---|---|---|
| B-C01 | Ngày | — | "Cộng / Duy nhất cả kỳ" |
| B-C02 | CBCS — lượt phát sinh | lượt | Cộng các ngày |
| B-C03 | CBCS — có hoạt động | đối tượng | Duy nhất cả kỳ (không cộng) |
| B-C04 | Khách — lượt phát sinh | lượt | Cộng các ngày |
| B-C05 | Khách — có định danh có hoạt động | đối tượng | Duy nhất cả kỳ (không cộng) |
| B-C06 | Phương tiện — lượt phát sinh | lượt | Cộng các ngày |
| B-C07 | Phương tiện — có biển có hoạt động | đối tượng | Duy nhất cả kỳ (không cộng) |

Quy tắc: BR-ND-06, BR-TONG-07. Chú thích dưới bảng: *"Cột 'có hoạt động' đếm đối tượng có ít nhất một lượt trong ngày; một đối tượng có thể có mặt ở nhiều ngày nên dòng cuối là số đối tượng duy nhất của cả kỳ, không phải tổng các ngày."*

**Phần C — Phân bổ theo cổng** (đếm sự kiện, BR-TONG-08)

| Cột | Tiêu đề | Đơn vị |
|---|---|---|
| C-C01 | Cổng | — |
| C-C02, C-C03 | CBCS — sự kiện Vào / Ra | sự kiện |
| C-C04, C-C05 | Khách — sự kiện Vào / Ra | sự kiện |
| C-C06, C-C07 | Phương tiện — sự kiện Vào / Ra | sự kiện |

Dòng cuối "Cộng" theo từng cột (cộng trong cùng nhóm, cùng loại sự kiện).

**Phần D — Lượt chưa hoàn tất tại thời điểm chốt** (ba bảng con D1 CBCS, D2 Khách, D3 Phương tiện; mỗi bảng có số lượng riêng, không cộng chung)

| Cột | Nội dung |
|---|---|
| STT (theo bảng con) | |
| Đối tượng | Mã + họ tên (CBCS); họ tên + số thẻ (khách); biển số + loại (phương tiện) |
| Sự kiện mở | Chiều, thời điểm, cổng |
| Hạn dự kiến | Nếu có |
| Thời lượng tính đến chốt | `≥ hh:mm` |
| Trạng thái | "Chưa về", "Chưa ra", "– Quá hạn", "Hoàn tất sau kỳ" |
| Dòng chi tiết | STT dòng tương ứng trong sổ riêng cùng điều kiện |

Sắp xếp: quá hạn trước, sau đó thời điểm mở ↑.

**Phần E — Tóm tắt đính chính và huỷ**

| Nhóm | Số lượt có đính chính | Số đính chính | Số bản ghi đã huỷ | Xem chi tiết |
|---|---|---|---|---|
| CBCS / Khách / Phương tiện | lượt | lần | bản ghi | "Phụ lục đính chính của SO-0x" |

**Phần F — Nhật ký hợp nhất** (tuỳ chọn, `XN-19`): mọi sự kiện của ba nhóm theo thời điểm ↑ — cột: STT, thời điểm, cổng, nhóm, loại sự kiện, đối tượng, mã lượt, ghi chú. Không có tổng.

### 6.5. Bộ lọc

Kỳ; Cổng; Nhóm đối tượng (chọn nhiều, mặc định cả ba); Phân bổ (theo ngày / theo ca); Các phần cần in (A–E mặc định chọn; F tuỳ chọn). Không có bộ lọc theo từng đối tượng (dùng sổ riêng).

### 6.6. Khoảng thời gian và sắp xếp

- Kỳ, thời điểm chốt, tập lượt: như sổ riêng (BR-KY-04, BR-KY-05), áp dụng riêng cho từng nhóm.
- Thứ tự dòng Phần A cố định: CBCS, Khách, Phương tiện. Phần B: ngày ↑. Phần C: thứ tự cổng theo danh mục.

### 6.7. Quy tắc tính tổng

- Phần A khớp sổ riêng (BR-TONG-06); không cộng chéo nhóm (BR-TONG-04); đẳng thức cân đối đúng cho từng dòng.
- Phần B, C: dòng cuối theo BR-TONG-07.
- Phần D: số lượng mỗi bảng con bằng cột C05 của nhóm tương ứng ở Phần A.

### 6.8. Hiển thị trạng thái

Phần D dùng nhãn BR-TT-01. Phần A–C không có trạng thái dòng.

### 6.9. Khổ giấy, tiêu đề lặp, ký xác nhận

- A4 dọc (Phần D, F được phép chuyển trang ngang nếu đơn vị chọn).
- Mỗi Phần bắt đầu bằng tiêu đề phần; bảng dài sang trang thì lặp tiêu đề bảng.
- Khối ký: như sổ riêng; chức danh xác nhận có thể khác (cấu hình riêng cho SO-04, `XN-14`).

### 6.10. Lượt chưa hoàn tất, qua nửa đêm, dữ liệu đính chính

Tính theo đúng quy tắc của sổ riêng; SO-04 không có phụ lục đính chính chi tiết, chỉ có Phần E và tham chiếu.

### 6.11. Thời điểm trích xuất và người lập sổ

Như sổ riêng. Một lần xuất SO-04 dùng **một** thời điểm trích xuất và một phiên đọc nhất quán cho cả ba nhóm (BR-TX-01).

---

## 7. Bản mẫu bố cục (dữ liệu DS-01)

Bản mẫu dưới đây chỉ minh hoạ bố cục và quy tắc; độ rộng thực tế theo tỷ lệ ở các bảng cột.

### 7.1. SO-01, kỳ 25/10/2026, trích xuất 09:00:12 ngày 27/10/2026

```
[CƠ QUAN CHỦ QUẢN]                                                                                       Mã sổ: SO-01
[TÊN ĐƠN VỊ]                                                                               Mẫu nội bộ — phiên bản 1.0
                                            SỔ THEO DÕI CBCS RA/VÀO
                              Từ 00:00 ngày 25/10/2026 đến hết ngày 25/10/2026
Điểm kiểm soát: Tất cả các cổng      Điều kiện lọc: Không      Số liệu tính đến: 00:00:00 ngày 26/10/2026

┌───┬───────┬────────────────┬───────────┬───────┬──────────────┬──────────────┬───────┬──────────────┬────────────┬──────────┬──────────────┬───────┐
│STT│Mã CBCS│Họ và tên       │Đơn vị     │Chiều  │Ra            │Vào           │Thời   │Lý do /       │Phương tiện │Người ghi │Trạng thái    │Ghi chú│
│   │       │                │           │lượt   │              │              │lượng  │nội dung      │đi kèm      │nhận      │              │       │
├───┼───────┼────────────────┼───────────┼───────┼──────────────┼──────────────┼───────┼──────────────┼────────────┼──────────┼──────────────┼───────┤
│ 1 │CB002  │Trần Thị Bình   │P. Hậu cần │Ra–Vào │23:30 24/10   │01:15 25/10   │ 01:45 │Việc riêng có │—           │R: tb03   │Hoàn tất      │       │
│   │       │                │           │       │Cổng 1        │Cổng 1        │       │phép          │            │V: tb01   │              │       │
│   │       │                │           │       │(từ kỳ trước) │              │       │              │            │          │              │       │
│ 2 │CB007  │Đặng Quốc Hưng  │P. Tham mưu│Vào–Ra │17:15 25/10   │07:30 25/10   │ 09:45 │—             │—           │V: tb01   │Hoàn tất      │       │
│   │       │                │           │       │Cổng 1        │Cổng 1        │       │              │            │R: tb02   │              │       │
│ 3 │CB001  │Nguyễn Văn An   │P. Tham mưu│Ra–Vào │08:00 25/10   │10:30 25/10   │ 02:30 │Công tác      │30A-123.45  │…         │Hoàn tất      │       │
│ 4 │CB005  │Hoàng Văn Đức   │P. Kỹ thuật│Ra–Vào │09:00 25/10   │09:40 25/10   │ 00:40 │Công tác      │—           │…         │Hoàn tất      │ĐC(1)  │
│ 5 │CB001  │Nguyễn Văn An   │P. Tham mưu│Ra–Vào │14:00 25/10   │15:00 25/10   │ 01:00 │Công tác      │30A12345    │…         │Hoàn tất      │       │
│   │       │                │           │       │Cổng 2        │Cổng 2        │       │              │            │          │              │       │
│ 6 │CB004  │Phạm Thị Dung   │P. Hậu cần │Ra–Vào │16:00 25/10   │—             │≥ 08:00│Việc riêng có │29X1-111.11 │…         │CHƯA VỀ –     │       │
│   │       │                │           │       │Cổng 1        │              │       │phép          │            │          │QUÁ HẠN       │       │
│   │       │                │           │       │              │              │       │Hạn về 18:00  │            │          │              │       │
│ 7 │CB003  │Lê Văn Cường    │P. Kỹ thuật│Ra–Vào │22:45 25/10   │00:20 26/10   │ 01:35 │Công tác      │—           │…         │Hoàn tất sau  │       │
│   │       │                │           │       │Cổng 2        │Cổng 1        │       │              │            │          │kỳ            │       │
│   │       │                │           │       │              │(sau kỳ)      │       │              │            │          │              │       │
└───┴───────┴────────────────┴───────────┴───────┴──────────────┴──────────────┴───────┴──────────────┴────────────┴──────────┴──────────────┴───────┘
(dòng 6 in đậm toàn dòng; dòng 3–7 lược bớt cổng/người ghi nhận cho gọn bản mẫu)

TỔNG HỢP SỐ LIỆU (tại thời điểm chốt 00:00:00 ngày 26/10/2026)
  Số lượt trong sổ: 7 lượt  (từ kỳ trước: 1 lượt; phát sinh trong kỳ: 6 lượt)
  Hoàn tất trong kỳ: 5 lượt
  Chưa hoàn tất tại thời điểm chốt: 2 lượt (đang mở: 1; hoàn tất sau kỳ: 1) — trong đó quá hạn: 1 lượt
  Số CBCS duy nhất: 6 đối tượng
  Theo chiều lượt: Ra–Vào 6 lượt; Vào–Ra 1 lượt
  Số lượt có đính chính: 1 lượt.   Số bản ghi đã huỷ trong kỳ (không tính): 1 bản ghi
  Cân đối: 1 + 6 = 5 + 2

CHÚ GIẢI KÝ HIỆU: ĐC(n) — có đính chính, xem Phụ lục mục (n); ≥ — thời lượng tính đến thời điểm chốt;
(từ kỳ trước) — sự kiện xảy ra trước kỳ; (sau kỳ) — sự kiện xảy ra sau thời điểm chốt.

PHỤ LỤC ĐÍNH CHÍNH
  (1) Dòng 4 — CB005 Hoàng Văn Đức — Thời điểm vào: 09:14 25/10/2026 → 09:40 25/10/2026
      Lý do: Nhập nhầm giờ — Người đính chính: Lê Thị Y (trucban02) — 20:00 25/10/2026

THÔNG TIN TRÍCH XUẤT … (mục 2.7 (4))          KHỐI KÝ … (mục 2.7 (5))          — Hết sổ —

SO-01 · Mã trích xuất SO01-20261027-0003 · Trích xuất lúc 09:00:12 27/10/2026 · Mẫu nghiệp vụ nội bộ · Trang 1/1
```

### 7.2. SO-02, kỳ 25/10/2026 (rút gọn cột)

```
STT│Khách                    │Giấy tờ           │Số thẻ│Vào               │Ra                 │TL     │Trạng thái        │Ghi chú
 1 │Bùi Văn Lâm              │CCCD ********0111 │K01   │08:30 25/10 Cổng 1│09:45 25/10 Cổng 1 │ 01:15 │Hoàn tất          │
 2 │Mai Thị Ngọc / Đoàn ĐK-01│CCCD ********0222 │K03   │10:00 25/10 Cổng 1│11:00 25/10 Cổng 1 │ 01:00 │Hoàn tất          │
 3 │Tạ Văn Phúc / Đoàn ĐK-01 │CCCD ********0333 │K04   │10:00 25/10 Cổng 1│11:05 25/10 Cổng 1 │ 01:05 │Hoàn tất          │GBS
 4 │Bùi Văn Lâm              │CCCD ********0111 │K02   │14:00 25/10 Cổng 1│14:30 25/10 Cổng 1 │ 00:30 │Hoàn tất          │
 5 │Ông Quang                │Không xuất trình  │K05   │15:00 25/10 Cổng 1│—                  │≥ 09:00│CHƯA RA – QUÁ HẠN │
 6 │Lý Thị Sen               │CCCD ********0444 │K06   │17:30 25/10 Cổng 1│00:10 26/10 Cổng 1 │ 06:40 │Hoàn tất sau kỳ   │
   │                         │                  │      │                  │(sau kỳ)           │       │                  │
Tổng hợp: 6 lượt (từ kỳ trước 0; phát sinh 6) · hoàn tất 4 · chưa hoàn tất 2 (đang mở 1; hoàn tất sau kỳ 1; quá hạn 1)
          Khách có định danh duy nhất: 4 đối tượng · Lượt khách không định danh: 1 lượt · Số đoàn: 1 · Thẻ chưa thu hồi: 2
```

### 7.3. SO-03, kỳ 25/10/2026 (rút gọn cột)

```
STT│Biển số             │Loại          │Nguồn                  │Người điều khiển    │Chiều │Ra                │Vào               │TL     │Trạng thái
 1 │30A-123.45          │Ô tô          │Cơ quan                │Nguyễn Văn An (CB001)│Ra–Vào│08:00 25/10 Cổng 1│10:30 25/10 Cổng 1│ 02:30 │Hoàn tất
 2 │29B-678.90          │Ô tô          │Khách — Bùi Văn Lâm    │Bùi Văn Lâm         │Vào–Ra│09:50 25/10 Cổng 1│08:28 25/10 Cổng 1│ 01:22 │Hoàn tất
 3 │Không biển — KB-001 │Xe chuyên dùng│Khác — Đơn vị thi công │Nguyễn Văn Tâm      │Vào–Ra│10:30 25/10 Cổng 1│10:00 25/10 Cổng 1│ 00:30 │Hoàn tất
 4 │30A12345            │Ô tô          │Cơ quan                │Nguyễn Văn An (CB001)│Ra–Vào│14:00 25/10 Cổng 2│15:00 25/10 Cổng 2│ 01:00 │Hoàn tất
 5 │29X1-111.11         │Xe máy        │CBCS — Phạm Thị Dung   │Phạm Thị Dung (CB004)│Ra–Vào│16:00 25/10 Cổng 1│—                 │≥ 08:00│CHƯA VỀ
Tổng hợp: 5 lượt (từ kỳ trước 0; phát sinh 5) · hoàn tất 4 · chưa hoàn tất 1 (đang mở 1)
          Phương tiện có biển duy nhất: 3 đối tượng (30A-123.45 và 30A12345 là một) · Lượt không biển: 1 lượt
```

### 7.4. SO-04, kỳ 25/10/2026 (A4 dọc)

```
                                          SỔ TỔNG HỢP RA/VÀO
                          Từ 00:00 ngày 25/10/2026 đến hết ngày 25/10/2026
Điểm kiểm soát: Tất cả các cổng   Nhóm đối tượng: CBCS, Khách, Phương tiện   Số liệu tính đến: 00:00:00 26/10/2026

A. CHỈ TIÊU THEO NHÓM ĐỐI TƯỢNG
   Số liệu của từng nhóm đối tượng được tính riêng và không cộng gộp giữa các nhóm.
┌─────────────┬─────────────────────────────────────────────────────────────────────────┬──────────────┬─────────┬──────┐
│             │                         SỐ LƯỢT                                          │ SỐ ĐỐI TƯỢNG │         │      │
│ Nhóm        ├────────┬────────┬────────┬──────────┬────────┬──────────────┬──────────┤ Duy nhất     │ Bản ghi │ Sổ   │
│             │Từ kỳ   │Phát    │Hoàn tất│Chưa hoàn │Trong đó│Không định    │Có đính   │ (có định     │ đã huỷ  │ riêng│
│             │trước   │sinh    │        │tất (chốt)│quá hạn │danh          │chính     │ danh)        │         │      │
├─────────────┼────────┼────────┼────────┼──────────┼────────┼──────────────┼──────────┼──────────────┼─────────┼──────┤
│ CBCS        │   1    │   6    │   5    │    2     │   1    │      —       │    1     │      6       │    1    │SO-01 │
│ Khách       │   0    │   6    │   4    │    2     │   1    │      1       │    0     │      4       │    0    │SO-02 │
│ Phương tiện │   0    │   5    │   4    │    1     │   0    │      1       │    0     │      3       │    0    │SO-03 │
└─────────────┴────────┴────────┴────────┴──────────┴────────┴──────────────┴──────────┴──────────────┴─────────┴──────┘
   (Không có dòng tổng cộng giữa các nhóm.)

B. PHÂN BỔ THEO NGÀY        … (xem TC-SO4-03 cho ví dụ kỳ hai ngày)
C. PHÂN BỔ THEO CỔNG (số sự kiện)
   Cổng   │CBCS Vào│CBCS Ra│Khách Vào│Khách Ra│PT Vào│PT Ra
   Cổng 1 │   4    │   4   │    6    │   4    │  3   │  4
   Cổng 2 │   1    │   2   │    0    │   0    │  1   │  1
   Cộng   │   5    │   6   │    6    │   4    │  4   │  5
D. LƯỢT CHƯA HOÀN TẤT TẠI THỜI ĐIỂM CHỐT
   D1. CBCS (2 lượt):  1. CB004 Phạm Thị Dung — Ra 16:00 25/10 Cổng 1 — hạn 18:00 — ≥ 08:00 — CHƯA VỀ – QUÁ HẠN
                       2. CB003 Lê Văn Cường — Ra 22:45 25/10 Cổng 2 — ≥ 01:15 — Hoàn tất sau kỳ
   D2. Khách (2 lượt): 1. Ông Quang (thẻ K05) — Vào 15:00 25/10 — hạn 17:30 — ≥ 09:00 — CHƯA RA – QUÁ HẠN
                       2. Lý Thị Sen (thẻ K06) — Vào 17:30 25/10 — ≥ 06:30 — Hoàn tất sau kỳ
   D3. Phương tiện (1 lượt): 1. 29X1-111.11 Xe máy — Ra 16:00 25/10 — ≥ 08:00 — CHƯA VỀ
E. TÓM TẮT ĐÍNH CHÍNH VÀ HUỶ: CBCS 1 lượt có đính chính (1 lần), 1 bản ghi huỷ — xem Phụ lục đính chính SO-01.
```

Lưu ý Phần D: thời lượng là thời lượng **tính đến thời điểm chốt** (`≥`), kể cả với lượt "Hoàn tất sau kỳ" — khác với sổ riêng (sổ riêng in thời lượng thực tế cho lượt này theo BR-ND-05), vì Phần D phản ánh tình trạng tại thời điểm giao ca.

---

## 8. Nội dung cần đơn vị xác nhận liên quan đến mẫu sổ

`XN-01` (có biểu mẫu bắt buộc không), `XN-03` (tên đơn vị), `XN-04` (tên sổ), `XN-05` (thứ tự cột Ra/Vào), `XN-06` (thông tin CBCS), `XN-07` (danh mục lý do), `XN-08` (dữ liệu khách), `XN-11` (hiển thị "(sau kỳ)"), `XN-14` (khối ký), `XN-15` (lề, phông), `XN-19` (Phần F), `XN-25` (phân bổ theo ngày/ca), `XN-26` (thông tin phương tiện). Chi tiết và đề xuất mặc định: `requirements.md` §9.
