# Đặc tả yêu cầu — Các sổ ra/vào

| Thuộc tính | Giá trị |
|---|---|
| Dự án | QL CBCS LAN — Quản lý CBCS, khách và phương tiện ra/vào |
| Mã tài liệu | QLCBCS-REQ-SO |
| Phiên bản | 0.1 — **Dự thảo để thống nhất** |
| Ngày lập | 26/10/2026 |
| Trạng thái | Chờ đơn vị xác nhận các mục `XN-xx` (mục 9). **Chưa lập trình** cho đến khi tài liệu được thống nhất (cổng G0, xem `test_plan.md` §2). |
| Tài liệu đi kèm | [`report_definitions.md`](report_definitions.md) (định nghĩa mẫu sổ), [`business_rules.md`](business_rules.md) (quy tắc nghiệp vụ), [`test_plan.md`](test_plan.md) (kế hoạch và ca kiểm thử) |

---

## 1. Mục đích và phạm vi

### 1.1. Mục đích

Tài liệu này đặc tả yêu cầu cho chức năng **xem, in và xuất bốn loại sổ ra/vào** của phần mềm QL CBCS LAN:

| Mã sổ | Tên sổ (đề xuất, `XN-04`) | Định nghĩa chi tiết |
|---|---|---|
| SO-01 | Sổ theo dõi CBCS ra/vào | `report_definitions.md` §3 |
| SO-02 | Sổ theo dõi khách ra/vào | `report_definitions.md` §4 |
| SO-03 | Sổ theo dõi phương tiện ra/vào | `report_definitions.md` §5 |
| SO-04 | Sổ tổng hợp ra/vào | `report_definitions.md` §6 |

### 1.2. Phạm vi

**Trong phạm vi**

- Hiển thị bốn sổ trên màn hình (trình duyệt trong mạng LAN).
- In sổ và xuất ra Excel (`.xlsx`), Word (`.docx`) và PDF theo ma trận định dạng ở mục 7 (cần đối chiếu với nội dung đã thống nhất trước đây, `XN-16`).
- Quy tắc lọc, khoảng thời gian, sắp xếp, tính tổng, hiển thị trạng thái, xử lý lượt chưa hoàn tất, lượt qua nửa đêm, dữ liệu đính chính và dữ liệu bị huỷ.
- Ghi thời điểm trích xuất, người trích xuất, người lập sổ, mã trích xuất và nhật ký trích xuất.

**Ngoài phạm vi của tài liệu này**

- Chức năng ghi nhận ra/vào (nhập liệu). Tài liệu chỉ nêu **dữ liệu tối thiểu mà các sổ cần** (mục 5) để làm ràng buộc cho phân hệ ghi nhận.
- Thiết kế cơ sở dữ liệu chi tiết, mã nguồn, giao diện quản trị ngoài phần cấu hình sổ.
- Tích hợp thiết bị (camera, đầu đọc thẻ, barrier), ký số, gửi sổ qua mạng ra ngoài LAN.
- Bất kỳ biểu mẫu pháp lý nào (xem mục 2).

### 1.3. Bối cảnh kỹ thuật (ràng buộc)

- Ứng dụng web Django, cơ sở dữ liệu PostgreSQL, chạy trên máy chủ nội bộ, người dùng truy cập qua mạng LAN.
- Hệ thống **không được phụ thuộc Internet** khi hiển thị, in hay xuất sổ (phông chữ, thư viện giao diện, thư viện xuất file đều cài đặt nội bộ).
- Mọi thời điểm lấy theo **đồng hồ máy chủ**, múi giờ Asia/Ho_Chi_Minh (UTC+7).

---

## 2. Tính chất của các mẫu sổ

1. Bốn sổ là **mẫu nghiệp vụ nội bộ được thiết kế mới** cho phần mềm, nhằm dễ đọc trên màn hình và dễ in. Tài liệu **không giả định** các sổ này là biểu mẫu pháp lý, không sao chép hay mô phỏng biểu mẫu của văn bản quy phạm nào.
2. Mẫu sổ không dùng Quốc hiệu, tiêu ngữ, số và ký hiệu văn bản. Chân trang mỗi trang ghi "Mẫu nghiệp vụ nội bộ" (BR-IN-06).
3. Nếu đơn vị có quy định nội bộ hoặc văn bản cấp trên bắt buộc dùng biểu mẫu sổ cụ thể, đơn vị cung cấp mẫu đó và tài liệu này sẽ được điều chỉnh (`XN-01`). Trước khi có xác nhận, mọi nội dung trong `report_definitions.md` là **đề xuất**.
4. Chữ ký trên bản in là xác nhận nghiệp vụ nội bộ của đơn vị; giá trị pháp lý của bản in (nếu có) do đơn vị quyết định, không thuộc phạm vi phần mềm.

---

## 3. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| CBCS | Cán bộ, chiến sĩ thuộc danh sách quản lý của đơn vị, có mã CBCS nội bộ. |
| Khách | Người không thuộc danh sách CBCS, vào đơn vị theo thủ tục tiếp khách. |
| Phương tiện | Xe hoặc thiết bị di chuyển qua điểm kiểm soát (ô tô, xe máy, xe chuyên dùng…). |
| Nhóm đối tượng | Một trong ba nhóm: CBCS, khách, phương tiện. Mỗi nhóm có cách định danh riêng (BR-DN). |
| Điểm kiểm soát (cổng) | Nơi ghi nhận sự kiện ra/vào; danh mục do quản trị cấu hình. |
| Sự kiện | Một lần ghi nhận "Ra" hoặc "Vào" của một đối tượng tại một cổng, có thời điểm sự kiện và thời điểm ghi nhận. |
| Lượt | Cặp gồm **sự kiện mở** và (nếu đã có) **sự kiện đóng** của cùng một đối tượng (BR-LT-01). |
| Chiều lượt | "Ra–Vào" (đối tượng đang ở trong đi ra rồi trở về) hoặc "Vào–Ra" (đối tượng ở ngoài đi vào rồi ra) (BR-LT-02). |
| Lượt hoàn tất | Lượt đã có sự kiện đóng trước thời điểm chốt số liệu. |
| Lượt chưa hoàn tất | Lượt chưa có sự kiện đóng tại thời điểm chốt số liệu (BR-CHT-01). |
| Kỳ | Khoảng thời gian `[Từ, Đến)` người dùng chọn để lập sổ (BR-KY-02). |
| Thời điểm chốt số liệu | `min(Đến, thời điểm trích xuất)`; mọi trạng thái và chỉ tiêu được tính tại thời điểm này (BR-KY-04). |
| Thời điểm trích xuất | Giờ máy chủ khi hệ thống bắt đầu đọc dữ liệu để lập sổ (BR-TX-01). |
| Người trích xuất | Tài khoản đăng nhập thực hiện thao tác in/xuất; hệ thống tự ghi, không sửa được. |
| Người lập sổ | Người ký ở mục "Người lập sổ" trên bản in; mặc định là người trích xuất, có thể đổi (BR-TX-04). |
| Mã trích xuất | Mã duy nhất cấp cho mỗi lần in/xuất, in trên mọi trang (BR-TX-02). |
| Đính chính | Sửa giá trị của bản ghi đã lưu, có lưu giá trị cũ, lý do, người và thời điểm sửa (BR-DC). |
| Huỷ | Đánh dấu bản ghi nhập nhầm là không có giá trị; bản ghi vẫn được lưu, không tính vào sổ (BR-DC-06). |
| Ghi bổ sung | Sự kiện được ghi nhận muộn hơn thời điểm xảy ra quá ngưỡng quy định (BR-DC-08). |
| Đối tượng duy nhất | Số đối tượng khác nhau (theo định danh) trong một tập lượt (BR-DN). |
| Không định danh | Khách không có giấy tờ, phương tiện không có biển số: không xác định được là cùng một đối tượng giữa các lượt (BR-DN-02, BR-DN-03). |

