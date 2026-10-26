from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # Địa chỉ gốc chuyển tới màn hình chính, tránh trang "Not Found" khi người dùng gõ http://<máy-chủ>:8000/.
    path("", RedirectView.as_view(pattern_name="baocao:man_hinh_xuat", permanent=False)),
    path("admin/", admin.site.urls),
    path("so/", include("baocao.urls")),
]
