# Quy tắc nghiệp vụ — Các sổ ra/vào

| Thuộc tính | Giá trị |
|---|---|
| Mã tài liệu | QLCBCS-BR-SO |
| Phiên bản | 0.1 — **Dự thảo để thống nhất** |
| Ngày lập | 26/10/2026 |
| Áp dụng cho | SO-01 Sổ CBCS ra/vào, SO-02 Sổ khách ra/vào, SO-03 Sổ phương tiện ra/vào, SO-04 Sổ tổng hợp ra/vào |
| Liên quan | [`requirements.md`](requirements.md), [`report_definitions.md`](report_definitions.md), [`test_plan.md`](test_plan.md) |

Quy tắc ghi "(đề xuất, `XN-xx`)" là giá trị mặc định chờ đơn vị xác nhận (danh mục ở `requirements.md` §9). Ví dụ trong tài liệu dùng bộ dữ liệu mẫu DS-01 (`test_plan.md` §5).

---

## 1. Lượt ra/vào (BR-LT)

**BR-LT-01 — Định nghĩa lượt.** Một lượt gồm một **sự kiện mở** và tối đa một **sự kiện đóng** của cùng một đối tượng, cùng nhóm đối tượng. Mỗi sự kiện thuộc đúng một lượt. Sổ chi tiết (SO-01, SO-02, SO-03) in **một dòng cho một lượt**.

**BR-LT-02 — Chiều lượt.** Chiều lượt xác định bởi sự kiện mở:

| Sự kiện mở | Sự kiện đóng | Chiều lượt | Ví dụ |
|---|---|---|---|
| Ra | Vào | Ra–Vào | CBCS đi công tác rồi về; xe cơ quan đi rồi về. |
| Vào | Ra | Vào–Ra | Khách vào làm việc rồi ra; xe khách vào rồi ra; CBCS đến đơn vị rồi về (nếu đơn vị ghi nhận, `XN-05`). |

Lượt của khách luôn là Vào–Ra.

**BR-LT-03 — Cổng.** Sự kiện mở và sự kiện đóng có thể ở hai cổng khác nhau; sổ in cổng của từng sự kiện.

**BR-LT-04 — Chồng lượt.** Một đối tượng không được có hai lượt đang mở cùng lúc trong cùng nhóm. Phân hệ ghi nhận phải chặn hoặc cảnh báo. Nếu dữ liệu vẫn có chồng lượt, sổ in cả hai lượt và ghi chú "Chồng lượt" ở cả hai dòng; chỉ tiêu vẫn đếm cả hai lượt.

**BR-LT-05 — Người và phương tiện là hai lượt độc lập.** CBCS hoặc khách đi cùng phương tiện tạo một lượt ở sổ người (SO-01/SO-02) và một lượt ở SO-03. Sổ người chỉ ghi tham chiếu biển số ở cột "Phương tiện"; không cộng lượt phương tiện vào sổ người và ngược lại.

**BR-LT-06 — Thời gian bất thường.** Nếu thời điểm sự kiện đóng sớm hơn thời điểm sự kiện mở (dữ liệu lỗi), sổ vẫn in dòng, ghi chú "Lỗi thời gian", ô thời lượng để "—"; lượt được xếp loại theo trạng thái như bình thường. Phân hệ ghi nhận phải chặn trường hợp này khi nhập.

---

## 2. Kỳ và thời gian (BR-KY)

**BR-KY-01 — Nguồn thời gian.** Mọi thời điểm (sự kiện, ghi nhận, trích xuất) lấy theo đồng hồ máy chủ, lưu kèm múi giờ, hiển thị theo Asia/Ho_Chi_Minh (UTC+7). Giờ của máy trạm không được dùng cho bất kỳ tính toán nào.

**BR-KY-02 — Kỳ nửa mở.** Kỳ là khoảng `[Từ, Đến)`: gồm thời điểm "Từ", không gồm thời điểm "Đến". Ví dụ kỳ ngày 25/10/2026 là `[25/10/2026 00:00:00, 26/10/2026 00:00:00)`; sự kiện lúc 26/10/2026 00:00:00 thuộc kỳ ngày 26/10.

