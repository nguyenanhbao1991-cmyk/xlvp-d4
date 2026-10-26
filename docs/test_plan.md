# Kế hoạch kiểm thử — Các sổ ra/vào

| Thuộc tính | Giá trị |
|---|---|
| Mã tài liệu | QLCBCS-TP-SO |
| Phiên bản | 0.1 — **Dự thảo để thống nhất** |
| Ngày lập | 26/10/2026 |
| Liên quan | [`requirements.md`](requirements.md), [`business_rules.md`](business_rules.md), [`report_definitions.md`](report_definitions.md) |

---

## 1. Mục tiêu và phạm vi

- Xác nhận bốn sổ SO-01…SO-04 đáp ứng các yêu cầu `REQ-…` và tiêu chí nghiệm thu `AC-…` trong `requirements.md`, theo các quy tắc `BR-…`.
- Phạm vi: hiển thị trên màn hình, in, xuất Excel/Word/PDF, nhật ký trích xuất, phân quyền xem/xuất, che dữ liệu cá nhân.
- Ngoài phạm vi: chức năng ghi nhận ra/vào (chỉ dùng để nạp dữ liệu thử), sao lưu, phục hồi.

## 2. Các giai đoạn và cổng kiểm soát

| Cổng | Giai đoạn | Nội dung | Điều kiện đạt |
|---|---|---|---|
| **G0** | Thống nhất tài liệu (hiện tại) | Rà soát bốn tài liệu; đơn vị trả lời các mục `XN`; duyệt bản mẫu bố cục | TC-DOC-01 đạt; tài liệu lên phiên bản 1.0. **Chưa lập trình trước G0.** |
| G1 | Kiểm thử đơn vị / tích hợp | Hàm xác định tập lượt, trạng thái, chỉ tiêu, định danh, mã trích xuất; kiểm thử tự động với DS-01, DS-02 | 100% ca mức Cao tự động hoá được đều đạt |
| G2 | Kiểm thử hệ thống | Toàn bộ ca trong tài liệu này trên môi trường thử LAN | Không còn lỗi mức Nghiêm trọng/Cao; ≤ 3 lỗi mức Trung bình đã có phương án |
| G3 | Nghiệm thu (UAT) | Người dùng đơn vị thực hiện ca có cột "UAT" = Có, in thực tế, ký thử | Đại diện đơn vị ký biên bản nghiệm thu |

## 3. Môi trường kiểm thử

- Máy chủ thử trong LAN: Django, PostgreSQL, cấu hình giống máy chủ thật; **không có kết nối Internet** (để kiểm TC-EXP-10).
- Múi giờ máy chủ Asia/Ho_Chi_Minh. **Đồng hồ giả lập**: môi trường thử cho phép đặt "thời điểm hiện tại" của máy chủ để tái lập thời điểm trích xuất (ví dụ 27/10/2026 09:00:12).
- Máy trạm: các trình duyệt theo `XN-27`; một máy trạm được cố ý đặt lệch giờ +15 phút (TC-NFR-03).
- Máy in laser A4 đen trắng của đơn vị; Microsoft Word và Excel phiên bản đơn vị đang dùng; trình đọc PDF thông dụng.
- Cấu hình thử: cơ quan chủ quản "CƠ QUAN THỬ NGHIỆM", đơn vị "ĐƠN VỊ THỬ NGHIỆM", cổng "Cổng 1", "Cổng 2"; giờ giao ca 07:30; ngưỡng ghi bổ sung 30 phút; chức danh xác nhận "Chỉ huy đơn vị".
- Tài khoản thử:

| Tài khoản | Họ tên | Vai trò | Ghi chú |
|---|---|---|---|
| `trucban01` | Nguyễn Văn X | Trực ban | Người trích xuất mặc định trong các ca |
| `trucban02` | Lê Thị Y | Trực ban | Người đính chính C6 |
| `trucban03` | Trần Văn Z | Trực ban | |
| `chihuy01` | Phan Văn H | Chỉ huy | Có quyền xem bản ghi huỷ, xem dữ liệu cá nhân đầy đủ |
| `lanhdao01` | Đỗ Văn L | Lãnh đạo | Chỉ cấu hình quyền xem/xuất SO-04 cho TC-GEN-24 |
| `xem01` | Hà Thị M | Chỉ xem | Không có quyền xuất |

## 4. Mức độ lỗi

| Mức | Định nghĩa | Ví dụ |
|---|---|---|
| Nghiêm trọng | Số liệu sai hoặc mất dữ liệu trên bản in/xuất | Sai chỉ tiêu, thiếu lượt, cộng chéo nhóm, lộ số giấy tờ |
| Cao | Sai quy tắc nghiệp vụ nhưng số liệu tổng đúng | Sai nhãn trạng thái, thiếu "(từ kỳ trước)", thiếu phụ lục đính chính |
| Trung bình | Sai trình bày ảnh hưởng đọc | Tiêu đề không lặp, dòng bị cắt trang, ký tự lỗi phông |
| Thấp | Thẩm mỹ | Lệch căn lề nhỏ |

---

## 5. Bộ dữ liệu kiểm thử

### 5.1. DS-01 — Bộ dữ liệu chuẩn

Mọi sự kiện ở **Cổng 1** trừ khi ghi khác. Thời điểm ghi nhận = thời điểm sự kiện + 1 phút trừ khi ghi khác. Ngày năm 2026.

**CBCS**

| Lượt | Mã CBCS | Họ tên | Đơn vị | Chiều | Sự kiện mở | Sự kiện đóng | Lý do / hạn | PT đi kèm | Đặc điểm |
|---|---|---|---|---|---|---|---|---|---|
| C0 | CB001 | Nguyễn Văn An | Phòng Tham mưu | Ra–Vào | Ra 09:00 24/10 | Vào 10:00 24/10 | Công tác | — | Chỉ dùng cho kỳ 24–25/10 |
| C1 | CB001 | Nguyễn Văn An | Phòng Tham mưu | Ra–Vào | Ra 08:00 25/10 | Vào 10:30 25/10 | Công tác | 30A-123.45 (P1) | |
| C2 | CB001 | Nguyễn Văn An | Phòng Tham mưu | Ra–Vào | Ra 14:00 25/10 **Cổng 2** | Vào 15:00 25/10 **Cổng 2** | Công tác | 30A12345 (P2) | Cùng CBCS với C1 |
| C3 | CB002 | Trần Thị Bình | Phòng Hậu cần | Ra–Vào | Ra 23:30 24/10 (trucban03) | Vào 01:15 25/10 (trucban01) | Việc riêng có phép | — | Từ kỳ trước |
| C4 | CB003 | Lê Văn Cường | Phòng Kỹ thuật | Ra–Vào | Ra 22:45 25/10 **Cổng 2** | Vào 00:20 26/10 | Công tác | — | Hoàn tất sau kỳ |
| C5 | CB004 | Phạm Thị Dung | Phòng Hậu cần | Ra–Vào | Ra 16:00 25/10 | *(chưa có)* | Việc riêng có phép; hạn về 18:00 25/10 | 29X1-111.11 (P4) | Đang mở, quá hạn |
| C6 | CB005 | Hoàng Văn Đức | Phòng Kỹ thuật | Ra–Vào | Ra 09:00 25/10 | Vào 09:40 25/10 (ghi nhận 09:41; ban đầu nhập **09:14**) | Công tác | — | Đính chính lúc 20:00 25/10 bởi `trucban02`, lý do "Nhập nhầm giờ" |
| C7 | CB006 | Vũ Thị Giang | Phòng Tham mưu | Ra–Vào | Ra 11:00 25/10 | — | — | — | **Đã huỷ** lúc 11:10 25/10 bởi `chihuy01`, lý do "Nhập nhầm người" |
| C8 | CB007 | Đặng Quốc Hưng | Phòng Tham mưu | Vào–Ra | Vào 07:30 25/10 (trucban01) | Ra 17:15 25/10 (trucban02) | — | — | Chiều Vào–Ra |