---

## 4. Người dùng và vai trò (đề xuất — `XN-02`)

| Vai trò | Nhu cầu chính với các sổ | Quyền đề xuất |
|---|---|---|
| Trực ban / bảo vệ cổng | Xem sổ trong ca, in sổ ca trực để giao ca, ký "Người lập sổ". | Xem và xuất SO-01, SO-02, SO-03, SO-04 trong phạm vi cổng được phân công; số giấy tờ của khách hiển thị đã che. |
| Chỉ huy trực / chỉ huy đơn vị | Kiểm tra, ký xác nhận sổ; nắm lượt chưa hoàn tất, quá hạn. | Xem, xuất mọi sổ; xem bản ghi đã huỷ. |
| Lãnh đạo đơn vị | Xem sổ tổng hợp theo ngày, tuần, tháng. | Xem, xuất SO-04; xem các sổ riêng. |
| Cán bộ tổ chức / hành chính | Tra cứu lượt ra/vào của CBCS. | Xem, xuất SO-01. |
| Quản trị hệ thống | Cấu hình tên đơn vị, cổng, chức danh ký, ngưỡng; xem nhật ký trích xuất. | Cấu hình; xem nhật ký; không mặc định xem dữ liệu cá nhân đầy đủ. |

---

## 5. Dữ liệu tối thiểu các sổ cần từ phân hệ ghi nhận

Đây là ràng buộc đầu vào; nếu phân hệ ghi nhận không cung cấp được trường nào thì cột tương ứng trong sổ phải được điều chỉnh.

| Nhóm | Trường bắt buộc | Trường tuỳ chọn (in nếu có) |
|---|---|---|
| Chung cho mọi sự kiện | Mã bản ghi; nhóm đối tượng; mã đối tượng; loại sự kiện (Ra/Vào); thời điểm sự kiện; thời điểm ghi nhận; cổng; người ghi nhận; trạng thái bản ghi (hiệu lực/đã huỷ); lịch sử đính chính | Ghi chú |
| CBCS | Mã CBCS; họ và tên; đơn vị/bộ phận | Cấp bậc, chức vụ, số hiệu (`XN-06`); lý do ra ngoài (`XN-07`); giờ về dự kiến; phương tiện đi kèm |
| Khách | Họ và tên; người/bộ phận tiếp; mục đích | Loại và số giấy tờ; cơ quan/địa chỉ; số thẻ khách; mã đoàn; giờ ra dự kiến; phương tiện; số điện thoại (`XN-08`) |
| Phương tiện | Biển số (hoặc mã tạm cho xe không biển); loại phương tiện; nguồn (cơ quan / CBCS / khách / khác) | Người điều khiển (liên kết CBCS hoặc khách nếu có); lý do, số lệnh điều xe, hàng hoá, số người (`XN-26`); giờ về dự kiến |

---

## 6. Yêu cầu chức năng

Quy ước: **M** = bắt buộc, **S** = nên có, **C** = tuỳ chọn. Mỗi yêu cầu có tiêu chí nghiệm thu `AC-…` và ca kiểm thử `TC-…` (chi tiết trong `test_plan.md`). Các quy tắc `BR-…` nằm trong `business_rules.md`.

### 6.1. Yêu cầu chung cho cả bốn sổ (REQ-GEN)

#### REQ-GEN-01 — Bốn sổ riêng biệt (M)
Hệ thống cung cấp bốn sổ SO-01…SO-04, truy cập từ một mục "Sổ ra/vào". Mỗi sổ có mã sổ, tên sổ và phiên bản mẫu in trên đầu trang.
- AC-GEN-01.1: Người dùng có quyền mở được đúng bốn sổ; sổ không có quyền thì không hiển thị trong menu.
- AC-GEN-01.2: Mã sổ, tên sổ và phiên bản mẫu hiển thị đúng như `report_definitions.md` §2.2.
- Quy tắc: BR-IN-01. Kiểm thử: TC-GEN-01.

#### REQ-GEN-02 — Chọn kỳ (M)
Người dùng chọn kỳ bằng các lựa chọn nhanh (Hôm nay, Hôm qua, Ca trực hiện tại, Ca trực trước, Tuần này, Tháng này, Tháng trước) hoặc nhập "Từ" và "Đến" (ngày và giờ:phút). Mặc định: Hôm nay.
- AC-GEN-02.1: Mỗi lựa chọn nhanh cho ra đúng khoảng `[Từ, Đến)` theo BR-KY-03.
- AC-GEN-02.2: Không cho chọn "Đến" ≤ "Từ"; thông báo lỗi bằng tiếng Việt.
- AC-GEN-02.3: Sự kiện đúng tại "Từ" thuộc kỳ; sự kiện đúng tại "Đến" không thuộc kỳ.
- AC-GEN-02.4: Kỳ vượt giới hạn cho phép (`XN-18`) bị chặn hoặc cảnh báo theo BR-KY-06.
- Quy tắc: BR-KY-01…BR-KY-06. Kiểm thử: TC-GEN-02, TC-GEN-03, TC-GEN-29. Cần xác nhận: `XN-10`, `XN-18`.

