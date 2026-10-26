from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET

from . import quyen
from django.core.exceptions import ValidationError

from .dich_vu import MIME, LoiGioiHan, LoiXuat, kiem_tra_ky_theo_dinh_dang, xuat
from .forms import FORM_THEO_SO


def _dinh_nghia(duong_dan):
    try:
        return quyen.SO_THEO_DUONG_DAN[duong_dan]
    except KeyError:
        raise Http404("Không có sổ này.")


@login_required
@require_GET
def danh_sach(request):
    cac_so = []
    for dn in quyen.SO.values():
        if request.user.has_perm(dn.quyen_xem):
            cac_so.append({
                "dinh_nghia": dn,
                "duoc_xuat": request.user.has_perm(dn.quyen_xuat),
                "form": FORM_THEO_SO[dn.ma](nguoi_dung=request.user, initial={"ky": "hom_nay"}),
            })
    return render(request, "baocao/danh_sach.html", {"cac_so": cac_so})


@login_required
@require_GET
def xuat_so(request, duong_dan, dinh_dang="xlsx"):
    dn = _dinh_nghia(duong_dan)
    # Kiểm tra quyền trước cả kiểm tra tham số để không lộ thông tin cho người không có quyền.
    quyen.kiem_tra_quyen_so(request.user, dn, xuat=True)
    form = FORM_THEO_SO[dn.ma](request.GET, nguoi_dung=request.user)
    if not form.is_valid():
        loi = "; ".join(f"{form.fields[k].label if k in form.fields else k}: {' '.join(v)}"
                        for k, v in form.errors.items())
        return HttpResponseBadRequest(f"Tham số không hợp lệ — {loi}", content_type="text/plain; charset=utf-8")
    ky = form.cleaned_data["ky_bao_cao"]
    try:
        kiem_tra_ky_theo_dinh_dang(dn, ky, dinh_dang)
    except ValidationError as loi:
        return HttpResponseBadRequest(f"Tham số không hợp lệ — Kỳ: {' '.join(loi.messages)}",
                                      content_type="text/plain; charset=utf-8")
    try:
        tep = xuat(
            request.user, dn, ky, form.bo_loc(), form.ten_nguoi_lap_so(),
            du_lieu_ca_nhan_day_du=form.cleaned_data.get("du_lieu_day_du", False),
            dia_chi_ip=request.META.get("REMOTE_ADDR"), dinh_dang=dinh_dang,
        )
    except LoiXuat as loi:
        # Vượt giới hạn định dạng là yêu cầu không xử lý được (422), không phải lỗi máy chủ.
        trang_thai = 422 if isinstance(loi.__cause__, LoiGioiHan) else 500
        return HttpResponse(
            f"Xuất thất bại ({loi.lich_su.ma_trich_xuat}): {loi}", status=trang_thai,
            content_type="text/plain; charset=utf-8",
        )
    phan_hoi = HttpResponse(tep.noi_dung, content_type=MIME[dinh_dang])
    phan_hoi["Content-Disposition"] = f'attachment; filename="{tep.ten_file}"'
    phan_hoi["X-Ma-Trich-Xuat"] = tep.lich_su.ma_trich_xuat
    phan_hoi["Cache-Control"] = "no-store"
    return phan_hoi