**Khách**

| Lượt | Họ tên | Giấy tờ | Đơn vị / đoàn | Mục đích; người tiếp | Thẻ | Vào | Ra | Đặc điểm |
|---|---|---|---|---|---|---|---|---|
| K1 | Bùi Văn Lâm | CCCD `001090000111` | Công ty TNHH An Phát | Liên hệ công tác; Nguyễn Văn An (CB001) | K01 | 08:30 25/10 | 09:45 25/10 | PT 29B-678.90 (P3) |
| K2 | Bùi Văn Lâm | CCCD `001 090 000 111` | Công ty TNHH An Phát | Nộp hồ sơ; Phòng Hậu cần | K02 | 14:00 25/10 | 14:30 25/10 | Cùng khách với K1 sau chuẩn hoá |
| K3 | Mai Thị Ngọc | CCCD `001190000222` | Đoàn ĐK-01 | Làm việc theo kế hoạch; Phòng Tham mưu | K03 | 10:00 25/10 | 11:00 25/10 | |
| K4 | Tạ Văn Phúc | CCCD `001090000333` | Đoàn ĐK-01 | Làm việc theo kế hoạch; Phòng Tham mưu | K04 | 10:00 25/10 | 11:05 25/10 (**ghi nhận 12:10**) | Ghi bổ sung; cùng giờ vào với K3, mã bản ghi lớn hơn |
| K5 | Ông Quang | Không xuất trình | — | Giao hàng; Phòng Hậu cần | K05 | 15:00 25/10; giờ ra dự kiến 17:30 | *(chưa có)* | Không định danh; quá hạn |
| K6 | Lý Thị Sen | CCCD `001190000444` | — | Thăm thân; Phòng Kỹ thuật | K06 | 17:30 25/10 | 00:10 26/10 | Hoàn tất sau kỳ; không có giờ ra dự kiến |

**Phương tiện**

| Lượt | Biển số (như ghi nhận) | Loại | Nguồn | Người điều khiển | Chiều | Sự kiện mở | Sự kiện đóng | Đặc điểm |
|---|---|---|---|---|---|---|---|---|
| P1 | 30A-123.45 | Ô tô | Cơ quan | Nguyễn Văn An (CB001) | Ra–Vào | Ra 08:00 25/10 | Vào 10:30 25/10 | Lệnh LĐX-101 |
| P2 | 30A12345 | Ô tô | Cơ quan | Nguyễn Văn An (CB001) | Ra–Vào | Ra 14:00 25/10 **Cổng 2** | Vào 15:00 25/10 **Cổng 2** | Cùng xe với P1 sau chuẩn hoá; lệnh LĐX-102 |
| P3 | 29B-678.90 | Ô tô | Khách — Bùi Văn Lâm | Bùi Văn Lâm | Vào–Ra | Vào 08:28 25/10 | Ra 09:50 25/10 | |
| P4 | 29X1-111.11 | Xe máy | CBCS — Phạm Thị Dung | Phạm Thị Dung (CB004) | Ra–Vào | Ra 16:00 25/10 | *(chưa có)* | Đang mở, không có hạn về |
| P5 | Không biển — KB-001 | Xe chuyên dùng | Khác — Đơn vị thi công | Nguyễn Văn Tâm | Vào–Ra | Vào 10:00 25/10 | Ra 10:30 25/10 | Không định danh |

### 5.2. Kịch bản và kết quả mong đợi trên DS-01

| Kịch bản | Kỳ | Thời điểm trích xuất (đồng hồ giả lập) | Thời điểm chốt |
|---|---|---|---|
| S1 | `[25/10 00:00, 26/10 00:00)` | 27/10/2026 09:00:12 | 26/10/2026 00:00:00 |
| S2 | `[25/10 00:00, 26/10 00:00)` | 25/10/2026 12:00:00 — dữ liệu chỉ gồm các ghi nhận có thời điểm ghi nhận ≤ 12:00 25/10 (C6 chưa đính chính, K4 chưa có sự kiện Ra, C7 đã huỷ) | 25/10/2026 12:00:00 |
| S3 | `[24/10 00:00, 26/10 00:00)` | 27/10/2026 09:00:12 | 26/10/2026 00:00:00 |

**Kết quả mong đợi S1**

| Sổ | Thứ tự dòng | (1) Từ kỳ trước | (2) Phát sinh | (3) Hoàn tất | (4) Chưa hoàn tất (đang mở / sau kỳ) | (4a) Quá hạn | Đối tượng duy nhất | Không định danh | Có ĐC | Huỷ |
|---|---|---|---|---|---|---|---|---|---|---|
| SO-01 | C3, C8, C1, C6, C2, C5, C4 | 1 | 6 | 5 | 2 (1 / 1) | 1 | 6 CBCS | — | 1 | 1 |
| SO-02 | K1, K3, K4, K2, K5, K6 | 0 | 6 | 4 | 2 (1 / 1) | 1 | 4 khách | 1 lượt | 0 | 0 |
| SO-03 | P1, P3, P5, P2, P4 | 0 | 5 | 4 | 1 (1 / 0) | 0 | 3 phương tiện | 1 lượt | 0 | 0 |

Giá trị ô mong đợi chọn lọc (S1):

| Lượt | Ô sự kiện mở | Ô sự kiện đóng | Thời lượng | Trạng thái | Ghi chú |
|---|---|---|---|---|---|
| C3 | `23:30 24/10` · Cổng 1 · (từ kỳ trước) | `01:15 25/10` · Cổng 1 | 01:45 | Hoàn tất | |
| C8 | Vào `07:30 25/10` | Ra `17:15 25/10` | 09:45 | Hoàn tất | |
| C6 | Ra `09:00 25/10` | Vào `09:40 25/10` | 00:40 | Hoàn tất | ĐC(1) |
| C5 | Ra `16:00 25/10` | — | ≥ 08:00 | **Chưa về – Quá hạn** | |
| C4 | Ra `22:45 25/10` · Cổng 2 | Vào `00:20 26/10` · Cổng 1 · (sau kỳ) | 01:35 | Hoàn tất sau kỳ | |
| K4 | Vào `10:00 25/10` | Ra `11:05 25/10` | 01:05 | Hoàn tất | GBS |
| K5 | Vào `15:00 25/10` | — | ≥ 09:00 | **Chưa ra – Quá hạn** | |
| K6 | Vào `17:30 25/10` | Ra `00:10 26/10` · (sau kỳ) | 06:40 | Hoàn tất sau kỳ | |
| P4 | Ra `16:00 25/10` | — | ≥ 08:00 | **Chưa về** | |

Chỉ tiêu riêng S1: SO-01 Ra–Vào 6, Vào–Ra 1; lý do: Công tác 4, Việc riêng có phép 2, Không ghi 1. SO-02 số đoàn 1; thẻ chưa thu hồi 2 (K05, K06). SO-03 theo loại: Ô tô 3, Xe máy 1, Xe chuyên dùng 1; theo nguồn: Cơ quan 2, CBCS 1, Khách 1, Khác 1.

SO-04 Phần C (S1) — số sự kiện theo cổng:

| Cổng | CBCS Vào | CBCS Ra | Khách Vào | Khách Ra | PT Vào | PT Ra |
|---|---|---|---|---|---|---|
| Cổng 1 | 4 | 4 | 6 | 4 | 3 | 4 |
| Cổng 2 | 1 | 2 | 0 | 0 | 1 | 1 |
| Cộng | 5 | 6 | 6 | 4 | 4 | 5 |

