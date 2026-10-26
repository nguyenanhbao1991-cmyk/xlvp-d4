"""Đóng gói QL CBCS LAN để cài trên máy chủ Windows không có Internet.

Chạy trên một máy CÓ Internet (Windows hoặc Linux, Python bất kỳ từ 3.10):

    py -3 trien_khai\\dong_goi.py --python 3.12 --kem-tep D:\\cai\\python-3.12.10-amd64.exe ^
        --kem-tep D:\\cai\\postgresql-16.6-1-windows-x64.exe

Kết quả trong thư mục ``dist``:
    QLCBCS_<phiên bản>.zip          — giải nén thẳng vào C:\\QLCBCS trên máy chủ
    QLCBCS_<phiên bản>.zip.sha256   — mã kiểm tra để đối chiếu sau khi chép (USB, mạng nội bộ)

Gói gồm: mã nguồn (chỉ các tệp được Git quản lý — không lẫn qlcbcs.env, .venv, nhật ký), thư
viện Python dạng wheel cho Windows 64-bit trong ``goi/``, các bộ cài kèm theo trong
``cai_dat_he_thong/``, ``PHIEN_BAN.txt`` và ``MANIFEST-SHA256.txt`` (mã SHA-256 từng tệp).
"""
import argparse
import datetime
import hashlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
NEN_TANG = "win_amd64"
TEP_MANIFEST = "MANIFEST-SHA256.txt"
TEP_PHIEN_BAN = "PHIEN_BAN.txt"
THU_MUC_GOI = "goi"
THU_MUC_CAI_DAT = "cai_dat_he_thong"
# Khi không có Git: bỏ các thư mục/tệp sinh ra lúc chạy hoặc chứa bí mật.
LOAI_TRU_THU_MUC = {".git", ".venv", "venv", THU_MUC_GOI, THU_MUC_CAI_DAT, "dist", "staticfiles", "nhat_ky",
                    "sao_luu", "__pycache__", "node_modules"}
LOAI_TRU_TEP = {"qlcbcs.env", ".env"}


class LoiDongGoi(Exception):
    pass


def sha256(tep):
    h = hashlib.sha256()
    with open(tep, "rb") as f:
        for khoi in iter(lambda: f.read(1 << 20), b""):
            h.update(khoi)
    return h.hexdigest()


def _git(*tham_so):
    return subprocess.run(["git", *tham_so], cwd=GOC, capture_output=True, text=True, check=True).stdout


def danh_sach_tep_nguon(cho_phep_thay_doi=False):
    """(danh sách đường dẫn tương đối, nhãn phiên bản)."""
    if (GOC / ".git").exists() and shutil.which("git"):
        thay_doi = _git("status", "--porcelain").strip()
        if thay_doi and not cho_phep_thay_doi:
            raise LoiDongGoi("Có thay đổi chưa commit; commit trước, hoặc dùng --cho-phep-thay-doi:\n" + thay_doi)
        tep = [Path(p) for p in _git("ls-files", "-z").split("\0") if p]
        nhan = _git("rev-parse", "--short=10", "HEAD").strip() + ("-co-thay-doi" if thay_doi else "")
        return [p for p in tep if (GOC / p).is_file()], nhan
    tep = []
    for p in sorted(GOC.rglob("*")):
        tuong_doi = p.relative_to(GOC)
        if any(phan in LOAI_TRU_THU_MUC for phan in tuong_doi.parts) or p.name in LOAI_TRU_TEP:
            continue
        if p.is_file():
            tep.append(tuong_doi)
    return tep, "khong-git"


def _co_pip_nen_tang(phien_ban_python):
    phien_ban = phien_ban_python.replace(".", "")
    return ["--only-binary=:all:", "--platform", NEN_TANG, "--python-version", phien_ban, "--implementation", "cp"]


def tai_thu_vien(thu_muc, phien_ban_python, yeu_cau):
    subprocess.run([sys.executable, "-m", "pip", "download", "--disable-pip-version-check", "-q",
                    *_co_pip_nen_tang(phien_ban_python), "-r", str(yeu_cau), "-d", str(thu_muc)], check=True)


