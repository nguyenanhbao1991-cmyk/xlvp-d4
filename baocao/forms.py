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

    def __init__(self, *args, nguoi_dung=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nguoi_dung = nguoi_dung

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
