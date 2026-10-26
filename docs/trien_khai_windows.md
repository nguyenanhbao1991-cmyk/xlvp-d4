# Hướng dẫn triển khai QL CBCS LAN trên máy chủ Windows

| Thuộc tính | Giá trị |
|---|---|
| Áp dụng cho | Mã nguồn nhánh `feat/man-hinh-xuat-so` trở về sau |
| Mô hình | Một máy chủ Windows trong LAN chạy cả PostgreSQL và ứng dụng; người dùng truy cập bằng trình duyệt |
| Trạng thái | Phần Python đã kiểm thử tự động (trên Linux). **Các script PowerShell chưa được chạy thử trên Windows thật** — chạy thử trên máy thử nghiệm trước khi dùng cho máy chủ thật |

## 1. Thành phần

```
Trình duyệt (máy trạm LAN) ──HTTP :8000──▶ Waitress (chay_may_chu.py, tài khoản LOCAL SERVICE)
                                              │  Django + WhiteNoise (tệp tĩnh)
                                              ▼
                                         PostgreSQL :5432 (chỉ nghe localhost)
```

- **Waitress**: máy chủ WSGI viết bằng Python thuần, chạy tốt trên Windows (Gunicorn không chạy trên Windows).
- **WhiteNoise**: phục vụ CSS/JS của trang quản trị, không cần IIS.
- **Task Scheduler** của Windows: chạy máy chủ khi khởi động máy, tự khởi động lại khi lỗi, chạy sao lưu hằng ngày. Không cần cài công cụ dịch vụ bên ngoài.
- Không phụ thuộc Internet khi chạy. Phông chữ PDF đi kèm mã nguồn.

## 2. Chuẩn bị

| Hạng mục | Yêu cầu |
|---|---|
| Hệ điều hành | Windows Server 2016 trở lên, hoặc Windows 10/11 (64-bit) |
| Python | 3.12 bản 64-bit (đã kiểm thử 3.13; hỗ trợ 3.10–3.13). **Cài với tuỳ chọn "Install for all users"** (vào `C:\Program Files\Python312`) — tài khoản LOCAL SERVICE không đọc được Python cài trong hồ sơ người dùng |
| PostgreSQL | 16 (bộ cài EDB cho Windows) |
| Quyền | Quản trị máy chủ |
| Đồng hồ | Đồng bộ với máy chủ thời gian của đơn vị (BR-KY-01): `w32tm /query /status` |

Máy chủ không có Internet: trên một máy Windows **có** Internet, cùng phiên bản Python, chạy

```powershell
powershell -ExecutionPolicy Bypass -File trien_khai\windows\tai_goi_ngoai_tuyen.ps1
```

rồi chép cả thư mục mã nguồn (gồm thư mục `goi` vừa tạo) và hai bộ cài Python, PostgreSQL sang máy chủ.

## 3. Cài PostgreSQL và tạo CSDL

1. Chạy bộ cài PostgreSQL, ghi nhớ mật khẩu tài khoản `postgres`.
2. Mở "SQL Shell (psql)" bằng tài khoản `postgres`, chạy (thay mật khẩu):

   ```sql
   CREATE ROLE qlcbcs LOGIN PASSWORD 'mat-khau-manh';
   CREATE DATABASE qlcbcs OWNER qlcbcs ENCODING 'UTF8' TEMPLATE template0;
   ```

3. Ứng dụng chạy trên cùng máy: trong `postgresql.conf` đặt `listen_addresses = 'localhost'`, khởi động lại dịch vụ PostgreSQL, và xoá luật tường lửa mở cổng 5432 nếu bộ cài đã tạo.

## 4. Cài ứng dụng

1. Chép mã nguồn vào thư mục **không** nằm trong hồ sơ người dùng, ví dụ `C:\QLCBCS`.
2. Mở PowerShell bằng "Run as administrator":

   ```powershell
   cd C:\QLCBCS
   powershell -ExecutionPolicy Bypass -File trien_khai\windows\cai_dat.ps1 -ThuMucGoi .\goi
   ```

   (Máy có Internet thì bỏ `-ThuMucGoi .\goi`.) Script:
   - tạo `.venv` và cài thư viện;
   - tạo `qlcbcs.env` với khoá bí mật ngẫu nhiên, hỏi mật khẩu CSDL, điền tên máy và IP vào `QLCBCS_ALLOWED_HOSTS`;
   - chỉ cho Administrators, SYSTEM và LOCAL SERVICE đọc `qlcbcs.env`;
   - chạy `migrate`, `collectstatic`, `check --deploy`;
   - cấp quyền đọc thư mục cài đặt và quyền ghi thư mục `nhat_ky` cho LOCAL SERVICE.

   Có thể chạy lại script bất cứ lúc nào: không ghi đè `qlcbcs.env`, không xoá dữ liệu.

3. Tạo tài khoản quản trị:

   ```powershell
   .venv\Scripts\python.exe manage.py createsuperuser
   ```

## 5. Chạy nền và mở tường lửa

```powershell
powershell -ExecutionPolicy Bypass -File trien_khai\windows\dang_ky_dich_vu.ps1
```

- Tạo tác vụ `QLCBCS-MayChu` chạy `chay_may_chu.py` khi máy khởi động, bằng LOCAL SERVICE, tự chạy lại sau 1 phút nếu dừng do lỗi.
- Mở cổng TCP 8000 chỉ cho **mạng con cục bộ** (hồ sơ Domain/Private).
- Chờ máy chủ phản hồi và in địa chỉ truy cập, ví dụ `http://MAY-CHU-QLCBCS:8000/so/xuat/`.