Cách ghi trên sổ:
- Kỳ trọn ngày: "Từ 00:00 ngày 25/10/2026 đến hết ngày 25/10/2026" (hoặc "… đến hết ngày 31/10/2026" với nhiều ngày).
- Kỳ khác: "Từ 07:30 ngày 25/10/2026 đến trước 07:30 ngày 26/10/2026".

**BR-KY-03 — Lựa chọn nhanh.**

| Lựa chọn | Từ | Đến |
|---|---|---|
| Hôm nay | 00:00 hôm nay | 00:00 ngày mai |
| Hôm qua | 00:00 hôm qua | 00:00 hôm nay |
| Ca trực hiện tại | Giờ giao ca gần nhất ≤ hiện tại (đề xuất 07:30, `XN-10`) | Giờ giao ca kế tiếp |
| Ca trực trước | Giờ giao ca trước ca hiện tại | Giờ giao ca của ca hiện tại |
| Tuần này | 00:00 thứ Hai tuần này | 00:00 thứ Hai tuần sau |
| Tháng này / Tháng trước | 00:00 ngày 1 của tháng | 00:00 ngày 1 tháng kế tiếp |

**BR-KY-04 — Thời điểm chốt số liệu.** `Chốt = min(Đến, thời điểm trích xuất)`. Mọi trạng thái, chỉ tiêu và thời lượng của lượt chưa hoàn tất được tính tại thời điểm chốt. Khi `Chốt < Đến`, sổ ghi "Số liệu tính đến hh:mm:ss ngày dd/mm/yyyy (kỳ chưa kết thúc)".

**BR-KY-05 — Lượt được đưa vào sổ chi tiết.** Lượt (không bị huỷ) được đưa vào sổ khi khoảng hoạt động của nó giao với `[Từ, Chốt)`:

```
thời điểm mở < Chốt   VÀ   (chưa có sự kiện đóng  HOẶC  thời điểm đóng ≥ Từ)
```

Như vậy sổ gồm: lượt mở trong kỳ; lượt mở trước kỳ nhưng đóng trong kỳ; lượt mở trước kỳ vẫn đang mở trong suốt kỳ.

**BR-KY-06 — Giới hạn kỳ (đề xuất, `XN-18`).** Sổ chi tiết xuất PDF/Word: kỳ tối đa 31 ngày và 5.000 dòng; Excel tối đa 366 ngày. SO-04: kỳ tối đa 366 ngày cho mọi định dạng. Vượt giới hạn: chặn xuất định dạng đó, thông báo lý do và gợi ý.

**BR-KY-07 — Áp dụng bộ lọc.** Bộ lọc áp dụng **sau** khi xác định tập lượt theo BR-KY-05. Lọc theo cổng: lượt thuộc cổng X khi sự kiện mở **hoặc** sự kiện đóng diễn ra tại cổng X. Lọc theo trạng thái dùng trạng thái tại thời điểm chốt.

---

## 3. Lượt qua nửa đêm và qua kỳ (BR-ND)

**BR-ND-01 — Không tách lượt.** Lượt qua nửa đêm (hoặc qua ranh giới kỳ, ca) luôn là một lượt, một dòng. Không tự sinh sự kiện đóng lúc 24:00 hay mở lúc 00:00.

**BR-ND-02 — Luôn ghi ngày cùng giờ.** Mỗi ô thời điểm ghi `HH:mm dd/mm`; nếu kỳ trải qua hai năm thì ghi `HH:mm dd/mm/yy`. Năm của kỳ có ở đầu sổ. Giây không in ở bảng (vẫn có trong Excel).

**BR-ND-03 — Lượt từ kỳ trước.** Lượt có thời điểm mở < Từ: ô sự kiện mở thêm dòng "(từ kỳ trước)"; lượt được đếm vào chỉ tiêu "Từ kỳ trước", **không** đếm vào "Phát sinh trong kỳ".
*Ví dụ:* C3 — CBCS B ra 23:30 24/10, vào 01:15 25/10. Trong sổ ngày 25/10: ô Ra "23:30 24/10 · Cổng 1 · (từ kỳ trước)", trạng thái "Hoàn tất".

