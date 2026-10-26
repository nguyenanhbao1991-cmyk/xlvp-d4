"""Dữ liệu ghi nhận ra/vào mà các sổ sử dụng (requirements.md §5).

Một bản ghi ``Luot`` là một lượt: sự kiện mở và (nếu có) sự kiện đóng của
cùng một đối tượng (BR-LT-01). Lượt không bao giờ bị xoá: nhập nhầm thì huỷ
(BR-DC-06), sửa giá trị thì đính chính có lưu vết (BR-DC-01).
"""
import re

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


def chuan_hoa_ma(gia_tri):
    """Bỏ khoảng trắng, dấu chấm, gạch; in hoa (BR-DN-02, BR-DN-03)."""
    return re.sub(r"[\s.\-]", "", gia_tri or "").upper()


class Cong(models.Model):
    ma = models.CharField("mã cổng", max_length=20, unique=True)
    ten = models.CharField("tên cổng", max_length=100)
    thu_tu = models.PositiveIntegerField("thứ tự", default=0)

    class Meta:
        verbose_name = "cổng"
        verbose_name_plural = "cổng"
        ordering = ["thu_tu", "ma"]

    def __str__(self):
        return self.ten


class DonVi(models.Model):
    ten = models.CharField("tên đơn vị/bộ phận", max_length=200, unique=True)

    class Meta:
        verbose_name = "đơn vị/bộ phận"
        verbose_name_plural = "đơn vị/bộ phận"
        ordering = ["ten"]

    def __str__(self):
        return self.ten


class CanBo(models.Model):
    # Mã là chuỗi để giữ số 0 ở đầu.
    ma = models.CharField("mã CBCS", max_length=30, unique=True)
    ho_ten = models.CharField("họ và tên", max_length=200)
    cap_bac = models.CharField("cấp bậc", max_length=100, blank=True)
    chuc_vu = models.CharField("chức vụ", max_length=200, blank=True)
    don_vi = models.ForeignKey(DonVi, on_delete=models.PROTECT, verbose_name="đơn vị/bộ phận")

    class Meta:
        verbose_name = "CBCS"
        verbose_name_plural = "CBCS"
        ordering = ["ma"]

    def __str__(self):
        return f"{self.ma} {self.ho_ten}"


class Khach(models.Model):
    ho_ten = models.CharField("họ và tên", max_length=200)
    loai_giay_to = models.CharField("loại giấy tờ", max_length=50, blank=True)
    so_giay_to = models.CharField("số giấy tờ", max_length=50, blank=True)
    so_giay_to_chuan = models.CharField(max_length=50, blank=True, editable=False, db_index=True)
    co_quan = models.CharField("cơ quan/địa chỉ", max_length=300, blank=True)
    # Không in lên sổ khi chưa được đơn vị xác nhận (XN-08, BR-BM-03).
    so_dien_thoai = models.CharField("số điện thoại", max_length=30, blank=True)

    class Meta:
        verbose_name = "khách"
        verbose_name_plural = "khách"

    def save(self, *args, **kwargs):
        self.so_giay_to_chuan = chuan_hoa_ma(self.so_giay_to)
        super().save(*args, **kwargs)

    @property
    def dinh_danh(self):
        """Khoá định danh duy nhất, ``None`` nếu không định danh (BR-DN-02)."""
        if not self.so_giay_to_chuan:
            return None
        return (chuan_hoa_ma(self.loai_giay_to), self.so_giay_to_chuan)

    def __str__(self):
        return self.ho_ten


class PhuongTien(models.Model):
    class Nguon(models.TextChoices):
        CO_QUAN = "CO_QUAN", "Cơ quan"
        CBCS = "CBCS", "CBCS"
        KHACH = "KHACH", "Khách"
        KHAC = "KHAC", "Khác"

    bien_so = models.CharField("biển số", max_length=30, blank=True)
    bien_so_chuan = models.CharField(max_length=30, blank=True, editable=False, db_index=True)
    ma_tam = models.CharField("mã tạm (xe không biển)", max_length=30, blank=True)
    loai = models.CharField("loại phương tiện", max_length=100)
    nguon = models.CharField("nguồn", max_length=10, choices=Nguon.choices)
    nguon_can_bo = models.ForeignKey(
        CanBo, null=True, blank=True, on_delete=models.PROTECT, verbose_name="CBCS sở hữu"
    )
    nguon_khach = models.ForeignKey(
        Khach, null=True, blank=True, on_delete=models.PROTECT, verbose_name="khách sở hữu"
    )
    nguon_ghi_chu = models.CharField("ghi rõ nguồn", max_length=200, blank=True)

    class Meta:
        verbose_name = "phương tiện"
        verbose_name_plural = "phương tiện"
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(bien_so="") | ~models.Q(ma_tam=""),
                name="phuong_tien_co_bien_so_hoac_ma_tam",
            ),
        ]

    def save(self, *args, **kwargs):
        self.bien_so_chuan = chuan_hoa_ma(self.bien_so)
        super().save(*args, **kwargs)

    @property
    def khong_bien(self):
        return not self.bien_so_chuan

    @property
    def dinh_danh(self):
        return self.bien_so_chuan or None

    @property
    def hien_thi_bien_so(self):
        return self.bien_so if self.bien_so else f"Không biển — {self.ma_tam}"

    def __str__(self):
        return self.hien_thi_bien_so