Đổi cổng: sửa `QLCBCS_CONG` trong `qlcbcs.env`, chạy lại script này.

## 6. Thiết lập ban đầu (trang quản trị)

Đăng nhập `http://<máy-chủ>:8000/admin/`:

1. **Cấu hình sổ**: cơ quan chủ quản, tên đơn vị, địa danh. Khối ký chỉ in khi bật "đã được đơn vị phê duyệt" và ghi căn cứ phê duyệt.
2. **Danh mục**: cổng, đơn vị/bộ phận, CBCS.
3. **Người dùng và nhóm**: nên tạo nhóm theo vai trò (Trực ban, Chỉ huy, Lãnh đạo…) rồi cấp quyền cho nhóm. Các quyền nằm ở mục "Ghi nhận ra/vào": xem/xuất từng sổ, xem bản ghi đã huỷ, xem dữ liệu cá nhân đầy đủ, xem mọi cổng. Người không có "xem mọi cổng" phải được phân công cổng (mục "Phân công cổng"), nếu không sẽ không thấy dữ liệu.

## 7. Sao lưu và khôi phục

Đăng ký sao lưu tự động 02:15 hằng ngày, giữ 30 ngày, **nên đặt trên ổ đĩa khác**:

```powershell
powershell -ExecutionPolicy Bypass -File trien_khai\windows\sao_luu.ps1 -ThuMucSaoLuu D:\SaoLuu\QLCBCS -DangKyHangNgay
```

Sao lưu ngay: bỏ `-DangKyHangNgay`. Kết quả từng lần ghi trong `sao_luu.log` cùng thư mục. CSDL chứa cả các tệp đã xuất (bản chốt), nên dung lượng sao lưu tăng theo số lần xuất.

Khôi phục (dừng máy chủ trước):

```powershell
Stop-ScheduledTask -TaskName QLCBCS-MayChu
& "C:\Program Files\PostgreSQL\16\bin\pg_restore.exe" --clean --if-exists --no-owner -U qlcbcs -d qlcbcs D:\SaoLuu\QLCBCS\qlcbcs_20261027_021500.dump
Start-ScheduledTask -TaskName QLCBCS-MayChu
```

Nên thử khôi phục định kỳ trên một máy thử nghiệm.

## 8. Cập nhật phiên bản

1. Chép mã nguồn mới đè lên `C:\QLCBCS` (giữ `qlcbcs.env`, `.venv`, `nhat_ky`). Máy không có Internet: tạo lại thư mục `goi` bằng `tai_goi_ngoai_tuyen.ps1`.
2. Chạy:

   ```powershell
   powershell -ExecutionPolicy Bypass -File trien_khai\windows\cap_nhat.ps1 -ThuMucGoi .\goi -ThuMucSaoLuu D:\SaoLuu\QLCBCS
   ```

   Script sao lưu CSDL trước; nếu sao lưu lỗi thì không cập nhật. Sau đó dừng máy chủ, cài thư viện, `migrate`, `collectstatic`, rồi chạy lại máy chủ (kể cả khi một bước lỗi).

## 9. Xử lý sự cố

| Hiện tượng | Kiểm tra |
|---|---|
| Không vào được trang | Task Scheduler › `QLCBCS-MayChu` › History; tệp `nhat_ky\khoi_dong.log` (lỗi lúc khởi động, ví dụ sai mật khẩu CSDL, thiếu khoá bí mật) |
| Lỗi 400 "Bad Request" | Tên/IP người dùng gõ chưa có trong `QLCBCS_ALLOWED_HOSTS` của `qlcbcs.env`; sửa rồi chạy lại tác vụ |
| Lỗi 500 khi dùng | `nhat_ky\qlcbcs.log` |
| Máy trạm không kết nối được | Luật tường lửa "QL CBCS LAN (TCP 8000)"; hồ sơ mạng của máy chủ phải là Domain hoặc Private, không phải Public |
| Trang quản trị không có giao diện | Chạy lại `cai_dat.ps1` (bước `collectstatic`) |
| Giờ trên sổ lệch | Đồng hồ máy chủ (`w32tm /resync`); ứng dụng luôn dùng giờ máy chủ, múi giờ Asia/Ho_Chi_Minh |

Gỡ tác vụ và luật tường lửa (không xoá dữ liệu): `trien_khai\windows\go_dich_vu.ps1`.

## 10. Rủi ro còn lại, cần đơn vị quyết định

- **Chưa có HTTPS.** Mật khẩu đăng nhập và dữ liệu đi trong LAN dưới dạng không mã hoá. `check --deploy` báo 4 cảnh báo về HTTPS vì lý do này. Phương án nếu cần: đặt IIS (URL Rewrite + ARR) hoặc một reverse proxy khác có chứng chỉ của đơn vị phía trước Waitress, rồi bật `QLCBCS_HTTPS=1`, `QLCBCS_SAU_PROXY=1`, `QLCBCS_CSRF_TRUSTED_ORIGINS` trong `qlcbcs.env`.
- **Đăng nhập** dùng trang đăng nhập của trang quản trị Django; chưa có màn hình đăng nhập riêng, chưa tích hợp tài khoản miền (Active Directory).
- **Một máy chủ**: chưa có phương án dự phòng nóng; khôi phục từ bản sao lưu.
- **Bản chốt tích luỹ trong CSDL**, chưa có quy tắc dọn theo thời hạn lưu (`XN-28`).
