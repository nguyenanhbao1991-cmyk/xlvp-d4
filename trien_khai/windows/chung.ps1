# Hàm dùng chung cho các script triển khai QL CBCS LAN trên Windows.
# Được nạp bằng: . "$PSScriptRoot\chung.ps1"

$ErrorActionPreference = "Stop"

# SID cố định, không phụ thuộc ngôn ngữ Windows (tên nhóm trên Windows tiếng Việt khác tiếng Anh).
$SID_QUAN_TRI = "*S-1-5-32-544"   # Administrators
$SID_SYSTEM = "*S-1-5-18"         # SYSTEM
$SID_LOCAL_SERVICE = "*S-1-5-19"  # LOCAL SERVICE — tài khoản chạy máy chủ ứng dụng
$TEN_TAC_VU_MAY_CHU = "QLCBCS-MayChu"
$TEN_TAC_VU_SAO_LUU = "QLCBCS-SaoLuu"

function Ghi([string]$ThongBao) {
    Write-Host ("[{0:HH:mm:ss}] {1}" -f (Get-Date), $ThongBao)
}

function Chay([string]$Tep, [string[]]$ThamSo) {
    # Chạy chương trình ngoài; dừng script nếu mã thoát khác 0.
    & $Tep @ThamSo
    if ($LASTEXITCODE -ne 0) {
        throw "Lệnh thất bại (mã $LASTEXITCODE): $Tep $($ThamSo -join ' ')"
    }
}

function Lay-ThuMucCai([string]$ThuMuc) {
    if ($ThuMuc) { return (Resolve-Path $ThuMuc).Path }
    # Mặc định: thư mục gốc mã nguồn (hai cấp trên thư mục chứa script).
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Lay-Python([string]$ThuMucCai) {
    $python = Join-Path $ThuMucCai ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        throw "Chưa có môi trường Python tại $python. Hãy chạy cai_dat.ps1 trước."
    }
    return $python
}

function Doc-CauHinh([string]$ThuMucCai) {
    # Đọc qlcbcs.env thành bảng KHOA -> giá trị (cùng quy tắc với qlcbcs/cau_hinh.py).
    $tep = Join-Path $ThuMucCai "qlcbcs.env"
    if (-not (Test-Path $tep)) { throw "Không thấy $tep." }
    $bang = @{}
    foreach ($dong in Get-Content -Path $tep -Encoding UTF8) {
        $dong = $dong.Trim()
        if ($dong -eq "" -or $dong.StartsWith("#")) { continue }
        $vi_tri = $dong.IndexOf("=")
        if ($vi_tri -lt 1) { continue }
        $khoa = $dong.Substring(0, $vi_tri).Trim()
        $gia_tri = $dong.Substring($vi_tri + 1).Trim()
        if ($gia_tri.Length -ge 2 -and ($gia_tri[0] -eq '"' -or $gia_tri[0] -eq "'") -and $gia_tri[-1] -eq $gia_tri[0]) {
            $gia_tri = $gia_tri.Substring(1, $gia_tri.Length - 2)
        }
        $bang[$khoa] = $gia_tri
    }
    return $bang
}
