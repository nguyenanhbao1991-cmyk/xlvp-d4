<#
.SYNOPSIS
  Đóng gói QL CBCS LAN trên máy CÓ Internet để cài trên máy chủ nội bộ không có Internet.

.DESCRIPTION
  Tạo dist\QLCBCS_<ngày>_<mã nguồn>_py312.zip gồm: mã nguồn, thư viện Python cho Windows 64-bit
  (thư mục goi), các bộ cài kèm theo (thư mục cai_dat_he_thong), PHIEN_BAN.txt và
  MANIFEST-SHA256.txt; cùng tệp .zip.sha256 để đối chiếu sau khi chép sang máy chủ.
  Máy đóng gói cần Python 3.10+ (bất kỳ phiên bản), Git và Internet; không cần trùng phiên bản
  Python với máy chủ.

.EXAMPLE
  # Thay đường dẫn bằng vị trí thật của các bộ cài; nhiều tệp ngăn bằng dấu phẩy, đặt trong ngoặc kép.
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\dong_goi.ps1 -KemTep "D:\cai\python-3.12.10-amd64.exe,D:\cai\postgresql-16.6-1-windows-x64.exe"

.EXAMPLE
  # Tự tìm bộ cài Python 3.12 64-bit và PostgreSQL trong thư mục Downloads của người dùng hiện tại.
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\dong_goi.ps1 -TimBoCai

.EXAMPLE
  # Chưa có bộ cài: đóng gói không kèm, chép bộ cài sang máy chủ riêng.
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\dong_goi.ps1
#>
# PositionalBinding=$false: giá trị thừa (ví dụ tệp thứ hai sau dấu phẩy) báo lỗi rõ ràng thay vì
# bị gán nhầm vào -PhienBanPython.
[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$PhienBanPython = "3.12",
    [string[]]$KemTep = @(),
    [switch]$TimBoCai,
    [string]$ThuMucRa = ""
)
. "$PSScriptRoot\chung.ps1"

$ThuMucCai = Lay-ThuMucCai ""
$tham_so = @((Join-Path $ThuMucCai "trien_khai\dong_goi.py"), "--python", $PhienBanPython)
if ($TimBoCai) {
    $thu_muc_tai = Join-Path $env:USERPROFILE "Downloads"
    Ghi "Tìm bộ cài trong $thu_muc_tai"
    foreach ($mau in @("python-$PhienBanPython.*-amd64.exe", "postgresql-*-windows-x64.exe")) {
        $tim = Get-ChildItem -Path $thu_muc_tai -Filter $mau -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($tim) {
            Ghi "  Thấy: $($tim.FullName)"
            $KemTep += $tim.FullName
        } else {
            Ghi "  KHÔNG thấy tệp dạng $mau - gói sẽ không kèm bộ cài này, hãy chép riêng sang máy chủ."
        }
    }
}

# Khi gọi bằng "powershell -File", PowerShell không tách danh sách theo dấu phẩy: tự tách ở đây.
$cac_tep = @($KemTep | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim().Trim('"') } |
    Where-Object { $_ })
foreach ($tep in $cac_tep) {
    if ($tep -match "[<>]") { throw "Giá trị '$tep' là chỗ để điền: hãy thay bằng đường dẫn thật tới tệp bộ cài." }
    if (-not (Test-Path -LiteralPath $tep -PathType Leaf)) {
        throw ("Không thấy tệp bộ cài: $tep`nKiểm tra tên tệp thật bằng lệnh: " +
               "Get-ChildItem `$env:USERPROFILE\Downloads\*.exe | Select-Object FullName" +
               "`nhoặc dùng -TimBoCai để script tự tìm trong thư mục Downloads.")
    }
    $tham_so += @("--kem-tep", (Resolve-Path -LiteralPath $tep).Path)
}
if ($ThuMucRa) { $tham_so += @("--ra", $ThuMucRa) }
Chay "py" (@("-3") + $tham_so)
Ghi "Chép tệp .zip và .zip.sha256 sang máy chủ nội bộ, rồi làm theo docs\trien_khai_windows.md mục 4."
