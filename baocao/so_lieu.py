"""Lập số liệu của bốn sổ ra/vào theo business_rules.md.

Module này không biết gì về Excel: nó trả về các dòng và chỉ tiêu đã tính,
để mọi định dạng xuất dùng chung một kết quả (BR-XF-01).
"""
import datetime
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from django.db.models import Prefetch, Q

from ravao.models import CanBo, DinhChinh, Luot, chuan_hoa_ma

from . import quyen

HT, MO, HTS, HUY = "HT", "MO", "HTS", "HUY"
MA_TRANG_THAI = {HT: "Hoàn tất", MO: "Đang mở", HTS: "Hoàn tất sau kỳ", HUY: "Đã huỷ"}


class LoiSoLieu(Exception):
    """Số liệu không thoả quy tắc nội bộ — lỗi lập trình, không xuất (BR-TONG-01)."""


# ---------------------------------------------------------------------------
# Bộ lọc
# ---------------------------------------------------------------------------


@dataclass
class BoLoc:
    cong: list = field(default_factory=list)
    trang_thai: str = ""  # HOAN_TAT, CHUA_HOAN_TAT, QUA_HAN, HOAN_TAT_SAU_KY
    chi_dinh_chinh: bool = False
    hien_huy: bool = False
    sap_xep: str = "mac_dinh"  # mac_dinh, doi_tuong, trang_thai
    # SO-01
    don_vi: list = field(default_factory=list)
    can_bo: str = ""
    chieu: str = ""
    ly_do: str = ""
    # SO-02
    muc_dich: str = ""
    nguoi_tiep: str = ""
    ma_doan: str = ""
    so_giay_to: str = ""
    so_the: str = ""
    chi_qua_han: bool = False
    # SO-03
    bien_so: str = ""
    loai: str = ""
    nguon: str = ""
    nguoi_dieu_khien: str = ""
    # SO-04
    nhom: list = field(default_factory=list)

    TRANG_THAI = {
        "HOAN_TAT": "Hoàn tất",
        "CHUA_HOAN_TAT": "Chưa hoàn tất",
        "QUA_HAN": "Quá hạn",
        "HOAN_TAT_SAU_KY": "Hoàn tất sau kỳ",
    }

    def ap_dung_csdl(self, qs, nhom):
        if self.cong:
            qs = qs.filter(Q(mo_cong__in=self.cong) | Q(dong_cong__in=self.cong))
        if self.chieu:
            qs = qs.filter(chieu=self.chieu)
        if nhom == Luot.Nhom.CBCS:
            if self.don_vi:
                qs = qs.filter(can_bo__don_vi__in=self.don_vi)
            if self.can_bo:
                qs = qs.filter(can_bo__ma=self.can_bo)
            if self.ly_do:
                qs = qs.filter(ly_do=self.ly_do)
        elif nhom == Luot.Nhom.KHACH:
            if self.muc_dich:
                qs = qs.filter(muc_dich__icontains=self.muc_dich)
            if self.nguoi_tiep:
                qs = qs.filter(nguoi_tiep__icontains=self.nguoi_tiep)
            if self.ma_doan:
                qs = qs.filter(ma_doan=self.ma_doan)
            if self.so_giay_to:
                qs = qs.filter(khach__so_giay_to_chuan=chuan_hoa_ma(self.so_giay_to))
            if self.so_the:
                qs = qs.filter(so_the=self.so_the)
        elif nhom == Luot.Nhom.PHUONG_TIEN:
            if self.bien_so:
                qs = qs.filter(phuong_tien__bien_so_chuan__contains=chuan_hoa_ma(self.bien_so))
            if self.loai:
                qs = qs.filter(phuong_tien__loai=self.loai)
            if self.nguon:
                qs = qs.filter(phuong_tien__nguon=self.nguon)
            if self.nguoi_dieu_khien:
                qs = qs.filter(nguoi_dieu_khien__icontains=self.nguoi_dieu_khien)
        return qs

    def giu_dong(self, dong):
        if self.trang_thai == "HOAN_TAT" and dong.trang_thai != HT:
            return False
        if self.trang_thai == "CHUA_HOAN_TAT" and dong.trang_thai not in (MO, HTS):
            return False
        if self.trang_thai == "HOAN_TAT_SAU_KY" and dong.trang_thai != HTS:
            return False
        if (self.trang_thai == "QUA_HAN" or self.chi_qua_han) and not dong.qua_han:
            return False
        if self.chi_dinh_chinh and not dong.dinh_chinh:
            return False
        return True

    def mo_ta(self):
        """Danh sách "Tên lọc: giá trị" để in lên sổ (REQ-GEN-06). Không gồm kỳ, cổng."""
        muc = []
        if self.don_vi:
            muc.append("Đơn vị/bộ phận: " + ", ".join(str(d) for d in self.don_vi))
        nhan = [
            ("can_bo", "CBCS"), ("chieu", "Chiều lượt"), ("ly_do", "Lý do"), ("muc_dich", "Mục đích"),
            ("nguoi_tiep", "Người/bộ phận tiếp"), ("ma_doan", "Đoàn"), ("so_the", "Số thẻ"),
            ("bien_so", "Biển số"), ("loai", "Loại phương tiện"), ("nguon", "Nguồn"),
            ("nguoi_dieu_khien", "Người điều khiển"),
        ]
        for ten, nhan_loc in nhan:
            gia_tri = getattr(self, ten)
            if gia_tri:
                if ten == "chieu":
                    gia_tri = Luot.Chieu(gia_tri).label
                muc.append(f"{nhan_loc}: {gia_tri}")
        if self.so_giay_to:
            muc.append("Số giấy tờ: (đã chỉ định)")  # Không in lại số giấy tờ người dùng nhập.
        if self.trang_thai:
            muc.append("Trạng thái: " + self.TRANG_THAI[self.trang_thai])
        if self.chi_qua_han:
            muc.append("Chỉ lượt quá hạn")
        if self.chi_dinh_chinh:
            muc.append("Chỉ dòng có đính chính")
        if self.nhom and set(self.nhom) != set(Luot.Nhom.values):
            muc.append("Nhóm: " + ", ".join(Luot.Nhom(n).label for n in self.nhom))
        return muc

    @property
    def co_loc(self):
        return bool(self.cong or self.mo_ta())


