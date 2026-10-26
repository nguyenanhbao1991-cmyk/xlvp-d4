from django.contrib import admin

from .models import CauHinhSo, LichSuXuat

admin.site.register(CauHinhSo)


@admin.register(LichSuXuat)
class LichSuXuatAdmin(admin.ModelAdmin):
    list_display = ["ma_trich_xuat", "ma_so", "tu", "den", "nguoi_xuat", "bat_dau_luc", "ket_qua", "so_dong"]
    list_filter = ["ma_so", "ket_qua"]
    search_fields = ["ma_trich_xuat"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
