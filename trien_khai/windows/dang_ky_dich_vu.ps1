<#
.SYNOPSIS
  Đăng ký QL CBCS LAN chạy nền khi Windows khởi động, mở cổng tường lửa cho mạng LAN.

.DESCRIPTION
  Dùng Task Scheduler có sẵn của Windows (không cần cài thêm công cụ):
  - Chạy chay_may_chu.py khi máy khởi động, bằng tài khoản LOCAL SERVICE (quyền thấp).
  - Tự khởi động lại sau 1 phút nếu tiến trình dừng do lỗi.
  - Mở cổng TCP trên tường lửa chỉ cho mạng con cục bộ (LocalSubnet), hồ sơ Domain/Private.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\dang_ky_dich_vu.ps1
#>
#Requires -RunAsAdministrator
param(
    [string]$ThuMucCai = ""
)
. "$PSScriptRoot\chung.ps1"

$ThuMucCai = Lay-ThuMucCai $ThuMucCai
$python = Lay-Python $ThuMucCai
$cau_hinh = Doc-CauHinh $ThuMucCai
$cong = 8000
if ($cau_hinh.ContainsKey("QLCBCS_CONG")) { $cong = [int]$cau_hinh["QLCBCS_CONG"] }

# Tác vụ chạy nền ---------------------------------------------------------------
if (Get-ScheduledTask -TaskName $TEN_TAC_VU_MAY_CHU -ErrorAction SilentlyContinue) {
    Ghi "Gỡ tác vụ cũ $TEN_TAC_VU_MAY_CHU"
    Stop-ScheduledTask -TaskName $TEN_TAC_VU_MAY_CHU -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TEN_TAC_VU_MAY_CHU -Confirm:$false
}
$hanh_dong = New-ScheduledTaskAction -Execute $python -Argument "`"$(Join-Path $ThuMucCai 'chay_may_chu.py')`"" `
    -WorkingDirectory $ThuMucCai
$kich_hoat = New-ScheduledTaskTrigger -AtStartup
$nguoi_chay = New-ScheduledTaskPrincipal -UserId "S-1-5-19" -LogonType ServiceAccount -RunLevel Limited
$thiet_lap = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $TEN_TAC_VU_MAY_CHU -Action $hanh_dong -Trigger $kich_hoat `
    -Principal $nguoi_chay -Settings $thiet_lap `
    -Description "QL CBCS LAN — máy chủ ứng dụng (Waitress), cổng $cong" | Out-Null
Ghi "Đã đăng ký tác vụ $TEN_TAC_VU_MAY_CHU (LOCAL SERVICE, tự khởi động lại khi lỗi)"

# Tường lửa ---------------------------------------------------------------------
$ten_luat = "QL CBCS LAN (TCP $cong)"
Get-NetFirewallRule -DisplayName $ten_luat -ErrorAction SilentlyContinue | Remove-NetFirewallRule
New-NetFirewallRule -DisplayName $ten_luat -Direction Inbound -Protocol TCP -LocalPort $cong -Action Allow `
    -Profile Domain, Private -RemoteAddress LocalSubnet | Out-Null
Ghi "Đã mở cổng $cong cho mạng con cục bộ (hồ sơ Domain/Private)"

# Khởi động và kiểm tra ---------------------------------------------------------
Start-ScheduledTask -TaskName $TEN_TAC_VU_MAY_CHU
$dia_chi = "http://localhost:$cong/admin/login/"
$ok = $false
for ($i = 0; $i -lt 20 -and -not $ok; $i++) {
    Start-Sleep -Seconds 2
    try {
        $phan_hoi = Invoke-WebRequest -Uri $dia_chi -UseBasicParsing -TimeoutSec 5
        $ok = ($phan_hoi.StatusCode -eq 200)
    } catch { }
}
if ($ok) {
    Ghi "Máy chủ đã chạy: http://$($env:COMPUTERNAME):$cong/so/xuat/"
} else {
    Ghi "Máy chủ chưa phản hồi sau 40 giây. Xem $(Join-Path $ThuMucCai 'nhat_ky') và Task Scheduler > $TEN_TAC_VU_MAY_CHU."
    exit 1
}
