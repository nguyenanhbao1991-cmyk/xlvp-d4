"""Màn hình "Xuất sổ theo dõi" và tải tệp đã xuất."""
import hashlib
import logging
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import F
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from . import dong_ho, quyen, xem_truoc
from .dich_vu import MIME, LoiGioiHan, LoiXuat, kha_nang_dinh_dang, kiem_tra_ky_theo_dinh_dang, xuat
from .forms import FORM_THEO_SO, TRUONG_KY_CU, FormXuatSo, tien_to
from .models import BanChotXuat, LichSuXuat

logger = logging.getLogger(__name__)
SO_LICH_SU_GAN_DAY = 10


def _cac_so_duoc_xem(nguoi_dung):
    return [dn for dn in quyen.SO.values() if nguoi_dung.has_perm(dn.quyen_xem)]


def _form_bo_loc(dn, nguoi_dung, du_lieu=None, ky=None):
    return FORM_THEO_SO[dn.ma](du_lieu, prefix=tien_to(dn), nguoi_dung=nguoi_dung, ky_co_dinh=ky)


def _lich_su_cua(nguoi_dung):
    return LichSuXuat.objects.filter(nguoi_xuat=nguoi_dung).order_by("-bat_dau_luc", "-pk")


def _trang(request, form, cac_so, bo_loc=None, xem=None, ket_qua=None, trang_thai=200):
    nhom_bo_loc = []
    for dn in cac_so:
        f = (bo_loc or {}).get(dn.ma) or _form_bo_loc(dn, request.user)
        nhom_bo_loc.append({
            "dinh_nghia": dn,
            "duoc_xuat": request.user.has_perm(dn.quyen_xuat),
            "truong": [t for t in f if t.name not in TRUONG_KY_CU],
            "loi_chung": f.non_field_errors() if f.is_bound else [],
        })
    return render(request, "baocao/xuat_so.html", {
        "form": form,
        "nhom_bo_loc": nhom_bo_loc,
        "xem": xem,
        "ket_qua": ket_qua,
        "kha_nang": kha_nang_dinh_dang(),
        "lich_su": _lich_su_cua(request.user)[:SO_LICH_SU_GAN_DAY],
    }, status=trang_thai)


