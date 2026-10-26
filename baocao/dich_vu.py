"""Điều phối một lần xuất Excel (REQ-GEN-15, BR-TX-01…05).

Thứ tự:
1. Kiểm tra quyền (không đạt: từ chối, không cấp mã, không ghi lịch sử).
2. Cấp mã trích xuất, ghi lịch sử ở trạng thái "Đang xử lý" (giao dịch riêng).
3. Đọc dữ liệu trong một giao dịch REPEATABLE READ, READ ONLY (đọc nhất quán).
4. Tạo tệp trong bộ nhớ, tính SHA-256.
5. Chỉ khi bước 3–4 xong mới ghi "Thành công"; mọi lỗi ghi "Thất bại".
"""
import datetime
import hashlib
import logging
from dataclasses import dataclass

from django.db import connection, transaction
from django.utils import timezone

from . import dong_ho, excel, quyen, so_lieu
from .models import BoDemTrichXuat, CauHinhSo, LichSuXuat

logger = logging.getLogger(__name__)

MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class LoiXuat(Exception):
    def __init__(self, thong_bao, lich_su):
        super().__init__(thong_bao)
        self.lich_su = lich_su


@dataclass
class TepXuat:
    ten_file: str
    noi_dung: bytes
    lich_su: LichSuXuat


def ho_ten_tai_khoan(nguoi_dung):
    return f"{quyen.ho_ten(nguoi_dung)} (tài khoản: {nguoi_dung.get_username()})"


def _cap_ma(dinh_nghia, bay_gio):
    ngay = timezone.localtime(bay_gio).date()
    so = BoDemTrichXuat.cap_so(ngay)
    return f"{dinh_nghia.ma_gon}-{ngay:%Y%m%d}-{so:04d}"


def ten_file(dinh_nghia, ky, ma_trich_xuat):
    return f"{dinh_nghia.ma_gon}_{dinh_nghia.ten_ngan}_{ky.ngay_dau:%Y%m%d}-{ky.ngay_cuoi:%Y%m%d}_{ma_trich_xuat}.xlsx"


def _mo_doc_nhat_quan():
    """Đặt mức cô lập cho giao dịch đọc. Chỉ làm được khi đây là giao dịch ngoài cùng."""
    if connection.vendor == "postgresql" and not connection.in_atomic_block:
        return True
    return False


def _dieu_kien_loc_json(bo_loc):
    return {
        "cong": [c.ma for c in bo_loc.cong],
        "dieu_kien": bo_loc.mo_ta(),
        "trang_thai": bo_loc.trang_thai,
        "sap_xep": bo_loc.sap_xep,
        "hien_huy": bo_loc.hien_huy,
    }


def xuat_excel(nguoi_dung, dinh_nghia, ky, bo_loc, nguoi_lap_so, du_lieu_ca_nhan_day_du=False, dia_chi_ip=None):
    quyen.kiem_tra_quyen_so(
        nguoi_dung, dinh_nghia, xuat=True, hien_huy=bo_loc.hien_huy, du_lieu_day_du=du_lieu_ca_nhan_day_du
    )
    cau_hinh = CauHinhSo.lay()
    bat_dau = dong_ho.hien_tai()
    lich_su = LichSuXuat.objects.create(
        ma_trich_xuat=_cap_ma(dinh_nghia, bat_dau),
        ma_so=dinh_nghia.ma,
        tu=ky.tu,
        den=ky.den,
        bat_dau_luc=bat_dau,
        nguoi_xuat=nguoi_dung,
        nguoi_lap_so=nguoi_lap_so,
        dieu_kien_loc=_dieu_kien_loc_json(bo_loc),
        du_lieu_ca_nhan_day_du=du_lieu_ca_nhan_day_du,
        dia_chi_ip=dia_chi_ip,
    )
    try:
        doc_nhat_quan = _mo_doc_nhat_quan()
        with transaction.atomic():
            if doc_nhat_quan:
                with connection.cursor() as c:
                    c.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                    c.execute("SELECT 1")  # Ảnh chụp dữ liệu được xác lập tại câu lệnh này.
            thoi_diem = dong_ho.hien_tai()
            chot = min(ky.den, thoi_diem)
            tt = excel.ThongTinXuat(
                ma_trich_xuat=lich_su.ma_trich_xuat,
                thoi_diem_trich_xuat=thoi_diem,
                nguoi_xuat=ho_ten_tai_khoan(nguoi_dung),
                nguoi_lap_so=nguoi_lap_so,
                cau_hinh=cau_hinh,
                du_lieu_ca_nhan_day_du=du_lieu_ca_nhan_day_du,
            )
            nguong = datetime.timedelta(minutes=cau_hinh.nguong_ghi_bo_sung_phut)
            if dinh_nghia.nhom:
                ket_qua = so_lieu.lap_so_chi_tiet(nguoi_dung, dinh_nghia, ky, chot, bo_loc, nguong, thoi_diem)
                wb, so_dong = excel.tao_so_chi_tiet(ket_qua, tt)
                chi_tieu = _json_duoc(ket_qua.chi_tieu)
            else:
                ket_qua = so_lieu.lap_so_tong_hop(nguoi_dung, dinh_nghia, ky, chot, bo_loc, nguong, thoi_diem)
                wb, theo_phan = excel.tao_so_tong_hop(ket_qua, tt)
                so_dong = sum(theo_phan.values())
                chi_tieu = {"theo_nhom": _json_duoc(ket_qua.phan_a), "so_dong_theo_phan": theo_phan}
        noi_dung = excel.luu(wb)
        if not noi_dung:
            raise excel.LoiDuLieuExcel("Tệp tạo ra rỗng.")
    except Exception as loi:
        logger.exception("Xuất %s thất bại (%s)", dinh_nghia.ma, lich_su.ma_trich_xuat)
        LichSuXuat.objects.filter(pk=lich_su.pk).update(
            ket_qua=LichSuXuat.KetQua.THAT_BAI,
            loi=f"{type(loi).__name__}: {loi}"[:2000],
            ket_thuc_luc=dong_ho.hien_tai(),
        )
        lich_su.refresh_from_db()
        thong_bao = str(loi) if isinstance(loi, excel.LoiDuLieuExcel) else "Không tạo được tệp Excel."
        raise LoiXuat(thong_bao, lich_su) from loi

    ten = ten_file(dinh_nghia, ky, lich_su.ma_trich_xuat)
    LichSuXuat.objects.filter(pk=lich_su.pk).update(
        ket_qua=LichSuXuat.KetQua.THANH_CONG,
        thoi_diem_trich_xuat=thoi_diem,
        thoi_diem_chot=chot,
        ket_thuc_luc=dong_ho.hien_tai(),
        so_dong=so_dong,
        chi_tieu=chi_tieu,
        ten_file=ten,
        sha256=hashlib.sha256(noi_dung).hexdigest(),
    )
    lich_su.refresh_from_db()
    return TepXuat(ten, noi_dung, lich_su)


def _json_duoc(gia_tri):
    if isinstance(gia_tri, dict):
        return {str(k): _json_duoc(v) for k, v in gia_tri.items()}
    return gia_tri