#### REQ-GEN-03 — Kỳ chưa kết thúc (M)
Khi "Đến" sau thời điểm trích xuất, thời điểm chốt số liệu là thời điểm trích xuất; sổ ghi rõ "Số liệu tính đến … (kỳ chưa kết thúc)".
- AC-GEN-03.1: Lượt có sự kiện mở sau thời điểm chốt không xuất hiện trong sổ.
- AC-GEN-03.2: Đầu trang và khối tổng hợp đều ghi cùng một thời điểm chốt.
- Quy tắc: BR-KY-04. Kiểm thử: TC-GEN-04, TC-SO1-06.

#### REQ-GEN-04 — Màn hình và bản in thống nhất nội dung (M)
Trên màn hình, mỗi sổ hiển thị cùng danh sách cột, thứ tự cột, thứ tự dòng, trạng thái và số liệu tổng như bản in/xuất của cùng điều kiện và cùng thời điểm chốt.
- AC-GEN-04.1: So sánh màn hình với PDF cùng điều kiện: trùng số dòng, thứ tự dòng, giá trị từng ô (trừ định dạng hiển thị) và mọi chỉ tiêu tổng.
- AC-GEN-04.2: Màn hình có tiêu đề bảng cố định khi cuộn; dòng chưa hoàn tất in đậm; đọc được ở độ phân giải 1366×768 không cần cuộn ngang với bộ cột mặc định.
- Quy tắc: BR-IN-08. Kiểm thử: TC-GEN-05.

#### REQ-GEN-05 — Thông tin đầu trang, đầu trang lặp và chân trang (M)
Trang đầu có khối đầu sổ; các trang sau có đầu trang rút gọn; mọi trang có chân trang theo `report_definitions.md` §2.3–§2.5.
- AC-GEN-05.1: Trang 1 có đủ: cơ quan chủ quản, tên đơn vị, mã sổ, phiên bản mẫu, tên sổ, kỳ, điểm kiểm soát, điều kiện lọc, thời điểm chốt số liệu.
- AC-GEN-05.2: Từ trang 2 có đầu trang rút gọn (tên đơn vị – tên sổ – kỳ) và **dòng tiêu đề bảng lặp lại**.
- AC-GEN-05.3: Mọi trang có chân trang: mã trích xuất, thời điểm trích xuất, "Mẫu nghiệp vụ nội bộ", "Trang x/y".
- Quy tắc: BR-IN-03…BR-IN-06. Kiểm thử: TC-GEN-06. Cần xác nhận: `XN-03`, `XN-04`.

#### REQ-GEN-06 — Lọc và ghi điều kiện lọc lên sổ (M)
Mỗi sổ có bộ lọc theo `report_definitions.md`. Mọi điều kiện lọc khác "Tất cả" được in ở đầu sổ; nếu có ít nhất một điều kiện lọc ngoài kỳ, sổ ghi "Sổ đã lọc — không phải toàn bộ dữ liệu của kỳ".
- AC-GEN-06.1: Chỉ tiêu tổng tính trên tập đã lọc.
- AC-GEN-06.2: Lọc theo cổng lấy lượt có sự kiện mở **hoặc** sự kiện đóng tại cổng đã chọn.
- Quy tắc: BR-TONG-03, BR-KY-07. Kiểm thử: TC-GEN-07, TC-GEN-27, TC-SO1-05, TC-SO3-04.

#### REQ-GEN-07 — Sắp xếp và số thứ tự (M)
Mặc định sắp theo thời điểm mở lượt tăng dần, trùng thì theo mã bản ghi tăng dần. Có thể chọn sắp xếp khác theo từng sổ. STT đánh liên tục từ 1 trên toàn sổ (không đánh lại theo trang).
- AC-GEN-07.1: Với bộ dữ liệu DS-01, thứ tự dòng đúng như `test_plan.md` §5.
- AC-GEN-07.2: Hai lượt cùng thời điểm mở luôn ra cùng một thứ tự giữa các lần trích xuất.
- Quy tắc: BR-IN-07. Kiểm thử: TC-GEN-08.

#### REQ-GEN-08 — Hiển thị trạng thái (M)
Trạng thái hiển thị bằng **chữ** theo bảng BR-TT-01, kèm các ký hiệu ghi chú BR-TT-02. Màu sắc trên màn hình chỉ là bổ trợ; bản in đen trắng vẫn phân biệt được mọi trạng thái.
- AC-GEN-08.1: In đen trắng trên máy in laser của đơn vị, người kiểm tra phân biệt đúng mọi trạng thái mà không cần màu.
- AC-GEN-08.2: Nhãn trạng thái dùng đúng từ ngữ theo nhóm đối tượng và chiều lượt ("Chưa về", "Chưa ra"…).
- Quy tắc: BR-TT-01…BR-TT-04. Kiểm thử: TC-GEN-09.

#### REQ-GEN-09 — Lượt chưa hoàn tất (M)
Lượt chưa hoàn tất tại thời điểm chốt vẫn có trong sổ; ô sự kiện đóng để "—"; thời lượng ghi "≥ hh:mm" tính đến thời điểm chốt; có trạng thái "Chưa về"/"Chưa ra", và "Quá hạn" nếu đủ điều kiện. Hệ thống không tự đóng lượt.
- AC-GEN-09.1: Với DS-01, lượt C5 hiển thị "—", "≥ 08:00", "Chưa về – Quá hạn".
- AC-GEN-09.2: Không có tác vụ tự động nào thêm sự kiện đóng.
- Quy tắc: BR-CHT-01…BR-CHT-05. Kiểm thử: TC-GEN-10, TC-GEN-11. Cần xác nhận: `XN-09`.

#### REQ-GEN-10 — Lượt qua nửa đêm và qua kỳ (M)
Một lượt qua nửa đêm là **một** lượt. Ô thời điểm luôn ghi cả giờ và ngày. Lượt mở trước kỳ ghi "(từ kỳ trước)"; lượt đóng sau thời điểm chốt ghi "(sau kỳ)" và có trạng thái "Hoàn tất sau kỳ".
- AC-GEN-10.1: Với DS-01, C3 có mặt trong sổ ngày 25/10 với "(từ kỳ trước)", được đếm vào "Từ kỳ trước", không đếm vào "Phát sinh trong kỳ".
- AC-GEN-10.2: C4 có mặt trong sổ ngày 25/10 với "(sau kỳ)", trạng thái "Hoàn tất sau kỳ", được đếm vào "Chưa hoàn tất tại thời điểm chốt".
- AC-GEN-10.3: Không có lượt nào bị tách thành hai dòng do qua nửa đêm.
- Quy tắc: BR-ND-01…BR-ND-06. Kiểm thử: TC-GEN-12, TC-GEN-13. Cần xác nhận: `XN-11`.

