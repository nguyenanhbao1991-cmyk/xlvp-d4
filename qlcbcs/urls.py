from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

admin.site.site_header = settings.TEN_HE_THONG
admin.site.site_title = settings.TEN_HE_THONG
admin.site.index_title = "Quản trị"

urlpatterns = [
    # Địa chỉ gốc chuyển tới màn hình chính, tránh trang "Not Found" khi người dùng gõ http://<máy-chủ>:8000/.
    path("", RedirectView.as_view(pattern_name="baocao:man_hinh_xuat", permanent=False)),
    path("admin/", admin.site.urls),
    path("so/", include("baocao.urls")),
]
