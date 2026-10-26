"""Nguồn thời gian duy nhất của các sổ (BR-KY-01).

Mọi nơi lấy "bây giờ" đều gọi ``dong_ho.hien_tai()`` để kiểm thử có thể
giả lập đồng hồ máy chủ (test_plan.md §3).
"""
from django.utils import timezone


def hien_tai():
    return timezone.now()