#### REQ-GEN-11 — Dữ liệu đính chính (M)
Sổ dùng giá trị hiện hành; dòng có đính chính mang ký hiệu "ĐC(n)"; cuối sổ có "Phụ lục đính chính" liệt kê trường, giá trị cũ, giá trị mới, lý do, người và thời điểm đính chính.
- AC-GEN-11.1: Với DS-01, C6 hiển thị giờ vào 09:40, ghi chú "ĐC(1)", phụ lục có dòng (1) với giá trị cũ 09:14.
- AC-GEN-11.2: Lượt bị đính chính thời gian khiến ra khỏi kỳ thì không có trong sổ của kỳ đó và xuất hiện ở sổ của kỳ mới kèm "ĐC".
- AC-GEN-11.3: Bản đã xuất không thay đổi khi có đính chính sau đó; lần xuất sau có mã trích xuất mới và phản ánh đính chính.
- Quy tắc: BR-DC-01…BR-DC-07. Kiểm thử: TC-GEN-14, TC-GEN-15, TC-GEN-26. Cần xác nhận: `XN-13`.

#### REQ-GEN-12 — Bản ghi đã huỷ (M)
Bản ghi đã huỷ không tính vào bất kỳ chỉ tiêu nào và mặc định không hiển thị. Người có quyền có thể chọn "Hiện bản ghi đã huỷ"; khi đó dòng huỷ có STT "—", trạng thái "ĐÃ HUỶ", lý do huỷ, và sổ ghi rõ có hiện bản ghi huỷ.
- AC-GEN-12.1: Với DS-01, C7 không xuất hiện mặc định; khi bật hiện, C7 xuất hiện, STT các dòng khác không đổi, chỉ tiêu không đổi.
- AC-GEN-12.2: Khối tổng hợp ghi "Số bản ghi đã huỷ (không tính): 1".
- Quy tắc: BR-DC-06, BR-TONG-02. Kiểm thử: TC-GEN-16.

#### REQ-GEN-13 — Đánh dấu ghi bổ sung (S)
Sự kiện có thời điểm ghi nhận muộn hơn thời điểm sự kiện quá ngưỡng (`XN-12`, đề xuất 30 phút) mang ký hiệu "GBS" ở cột ghi chú.
- AC-GEN-13.1: Với DS-01, K4 có "GBS"; các lượt khác không có.
- Quy tắc: BR-DC-08. Kiểm thử: TC-GEN-17.

#### REQ-GEN-14 — Khối tổng hợp số liệu cuối sổ (M)
Mỗi sổ riêng có khối "Tổng hợp số liệu" theo BR-TONG-01, ghi rõ thời điểm chốt. Thoả đẳng thức cân đối: *Từ kỳ trước + Phát sinh trong kỳ = Hoàn tất trong kỳ + Chưa hoàn tất tại thời điểm chốt*.
- AC-GEN-14.1: Với DS-01 kỳ 25/10: SO-01 = 1 / 6 / 5 / 2; SO-02 = 0 / 6 / 4 / 2; SO-03 = 0 / 5 / 4 / 1.
- AC-GEN-14.2: Đẳng thức cân đối đúng với mọi bộ dữ liệu kiểm thử.
- AC-GEN-14.3: Không có chỉ tiêu "tổng thời lượng"; không có dòng cộng trang.
- Quy tắc: BR-TONG-01…BR-TONG-05. Kiểm thử: TC-GEN-18, TC-SO1-02, TC-SO2-02, TC-SO3-02.

#### REQ-GEN-15 — Thời điểm trích xuất, mã trích xuất, nhật ký (M)
Mỗi lần in/xuất sinh một mã trích xuất duy nhất; ghi thời điểm trích xuất (đến giây, giờ máy chủ) và người trích xuất; lưu nhật ký trích xuất. Xem trên màn hình không sinh mã nhưng ghi "Xem lúc …".
- AC-GEN-15.1: Mã, thời điểm, người trích xuất in ở chân trang mọi trang và ở khối "Thông tin trích xuất".
- AC-GEN-15.2: Nhật ký có đủ trường theo BR-TX-05; tra cứu được theo mã trích xuất.
- AC-GEN-15.3: Toàn bộ nội dung một lần xuất lấy từ cùng một trạng thái dữ liệu (đọc nhất quán).
- Quy tắc: BR-TX-01…BR-TX-06. Kiểm thử: TC-GEN-19, TC-GEN-25. Cần xác nhận: `XN-23`, `XN-28`.

#### REQ-GEN-16 — Người lập sổ (M)
Trước khi in/xuất, người dùng xác nhận "Người lập sổ": mặc định là người trích xuất, có thể chọn người khác trong danh sách người dùng/CBCS hoặc để trống để ký tay. Nhật ký ghi cả người trích xuất và người lập sổ.
- AC-GEN-16.1: Không thay đổi được người trích xuất.
- AC-GEN-16.2: Tên người lập sổ đã chọn in dưới dòng "(Ký, ghi rõ họ tên)".
- Quy tắc: BR-TX-03, BR-TX-04. Kiểm thử: TC-GEN-20.

#### REQ-GEN-17 — Khối ký xác nhận (M)
Trang cuối có khối ký gồm "Người lập sổ" và chức danh xác nhận do quản trị cấu hình. Khối ký không bị tách sang trang riêng nếu không kèm khối tổng hợp hoặc ít nhất phần cuối của bảng.
- AC-GEN-17.1: Khối ký luôn cùng trang với dòng cuối của khối "Thông tin trích xuất".
- AC-GEN-17.2: Chức danh, số ô ký, dòng địa danh/ngày đúng theo cấu hình.
- Quy tắc: BR-IN-09. Kiểm thử: TC-GEN-21, TC-GEN-30. Cần xác nhận: `XN-14`.

#### REQ-GEN-18 — Sổ không có dữ liệu (M)
Kỳ không có lượt nào vẫn lập được sổ với đầu sổ, dòng "Không có lượt nào trong kỳ theo điều kiện đã chọn", khối tổng hợp toàn số 0 và khối ký.
- Kiểm thử: TC-GEN-22.

#### REQ-GEN-19 — Bảo vệ dữ liệu cá nhân (M)
Số giấy tờ của khách hiển thị đã che (giữ 4 ký tự cuối) với vai trò không được xem đầy đủ; số điện thoại khách chỉ hiển thị nếu đơn vị đồng ý (`XN-08`). Mức hiển thị áp dụng như nhau cho màn hình và mọi định dạng xuất.
- AC-GEN-19.1: Trực ban xuất SO-02: số CCCD dạng `********0111` ở cả Excel, Word, PDF.
- AC-GEN-19.2: Xuất với dữ liệu đầy đủ được ghi trong nhật ký trích xuất.
- Quy tắc: BR-BM-01…BR-BM-03. Kiểm thử: TC-GEN-23, TC-SO2-06.