**Kết quả mong đợi S2 (SO-01)**: 4 dòng C3, C8, C1, C6; (1) = 1, (2) = 3, (3) = 3 (C3, C1, C6), (4) = 1 (C8 "Chưa ra", ≥ 04:30); CBCS duy nhất 4; C6 hiển thị vào 09:14, không có ĐC; đầu sổ ghi "Số liệu tính đến 12:00:00 ngày 25/10/2026 (kỳ chưa kết thúc)".

**Kết quả mong đợi S3**: SO-01 (1) = 0, (2) = 8, (3) = 6, (4) = 2; CBCS duy nhất 6. SO-04 Phần B:

| Ngày | CBCS lượt phát sinh | CBCS có hoạt động | Khách lượt phát sinh | Khách có định danh có hoạt động | PT lượt phát sinh | PT có biển có hoạt động |
|---|---|---|---|---|---|---|
| 24/10/2026 | 2 (C0, C3) | 2 (CB001, CB002) | 0 | 0 | 0 | 0 |
| 25/10/2026 | 6 | 6 | 6 | 4 | 5 | 3 |
| **Cộng / Duy nhất cả kỳ** | **8** | **6** (không phải 8) | **6** | **4** | **5** | **3** |

### 5.3. DS-02 — Trường hợp biên (nạp riêng, không trộn với DS-01)

| Mã | Dữ liệu | Kỳ kiểm tra | Mong đợi |
|---|---|---|---|
| E1 | CB101 Ra 00:00:00 25/10, Vào 00:30 25/10 | 25/10 | Có trong sổ, tính "Phát sinh" |
| E2 | CB102 Ra 23:00 24/10, Vào 00:00:00 25/10 | 24/10 và 25/10 | Kỳ 24/10: "Hoàn tất sau kỳ", tính (4). Kỳ 25/10: "(từ kỳ trước)", tính (1) và (3) |
| E3 | CB103 Ra 00:00:00 26/10 | 25/10 | Không có trong sổ |
| E4 | CB104 Ra 08:00 25/10 (mở), Ra 09:00 25/10 (mở) | 25/10 | Hai dòng, cả hai ghi "Chồng lượt"; (2) đếm 2 |
| E5 | CB105 Ra 10:00 25/10, Vào 09:50 25/10 (nạp trực tiếp vào CSDL) | 25/10 | Ghi chú "Lỗi thời gian", thời lượng "—" |
| E6 | CB106 Ra ghi 10:00 25/10, đính chính thành 10:00 26/10; Vào 11:00 26/10 | 25/10 và 26/10 | Không có trong sổ 25/10 và phụ lục của sổ này; có trong sổ 26/10 với ĐC(1) |
| E7 | Đồng hồ giả lập 26/10 06:00, chọn "Ca trực hiện tại" | — | Kỳ `[25/10 07:30, 26/10 07:30)` |
| E8 | CB108 Ra 23:00 31/12/2026, Vào 01:00 01/01/2027 | `[31/12/2026, 02/01/2027)` | Ô thời điểm dạng `23:00 31/12/26`, `01:00 01/01/27` |
| E9 | CB107 Ra 08:00 20/10, chưa vào | 25/10 (S1) | "(từ kỳ trước)", "≥ 136:00", tính (1) và (4) |
| E10 | Kỳ không có lượt nào (ví dụ 01/01/2026) | — | Sổ trống theo REQ-GEN-18 |

### 5.4. DS-03 — Khối lượng

Sinh ngẫu nhiên có kiểm soát: 10.000 lượt/tháng cho mỗi nhóm trong tháng 10/2026 (`XN-24`), 1% chưa hoàn tất, 2% có đính chính, 0,5% đã huỷ; thêm một ngày có 5.001 lượt CBCS để kiểm tra giới hạn (`XN-18`).

### 5.5. DS-04 — Tiếng Việt

Họ tên: "Nguyễn Thị Ánh Tuyết", "Ưng Hoàng Phúc", "Ông Ích Khiêm", "Lương Thế Vinh", "Đặng Quốc Hưng", "Phạm Thị Ngọc Hà", "Bùi Thị Ơn" — mỗi tên được nạp hai lần: một lần dạng Unicode dựng sẵn (NFC), một lần dạng tổ hợp (NFD). Thứ tự mong đợi khi sắp theo họ tên (theo tên, rồi họ và tên đệm): Hà, Hưng, Khiêm, Ơn, Phúc, Tuyết, Vinh.

---

## 6. Ca kiểm thử

Quy ước: **Mức** = Cao / Trung bình / Thấp (ưu tiên thực hiện). **UAT** = có thực hiện lại khi nghiệm thu. Trừ khi ghi khác, dùng DS-01 kịch bản S1, tài khoản `trucban01`.

### 6.0. Rà soát tài liệu

**TC-DOC-01 — Thống nhất tài liệu trước khi lập trình** · Truy vết: `requirements.md` §10 · Mức: Cao · UAT: Có
- Bước: (1) Đơn vị đọc bốn tài liệu; (2) trả lời từng mục `XN-01`…`XN-29`; (3) duyệt bản mẫu bố cục §7 của `report_definitions.md`; (4) nhóm dự án cập nhật tài liệu theo trả lời; (5) kiểm tra chéo: mọi `REQ` có ít nhất một `AC` và một `TC`; mọi mã `BR`, `TC`, `XN` được dẫn chiếu đều tồn tại; kết quả mong đợi ở §5.2 thoả đẳng thức cân đối.
- Mong đợi: không còn mục `XN` ở trạng thái "Chờ xác nhận"; ma trận §7 đầy đủ; tài liệu phiên bản 1.0 có người duyệt.

### 6.1. Chung (TC-GEN)

**TC-GEN-01 — Truy cập bốn sổ** · REQ-GEN-01, BR-IN-01 · Cao
- Bước: đăng nhập `trucban01`, mở mục "Sổ ra/vào"; đăng nhập `lanhdao01` (cấu hình thử chỉ có SO-04).
- Mong đợi: `trucban01` thấy SO-01…SO-04 với đúng mã, tên, "Mẫu nội bộ — phiên bản 1.0"; `lanhdao01` chỉ thấy SO-04.

**TC-GEN-02 — Lựa chọn nhanh của kỳ** · REQ-GEN-02, BR-KY-03 · Cao
- Bước: đặt đồng hồ giả lập 26/10/2026 06:00 (thứ Hai); lần lượt chọn từng lựa chọn nhanh; nhập "Đến" ≤ "Từ".
- Mong đợi: Hôm nay `[26/10 00:00, 27/10 00:00)`; Hôm qua `[25/10, 26/10)`; Ca trực hiện tại `[25/10 07:30, 26/10 07:30)` (E7); Ca trực trước `[24/10 07:30, 25/10 07:30)`; Tuần này `[26/10, 02/11)`; Tháng này `[01/10, 01/11)`; Tháng trước `[01/09, 01/10)`. "Đến" ≤ "Từ" bị chặn với thông báo tiếng Việt.

**TC-GEN-03 — Ranh giới kỳ nửa mở** · REQ-GEN-02 (AC-GEN-02.3), BR-KY-02, BR-KY-05 · Cao
- Dữ liệu: DS-02 E1, E2, E3.
- Mong đợi: theo bảng DS-02.

**TC-GEN-04 — Kỳ chưa kết thúc** · REQ-GEN-03, BR-KY-04 · Cao
- Dữ liệu: DS-01 S2.
- Mong đợi: theo "Kết quả mong đợi S2"; C2, C4, C5 không xuất hiện; đầu sổ và khối tổng hợp ghi cùng thời điểm chốt 12:00:00.