# ---------------------------------------------------------------------------
# Sắp xếp tiếng Việt
# ---------------------------------------------------------------------------

_BANG_CHU = "aăâbcdđeêfghijklmnoôơpqrstuưvwxyz"
_DAU_CHU = {"̆": "ă", "̂": "â", "̛": "ơ"}  # breve, circumflex, horn
_DAU_THANH = {"̀": 1, "̉": 2, "̃": 3, "́": 4, "̣": 5}


def khoa_tieng_viet(chuoi):
    """Khoá sắp xếp theo bảng chữ cái tiếng Việt (a < ă < â < … < đ < …)."""
    chinh, phu = [], []
    for ky_tu in unicodedata.normalize("NFC", chuoi or "").lower():
        phan = unicodedata.normalize("NFD", ky_tu)
        goc, dau = phan[0], phan[1:]
        chu = goc
        for d in dau:
            if d in _DAU_CHU:
                chu = {("a", "̆"): "ă", ("a", "̂"): "â", ("e", "̂"): "ê",
                       ("o", "̂"): "ô", ("o", "̛"): "ơ", ("u", "̛"): "ư"}.get((goc, d), goc)
        vi_tri = _BANG_CHU.find(chu)
        chinh.append(vi_tri if vi_tri >= 0 else 100 + ord(chu))
        phu.append(sum(_DAU_THANH.get(d, 0) for d in dau))
    return (tuple(chinh), tuple(phu))


def khoa_ho_ten(ho_ten):
    """Sắp theo tên, rồi họ và tên đệm (report_definitions.md §3.6)."""
    ten = (ho_ten or "").split()
    return (khoa_tieng_viet(ten[-1] if ten else ""), khoa_tieng_viet(ho_ten))


