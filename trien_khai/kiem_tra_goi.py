"""Kiểm tra gói cài đặt ngoại tuyến trước khi cài trên máy chủ.

    py -3.12 trien_khai\\kiem_tra_goi.py

- Mọi tệp trong MANIFEST-SHA256.txt phải có và đúng mã SHA-256 (phát hiện chép thiếu, hỏng,
  hoặc bị sửa trên đường chuyển).
- Thư mục ``goi/`` và ``cai_dat_he_thong/`` không được có tệp lạ: pip sẽ cài bất kỳ wheel nào
  nằm trong ``goi/``.
- Python đang chạy phải đúng phiên bản và 64-bit như lúc đóng gói.
Thoát mã 0 nếu đạt, 1 nếu không.
"""
import hashlib
import struct
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
TEP_MANIFEST = "MANIFEST-SHA256.txt"
THU_MUC_KIEM_SOAT = ("goi", "cai_dat_he_thong")


def _sha256(tep):
    h = hashlib.sha256()
    with open(tep, "rb") as f:
        for khoi in iter(lambda: f.read(1 << 20), b""):
            h.update(khoi)
    return h.hexdigest()


def doc_phien_ban(goc):
    tep = goc / "PHIEN_BAN.txt"
    if not tep.is_file():
        return {}
    return dict(dong.split("=", 1) for dong in tep.read_text(encoding="utf-8").splitlines() if "=" in dong)


def kiem_tra(goc=GOC, python_hien_tai=None, bit=None):
    """Trả về danh sách lỗi (rỗng là đạt)."""
    loi = []
    manifest = goc / TEP_MANIFEST
    if not manifest.is_file():
        return [f"Không có {TEP_MANIFEST}: đây không phải gói do dong_goi.py tạo, hoặc đã bị chép thiếu."]
    da_khai = set()
    for so, dong in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not dong.strip():
            continue
        ma, _, ten = dong.partition("  ")
        if len(ma) != 64 or not ten:
            loi.append(f"{TEP_MANIFEST}:{so}: dòng không hợp lệ.")
            continue
        da_khai.add(ten)
        tep = goc / ten
        if not tep.is_file():
            loi.append(f"Thiếu tệp: {ten}")
        elif _sha256(tep) != ma:
            loi.append(f"Sai mã SHA-256 (tệp hỏng hoặc bị sửa): {ten}")
    for thu_muc in THU_MUC_KIEM_SOAT:
        for p in sorted((goc / thu_muc).rglob("*")) if (goc / thu_muc).is_dir() else []:
            if p.is_file() and p.relative_to(goc).as_posix() not in da_khai:
                loi.append(f"Tệp lạ không có trong gói: {p.relative_to(goc).as_posix()}")

    pb = doc_phien_ban(goc)
    python_hien_tai = python_hien_tai or f"{sys.version_info[0]}.{sys.version_info[1]}"
    bit = bit or struct.calcsize("P") * 8
    if pb.get("python") and pb["python"] != python_hien_tai:
        loi.append(f"Gói dành cho Python {pb['python']} nhưng đang chạy Python {python_hien_tai}.")
    if pb.get("nen_tang") == "win_amd64" and bit != 64:
        loi.append("Gói dành cho Python 64-bit nhưng đang chạy Python 32-bit.")
    return loi


def main():
    pb = doc_phien_ban(GOC)
    if pb:
        print(f"Gói: mã nguồn {pb.get('ma_nguon')}, đóng gói {pb.get('ngay_dong_goi')}, Python {pb.get('python')}")
    loi = kiem_tra()
    if loi:
        print("GÓI KHÔNG ĐẠT — không cài:", file=sys.stderr)
        for x in loi:
            print(f"  - {x}", file=sys.stderr)
        return 1
    print("Gói đạt: đủ tệp, đúng mã SHA-256, đúng phiên bản Python.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