**BR-ND-04 — Lượt hoàn tất sau kỳ (đề xuất, `XN-11`).** Lượt đang mở tại thời điểm chốt nhưng **đến lúc trích xuất** đã có sự kiện đóng (chỉ xảy ra khi Chốt = Đến): ô sự kiện đóng ghi thời điểm thực tế kèm "(sau kỳ)"; trạng thái "Hoàn tất sau kỳ"; được đếm vào "Chưa hoàn tất tại thời điểm chốt".
*Ví dụ:* C4 — CBCS C ra 22:45 25/10, vào 00:20 26/10. Sổ ngày 25/10 trích xuất ngày 27/10: ô Vào "00:20 26/10 · Cổng 1 · (sau kỳ)", trạng thái "Hoàn tất sau kỳ".

**BR-ND-05 — Thời lượng.** Thời lượng = thời điểm đóng − thời điểm mở, tính cho toàn bộ lượt (không cắt theo kỳ), định dạng `hh:mm` (có thể vượt 24, ví dụ `26:10`).
- Lượt hoàn tất hoặc hoàn tất sau kỳ: thời lượng thực tế (C4 = `01:35`).
- Lượt chưa hoàn tất: `≥ hh:mm` = Chốt − thời điểm mở (C5 ra 16:00 25/10, chốt 00:00 26/10 → `≥ 08:00`).

**BR-ND-06 — Phân bổ theo ngày (SO-04).**
- *Lượt phát sinh trong ngày:* lượt được gán cho ngày (hoặc ca) chứa thời điểm mở. Mỗi lượt thuộc đúng một ngày nên cộng được qua các ngày.
- *Đối tượng có hoạt động trong ngày:* đối tượng có ít nhất một lượt giao với ngày đó (áp dụng BR-KY-05 cho từng ngày). Một đối tượng có thể có mặt ở nhiều ngày nên **không** cộng qua các ngày (BR-TONG-07).

---

## 4. Lượt chưa hoàn tất (BR-CHT)

**BR-CHT-01 — Định nghĩa.** Lượt chưa hoàn tất tại thời điểm chốt là lượt có thời điểm mở < Chốt và không có sự kiện đóng có thời điểm < Chốt. Gồm hai trường hợp: *đang mở* (đến lúc trích xuất vẫn chưa đóng) và *hoàn tất sau kỳ* (BR-ND-04).

**BR-CHT-02 — Hiển thị.** Ô sự kiện đóng của lượt đang mở để "—"; dòng in đậm; trạng thái theo BR-TT-01 ("Chưa về" với chiều Ra–Vào, "Chưa ra" với chiều Vào–Ra).

**BR-CHT-03 — Thời lượng.** Theo BR-ND-05: `≥ hh:mm` tính đến thời điểm chốt.

**BR-CHT-04 — Quá hạn (đề xuất, `XN-09`).** Lượt đang mở tại thời điểm chốt được ghi "Quá hạn" khi lượt có mốc dự kiến (giờ về dự kiến của CBCS, giờ ra dự kiến của khách, giờ về dự kiến theo lệnh điều xe) và mốc đó < Chốt. Không có mốc dự kiến thì không xét quá hạn. Nhãn: "Chưa về – Quá hạn" / "Chưa ra – Quá hạn".

**BR-CHT-05 — Không tự đóng lượt.** Hệ thống không tự đóng lượt vào cuối ngày, cuối ca hay khi lập sổ. Lượt chỉ được đóng bằng thao tác ghi nhận của người dùng; nếu ghi muộn thì áp dụng BR-DC-08.

---

## 5. Tính tổng (BR-TONG)

**BR-TONG-01 — Chỉ tiêu lượt chuẩn (mọi sổ, mọi nhóm).**

