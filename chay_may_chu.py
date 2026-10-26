"""Chạy QL CBCS LAN bằng Waitress (dùng cho máy chủ Windows trong LAN).

    .venv\\Scripts\\python.exe chay_may_chu.py

Địa chỉ, cổng và số luồng lấy từ qlcbcs.env: QLCBCS_DIA_CHI (mặc định 0.0.0.0),
QLCBCS_CONG (8000), QLCBCS_SO_LUONG (8).
"""
import os
import sys
from pathlib import Path

THU_MUC_GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(THU_MUC_GOC))

from qlcbcs.cau_hinh import nap_cau_hinh  # noqa: E402


def _ghi_loi_khoi_dong(loi):
    """Tác vụ chạy nền không có cửa sổ: ghi lỗi khởi động ra tệp để quản trị xem."""
    import datetime
    import traceback

    thu_muc = Path(os.environ.get("QLCBCS_THU_MUC_NHAT_KY", THU_MUC_GOC / "nhat_ky"))
    thu_muc.mkdir(parents=True, exist_ok=True)
    with open(thu_muc / "khoi_dong.log", "a", encoding="utf-8") as tep:
        tep.write(f"\n[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] Không khởi động được: {loi}\n")
        tep.write(traceback.format_exc())


def main():
    nap_cau_hinh(THU_MUC_GOC)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qlcbcs.settings")
    from django.core.wsgi import get_wsgi_application
    from waitress import serve

    ung_dung = get_wsgi_application()  # Lỗi cấu hình (thiếu khoá bí mật...) dừng ngay tại đây.
    dia_chi = os.environ.get("QLCBCS_DIA_CHI", "0.0.0.0")
    cong = int(os.environ.get("QLCBCS_CONG", "8000"))
    print(f"QL CBCS LAN đang chạy tại http://{dia_chi}:{cong}/so/xuat/", flush=True)
    serve(
        ung_dung, host=dia_chi, port=cong, threads=int(os.environ.get("QLCBCS_SO_LUONG", "8")),
        # Xuất PDF 5.000 dòng mất khoảng 30 giây: giữ kết nối đủ lâu.
        channel_timeout=300, ident="QLCBCS",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as loi:
        _ghi_loi_khoi_dong(loi)
        raise  # Mã thoát khác 0: Task Scheduler sẽ khởi động lại sau 1 phút.
