"""Nhãn, chuỗi hiển thị và cấu hình khối ký dùng chung cho Excel, Word và PDF.

Mọi định dạng xuất lấy chữ từ đây để tên cột, nhãn chỉ tiêu, chú giải và cách
ghi thời điểm thống nhất với report_definitions.md (BR-XF-01).
"""
import datetime
import re
from dataclasses import dataclass

from django.utils import timezone
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

from ravao.models import Luot, chuan_hoa_ma

from . import quyen

TEN_NHOM = {Luot.Nhom.CBCS: "CBCS", Luot.Nhom.KHACH: "Khách", Luot.Nhom.PHUONG_TIEN: "Phương tiện"}
SO_RIENG_CUA_NHOM = {Luot.Nhom.CBCS: "SO-01", Luot.Nhom.KHACH: "SO-02", Luot.Nhom.PHUONG_TIEN: "SO-03"}

# Chú giải dùng cho Excel (cột tách riêng).
CHU_GIAI = [
    "ĐC(n) — dòng có đính chính, xem sheet Dinh_chinh mục (n).",
    "GBS — sự kiện được ghi bổ sung muộn hơn ngưỡng quy định.",
    "Chồng lượt — đối tượng có lượt mở chồng thời gian.",
    "Lỗi thời gian — thời điểm đóng sớm hơn thời điểm mở; không tính thời lượng.",
    "(từ kỳ trước) — sự kiện xảy ra trước kỳ; (sau kỳ) — sự kiện xảy ra sau thời điểm chốt.",
    "Thời lượng có “Là thời lượng tối thiểu = Có” là thời lượng tính đến thời điểm chốt của lượt chưa hoàn tất.",
]

# Chú giải cho bản in Word/PDF: chỉ in ký hiệu xuất hiện trong sổ (BR-TT-02).
CHU_GIAI_IN = {
    "ĐC": "ĐC(n) — dòng có đính chính, xem Phụ lục đính chính mục (n).",
    "GBS": "GBS — sự kiện được ghi bổ sung muộn hơn ngưỡng quy định.",
    "Chồng lượt": "Chồng lượt — đối tượng có lượt mở chồng thời gian.",
    "Lỗi thời gian": "Lỗi thời gian — thời điểm đóng sớm hơn thời điểm mở; không tính thời lượng.",
    "(từ kỳ trước)": "(từ kỳ trước) — sự kiện xảy ra trước kỳ.",
    "(sau kỳ)": "(sau kỳ) — sự kiện xảy ra sau thời điểm chốt.",
    "≥": "≥ — thời lượng tính đến thời điểm chốt của lượt chưa hoàn tất.",
    "PL": "PL-n — nội dung dài được in đầy đủ ở Phụ lục nội dung dài mục n.",
}


@dataclass
class ThongTinXuat:
    ma_trich_xuat: str
    thoi_diem_trich_xuat: datetime.datetime
    nguoi_xuat: str  # "Họ tên (tài khoản: x)"
    nguoi_lap_so: str  # rỗng = để trống, ký tay
    cau_hinh: object
    du_lieu_ca_nhan_day_du: bool = False


def lam_sach(chuoi):
    """Thay ký tự điều khiển không hợp lệ trong XML bằng U+FFFD (không âm thầm xoá)."""
    return ILLEGAL_CHARACTERS_RE.sub("�", str(chuoi))


def thoi_diem_day_du(gia_tri):
    return timezone.localtime(gia_tri).strftime("%H:%M:%S ngày %d/%m/%Y")


def thoi_diem_o(gia_tri, ky):
    """Ô thời điểm trong bảng in: ``HH:mm dd/mm`` hoặc ``dd/mm/yy`` khi kỳ qua hai năm (BR-ND-02)."""
    dia_phuong = timezone.localtime(gia_tri)
    if ky.ngay_dau.year != ky.ngay_cuoi.year:
        return dia_phuong.strftime("%H:%M %d/%m/%y")
    return dia_phuong.strftime("%H:%M %d/%m")


