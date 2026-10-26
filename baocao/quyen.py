"""Kiểm tra quyền và giới hạn phạm vi dữ liệu của các sổ (REQ-GEN-19, REQ-GEN-20).

Mọi truy vấn lấy dữ liệu cho sổ phải đi qua ``pham_vi_luot`` sau khi đã gọi
``kiem_tra_quyen_so``.
"""
from dataclasses import dataclass

from django.core.exceptions import PermissionDenied
from django.db.models import Q

from ravao.models import Luot, PhanCongCong


@dataclass(frozen=True)
class DinhNghiaSo:
    ma: str  # SO-01
    ma_gon: str  # SO01
    duong_dan: str
    ten: str
    ten_ngan: str
    nhom: str | None  # None với sổ tổng hợp
    quyen_xem: str
    quyen_xuat: str


SO = {
    d.ma: d
    for d in [
        DinhNghiaSo("SO-01", "SO01", "cbcs", "SỔ THEO DÕI CBCS RA/VÀO", "CBCS", Luot.Nhom.CBCS,
                    "ravao.xem_so_cbcs", "ravao.xuat_so_cbcs"),
        DinhNghiaSo("SO-02", "SO02", "khach", "SỔ THEO DÕI KHÁCH RA/VÀO", "Khach", Luot.Nhom.KHACH,
                    "ravao.xem_so_khach", "ravao.xuat_so_khach"),
        DinhNghiaSo("SO-03", "SO03", "phuong-tien", "SỔ THEO DÕI PHƯƠNG TIỆN RA/VÀO", "PhuongTien",
                    Luot.Nhom.PHUONG_TIEN, "ravao.xem_so_phuong_tien", "ravao.xuat_so_phuong_tien"),
        DinhNghiaSo("SO-04", "SO04", "tong-hop", "SỔ TỔNG HỢP RA/VÀO", "TongHop", None,
                    "ravao.xem_so_tong_hop", "ravao.xuat_so_tong_hop"),
    ]
}
SO_THEO_DUONG_DAN = {d.duong_dan: d for d in SO.values()}
SO_THEO_NHOM = {d.nhom: d for d in SO.values() if d.nhom}

QUYEN_XEM_HUY = "ravao.xem_ban_ghi_huy"
QUYEN_DU_LIEU_CA_NHAN = "ravao.xem_du_lieu_ca_nhan_day_du"
QUYEN_MOI_CONG = "ravao.xem_moi_cong"


def ho_ten(nguoi_dung):
    """Họ tên theo thứ tự tiếng Việt: họ và tên đệm (last_name) rồi tên (first_name)."""
    return f"{nguoi_dung.last_name} {nguoi_dung.first_name}".strip() or nguoi_dung.get_username()


def kiem_tra_quyen_so(nguoi_dung, dinh_nghia, xuat=False, hien_huy=False, du_lieu_day_du=False):
    if not nguoi_dung.is_authenticated or not nguoi_dung.is_active:
        raise PermissionDenied("Chưa đăng nhập.")
    if not nguoi_dung.has_perm(dinh_nghia.quyen_xem):
        raise PermissionDenied(f"Không có quyền xem {dinh_nghia.ma}.")
    if xuat and not nguoi_dung.has_perm(dinh_nghia.quyen_xuat):
        raise PermissionDenied(f"Không có quyền xuất {dinh_nghia.ma}.")
    if hien_huy and not nguoi_dung.has_perm(QUYEN_XEM_HUY):
        raise PermissionDenied("Không có quyền xem bản ghi đã huỷ.")
    if du_lieu_day_du and not nguoi_dung.has_perm(QUYEN_DU_LIEU_CA_NHAN):
        raise PermissionDenied("Không có quyền xuất dữ liệu cá nhân đầy đủ.")


def duoc_xem_chi_tiet_nhom(nguoi_dung, nhom):
    """Người dùng có được thấy định danh đối tượng của nhóm này không (SO-04 Phần D)."""
    return nguoi_dung.has_perm(SO_THEO_NHOM[nhom].quyen_xem)


def pham_vi_luot(nguoi_dung, nhom):
    """Truy vấn lượt của một nhóm trong phạm vi cổng người dùng được phép."""
    qs = Luot.objects.filter(nhom=nhom)
    if not nguoi_dung.has_perm(QUYEN_MOI_CONG):
        cong = PhanCongCong.objects.filter(nguoi_dung=nguoi_dung).values("cong_id")
        qs = qs.filter(Q(mo_cong__in=cong) | Q(dong_cong__in=cong))
    return qs
