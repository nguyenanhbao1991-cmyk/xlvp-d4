"""Kỳ báo cáo nửa mở [Từ, Đến) (BR-KY-02, BR-KY-03, BR-KY-06)."""
import datetime
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.utils import timezone

KY_TOI_DA_NGAY = 366  # Giới hạn Excel cho mọi sổ (BR-KY-06, XN-18).

LUA_CHON_NHANH = [
    ("hom_nay", "Hôm nay"),
    ("hom_qua", "Hôm qua"),
    ("ca_hien_tai", "Ca trực hiện tại"),
    ("ca_truoc", "Ca trực trước"),
    ("tuan_nay", "Tuần này"),
    ("thang_nay", "Tháng này"),
    ("thang_truoc", "Tháng trước"),
]


def _nua_dem(ngay):
    return timezone.make_aware(datetime.datetime.combine(ngay, datetime.time()))


def _dau_thang(ngay):
    return ngay.replace(day=1)


def _thang_sau(ngay):
    return (ngay.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)


@dataclass(frozen=True)
class KyBaoCao:
    tu: datetime.datetime
    den: datetime.datetime

    def __post_init__(self):
        if timezone.is_naive(self.tu) or timezone.is_naive(self.den):
            raise ValidationError("Thời điểm của kỳ phải có múi giờ.")
        if self.den <= self.tu:
            raise ValidationError("Thời điểm “Đến” phải sau thời điểm “Từ”.", code="ky_nguoc")
        if self.den - self.tu > datetime.timedelta(days=KY_TOI_DA_NGAY):
            raise ValidationError(
                f"Kỳ dài hơn {KY_TOI_DA_NGAY} ngày. Hãy thu hẹp khoảng thời gian.", code="ky_qua_dai"
            )

    @classmethod
    def tu_lua_chon(cls, ma, bay_gio, gio_giao_ca):
        hom_nay = timezone.localtime(bay_gio).date()
        mot_ngay = datetime.timedelta(days=1)
        if ma == "hom_nay":
            return cls(_nua_dem(hom_nay), _nua_dem(hom_nay + mot_ngay))
        if ma == "hom_qua":
            return cls(_nua_dem(hom_nay - mot_ngay), _nua_dem(hom_nay))
        if ma in ("ca_hien_tai", "ca_truoc"):
            giao_ca = timezone.make_aware(datetime.datetime.combine(hom_nay, gio_giao_ca))
            if giao_ca > bay_gio:
                giao_ca -= mot_ngay
            if ma == "ca_truoc":
                giao_ca -= mot_ngay
            return cls(giao_ca, giao_ca + mot_ngay)
        if ma == "tuan_nay":
            thu_hai = hom_nay - datetime.timedelta(days=hom_nay.weekday())
            return cls(_nua_dem(thu_hai), _nua_dem(thu_hai + datetime.timedelta(days=7)))
        if ma == "thang_nay":
            return cls(_nua_dem(_dau_thang(hom_nay)), _nua_dem(_thang_sau(hom_nay)))
        if ma == "thang_truoc":
            dau = _dau_thang(_dau_thang(hom_nay) - mot_ngay)
            return cls(_nua_dem(dau), _nua_dem(_dau_thang(hom_nay)))
        raise ValidationError("Lựa chọn kỳ không hợp lệ.")

    @property
    def tu_dia_phuong(self):
        return timezone.localtime(self.tu)

    @property
    def den_dia_phuong(self):
        return timezone.localtime(self.den)

    @property
    def ngay_dau(self):
        return self.tu_dia_phuong.date()

    @property
    def ngay_cuoi(self):
        """Ngày lịch cuối cùng có trong kỳ (BR-XF-05)."""
        return timezone.localtime(self.den - datetime.timedelta(microseconds=1)).date()

    def mo_ta(self):
        """Cách ghi kỳ trên sổ (BR-KY-02)."""
        tu, den = self.tu_dia_phuong, self.den_dia_phuong
        if tu.time() == datetime.time() and den.time() == datetime.time():
            return f"Từ 00:00 ngày {tu:%d/%m/%Y} đến hết ngày {self.ngay_cuoi:%d/%m/%Y}"
        return f"Từ {tu:%H:%M} ngày {tu:%d/%m/%Y} đến trước {den:%H:%M} ngày {den:%d/%m/%Y}"

    def cac_ngay(self, chot):
        """Các khoảng [đầu, cuối) theo ngày lịch giao với [Từ, chốt) (BR-ND-06)."""
        ngay = self.ngay_dau
        while True:
            dau = max(_nua_dem(ngay), self.tu)
            cuoi = min(_nua_dem(ngay + datetime.timedelta(days=1)), chot)
            if dau >= chot:
                break
            yield ngay, dau, cuoi
            ngay += datetime.timedelta(days=1)