#### REQ-GEN-20 — Phân quyền xem/xuất (M)
Quyền xem, xuất, xem bản ghi huỷ, xem dữ liệu cá nhân đầy đủ được gán theo vai trò và (nếu cần) theo cổng.
- AC-GEN-20.1: Người không có quyền xuất không thấy nút xuất và bị từ chối nếu gọi trực tiếp địa chỉ xuất.
- Kiểm thử: TC-GEN-24. Cần xác nhận: `XN-02`.

#### REQ-GEN-21 — Cấu hình sổ (M)
Quản trị cấu hình: cơ quan chủ quản, tên đơn vị, địa danh, danh mục cổng, giờ giao ca, chức danh ký, ngưỡng ghi bổ sung, ngưỡng quá hạn mặc định, giới hạn kỳ/số dòng. Thay đổi cấu hình không làm thay đổi bản đã xuất.
- Kiểm thử: TC-GEN-30.

#### REQ-GEN-22 — Chồng lượt và dữ liệu thời gian bất thường (S)
Nếu dữ liệu có hai lượt mở đồng thời của cùng đối tượng, hoặc sự kiện đóng sớm hơn sự kiện mở, sổ vẫn hiển thị và đánh dấu "Chồng lượt" hoặc "Lỗi thời gian"; không tính thời lượng cho dòng lỗi thời gian.
- Quy tắc: BR-LT-04, BR-LT-06. Kiểm thử: TC-GEN-28.

### 6.2. Sổ CBCS ra/vào — SO-01 (REQ-SO1)

#### REQ-SO1-01 — Nội dung sổ (M)
Liệt kê mọi lượt ra/vào của CBCS trong kỳ theo cột ở `report_definitions.md` §3.4.
- AC-SO1-01.1: Với DS-01 kỳ 25/10: 7 dòng theo thứ tự C3, C8, C1, C6, C2, C5, C4.
- Kiểm thử: TC-SO1-01. Cần xác nhận: `XN-05`, `XN-06`, `XN-07`.

#### REQ-SO1-02 — Chỉ tiêu riêng (M)
Ngoài chỉ tiêu chung, khối tổng hợp có: số CBCS duy nhất; số lượt theo chiều lượt; số lượt quá hạn.
- AC-SO1-02.1: DS-01 kỳ 25/10: CBCS duy nhất = 6; Ra–Vào = 6, Vào–Ra = 1; quá hạn = 1.
- Kiểm thử: TC-SO1-02.

#### REQ-SO1-03 — Lượt chiều Vào–Ra (M)
Lượt "Vào–Ra" của CBCS hiển thị đúng ở cột Ra/Vào theo sự kiện thực tế; cột "Chiều lượt" ghi "Vào–Ra"; trạng thái chưa đóng là "Chưa ra".
- Kiểm thử: TC-SO1-03.

#### REQ-SO1-04 — Phương tiện đi kèm (S)
Nếu lượt CBCS có liên kết phương tiện, cột "Phương tiện đi kèm" ghi biển số. Lượt phương tiện vẫn được ghi riêng ở SO-03 và không cộng vào chỉ tiêu SO-01.
- Quy tắc: BR-LT-05. Kiểm thử: TC-SO1-04.

#### REQ-SO1-05 — Bộ lọc riêng (M)
Lọc theo đơn vị/bộ phận, CBCS, chiều lượt, lý do, trạng thái, có đính chính.
- Kiểm thử: TC-SO1-05.

### 6.3. Sổ khách ra/vào — SO-02 (REQ-SO2)

#### REQ-SO2-01 — Nội dung sổ (M)
Mỗi khách là một dòng (kể cả khách đi theo đoàn), theo cột ở `report_definitions.md` §4.4.
- AC-SO2-01.1: Với DS-01 kỳ 25/10: 6 dòng theo thứ tự K1, K3, K4, K2, K5, K6.
- Kiểm thử: TC-SO2-01.

#### REQ-SO2-02 — Chỉ tiêu riêng (M)
Khối tổng hợp có: số khách có định danh duy nhất; số lượt khách không định danh (ghi riêng, **không cộng** vào số khách duy nhất); số đoàn; số thẻ khách chưa thu hồi tại thời điểm chốt; số lượt quá hạn.
- AC-SO2-02.1: DS-01 kỳ 25/10: 4; 1; 1; 2; 1.
- Quy tắc: BR-DN-02. Kiểm thử: TC-SO2-02, TC-SO2-03, TC-SO2-05. Cần xác nhận: `XN-21`.

#### REQ-SO2-03 — Khách theo đoàn (M)
Khách thuộc đoàn ghi mã đoàn ở dòng thứ hai của ô "Khách"; có bộ lọc theo đoàn.
- Kiểm thử: TC-SO2-04.

#### REQ-SO2-04 — Bộ lọc riêng (M)
Lọc theo mục đích, người/bộ phận tiếp, đoàn, khách (theo số giấy tờ), số thẻ, trạng thái, quá hạn.
- Kiểm thử: TC-SO2-04.

### 6.4. Sổ phương tiện ra/vào — SO-03 (REQ-SO3)

#### REQ-SO3-01 — Nội dung sổ (M)
Liệt kê mọi lượt phương tiện theo cột ở `report_definitions.md` §5.4. Biển số in như đã ghi nhận; đối chiếu trùng theo biển số chuẩn hoá.
- AC-SO3-01.1: Với DS-01 kỳ 25/10: 5 dòng theo thứ tự P1, P3, P5, P2, P4.
- Kiểm thử: TC-SO3-01, TC-SO3-03.

#### REQ-SO3-02 — Chỉ tiêu riêng (M)
Khối tổng hợp có: số phương tiện có biển số duy nhất; số lượt phương tiện không biển (ghi riêng); số lượt theo loại phương tiện; số lượt theo nguồn.
- AC-SO3-02.1: DS-01 kỳ 25/10: 3 phương tiện có biển duy nhất (30A-123.45 và 30A12345 là một); 1 lượt không biển.
- Quy tắc: BR-DN-03. Kiểm thử: TC-SO3-01, TC-SO3-02.

#### REQ-SO3-03 — Người điều khiển (M)
Nếu người điều khiển là CBCS hoặc khách đã có trong hệ thống, in họ tên kèm mã; nếu không, in họ tên đã ghi nhận.
- Kiểm thử: TC-SO3-05.