# ---------------------------------------------------------------------------
# Dòng lượt
# ---------------------------------------------------------------------------


@dataclass
class DongLuot:
    luot: Luot
    trang_thai: str
    qua_han: bool
    tu_ky_truoc: bool
    sau_ky: bool
    thoi_luong: datetime.timedelta | None
    thoi_luong_toi_thieu: bool
    loi_thoi_gian: bool
    ghi_bo_sung: bool
    khoa_doi_tuong: object
    chong_luot: bool = False
    stt: int | None = None
    dinh_chinh: list = field(default_factory=list)  # [(n, DinhChinh)]

    @property
    def nhan_trang_thai(self):
        if self.trang_thai == HT:
            return "Hoàn tất"
        if self.trang_thai == HTS:
            return "Hoàn tất sau kỳ"
        if self.trang_thai == HUY:
            return "ĐÃ HUỶ"
        nhan = "Chưa về" if self.luot.chieu == Luot.Chieu.RA_VAO else "Chưa ra"
        return nhan + (" – Quá hạn" if self.qua_han else "")

    @property
    def ky_hieu(self):
        """Ký hiệu cột Ghi chú theo thứ tự BR-TT-02."""
        muc = []
        if self.dinh_chinh:
            muc.append("ĐC(" + ",".join(str(n) for n, _ in self.dinh_chinh) + ")")
        if self.ghi_bo_sung:
            muc.append("GBS")
        if self.chong_luot:
            muc.append("Chồng lượt")
        if self.loi_thoi_gian:
            muc.append("Lỗi thời gian")
        if self.trang_thai == HUY and self.luot.ly_do_huy:
            muc.append("Lý do huỷ: " + self.luot.ly_do_huy)
        if self.luot.ghi_chu:
            muc.append(self.luot.ghi_chu)
        return "; ".join(muc)

    # Sự kiện theo chiều: Ra–Vào thì mở là Ra; Vào–Ra thì mở là Vào.
    def su_kien(self, loai):
        l = self.luot
        mo_la_ra = l.chieu == Luot.Chieu.RA_VAO
        la_mo = (loai == "RA") == mo_la_ra
        if la_mo:
            return SuKien(l.mo_thoi_diem, l.mo_cong, l.mo_nguoi_ghi, l.mo_ghi_nhan_luc,
                          "(từ kỳ trước)" if self.tu_ky_truoc else "")
        return SuKien(l.dong_thoi_diem, l.dong_cong, l.dong_nguoi_ghi, l.dong_ghi_nhan_luc,
                      "(sau kỳ)" if self.sau_ky else "")


@dataclass
class SuKien:
    thoi_diem: datetime.datetime | None
    cong: object
    nguoi_ghi: object
    ghi_nhan_luc: datetime.datetime | None
    chu_thich: str


def _khoa_doi_tuong(luot):
    if luot.nhom == Luot.Nhom.CBCS:
        return ("CBCS", luot.can_bo_id)
    if luot.nhom == Luot.Nhom.KHACH:
        return luot.khach.dinh_danh
    return luot.phuong_tien.dinh_danh


def _tao_dong(luot, ky, chot, nguong_gbs):
    dong_tg = luot.dong_thoi_diem
    if luot.da_huy:
        trang_thai = HUY
    elif dong_tg is not None and dong_tg < chot:
        trang_thai = HT
    elif dong_tg is not None:
        trang_thai = HTS
    else:
        trang_thai = MO
    loi_thoi_gian = dong_tg is not None and dong_tg < luot.mo_thoi_diem
    if dong_tg is None:
        thoi_luong, toi_thieu = chot - luot.mo_thoi_diem, True
    elif loi_thoi_gian:
        thoi_luong, toi_thieu = None, False
    else:
        thoi_luong, toi_thieu = dong_tg - luot.mo_thoi_diem, False
    ghi_bo_sung = (luot.mo_ghi_nhan_luc - luot.mo_thoi_diem) > nguong_gbs or (
        dong_tg is not None and luot.dong_ghi_nhan_luc is not None
        and (luot.dong_ghi_nhan_luc - dong_tg) > nguong_gbs
    )
    return DongLuot(
        luot=luot,
        trang_thai=trang_thai,
        qua_han=trang_thai == MO and luot.han_du_kien is not None and luot.han_du_kien < chot,
        tu_ky_truoc=luot.mo_thoi_diem < ky.tu,
        sau_ky=dong_tg is not None and dong_tg >= chot,
        thoi_luong=thoi_luong,
        thoi_luong_toi_thieu=toi_thieu,
        loi_thoi_gian=loi_thoi_gian,
        ghi_bo_sung=ghi_bo_sung,
        khoa_doi_tuong=_khoa_doi_tuong(luot),
    )


