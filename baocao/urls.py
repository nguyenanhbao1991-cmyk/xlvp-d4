from django.urls import path

from . import man_hinh, views

app_name = "baocao"

urlpatterns = [
    path("", views.danh_sach, name="danh_sach"),
    path("xuat/", man_hinh.man_hinh_xuat, name="man_hinh_xuat"),
    path("tai/<uuid:ma_tai>/", man_hinh.tai_tep, name="tai_tep"),
    path("<slug:duong_dan>/xuat-excel/", views.xuat_so, {"dinh_dang": "xlsx"}, name="xuat_excel"),
    path("<slug:duong_dan>/xuat-word/", views.xuat_so, {"dinh_dang": "docx"}, name="xuat_word"),
    path("<slug:duong_dan>/xuat-pdf/", views.xuat_so, {"dinh_dang": "pdf"}, name="xuat_pdf"),
]
