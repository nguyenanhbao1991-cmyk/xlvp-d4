"""Điều phối một lần xuất Excel, Word hoặc PDF (REQ-GEN-15, BR-TX-01…05).

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

from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.utils import timezone

from . import bo_cuc, dong_ho, excel, in_pdf, in_word, quyen, so_lieu, trinh_bay
from .models import BanChotXuat, BoDemTrichXuat, CauHinhSo, LichSuXuat

logger = logging.getLogger(__name__)

MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MIME = {
    "xlsx": MIME_XLSX,
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}
TEN_DINH_DANG = {"xlsx": "Excel", "docx": "Word", "pdf": "PDF"}

# Giới hạn bản in Word/PDF của sổ chi tiết (BR-KY-06, XN-18).
KY_TOI_DA_IN_NGAY = 31
SO_DONG_TOI_DA_IN = 5000


class LoiXuat(Exception):
    def __init__(self, thong_bao, lich_su):
        super().__init__(thong_bao)
        self.lich_su = lich_su


class LoiGioiHan(Exception):
    """Dữ liệu vượt giới hạn của định dạng — từ chối thay vì tạo tệp bị cắt (REQ-EXP-06)."""


def kha_nang_dinh_dang():
    """{định dạng: lý do không dùng được} — rỗng nghĩa là dùng được trên máy chủ này."""
    ly_do = {}
    thieu = [p.name for p in in_pdf.tep_phong_can_co() if not p.exists()]
    if thieu:
        ly_do["pdf"] = "Thiếu phông chữ nhúng cho PDF: " + ", ".join(thieu)
    return ly_do


def kiem_tra_ky_theo_dinh_dang(dinh_nghia, ky, dinh_dang):
    if dinh_dang in ("docx", "pdf") and dinh_nghia.nhom and ky.den - ky.tu > datetime.timedelta(days=KY_TOI_DA_IN_NGAY):
        raise ValidationError(
            f"Bản {TEN_DINH_DANG[dinh_dang]} của sổ chi tiết chỉ lập cho kỳ tối đa {KY_TOI_DA_IN_NGAY} ngày. "
            "Hãy thu hẹp kỳ hoặc xuất Excel.", code="ky_qua_dai_cho_ban_in",
        )


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


def ten_file(dinh_nghia, ky, ma_trich_xuat, dinh_dang="xlsx"):
    return (f"{dinh_nghia.ma_gon}_{dinh_nghia.ten_ngan}_{ky.ngay_dau:%Y%m%d}-{ky.ngay_cuoi:%Y%m%d}_"
            f"{ma_trich_xuat}.{dinh_dang}")


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


def xuat_excel(*args, **kwargs):
    return xuat(*args, dinh_dang="xlsx", **kwargs)


def _tao_tep(ket_qua, tt, dinh_dang):
    """Trả về (nội dung, số dòng dữ liệu)."""
    if dinh_dang == "xlsx":
        if isinstance(ket_qua, so_lieu.KetQuaTongHop):
            wb, so_dong = excel.tao_so_tong_hop(ket_qua, tt)
        else:
            wb, so_dong = excel.tao_so_chi_tiet(ket_qua, tt)
        return excel.luu(wb), so_dong
    if isinstance(ket_qua, so_lieu.KetQuaSoChiTiet) and len(ket_qua.dong) > SO_DONG_TOI_DA_IN:
        raise LoiGioiHan(
            f"Sổ có {len(ket_qua.dong):,} dòng, vượt giới hạn {SO_DONG_TOI_DA_IN:,} dòng của bản "
            f"{TEN_DINH_DANG[dinh_dang]}. Hãy thu hẹp kỳ hoặc bộ lọc, hoặc xuất Excel.".replace(",", ".")
        )
    tai_lieu = bo_cuc.tao_tai_lieu(ket_qua, tt, dinh_dang)
    noi_dung = in_word.tao_docx(tai_lieu) if dinh_dang == "docx" else in_pdf.tao_pdf(tai_lieu)
    return noi_dung, tai_lieu.so_dong


def xuat(nguoi_dung, dinh_nghia, ky, bo_loc, nguoi_lap_so, du_lieu_ca_nhan_day_du=False, dia_chi_ip=None,
         dinh_dang="xlsx"):
    if dinh_dang not in MIME:
        raise ValueError(dinh_dang)
    quyen.kiem_tra_quyen_so(
        nguoi_dung, dinh_nghia, xuat=True, hien_huy=bo_loc.hien_huy, du_lieu_day_du=du_lieu_ca_nhan_day_du
    )
    cau_hinh = CauHinhSo.lay()
    bat_dau = dong_ho.hien_tai()
    lich_su = LichSuXuat.objects.create(
        ma_trich_xuat=_cap_ma(dinh_nghia, bat_dau),
        ma_so=dinh_nghia.ma,
        phien_ban_mau=dinh_nghia.phien_ban_mau,
        dinh_dang=dinh_dang,
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
            tt = trinh_bay.ThongTinXuat(
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
                chi_tieu = _json_duoc(ket_qua.chi_tieu)
            else:
                ket_qua = so_lieu.lap_so_tong_hop(nguoi_dung, dinh_nghia, ky, chot, bo_loc, nguong, thoi_diem)
                chi_tieu = {"theo_nhom": _json_duoc(ket_qua.phan_a)}
        # Tạo tệp sau khi đã đóng giao dịch đọc: số liệu đã nằm trong bộ nhớ.
        noi_dung, so_dong = _tao_tep(ket_qua, tt, dinh_dang)
        if isinstance(so_dong, dict):
            chi_tieu["so_dong_theo_phan"] = so_dong
            so_dong = sum(so_dong.values())
        if not noi_dung:
            raise excel.LoiDuLieuExcel("Tệp tạo ra rỗng.")
        ten = ten_file(dinh_nghia, ky, lich_su.ma_trich_xuat, dinh_dang)
        # Lưu bản chốt và đánh dấu thành công trong cùng một giao dịch: không bao giờ có lịch sử
        # "Thành công" mà thiếu tệp, hoặc tệp đã lưu mà lịch sử vẫn "Đang xử lý".
        with transaction.atomic():
            BanChotXuat.objects.create(
                lich_su=lich_su, noi_dung=noi_dung, kich_thuoc=len(noi_dung),
                du_lieu=du_lieu_chot(ket_qua, dinh_nghia),
            )
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
    except Exception as loi:
        logger.exception("Xuất %s thất bại (%s)", dinh_nghia.ma, lich_su.ma_trich_xuat)
        LichSuXuat.objects.filter(pk=lich_su.pk).update(
            ket_qua=LichSuXuat.KetQua.THAT_BAI,
            loi=f"{type(loi).__name__}: {loi}"[:2000],
            ket_thuc_luc=dong_ho.hien_tai(),
        )
        lich_su.refresh_from_db()
        if isinstance(loi, (excel.LoiDuLieuExcel, in_pdf.LoiTaoPdf, LoiGioiHan)):
            thong_bao = str(loi)
        else:
            thong_bao = f"Không tạo được tệp {TEN_DINH_DANG[dinh_dang]}."
        raise LoiXuat(thong_bao, lich_su) from loi

    lich_su.refresh_from_db()
    return TepXuat(ten, noi_dung, lich_su)


def _iso(gia_tri):
    return gia_tri.isoformat() if gia_tri else None


def _dong_chot(d):
    """Dữ liệu cấu trúc của một dòng — không gồm họ tên, số giấy tờ hay văn bản tự do."""
    l = d.luot
    return {
        "stt": d.stt, "ma_luot": l.pk, "trang_thai": d.trang_thai, "qua_han": d.qua_han,
        "chieu": l.chieu, "mo": _iso(l.mo_thoi_diem), "dong": _iso(l.dong_thoi_diem),
        "cong_mo": l.mo_cong.ma, "cong_dong": l.dong_cong.ma if l.dong_cong else None,
        "tu_ky_truoc": d.tu_ky_truoc, "sau_ky": d.sau_ky,
        "thoi_luong_phut": int(d.thoi_luong.total_seconds() // 60) if d.thoi_luong is not None else None,
        "thoi_luong_toi_thieu": d.thoi_luong_toi_thieu,
        "dinh_chinh": [{"n": n, "ma": dc.pk} for n, dc in d.dinh_chinh],
        "ghi_bo_sung": d.ghi_bo_sung, "chong_luot": d.chong_luot, "loi_thoi_gian": d.loi_thoi_gian,
    }


def du_lieu_chot(ket_qua, dinh_nghia):
    """Bản chốt dữ liệu riêng của lần xuất: giữ nguyên lịch sử dù dữ liệu gốc thay đổi về sau."""
    chung = {
        "ma_so": dinh_nghia.ma, "phien_ban_mau": dinh_nghia.phien_ban_mau,
        "ky": {"tu": _iso(ket_qua.ky.tu), "den": _iso(ket_qua.ky.den)}, "chot": _iso(ket_qua.chot),
        "dieu_kien_loc": _dieu_kien_loc_json(ket_qua.bo_loc),
    }
    if isinstance(ket_qua, so_lieu.KetQuaSoChiTiet):
        return {**chung, "chi_tieu": _json_duoc(ket_qua.chi_tieu), "dong": [_dong_chot(d) for d in ket_qua.dong]}
    return {
        **chung,
        "nhom": list(ket_qua.nhom),
        "phan_a": _json_duoc(ket_qua.phan_a),
        "phan_b": [{"ngay": ngay.isoformat(), **{n: list(v) for n, v in hang.items()}} for ngay, hang in ket_qua.phan_b],
        "phan_b_cuoi": {n: list(v) for n, v in ket_qua.phan_b_cuoi.items()},
        "phan_c": [{"cong": cong.ma, **{n: list(v) for n, v in so.items()}} for cong, so in ket_qua.phan_c],
        "phan_c_cuoi": {n: list(v) for n, v in ket_qua.phan_c_cuoi.items()},
        "phan_d": {n: [_dong_chot(d) for d in dong] for n, dong in ket_qua.phan_d.items()},
    }


def _json_duoc(gia_tri):
    if isinstance(gia_tri, dict):
        return {str(k): _json_duoc(v) for k, v in gia_tri.items()}
    return gia_tri
