<#
.SYNOPSIS
  Sao lưu CSDL QL CBCS LAN bằng pg_dump; tuỳ chọn đăng ký chạy hằng ngày.

.DESCRIPTION
  Tạo tệp qlcbcs_yyyyMMdd_HHmmss.dump (định dạng custom của pg_dump, khôi phục bằng pg_restore),
  xoá bản cũ hơn -SoNgayGiu ngày. CSDL chứa cả dữ liệu ra/vào, lịch sử xuất và các tệp đã xuất
  (bản chốt), nên một bản sao lưu là đủ để khôi phục toàn bộ.
  Nên đặt -ThuMucSaoLuu trên ổ đĩa khác hoặc máy khác trong LAN.

.EXAMPLE
  # Sao lưu ngay:
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\sao_luu.ps1 -ThuMucSaoLuu D:\SaoLuu\QLCBCS
  # Đăng ký sao lưu tự động 02:15 hằng ngày:
  powershell -ExecutionPolicy Bypass -File trien_khai\windows\sao_luu.ps1 -ThuMucSaoLuu D:\SaoLuu\QLCBCS -DangKyHangNgay
#>
param(
    [string]$ThuMucCai = "",
    [string]$ThuMucSaoLuu = "",
    [int]$SoNgayGiu = 30,
    [string]$PgDump = "",
    [switch]$DangKyHangNgay
)
. "$PSScriptRoot\chung.ps1"

$ThuMucCai = Lay-ThuMucCai $ThuMucCai
if (-not $ThuMucSaoLuu) { $ThuMucSaoLuu = Join-Path $ThuMucCai "sao_luu" }
New-Item -ItemType Directory -Force -Path $ThuMucSaoLuu | Out-Null
$ThuMucSaoLuu = (Resolve-Path $ThuMucSaoLuu).Path

if ($DangKyHangNgay) {
    $hanh_dong = New-ScheduledTaskAction -Execute "powershell.exe" -Argument (
        "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -ThuMucCai `"$ThuMucCai`" " +
        "-ThuMucSaoLuu `"$ThuMucSaoLuu`" -SoNgayGiu $SoNgayGiu")
    $kich_hoat = New-ScheduledTaskTrigger -Daily -At "02:15"
    $nguoi_chay = New-ScheduledTaskPrincipal -UserId "S-1-5-18" -LogonType ServiceAccount -RunLevel Highest
    $thiet_lap = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
    Register-ScheduledTask -TaskName $TEN_TAC_VU_SAO_LUU -Action $hanh_dong -Trigger $kich_hoat `
        -Principal $nguoi_chay -Settings $thiet_lap -Force `
        -Description "QL CBCS LAN — sao lưu CSDL hằng ngày vào $ThuMucSaoLuu" | Out-Null
    Ghi "Đã đăng ký $TEN_TAC_VU_SAO_LUU lúc 02:15 hằng ngày."
    exit 0
}

if (-not $PgDump) {
    $tim = Get-ChildItem "C:\Program Files\PostgreSQL\*\bin\pg_dump.exe" -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1
    if (-not $tim) { throw "Không thấy pg_dump.exe. Chỉ định đường dẫn bằng -PgDump." }
    $PgDump = $tim.FullName
}
$cau_hinh = Doc-CauHinh $ThuMucCai
$tep = Join-Path $ThuMucSaoLuu ("qlcbcs_{0:yyyyMMdd_HHmmss}.dump" -f (Get-Date))
$nhat_ky = Join-Path $ThuMucSaoLuu "sao_luu.log"

$env:PGPASSWORD = $cau_hinh["QLCBCS_DB_PASSWORD"]
try {
    Chay $PgDump @("--format=custom", "--no-owner", "--file=$tep",
                   "--host=$($cau_hinh['QLCBCS_DB_HOST'])", "--port=$($cau_hinh['QLCBCS_DB_PORT'])",
                   "--username=$($cau_hinh['QLCBCS_DB_USER'])", $cau_hinh["QLCBCS_DB_NAME"])
} catch {
    Add-Content -Path $nhat_ky -Value ("{0:yyyy-MM-dd HH:mm:ss} THẤT BẠI: {1}" -f (Get-Date), $_) -Encoding UTF8
    throw
} finally {
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}
$kich_thuoc = [math]::Round((Get-Item $tep).Length / 1MB, 1)
Add-Content -Path $nhat_ky -Value ("{0:yyyy-MM-dd HH:mm:ss} OK {1} ({2} MB)" -f (Get-Date), $tep, $kich_thuoc) -Encoding UTF8
Ghi "Đã sao lưu: $tep ($kich_thuoc MB)"

Get-ChildItem $ThuMucSaoLuu -Filter "qlcbcs_*.dump" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$SoNgayGiu) } |
    ForEach-Object { Remove-Item $_.FullName; Ghi "Xoá bản cũ: $($_.Name)" }