class Luot(models.Model):
    class Nhom(models.TextChoices):
        CBCS = "CBCS", "CBCS"
        KHACH = "KHACH", "Khách"
        PHUONG_TIEN = "PT", "Phương tiện"

    class Chieu(models.TextChoices):
        RA_VAO = "RV", "Ra–Vào"
        VAO_RA = "VR", "Vào–Ra"

    nhom = models.CharField("nhóm đối tượng", max_length=5, choices=Nhom.choices, db_index=True)
    can_bo = models.ForeignKey(CanBo, null=True, blank=True, on_delete=models.PROTECT, related_name="luot")
    khach = models.ForeignKey(Khach, null=True, blank=True, on_delete=models.PROTECT, related_name="luot")
    phuong_tien = models.ForeignKey(
        PhuongTien, null=True, blank=True, on_delete=models.PROTECT, related_name="luot"
    )
    chieu = models.CharField("chiều lượt", max_length=2, choices=Chieu.choices)

    mo_thoi_diem = models.DateTimeField("thời điểm sự kiện mở", db_index=True)
    mo_cong = models.ForeignKey(Cong, on_delete=models.PROTECT, related_name="+", verbose_name="cổng mở")
    mo_ghi_nhan_luc = models.DateTimeField("ghi nhận sự kiện mở lúc", default=timezone.now)
    mo_nguoi_ghi = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", verbose_name="người ghi sự kiện mở"
    )
    dong_thoi_diem = models.DateTimeField("thời điểm sự kiện đóng", null=True, blank=True, db_index=True)
    dong_cong = models.ForeignKey(
        Cong, null=True, blank=True, on_delete=models.PROTECT, related_name="+", verbose_name="cổng đóng"
    )
    dong_ghi_nhan_luc = models.DateTimeField("ghi nhận sự kiện đóng lúc", null=True, blank=True)
    dong_nguoi_ghi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="người ghi sự kiện đóng",
    )
    han_du_kien = models.DateTimeField("hạn về/ra dự kiến", null=True, blank=True)

    # CBCS
    ly_do = models.CharField("lý do", max_length=100, blank=True)
    ly_do_chi_tiet = models.CharField("nội dung", max_length=500, blank=True)
    phuong_tien_di_kem = models.ForeignKey(
        PhuongTien, null=True, blank=True, on_delete=models.PROTECT, related_name="+",
        verbose_name="phương tiện đi kèm",
    )
    # Khách
    muc_dich = models.CharField("mục đích", max_length=500, blank=True)
    nguoi_tiep = models.CharField("người/bộ phận tiếp", max_length=200, blank=True)
    so_the = models.CharField("số thẻ khách", max_length=20, blank=True)
    ma_doan = models.CharField("mã đoàn", max_length=30, blank=True)
    # Phương tiện
    nguoi_dieu_khien = models.CharField("người điều khiển", max_length=200, blank=True)
    nguoi_dieu_khien_can_bo = models.ForeignKey(
        CanBo, null=True, blank=True, on_delete=models.PROTECT, related_name="+",
        verbose_name="CBCS điều khiển",
    )
    lenh_dieu_xe = models.CharField("số lệnh điều xe", max_length=50, blank=True)

    ghi_chu = models.TextField("ghi chú", max_length=2000, blank=True)

    da_huy = models.BooleanField("đã huỷ", default=False)
    ly_do_huy = models.CharField("lý do huỷ", max_length=500, blank=True)
    huy_luc = models.DateTimeField(null=True, blank=True)
    huy_boi = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )

    class Meta:
        verbose_name = "lượt ra/vào"
        verbose_name_plural = "lượt ra/vào"
        constraints = [
            models.CheckConstraint(
                name="luot_dung_mot_doi_tuong_theo_nhom",
                condition=(
                    models.Q(nhom="CBCS", can_bo__isnull=False, khach__isnull=True, phuong_tien__isnull=True)
                    | models.Q(nhom="KHACH", can_bo__isnull=True, khach__isnull=False, phuong_tien__isnull=True)
                    | models.Q(nhom="PT", can_bo__isnull=True, khach__isnull=True, phuong_tien__isnull=False)
                ),
            ),
            models.CheckConstraint(
                name="luot_khach_luon_vao_ra",
                condition=~models.Q(nhom="KHACH") | models.Q(chieu="VR"),
            ),
        ]
        permissions = [
            ("xem_so_cbcs", "Xem sổ CBCS ra/vào"),
            ("xuat_so_cbcs", "Xuất sổ CBCS ra/vào"),
            ("xem_so_khach", "Xem sổ khách ra/vào"),
            ("xuat_so_khach", "Xuất sổ khách ra/vào"),
            ("xem_so_phuong_tien", "Xem sổ phương tiện ra/vào"),
            ("xuat_so_phuong_tien", "Xuất sổ phương tiện ra/vào"),
            ("xem_so_tong_hop", "Xem sổ tổng hợp ra/vào"),
            ("xuat_so_tong_hop", "Xuất sổ tổng hợp ra/vào"),
            ("xem_ban_ghi_huy", "Xem bản ghi đã huỷ trên sổ"),
            ("xem_du_lieu_ca_nhan_day_du", "Xem/xuất dữ liệu cá nhân đầy đủ"),
            ("xem_moi_cong", "Xem dữ liệu của mọi cổng"),
        ]

    @property
    def doi_tuong(self):
        return {"CBCS": self.can_bo, "KHACH": self.khach, "PT": self.phuong_tien}[self.nhom]

    @transaction.atomic
    def dinh_chinh(self, truong, gia_tri_moi, ly_do, nguoi):
        """Đính chính một trường, lưu giá trị cũ (BR-DC-01, BR-DC-02).

        ``truong`` là tên trường của lượt, hoặc ``khach.so_giay_to`` /
        ``phuong_tien.bien_so`` với trường của đối tượng.
        """
        if not (ly_do or "").strip():
            raise ValueError("Đính chính phải có lý do.")
        doi_tuong, ten = (self, truong)
        if "." in truong:
            ten_quan_he, ten = truong.split(".", 1)
            doi_tuong = getattr(self, ten_quan_he)
        gia_tri_cu = getattr(doi_tuong, ten)
        setattr(doi_tuong, ten, gia_tri_moi)
        doi_tuong.save()
        return DinhChinh.objects.create(
            luot=self,
            truong=truong,
            gia_tri_cu=DinhChinh.bieu_dien(gia_tri_cu),
            gia_tri_moi=DinhChinh.bieu_dien(gia_tri_moi),
            ly_do=ly_do,
            nguoi=nguoi,
        )

    @transaction.atomic
    def huy(self, ly_do, nguoi):
        if not (ly_do or "").strip():
            raise ValueError("Huỷ phải có lý do.")
        self.da_huy = True
        self.ly_do_huy = ly_do
        self.huy_luc = timezone.now()
        self.huy_boi = nguoi
        self.save(update_fields=["da_huy", "ly_do_huy", "huy_luc", "huy_boi"])

    def __str__(self):
        return f"Lượt {self.pk} ({self.get_nhom_display()})"


