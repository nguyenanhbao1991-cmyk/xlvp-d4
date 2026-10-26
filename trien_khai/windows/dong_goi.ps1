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
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\dong_goi.ps1 `
      -KemTep D:\cai\python-3.12.10-amd64.exe, D:\cai\postgresql-16.6-1-windows-x64.exe
#>
param(
    [string]$PhienBanPython = "3.12",
    [string[]]$KemTep = @(),
    [string]$ThuMucRa = ""
)
. "$PSScriptRoot\chung.ps1"

$ThuMucCai = Lay-ThuMucCai ""
$tham_so = @((Join-Path $ThuMucCai "trien_khai\dong_goi.py"), "--python", $PhienBanPython)
foreach ($tep in $KemTep) { $tham_so += @("--kem-tep", (Resolve-Path $tep).Path) }
if ($ThuMucRa) { $tham_so += @("--ra", $ThuMucRa) }
Chay "py" (@("-3") + $tham_so)
Ghi "Chép tệp .zip và .zip.sha256 sang máy chủ nội bộ, rồi làm theo docs\trien_khai_windows.md mục 4."