| Chỉ tiêu | Định nghĩa | Đơn vị |
|---|---|---|
| (1) Từ kỳ trước | Lượt có thời điểm mở < Từ và không có sự kiện đóng trước thời điểm Từ (chưa đóng, hoặc đóng ≥ Từ) | lượt |
| (2) Phát sinh trong kỳ | Lượt có Từ ≤ thời điểm mở < Chốt | lượt |
| (3) Hoàn tất trong kỳ | Lượt có Từ ≤ thời điểm đóng < Chốt | lượt |
| (4) Chưa hoàn tất tại thời điểm chốt | Theo BR-CHT-01; ghi chi tiết: đang mở / hoàn tất sau kỳ | lượt |
| (4a) Trong đó quá hạn | Theo BR-CHT-04 | lượt |
| Số lượt trong sổ | (1) + (2) = số dòng có STT | lượt |

**Đẳng thức cân đối:** `(1) + (2) = (3) + (4)`. Hệ thống tự kiểm tra trước khi xuất; nếu sai thì không xuất và ghi lỗi hệ thống (đây là lỗi lập trình, không phải lỗi dữ liệu).

*Ví dụ DS-01, SO-01, kỳ 25/10:* (1) = 1 (C3); (2) = 6 (C8, C1, C6, C2, C5, C4); (3) = 5 (C3, C8, C1, C6, C2); (4) = 2 (C5 đang mở, C4 hoàn tất sau kỳ). Kiểm tra: 1 + 6 = 5 + 2.

**BR-TONG-02 — Bản ghi huỷ.** Không tính vào bất kỳ chỉ tiêu nào ở mọi sổ. Khối tổng hợp chỉ ghi riêng "Số bản ghi đã huỷ trong kỳ (không tính)".

**BR-TONG-03 — Tổng theo bộ lọc.** Chỉ tiêu tính trên tập lượt sau khi lọc. Khi có lọc, khối tổng hợp ghi "Số liệu theo điều kiện lọc đã nêu ở đầu sổ".

**BR-TONG-04 — Phép cộng bị cấm.**
- Không cộng số lượt hoặc số đối tượng của CBCS, khách và phương tiện thành một chỉ tiêu (ví dụ không có "Tổng số lượt ra/vào" hay "Tổng số đối tượng"). Lý do: một CBCS lái xe ra cổng tạo hai lượt ở hai sổ; cộng lại không đo được điều gì cụ thể. Mọi nhu cầu cộng chéo phải được đơn vị nêu rõ ý nghĩa (`XN-20`).
- Không cộng thời lượng thành "tổng thời gian".
- Không có dòng "cộng trang", "cộng chuyển trang".

**BR-TONG-05 — Chỉ tiêu riêng theo sổ.**

| Sổ | Chỉ tiêu riêng |
|---|---|
| SO-01 | Số CBCS duy nhất; số lượt theo chiều lượt; số lượt theo lý do |
| SO-02 | Số khách có định danh duy nhất; số lượt khách không định danh; số đoàn; số thẻ khách chưa thu hồi tại thời điểm chốt |
| SO-03 | Số phương tiện có biển duy nhất; số lượt phương tiện không biển; số lượt theo loại phương tiện; số lượt theo nguồn |

**BR-TONG-06 — Khớp số liệu giữa SO-04 và sổ riêng.** Dòng CBCS/Khách/Phương tiện của SO-04 Phần A phải bằng đúng khối tổng hợp của SO-01/SO-02/SO-03 khi cùng kỳ, cùng bộ lọc cổng và cùng thời điểm chốt.

**BR-TONG-07 — Dòng cuối bảng phân bổ.** Ở bảng phân bổ theo ngày/ca/cổng:
- Cột đơn vị "lượt" hoặc "sự kiện": dòng cuối ghi "Cộng" và là tổng các dòng.
- Cột đơn vị "đối tượng": dòng cuối ghi "Duy nhất cả kỳ (không phải tổng các dòng)" và là số đối tượng duy nhất của cả kỳ.

*Ví dụ DS-01, kỳ 24–25/10:* CBCS có hoạt động ngày 24/10 = 2, ngày 25/10 = 6; dòng cuối = 6 (CB001 và CB002 có mặt cả hai ngày), không phải 8.

