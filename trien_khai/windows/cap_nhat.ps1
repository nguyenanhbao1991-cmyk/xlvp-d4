<#
.SYNOPSIS
  Cập nhật QL CBCS LAN từ gói ZIP do dong_goi.ps1 tạo (cài ngoại tuyến).

.DESCRIPTION
  1. Đối chiếu SHA-256 của tệp ZIP với tệp .zip.sha256 đi kèm.
  2. Giải nén vào thư mục tạm, kiểm tra gói (đủ tệp, đúng mã, đúng phiên bản Python).
  3. Sao lưu CSDL. Nếu sao lưu lỗi thì dừng, không đụng vào hệ thống đang chạy.
  4. Dừng máy chủ; thay mã nguồn cũ bằng mã nguồn mới (giữ qlcbcs.env, .venv, nhat_ky, sao_luu);
     cài thư viện từ gói; migrate; collectstatic; check.
  5. Chạy lại máy chủ (kể cả khi bước 4 lỗi — khi đó máy chủ chạy với những gì đang có, cần xem
     lỗi và khôi phục bản sao lưu nếu CSDL đã bị migrate dở).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File C:\QLCBCS\trien_khai\windows\cap_nhat.ps1 `
      -TepGoi E:\QLCBCS_20261030_abc1234567_py312.zip -ThuMucSaoLuu D:\SaoLuu\QLCBCS
#>
#Requires -RunAsAdministrator
param(
    [Parameter(Mandatory = $true)][string]$TepGoi,
    [string]$ThuMucCai = "",
    [string]$ThuMucSaoLuu = "",
    [string]$PhienBanPython = "3.12"
)
. "$PSScriptRoot\chung.ps1"

$ThuMucCai = Lay-ThuMucCai $ThuMucCai
# Chốt chặn: script sẽ xoá mã nguồn cũ trong thư mục này, nên chỉ chạy trên bản ĐÃ CÀI.
foreach ($bat_buoc in @("qlcbcs.env", ".venv")) {
    if (-not (Test-Path (Join-Path $ThuMucCai $bat_buoc))) {
        throw "$ThuMucCai không phải thư mục đã cài (thiếu $bat_buoc). Chạy script từ thư mục cài, " +
              "ví dụ C:\QLCBCS\trien_khai\windows\cap_nhat.ps1, hoặc chỉ định -ThuMucCai."
    }
}
$TepGoi = (Resolve-Path $TepGoi).Path
$python = Lay-Python $ThuMucCai
# Giữ lại khi thay mã nguồn: cấu hình, môi trường Python, dữ liệu sinh ra khi chạy.
$GIU_LAI = @("qlcbcs.env", ".venv", "nhat_ky", "sao_luu", "staticfiles")

# 1. Đối chiếu mã của tệp ZIP ------------------------------------------------------
$tep_ma = "$TepGoi.sha256"
if (-not (Test-Path $tep_ma)) { throw "Thiếu $tep_ma (tạo cùng lúc với tệp ZIP)." }
$ma_mong_doi = ((Get-Content $tep_ma -Encoding UTF8 | Select-Object -First 1) -split "\s+")[0].ToLower()
$ma_thuc = (Get-FileHash -Path $TepGoi -Algorithm SHA256).Hash.ToLower()
if ($ma_mong_doi -ne $ma_thuc) { throw "SHA-256 của tệp ZIP không khớp: tệp bị hỏng hoặc bị sửa. Không cập nhật." }
Ghi "Tệp ZIP đúng mã SHA-256."

# 2. Giải nén và kiểm tra gói ------------------------------------------------------
$tam = Join-Path $env:TEMP ("QLCBCS_capnhat_" + [guid]::NewGuid().ToString("N"))
Expand-Archive -Path $TepGoi -DestinationPath $tam
Get-ChildItem -Path $tam -Recurse -File | Unblock-File
try {
    Chay "py" @("-$PhienBanPython", (Join-Path $tam "trien_khai\kiem_tra_goi.py"))

    # 3. Sao lưu ------------------------------------------------------------------
    Ghi "Sao lưu CSDL trước khi cập nhật"
    & "$PSScriptRoot\sao_luu.ps1" -ThuMucCai $ThuMucCai -ThuMucSaoLuu $ThuMucSaoLuu

    # 4. Thay mã nguồn và cập nhật -----------------------------------------------------
    Ghi "Dừng máy chủ"
    Stop-ScheduledTask -TaskName $TEN_TAC_VU_MAY_CHU -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    try {
        Ghi "Thay mã nguồn"
        Get-ChildItem -Path $ThuMucCai -Force | Where-Object { $GIU_LAI -notcontains $_.Name } |
            Remove-Item -Recurse -Force
        Get-ChildItem -Path $tam -Force | Copy-Item -Destination $ThuMucCai -Recurse -Force
        $goi = Join-Path $ThuMucCai "goi"
        Chay $python @("-m", "pip", "install", "--no-index", "--find-links", $goi, "-r",
                       (Join-Path $ThuMucCai "requirements.txt"))
        Set-Location $ThuMucCai
        Chay $python @("manage.py", "migrate", "--noinput")
        Chay $python @("manage.py", "collectstatic", "--noinput", "--clear")
        Chay $python @("manage.py", "check", "--deploy")
    } finally {
        Ghi "Chạy lại máy chủ"
        Start-ScheduledTask -TaskName $TEN_TAC_VU_MAY_CHU
    }
} finally {
    Remove-Item -Path $tam -Recurse -Force -ErrorAction SilentlyContinue
}
Get-Content (Join-Path $ThuMucCai "PHIEN_BAN.txt") -Encoding UTF8 | ForEach-Object { Ghi $_ }
Ghi "Cập nhật xong."
