# Hướng dẫn triển khai QL CBCS LAN trên máy chủ Windows

| Thuộc tính | Giá trị |
|---|---|
| Áp dụng cho | Mã nguồn nhánh `feat/man-hinh-xuat-so` trở về sau |
| Mô hình | Một máy chủ Windows trong LAN chạy cả PostgreSQL và ứng dụng; người dùng truy cập bằng trình duyệt |
| Trạng thái | Phần Python (máy chủ, đóng gói, kiểm tra gói) đã kiểm thử tự động trên Linux. **Các script PowerShell chưa được chạy thử trên Windows thật** — chạy thử toàn bộ quy trình trên một máy thử nghiệm trước khi dùng cho máy chủ thật |

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

### 2.1. Đóng gói trên máy có Internet

Máy đóng gói: Windows có Internet, đã cài Git và Python bất kỳ từ 3.10 (không cần trùng phiên bản với máy chủ —
thư viện được tải đúng cho Windows 64-bit, Python của máy chủ).

1. Tải hai bộ cài từ trang chính thức và kiểm tra chữ ký/mã của nhà phát hành:
   - Python 3.12, bản "Windows installer (64-bit)" — https://www.python.org/downloads/windows/
   - PostgreSQL 16 cho Windows x86-64 — https://www.postgresql.org/download/windows/
2. Lấy mã nguồn đúng phiên bản cần cài (`git clone`, `git checkout <nhánh hoặc thẻ>`), rồi chạy:

   ```powershell
   powershell -ExecutionPolicy Bypass -File trien_khai\windows\dong_goi.ps1 -KemTep "D:\cai\python-3.12.10-amd64.exe,D:\cai\postgresql-16.6-1-windows-x64.exe"
   ```

   Hoặc để script tự tìm hai bộ cài vừa tải trong thư mục Downloads (Python đúng phiên bản 3.12, 64-bit):
   `powershell -ExecutionPolicy Bypass -File trien_khai\windows\dong_goi.ps1 -TimBoCai`.

   Thay hai đường dẫn bằng vị trí thật của tệp bộ cài; nhiều tệp ngăn bằng dấu phẩy, **cả danh sách đặt trong một
   cặp ngoặc kép**. Chưa có bộ cài thì bỏ hẳn phần `-KemTep "..."` và chép bộ cài sang máy chủ riêng.

   (Không có PowerShell: `py -3 trien_khai\dong_goi.py --python 3.12 --kem-tep <bộ cài> ...` — chạy được cả
   trên Linux.) Script từ chối đóng gói khi còn thay đổi chưa commit, để gói luôn ứng với một commit cụ thể.

3. Kết quả trong `dist\`:

   | Tệp | Nội dung |
   |---|---|
   | `QLCBCS_<ngày>_<commit>_py312.zip` | Mã nguồn (chỉ tệp Git quản lý: không lẫn `qlcbcs.env`, `.venv`, nhật ký), thư mục `goi\` (16 thư viện dạng wheel cho Windows 64-bit, kể cả thư viện phụ thuộc), `cai_dat_he_thong\` (các bộ cài kèm theo), `PHIEN_BAN.txt`, `MANIFEST-SHA256.txt` |
   | `QLCBCS_...zip.sha256` | Mã SHA-256 của tệp ZIP |

   Trước khi tạo ZIP, script thử cài toàn bộ thư viện chỉ từ thư mục `goi\` (như máy không có mạng) và báo lỗi
   nếu thiếu thư viện nào. Gói khoảng 25 MB, cộng dung lượng bộ cài kèm theo (PostgreSQL khoảng 300–400 MB).

4. Chép **cả hai tệp** sang máy chủ (USB, ổ mạng nội bộ). Ghi mã SHA-256 vào sổ giao nhận nếu đơn vị yêu cầu.

### 2.2. Kiểm tra trên máy chủ nội bộ

```powershell
Get-FileHash E:\QLCBCS_20261030_abc1234567_py312.zip -Algorithm SHA256   # so với nội dung tệp .sha256
```

Mã khác nhau: **không cài** — tệp bị hỏng hoặc bị sửa khi chép.

## 3. Cài PostgreSQL và tạo CSDL

1. Giải nén gói (mục 4, bước 1) rồi chạy bộ cài PostgreSQL trong `C:\QLCBCS\cai_dat_he_thong\`, ghi nhớ mật khẩu tài
   khoản `postgres`. Cài Python từ cùng thư mục, chọn **"Install for all users"** và "Add python.exe to PATH".
2. Mở "SQL Shell (psql)" bằng tài khoản `postgres`, chạy (thay mật khẩu):

   ```sql
   CREATE ROLE qlcbcs LOGIN PASSWORD 'mat-khau-manh';
   CREATE DATABASE qlcbcs OWNER qlcbcs ENCODING 'UTF8' TEMPLATE template0;
   ```

3. Ứng dụng chạy trên cùng máy: trong `postgresql.conf` đặt `listen_addresses = 'localhost'`, khởi động lại dịch vụ PostgreSQL, và xoá luật tường lửa mở cổng 5432 nếu bộ cài đã tạo.

## 4. Cài ứng dụng

1. Giải nén gói vào thư mục **không** nằm trong hồ sơ người dùng và đang trống, ví dụ `C:\QLCBCS`:

   ```powershell
   Expand-Archive E:\QLCBCS_20261030_abc1234567_py312.zip -DestinationPath C:\QLCBCS
   Get-ChildItem C:\QLCBCS -Recurse -File | Unblock-File
   ```

2. (Sau khi đã cài Python, PostgreSQL và tạo CSDL ở mục 3.) Mở PowerShell bằng "Run as administrator":

   ```powershell
   cd C:\QLCBCS
   powershell -ExecutionPolicy Bypass -File trien_khai\windows\cai_dat.ps1
   ```

   Script:
   - kiểm tra gói: đủ tệp, đúng SHA-256 từng tệp, không có thư viện lạ trong `goi\`, đúng Python 3.12 64-bit —
     không đạt thì dừng, không cài;
   - tạo `.venv` và cài thư viện **chỉ từ thư mục `goi\`** (không cần Internet);
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

1. Đóng gói bản mới như mục 2.1, chép tệp ZIP và tệp `.sha256` sang máy chủ. **Không giải nén đè** lên `C:\QLCBCS`.
2. Chạy script cập nhật **của bản đang cài**:

   ```powershell
   powershell -ExecutionPolicy Bypass -File C:\QLCBCS\trien_khai\windows\cap_nhat.ps1 `
       -TepGoi E:\QLCBCS_20261030_abc1234567_py312.zip -ThuMucSaoLuu D:\SaoLuu\QLCBCS
   ```

   Script: đối chiếu SHA-256 tệp ZIP → giải nén vào thư mục tạm và kiểm tra gói → sao lưu CSDL (lỗi thì dừng,
   không đụng vào hệ thống đang chạy) → dừng máy chủ → thay toàn bộ mã nguồn cũ, giữ `qlcbcs.env`, `.venv`,
   `nhat_ky`, `sao_luu` → cài thư viện từ gói → `migrate`, `collectstatic` → chạy lại máy chủ. Thay toàn bộ thay vì
   chép đè để tệp đã bỏ ở bản mới (nhất là thư viện cũ trong `goi\`) không còn sót lại.
3. Nếu một bước sau khi dừng máy chủ bị lỗi, máy chủ vẫn được chạy lại; xem thông báo lỗi, và khôi phục bản sao
   lưu vừa tạo (mục 7) nếu `migrate` đã chạy dở.

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
