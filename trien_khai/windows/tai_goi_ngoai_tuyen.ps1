<#
.SYNOPSIS
  Tải sẵn các gói Python để cài QL CBCS LAN trên máy chủ không có Internet.

.DESCRIPTION
  Chạy trên một máy Windows CÓ Internet, cùng phiên bản Python (ví dụ 3.12, 64-bit) với máy chủ.
  Sao chép cả thư mục mã nguồn (gồm thư mục "goi" vừa tạo) sang máy chủ, rồi chạy cai_dat.ps1
  với tham số -ThuMucGoi.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\tai_goi_ngoai_tuyen.ps1
#>
param(
    [string]$ThuMucCai = "",
    [string]$PhienBanPython = "3.12",
    [string]$ThuMucGoi = ""
)
. "$PSScriptRoot\chung.ps1"

$ThuMucCai = Lay-ThuMucCai $ThuMucCai
if (-not $ThuMucGoi) { $ThuMucGoi = Join-Path $ThuMucCai "goi" }
New-Item -ItemType Directory -Force -Path $ThuMucGoi | Out-Null

Ghi "Tải gói cho Python $PhienBanPython vào $ThuMucGoi"
Chay "py" @("-$PhienBanPython", "-m", "pip", "download", "--only-binary=:all:",
            "-r", (Join-Path $ThuMucCai "requirements.txt"), "-d", $ThuMucGoi)
Chay "py" @("-$PhienBanPython", "-m", "pip", "download", "--only-binary=:all:", "pip", "-d", $ThuMucGoi)
Ghi "Xong. Số tệp: $((Get-ChildItem $ThuMucGoi).Count)"