#### REQ-SO3-04 — Bộ lọc riêng (M)
Lọc theo biển số, loại phương tiện, nguồn, người điều khiển, chiều lượt, trạng thái.
- Kiểm thử: TC-SO3-04.

### 6.5. Sổ tổng hợp ra/vào — SO-04 (REQ-SO4)

#### REQ-SO4-01 — Bảng chỉ tiêu theo nhóm đối tượng (M)
Bảng có một dòng cho mỗi nhóm (CBCS, Khách, Phương tiện) và các cột chỉ tiêu theo `report_definitions.md` §6.4 Phần A. **Không có dòng "Tổng cộng" cộng ba nhóm**; không có chỉ tiêu nào cộng số CBCS, khách và phương tiện.
- AC-SO4-01.1: Số liệu từng dòng bằng đúng khối tổng hợp của SO-01, SO-02, SO-03 cùng kỳ, cùng điều kiện cổng, cùng thời điểm chốt.
- AC-SO4-01.2: Không có ô nào (trên màn hình, Excel, Word, PDF) chứa tổng cộng giữa các nhóm.
- Quy tắc: BR-TONG-04, BR-TONG-06, BR-DN-05. Kiểm thử: TC-SO4-01, TC-SO4-02. Cần xác nhận: `XN-20`.

#### REQ-SO4-02 — Phân biệt số lượt và số đối tượng duy nhất (M)
Mọi chỉ tiêu ghi rõ đơn vị tính "lượt" hoặc "đối tượng". Cột số lượt và cột số đối tượng duy nhất đặt riêng, có tiêu đề khác nhau.
- AC-SO4-02.1: Không có tiêu đề cột nào chỉ ghi "Số lượng" mà không có đơn vị tính.
- Kiểm thử: TC-SO4-01.

#### REQ-SO4-03 — Phân bổ theo ngày (M)
Phần B phân bổ theo ngày lịch (hoặc theo ca, `XN-25`): số lượt phát sinh theo ngày của thời điểm mở; số đối tượng có hoạt động trong ngày. Dòng cuối: cột lượt là tổng các ngày; cột đối tượng là **số đối tượng duy nhất cả kỳ**, ghi rõ "không phải tổng các ngày".
- AC-SO4-03.1: DS-01 kỳ 24/10–25/10: CBCS lượt 2 + 6 = 8; CBCS hoạt động 2 và 6, dòng cuối ghi 6 (không phải 8).
- Quy tắc: BR-ND-06, BR-TONG-07. Kiểm thử: TC-SO4-03.

#### REQ-SO4-04 — Phân bổ theo cổng (S)
Phần C đếm **số sự kiện** Vào và Ra theo cổng cho từng nhóm (không đếm lượt, vì một lượt có thể qua hai cổng).
- AC-SO4-04.1: DS-01 kỳ 25/10 khớp bảng kỳ vọng trong TC-SO4-05.
- Quy tắc: BR-TONG-08. Kiểm thử: TC-SO4-05.

#### REQ-SO4-05 — Danh sách lượt chưa hoàn tất tại thời điểm chốt (M)
Phần D liệt kê mọi lượt chưa hoàn tất tại thời điểm chốt, nhóm theo CBCS / Khách / Phương tiện, có số lượng theo từng nhóm (không cộng chung).
- AC-SO4-05.1: DS-01 kỳ 25/10: CBCS C5, C4; Khách K5, K6; Phương tiện P4.
- Kiểm thử: TC-SO4-04.

#### REQ-SO4-06 — Tóm tắt đính chính và huỷ (S)
Phần E nêu số lượt có đính chính và số bản ghi đã huỷ theo nhóm, kèm tham chiếu mã sổ riêng để xem chi tiết.
- Kiểm thử: TC-SO4-06.

#### REQ-SO4-07 — Nhật ký hợp nhất (C)
Tuỳ chọn Phần F: danh sách mọi sự kiện của cả ba nhóm theo trình tự thời gian. Chỉ triển khai nếu đơn vị xác nhận cần (`XN-19`).
- Kiểm thử: TC-SO4-08.

#### REQ-SO4-08 — Khổ giấy dọc (M)
SO-04 in khổ A4 dọc; Phần D và F (nếu có) được phép chuyển sang trang ngang nếu đơn vị chọn.
- Kiểm thử: TC-SO4-07.

---

## 7. Yêu cầu xuất và in (REQ-EXP)

### 7.1. Ma trận định dạng (đề xuất — đối chiếu với nội dung đã thống nhất, `XN-16`)

| Sổ | Màn hình | In (qua PDF) | Excel `.xlsx` | Word `.docx` | PDF |
|---|---|---|---|---|---|
| SO-01 | Có | Có | Có | Có | Có |
| SO-02 | Có | Có | Có | Có | Có |
| SO-03 | Có | Có | Có | Có | Có |
| SO-04 | Có | Có | Có (nhiều sheet) | Có | Có |

| Định dạng | Vai trò đề xuất | Giới hạn cần thông báo cho người dùng |
|---|---|---|
| PDF | Bản in và lưu chính; bố cục cố định. | Không sửa được; giới hạn số dòng (`XN-18`). |
| Excel | Bản dữ liệu để tra cứu, lọc, đối chiếu. | Không bảo đảm bố cục trang như PDF; người nhận có thể sửa. |
| Word | Bản để đơn vị biên tập, bổ sung trước khi in. | Bố cục có thể lệch nhẹ theo phiên bản Word; người nhận có thể sửa (`XN-17`). |

#### REQ-EXP-01 — Nhất quán giữa các định dạng (M)
Cùng điều kiện và cùng thời điểm chốt, ba định dạng có cùng dòng, thứ tự, giá trị và chỉ tiêu tổng như màn hình.
- AC-EXP-01.1: Đối chiếu tự động số dòng, mã bản ghi theo thứ tự và mọi chỉ tiêu giữa ba file.
- Quy tắc: BR-XF-01. Kiểm thử: TC-EXP-01, TC-EXP-09.

#### REQ-EXP-02 — Excel (M)
Sheet sổ có khối đầu sổ, bảng với dòng tiêu đề cố định (freeze) và bộ lọc tự động, khối tổng hợp; sheet "Dinh_chinh"; sheet "Thong_tin_trich_xuat". Thời điểm lưu kiểu ngày giờ thực; thời lượng lưu kiểu thời lượng định dạng `[h]:mm`. Giá trị tĩnh (không dùng công thức). Thiết lập sẵn khổ giấy, hướng giấy và dòng tiêu đề lặp khi in.
- Quy tắc: BR-XF-02. Kiểm thử: TC-EXP-02, TC-EXP-08.