**TC-GEN-05 — Màn hình khớp bản in** · REQ-GEN-04, BR-IN-08 · Cao · UAT
- Bước: xem SO-01, SO-02, SO-03 trên màn hình; xuất PDF cùng điều kiện; so sánh; thu nhỏ cửa sổ về 1366×768.
- Mong đợi: cùng cột, thứ tự, giá trị, chỉ tiêu; tiêu đề bảng cố định khi cuộn; dòng chưa hoàn tất in đậm; không cần cuộn ngang ở 1366×768.

**TC-GEN-06 — Đầu sổ, đầu trang lặp, chân trang** · REQ-GEN-05, BR-IN-03…06 · Cao · UAT
- Dữ liệu: DS-03, SO-01 kỳ 1 ngày có ≥ 3 trang PDF.
- Mong đợi: trang 1 đủ các dòng của `report_definitions.md` §2.3; từ trang 2 có đầu trang rút gọn và dòng tiêu đề bảng; mọi trang có chân trang đủ 5 thành phần, "Trang x/y" đúng; không có Quốc hiệu, tiêu ngữ.

**TC-GEN-07 — Lọc** · REQ-GEN-06, BR-KY-07, BR-TONG-03 · Cao
- Bước: SO-01 lọc Đơn vị = Phòng Tham mưu.
- Mong đợi: 3 dòng C8, C1, C2 (C7 thuộc Phòng Tham mưu nhưng đã huỷ); đầu sổ ghi "Điều kiện lọc: Đơn vị/bộ phận: Phòng Tham mưu" và "Sổ đã lọc — không phải toàn bộ dữ liệu của kỳ"; chỉ tiêu: (1) 0, (2) 3, (3) 3, (4) 0; CBCS duy nhất 2; khối tổng hợp có câu "Số liệu theo điều kiện lọc…".

**TC-GEN-08 — Sắp xếp và STT** · REQ-GEN-07, BR-IN-07 · Cao
- Bước: SO-02 sắp mặc định; xuất hai lần; đổi sang sắp theo họ tên.
- Mong đợi: thứ tự mặc định K1, K3, K4, K2, K5, K6 (K3 trước K4 do mã bản ghi); hai lần xuất cùng thứ tự; STT 1–6 liên tục; sắp theo họ tên: Lâm (K1, K2), Ngọc (K3), Phúc (K4), Quang (K5), Sen (K6).

**TC-GEN-09 — Trạng thái khi in đen trắng** · REQ-GEN-08, BR-TT-01…04 · Cao · UAT
- Bước: in PDF SO-01, SO-02, SO-03 (S1) trên máy in đen trắng; người kiểm tra không tham gia thiết kế đọc và liệt kê trạng thái từng dòng.
- Mong đợi: liệt kê đúng 100%; nhãn đúng "Chưa về"/"Chưa ra" theo chiều lượt; "Quá hạn" in đậm, gạch chân; PDF/Word/Excel không dùng màu cho trạng thái.

**TC-GEN-10 — Lượt chưa hoàn tất** · REQ-GEN-09, BR-CHT-01…03, BR-CHT-05 · Cao
- Mong đợi: C5, K5, P4 như bảng giá trị ô S1; dòng in đậm. Để hệ thống chạy qua 00:00 với đồng hồ giả lập: không phát sinh sự kiện đóng tự động cho C5, K5, P4.

**TC-GEN-11 — Quá hạn** · REQ-GEN-09, BR-CHT-04 · Cao
- Bước: S1; sau đó lập lại SO-01 kỳ 25/10 với đồng hồ giả lập 25/10 17:00 (chốt 17:00).
- Mong đợi: S1: C5 "Chưa về – Quá hạn", K5 "Chưa ra – Quá hạn", P4 "Chưa về" (không có hạn). Chốt 17:00: C5 "Chưa về" (chưa quá 18:00).

**TC-GEN-12 — Lượt từ kỳ trước qua nửa đêm** · REQ-GEN-10 (AC-GEN-10.1), BR-ND-01…03 · Cao
- Mong đợi: C3 một dòng duy nhất trong sổ 25/10 với "(từ kỳ trước)"; được đếm vào (1), không vào (2); DS-02 E9 có "≥ 136:00".

**TC-GEN-13 — Lượt hoàn tất sau kỳ** · REQ-GEN-10 (AC-GEN-10.2), BR-ND-04, BR-ND-05 · Cao
- Mong đợi: C4 ô Vào "00:20 26/10 · Cổng 1 · (sau kỳ)", thời lượng 01:35, "Hoàn tất sau kỳ", tính (4); K6 tương tự (06:40). Sổ kỳ 26/10 có C4 với "(từ kỳ trước)". DS-02 E2 đúng như bảng.

**TC-GEN-14 — Đính chính** · REQ-GEN-11 (AC-GEN-11.1), BR-DC-01…04 · Cao · UAT
- Mong đợi: C6 vào 09:40, "ĐC(1)"; phụ lục có dòng (1): STT dòng 4, CB005 Hoàng Văn Đức, "Thời điểm vào", 09:14 → 09:40, "Nhập nhầm giờ", Lê Thị Y (trucban02), 20:00 25/10/2026. SO-02 (không có đính chính) ghi "Không có đính chính." Thử đính chính không nhập lý do: bị từ chối.

**TC-GEN-15 — Đính chính làm lượt đổi kỳ** · REQ-GEN-11 (AC-GEN-11.2), BR-DC-05 · Cao
- Dữ liệu: DS-02 E6.
- Mong đợi: theo bảng DS-02.

**TC-GEN-16 — Bản ghi đã huỷ** · REQ-GEN-12, BR-DC-06, BR-TONG-02 · Cao
- Bước: SO-01 mặc định; đăng nhập `chihuy01`, bật "Hiện bản ghi đã huỷ"; thử bật với `trucban01`.
- Mong đợi: mặc định không có C7; khi bật: C7 nằm giữa C6 và C2, STT "—", "ĐÃ HUỶ", ghi chú "Nhập nhầm người"; STT các dòng khác vẫn 1–7; chỉ tiêu không đổi; đầu sổ có dòng "Có hiển thị bản ghi đã huỷ…"; `trucban01` không có tuỳ chọn này. SO-04 Phần C không đếm sự kiện của C7.

**TC-GEN-17 — Ghi bổ sung** · REQ-GEN-13, BR-DC-08 · Trung bình
- Mong đợi: chỉ K4 có "GBS"; C6 (ghi nhận 09:41 cho sự kiện 09:40) không có "GBS". Đổi ngưỡng cấu hình thành 90 phút → K4 không còn "GBS".

**TC-GEN-18 — Đẳng thức cân đối** · REQ-GEN-14, BR-TONG-01 · Cao
- Bước: kiểm tra mọi sổ ở S1, S2, S3, DS-02, DS-03 (mỗi ngày của tháng 10).
- Mong đợi: `(1) + (2) = (3) + (4)` ở mọi trường hợp; dòng "Cân đối: …" in đúng; không có "tổng thời lượng", không có "cộng trang".

**TC-GEN-19 — Thông tin và nhật ký trích xuất** · REQ-GEN-15, REQ-NFR-06, BR-TX-01, BR-TX-02, BR-TX-05, BR-TX-06 · Cao
- Bước: xem SO-01 trên màn hình; xuất PDF hai lần; mở nhật ký trích xuất bằng tài khoản quản trị; thử sửa/xoá dòng nhật ký qua giao diện.
- Mong đợi: màn hình ghi "Xem lúc … — chưa phải bản trích xuất", không sinh mã; hai lần xuất có mã `SO01-20261027-nnnn` khác nhau, tăng dần; chân trang và khối "Thông tin trích xuất" ghi "09:00:12 ngày 27/10/2026", "Nguyễn Văn X (tài khoản: trucban01)"; nhật ký có đủ trường BR-TX-05 (kể cả mã băm khớp file đã tải); không sửa/xoá được nhật ký.