def thoi_luong_o(dong):
    """``hh:mm``; chưa hoàn tất ``≥ hh:mm``; lỗi thời gian ``—`` (BR-ND-05)."""
    if dong.thoi_luong is None:
        return "—"
    phut = int(dong.thoi_luong.total_seconds() // 60)
    chu = f"{phut // 60:02d}:{phut % 60:02d}"
    return f"≥ {chu}" if dong.thoi_luong_toi_thieu else chu


def mo_ta_chot(ky, chot):
    chu = f"Số liệu tính đến: {thoi_diem_day_du(chot)}"
    return chu + (" (kỳ chưa kết thúc)" if chot < ky.den else "")


def mo_ta_cong(bo_loc):
    return "Điểm kiểm soát: " + (", ".join(c.ten for c in bo_loc.cong) if bo_loc.cong else "Tất cả các cổng")


def che_so_giay_to(so):
    """Giữ 4 ký tự cuối (BR-BM-01)."""
    if not so:
        return so
    return "*" * max(len(so) - 4, 0) + so[-4:] if len(so) > 4 else "*" * len(so)


def so_giay_to_hien_thi(khach, day_du):
    if not khach.so_giay_to:
        return "Không xuất trình"
    # Che trên số đã chuẩn hoá để khoảng trắng, dấu chấm không làm lộ thêm chữ số.
    return khach.so_giay_to if day_du else che_so_giay_to(khach.so_giay_to_chuan)


def ten_nguon(pt):
    if pt.nguon == pt.Nguon.CBCS and pt.nguon_can_bo:
        return f"CBCS — {pt.nguon_can_bo.ho_ten}"
    if pt.nguon == pt.Nguon.KHACH and pt.nguon_khach:
        return f"Khách — {pt.nguon_khach.ho_ten}"
    if pt.nguon == pt.Nguon.KHAC and pt.nguon_ghi_chu:
        return f"Khác — {pt.nguon_ghi_chu}"
    return pt.get_nguon_display()


_NHAN_DOI_TUONG = {
    Luot.Nhom.CBCS: "Số CBCS duy nhất",
    Luot.Nhom.KHACH: "Số khách có định danh duy nhất",
    Luot.Nhom.PHUONG_TIEN: "Số phương tiện có biển duy nhất",
}
_NHAN_KHONG_DINH_DANH = {
    Luot.Nhom.KHACH: "Số lượt khách không định danh (không cộng vào số khách duy nhất)",
    Luot.Nhom.PHUONG_TIEN: "Số lượt phương tiện không biển (không cộng vào số phương tiện duy nhất)",
}


def dong_chi_tieu(ct, nhom):
    """Các dòng (nhãn, giá trị, đơn vị) của khối "Tổng hợp số liệu" (report_definitions.md §2.7)."""
    dong = [
        ("Số lượt trong sổ", ct["so_luot"], "lượt"),
        ("— Từ kỳ trước", ct["tu_ky_truoc"], "lượt"),
        ("— Phát sinh trong kỳ", ct["phat_sinh"], "lượt"),
        ("Hoàn tất trong kỳ", ct["hoan_tat"], "lượt"),
        ("Chưa hoàn tất tại thời điểm chốt", ct["chua_hoan_tat"], "lượt"),
        ("— Đang mở", ct["dang_mo"], "lượt"),
        ("— Hoàn tất sau kỳ", ct["hoan_tat_sau_ky"], "lượt"),
        ("— Trong đó quá hạn", ct["qua_han"], "lượt"),
        (_NHAN_DOI_TUONG[nhom], ct["doi_tuong_duy_nhat"], "đối tượng"),
    ]
    if nhom in _NHAN_KHONG_DINH_DANH:
        dong.append((_NHAN_KHONG_DINH_DANH[nhom], ct["khong_dinh_danh"], "lượt"))
    if nhom == Luot.Nhom.KHACH:
        dong += [("Số đoàn", ct["so_doan"], "đoàn"),
                 ("Thẻ khách chưa thu hồi tại thời điểm chốt", ct["the_chua_thu_hoi"], "thẻ")]
    for khoa, tieu_de in (("theo_chieu", "Theo chiều lượt"), ("theo_ly_do", "Theo lý do"),
                          ("theo_loai", "Theo loại phương tiện"), ("theo_nguon", "Theo nguồn")):
        if khoa in ct:
            dong.append((tieu_de, None, ""))
            dong += [(f"— {k}", v, "lượt") for k, v in ct[khoa].items()]
    dong += [
        ("Số lượt có đính chính", ct["luot_dinh_chinh"], "lượt"),
        ("Số bản ghi đã huỷ trong kỳ (không tính vào các chỉ tiêu trên)", ct["ban_ghi_huy"], "bản ghi"),
    ]
    return dong


def dong_can_doi(ct):
    return (f"Cân đối: Từ kỳ trước + Phát sinh = Hoàn tất + Chưa hoàn tất "
            f"({ct['tu_ky_truoc']} + {ct['phat_sinh']} = {ct['hoan_tat']} + {ct['chua_hoan_tat']})")


def doi_tuong_dinh_chinh(d):
    l = d.luot
    if l.nhom == Luot.Nhom.CBCS:
        return f"{l.can_bo.ma} {l.can_bo.ho_ten}"
    if l.nhom == Luot.Nhom.KHACH:
        return l.khach.ho_ten
    return l.phuong_tien.hien_thi_bien_so


def nhan_truong(truong):
    if truong == "khach.so_giay_to":
        return "Số giấy tờ"
    if truong == "phuong_tien.bien_so":
        return "Biển số"
    try:
        return str(Luot._meta.get_field(truong).verbose_name).capitalize()
    except Exception:
        return truong


def gia_tri_dinh_chinh(dc, cu, day_du):
    v = dc.gia_tri_cu if cu else dc.gia_tri_moi
    if dc.la_du_lieu_ca_nhan and not day_du:
        return che_so_giay_to(chuan_hoa_ma(v))
    return v


def ho_ten_tai_khoan(nguoi):
    return f"{quyen.ho_ten(nguoi)} ({nguoi.get_username()})"


# ---------------------------------------------------------------------------
# Khối ký (REQ-GEN-17, XN-14)
# ---------------------------------------------------------------------------


@dataclass
class OKy:
    chuc_danh: str
    ten: str | None  # None: dòng chấm để ký tay


@dataclass
class KhoiKy:
    dong_ngay: str
    o: list


def khoi_ky(cau_hinh, ma_so, tt):
    """Khối ký theo cấu hình đã được đơn vị phê duyệt; ``None`` nếu chưa phê duyệt.

    Chưa có phê duyệt thì không in khối ký nào — kể cả mẫu mặc định — để bản xuất
    không thể hiện một quy trình ký chưa được đơn vị chấp nhận.
    """
    if not cau_hinh.khoi_ky_da_phe_duyet:
        return None
    cac_o = []
    for muc in cau_hinh.o_ky or []:
        if muc.get("ap_dung") and ma_so not in muc["ap_dung"]:
            continue
        ten = (tt.nguoi_lap_so or None) if muc.get("nguoi_lap_so") else None
        cac_o.append(OKy(muc["chuc_danh"].upper(), ten))
    if not cac_o:
        return None
    dia_danh = cau_hinh.dia_danh or "..........."
    if cau_hinh.dien_san_ngay_ky:
        ngay = timezone.localtime(tt.thoi_diem_trich_xuat)
        dong_ngay = f"{dia_danh}, ngày {ngay.day:02d} tháng {ngay.month:02d} năm {ngay.year}"
    else:
        dong_ngay = f"{dia_danh}, ngày ..... tháng ..... năm .........."
    return KhoiKy(dong_ngay, cac_o)


def kiem_tra_o_ky(o_ky):
    """Kiểm tra cấu trúc cấu hình ô ký; trả về danh sách lỗi."""
    loi = []
    if not isinstance(o_ky, list):
        return ["Cấu hình ô ký phải là danh sách."]
    for i, muc in enumerate(o_ky, 1):
        if not isinstance(muc, dict) or not str(muc.get("chuc_danh", "")).strip():
            loi.append(f"Ô ký {i}: thiếu chức danh.")
            continue
        thua = set(muc) - {"chuc_danh", "nguoi_lap_so", "ap_dung"}
        if thua:
            loi.append(f"Ô ký {i}: khoá không hợp lệ {sorted(thua)}.")
        ap_dung = muc.get("ap_dung", [])
        if not isinstance(ap_dung, list) or any(not re.fullmatch(r"SO-0[1-4]", str(m)) for m in ap_dung):
            loi.append(f"Ô ký {i}: “ap_dung” phải là danh sách mã sổ SO-01…SO-04.")
    return loi