**BR-TONG-08 — Phân bổ theo cổng đếm sự kiện.** Bảng theo cổng đếm số sự kiện Vào và số sự kiện Ra có thời điểm trong `[Từ, Chốt)` tại từng cổng, riêng cho từng nhóm. Không đếm lượt theo cổng vì một lượt có thể có hai cổng.

---

## 6. Đối tượng duy nhất (BR-DN)

**BR-DN-01 — CBCS.** Định danh theo mã CBCS nội bộ (không theo họ tên, vì có thể trùng tên).

**BR-DN-02 — Khách (đề xuất, `XN-21`).** Định danh theo cặp (loại giấy tờ, số giấy tờ đã chuẩn hoá: bỏ khoảng trắng, dấu chấm, gạch; chữ in hoa).
- Khách không có giấy tờ là *không định danh*: mỗi lượt được tính là một "lượt khách không định danh", ghi ở chỉ tiêu riêng, **không cộng** vào "Số khách có định danh duy nhất".
- Cùng một người dùng hai loại giấy tờ khác nhau ở hai lượt sẽ được tính là hai khách; đây là giới hạn đã biết.

*Ví dụ DS-01:* K1 (số `001090000111`) và K2 (số `001 090 000 111`) là một khách.

**BR-DN-03 — Phương tiện (đề xuất, `XN-21`).** Định danh theo biển số chuẩn hoá (bỏ khoảng trắng, dấu chấm, gạch; in hoa). Biển số in trên sổ giữ nguyên như đã ghi nhận. Phương tiện không có biển (dùng mã tạm) là *không định danh*, đếm theo lượt ở chỉ tiêu riêng.

*Ví dụ DS-01:* `30A-123.45` và `30A12345` → `30A12345`, là một phương tiện.

**BR-DN-04 — Phạm vi đếm.** Số đối tượng duy nhất đếm trên tập lượt của sổ (sau BR-KY-05, sau lọc, không gồm bản ghi huỷ).

**BR-DN-05 — Không cộng giữa nhóm, không cộng giữa ngày.** Số đối tượng duy nhất chỉ có nghĩa trong một nhóm và một phạm vi thời gian; không cộng CBCS + khách + phương tiện; không cộng số duy nhất của các ngày để ra số của kỳ (BR-TONG-04, BR-TONG-07).

**BR-DN-06 — Định danh sau đính chính.** Dùng giá trị định danh hiện hành tại thời điểm trích xuất.

---

## 7. Trạng thái và ký hiệu (BR-TT)

**BR-TT-01 — Bảng trạng thái (tại thời điểm chốt).**

| Mã | Điều kiện | Nhãn in trên sổ | Tính vào chỉ tiêu |
|---|---|---|---|
| HT | Đã đóng trước thời điểm chốt | Hoàn tất | (3) nếu đóng trong kỳ |
| MO | Đang mở, chiều Ra–Vào | **Chưa về** | (4) |
| MO | Đang mở, chiều Vào–Ra | **Chưa ra** | (4) |
| MO + QH | Đang mở và quá hạn | **Chưa về – Quá hạn** / **Chưa ra – Quá hạn** | (4), (4a) |
| HTS | Đóng sau thời điểm chốt | Hoàn tất sau kỳ | (4) |
| HUY | Bản ghi đã huỷ (chỉ khi bật hiện) | ĐÃ HUỶ | Không tính |

**BR-TT-02 — Ký hiệu ở cột Ghi chú.** Có thể có nhiều ký hiệu, cách nhau bằng dấu chấm phẩy, theo thứ tự:

| Ký hiệu | Ý nghĩa | Quy tắc |
|---|---|---|
| `ĐC(n)` | Dòng có đính chính; `n` là số thứ tự trong Phụ lục đính chính (nhiều đính chính: `ĐC(2,3)`) | BR-DC-04 |
| `GBS` | Có sự kiện ghi bổ sung | BR-DC-08 |
| `Chồng lượt` | Đối tượng có lượt mở chồng thời gian | BR-LT-04 |
| `Lỗi thời gian` | Thời điểm đóng < thời điểm mở | BR-LT-06 |
| Ghi chú tự do | Do người ghi nhận nhập | — |

