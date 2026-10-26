"""Bố cục bản in (Word, PDF) dựng từ kết quả số liệu (report_definitions.md §2–§7).

Lớp này không phụ thuộc thư viện tạo tệp: nó tạo ra một ``TaiLieu`` gồm các
khối (đoạn văn, bảng, khối ký...) mà ``in_word`` và ``in_pdf`` vẽ lại. Nhờ đó
tên cột, nội dung ô, thứ tự dòng và chỉ tiêu của hai định dạng luôn trùng nhau.
"""
from dataclasses import dataclass

from django.utils import timezone

from ravao.models import Luot

from . import so_lieu, trinh_bay
from .so_lieu import HUY, MO

# Lề trang (BR-IN-02, XN-15).
LE_TREN_MM, LE_DUOI_MM, LE_TRAI_MM, LE_PHAI_MM = 15, 15, 20, 15
# Khổ giấy thử lần lượt: cái đầu tiên đủ rộng cho tổng độ rộng tối thiểu của các cột được chọn.
KHO_GIAY = [("A4", "doc", 210, 297), ("A4", "ngang", 297, 210), ("A3", "ngang", 420, 297)]
# Nội dung dài hơn ngưỡng này không đặt trọn trong ô mà in đầy đủ ở phụ lục, để một dòng
# bảng không cao quá một trang (BR-IN-09) và không phải cắt dữ liệu.
NGUONG_NOI_DUNG_DAI = 300
SO_KY_TU_TRICH = 100


def rong_vung_in(kho, huong):
    for k, h, rong, _cao in KHO_GIAY:
        if (k, h) == (kho, huong):
            return rong - LE_TRAI_MM - LE_PHAI_MM
    raise ValueError((kho, huong))


def chon_kho_giay(*bang):
    """Chọn khổ và hướng giấy theo số cột và độ rộng tối thiểu của bảng rộng nhất."""
    can = max((sum(c.toi_thieu_mm for c in b.cot) for b in bang), default=0)
    for kho, huong, rong, _cao in KHO_GIAY:
        if rong - LE_TRAI_MM - LE_PHAI_MM >= can:
            return kho, huong
    return KHO_GIAY[-1][:2]


# ---------------------------------------------------------------------------
# Các khối
# ---------------------------------------------------------------------------


@dataclass
class O:
    """Một ô: các dòng chữ, in đậm, đoạn cần nhấn mạnh (đậm, gạch chân), căn lề."""

    dong: list
    dam: bool = False
    nhan_manh: str = ""
    can: str = "trai"
    nghieng: bool = False
    co_chu_dong_sau: float | None = None  # cỡ chữ riêng cho dòng thứ hai trở đi (ví dụ mã lượt)


@dataclass
class CotIn:
    tieu_de: str
    ty_le: float
    toi_thieu_mm: float
    can: str = "trai"


@dataclass
class Bang:
    cot: list
    dong: list  # list[list[O]]
    nhom_tieu_de: list | None = None  # [(nhãn, số cột gộp)] — tiêu đề tầng trên
    co_tieu_de: bool = True
    khung: bool = True
    co_chu: float = 9.5
    ten: str = ""  # để kiểm thử nhận diện bảng

    @property
    def so_hang_tieu_de(self):
        return (1 if self.nhom_tieu_de else 0) + (1 if self.co_tieu_de else 0)


@dataclass
class Doan:
    chu: str
    kieu: str = "thuong"  # ten_so, giua, thuong, nghieng, muc, nho, dam, phai


@dataclass
class GiuCung:
    """Các khối phải nằm cùng trang (ví dụ thông tin trích xuất và khối ký)."""

    khoi: list


@dataclass
class Phan:
    khoi: list
    kho: str
    huong: str


@dataclass
class TaiLieu:
    phan: list
    dau_trang_rut_gon: str
    chan_trang: str
    tieu_de: str
    tac_gia: str
    chu_de: str
    so_dong: object = 0


class PhuLucNoiDungDai:
    def __init__(self):
        self.muc = []  # (n, stt, mã lượt, tên cột, nội dung)

    def o(self, chu, d, ten_cot):
        chu = trinh_bay.lam_sach(chu or "")
        if len(chu) <= NGUONG_NOI_DUNG_DAI:
            return chu
        n = len(self.muc) + 1
        self.muc.append((n, d.stt, d.luot.pk, ten_cot, chu))
        return f"{chu[:SO_KY_TU_TRICH].rstrip()}… (đầy đủ: PL-{n})"