**TC-GEN-20 — Người lập sổ** · REQ-GEN-16, BR-TX-03, BR-TX-04 · Cao · UAT
- Bước: xuất với mặc định; xuất với người lập sổ "Trần Văn Z"; xuất với "Để trống — ký tay"; thử sửa người trích xuất.
- Mong đợi: lần lượt in "Nguyễn Văn X", "Trần Văn Z", dòng chấm dưới "(Ký, ghi rõ họ tên)"; người trích xuất luôn là Nguyễn Văn X; nhật ký lưu cả hai.

**TC-GEN-21 — Khối ký và ngắt trang** · REQ-GEN-17, BR-IN-09 · Trung bình · UAT
- Bước: tạo dữ liệu sao cho bảng kết thúc sát cuối trang (điều chỉnh số dòng DS-03 từ 1 đến 40 dòng, xuất PDF/Word từng trường hợp).
- Mong đợi: không trang nào chỉ có khối ký; khối ký luôn cùng trang với "Thông tin trích xuất"; không dòng bảng nào bị cắt; thứ tự các khối cuối đúng; có "— Hết sổ —".

**TC-GEN-22 — Sổ trống** · REQ-GEN-18 · Trung bình
- Dữ liệu: DS-02 E10; lập cả bốn sổ.
- Mong đợi: đầu sổ đầy đủ; dòng "Không có lượt nào trong kỳ theo điều kiện đã chọn"; mọi chỉ tiêu bằng 0; có khối ký; Excel/Word/PDF đều tạo được.

**TC-GEN-23 — Che dữ liệu cá nhân** · REQ-GEN-19, BR-BM-01, BR-BM-02 · Cao
- Bước: `trucban01` xem và xuất SO-02 ba định dạng; `chihuy01` xuất với "dữ liệu cá nhân đầy đủ".
- Mong đợi: `trucban01`: `********0111` ở màn hình và trong **giá trị ô** Excel (không phải định dạng ẩn), Word, PDF; tìm kiếm trong file không ra số đầy đủ. `chihuy01`: số đầy đủ; đầu sổ và "Thông tin trích xuất" ghi "Dữ liệu cá nhân: hiển thị đầy đủ"; nhật ký ghi lựa chọn.

**TC-GEN-24 — Phân quyền** · REQ-GEN-20 · Cao
- Bước: `xem01` mở SO-01; gọi trực tiếp địa chỉ xuất của SO-01; `lanhdao01` gọi địa chỉ xem SO-02.
- Mong đợi: `xem01` không thấy nút xuất; gọi trực tiếp bị từ chối (HTTP 403) và không sinh mã/nhật ký trích xuất; `lanhdao01` bị từ chối SO-02.

**TC-GEN-25 — Đọc nhất quán khi đang ghi** · REQ-GEN-15 (AC-GEN-15.3), BR-TX-01 · Cao
- Bước: dùng DS-03; bắt đầu xuất PDF SO-04 tháng 10; trong lúc xuất, một tiến trình ghi liên tục sự kiện mới có thời điểm trong kỳ.
- Mong đợi: Phần A khớp từng sổ riêng xuất cùng thời điểm trích xuất; đẳng thức cân đối đúng; số liệu trong file khớp với số liệu ghi trong nhật ký trích xuất.

**TC-GEN-26 — Đính chính sau khi đã xuất** · REQ-GEN-11 (AC-GEN-11.3), BR-DC-07 · Cao
- Bước: xuất PDF SO-01 S1 (mã A); đính chính thời điểm ra C1 thành 08:05; xem lại sổ; xuất lại (mã B).
- Mong đợi: file A không đổi (mã băm như nhật ký); màn hình cảnh báo "Dữ liệu kỳ này đã thay đổi sau lần trích xuất A…"; file B có C1 ra 08:05, "ĐC(1)" và phụ lục có 2 dòng (thứ tự theo STT dòng).

**TC-GEN-27 — Lọc theo cổng** · REQ-GEN-06 (AC-GEN-06.2), BR-KY-07 · Cao
- Bước: SO-01 lọc Cổng 2; SO-03 lọc Cổng 2.
- Mong đợi: SO-01: C2 (ra và vào Cổng 2), C4 (ra Cổng 2, vào Cổng 1) — 2 dòng; SO-03: P2 — 1 dòng; đầu sổ ghi "Điểm kiểm soát: Cổng 2".

**TC-GEN-28 — Chồng lượt và lỗi thời gian** · REQ-GEN-22, BR-LT-04, BR-LT-06 · Trung bình
- Dữ liệu: DS-02 E4, E5.
- Mong đợi: theo bảng DS-02.

**TC-GEN-29 — Kỳ vượt giới hạn** · REQ-GEN-02 (AC-GEN-02.4), BR-KY-06 · Trung bình
- Bước: SO-01 kỳ 45 ngày, xuất PDF và Excel; SO-04 kỳ 400 ngày.
- Mong đợi: PDF bị chặn với thông báo và gợi ý; Excel tạo được; SO-04 400 ngày bị chặn.

**TC-GEN-30 — Cấu hình sổ** · REQ-GEN-21, REQ-GEN-17 (AC-GEN-17.2) · Trung bình
- Bước: xuất PDF (mã A); quản trị đổi tên đơn vị, chức danh xác nhận "Thủ trưởng đơn vị", thêm ô ký thứ ba; xuất lại (mã B).
- Mong đợi: B dùng cấu hình mới; A không đổi; nhật ký A vẫn tra được.

### 6.2. SO-01 (TC-SO1)

**TC-SO1-01 — Nội dung SO-01** · REQ-SO1-01 · Cao · UAT
- Mong đợi: 7 dòng theo thứ tự C3, C8, C1, C6, C2, C5, C4; đủ 13 cột theo `report_definitions.md` §3.4; giá trị ô theo bảng S1; C1 cột "Phương tiện đi kèm" = 30A-123.45; cột "Người ghi nhận" C3 = "R: trucban03 / V: trucban01".

**TC-SO1-02 — Chỉ tiêu SO-01** · REQ-SO1-02, REQ-GEN-14, BR-TONG-05, BR-DN-01 · Cao
- Mong đợi: 1 / 6 / 5 / 2 (1 / 1) / quá hạn 1; CBCS duy nhất 6 (CB001 có 2 lượt chỉ đếm 1; CB006 huỷ không đếm); Ra–Vào 6, Vào–Ra 1; lý do như S1.

**TC-SO1-03 — Lượt Vào–Ra** · REQ-SO1-03 · Cao
- Mong đợi: C8 cột Chiều "Vào–Ra", cột Ra "17:15 25/10", cột Vào "07:30 25/10", thời lượng 09:45. S2: C8 "Chưa ra", ô Ra "—", "≥ 04:30".

**TC-SO1-04 — Phương tiện đi kèm** · REQ-SO1-04, BR-LT-05 · Trung bình
- Mong đợi: C1, C2, C5 có biển số; chỉ tiêu SO-01 không thay đổi khi xoá liên kết phương tiện (trên bản sao dữ liệu thử).

**TC-SO1-05 — Bộ lọc SO-01** · REQ-SO1-05, REQ-GEN-06 · Trung bình
- Bước: lần lượt lọc Chiều = Vào–Ra; Lý do = Việc riêng có phép; Trạng thái = Chưa hoàn tất; Chỉ dòng có đính chính; CBCS = CB001.
- Mong đợi: {C8}; {C3, C5}; {C5, C4}; {C6}; {C1, C2}; mỗi lần chỉ tiêu tính trên tập đã lọc và cân đối.