Các chú thích "(từ kỳ trước)", "(sau kỳ)" ghi trong ô thời điểm, không ghi ở cột Ghi chú. Mọi bản in có dòng "Chú giải ký hiệu" ở khối cuối sổ.

**BR-TT-03 — Màu chỉ là bổ trợ.** Trên màn hình có thể tô màu nền nhãn (ví dụ cam cho "Chưa về", đỏ cho "Quá hạn") nhưng chữ luôn hiển thị; PDF/Word/Excel không dùng màu để truyền tải trạng thái.

**BR-TT-04 — Nhấn mạnh khi in.** Dòng chưa hoàn tất (MO, MO+QH) in đậm toàn dòng; chữ "Quá hạn" in đậm và gạch chân. Không dùng ký tự đặc biệt ngoài bảng mã tiếng Việt thông dụng (tránh lỗi phông).

---

## 8. Đính chính, huỷ, ghi bổ sung (BR-DC)

**BR-DC-01 — Không sửa đè, không xoá.** Mỗi đính chính lưu: bản ghi, trường, giá trị cũ, giá trị mới, lý do, người đính chính, thời điểm đính chính. Không có thao tác xoá vật lý qua giao diện.

**BR-DC-02 — Lý do bắt buộc.** Đính chính và huỷ đều phải nhập lý do. Quyền đính chính/huỷ theo `XN-13`.

**BR-DC-03 — Giá trị dùng trên sổ.** Sổ dùng giá trị hiện hành tại thời điểm trích xuất (kể cả để xác định lượt có thuộc kỳ hay không).

**BR-DC-04 — Phụ lục đính chính.** Cuối mỗi sổ riêng có "Phụ lục đính chính" liệt kê mọi đính chính (đã thực hiện đến thời điểm trích xuất) của các lượt có trong sổ: số thứ tự (n), STT dòng, đối tượng, trường, giá trị cũ, giá trị mới, lý do, người đính chính, thời điểm đính chính. Số (n) đánh theo STT dòng tăng dần, cùng dòng thì theo thời điểm đính chính tăng dần. Không có đính chính thì ghi "Không có đính chính". Phụ lục luôn in (đề xuất, `XN-13`).

**BR-DC-05 — Đính chính làm thay đổi kỳ.** Nếu đính chính thời gian khiến lượt không còn giao với kỳ, lượt không có trong sổ của kỳ đó (và cũng không có trong phụ lục của sổ đó); lượt xuất hiện ở sổ của kỳ mới kèm `ĐC(n)`.

**BR-DC-06 — Huỷ.** Bản ghi huỷ vẫn được lưu; mặc định không hiển thị. Khi người có quyền bật "Hiện bản ghi đã huỷ": dòng huỷ có STT "—", trạng thái "ĐÃ HUỶ", ghi chú là lý do huỷ, đặt theo thứ tự sắp xếp như dòng thường; STT các dòng khác giữ nguyên; đầu sổ ghi "Có hiển thị bản ghi đã huỷ (không tính vào số liệu)".

**BR-DC-07 — Đính chính sau khi đã xuất (đề xuất, `XN-22`).** Bản đã xuất không thay đổi. Lần xuất sau có mã trích xuất mới và phản ánh đính chính. Khi xem một kỳ đã có bản xuất, nếu có đính chính hoặc ghi bổ sung sau lần xuất gần nhất, màn hình cảnh báo "Dữ liệu kỳ này đã thay đổi sau lần trích xuất <mã> lúc <thời điểm>". Không khoá sổ.

**BR-DC-08 — Ghi bổ sung (đề xuất, `XN-12`).** Sự kiện có (thời điểm ghi nhận − thời điểm sự kiện) > 30 phút được đánh dấu `GBS`. Thời điểm dùng để tính toán luôn là thời điểm sự kiện.

---

## 9. Trích xuất và người lập sổ (BR-TX)

**BR-TX-01 — Thời điểm trích xuất và đọc nhất quán.** Thời điểm trích xuất là giờ máy chủ khi bắt đầu đọc dữ liệu. Toàn bộ nội dung một lần xuất (bảng, tổng hợp, phụ lục) được đọc trong cùng một phiên đọc nhất quán của PostgreSQL; dữ liệu ghi nhận trong lúc đang xuất không xuất hiện một phần.