def _ky_rut_gon(ky):
    if ky.ngay_dau == ky.ngay_cuoi:
        return f"{ky.ngay_dau:%d/%m/%Y}"
    return f"{ky.ngay_dau:%d/%m/%Y}–{ky.ngay_cuoi:%d/%m/%Y}"


def _dau_so(dn, ky, chot, bo_loc, tt, dong_them=()):
    """Khối đầu sổ (report_definitions.md §2.3)."""
    ch = tt.cau_hinh
    dau = Bang(
        cot=[CotIn("", 68, 0), CotIn("", 32, 0, "phai")],
        dong=[
            [O([ch.co_quan_chu_quan.upper()]), O([f"Mã sổ: {dn.ma}"], can="phai")],
            [O([ch.ten_don_vi.upper()], dam=True), O([f"Mẫu nội bộ — phiên bản {dn.phien_ban_mau}"], can="phai")],
        ],
        co_tieu_de=False, khung=False, co_chu=10, ten="dau_so",
    )
    loc = bo_loc.mo_ta()
    khoi = [
        dau,
        Doan(dn.ten, "ten_so"),
        Doan(ky.mo_ta(), "giua"),
        Doan(trinh_bay.mo_ta_cong(bo_loc) + " · Điều kiện lọc: " + ("; ".join(loc) if loc else "Không")),
        Doan(trinh_bay.mo_ta_chot(ky, chot)),
        Doan(f"Thời điểm trích xuất: {trinh_bay.thoi_diem_day_du(tt.thoi_diem_trich_xuat)} (giờ máy chủ) · "
             f"Mã trích xuất: {tt.ma_trich_xuat}"),
        Doan(f"Người xuất: {tt.nguoi_xuat} · Người lập sổ: {tt.nguoi_lap_so or '(để trống — ký tay)'}"),
    ]
    them = list(dong_them)
    if bo_loc.co_loc:
        them.insert(0, "Sổ đã lọc — không phải toàn bộ dữ liệu của kỳ.")
    if bo_loc.hien_huy:
        them.append("Có hiển thị bản ghi đã huỷ (không tính vào số liệu).")
    khoi += [Doan(chu, "nghieng") for chu in them]
    return khoi


def _chan_trang(dn, tt, dinh_dang):
    chu = (f"{dn.ma} · Mã trích xuất {tt.ma_trich_xuat} · Trích xuất lúc "
           f"{timezone.localtime(tt.thoi_diem_trich_xuat):%H:%M:%S %d/%m/%Y} · Mẫu nghiệp vụ nội bộ")
    if dinh_dang == "docx":
        chu += " · Bản xuất để biên tập"  # XN-17
    return chu


def _khoi_ket_thuc(dn, ky, chot, tt, dinh_dang, them=()):
    """Thông tin trích xuất + khối ký (nếu đã phê duyệt) + "Hết sổ", giữ cùng trang (BR-IN-09)."""
    khoi = [
        Doan("THÔNG TIN TRÍCH XUẤT", "muc"),
        Doan(f"Mã trích xuất: {tt.ma_trich_xuat} · Định dạng: {'Word (.docx)' if dinh_dang == 'docx' else 'PDF'}"),
        Doan(f"Thời điểm trích xuất: {trinh_bay.thoi_diem_day_du(tt.thoi_diem_trich_xuat)} (giờ máy chủ)"),
        Doan(f"Người xuất: {tt.nguoi_xuat}"),
        Doan(f"Người lập sổ: {tt.nguoi_lap_so or '(để trống — ký tay)'}"),
        Doan(f"Kỳ: {ky.mo_ta()} — {trinh_bay.mo_ta_chot(ky, chot)}"),
        *[Doan(chu) for chu in them],
        Doan("Số liệu phản ánh dữ liệu đã ghi nhận trong hệ thống tại thời điểm trích xuất. "
             "Số sau dấu # là mã lượt để đối chiếu với bản ghi gốc.", "nho"),
    ]
    if dinh_dang == "docx":
        khoi.append(Doan("Bản xuất để biên tập: nội dung có thể đã được chỉnh sửa sau khi xuất; "
                         "đối chiếu bản PDF hoặc hệ thống khi cần.", "nho"))
    ky_ten = trinh_bay.khoi_ky(tt.cau_hinh, dn.ma, tt)
    if ky_ten:
        khoi.append(ky_ten)
    khoi.append(Doan("— Hết sổ —", "giua"))
    return GiuCung(khoi)