**TC-SO1-06 — SO-01 khi kỳ chưa kết thúc** · REQ-GEN-03 · Cao
- Dữ liệu: S2. Mong đợi: theo "Kết quả mong đợi S2".

### 6.3. SO-02 (TC-SO2)

**TC-SO2-01 — Nội dung SO-02** · REQ-SO2-01 · Cao · UAT
- Mong đợi: 6 dòng K1, K3, K4, K2, K5, K6; 13 cột theo §4.4; K3, K4 dòng 3 ô Khách "Đoàn ĐK-01"; K5 cột Giấy tờ "Không xuất trình".

**TC-SO2-02 — Chỉ tiêu SO-02** · REQ-SO2-02, REQ-GEN-14 · Cao
- Mong đợi: 0 / 6 / 4 / 2 (1 / 1) / quá hạn 1; khách có định danh duy nhất 4; lượt không định danh 1 (ghi riêng, không có chỉ tiêu "5 khách"); số đoàn 1; thẻ chưa thu hồi 2.

**TC-SO2-03 — Chuẩn hoá số giấy tờ** · REQ-SO2-02, BR-DN-02 · Cao
- Mong đợi: K1 và K2 là một khách; đổi số giấy tờ K2 thành `001090000999` (bản sao dữ liệu) → khách duy nhất 5.

**TC-SO2-04 — Đoàn và bộ lọc SO-02** · REQ-SO2-03, REQ-SO2-04 · Trung bình
- Bước: lọc Đoàn = ĐK-01; lọc Người tiếp = Phòng Hậu cần; lọc Chỉ khách quá hạn; lọc Số thẻ = K06.
- Mong đợi: {K3, K4}; {K2, K5}; {K5}; {K6}.

**TC-SO2-05 — Khách không định danh** · REQ-SO2-02, BR-DN-02 · Cao
- Bước: thêm (bản sao dữ liệu) một lượt khách không giấy tờ cùng tên "Ông Quang" lúc 16:00.
- Mong đợi: lượt khách không định danh = 2 (không gộp theo tên); khách có định danh duy nhất vẫn 4.

**TC-SO2-06 — Che số giấy tờ trong phụ lục đính chính** · REQ-GEN-19, BR-BM-01 · Cao
- Bước: đính chính số giấy tờ K6 từ `001190000444` thành `001190000445`; `trucban01` xuất SO-02.
- Mong đợi: phụ lục ghi `********0444` → `********0445`; không có số đầy đủ ở bất kỳ đâu trong file.

### 6.4. SO-03 (TC-SO3)

**TC-SO3-01 — Nội dung và chuẩn hoá biển số** · REQ-SO3-01, REQ-SO3-02, BR-DN-03 · Cao · UAT
- Mong đợi: 5 dòng P1, P3, P5, P2, P4; biển số in như ghi nhận ("30A-123.45" và "30A12345"); phương tiện có biển duy nhất 3; P5 in "Không biển — KB-001".

**TC-SO3-02 — Chỉ tiêu SO-03** · REQ-SO3-02, REQ-GEN-14 · Cao
- Mong đợi: 0 / 5 / 4 / 1 (1 / 0) / quá hạn 0; lượt không biển 1; theo loại và theo nguồn như S1.

**TC-SO3-03 — Lượt Vào–Ra của phương tiện** · REQ-SO3-01 · Trung bình
- Mong đợi: P3 Chiều "Vào–Ra", Vào 08:28, Ra 09:50, thời lượng 01:22.

**TC-SO3-04 — Bộ lọc SO-03** · REQ-SO3-04, REQ-GEN-06 · Trung bình
- Bước: lọc Nguồn = Cơ quan; Biển số chứa "30A123"; Loại = Xe máy.
- Mong đợi: {P1, P2}; {P1, P2} (khớp theo biển chuẩn hoá); {P4}.

**TC-SO3-05 — Người điều khiển** · REQ-SO3-03 · Trung bình
- Mong đợi: P1, P2 "Nguyễn Văn An (CB001)"; P4 "Phạm Thị Dung (CB004)"; P3 "Bùi Văn Lâm"; P5 "Nguyễn Văn Tâm".

### 6.5. SO-04 (TC-SO4)

**TC-SO4-01 — Phần A khớp sổ riêng; phân biệt lượt và đối tượng** · REQ-SO4-01 (AC-SO4-01.1), REQ-SO4-02, BR-TONG-06 · Cao · UAT
- Bước: lập SO-04 S1; so với khối tổng hợp SO-01, SO-02, SO-03 cùng kỳ; lặp lại với lọc Cổng 2.
- Mong đợi: ba dòng đúng bảng S1 và bản mẫu §7.4 của `report_definitions.md`; tiêu đề hai tầng "SỐ LƯỢT" / "SỐ ĐỐI TƯỢNG"; mọi tiêu đề có đơn vị tính; khớp sổ riêng cả khi lọc Cổng 2.

**TC-SO4-02 — Không cộng chéo nhóm** · REQ-SO4-01 (AC-SO4-01.2), BR-TONG-04, BR-DN-05 · Cao
- Bước: kiểm tra màn hình, Excel (mọi sheet), Word, PDF của SO-04 S1.
- Mong đợi: không có dòng/ô "Tổng cộng" cộng CBCS + Khách + Phương tiện ở bất kỳ phần nào (ví dụ không có giá trị 17 = 6 + 6 + 5 lượt phát sinh, hay 13 = 6 + 4 + 3 đối tượng); có ghi chú "không cộng gộp giữa các nhóm".

**TC-SO4-03 — Phân bổ theo ngày** · REQ-SO4-03, BR-ND-06, BR-TONG-07 · Cao
- Dữ liệu: S3.
- Mong đợi: theo bảng Phần B của S3; dòng cuối cột CBCS có hoạt động = 6 với nhãn "Duy nhất cả kỳ (không phải tổng các dòng)".

**TC-SO4-04 — Lượt chưa hoàn tất** · REQ-SO4-05 · Cao · UAT
- Mong đợi: D1 CBCS 2 lượt (C5 quá hạn trước, rồi C4); D2 Khách 2 lượt (K5, K6); D3 Phương tiện 1 lượt (P4); mỗi bảng con có số lượng riêng, không có "5 lượt chưa hoàn tất" cộng chung; thời lượng tính đến chốt (C4 ≥ 01:15, K6 ≥ 06:30); số lượng mỗi bảng con bằng cột C05 Phần A.

**TC-SO4-05 — Phân bổ theo cổng** · REQ-SO4-04, BR-TONG-08 · Trung bình
- Mong đợi: bằng bảng "SO-04 Phần C (S1)" ở §5.2; sự kiện C4 Vào 00:20 26/10 và K6 Ra 00:10 26/10 không được đếm.

**TC-SO4-06 — Tóm tắt đính chính và huỷ** · REQ-SO4-06 · Trung bình
- Mong đợi: CBCS 1 lượt có đính chính, 1 lần, 1 bản ghi huỷ; Khách và Phương tiện 0; tham chiếu "Phụ lục đính chính của SO-01".

**TC-SO4-07 — Khổ giấy SO-04** · REQ-SO4-08, BR-IN-02 · Trung bình · UAT
- Mong đợi: PDF/Word A4 dọc; Phần D (nếu bật tuỳ chọn) ngang; tiêu đề bảng lặp khi sang trang (dùng DS-03).

**TC-SO4-08 — Nhật ký hợp nhất (chỉ khi `XN-19` = Có)** · REQ-SO4-07 · Thấp
- Mong đợi: S1 có 30 sự kiện (CBCS 11, Khách 10, Phương tiện 9) theo thời điểm tăng dần; không có dòng tổng.

