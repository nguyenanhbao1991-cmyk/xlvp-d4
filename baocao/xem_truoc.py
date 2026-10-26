"""Xem trước sổ trên màn hình "Xuất sổ theo dõi" (BR-TX-06).

Xem trước dùng cùng hàm số liệu với bản xuất nhưng KHÔNG phải dữ liệu đã chốt: không cấp mã
trích xuất, không ghi lịch sử, không lưu bản chốt. Khi xuất, số liệu được tính lại trong giao
dịch đọc nhất quán; bản chốt là bản được lưu lúc đó.
"""
import datetime
from dataclasses import dataclass, field

from . import bo_cuc, dong_ho, quyen, so_lieu, trinh_bay
from .dich_vu import KY_TOI_DA_IN_NGAY, SO_DONG_TOI_DA_IN, TEN_DINH_DANG
from .models import CauHinhSo

SO_DONG_HIEN_THI = 50


@dataclass
class XemTruoc:
    dinh_nghia: object
    ky: object
    chot: datetime.datetime
    thoi_diem: datetime.datetime
    bo_loc: object
    so_dong: int  # bằng số dòng dữ liệu của tệp nếu xuất cùng điều kiện, cùng thời điểm
    cot: list = field(default_factory=list)
    dong: list = field(default_factory=list)  # [(lớp css, [list dòng chữ của từng ô])]
    chi_tieu: list = field(default_factory=list)  # [(nhãn, giá trị, đơn vị)]
    tong_hop: object = None
    so_dong_theo_phan: dict | None = None
    canh_bao: list = field(default_factory=list)

    @property
    def con_lai(self):
        return max(self.so_dong - len(self.dong), 0)

    @property
    def mo_ta_chot(self):
        return trinh_bay.mo_ta_chot(self.ky, self.chot)


def lap(nguoi_dung, dinh_nghia, ky, bo_loc, du_lieu_day_du=False, dinh_dang="xlsx"):
    # Xem trước chỉ cần quyền xem; quyền xuất được kiểm tra khi xuất.
    quyen.kiem_tra_quyen_so(nguoi_dung, dinh_nghia, hien_huy=bo_loc.hien_huy, du_lieu_day_du=du_lieu_day_du)
    cau_hinh = CauHinhSo.lay()
    thoi_diem = dong_ho.hien_tai()
    chot = min(ky.den, thoi_diem)
    nguong = datetime.timedelta(minutes=cau_hinh.nguong_ghi_bo_sung_phut)
    xt = XemTruoc(dinh_nghia, ky, chot, thoi_diem, bo_loc, 0)

    if dinh_nghia.nhom:
        kq = so_lieu.lap_so_chi_tiet(nguoi_dung, dinh_nghia, ky, chot, bo_loc, nguong, thoi_diem)
        cot, ham_dong = bo_cuc.cot_va_o(dinh_nghia.nhom, du_lieu_day_du, ky, bo_cuc.PhuLucNoiDungDai())
        xt.cot = [c.tieu_de for c in cot]
        for d in kq.dong[:SO_DONG_HIEN_THI]:
            lop = {so_lieu.MO: "chua-hoan-tat", so_lieu.HUY: "da-huy"}.get(d.trang_thai, "")
            xt.dong.append((lop, ["\n".join(o.dong) for o in ham_dong(d)]))
        xt.so_dong = len(kq.dong)
        xt.chi_tieu = trinh_bay.dong_chi_tieu(kq.chi_tieu, dinh_nghia.nhom)
        if dinh_dang in ("docx", "pdf"):
            if ky.den - ky.tu > datetime.timedelta(days=KY_TOI_DA_IN_NGAY):
                xt.canh_bao.append(f"Kỳ dài hơn {KY_TOI_DA_IN_NGAY} ngày: bản {TEN_DINH_DANG[dinh_dang]} sẽ bị từ "
                                   "chối, chỉ xuất được Excel.")
            if xt.so_dong > SO_DONG_TOI_DA_IN:
                xt.canh_bao.append(f"Sổ có {xt.so_dong} dòng, vượt giới hạn {SO_DONG_TOI_DA_IN} dòng của bản "
                                   f"{TEN_DINH_DANG[dinh_dang]}: chỉ xuất được Excel.")
    else:
        kq = so_lieu.lap_so_tong_hop(nguoi_dung, dinh_nghia, ky, chot, bo_loc, nguong, thoi_diem)
        xt.tong_hop = kq
        # Cùng cách đếm với bản xuất (excel.tao_so_tong_hop, bo_cuc.tai_lieu_tong_hop).
        xt.so_dong_theo_phan = {"A": len(kq.nhom), "B": len(kq.phan_b), "C": len(kq.phan_c),
                                "D": sum(len(kq.phan_d[n]) for n in kq.nhom), "E": len(kq.nhom)}
        xt.so_dong = sum(xt.so_dong_theo_phan.values())
    return xt