# ---------------------------------------------------------------------------
# Sổ chi tiết
# ---------------------------------------------------------------------------


def _o_su_kien(d, loai, ky):
    sk = d.su_kien(loai)
    if sk.thoi_diem is None:
        return O(["—"], can="giua")
    dong = [trinh_bay.thoi_diem_o(sk.thoi_diem, ky)]
    if sk.cong:
        dong.append(sk.cong.ten)
    if sk.chu_thich:
        dong.append(sk.chu_thich)
    return O(dong)


def _o_nguoi_ghi(d, thu_tu):
    dong = []
    for loai, ky_tu in thu_tu:
        nguoi = d.su_kien(loai).nguoi_ghi
        if nguoi:
            dong.append(f"{ky_tu}: {so_lieu.nguoi_ghi_hien_thi(nguoi)}")
    return O(dong or ["—"])


def cot_va_o(nhom, du_lieu_day_du, ky, pl):
    """(cột in, hàm dòng → list[O]) theo report_definitions.md §3.4, §4.4, §5.4."""
    def stt(d):
        # Mã lượt in nhỏ để mã nhiều chữ số không bị ngắt giữa chừng trong cột hẹp.
        return O([str(d.stt) if d.stt is not None else "—", f"#{d.luot.pk}"], can="giua", co_chu_dong_sau=7.5)

    def thoi_luong(d):
        return O([trinh_bay.thoi_luong_o(d)], can="phai")

    def trang_thai(d):
        return O([d.nhan_trang_thai], nhan_manh="Quá hạn" if d.qua_han else "")

    def ghi_chu(d):
        return O([pl.o(d.ky_hieu, d, "Ghi chú")] if d.ky_hieu else [""])

    def han(d, nhan):
        return [f"{nhan} {trinh_bay.thoi_diem_o(d.luot.han_du_kien, ky)}"] if d.luot.han_du_kien else []

    if nhom == Luot.Nhom.CBCS:
        cot = [
            CotIn("STT", 6, 15, "giua"), CotIn("Mã CBCS", 6, 14), CotIn("Họ và tên", 11, 22),
            CotIn("Đơn vị / bộ phận", 9, 18), CotIn("Chiều lượt", 6, 14), CotIn("Ra", 9, 20),
            CotIn("Vào", 9, 20), CotIn("Thời lượng\n(giờ:phút)", 5, 13, "phai"), CotIn("Lý do / nội dung", 10, 20),
            CotIn("Phương tiện đi kèm", 8, 18), CotIn("Người ghi nhận", 8, 18), CotIn("Trạng thái", 7, 17),
            CotIn("Ghi chú", 6, 13),
        ]

        def dong(d):
            l = d.luot
            cb = l.can_bo
            ly_do = ": ".join(x for x in (l.ly_do, l.ly_do_chi_tiet) if x)
            return [
                stt(d), O([cb.ma]),
                O([cb.ho_ten] + ([", ".join(x for x in (cb.cap_bac, cb.chuc_vu) if x)] if cb.cap_bac or cb.chuc_vu else [])),
                O([cb.don_vi.ten]), O([l.get_chieu_display()]),
                _o_su_kien(d, "RA", ky), _o_su_kien(d, "VAO", ky), thoi_luong(d),
                O(([pl.o(ly_do, d, "Lý do / nội dung")] if ly_do else ["—"]) + han(d, "Hạn về")),
                O([l.phuong_tien_di_kem.hien_thi_bien_so if l.phuong_tien_di_kem else "—"]),
                _o_nguoi_ghi(d, [("RA", "R"), ("VAO", "V")]), trang_thai(d), ghi_chu(d),
            ]
        return cot, dong

    if nhom == Luot.Nhom.KHACH:
        cot = [
            CotIn("STT", 6, 15, "giua"), CotIn("Khách", 13, 26), CotIn("Giấy tờ", 9, 22), CotIn("Mục đích", 9, 18),
            CotIn("Người / bộ phận tiếp", 10, 20), CotIn("Số thẻ", 4, 11), CotIn("Vào", 9, 20), CotIn("Ra", 9, 20),
            CotIn("Thời lượng\n(giờ:phút)", 5, 13, "phai"), CotIn("Phương tiện", 6, 15),
            CotIn("Người ghi nhận", 7, 18), CotIn("Trạng thái", 7, 17), CotIn("Ghi chú", 6, 14),
        ]

        def dong(d):
            l, k = d.luot, d.luot.khach
            giay_to = trinh_bay.so_giay_to_hien_thi(k, du_lieu_day_du)
            if k.so_giay_to and k.loai_giay_to:
                giay_to = f"{k.loai_giay_to} {giay_to}"
            return [
                stt(d),
                O([k.ho_ten] + ([pl.o(k.co_quan, d, "Khách")] if k.co_quan else [])
                  + ([f"Đoàn {l.ma_doan}"] if l.ma_doan else [])),
                O([giay_to]), O([pl.o(l.muc_dich, d, "Mục đích") or "—"]), O([pl.o(l.nguoi_tiep, d, "Người tiếp") or "—"]),
                O([l.so_the or "—"]), _o_su_kien(d, "VAO", ky), _o_su_kien(d, "RA", ky), thoi_luong(d),
                O([l.phuong_tien_di_kem.hien_thi_bien_so if l.phuong_tien_di_kem else "—"]),
                _o_nguoi_ghi(d, [("VAO", "V"), ("RA", "R")]), trang_thai(d), ghi_chu(d),
            ]
        return cot, dong

    cot = [
        CotIn("STT", 6, 15, "giua"), CotIn("Biển số", 8, 19), CotIn("Loại phương tiện", 7, 16), CotIn("Nguồn", 8, 18),
        CotIn("Người điều khiển", 11, 20), CotIn("Chiều lượt", 6, 14), CotIn("Ra", 9, 20), CotIn("Vào", 9, 20),
        CotIn("Thời lượng\n(giờ:phút)", 5, 13, "phai"), CotIn("Lý do / lệnh điều xe", 10, 20),
        CotIn("Người ghi nhận", 7, 18), CotIn("Trạng thái", 7, 17), CotIn("Ghi chú", 7, 14),
    ]

    def dong(d):
        l, pt = d.luot, d.luot.phuong_tien
        return [
            stt(d), O([pt.hien_thi_bien_so]), O([pt.loai]), O([trinh_bay.ten_nguon(pt)]),
            O([so_lieu.ten_can_bo(l.nguoi_dieu_khien_can_bo) or l.nguoi_dieu_khien or "—"]),
            O([l.get_chieu_display()]), _o_su_kien(d, "RA", ky), _o_su_kien(d, "VAO", ky), thoi_luong(d),
            O(([pl.o(l.ly_do, d, "Lý do")] if l.ly_do else ["—"])
              + ([f"Lệnh: {l.lenh_dieu_xe}"] if l.lenh_dieu_xe else []) + han(d, "Hạn về")),
            _o_nguoi_ghi(d, [("RA", "R"), ("VAO", "V")]), trang_thai(d), ghi_chu(d),
        ]
    return cot, dong


