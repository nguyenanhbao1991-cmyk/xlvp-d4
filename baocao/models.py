import datetime
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


def o_ky_mac_dinh():
    """Đề xuất XN-14; chỉ có hiệu lực khi đơn vị bật ``khoi_ky_da_phe_duyet``."""
    return [{"chuc_danh": "Người lập sổ", "nguoi_lap_so": True}, {"chuc_danh": "Chỉ huy đơn vị"}]


class CauHinhSo(models.Model):
    """Cấu hình in trên sổ (REQ-GEN-21). Chỉ dùng một bản ghi."""

    co_quan_chu_quan = models.CharField("cơ quan chủ quản", max_length=200, blank=True)
    ten_don_vi = models.CharField("tên đơn vị", max_length=200, default="")
    dia_danh = models.CharField("địa danh", max_length=100, blank=True)
    # Khối ký chỉ được in khi đơn vị đã phê duyệt cấu hình (REQ-GEN-17, XN-14).
    khoi_ky_da_phe_duyet = models.BooleanField("khối ký đã được đơn vị phê duyệt", default=False)
    can_cu_phe_duyet = models.CharField(
        "căn cứ phê duyệt khối ký", max_length=300, blank=True,
        help_text="Ví dụ: số, ngày văn bản hoặc biên bản đơn vị phê duyệt mẫu ký.",
    )
    o_ky = models.JSONField(
        "các ô ký", default=o_ky_mac_dinh, blank=True,
        help_text='Danh sách {"chuc_danh": "...", "nguoi_lap_so": true/false, "ap_dung": ["SO-01", ...]}; '
                  "không có “ap_dung” là áp dụng cho mọi sổ.",
    )
    dien_san_ngay_ky = models.BooleanField("điền sẵn ngày ký bằng ngày trích xuất", default=False)
    nguong_ghi_bo_sung_phut = models.PositiveIntegerField("ngưỡng ghi bổ sung (phút)", default=30)
    gio_giao_ca = models.TimeField("giờ giao ca", default=datetime.time(7, 30))

    class Meta:
        verbose_name = "cấu hình sổ"
        verbose_name_plural = "cấu hình sổ"

    def clean(self):
        from .trinh_bay import kiem_tra_o_ky

        loi = kiem_tra_o_ky(self.o_ky)
        if loi:
            raise ValidationError({"o_ky": loi})
        if self.khoi_ky_da_phe_duyet and not self.can_cu_phe_duyet.strip():
            raise ValidationError({"can_cu_phe_duyet": "Ghi căn cứ phê duyệt trước khi bật khối ký."})

    @classmethod
    def lay(cls):
        cau_hinh = cls.objects.order_by("pk").first()
        return cau_hinh or cls()


class BoDemTrichXuat(models.Model):
    """Bộ đếm cấp số thứ tự mã trích xuất theo ngày (BR-TX-02)."""

    ngay = models.DateField(unique=True)
    gia_tri = models.PositiveIntegerField(default=0)

    @classmethod
    def cap_so(cls, ngay):
        with transaction.atomic():
            bo_dem, _ = cls.objects.select_for_update().get_or_create(ngay=ngay)
            bo_dem.gia_tri += 1
            bo_dem.save(update_fields=["gia_tri"])
            return bo_dem.gia_tri


class LichSuXuat(models.Model):
    """Nhật ký trích xuất (BR-TX-05). Không sửa/xoá qua giao diện."""

    class KetQua(models.TextChoices):
        DANG_XU_LY = "DANG_XU_LY", "Đang xử lý"
        THANH_CONG = "THANH_CONG", "Thành công"
        THAT_BAI = "THAT_BAI", "Thất bại"

    ma_trich_xuat = models.CharField("mã trích xuất", max_length=40, unique=True)
    # Mã tải tệp: ngẫu nhiên, không suy ra được từ mã trích xuất (tăng dần) hay khoá chính.
    ma_tai = models.UUIDField("mã tải", default=uuid.uuid4, unique=True, editable=False)
    ma_so = models.CharField("mã sổ", max_length=10, db_index=True)
    phien_ban_mau = models.CharField("phiên bản mẫu", max_length=20, blank=True)
    dinh_dang = models.CharField("định dạng", max_length=10, default="xlsx")
    tu = models.DateTimeField("kỳ từ")
    den = models.DateTimeField("kỳ đến (không gồm)")
    thoi_diem_chot = models.DateTimeField("thời điểm chốt", null=True, blank=True)
    bat_dau_luc = models.DateTimeField("bắt đầu lúc", default=timezone.now)
    thoi_diem_trich_xuat = models.DateTimeField("thời điểm trích xuất", null=True, blank=True)
    ket_thuc_luc = models.DateTimeField("kết thúc lúc", null=True, blank=True)
    nguoi_xuat = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", verbose_name="người xuất"
    )
    nguoi_lap_so = models.CharField("người lập sổ", max_length=200, blank=True)
    dieu_kien_loc = models.JSONField("điều kiện lọc", default=dict)
    du_lieu_ca_nhan_day_du = models.BooleanField(default=False)
    ket_qua = models.CharField("kết quả", max_length=12, choices=KetQua.choices, default=KetQua.DANG_XU_LY)
    loi = models.TextField("lỗi", blank=True)
    so_dong = models.PositiveIntegerField("số dòng", null=True, blank=True)
    chi_tieu = models.JSONField("chỉ tiêu", default=dict)
    ten_file = models.CharField("tên file", max_length=200, blank=True)
    sha256 = models.CharField(max_length=64, blank=True)
    dia_chi_ip = models.GenericIPAddressField(null=True, blank=True)
    so_lan_tai = models.PositiveIntegerField("số lần tải", default=0)
    tai_lan_cuoi = models.DateTimeField("tải lần cuối", null=True, blank=True)

    class Meta:
        verbose_name = "lịch sử xuất"
        verbose_name_plural = "lịch sử xuất"
        ordering = ["-bat_dau_luc"]

    def __str__(self):
        return f"{self.ma_trich_xuat} ({self.get_ket_qua_display()})"


class BanChotXuat(models.Model):
    """Bản chốt của một lần xuất thành công: tệp đã tạo và dữ liệu đã dùng để tạo tệp.

    Tải lại luôn trả đúng tệp này (kiểm tra SHA-256), không truy vấn lại dữ liệu hiện hành,
    nên bản đã xuất giữ nguyên dù dữ liệu gốc về sau được đính chính (BR-DC-07).
    """

    lich_su = models.OneToOneField(LichSuXuat, on_delete=models.PROTECT, related_name="ban_chot")
    noi_dung = models.BinaryField("nội dung tệp")
    kich_thuoc = models.PositiveIntegerField("kích thước (byte)")
    du_lieu = models.JSONField("dữ liệu đã chốt")
    tao_luc = models.DateTimeField("tạo lúc", default=timezone.now)

    class Meta:
        verbose_name = "bản chốt xuất sổ"
        verbose_name_plural = "bản chốt xuất sổ"