class DinhChinh(models.Model):
    TRUONG_DU_LIEU_CA_NHAN = {"khach.so_giay_to"}

    luot = models.ForeignKey(Luot, on_delete=models.PROTECT, related_name="dinh_chinh_set")
    truong = models.CharField("trường", max_length=100)
    gia_tri_cu = models.TextField("giá trị cũ", blank=True)
    gia_tri_moi = models.TextField("giá trị mới", blank=True)
    ly_do = models.CharField("lý do", max_length=500)
    nguoi = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    thoi_diem = models.DateTimeField("thời điểm đính chính", default=timezone.now)

    class Meta:
        verbose_name = "đính chính"
        verbose_name_plural = "đính chính"
        ordering = ["thoi_diem", "id"]

    @staticmethod
    def bieu_dien(gia_tri):
        if gia_tri is None:
            return ""
        if hasattr(gia_tri, "isoformat"):
            return timezone.localtime(gia_tri).strftime("%H:%M %d/%m/%Y")
        if isinstance(gia_tri, models.Model):
            return str(gia_tri)
        return str(gia_tri)

    @property
    def la_du_lieu_ca_nhan(self):
        return self.truong in self.TRUONG_DU_LIEU_CA_NHAN


class PhanCongCong(models.Model):
    """Giới hạn người dùng chỉ xem dữ liệu của các cổng được phân công (XN-02)."""

    nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="phan_cong_cong")
    cong = models.ForeignKey(Cong, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "phân công cổng"
        verbose_name_plural = "phân công cổng"
        constraints = [models.UniqueConstraint(fields=["nguoi_dung", "cong"], name="phan_cong_cong_duy_nhat")]