def _truy_van_luot(nguoi_dung, nhom, ky, chot, bo_loc, da_huy):
    """Tập lượt giao với [Từ, chốt) trong phạm vi được phép (BR-KY-05, BR-KY-07)."""
    qs = quyen.pham_vi_luot(nguoi_dung, nhom).filter(
        Q(dong_thoi_diem__isnull=True) | Q(dong_thoi_diem__gte=ky.tu),
        mo_thoi_diem__lt=chot,
        da_huy=da_huy,
    )
    qs = bo_loc.ap_dung_csdl(qs, nhom)
    return qs.select_related(
        "can_bo__don_vi", "khach", "phuong_tien__nguon_can_bo", "phuong_tien__nguon_khach",
        "mo_cong", "dong_cong", "mo_nguoi_ghi", "dong_nguoi_ghi", "phuong_tien_di_kem",
        "nguoi_dieu_khien_can_bo",
    ).prefetch_related(Prefetch("dinh_chinh_set", queryset=DinhChinh.objects.select_related("nguoi")))


_TRUONG_DOI_TUONG = {Luot.Nhom.CBCS: "can_bo_id", Luot.Nhom.KHACH: "khach_id", Luot.Nhom.PHUONG_TIEN: "phuong_tien_id"}


def _danh_dau_chong_luot(dong, nhom, chot):
    """Đánh dấu lượt chồng thời gian của cùng đối tượng (BR-LT-04)."""
    if not dong:
        return
    truong = _TRUONG_DOI_TUONG[nhom]
    ids = {getattr(d.luot, truong) for d in dong}
    som_nhat = min(d.luot.mo_thoi_diem for d in dong)
    khac = Luot.objects.filter(
        Q(dong_thoi_diem__isnull=True) | Q(dong_thoi_diem__gt=som_nhat),
        nhom=nhom, da_huy=False, mo_thoi_diem__lt=chot, **{f"{truong}__in": ids},
    ).values_list("id", truong, "mo_thoi_diem", "dong_thoi_diem")
    theo_doi_tuong = defaultdict(list)
    for id_, ma, mo, dong_tg in khac:
        ket_thuc = datetime.datetime.max.replace(tzinfo=datetime.UTC) if dong_tg is None else max(dong_tg, mo)
        theo_doi_tuong[ma].append((mo, ket_thuc, id_))
    bi_chong = set()
    for khoang in theo_doi_tuong.values():
        khoang.sort()
        for i, (mo_i, kt_i, id_i) in enumerate(khoang):
            for mo_j, _kt_j, id_j in khoang[i + 1:]:
                if mo_j >= kt_i:
                    break
                bi_chong.update((id_i, id_j))
    for d in dong:
        d.chong_luot = d.luot.id in bi_chong


def _khoa_sap_xep(sap_xep, nhom):
    def mac_dinh(d):
        return (d.luot.mo_thoi_diem, d.luot.id)

    if sap_xep == "doi_tuong":
        if nhom == Luot.Nhom.CBCS:
            return lambda d: (khoa_ho_ten(d.luot.can_bo.ho_ten), mac_dinh(d))
        if nhom == Luot.Nhom.KHACH:
            return lambda d: (khoa_ho_ten(d.luot.khach.ho_ten), mac_dinh(d))
        return lambda d: (d.luot.phuong_tien.bien_so_chuan or "~" + d.luot.phuong_tien.ma_tam, mac_dinh(d))
    if sap_xep == "trang_thai":
        return lambda d: (0 if d.qua_han else 1 if d.trang_thai in (MO, HTS) else 2, mac_dinh(d))
    return mac_dinh