**BR-TX-02 — Mã trích xuất.** Dạng `<MãSổ>-<yyyymmdd>-<nnnn>`, `nnnn` tăng dần theo ngày trên toàn hệ thống, ví dụ `SO01-20261027-0003`. Mỗi lần in/xuất (mỗi định dạng) một mã. Không tái sử dụng mã.

**BR-TX-03 — Người trích xuất.** Họ tên và tên đăng nhập của tài khoản thực hiện; hệ thống tự ghi, không sửa được. Cách in: "Nguyễn Văn X (tài khoản: trucban01)".

**BR-TX-04 — Người lập sổ.** Hộp thoại xuất có trường "Người lập sổ": mặc định là người trích xuất; có thể chọn người khác từ danh sách người dùng/CBCS, hoặc chọn "Để trống — ký tay". Tên in dưới dòng "(Ký, ghi rõ họ tên)"; để trống thì in dòng chấm.

**BR-TX-05 — Nhật ký trích xuất.** Mỗi lần in/xuất lưu: mã trích xuất, mã sổ, định dạng, thời điểm trích xuất, thời điểm chốt, kỳ (Từ, Đến), toàn bộ điều kiện lọc và tuỳ chọn (hiện bản ghi huỷ, mức hiển thị dữ liệu cá nhân), người trích xuất, người lập sổ, số dòng, các chỉ tiêu tổng, tên file, mã băm (SHA-256) của file, tên máy trạm/địa chỉ IP (chỉ lưu nhật ký, không in, `XN-23`).

**BR-TX-06 — Xem trên màn hình.** Xem không sinh mã trích xuất, không ghi nhật ký trích xuất; đầu sổ trên màn hình ghi "Xem lúc hh:mm:ss dd/mm/yyyy — chưa phải bản trích xuất". Nút "In" tạo bản PDF và sinh mã như một lần xuất.

---

## 10. Bố cục in (BR-IN)

**BR-IN-01 — Mã sổ và phiên bản mẫu.** SO-01…SO-04, phiên bản mẫu `1.0` sau khi được duyệt. Đổi bố cục thì tăng phiên bản mẫu.

**BR-IN-02 — Khổ, hướng, lề, phông (đề xuất, `XN-15`).**

| Sổ | Khổ | Hướng | Lề (trên/dưới/trái/phải) | Phông, cỡ chữ |
|---|---|---|---|---|
| SO-01, SO-02, SO-03 | A4 | Ngang | 15 / 15 / 20 / 15 mm | Phông serif Unicode nhúng; tiêu đề sổ 14 pt đậm; bảng 9,5 pt; chân trang 8 pt |
| SO-04 | A4 | Dọc (Phần D, F được phép ngang) | 15 / 15 / 20 / 15 mm | Như trên; bảng 10 pt |

**BR-IN-03 — Khối đầu sổ (trang 1).** Theo `report_definitions.md` §2.3.

**BR-IN-04 — Lặp lại trên mỗi trang.** Từ trang 2: đầu trang rút gọn một dòng và **dòng tiêu đề bảng** được lặp lại. Tiêu đề hai tầng (nếu có) lặp đủ hai tầng.

**BR-IN-05 — Chân trang mọi trang.** "Mã sổ · Mã trích xuất · Trích xuất lúc hh:mm:ss dd/mm/yyyy · Mẫu nghiệp vụ nội bộ · Trang x/y".

**BR-IN-06 — Ghi chú tính chất mẫu.** Chân trang có cụm "Mẫu nghiệp vụ nội bộ"; bản Word thêm "Bản xuất để biên tập" (`XN-17`).

**BR-IN-07 — STT và sắp xếp ổn định.** STT liên tục 1…N trên toàn sổ. Mọi kiểu sắp xếp đều có khoá phụ cuối cùng là mã bản ghi tăng dần để thứ tự không đổi giữa các lần xuất.

