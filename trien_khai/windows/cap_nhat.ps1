<#
.SYNOPSIS
  Cập nhật QL CBCS LAN lên phiên bản mã nguồn mới.

.DESCRIPTION
  Chạy SAU KHI đã chép mã nguồn mới đè lên thư mục cài đặt (giữ nguyên qlcbcs.env, .venv).
  Trình tự: sao lưu CSDL -> dừng máy chủ -> cài thư viện -> migrate -> collectstatic -> chạy lại.
  Nếu một bước lỗi, máy chủ được chạy lại với mã đang có và script dừng.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\cap_nhat.ps1 -ThuMucGoi .\goi -ThuMucSaoLuu D:\SaoLuu\QLCBCS
#>
#Requires -RunAsAdministrator
param(
    [string]$ThuMucCai = "",
    [string]$ThuMucGoi = "",
    [string]$ThuMucSaoLuu = ""
)
. "$PSScriptRoot\chung.ps1"

$ThuMucCai = Lay-ThuMucCai $ThuMucCai
Set-Location $ThuMucCai
$python = Lay-Python $ThuMucCai

Ghi "Sao lưu CSDL trước khi cập nhật"
& "$PSScriptRoot\sao_luu.ps1" -ThuMucCai $ThuMucCai -ThuMucSaoLuu $ThuMucSaoLuu

Ghi "Dừng máy chủ"
Stop-ScheduledTask -TaskName $TEN_TAC_VU_MAY_CHU -ErrorAction SilentlyContinue
try {
    $yeu_cau = Join-Path $ThuMucCai "requirements.txt"
    if ($ThuMucGoi) {
        Chay $python @("-m", "pip", "install", "--no-index", "--find-links", (Resolve-Path $ThuMucGoi).Path, "-r", $yeu_cau)
    } else {
        Chay $python @("-m", "pip", "install", "-r", $yeu_cau)
    }
    Chay $python @("manage.py", "migrate", "--noinput")
    Chay $python @("manage.py", "collectstatic", "--noinput")
    Chay $python @("manage.py", "check", "--deploy")
} finally {
    Ghi "Chạy lại máy chủ"
    Start-ScheduledTask -TaskName $TEN_TAC_VU_MAY_CHU
}
Ghi "Cập nhật xong."