def _ky_hieu_xuat_hien(dong, pl):
    co = set()
    for d in dong:
        if d.dinh_chinh:
            co.add("ĐC")
        if d.ghi_bo_sung:
            co.add("GBS")
        if d.chong_luot:
            co.add("Chồng lượt")
        if d.loi_thoi_gian:
            co.add("Lỗi thời gian")
        if d.tu_ky_truoc:
            co.add("(từ kỳ trước)")
        if d.sau_ky:
            co.add("(sau kỳ)")
        if d.thoi_luong_toi_thieu and d.trang_thai != HUY:
            co.add("≥")
    if pl.muc:
        co.add("PL")
    return [chu for khoa, chu in trinh_bay.CHU_GIAI_IN.items() if khoa in co]


def _bang_chi_tieu(dong_ct, ten):
    return Bang(
        cot=[CotIn("Chỉ tiêu", 70, 80), CotIn("Số liệu", 15, 20, "phai"), CotIn("Đơn vị tính", 15, 20)],
        dong=[[O([nhan], dam=gia_tri is None), O(["" if gia_tri is None else f"{gia_tri:,}".replace(",", ".")],
                                                   can="phai"), O([don_vi])]
              for nhan, gia_tri, don_vi in dong_ct],
        ten=ten,
    )


def _phu_luc_dinh_chinh(ket_qua, tt):
    if not ket_qua.phu_luc:
        return [Doan("PHỤ LỤC ĐÍNH CHÍNH", "muc"), Doan("Không có đính chính.")]
    day_du = tt.du_lieu_ca_nhan_day_du
    bang = Bang(
        cot=[CotIn("(n)", 4, 9, "giua"), CotIn("STT dòng", 5, 11, "giua"), CotIn("Mã lượt", 6, 13),
             CotIn("Đối tượng", 14, 26), CotIn("Trường", 10, 20), CotIn("Giá trị cũ", 11, 22),
             CotIn("Giá trị mới", 11, 22), CotIn("Lý do", 15, 26), CotIn("Người đính chính", 12, 24),
             CotIn("Thời điểm đính chính", 12, 22)],
        dong=[
            [O([f"({n})"], can="giua"), O([str(stt) if stt is not None else "— (đã huỷ)"], can="giua"),
             O([f"#{d.luot.pk}"]), O([trinh_bay.doi_tuong_dinh_chinh(d)]), O([trinh_bay.nhan_truong(dc.truong)]),
             O([trinh_bay.lam_sach(trinh_bay.gia_tri_dinh_chinh(dc, True, day_du))]),
             O([trinh_bay.lam_sach(trinh_bay.gia_tri_dinh_chinh(dc, False, day_du))]),
             O([trinh_bay.lam_sach(dc.ly_do)]), O([trinh_bay.ho_ten_tai_khoan(dc.nguoi)]),
             O([trinh_bay.thoi_diem_day_du(dc.thoi_diem)])]
            for n, stt, d, dc in ket_qua.phu_luc
        ],
        co_chu=9, ten="phu_luc_dinh_chinh",
    )
    return [Doan("PHỤ LỤC ĐÍNH CHÍNH", "muc"), bang]