#### REQ-EXP-03 — Word (M)
Khổ và hướng giấy đúng; dòng tiêu đề bảng lặp lại mỗi trang; dòng bảng không bị cắt ngang trang; có đầu trang, chân trang, số trang, khối tổng hợp, phụ lục đính chính, khối ký.
- Quy tắc: BR-XF-03. Kiểm thử: TC-EXP-03.

#### REQ-EXP-04 — PDF (M)
Nhúng phông chữ Unicode tiếng Việt; khổ, hướng, lề đúng; tiêu đề bảng lặp; không cắt dòng; "Trang x/y" đúng tổng số trang.
- Quy tắc: BR-XF-04, BR-IN-02…BR-IN-09. Kiểm thử: TC-EXP-04, TC-EXP-07.

#### REQ-EXP-05 — Tên file (M)
Tên file không dấu, không khoảng trắng: `<MaSo>_<TenNgan>_<Tu>-<Den>_<MaTrichXuat>.<ext>`, ví dụ `SO01_CBCS_20261025-20261025_SO01-20261027-0003.pdf`.
- Quy tắc: BR-XF-05. Kiểm thử: TC-EXP-05.

#### REQ-EXP-06 — Giới hạn dung lượng (M)
Khi số dòng vượt giới hạn PDF/Word (`XN-18`), hệ thống thông báo và đề nghị thu hẹp kỳ hoặc xuất Excel; không tạo file bị cắt cụt.
- Kiểm thử: TC-EXP-06.

#### REQ-EXP-07 — Hoạt động không cần Internet (M)
Xuất và in hoạt động bình thường khi máy chủ và máy trạm không có kết nối Internet.
- Kiểm thử: TC-EXP-10.

#### REQ-EXP-08 — Màn hình "Xuất sổ theo dõi" (M)
Một màn hình (`/so/xuat/`) cho chọn loại sổ, khoảng thời gian (một ngày, từ ngày đến ngày gồm cả ngày cuối, theo tháng — giờ Việt Nam), bộ lọc của sổ, định dạng có thể dùng trên máy chủ; xem trước số dòng và các dòng đầu; thông báo thành công/thất bại; liên kết tải tệp.
- AC-EXP-08.1: Ngày bắt đầu sau ngày kết thúc bị từ chối với thông báo "Ngày bắt đầu không được sau ngày kết thúc."; không ghi lịch sử.
- AC-EXP-08.2: Xem trước ghi rõ "chưa phải dữ liệu đã chốt", không cấp mã, không ghi lịch sử; số dòng xem trước bằng số dòng tệp khi dữ liệu không đổi; nếu dữ liệu đổi trước khi xuất, màn hình báo chênh lệch.
- AC-EXP-08.3: Người không đủ quyền không có lịch sử xuất, mã trích xuất hay tệp nào được tạo.
- Kiểm thử: `baocao/tests/test_man_hinh_xuat.py` (TC-MH-01…TC-MH-08, `test_plan.md` §6.8).

#### REQ-EXP-09 — Bản chốt và tải tệp (M)
Mỗi lần xuất thành công lưu bản chốt gồm tệp đã tạo và dữ liệu cấu trúc đã dùng (mã lượt, trạng thái, thời điểm, chỉ tiêu; không gồm họ tên, số giấy tờ). Tải lại trả đúng tệp đã lưu (kiểm tra SHA-256), không truy vấn lại dữ liệu hiện hành. Lịch sử xuất ghi phiên bản mẫu, số lần tải, lần tải cuối.
- AC-EXP-09.1: Đường dẫn tải dùng mã ngẫu nhiên (UUID v4); chỉ người đã xuất và còn quyền xuất sổ đó tải được; mọi trường hợp khác trả 404 như nhau.
- AC-EXP-09.2: Lưu bản chốt và ghi "Thành công" trong cùng một giao dịch.
- Kiểm thử: TC-MH-05, TC-MH-07.

---

## 8. Yêu cầu phi chức năng (REQ-NFR)

| Mã | Yêu cầu | Tiêu chí nghiệm thu | Kiểm thử |
|---|---|---|---|
| REQ-NFR-01 (M) | Hiệu năng trong LAN (chỉ tiêu đề xuất, `XN-24`). | Với 10.000 lượt/tháng mỗi nhóm: hiển thị trang đầu sổ 1 ngày ≤ 2 giây; sổ 1 tháng ≤ 5 giây; xuất PDF sổ 1 tháng ≤ 30 giây; xuất Excel ≤ 15 giây. | TC-NFR-01 |
| REQ-NFR-02 (M) | Dễ đọc khi in. | Cỡ chữ bảng khi in ≥ 9 pt, tiêu đề sổ ≥ 13 pt; in đen trắng đọc rõ; không có ô bị cắt chữ. | TC-NFR-02 |
| REQ-NFR-03 (M) | Thời gian theo máy chủ. | Máy trạm lệch giờ 15 phút không làm thay đổi thời điểm trích xuất, thời điểm chốt hay kỳ. | TC-NFR-03 |
| REQ-NFR-04 (M) | Trình duyệt hỗ trợ (`XN-27`). | Hiển thị, in và tải file đúng trên các trình duyệt được đơn vị xác nhận. | TC-NFR-04 |
| REQ-NFR-05 (M) | Tiếng Việt Unicode. | Họ tên có dấu (chuẩn NFC) hiển thị đúng ở màn hình và ba định dạng; sắp xếp theo họ tên đúng thứ tự tiếng Việt. | TC-EXP-07 |
| REQ-NFR-06 (M) | Truy vết. | Nhật ký trích xuất và lịch sử đính chính không sửa, không xoá được qua giao diện; lưu tối thiểu theo `XN-28`. | TC-GEN-19 |

---

## 9. Nội dung cần đơn vị xác nhận (XN)

Mỗi mục có **đề xuất mặc định** đã được dùng trong tài liệu. Đơn vị xác nhận "Đồng ý" hoặc ghi nội dung thay thế. Trạng thái hiện tại của mọi mục: **Chờ xác nhận**.