### 6.6. Xuất file (TC-EXP)

**TC-EXP-01 — Nhất quán màn hình và ba định dạng** · REQ-EXP-01, BR-XF-01 · Cao
- Bước: với S1, S3, DS-03 (tháng 10): xuất ba định dạng cho bốn sổ; công cụ đối chiếu đọc file và so mã bản ghi theo thứ tự, giá trị ô, chỉ tiêu.
- Mong đợi: trùng hoàn toàn với màn hình (ngoài khác biệt trình bày đã định nghĩa ở BR-XF-02).

**TC-EXP-02 — Excel** · REQ-EXP-02, BR-XF-02 · Cao
- Mong đợi: sheet `SO01`, `Dinh_chinh`, `Thong_tin_trich_xuat`; dòng tiêu đề cố định và có bộ lọc tự động; ô thời điểm là kiểu ngày giờ (lọc theo ngày được trong Excel); thời lượng kiểu `[h]:mm` (DS-02 E9 hiển thị 136:00); C5 có "Là thời lượng tối thiểu" = Có; không có công thức; Print Preview: A4 ngang, lặp dòng tiêu đề.

**TC-EXP-03 — Word** · REQ-EXP-03, BR-XF-03 · Cao · UAT
- Mong đợi: A4 ngang (SO-01…03); dòng tiêu đề bảng lặp; không dòng nào ngắt trang; đầu/chân trang, số trang đúng; có khối tổng hợp, phụ lục, khối ký; chân trang có "Bản xuất để biên tập" (`XN-17`).

**TC-EXP-04 — PDF** · REQ-EXP-04, BR-XF-04 · Cao · UAT
- Mong đợi: phông được nhúng (kiểm bằng thuộc tính tài liệu); "Trang x/y" đúng; thuộc tính Title, Author, Subject đúng; lề đo trên bản in đúng ± 2 mm.

**TC-EXP-05 — Tên file** · REQ-EXP-05, BR-XF-05 · Thấp
- Mong đợi: ví dụ `SO01_CBCS_20261025-20261025_SO01-20261027-0003.pdf`; kỳ S3: `…_20261024-20261025_…`; không dấu, không khoảng trắng.

**TC-EXP-06 — Vượt giới hạn dòng** · REQ-EXP-06 · Trung bình
- Dữ liệu: DS-03 ngày có 5.001 lượt.
- Mong đợi: PDF và Word bị từ chối với thông báo; không có file cụt; Excel tạo được đủ 5.001 dòng.

**TC-EXP-07 — Tiếng Việt** · REQ-NFR-05 · Cao
- Dữ liệu: DS-04.
- Mong đợi: họ tên hiển thị đúng dấu ở màn hình và ba định dạng; bản NFC và NFD hiển thị giống nhau và được tìm thấy khi tìm kiếm; thứ tự sắp theo họ tên đúng §5.5.

**TC-EXP-08 — Excel của SO-04** · REQ-EXP-02 · Trung bình
- Mong đợi: các sheet `A_Chi_tieu`, `B_Theo_ngay`, `C_Theo_cong`, `D_Chua_hoan_tat`, `E_Dinh_chinh_huy`, `Thong_tin_trich_xuat`; số liệu khớp PDF.

**TC-EXP-09 — Chỉ tiêu giống nhau giữa định dạng** · REQ-EXP-01 · Cao
- Mong đợi: với S1, mọi chỉ tiêu ở PDF, Word, Excel giống nhau và giống nhật ký trích xuất.

**TC-EXP-10 — Không cần Internet** · REQ-EXP-07 · Cao
- Bước: ngắt hoàn toàn kết nối Internet của máy chủ và máy trạm; xem, in, xuất bốn sổ.
- Mong đợi: mọi chức năng hoạt động; phông, biểu tượng hiển thị đúng; không có yêu cầu mạng ra ngoài LAN (kiểm bằng công cụ dành cho nhà phát triển của trình duyệt).

### 6.7. Phi chức năng (TC-NFR)

**TC-NFR-01 — Hiệu năng** · REQ-NFR-01 · Trung bình
- Dữ liệu: DS-03. Đo 5 lần, lấy trung vị.
- Mong đợi: đạt chỉ tiêu REQ-NFR-01 (sau khi `XN-24` được xác nhận).

**TC-NFR-02 — Dễ đọc khi in** · REQ-NFR-02 · Trung bình · UAT
- Mong đợi: in thực tế bốn sổ; cỡ chữ bảng ≥ 9 pt; không ô nào bị cắt chữ; người dùng đơn vị xác nhận đọc được.

**TC-NFR-03 — Máy trạm lệch giờ** · REQ-NFR-03, BR-KY-01 · Cao
- Bước: dùng máy trạm lệch +15 phút, chọn "Hôm nay", xuất.
- Mong đợi: kỳ, thời điểm chốt, thời điểm trích xuất theo giờ máy chủ.

**TC-NFR-04 — Trình duyệt** · REQ-NFR-04 · Trung bình
- Mong đợi: TC-GEN-05, TC-EXP-04 đạt trên từng trình duyệt theo `XN-27`.

### 6.8. Màn hình "Xuất sổ theo dõi" (TC-MH)

Tự động hoá trong `baocao/tests/test_man_hinh_xuat.py`; dữ liệu DS-01, đồng hồ giả lập 09:00 27/10/2026.

| Mã | Nội dung | Lớp kiểm thử |
|---|---|---|
| TC-MH-01 | Màn hình chỉ hiện sổ được xem; ngày mặc định theo giờ Việt Nam; không tham chiếu tài nguyên Internet | `GiaoDienTest` |
| TC-MH-02 | Xem trước: thứ tự dòng, lượt qua nửa đêm, chưa hoàn tất, chỉ tiêu; không ghi lịch sử; kỳ trống không có dòng giả | `XemTruocTest` |
| TC-MH-03 | Xuất ba định dạng: số dòng xem trước = tệp = lịch sử = bản chốt; thông báo thành công đúng giờ Việt Nam | `XuatVaDoiChieuTest` |
| TC-MH-04 | Kỳ một ngày / khoảng ngày / tháng; ranh giới 00:00 giờ Việt Nam; bộ lọc từ giao diện tới tệp; sổ tổng hợp | `XuatVaDoiChieuTest` |
| TC-MH-05 | Bản chốt: tải lại trả đúng tệp sau khi dữ liệu gốc đổi; tệp lưu bị sửa thì không tải | `BanChotVaXemTruocTest` |
| TC-MH-06 | Dữ liệu nhập sai, kỳ quá dài cho Word/PDF, lỗi tạo tệp, lỗi lưu bản chốt | `KiemTraNhapVaThatBaiTest` |
| TC-MH-07 | Không đủ quyền không tạo tệp; giới hạn cổng; không tải được tệp của người khác hay bằng đường dẫn đoán | `PhanQuyenTest` |
| TC-MH-08 | Xem trước không phải bản chốt: dữ liệu đổi giữa xem trước và xuất thì báo chênh lệch | `BanChotVaXemTruocTest` |

---

## 7. Ma trận truy vết