def _phu_luc_noi_dung_dai(pl):
    if not pl.muc:
        return []
    khoi = [Doan("PHỤ LỤC NỘI DUNG DÀI", "muc"),
            Doan("Nội dung vượt quá sức chứa của một ô được in đầy đủ dưới đây; ô trong bảng ghi phần đầu "
                 "và số phụ lục.", "nho")]
    for n, stt, ma, ten_cot, chu in pl.muc:
        khoi.append(Doan(f"PL-{n} — dòng {stt if stt is not None else '— (đã huỷ)'}, mã lượt #{ma}, cột {ten_cot}:",
                         "dam"))
        khoi.append(Doan(chu))
    return khoi


def tai_lieu_chi_tiet(ket_qua, tt, dinh_dang):
    dn, ky, chot = ket_qua.dinh_nghia, ket_qua.ky, ket_qua.chot
    pl = PhuLucNoiDungDai()
    cot, ham_dong = cot_va_o(dn.nhom, tt.du_lieu_ca_nhan_day_du, ky, pl)
    dong = []
    for d in ket_qua.dong:
        cac_o = ham_dong(d)
        if d.trang_thai == MO:  # Lượt chưa hoàn tất in đậm toàn dòng (BR-TT-04).
            for o in cac_o:
                o.dam = True
        if d.trang_thai == HUY:
            for o in cac_o:
                o.nghieng = True
        dong.append(cac_o)
    bang = Bang(cot=cot, dong=dong, ten="bang_luot")
    kho, huong = chon_kho_giay(bang)

    them = []
    if dn.nhom == Luot.Nhom.KHACH:
        them.append("Dữ liệu cá nhân: " + ("hiển thị đầy đủ" if tt.du_lieu_ca_nhan_day_du else "số giấy tờ đã che"))
    khoi = _dau_so(dn, ky, chot, ket_qua.bo_loc, tt, them)
    khoi.append(bang if dong else Doan("Không có lượt nào trong kỳ theo điều kiện đã chọn.", "nghieng"))
    if not dong:
        khoi.insert(len(khoi) - 1, Bang(cot=cot, dong=[], ten="bang_luot"))

    ct = ket_qua.chi_tieu
    khoi += [
        Doan(f"TỔNG HỢP SỐ LIỆU (tại thời điểm chốt {trinh_bay.thoi_diem_day_du(chot)})", "muc"),
        _bang_chi_tieu(trinh_bay.dong_chi_tieu(ct, dn.nhom), "tong_hop_so_lieu"),
        Doan(trinh_bay.dong_can_doi(ct), "nho"),
    ]
    if ket_qua.bo_loc.co_loc:
        khoi.append(Doan("Số liệu theo điều kiện lọc đã nêu ở đầu sổ.", "nho"))
    chu_giai = _ky_hieu_xuat_hien(ket_qua.dong, pl)
    if chu_giai:
        khoi += [Doan("CHÚ GIẢI KÝ HIỆU", "muc")] + [Doan(chu, "nho") for chu in chu_giai]
    khoi += _phu_luc_dinh_chinh(ket_qua, tt)
    khoi += _phu_luc_noi_dung_dai(pl)
    khoi.append(_khoi_ket_thuc(dn, ky, chot, tt, dinh_dang))
    return TaiLieu(
        phan=[Phan(khoi, kho, huong)],
        dau_trang_rut_gon=f"{tt.cau_hinh.ten_don_vi.upper()} — {dn.ten} — {_ky_rut_gon(ky)}",
        chan_trang=_chan_trang(dn, tt, dinh_dang),
        tieu_de=f"{dn.ten} — {ky.mo_ta()}",
        tac_gia=tt.nguoi_xuat,
        chu_de=tt.ma_trich_xuat,
        so_dong=len(ket_qua.dong),
    )


