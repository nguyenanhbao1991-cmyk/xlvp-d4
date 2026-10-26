"""Bộ lọc của từng sổ (report_definitions.md §3.5, §4.5, §5.5, §6.5)."""
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from ravao.models import Cong, DonVi, Luot, PhuongTien

from . import dong_ho, quyen
from .ky import LUA_CHON_NHANH, KyBaoCao
from .models import CauHinhSo
from .so_lieu import BoLoc

DINH_DANG_NHAP = ["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d"]
DE_TRONG = "__trong__"


class BoLocChung(forms.Form):
    ky = forms.ChoiceField(label="Kỳ", choices=[("", "Tuỳ chọn")] + LUA_CHON_NHANH, required=False)
    tu = forms.DateTimeField(label="Từ", required=False, input_formats=DINH_DANG_NHAP)
    den = forms.DateTimeField(label="Đến (không gồm)", required=False, input_formats=DINH_DANG_NHAP)
    cong = forms.ModelMultipleChoiceField(label="Cổng", queryset=Cong.objects.all(), required=False)
    nguoi_lap_so = forms.CharField(
        label="Người lập sổ", required=False,
        help_text="Để trống: người xuất. Nhập tên đăng nhập để chọn người khác, hoặc “__trong__” để ký tay.",
    )

    def __init__(self, *args, nguoi_dung=None, ky_co_dinh=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nguoi_dung = nguoi_dung
        # Màn hình "Xuất sổ theo dõi" tự tính kỳ (một ngày / khoảng ngày / tháng) và truyền vào đây.
        self.ky_co_dinh = ky_co_dinh

    def clean_nguoi_lap_so(self):
        gia_tri = (self.cleaned_data.get("nguoi_lap_so") or "").strip()
        if not gia_tri or gia_tri == DE_TRONG:
            return gia_tri
        try:
            nguoi = get_user_model().objects.get(username=gia_tri, is_active=True)
        except get_user_model().DoesNotExist:
            raise ValidationError("Không tìm thấy người dùng đang hoạt động với tên đăng nhập này.")
        return nguoi

    def clean(self):
        du_lieu = super().clean()
        if self.errors:
            return du_lieu
        if self.ky_co_dinh is not None:
            du_lieu["ky_bao_cao"] = self.ky_co_dinh
            return du_lieu
        try:
            if du_lieu.get("ky"):
                du_lieu["ky_bao_cao"] = KyBaoCao.tu_lua_chon(
                    du_lieu["ky"], dong_ho.hien_tai(), CauHinhSo.lay().gio_giao_ca
                )
            elif du_lieu.get("tu") and du_lieu.get("den"):
                du_lieu["ky_bao_cao"] = KyBaoCao(du_lieu["tu"], du_lieu["den"])
            else:
                raise ValidationError("Chọn kỳ nhanh hoặc nhập đủ “Từ” và “Đến”.", code="thieu_ky")
        except ValidationError as loi:
            raise ValidationError({"den": loi.messages})
        return du_lieu

    def ten_nguoi_lap_so(self):
        gia_tri = self.cleaned_data.get("nguoi_lap_so")
        if gia_tri == DE_TRONG:
            return ""
        nguoi = gia_tri or self.nguoi_dung
        return quyen.ho_ten(nguoi)

    TRUONG_BO_LOC = ["cong"]

    def bo_loc(self):
        gia_tri = {k: self.cleaned_data.get(k) for k in self.TRUONG_BO_LOC}
        gia_tri = {k: (list(v) if hasattr(v, "model") else v) for k, v in gia_tri.items() if v not in (None, "")}
        return BoLoc(**gia_tri)


_TRANG_THAI = [("", "Tất cả")] + list(BoLoc.TRANG_THAI.items())
_SAP_XEP = [("mac_dinh", "Thời điểm mở"), ("doi_tuong", "Đối tượng"), ("trang_thai", "Trạng thái")]


class BoLocSoChiTiet(BoLocChung):
    trang_thai = forms.ChoiceField(label="Trạng thái", choices=_TRANG_THAI, required=False)
    chi_dinh_chinh = forms.BooleanField(label="Chỉ dòng có đính chính", required=False)
    hien_huy = forms.BooleanField(label="Hiện bản ghi đã huỷ", required=False)
    sap_xep = forms.ChoiceField(label="Sắp xếp", choices=_SAP_XEP, required=False)

    TRUONG_BO_LOC = BoLocChung.TRUONG_BO_LOC + ["trang_thai", "chi_dinh_chinh", "hien_huy", "sap_xep"]


class BoLocCBCS(BoLocSoChiTiet):
    don_vi = forms.ModelMultipleChoiceField(label="Đơn vị/bộ phận", queryset=DonVi.objects.all(), required=False)
    can_bo = forms.CharField(label="Mã CBCS", max_length=30, required=False)
    chieu = forms.ChoiceField(label="Chiều lượt", choices=[("", "Tất cả")] + Luot.Chieu.choices, required=False)
    ly_do = forms.CharField(label="Lý do", max_length=100, required=False)

    TRUONG_BO_LOC = BoLocSoChiTiet.TRUONG_BO_LOC + ["don_vi", "can_bo", "chieu", "ly_do"]


class BoLocKhach(BoLocSoChiTiet):
    muc_dich = forms.CharField(label="Mục đích", max_length=200, required=False)
    nguoi_tiep = forms.CharField(label="Người/bộ phận tiếp", max_length=200, required=False)
    ma_doan = forms.CharField(label="Đoàn", max_length=30, required=False)
    so_giay_to = forms.CharField(label="Số giấy tờ (khớp chính xác)", max_length=50, required=False)
    so_the = forms.CharField(label="Số thẻ", max_length=20, required=False)
    chi_qua_han = forms.BooleanField(label="Chỉ khách quá hạn", required=False)
    du_lieu_day_du = forms.BooleanField(label="Xuất dữ liệu cá nhân đầy đủ", required=False)

    TRUONG_BO_LOC = BoLocSoChiTiet.TRUONG_BO_LOC + [
        "muc_dich", "nguoi_tiep", "ma_doan", "so_giay_to", "so_the", "chi_qua_han",
    ]


class BoLocPhuongTien(BoLocSoChiTiet):
    bien_so = forms.CharField(label="Biển số", max_length=30, required=False)
    loai = forms.CharField(label="Loại phương tiện", max_length=100, required=False)
    nguon = forms.ChoiceField(label="Nguồn", choices=[("", "Tất cả")] + PhuongTien.Nguon.choices, required=False)
    nguoi_dieu_khien = forms.CharField(label="Người điều khiển", max_length=200, required=False)
    chieu = forms.ChoiceField(label="Chiều lượt", choices=[("", "Tất cả")] + Luot.Chieu.choices, required=False)

    TRUONG_BO_LOC = BoLocSoChiTiet.TRUONG_BO_LOC + ["bien_so", "loai", "nguon", "nguoi_dieu_khien", "chieu"]


class BoLocTongHop(BoLocChung):
    nhom = forms.MultipleChoiceField(label="Nhóm đối tượng", choices=Luot.Nhom.choices, required=False)

    TRUONG_BO_LOC = BoLocChung.TRUONG_BO_LOC + ["nhom"]


FORM_THEO_SO = {"SO-01": BoLocCBCS, "SO-02": BoLocKhach, "SO-03": BoLocPhuongTien, "SO-04": BoLocTongHop}


# ---------------------------------------------------------------------------
# Màn hình "Xuất sổ theo dõi"
# ---------------------------------------------------------------------------

TRUONG_KY_CU = ("ky", "tu", "den")  # Không hiển thị trên màn hình: kỳ chọn ở phần chung.
DINH_DANG = [("xlsx", "Excel (.xlsx)"), ("docx", "Word (.docx)"), ("pdf", "PDF")]
CHE_DO_KY = [("ngay", "Một ngày"), ("khoang", "Từ ngày đến ngày"), ("thang", "Theo tháng")]
DINH_DANG_NGAY = ["%Y-%m-%d", "%d/%m/%Y"]


def tien_to(dinh_nghia):
    return dinh_nghia.ma_gon.lower()


class FormXuatSo(forms.Form):
    loai_so = forms.ChoiceField(label="Loại sổ")
    che_do_ky = forms.ChoiceField(label="Khoảng thời gian", choices=CHE_DO_KY, initial="ngay")
    ngay = forms.DateField(label="Ngày", required=False, input_formats=DINH_DANG_NGAY,
                           widget=forms.DateInput(attrs={"type": "date"}))
    tu_ngay = forms.DateField(label="Từ ngày", required=False, input_formats=DINH_DANG_NGAY,
                              widget=forms.DateInput(attrs={"type": "date"}))
    den_ngay = forms.DateField(label="Đến ngày (gồm cả ngày này)", required=False, input_formats=DINH_DANG_NGAY,
                               widget=forms.DateInput(attrs={"type": "date"}))
    thang = forms.RegexField(label="Tháng", required=False, regex=r"^\d{4}-(0[1-9]|1[0-2])$",
                             error_messages={"invalid": "Tháng phải có dạng NNNN-TT, ví dụ 2026-10."},
                             widget=forms.TextInput(attrs={"type": "month", "placeholder": "2026-10"}))
    dinh_dang = forms.ChoiceField(label="Định dạng", choices=DINH_DANG, initial="xlsx")
    # Số dòng lúc xem trước: chỉ để so sánh, không dùng làm số liệu xuất.
    so_dong_xem_truoc = forms.IntegerField(required=False, min_value=0, widget=forms.HiddenInput)

    def __init__(self, *args, cac_so=(), kha_nang=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["loai_so"].choices = [(dn.ma, f"{dn.ma} — {dn.ten}") for dn in cac_so]
        self.kha_nang = kha_nang or {}

    def clean_dinh_dang(self):
        dinh_dang = self.cleaned_data["dinh_dang"]
        if dinh_dang in self.kha_nang:
            raise ValidationError(f"Định dạng này chưa dùng được trên máy chủ: {self.kha_nang[dinh_dang]}")
        return dinh_dang

    def clean(self):
        du_lieu = super().clean()
        che_do = du_lieu.get("che_do_ky")
        try:
            if che_do == "ngay":
                if not du_lieu.get("ngay"):
                    self.add_error("ngay", "Chọn ngày.")
                    return du_lieu
                du_lieu["ky_bao_cao"] = KyBaoCao.theo_ngay(du_lieu["ngay"], du_lieu["ngay"])
            elif che_do == "khoang":
                tu, den = du_lieu.get("tu_ngay"), du_lieu.get("den_ngay")
                if not tu or not den:
                    self.add_error("tu_ngay" if not tu else "den_ngay", "Chọn đủ ngày bắt đầu và ngày kết thúc.")
                    return du_lieu
                du_lieu["ky_bao_cao"] = KyBaoCao.theo_ngay(tu, den)
            elif che_do == "thang":
                if not du_lieu.get("thang"):
                    if "thang" not in self.errors:
                        self.add_error("thang", "Chọn tháng.")
                    return du_lieu
                nam, thang = map(int, du_lieu["thang"].split("-"))
                du_lieu["ky_bao_cao"] = KyBaoCao.theo_thang(nam, thang)
        except ValidationError as loi:
            truong = {"ngay": "ngay", "khoang": "den_ngay", "thang": "thang"}[che_do]
            self.add_error(truong, loi)
        return du_lieu