| Yêu cầu | Tiêu chí nghiệm thu | Quy tắc chính | Ca kiểm thử |
|---|---|---|---|
| REQ-GEN-01 | AC-GEN-01.1–01.2 | BR-IN-01 | TC-GEN-01 |
| REQ-GEN-02 | AC-GEN-02.1–02.4 | BR-KY-01…06 | TC-GEN-02, TC-GEN-03, TC-GEN-29 |
| REQ-GEN-03 | AC-GEN-03.1–03.2 | BR-KY-04 | TC-GEN-04, TC-SO1-06 |
| REQ-GEN-04 | AC-GEN-04.1–04.2 | BR-IN-08 | TC-GEN-05 |
| REQ-GEN-05 | AC-GEN-05.1–05.3 | BR-IN-03…06 | TC-GEN-06 |
| REQ-GEN-06 | AC-GEN-06.1–06.2 | BR-KY-07, BR-TONG-03 | TC-GEN-07, TC-GEN-27, TC-SO1-05, TC-SO3-04 |
| REQ-GEN-07 | AC-GEN-07.1–07.2 | BR-IN-07 | TC-GEN-08 |
| REQ-GEN-08 | AC-GEN-08.1–08.2 | BR-TT-01…04 | TC-GEN-09 |
| REQ-GEN-09 | AC-GEN-09.1–09.2 | BR-CHT-01…05 | TC-GEN-10, TC-GEN-11 |
| REQ-GEN-10 | AC-GEN-10.1–10.3 | BR-ND-01…06 | TC-GEN-12, TC-GEN-13 |
| REQ-GEN-11 | AC-GEN-11.1–11.3 | BR-DC-01…07 | TC-GEN-14, TC-GEN-15, TC-GEN-26 |
| REQ-GEN-12 | AC-GEN-12.1–12.2 | BR-DC-06, BR-TONG-02 | TC-GEN-16 |
| REQ-GEN-13 | AC-GEN-13.1 | BR-DC-08 | TC-GEN-17 |
| REQ-GEN-14 | AC-GEN-14.1–14.3 | BR-TONG-01…05 | TC-GEN-18, TC-SO1-02, TC-SO2-02, TC-SO3-02 |
| REQ-GEN-15 | AC-GEN-15.1–15.3 | BR-TX-01, 02, 05, 06 | TC-GEN-19, TC-GEN-25 |
| REQ-GEN-16 | AC-GEN-16.1–16.2 | BR-TX-03, BR-TX-04 | TC-GEN-20 |
| REQ-GEN-17 | AC-GEN-17.1–17.2 | BR-IN-09 | TC-GEN-21, TC-GEN-30 |
| REQ-GEN-18 | (mô tả yêu cầu) | — | TC-GEN-22 |
| REQ-GEN-19 | AC-GEN-19.1–19.2 | BR-BM-01…03 | TC-GEN-23, TC-SO2-06 |
| REQ-GEN-20 | AC-GEN-20.1 | — | TC-GEN-24 |
| REQ-GEN-21 | (mô tả yêu cầu) | — | TC-GEN-30 |
| REQ-GEN-22 | (mô tả yêu cầu) | BR-LT-04, BR-LT-06 | TC-GEN-28 |
| REQ-SO1-01 | AC-SO1-01.1 | BR-LT-01, BR-LT-02 | TC-SO1-01 |
| REQ-SO1-02 | AC-SO1-02.1 | BR-TONG-05, BR-DN-01 | TC-SO1-02 |
| REQ-SO1-03 | (mô tả yêu cầu) | BR-LT-02, BR-TT-01 | TC-SO1-03 |
| REQ-SO1-04 | (mô tả yêu cầu) | BR-LT-05 | TC-SO1-04 |
| REQ-SO1-05 | (mô tả yêu cầu) | BR-KY-07 | TC-SO1-05 |
| REQ-SO2-01 | AC-SO2-01.1 | BR-LT-01 | TC-SO2-01 |
| REQ-SO2-02 | AC-SO2-02.1 | BR-DN-02, BR-TONG-05 | TC-SO2-02, TC-SO2-03, TC-SO2-05 |
| REQ-SO2-03 | (mô tả yêu cầu) | — | TC-SO2-04 |
| REQ-SO2-04 | (mô tả yêu cầu) | BR-KY-07 | TC-SO2-04 |
| REQ-SO3-01 | AC-SO3-01.1 | BR-DN-03 | TC-SO3-01, TC-SO3-03 |
| REQ-SO3-02 | AC-SO3-02.1 | BR-DN-03, BR-TONG-05 | TC-SO3-01, TC-SO3-02 |
| REQ-SO3-03 | (mô tả yêu cầu) | — | TC-SO3-05 |
| REQ-SO3-04 | (mô tả yêu cầu) | BR-KY-07 | TC-SO3-04 |
| REQ-SO4-01 | AC-SO4-01.1–01.2 | BR-TONG-04, 06, BR-DN-05 | TC-SO4-01, TC-SO4-02 |
| REQ-SO4-02 | AC-SO4-02.1 | BR-TONG-01 | TC-SO4-01 |
| REQ-SO4-03 | AC-SO4-03.1 | BR-ND-06, BR-TONG-07 | TC-SO4-03 |
| REQ-SO4-04 | AC-SO4-04.1 | BR-TONG-08 | TC-SO4-05 |
| REQ-SO4-05 | AC-SO4-05.1 | BR-CHT-01 | TC-SO4-04 |
| REQ-SO4-06 | (mô tả yêu cầu) | BR-DC-04, BR-DC-06 | TC-SO4-06 |
| REQ-SO4-07 | (mô tả yêu cầu) | — | TC-SO4-08 |
| REQ-SO4-08 | (mô tả yêu cầu) | BR-IN-02 | TC-SO4-07 |
| REQ-EXP-01 | AC-EXP-01.1 | BR-XF-01 | TC-EXP-01, TC-EXP-09 |
| REQ-EXP-02 | (mô tả yêu cầu) | BR-XF-02 | TC-EXP-02, TC-EXP-08 |
| REQ-EXP-03 | (mô tả yêu cầu) | BR-XF-03 | TC-EXP-03 |
| REQ-EXP-04 | (mô tả yêu cầu) | BR-XF-04, BR-IN-02…09 | TC-EXP-04, TC-EXP-07 |
| REQ-EXP-05 | (mô tả yêu cầu) | BR-XF-05 | TC-EXP-05 |
| REQ-EXP-06 | (mô tả yêu cầu) | BR-KY-06 | TC-EXP-06 |
| REQ-EXP-07 | (mô tả yêu cầu) | — | TC-EXP-10 |
| REQ-EXP-08 | AC-EXP-08.1–08.3 | BR-KY-01, BR-KY-02, BR-TX-06 | TC-MH-01…TC-MH-04, TC-MH-06, TC-MH-08 |
| REQ-EXP-09 | AC-EXP-09.1–09.2 | BR-DC-07, BR-TX-05 | TC-MH-05, TC-MH-07 |
| REQ-NFR-01 | Bảng mục 8 | — | TC-NFR-01 |
| REQ-NFR-02 | Bảng mục 8 | BR-IN-02 | TC-NFR-02 |
| REQ-NFR-03 | Bảng mục 8 | BR-KY-01 | TC-NFR-03 |
| REQ-NFR-04 | Bảng mục 8 | — | TC-NFR-04 |
| REQ-NFR-05 | Bảng mục 8 | — | TC-EXP-07 |
| REQ-NFR-06 | Bảng mục 8 | BR-DC-01, BR-TX-05 | TC-GEN-19 |

## 8. Tiêu chí bắt đầu và kết thúc

- **Bắt đầu G1/G2:** G0 đạt; DS-01…DS-04 đã nạp và kiểm tra bằng truy vấn đối chiếu; đồng hồ giả lập hoạt động.
- **Kết thúc G2:** mọi ca mức Cao đạt; không còn lỗi Nghiêm trọng/Cao; các ca phụ thuộc `XN` (TC-SO4-08, TC-NFR-01) được thực hiện theo kết quả xác nhận.
- **Kết thúc G3:** mọi ca có "UAT" đạt khi người dùng đơn vị thực hiện; bản in thử của bốn sổ được đơn vị ký nhận.