# ---------------------------------------------------------------------------
# Sổ tổng hợp
# ---------------------------------------------------------------------------


def _so(gia_tri, dam=False):
    chu = "—" if gia_tri is None else f"{gia_tri:,}".replace(",", ".")
    return O([chu], can="phai", dam=dam)


def tai_lieu_tong_hop(ket_qua, tt, dinh_dang):
    dn, ky, chot = ket_qua.dinh_nghia, ket_qua.ky, ket_qua.chot
    nhom = ket_qua.nhom
    ten = trinh_bay.TEN_NHOM
    phan = []  # (khối, các bảng quyết định khổ giấy)

    # A — không có dòng tổng cộng giữa các nhóm (BR-TONG-04).
    bang_a = Bang(
        cot=[CotIn("Nhóm đối tượng", 12, 20), CotIn("Từ kỳ trước (lượt)", 8, 13, "phai"),
             CotIn("Phát sinh trong kỳ (lượt)", 8, 13, "phai"), CotIn("Hoàn tất trong kỳ (lượt)", 8, 13, "phai"),
             CotIn("Chưa hoàn tất tại thời điểm chốt (lượt)", 9, 15, "phai"),
             CotIn("Trong đó quá hạn (lượt)", 8, 13, "phai"), CotIn("Không định danh (lượt)", 8, 13, "phai"),
             CotIn("Có đính chính (lượt)", 8, 13, "phai"), CotIn("Duy nhất, có định danh (đối tượng)", 10, 15, "phai"),
             CotIn("Bản ghi đã huỷ, không tính (bản ghi)", 10, 15, "phai"), CotIn("Sổ riêng", 7, 12)],
        dong=[[O([ten[n]]), _so(a["tu_ky_truoc"]), _so(a["phat_sinh"]), _so(a["hoan_tat"]), _so(a["chua_hoan_tat"]),
               _so(a["qua_han"]), _so(a["khong_dinh_danh"]), _so(a["luot_dinh_chinh"]), _so(a["doi_tuong_duy_nhat"]),
               _so(a["ban_ghi_huy"]), O([trinh_bay.SO_RIENG_CUA_NHOM[n]])]
              for n in nhom for a in [ket_qua.phan_a[n]]],
        nhom_tieu_de=[("", 1), ("SỐ LƯỢT", 7), ("SỐ ĐỐI TƯỢNG", 1), ("", 2)],
        co_chu=9, ten="phan_a",
    )
    phan.append(([Doan("A. CHỈ TIÊU THEO NHÓM ĐỐI TƯỢNG", "muc"),
                  Doan("Số liệu của từng nhóm đối tượng được tính riêng và không cộng gộp giữa các nhóm.", "nghieng"),
                  bang_a, Doan("(Không có dòng tổng cộng giữa các nhóm.)", "nho")], [bang_a]))

    # B — theo ngày (BR-TONG-07).
    cot_b = [CotIn("Ngày", 14, 22)]
    for n in nhom:
        cot_b += [CotIn(f"{ten[n]} — lượt phát sinh (lượt)", 10, 18, "phai"),
                  CotIn(f"{ten[n]} — có hoạt động (đối tượng)", 10, 18, "phai")]
    dong_b = [[O([f"{ngay:%d/%m/%Y}"])] + [o for n in nhom for o in (_so(hang[n][0]), _so(hang[n][1]))]
              for ngay, hang in ket_qua.phan_b]
    dong_b.append([O(["Cộng / Duy nhất cả kỳ"], dam=True)]
                  + [o for n in nhom for o in (_so(ket_qua.phan_b_cuoi[n][0], True), _so(ket_qua.phan_b_cuoi[n][1], True))])
    bang_b = Bang(cot=cot_b, dong=dong_b, co_chu=9, ten="phan_b")
    phan.append(([Doan("B. PHÂN BỔ THEO NGÀY", "muc"),
                  Doan("Cột “có hoạt động” đếm đối tượng có ít nhất một lượt trong ngày; một đối tượng có thể có mặt "
                       "ở nhiều ngày nên dòng cuối là số đối tượng duy nhất của cả kỳ, không phải tổng các ngày.",
                       "nghieng"), bang_b], [bang_b]))

    # C — theo cổng, đếm sự kiện (BR-TONG-08).
    cot_c = [CotIn("Cổng", 16, 22)]
    for n in nhom:
        cot_c += [CotIn(f"{ten[n]} — sự kiện Vào", 10, 17, "phai"), CotIn(f"{ten[n]} — sự kiện Ra", 10, 17, "phai")]
    dong_c = [[O([cong.ten])] + [o for n in nhom for o in (_so(so[n][0]), _so(so[n][1]))] for cong, so in ket_qua.phan_c]
    dong_c.append([O(["Cộng"], dam=True)]
                  + [o for n in nhom for o in (_so(ket_qua.phan_c_cuoi[n][0], True), _so(ket_qua.phan_c_cuoi[n][1], True))])
    bang_c = Bang(cot=cot_c, dong=dong_c, co_chu=9, ten="phan_c")
    phan.append(([Doan("C. PHÂN BỔ THEO CỔNG (số sự kiện)", "muc"), bang_c], [bang_c]))

    # D — lượt chưa hoàn tất, bảng con theo nhóm, không cộng chung.
    cot_d = [CotIn("STT", 4, 9, "giua"), CotIn("Đối tượng", 26, 45), CotIn("Sự kiện mở", 18, 34),
             CotIn("Hạn dự kiến", 11, 20), CotIn("Thời lượng tính đến chốt", 10, 18, "phai"),
             CotIn("Trạng thái", 15, 28), CotIn("Mã lượt", 9, 16)]
    khoi_d, bang_d = [Doan("D. LƯỢT CHƯA HOÀN TẤT TẠI THỜI ĐIỂM CHỐT", "muc")], []
    for i, n in enumerate(nhom, 1):
        cac_dong = ket_qua.phan_d[n]
        khoi_d.append(Doan(f"D{i}. {ten[n]} ({len(cac_dong)} lượt)", "dam"))
        if not cac_dong:
            khoi_d.append(Doan("Không có lượt chưa hoàn tất.", "nghieng"))
            continue
        dong_d = []
        for stt, d in enumerate(cac_dong, 1):
            l = d.luot
            if not ket_qua.xem_chi_tiet[n]:
                doi_tuong = "(không có quyền xem chi tiết)"
            elif n == Luot.Nhom.CBCS:
                doi_tuong = f"{l.can_bo.ma} {l.can_bo.ho_ten}"
            elif n == Luot.Nhom.KHACH:
                doi_tuong = l.khach.ho_ten + (f" (thẻ {l.so_the})" if l.so_the else "")
            else:
                doi_tuong = f"{l.phuong_tien.hien_thi_bien_so} — {l.phuong_tien.loai}"
            loai = "RA" if l.chieu == Luot.Chieu.RA_VAO else "VAO"
            sk = d.su_kien(loai)
            phut = int((chot - l.mo_thoi_diem).total_seconds() // 60)
            dong_d.append([
                O([str(stt)], can="giua", dam=d.trang_thai == MO), O([doi_tuong], dam=d.trang_thai == MO),
                O([f"{'Ra' if loai == 'RA' else 'Vào'} {trinh_bay.thoi_diem_o(sk.thoi_diem, ky)}", sk.cong.ten],
                  dam=d.trang_thai == MO),
                O([trinh_bay.thoi_diem_o(l.han_du_kien, ky) if l.han_du_kien else "—"], dam=d.trang_thai == MO),
                O([f"≥ {phut // 60:02d}:{phut % 60:02d}"], can="phai", dam=d.trang_thai == MO),
                O([d.nhan_trang_thai], nhan_manh="Quá hạn" if d.qua_han else "", dam=d.trang_thai == MO),
                O([f"#{l.pk}"], dam=d.trang_thai == MO),
            ])
        b = Bang(cot=cot_d, dong=dong_d, co_chu=9, ten=f"phan_d_{n}")
        khoi_d.append(b)
        bang_d.append(b)
    phan.append((khoi_d, bang_d or [Bang(cot=cot_d, dong=[])]))

    # E — tóm tắt đính chính, huỷ.
    bang_e = Bang(
        cot=[CotIn("Nhóm", 18, 22), CotIn("Số lượt có đính chính (lượt)", 18, 22, "phai"),
             CotIn("Số đính chính (lần)", 16, 20, "phai"), CotIn("Số bản ghi đã huỷ (bản ghi)", 18, 22, "phai"),
             CotIn("Xem chi tiết", 30, 40)],
        dong=[[O([ten[n]]), _so(ket_qua.phan_a[n]["luot_dinh_chinh"]), _so(ket_qua.phan_a[n]["so_dinh_chinh"]),
               _so(ket_qua.phan_a[n]["ban_ghi_huy"]),
               O([f"Phụ lục đính chính của {trinh_bay.SO_RIENG_CUA_NHOM[n]}"])] for n in nhom],
        co_chu=9, ten="phan_e",
    )
    phan.append(([Doan("E. TÓM TẮT ĐÍNH CHÍNH VÀ HUỶ", "muc"), bang_e], [bang_e]))

    # Gộp các phần liền nhau cùng khổ giấy thành một Phan (một section).
    cac_phan = []
    for i, (khoi, bang) in enumerate(phan):
        kho, huong = chon_kho_giay(*bang)
        if i == 0:
            khoi = _dau_so(dn, ky, chot, ket_qua.bo_loc, tt, [
                "Nhóm đối tượng: " + ", ".join(ten[n] for n in nhom), "Phân bổ: theo ngày lịch"]) + khoi
        if cac_phan and (cac_phan[-1].kho, cac_phan[-1].huong) == (kho, huong):
            cac_phan[-1].khoi += khoi
        else:
            cac_phan.append(Phan(list(khoi), kho, huong))
    so_dong = {"A": len(nhom), "B": len(ket_qua.phan_b), "C": len(ket_qua.phan_c),
               "D": sum(len(ket_qua.phan_d[n]) for n in nhom), "E": len(nhom)}
    cac_phan[-1].khoi.append(_khoi_ket_thuc(dn, ky, chot, tt, dinh_dang, [
        "Số dòng theo phần: " + "; ".join(f"{k}: {v}" for k, v in so_dong.items())]))
    return TaiLieu(
        phan=cac_phan,
        dau_trang_rut_gon=f"{tt.cau_hinh.ten_don_vi.upper()} — {dn.ten} — {_ky_rut_gon(ky)}",
        chan_trang=_chan_trang(dn, tt, dinh_dang),
        tieu_de=f"{dn.ten} — {ky.mo_ta()}",
        tac_gia=tt.nguoi_xuat,
        chu_de=tt.ma_trich_xuat,
        so_dong=so_dong,
    )


def tao_tai_lieu(ket_qua, tt, dinh_dang):
    if isinstance(ket_qua, so_lieu.KetQuaTongHop):
        return tai_lieu_tong_hop(ket_qua, tt, dinh_dang)
    return tai_lieu_chi_tiet(ket_qua, tt, dinh_dang)

