<#
.SYNOPSIS
  Cài đặt (hoặc cài lại) QL CBCS LAN trên máy chủ Windows.

.DESCRIPTION
  1. Tạo môi trường Python .venv và cài thư viện (ngoại tuyến nếu có -ThuMucGoi).
  2. Tạo qlcbcs.env với khoá bí mật ngẫu nhiên nếu chưa có; giới hạn quyền đọc tệp này.
  3. Tạo bảng CSDL (migrate), gom tệp tĩnh (collectstatic), kiểm tra cấu hình.
  4. Cấp quyền thư mục cho tài khoản LOCAL SERVICE (tài khoản chạy máy chủ ứng dụng).
  Chạy lại an toàn: không ghi đè qlcbcs.env đã có, không xoá dữ liệu.

.EXAMPLE
  # PowerShell "Run as administrator", trong thư mục mã nguồn:
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\cai_dat.ps1
  # Gói ngoại tuyến (có MANIFEST-SHA256.txt) được kiểm tra và dùng thư mục goi tự động.
#>
#Requires -RunAsAdministrator
param(
    [string]$ThuMucCai = "",
    [string]$PhienBanPython = "3.12",
    [string]$ThuMucGoi = ""
)
. "$PSScriptRoot\chung.ps1"

$ThuMucCai = Lay-ThuMucCai $ThuMucCai
Set-Location $ThuMucCai
Ghi "Thư mục cài đặt: $ThuMucCai"

# 0. Gói ngoại tuyến: kiểm tra đủ tệp, đúng mã SHA-256, đúng phiên bản Python trước khi cài.
if (Test-Path (Join-Path $ThuMucCai "MANIFEST-SHA256.txt")) {
    Ghi "Kiểm tra gói cài đặt"
    Chay "py" @("-$PhienBanPython", (Join-Path $ThuMucCai "trien_khai\kiem_tra_goi.py"))
    if (-not $ThuMucGoi -and (Test-Path (Join-Path $ThuMucCai "goi"))) { $ThuMucGoi = Join-Path $ThuMucCai "goi" }
}

# 1. Python và thư viện -------------------------------------------------------
$venv = Join-Path $ThuMucCai ".venv"
if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) {
    Ghi "Tạo môi trường Python $PhienBanPython"
    Chay "py" @("-$PhienBanPython", "-m", "venv", $venv)
}
$python = Lay-Python $ThuMucCai
$phien_ban = & $python -c "import sys; print('%d.%d' % sys.version_info[:2])"
if (@("3.10", "3.11", "3.12", "3.13") -notcontains $phien_ban) {
    throw "Python $phien_ban chưa được kiểm thử; cần 3.10–3.13."
}
# Máy chủ chạy bằng LOCAL SERVICE: Python phải cài "for all users" (C:\Program Files\...),
# không được nằm trong thư mục hồ sơ người dùng.
$goc_python = & $python -c "import sys; print(sys.base_prefix)"
if ($goc_python -like "*\Users\*") {
    throw "Python đang cài trong hồ sơ người dùng ($goc_python). Cài lại Python với tuỳ chọn " +
          "'Install for all users', xoá thư mục .venv rồi chạy lại script này."
}
$yeu_cau = Join-Path $ThuMucCai "requirements.txt"
if ($ThuMucGoi) {
    Ghi "Cài thư viện ngoại tuyến từ $ThuMucGoi"
    Chay $python @("-m", "pip", "install", "--no-index", "--find-links", (Resolve-Path $ThuMucGoi).Path, "-r", $yeu_cau)
} else {
    Ghi "Cài thư viện từ Internet"
    Chay $python @("-m", "pip", "install", "-r", $yeu_cau)
}

# 2. Tệp cấu hình -------------------------------------------------------------
$tep_cau_hinh = Join-Path $ThuMucCai "qlcbcs.env"
if (-not (Test-Path $tep_cau_hinh)) {
    Ghi "Tạo qlcbcs.env"
    $byte = New-Object byte[] 48
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($byte)
    $khoa = [Convert]::ToBase64String($byte).Replace("+", "-").Replace("/", "_").TrimEnd("=")

    $mat_khau_an = Read-Host "Mật khẩu tài khoản CSDL 'qlcbcs' (đã tạo ở bước PostgreSQL)" -AsSecureString
    $mat_khau = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($mat_khau_an))
    if (-not $mat_khau) { throw "Chưa nhập mật khẩu CSDL." }

    # Tên máy và các địa chỉ IPv4 trong LAN để người dùng truy cập.
    $dia_chi = @("localhost", "127.0.0.1", $env:COMPUTERNAME)
    $dia_chi += Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -ne "127.0.0.1" -and -not $_.IPAddress.StartsWith("169.254.") } |
        ForEach-Object { $_.IPAddress }

    $noi_dung = Get-Content -Path (Join-Path $ThuMucCai "qlcbcs.env.mau") -Encoding UTF8
    $noi_dung = $noi_dung | ForEach-Object {
        if ($_ -like "QLCBCS_SECRET_KEY=*") { "QLCBCS_SECRET_KEY=$khoa" }
        elseif ($_ -like "QLCBCS_DB_PASSWORD=*") { "QLCBCS_DB_PASSWORD=$mat_khau" }
        elseif ($_ -like "QLCBCS_ALLOWED_HOSTS=*") { "QLCBCS_ALLOWED_HOSTS=" + (($dia_chi | Select-Object -Unique) -join ",") }
        else { $_ }
    }
    Set-Content -Path $tep_cau_hinh -Value $noi_dung -Encoding UTF8
    Ghi "Đã ghi qlcbcs.env. Kiểm tra lại QLCBCS_ALLOWED_HOSTS nếu người dùng truy cập bằng tên khác."
} else {
    Ghi "Giữ nguyên qlcbcs.env đã có."
}
# Chỉ quản trị, SYSTEM (sao lưu) và LOCAL SERVICE (máy chủ ứng dụng) được đọc tệp chứa mật khẩu.
Chay "icacls" @($tep_cau_hinh, "/inheritance:r", "/grant:r", "${SID_QUAN_TRI}:(F)", "${SID_SYSTEM}:(F)",
                "${SID_LOCAL_SERVICE}:(R)")

# 3. CSDL, tệp tĩnh, kiểm tra ---------------------------------------------------
Ghi "Tạo/cập nhật bảng CSDL"
Chay $python @("manage.py", "migrate", "--noinput")
Ghi "Gom tệp tĩnh"
Chay $python @("manage.py", "collectstatic", "--noinput")
Ghi "Kiểm tra cấu hình (cảnh báo về HTTPS là bình thường nếu chưa dùng HTTPS)"
Chay $python @("manage.py", "check", "--deploy")

# 4. Quyền thư mục cho LOCAL SERVICE ----------------------------------------------
$nhat_ky = Join-Path $ThuMucCai "nhat_ky"
New-Item -ItemType Directory -Force -Path $nhat_ky | Out-Null
Chay "icacls" @($ThuMucCai, "/grant", "${SID_LOCAL_SERVICE}:(OI)(CI)(RX)")
Chay "icacls" @($nhat_ky, "/grant", "${SID_LOCAL_SERVICE}:(OI)(CI)(M)")

Ghi "Cài đặt xong. Tiếp theo:"
Ghi "  - Tạo tài khoản quản trị: .venv\Scripts\python.exe manage.py createsuperuser"
Ghi "  - Đăng ký chạy nền:       trien_khai\windows\dang_ky_dich_vu.ps1"
