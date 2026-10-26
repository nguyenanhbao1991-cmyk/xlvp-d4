from django.urls import path

from . import views

app_name = "baocao"

urlpatterns = [
    path("", views.danh_sach, name="danh_sach"),
    path("<slug:duong_dan>/xuat-excel/", views.xuat, name="xuat_excel"),
]