**BR-IN-08 — Thống nhất màn hình và bản in.** Màn hình dùng cùng định nghĩa cột, cùng truy vấn, cùng hàm tính chỉ tiêu với bản xuất.

**BR-IN-09 — Ngắt trang.**
- Không cắt một dòng bảng sang hai trang.
- Thứ tự khối cuối sổ: Tổng hợp số liệu → Chú giải ký hiệu → Phụ lục đính chính → Thông tin trích xuất → Khối ký.
- Khối ký không đứng một mình trên một trang: nếu không đủ chỗ, chuyển cả khối "Thông tin trích xuất" sang trang mới cùng khối ký.
- Sau khối ký ghi "— Hết sổ —".

---

## 11. Xuất file (BR-XF)

**BR-XF-01 — Một nguồn dữ liệu.** Màn hình, Excel, Word, PDF dùng chung một tập kết quả đã tính (dòng, trạng thái, chỉ tiêu). Định dạng chỉ khác ở cách trình bày.

**BR-XF-02 — Excel.**
- Sheet 1 (tên theo mã sổ, ví dụ `SO01`): khối đầu sổ ở các dòng đầu; dòng tiêu đề bảng được cố định (freeze) và có bộ lọc tự động; khối tổng hợp dưới bảng.
- Thời điểm: kiểu ngày giờ, định dạng `dd/mm/yyyy hh:mm:ss`. Thời lượng: kiểu thời lượng `[h]:mm`; lượt chưa hoàn tất có thêm cột "Thời lượng tính đến chốt" và cột "Là thời lượng tối thiểu" = Có.
- Ô có nhiều dòng trên PDF được tách thành cột riêng trong Excel (ví dụ "Ra – thời điểm", "Ra – cổng", "Ra – chú thích kỳ").
- Giá trị tĩnh, không dùng công thức.
- Sheet `Dinh_chinh` (phụ lục đính chính), sheet `Thong_tin_trich_xuat` (kỳ, chốt, lọc, người trích xuất, người lập sổ, mã trích xuất, chú giải ký hiệu).
- Thiết lập in sẵn: khổ A4, hướng như BR-IN-02, lặp dòng tiêu đề, vừa chiều ngang một trang.
- SO-04: mỗi Phần một sheet (`A_Chi_tieu`, `B_Theo_ngay`, `C_Theo_cong`, `D_Chua_hoan_tat`, `E_Dinh_chinh_huy`).

**BR-XF-03 — Word.** Khổ, hướng, lề như BR-IN-02; bảng có thuộc tính "lặp dòng tiêu đề" và "không cho dòng ngắt qua trang"; đầu trang, chân trang dùng trường số trang của Word.

**BR-XF-04 — PDF.** Nhúng phông; khổ, hướng, lề như BR-IN-02; "Trang x/y" là số thực tế; thuộc tính tài liệu (Title, Author = người trích xuất, Subject = mã trích xuất).

**BR-XF-05 — Tên file.** `<MaSo>_<TenNgan>_<yyyymmdd Từ>-<yyyymmdd ngày cuối của kỳ>_<MaTrichXuat>.<ext>`; `TenNgan` ∈ {`CBCS`, `Khach`, `PhuongTien`, `TongHop`}; không dấu, không khoảng trắng.

---

## 12. Dữ liệu cá nhân (BR-BM)

**BR-BM-01 — Che số giấy tờ (đề xuất, `XN-08`).** Vai trò không có quyền "xem dữ liệu cá nhân đầy đủ" thấy số giấy tờ dạng `*` thay cho mọi ký tự trừ 4 ký tự cuối (ví dụ `********0111`). Áp dụng cho màn hình và mọi định dạng xuất, kể cả Excel (giá trị trong file đã là chuỗi đã che, không phải định dạng hiển thị).

**BR-BM-02 — Xuất dữ liệu đầy đủ.** Người có quyền có thể chọn "Xuất dữ liệu cá nhân đầy đủ"; lựa chọn này được ghi trong nhật ký và in ở khối "Thông tin trích xuất".

**BR-BM-03 — Số điện thoại khách.** Không hiển thị trên sổ trừ khi đơn vị xác nhận (`XN-08`).