def kiem_tra_du_thu_vien(thu_muc, phien_ban_python, yeu_cau):
    """Thử giải phụ thuộc chỉ từ thư mục gói, như máy chủ không có mạng sẽ làm."""
    with tempfile.TemporaryDirectory() as tam:
        kq = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--dry-run", "--ignore-installed",
             "--no-index", "--find-links", str(thu_muc), *_co_pip_nen_tang(phien_ban_python), "--target", tam,
             "-r", str(yeu_cau)],
            capture_output=True, text=True,
        )
    if kq.returncode != 0:
        raise LoiDongGoi("Thư mục gói thiếu thư viện cho Windows:\n" + kq.stdout + kq.stderr)


def ghi_manifest(thu_muc_goi):
    dong = []
    for p in sorted(x for x in thu_muc_goi.rglob("*") if x.is_file() and x.name != TEP_MANIFEST):
        dong.append(f"{sha256(p)}  {p.relative_to(thu_muc_goi).as_posix()}")
    (thu_muc_goi / TEP_MANIFEST).write_text("\n".join(dong) + "\n", encoding="utf-8")
    return len(dong)


def dong_goi(phien_ban_python, kem_tep=(), thu_muc_ra=None, cho_phep_thay_doi=False, tai=True, bao=print):
    thu_muc_ra = Path(thu_muc_ra or GOC / "dist")
    tep_nguon, nhan = danh_sach_tep_nguon(cho_phep_thay_doi)
    ten = f"QLCBCS_{datetime.date.today():%Y%m%d}_{nhan}_py{phien_ban_python.replace('.', '')}"
    with tempfile.TemporaryDirectory() as tam:
        goi = Path(tam) / ten
        bao(f"Chép {len(tep_nguon)} tệp mã nguồn")
        for p in tep_nguon:
            (goi / p).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(GOC / p, goi / p)
        thu_vien = goi / THU_MUC_GOI
        thu_vien.mkdir()
        if tai:
            bao(f"Tải thư viện cho Python {phien_ban_python} {NEN_TANG}")
            tai_thu_vien(thu_vien, phien_ban_python, goi / "requirements.txt")
            kiem_tra_du_thu_vien(thu_vien, phien_ban_python, goi / "requirements.txt")
        for p in kem_tep:
            p = Path(p)
            if not p.is_file():
                raise LoiDongGoi(f"Không thấy tệp kèm theo {p}")
            (goi / THU_MUC_CAI_DAT).mkdir(exist_ok=True)
            shutil.copy2(p, goi / THU_MUC_CAI_DAT / p.name)
        (goi / TEP_PHIEN_BAN).write_text(
            f"ma_nguon={nhan}\nngay_dong_goi={datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n"
            f"python={phien_ban_python}\nnen_tang={NEN_TANG}\n"
            f"so_thu_vien={len(list(thu_vien.iterdir()))}\n", encoding="utf-8")
        so_tep = ghi_manifest(goi)

        thu_muc_ra.mkdir(parents=True, exist_ok=True)
        tep_zip = thu_muc_ra / f"{ten}.zip"
        with zipfile.ZipFile(tep_zip, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(goi.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(goi).as_posix())
    ma = sha256(tep_zip)
    (thu_muc_ra / f"{tep_zip.name}.sha256").write_text(f"{ma}  {tep_zip.name}\n", encoding="utf-8")
    bao(f"Đã tạo {tep_zip} ({tep_zip.stat().st_size / 1048576:.1f} MB, {so_tep} tệp)")
    bao(f"SHA-256: {ma}")
    return tep_zip, ma


def main(argv=None):
    p = argparse.ArgumentParser(description="Đóng gói QL CBCS LAN để cài ngoại tuyến trên Windows.")
    p.add_argument("--python", default="3.12", help="Phiên bản Python trên máy chủ (mặc định 3.12)")
    p.add_argument("--kem-tep", action="append", default=[], help="Bộ cài kèm theo (Python, PostgreSQL...)")
    p.add_argument("--ra", default=None, help="Thư mục kết quả (mặc định dist)")
    p.add_argument("--cho-phep-thay-doi", action="store_true", help="Cho đóng gói khi còn thay đổi chưa commit")
    a = p.parse_args(argv)
    if a.python not in ("3.10", "3.11", "3.12", "3.13"):
        p.error("--python phải là 3.10, 3.11, 3.12 hoặc 3.13")
    try:
        dong_goi(a.python, a.kem_tep, a.ra, a.cho_phep_thay_doi)
    except (LoiDongGoi, subprocess.CalledProcessError) as loi:
        print(f"LỖI: {loi}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