# ---------------------------------------------------------------------------
# Chỉ tiêu
# ---------------------------------------------------------------------------


def tinh_chi_tieu(dong, nhom, ky, so_huy):
    """Chỉ tiêu chuẩn và chỉ tiêu riêng (BR-TONG-01, BR-TONG-05, BR-DN)."""
    hieu_luc = [d for d in dong if d.trang_thai != HUY]
    ct = {
        "so_luot": len(hieu_luc),
        "tu_ky_truoc": sum(d.luot.mo_thoi_diem < ky.tu for d in hieu_luc),
        "phat_sinh": sum(d.luot.mo_thoi_diem >= ky.tu for d in hieu_luc),
        "hoan_tat": sum(d.trang_thai == HT for d in hieu_luc),
        "chua_hoan_tat": sum(d.trang_thai in (MO, HTS) for d in hieu_luc),
        "dang_mo": sum(d.trang_thai == MO for d in hieu_luc),
        "hoan_tat_sau_ky": sum(d.trang_thai == HTS for d in hieu_luc),
        "qua_han": sum(d.qua_han for d in hieu_luc),
        "doi_tuong_duy_nhat": len({d.khoa_doi_tuong for d in hieu_luc if d.khoa_doi_tuong is not None}),
        "khong_dinh_danh": (
            None if nhom == Luot.Nhom.CBCS else sum(d.khoa_doi_tuong is None for d in hieu_luc)
        ),
        "luot_dinh_chinh": sum(bool(d.dinh_chinh) for d in hieu_luc),
        "so_dinh_chinh": sum(len(d.dinh_chinh) for d in hieu_luc),
        "ban_ghi_huy": so_huy,
    }
    if ct["tu_ky_truoc"] + ct["phat_sinh"] != ct["hoan_tat"] + ct["chua_hoan_tat"]:
        raise LoiSoLieu(f"Số liệu {nhom} không cân đối: {ct}")
    if nhom == Luot.Nhom.CBCS:
        ct["theo_chieu"] = _dem(Luot.Chieu(d.luot.chieu).label for d in hieu_luc)
        ct["theo_ly_do"] = _dem(d.luot.ly_do or "Không ghi" for d in hieu_luc)
    elif nhom == Luot.Nhom.KHACH:
        ct["so_doan"] = len({d.luot.ma_doan for d in hieu_luc if d.luot.ma_doan})
        ct["the_chua_thu_hoi"] = sum(bool(d.luot.so_the) and d.trang_thai in (MO, HTS) for d in hieu_luc)
    else:
        ct["theo_chieu"] = _dem(Luot.Chieu(d.luot.chieu).label for d in hieu_luc)
        ct["theo_loai"] = _dem(d.luot.phuong_tien.loai for d in hieu_luc)
        ct["theo_nguon"] = _dem(d.luot.phuong_tien.get_nguon_display() for d in hieu_luc)
    return ct


def _dem(gia_tri):
    return dict(sorted(Counter(gia_tri).items(), key=lambda m: (-m[1], khoa_tieng_viet(m[0]))))


# ---------------------------------------------------------------------------
# Sổ chi tiết SO-01, SO-02, SO-03
# ---------------------------------------------------------------------------


@dataclass
class KetQuaSoChiTiet:
    dinh_nghia: quyen.DinhNghiaSo
    ky: object
    chot: datetime.datetime
    bo_loc: BoLoc
    dong: list
    chi_tieu: dict
    phu_luc: list  # [(n, stt, DongLuot, DinhChinh)]

    @property
    def so_dong_co_stt(self):
        return sum(d.stt is not None for d in self.dong)