@login_required
@require_http_methods(["GET", "POST"])
def man_hinh_xuat(request):
    cac_so = _cac_so_duoc_xem(request.user)
    if not cac_so:
        raise PermissionDenied("Bạn không có quyền xem sổ nào.")
    kha_nang = kha_nang_dinh_dang()

    if request.method == "GET":
        ket_qua = None
        ma = request.GET.get("ket_qua")
        if ma:
            # Chỉ hiện kết quả của chính người dùng; mã lạ hoặc của người khác thì bỏ qua.
            ket_qua = _lich_su_cua(request.user).filter(ma_tai=_uuid_hay_none(ma)).first()
        ngay = dong_ho.hien_tai()
        hom_nay = timezone.localtime(ngay, timezone.get_default_timezone()).date()
        form = FormXuatSo(cac_so=cac_so, kha_nang=kha_nang, initial={
            "ngay": hom_nay, "tu_ngay": hom_nay, "den_ngay": hom_nay, "thang": f"{hom_nay:%Y-%m}"})
        return _trang(request, form, cac_so, ket_qua=ket_qua)

    form = FormXuatSo(request.POST, cac_so=cac_so, kha_nang=kha_nang)
    hanh_dong = request.POST.get("hanh_dong")
    if hanh_dong not in ("xem_truoc", "xuat"):
        messages.error(request, "Thao tác không hợp lệ.")
        return _trang(request, form, cac_so, trang_thai=400)
    if not form.is_valid():
        messages.error(request, "Chưa xuất: kiểm tra lại các ô được đánh dấu.")
        return _trang(request, form, cac_so, trang_thai=400)

    dn = quyen.SO[form.cleaned_data["loai_so"]]
    ky = form.cleaned_data["ky_bao_cao"]
    dinh_dang = form.cleaned_data["dinh_dang"]
    f_loc = _form_bo_loc(dn, request.user, request.POST, ky)
    bo_loc_da_gan = {dn.ma: f_loc}
    if not f_loc.is_valid():
        messages.error(request, "Chưa xuất: bộ lọc của sổ có giá trị không hợp lệ.")
        return _trang(request, form, cac_so, bo_loc_da_gan, trang_thai=400)
    bo_loc = f_loc.bo_loc()
    day_du = f_loc.cleaned_data.get("du_lieu_day_du", False)

    if hanh_dong == "xem_truoc":
        try:
            xem = xem_truoc.lap(request.user, dn, ky, bo_loc, day_du, dinh_dang)
        except PermissionDenied as loi:
            messages.error(request, f"Không xem trước được: {loi}")
            return _trang(request, form, cac_so, bo_loc_da_gan, trang_thai=403)
        # Gửi kèm số dòng xem trước để khi xuất có thể báo nếu dữ liệu đã thay đổi.
        du_lieu = request.POST.copy()
        du_lieu["so_dong_xem_truoc"] = str(xem.so_dong)
        form = FormXuatSo(du_lieu, cac_so=cac_so, kha_nang=kha_nang)
        form.is_valid()
        return _trang(request, form, cac_so, bo_loc_da_gan, xem=xem)

    # Xuất: quyền được kiểm tra trước khi cấp mã, ghi lịch sử hay tạo tệp.
    try:
        kiem_tra_ky_theo_dinh_dang(dn, ky, dinh_dang)
        tep = xuat(request.user, dn, ky, bo_loc, f_loc.ten_nguoi_lap_so(), du_lieu_ca_nhan_day_du=day_du,
                   dia_chi_ip=request.META.get("REMOTE_ADDR"), dinh_dang=dinh_dang)
    except PermissionDenied as loi:
        messages.error(request, f"Không xuất: {loi} Không có tệp nào được tạo.")
        return _trang(request, form, cac_so, bo_loc_da_gan, trang_thai=403)
    except ValidationError as loi:
        messages.error(request, "Không xuất: " + " ".join(loi.messages))
        return _trang(request, form, cac_so, bo_loc_da_gan, trang_thai=400)
    except LoiXuat as loi:
        loai = "vượt giới hạn" if isinstance(loi.__cause__, LoiGioiHan) else "lỗi khi tạo tệp"
        messages.error(request, f"Xuất thất bại ({loai}, mã {loi.lich_su.ma_trich_xuat}): {loi}")
        return redirect(f"{reverse('baocao:man_hinh_xuat')}?ket_qua={loi.lich_su.ma_tai}")

    ls = tep.lich_su
    messages.success(request, f"Đã tạo tệp {ls.ten_file} — mã trích xuất {ls.ma_trich_xuat}, {ls.so_dong} dòng "
                              f"dữ liệu, số liệu tính đến "
                              f"{timezone.localtime(ls.thoi_diem_chot, timezone.get_default_timezone()):%H:%M:%S %d/%m/%Y} "
                              "(giờ Việt Nam).")
    so_dong_xem = form.cleaned_data.get("so_dong_xem_truoc")
    if so_dong_xem is not None and so_dong_xem != ls.so_dong:
        messages.warning(request, f"Dữ liệu đã thay đổi kể từ lúc xem trước (xem trước: {so_dong_xem} dòng, bản "
                                  f"xuất: {ls.so_dong} dòng). Bản xuất vừa tạo là bản chốt.")
    return redirect(f"{reverse('baocao:man_hinh_xuat')}?ket_qua={ls.ma_tai}")


def _uuid_hay_none(chuoi):
    try:
        return uuid.UUID(str(chuoi))
    except ValueError:
        return None


@login_required
@require_GET
def tai_tep(request, ma_tai):
    """Tải bản chốt của một lần xuất thành công.

    Chỉ người đã xuất tải được, và người đó vẫn phải còn quyền xuất sổ. Mọi trường hợp khác
    (mã của người khác, mã không tồn tại, lần xuất thất bại, đã mất quyền) đều trả 404 như nhau
    để không lộ việc tệp có tồn tại hay không.
    """
    ls = (LichSuXuat.objects.filter(ma_tai=ma_tai, nguoi_xuat=request.user, ket_qua=LichSuXuat.KetQua.THANH_CONG)
          .select_related("ban_chot").first())
    dn = quyen.SO.get(ls.ma_so) if ls else None
    if not ls or not dn or not request.user.has_perm(dn.quyen_xuat):
        raise Http404("Không tìm thấy tệp.")
    try:
        ban_chot = ls.ban_chot
    except BanChotXuat.DoesNotExist:
        raise Http404("Không tìm thấy tệp.")
    noi_dung = bytes(ban_chot.noi_dung)
    if hashlib.sha256(noi_dung).hexdigest() != ls.sha256:
        logger.error("Bản chốt %s không khớp mã băm đã ghi.", ls.ma_trich_xuat)
        return HttpResponse("Tệp lưu trữ không khớp mã kiểm tra; không tải. Hãy báo quản trị.", status=500,
                            content_type="text/plain; charset=utf-8")
    LichSuXuat.objects.filter(pk=ls.pk).update(so_lan_tai=F("so_lan_tai") + 1, tai_lan_cuoi=dong_ho.hien_tai())
    phan_hoi = HttpResponse(noi_dung, content_type=MIME[ls.dinh_dang])
    phan_hoi["Content-Disposition"] = f'attachment; filename="{ls.ten_file}"'
    phan_hoi["X-Ma-Trich-Xuat"] = ls.ma_trich_xuat
    phan_hoi["Cache-Control"] = "private, no-store"
    phan_hoi["X-Content-Type-Options"] = "nosniff"
    return phan_hoi