| Mã | Nội dung cần xác nhận | Đề xuất mặc định trong tài liệu | Ảnh hưởng |
|---|---|---|---|
| XN-01 | Đơn vị có quy định biểu mẫu sổ bắt buộc không? Nếu có, cung cấp mẫu. | Không có; dùng mẫu nghiệp vụ nội bộ mới. | Toàn bộ `report_definitions.md` |
| XN-02 | Danh sách vai trò, quyền xem/xuất từng sổ, phạm vi theo cổng. | Như mục 4. | REQ-GEN-19, REQ-GEN-20 |
| XN-03 | Tên cơ quan chủ quản, tên đơn vị, địa danh in trên sổ. | Cấu hình được, chưa có giá trị. | Đầu sổ, khối ký |
| XN-04 | Tên chính thức bốn sổ. | Như bảng mục 1.1. | Đầu sổ, tên file |
| XN-05 | Phạm vi ghi nhận CBCS: chỉ ra ngoài trong giờ làm việc, hay cả đến/về hằng ngày? Thứ tự cột Ra trước Vào cho SO-01, SO-03 có phù hợp? | Ghi nhận cả hai chiều; cột Ra trước Vào (SO-01, SO-03), Vào trước Ra (SO-02). | SO-01, SO-03 |
| XN-06 | Thông tin CBCS được in: cấp bậc, chức vụ, số hiệu. | In cấp bậc, chức vụ ở dòng 2 ô họ tên; mã CBCS ở cột riêng. | SO-01 |
| XN-07 | Danh mục lý do ra ngoài của CBCS. | Công tác; Học tập; Việc riêng có phép; Khác (ghi rõ). | SO-01 |
| XN-08 | Thông tin khách được in; mức che số giấy tờ; có in số điện thoại? | Che, giữ 4 ký tự cuối; không in số điện thoại. | SO-02, REQ-GEN-19 |
| XN-09 | Định nghĩa "quá hạn" cho từng nhóm. | Có "giờ về/ra dự kiến" trên lượt thì quá hạn khi chưa đóng sau mốc đó; không có thì không xét. Khách không có giờ ra dự kiến: không xét. | REQ-GEN-09 |
| XN-10 | Giờ giao ca trực. | Một ca 24 giờ, giao ca 07:30. | Lựa chọn nhanh "Ca trực" |
| XN-11 | Có hiển thị thời điểm đóng xảy ra sau kỳ không? | Có, kèm "(sau kỳ)". | REQ-GEN-10 |
| XN-12 | Ngưỡng "ghi bổ sung". | 30 phút. | REQ-GEN-13 |
| XN-13 | Ai được đính chính, huỷ; có cần phê duyệt; phụ lục đính chính có bắt buộc khi in? | Trực ban đính chính trong ca, chỉ huy đính chính mọi lúc; không cần phê duyệt; phụ lục luôn in. | REQ-GEN-11 |
| XN-14 | Chức danh và số người ký; ngày ký điền sẵn hay để trống; có ký/nháy từng trang? | Hai ô: "Người lập sổ" và "Chỉ huy đơn vị"; địa danh điền sẵn, ngày để trống; không ký từng trang. | REQ-GEN-17 |
| XN-15 | Lề giấy, phông, cỡ chữ in. | Lề trái 20 mm, các lề khác 15 mm; phông serif Unicode; bảng 9,5 pt. | BR-IN-02 |
| XN-16 | Ma trận định dạng xuất đã thống nhất trước đây. | Như mục 7.1. | REQ-EXP |
| XN-17 | Bản lưu chính thức là PDF? Có cho xuất Word để sửa? | PDF là bản in/lưu; Word cho phép, chân trang ghi "Bản xuất để biên tập". | REQ-EXP-03 |
| XN-18 | Giới hạn kỳ và số dòng cho PDF/Word. | Sổ riêng: kỳ tối đa 31 ngày và 5.000 dòng cho PDF/Word; Excel tối đa 366 ngày. | REQ-GEN-02, REQ-EXP-06 |
| XN-19 | SO-04 có cần phần nhật ký hợp nhất theo thời gian? | Không (tuỳ chọn, giai đoạn sau). | REQ-SO4-07 |
| XN-20 | Có cần chỉ tiêu "tổng lượt người qua cổng" (CBCS + khách)? | Không. Không có chỉ tiêu cộng giữa các nhóm. | REQ-SO4-01 |
| XN-21 | Cách thể hiện khách không định danh, xe không biển. | Đếm riêng theo lượt, không cộng vào số đối tượng duy nhất. | BR-DN-02, BR-DN-03 |
| XN-22 | Có cần "khoá sổ" kỳ đã ký để chặn đính chính? | Không khoá; đính chính sau khi đã xuất được cảnh báo trên màn hình. | BR-DC-07 |
| XN-23 | Có in tên máy trạm/địa chỉ IP trong thông tin trích xuất? | Không in; chỉ lưu trong nhật ký. | BR-TX-05 |
| XN-24 | Khối lượng dữ liệu dự kiến và chỉ tiêu hiệu năng. | Như REQ-NFR-01. | REQ-NFR-01 |
| XN-25 | SO-04 phân bổ theo ngày lịch hay theo ca trực? | Theo ngày lịch; có tuỳ chọn theo ca. | REQ-SO4-03 |
| XN-26 | Thông tin phương tiện cần in: lệnh điều xe, hàng hoá, số người. | In "Lý do / lệnh điều xe"; hàng hoá và số người chỉ có ở Excel. | SO-03 |
| XN-27 | Trình duyệt và máy in đang dùng. | Chromium/Edge/Firefox bản hiện hành; máy in laser A4 đen trắng. | REQ-NFR-04 |
| XN-28 | Thời hạn lưu nhật ký trích xuất. | Không thấp hơn thời hạn lưu dữ liệu ra/vào. | REQ-NFR-06 |
| XN-29 | Thư viện và quy trình tạo PDF. Tài liệu trước đây chưa ghi thư viện đã thống nhất. | Tạo PDF trực tiếp bằng ReportLab từ cùng số liệu với Word/Excel, nhúng phông Liberation Serif (SIL OFL) kèm mã nguồn; không chuyển đổi từ Word. Nếu đơn vị yêu cầu PDF phải là bản chuyển từ Word: chuyển bằng LibreOffice chạy không giao diện trên máy chủ (cần cài thêm), như mô tả trong README. | REQ-EXP-04 |

---

## 10. Điều kiện để chuyển sang lập trình

1. Mọi mục `XN-01`…`XN-29` có kết quả "Đồng ý" hoặc nội dung thay thế đã cập nhật vào bốn tài liệu.
2. Đơn vị duyệt bản mẫu bố cục (`report_definitions.md` §7) cho cả bốn sổ.
3. Ca kiểm thử TC-DOC-01 (rà soát tài liệu) đạt.
4. Tài liệu được nâng lên phiên bản 1.0 và ghi người duyệt ở bảng dưới.

| Phiên bản | Ngày | Nội dung thay đổi | Người lập | Người duyệt |
|---|---|---|---|---|
| 0.1 | 26/10/2026 | Dự thảo đầu tiên | | (chờ) |