def lap_so_chi_tiet(nguoi_dung, dinh_nghia, ky, chot, bo_loc, nguong_gbs, thoi_diem_trich_xuat):
    quyen.kiem_tra_quyen_so(nguoi_dung, dinh_nghia, hien_huy=bo_loc.hien_huy)
    nhom = dinh_nghia.nhom
    dong = [_tao_dong(l, ky, chot, nguong_gbs) for l in _truy_van_luot(nguoi_dung, nhom, ky, chot, bo_loc, False)]
    _gan_dinh_chinh_tam(dong, thoi_diem_trich_xuat)
    dong = [d for d in dong if bo_loc.giu_dong(d)]
    _danh_dau_chong_luot(dong, nhom, chot)

    huy = [
        _tao_dong(l, ky, chot, nguong_gbs)
        for l in _truy_van_luot(nguoi_dung, nhom, ky, chot, bo_loc, True)
    ]
    so_huy = len(huy)
    if bo_loc.hien_huy:
        _gan_dinh_chinh_tam(huy, thoi_diem_trich_xuat)
        dong += [d for d in huy if not bo_loc.chi_dinh_chinh or d.dinh_chinh]

    dong.sort(key=_khoa_sap_xep(bo_loc.sap_xep, nhom))
    stt = 0
    for d in dong:
        if d.trang_thai != HUY:
            stt += 1
            d.stt = stt
    phu_luc = _danh_so_dinh_chinh(dong)
    chi_tieu = tinh_chi_tieu(dong, nhom, ky, so_huy)
    return KetQuaSoChiTiet(dinh_nghia, ky, chot, bo_loc, dong, chi_tieu, phu_luc)


def _gan_dinh_chinh_tam(dong, thoi_diem_trich_xuat):
    for d in dong:
        d.dinh_chinh = [
            (None, dc) for dc in d.luot.dinh_chinh_set.all() if dc.thoi_diem <= thoi_diem_trich_xuat
        ]


def _danh_so_dinh_chinh(dong):
    """(n) theo STT dòng tăng dần rồi thời điểm đính chính (BR-DC-04)."""
    phu_luc, n = [], 0
    for d in dong:
        danh_so = []
        for _, dc in sorted(d.dinh_chinh, key=lambda m: (m[1].thoi_diem, m[1].id)):
            n += 1
            danh_so.append((n, dc))
            phu_luc.append((n, d.stt, d, dc))
        d.dinh_chinh = danh_so
    return phu_luc


# ---------------------------------------------------------------------------
# Sổ tổng hợp SO-04
# ---------------------------------------------------------------------------


@dataclass
class KetQuaTongHop:
    dinh_nghia: quyen.DinhNghiaSo
    ky: object
    chot: datetime.datetime
    bo_loc: BoLoc
    nhom: list
    phan_a: dict  # nhom -> chi_tieu
    phan_b: list  # [(ngay, {nhom: (luot_phat_sinh, doi_tuong_hoat_dong)})]
    phan_b_cuoi: dict  # nhom -> (tong_luot, duy_nhat_ca_ky)
    phan_c: list  # [(cong, {nhom: (vao, ra)})]
    phan_c_cuoi: dict
    phan_d: dict  # nhom -> [DongLuot]
    xem_chi_tiet: dict  # nhom -> bool


