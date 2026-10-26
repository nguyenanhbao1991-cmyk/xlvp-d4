from django.contrib import admin

from .models import CanBo, Cong, DinhChinh, DonVi, Khach, Luot, PhanCongCong, PhuongTien

admin.site.register([Cong, DonVi, CanBo, Khach, PhuongTien, PhanCongCong])


@admin.register(Luot)
class LuotAdmin(admin.ModelAdmin):
    list_display = ["id", "nhom", "chieu", "mo_thoi_diem", "dong_thoi_diem", "da_huy"]
    list_filter = ["nhom", "chieu", "da_huy"]

    def has_delete_permission(self, request, obj=None):
        return False  # BR-DC-01: không xoá, chỉ huỷ.


@admin.register(DinhChinh)
class DinhChinhAdmin(admin.ModelAdmin):
    list_display = ["luot", "truong", "gia_tri_cu", "gia_tri_moi", "nguoi", "thoi_diem"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
