# QL CBCS LAN

Phần mềm quản lý CBCS, khách và phương tiện ra/vào, chạy trong mạng LAN (Django, PostgreSQL).

Đặc tả nằm trong [`docs/`](docs/). Mã hiện có gồm mô hình dữ liệu ghi nhận ra/vào và chức năng **xuất bốn sổ ra
Excel, Word và PDF**: SO-01 CBCS, SO-02 Khách, SO-03 Phương tiện, SO-04 Tổng hợp.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `qlcbcs/` | Cấu hình Django (múi giờ Asia/Ho_Chi_Minh, CSDL đọc từ biến môi trường `QLCBCS_DB_*`) |
| `ravao/` | Dữ liệu ghi nhận: cổng, đơn vị, CBCS, khách, phương tiện, lượt, đính chính, phân công cổng; các quyền xem/xuất sổ |
| `baocao/ky.py` | Kỳ báo cáo nửa mở `[Từ, Đến)`, lựa chọn nhanh |
| `baocao/quyen.py` | Kiểm tra quyền và giới hạn phạm vi theo cổng — mọi truy vấn của sổ đi qua đây |
| `baocao/so_lieu.py` | Tính dòng, trạng thái, chỉ tiêu theo `docs/business_rules.md` (không phụ thuộc Excel) |
| `baocao/trinh_bay.py` | Nhãn, chú giải, cách ghi thời điểm, che dữ liệu cá nhân, khối ký theo cấu hình — dùng chung |
| `baocao/excel.py` | Ghi workbook bằng openpyxl: bố cục, định dạng, thiết lập in, ghi ô an toàn |
| `baocao/bo_cuc.py` | Bố cục bản in (Word/PDF): khối đầu sổ, bảng, phụ lục, khối ký; chọn khổ/hướng giấy theo số cột |
| `baocao/in_word.py` | Vẽ bố cục ra `.docx` bằng python-docx (tiêu đề bảng lặp, không ngắt dòng, số trang) |
| `baocao/in_pdf.py` | Vẽ bố cục ra PDF bằng ReportLab, nhúng phông `baocao/fonts/` (Liberation Serif, SIL OFL) |
| `baocao/dich_vu.py` | Điều phối một lần xuất: mã trích xuất, lịch sử xuất, đọc nhất quán |
| `baocao/tests/` | Kiểm thử; `du_lieu.py` dựng bộ dữ liệu DS-01 của `docs/test_plan.md` |

## Chạy thử

```bash
pip install -r requirements.txt
# PostgreSQL: tạo role/CSDL theo QLCBCS_DB_NAME, QLCBCS_DB_USER, QLCBCS_DB_PASSWORD (mặc định qlcbcs/qlcbcs/qlcbcs)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

- Trang chọn sổ: `/so/` (cần đăng nhập qua `/admin/`).
- Xuất trực tiếp: `GET /so/<cbcs|khach|phuong-tien|tong-hop>/<xuat-excel|xuat-word|xuat-pdf>/?tu=2026-10-25T00:00&den=2026-10-26T00:00`
  hoặc `?ky=hom_nay|hom_qua|ca_hien_tai|ca_truoc|tuan_nay|thang_nay|thang_truoc`, cùng bộ lọc của từng sổ
  (`baocao/forms.py`).
- Lịch sử xuất xem ở `/admin/baocao/lichsuxuat/` (chỉ đọc).

- Khối ký chỉ được in khi quản trị bật “Khối ký đã được đơn vị phê duyệt” trong `/admin/baocao/cauhinhso/`
  và ghi căn cứ phê duyệt.

## PDF

PDF được tạo **trực tiếp bằng ReportLab** từ cùng số liệu với Word và Excel; không chuyển đổi từ Word, nên máy chủ
không cần Microsoft Word hay LibreOffice. Đặc tả chưa ghi thư viện PDF nào đã được thống nhất (`XN-29`).

Nếu đơn vị yêu cầu PDF phải là bản chuyển từ chính tệp Word, quy trình đề xuất (chưa tích hợp vào phần mềm):

1. Cài LibreOffice trên máy chủ (không cần giao diện).
2. Xuất Word từ phần mềm, sau đó chạy
   `soffice --headless --convert-to pdf --outdir <thư-mục> <tệp>.docx`.
3. Kiểm tra số trang và tiêu đề bảng lặp lại trên bản PDF; lưu kèm mã trích xuất của tệp Word.

Không dùng chuyển đổi trực tuyến ngoài LAN vì tệp chứa dữ liệu cá nhân.

## Kiểm thử

```bash
pip install -r requirements-dev.txt
python manage.py test baocao
```

Kiểm thử dàn trang thật tệp Word (`test_word_dan_trang_that_bang_libreoffice`) chỉ chạy khi máy có LibreOffice;
nếu không có, ca này được báo *skipped*.

Kiểm thử cần PostgreSQL (role được phép `CREATEDB`) để chạy cả nhánh đọc nhất quán `REPEATABLE READ`.
