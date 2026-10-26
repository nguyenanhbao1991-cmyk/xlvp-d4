from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET

from . import quyen
from .dich_vu import MIME_XLSX, LoiXuat, xuat_excel
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
def xuat(request, duong_dan):
    dn = _dinh_nghia(duong_dan)
    # Kiểm tra quyền trước cả kiểm tra tham số để không lộ thông tin cho người không có quyền.
    quyen.kiem_tra_quyen_so(request.user, dn, xuat=True)
    form = FORM_THEO_SO[dn.ma](request.GET, nguoi_dung=request.user)
    if not form.is_valid():
        loi = "; ".join(f"{form.fields[k].label if k in form.fields else k}: {' '.join(v)}"
                        for k, v in form.errors.items())
        return HttpResponseBadRequest(f"Tham số không hợp lệ — {loi}", content_type="text/plain; charset=utf-8")
    try:
        tep = xuat_excel(
            request.user, dn, form.cleaned_data["ky_bao_cao"], form.bo_loc(), form.ten_nguoi_lap_so(),
            du_lieu_ca_nhan_day_du=form.cleaned_data.get("du_lieu_day_du", False),
            dia_chi_ip=request.META.get("REMOTE_ADDR"),
        )
    except LoiXuat as loi:
        return HttpResponse(
            f"Xuất thất bại ({loi.lich_su.ma_trich_xuat}): {loi}", status=500,
            content_type="text/plain; charset=utf-8",
        )
    phan_hoi = HttpResponse(tep.noi_dung, content_type=MIME_XLSX)
    phan_hoi["Content-Disposition"] = f'attachment; filename="{tep.ten_file}"'
    phan_hoi["X-Ma-Trich-Xuat"] = tep.lich_su.ma_trich_xuat
    phan_hoi["Cache-Control"] = "no-store"
    return phan_hoi
