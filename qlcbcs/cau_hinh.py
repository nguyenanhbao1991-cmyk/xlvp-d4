"""Đọc tệp cấu hình ``qlcbcs.env`` (dạng KHOA=gia_tri) vào biến môi trường.

Trên máy chủ Windows, cấu hình (mật khẩu CSDL, khoá bí mật...) để trong một tệp chỉ tài khoản
chạy dịch vụ và quản trị được đọc, thay vì biến môi trường hệ thống. Biến môi trường đã đặt
sẵn luôn được ưu tiên hơn giá trị trong tệp.
"""
import os
from pathlib import Path


def doc_tep_moi_truong(duong_dan):
    """Nạp các dòng ``KHOA=gia_tri`` chưa có trong môi trường. Trả về danh sách khoá đã nạp."""
    duong_dan = Path(duong_dan)
    if not duong_dan.is_file():
        return []
    da_nap = []
    # utf-8-sig: chấp nhận tệp do Notepad trên Windows lưu kèm BOM.
    for so_dong, dong in enumerate(duong_dan.read_text(encoding="utf-8-sig").splitlines(), 1):
        dong = dong.strip()
        if not dong or dong.startswith("#"):
            continue
        if "=" not in dong:
            raise ValueError(f"{duong_dan}:{so_dong}: thiếu dấu '=' (cần dạng KHOA=gia_tri).")
        khoa, gia_tri = (phan.strip() for phan in dong.split("=", 1))
        if len(gia_tri) >= 2 and gia_tri[0] == gia_tri[-1] and gia_tri[0] in "\"'":
            gia_tri = gia_tri[1:-1]
        if khoa and khoa not in os.environ:
            os.environ[khoa] = gia_tri
            da_nap.append(khoa)
    return da_nap


def nap_cau_hinh(thu_muc_goc):
    """Nạp tệp do ``QLCBCS_TEP_CAU_HINH`` chỉ định, mặc định ``<thư mục gốc>/qlcbcs.env``."""
    return doc_tep_moi_truong(os.environ.get("QLCBCS_TEP_CAU_HINH", Path(thu_muc_goc) / "qlcbcs.env"))