def lap_so_tong_hop(nguoi_dung, dinh_nghia, ky, chot, bo_loc, nguong_gbs, thoi_diem_trich_xuat):
    quyen.kiem_tra_quyen_so(nguoi_dung, dinh_nghia)
    cac_nhom = [n for n in Luot.Nhom.values if not bo_loc.nhom or n in bo_loc.nhom]
    bo_loc_nhom = BoLoc(cong=bo_loc.cong)  # SO-04 chỉ lọc theo cổng và nhóm (§6.5).
    phan_a, dong_theo_nhom, phan_d, xem_chi_tiet = {}, {}, {}, {}
    for nhom in cac_nhom:
        dong = [_tao_dong(l, ky, chot, nguong_gbs)
                for l in _truy_van_luot(nguoi_dung, nhom, ky, chot, bo_loc_nhom, False)]
        _gan_dinh_chinh_tam(dong, thoi_diem_trich_xuat)
        dong.sort(key=_khoa_sap_xep("mac_dinh", nhom))
        so_huy = _truy_van_luot(nguoi_dung, nhom, ky, chot, bo_loc_nhom, True).count()
        phan_a[nhom] = tinh_chi_tieu(dong, nhom, ky, so_huy)
        dong_theo_nhom[nhom] = dong
        phan_d[nhom] = sorted(
            (d for d in dong if d.trang_thai in (MO, HTS)),
            key=lambda d: (not d.qua_han, d.luot.mo_thoi_diem, d.luot.id),
        )
        xem_chi_tiet[nhom] = quyen.duoc_xem_chi_tiet_nhom(nguoi_dung, nhom)

    phan_b, tong_b = [], {n: 0 for n in cac_nhom}
    for ngay, dau, cuoi in ky.cac_ngay(chot):
        hang = {}
        for nhom in cac_nhom:
            phat_sinh = sum(dau <= d.luot.mo_thoi_diem < cuoi for d in dong_theo_nhom[nhom])
            hoat_dong = {
                d.khoa_doi_tuong for d in dong_theo_nhom[nhom]
                if d.khoa_doi_tuong is not None and d.luot.mo_thoi_diem < cuoi
                and (d.luot.dong_thoi_diem is None or d.luot.dong_thoi_diem >= dau)
            }
            hang[nhom] = (phat_sinh, len(hoat_dong))
            tong_b[nhom] += phat_sinh
        phan_b.append((ngay, hang))
    phan_b_cuoi = {n: (tong_b[n], phan_a[n]["doi_tuong_duy_nhat"]) for n in cac_nhom}
    if any(tong_b[n] != phan_a[n]["phat_sinh"] for n in cac_nhom):
        raise LoiSoLieu("Tổng lượt phát sinh theo ngày không khớp Phần A.")

    phan_c, phan_c_cuoi = _phan_bo_theo_cong(dong_theo_nhom, cac_nhom, ky, chot, bo_loc.cong)
    return KetQuaTongHop(dinh_nghia, ky, chot, bo_loc, cac_nhom, phan_a, phan_b, phan_b_cuoi,
                         phan_c, phan_c_cuoi, phan_d, xem_chi_tiet)


def _phan_bo_theo_cong(dong_theo_nhom, cac_nhom, ky, chot, cong_loc):
    """Đếm sự kiện Vào/Ra theo cổng trong [Từ, chốt) (BR-TONG-08)."""
    dem = defaultdict(lambda: {n: [0, 0] for n in cac_nhom})
    cac_cong = {}
    for nhom in cac_nhom:
        for d in dong_theo_nhom[nhom]:
            for loai, chi_so in (("VAO", 0), ("RA", 1)):
                sk = d.su_kien(loai)
                if sk.thoi_diem is None or not (ky.tu <= sk.thoi_diem < chot):
                    continue
                if cong_loc and sk.cong not in cong_loc:
                    continue
                cac_cong[sk.cong.pk] = sk.cong
                dem[sk.cong.pk][nhom][chi_so] += 1
    hang = []
    cuoi = {n: [0, 0] for n in cac_nhom}
    for cong in sorted(cac_cong.values(), key=lambda c: (c.thu_tu, c.ma)):
        so = {n: tuple(dem[cong.pk][n]) for n in cac_nhom}
        hang.append((cong, so))
        for n in cac_nhom:
            cuoi[n][0] += so[n][0]
            cuoi[n][1] += so[n][1]
    return hang, {n: tuple(v) for n, v in cuoi.items()}


def nguoi_ghi_hien_thi(nguoi_dung):
    return nguoi_dung.get_username() if nguoi_dung else ""


def ten_can_bo(can_bo: CanBo | None):
    return f"{can_bo.ho_ten} ({can_bo.ma})" if can_bo else ""
