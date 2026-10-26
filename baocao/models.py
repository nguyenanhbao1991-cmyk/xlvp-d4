import datetime

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class CauHinhSo(models.Model):
    """Cấu hình in trên sổ (REQ-GEN-21). Chỉ dùng một bản ghi."""

    co_quan_chu_quan = models.CharField("cơ quan chủ quản", max_length=200, blank=True)
    ten_don_vi = models.CharField("tên đơn vị", max_length=200, default="")
    dia_danh = models.CharField("địa danh", max_length=100, blank=True)
    chuc_danh_xac_nhan = models.CharField("chức danh xác nhận", max_length=100, default="Chỉ huy đơn vị")
    nguong_ghi_bo_sung_phut = models.PositiveIntegerField("ngưỡng ghi bổ sung (phút)", default=30)
    gio_giao_ca = models.TimeField("giờ giao ca", default=datetime.time(7, 30))

    class Meta:
        verbose_name = "cấu hình sổ"
        verbose_name_plural = "cấu hình sổ"

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
    ma_so = models.CharField("mã sổ", max_length=10, db_index=True)
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

    class Meta:
        verbose_name = "lịch sử xuất"
        verbose_name_plural = "lịch sử xuất"
        ordering = ["-bat_dau_luc"]

    def __str__(self):
        return f"{self.ma_trich_xuat} ({self.get_ket_qua_display()})"
