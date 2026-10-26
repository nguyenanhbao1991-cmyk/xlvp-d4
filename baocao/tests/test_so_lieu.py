"""Số liệu các sổ trên DS-01/DS-02, đối chiếu kết quả mong đợi ở test_plan.md §5.2–§5.3."""
import datetime

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase

from ravao.models import CanBo, DinhChinh, Luot

from ..ky import KyBaoCao
from ..quyen import SO
from ..so_lieu import BoLoc, khoa_ho_ten, lap_so_chi_tiet, lap_so_tong_hop
from .du_lieu import DS01, t, tao_nguoi_dung

NGUONG = datetime.timedelta(minutes=30)
TRICH_XUAT_S1 = t("09:00 27/10")
KY_S1 = KyBaoCao(t("00:00 25/10"), t("00:00 26/10"))


def lap(nguoi, ma_so, ky=KY_S1, chot=None, bo_loc=None, trich_xuat=TRICH_XUAT_S1):
    chot = chot or min(ky.den, trich_xuat)
    ham = lap_so_tong_hop if ma_so == "SO-04" else lap_so_chi_tiet
    return ham(nguoi, SO[ma_so], ky, chot, bo_loc or BoLoc(), NGUONG, trich_xuat)


class SoChiTietS1Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ds = DS01()

    def ten_dong(self, kq):
        return [self.ds.ten(d.luot.pk) for d in kq.dong]

    def chi_tieu_chuan(self, kq):
        ct = kq.chi_tieu
        return (ct["tu_ky_truoc"], ct["phat_sinh"], ct["hoan_tat"], ct["chua_hoan_tat"], ct["dang_mo"],
                ct["hoan_tat_sau_ky"], ct["qua_han"])

    def test_so01_thu_tu_va_chi_tieu(self):
        kq = lap(self.ds.tb01, "SO-01")
        self.assertEqual(self.ten_dong(kq), ["C3", "C8", "C1", "C6", "C2", "C5", "C4"])
        self.assertEqual([d.stt for d in kq.dong], [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(self.chi_tieu_chuan(kq), (1, 6, 5, 2, 1, 1, 1))
        self.assertEqual(kq.chi_tieu["doi_tuong_duy_nhat"], 6)
        self.assertEqual(kq.chi_tieu["ban_ghi_huy"], 1)
        self.assertEqual(kq.chi_tieu["luot_dinh_chinh"], 1)
        self.assertEqual(kq.chi_tieu["theo_chieu"], {"Ra–Vào": 6, "Vào–Ra": 1})
        self.assertEqual(kq.chi_tieu["theo_ly_do"], {"Công tác": 4, "Việc riêng có phép": 2, "Không ghi": 1})

    def test_so02_chi_tieu_khach(self):
        kq = lap(self.ds.tb01, "SO-02")
        self.assertEqual(self.ten_dong(kq), ["K1", "K3", "K4", "K2", "K5", "K6"])
        self.assertEqual(self.chi_tieu_chuan(kq), (0, 6, 4, 2, 1, 1, 1))
        ct = kq.chi_tieu
        self.assertEqual((ct["doi_tuong_duy_nhat"], ct["khong_dinh_danh"], ct["so_doan"], ct["the_chua_thu_hoi"]),
                         (4, 1, 1, 2))

    def test_so03_chuan_hoa_bien_so(self):
        kq = lap(self.ds.tb01, "SO-03")
        self.assertEqual(self.ten_dong(kq), ["P1", "P3", "P5", "P2", "P4"])
        self.assertEqual(self.chi_tieu_chuan(kq), (0, 5, 4, 1, 1, 0, 0))
        ct = kq.chi_tieu
        self.assertEqual((ct["doi_tuong_duy_nhat"], ct["khong_dinh_danh"]), (3, 1))
        self.assertEqual(ct["theo_loai"], {"Ô tô": 3, "Xe chuyên dùng": 1, "Xe máy": 1})
        self.assertEqual(ct["theo_nguon"], {"Cơ quan": 2, "CBCS": 1, "Khác": 1, "Khách": 1})

    def test_qua_nua_dem(self):
        dong = {self.ds.ten(d.luot.pk): d for d in lap(self.ds.tb01, "SO-01").dong}
        c3, c4, c5 = dong["C3"], dong["C4"], dong["C5"]
        self.assertTrue(c3.tu_ky_truoc)
        self.assertEqual(c3.su_kien("RA").chu_thich, "(từ kỳ trước)")
        self.assertEqual(c3.thoi_luong, datetime.timedelta(hours=1, minutes=45))
        self.assertEqual((c4.trang_thai, c4.nhan_trang_thai, c4.su_kien("VAO").chu_thich),
                         ("HTS", "Hoàn tất sau kỳ", "(sau kỳ)"))
        self.assertEqual(c4.thoi_luong, datetime.timedelta(hours=1, minutes=35))
        self.assertEqual(c5.nhan_trang_thai, "Chưa về – Quá hạn")
        self.assertEqual((c5.thoi_luong, c5.thoi_luong_toi_thieu), (datetime.timedelta(hours=8), True))
        self.assertIsNone(c5.su_kien("VAO").thoi_diem)

    def test_luot_vao_ra_cua_cbcs(self):
        c8 = next(d for d in lap(self.ds.tb01, "SO-01").dong if d.luot == self.ds.l["C8"])
        self.assertEqual(c8.su_kien("VAO").thoi_diem, t("07:30 25/10"))
        self.assertEqual(c8.su_kien("RA").thoi_diem, t("17:15 25/10"))

    def test_dinh_chinh_va_ghi_bo_sung(self):
        kq = lap(self.ds.tb01, "SO-01")
        c6 = next(d for d in kq.dong if d.luot == self.ds.l["C6"])
        self.assertEqual(c6.ky_hieu, "ĐC(1)")
        (n, stt, _, dc), = kq.phu_luc
        self.assertEqual((n, stt, dc.gia_tri_cu, dc.gia_tri_moi), (1, 4, "09:14 25/10/2026", "09:40 25/10/2026"))
        k4 = next(d for d in lap(self.ds.tb01, "SO-02").dong if d.luot == self.ds.l["K4"])
        self.assertEqual(k4.ky_hieu, "GBS")

    def test_hien_ban_ghi_huy(self):
        kq = lap(self.ds.chihuy, "SO-01", bo_loc=BoLoc(hien_huy=True))
        self.assertEqual(self.ten_dong(kq), ["C3", "C8", "C1", "C6", "C7", "C2", "C5", "C4"])
        c7 = kq.dong[4]
        self.assertEqual((c7.stt, c7.nhan_trang_thai), (None, "ĐÃ HUỶ"))
        self.assertEqual(kq.chi_tieu["so_luot"], 7)
        with self.assertRaises(PermissionDenied):
            lap(self.ds.tb01, "SO-01", bo_loc=BoLoc(hien_huy=True))

    def test_bo_loc(self):
        tham_muu = self.ds.cb["CB001"].don_vi
        kq = lap(self.ds.tb01, "SO-01", bo_loc=BoLoc(don_vi=[tham_muu]))
        self.assertEqual(self.ten_dong(kq), ["C8", "C1", "C2"])
        self.assertEqual(kq.chi_tieu["doi_tuong_duy_nhat"], 2)
        self.assertEqual(self.ten_dong(lap(self.ds.tb01, "SO-01", bo_loc=BoLoc(cong=[self.ds.c2]))), ["C2", "C4"])
        self.assertEqual(self.ten_dong(lap(self.ds.tb01, "SO-01", bo_loc=BoLoc(trang_thai="CHUA_HOAN_TAT"))),
                         ["C5", "C4"])
        self.assertEqual(self.ten_dong(lap(self.ds.tb01, "SO-02", bo_loc=BoLoc(ma_doan="ĐK-01"))), ["K3", "K4"])
        self.assertEqual(self.ten_dong(lap(self.ds.tb01, "SO-03", bo_loc=BoLoc(bien_so="30A 123"))), ["P1", "P2"])

    def test_ky_chua_ket_thuc_s2(self):
        # S2: chỉ có dữ liệu đã ghi nhận đến 12:00 25/10.
        Luot.objects.filter(pk__in=[self.ds.l[k].pk for k in ("C2", "C5", "C4")]).delete()
        Luot.objects.filter(pk=self.ds.l["C8"].pk).update(dong_thoi_diem=None, dong_cong=None,
                                                          dong_ghi_nhan_luc=None, dong_nguoi_ghi=None)
        Luot.objects.filter(pk=self.ds.l["C6"].pk).update(dong_thoi_diem=t("09:14 25/10"))
        kq = lap(self.ds.tb01, "SO-01", trich_xuat=t("12:00 25/10"))
        self.assertEqual(kq.chot, t("12:00 25/10"))
        self.assertEqual(self.ten_dong(kq), ["C3", "C8", "C1", "C6"])
        self.assertEqual(self.chi_tieu_chuan(kq)[:4], (1, 3, 3, 1))
        c8 = kq.dong[1]
        self.assertEqual((c8.nhan_trang_thai, c8.thoi_luong), ("Chưa ra", datetime.timedelta(hours=4, minutes=30)))
        # Đính chính lúc 20:00 chưa xảy ra tại thời điểm trích xuất 12:00.
        self.assertEqual(kq.phu_luc, [])

    def test_tong_hop_s1(self):
        kq = lap(self.ds.tb01, "SO-04")
        a = kq.phan_a
        self.assertEqual([(a[n]["tu_ky_truoc"], a[n]["phat_sinh"], a[n]["hoan_tat"], a[n]["chua_hoan_tat"],
                           a[n]["qua_han"], a[n]["doi_tuong_duy_nhat"]) for n in ("CBCS", "KHACH", "PT")],
                         [(1, 6, 5, 2, 1, 6), (0, 6, 4, 2, 1, 4), (0, 5, 4, 1, 0, 3)])
        self.assertEqual({c.ma: so for c, so in kq.phan_c},
                         {"C1": {"CBCS": (4, 4), "KHACH": (6, 4), "PT": (3, 4)},
                          "C2": {"CBCS": (1, 2), "KHACH": (0, 0), "PT": (1, 1)}})
        self.assertEqual(kq.phan_c_cuoi, {"CBCS": (5, 6), "KHACH": (6, 4), "PT": (4, 5)})
        self.assertEqual({n: [self.ds.ten(d.luot.pk) for d in v] for n, v in kq.phan_d.items()},
                         {"CBCS": ["C5", "C4"], "KHACH": ["K5", "K6"], "PT": ["P4"]})

    def test_tong_hop_phan_bo_theo_ngay_s3(self):
        kq = lap(self.ds.tb01, "SO-04", ky=KyBaoCao(t("00:00 24/10"), t("00:00 26/10")))
        theo_ngay = {ngay.day: hang for ngay, hang in kq.phan_b}
        self.assertEqual(theo_ngay[24], {"CBCS": (2, 2), "KHACH": (0, 0), "PT": (0, 0)})
        self.assertEqual(theo_ngay[25], {"CBCS": (6, 6), "KHACH": (6, 4), "PT": (5, 3)})
        # Dòng cuối: lượt cộng được, đối tượng là duy nhất cả kỳ (6, không phải 8).
        self.assertEqual(kq.phan_b_cuoi, {"CBCS": (8, 6), "KHACH": (6, 4), "PT": (5, 3)})

    def test_pham_vi_cong_cua_nguoi_dung(self):
        from .du_lieu import phan_cong

        tb_cong_2 = tao_nguoi_dung("cong2", quyen=["xem_so_cbcs"])
        phan_cong(tb_cong_2, self.ds.c2)
        self.assertEqual(self.ten_dong(lap(tb_cong_2, "SO-01")), ["C2", "C4"])
        khong_cong = tao_nguoi_dung("khongcong", quyen=["xem_so_cbcs"])
        self.assertEqual(lap(khong_cong, "SO-01").dong, [])

    def test_khong_co_quyen_xem(self):
        nguoi = tao_nguoi_dung("chixemkhach", quyen=["xem_so_khach", "xem_moi_cong"])
        with self.assertRaises(PermissionDenied):
            lap(nguoi, "SO-01")


class TruongHopBienTest(TestCase):
    """DS-02 (test_plan.md §5.3)."""

    @classmethod
    def setUpTestData(cls):
        cls.ds = DS01()
        DinhChinh.objects.all().delete()
        Luot.objects.all().delete()
        don_vi = cls.ds.cb["CB001"].don_vi
        cls.cb = {ma: CanBo.objects.create(ma=ma, ho_ten=f"Cán bộ {ma}", don_vi=don_vi)
                  for ma in ("CB101", "CB102", "CB103", "CB104", "CB105", "CB107")}
        L = cls.ds._luot
        L("E1", "CBCS", "RV", "00:00 25/10", "00:30 25/10", can_bo=cls.cb["CB101"])
        L("E2", "CBCS", "RV", "23:00 24/10", "00:00 25/10", can_bo=cls.cb["CB102"])
        L("E3", "CBCS", "RV", "00:00 26/10", None, can_bo=cls.cb["CB103"])
        L("E4a", "CBCS", "RV", "08:00 25/10", None, can_bo=cls.cb["CB104"])
        L("E4b", "CBCS", "RV", "09:00 25/10", None, can_bo=cls.cb["CB104"])
        L("E5", "CBCS", "RV", "10:00 25/10", "09:50 25/10", can_bo=cls.cb["CB105"])
        L("E9", "CBCS", "RV", "08:00 20/10", None, can_bo=cls.cb["CB107"])

    def dong(self, ky=KY_S1):
        return {self.ds.ten(d.luot.pk): d for d in lap(self.ds.tb01, "SO-01", ky=ky).dong}

    def test_ranh_gioi_ky_nua_mo(self):
        d = self.dong()
        self.assertIn("E1", d)
        self.assertFalse(d["E1"].tu_ky_truoc)
        self.assertNotIn("E3", d)
        self.assertEqual((d["E2"].tu_ky_truoc, d["E2"].trang_thai), (True, "HT"))
        hom_truoc = self.dong(KyBaoCao(t("00:00 24/10"), t("00:00 25/10")))
        self.assertEqual(hom_truoc["E2"].trang_thai, "HTS")

    def test_chong_luot_va_loi_thoi_gian(self):
        d = self.dong()
        self.assertEqual((d["E4a"].ky_hieu, d["E4b"].ky_hieu), ("Chồng lượt", "Chồng lượt"))
        self.assertEqual((d["E5"].ky_hieu, d["E5"].thoi_luong), ("Lỗi thời gian", None))
        self.assertEqual(d["E1"].ky_hieu, "")

    def test_luot_mo_lau(self):
        e9 = self.dong()["E9"]
        self.assertEqual((e9.tu_ky_truoc, e9.thoi_luong), (True, datetime.timedelta(hours=136)))

    def test_ky_khong_co_du_lieu(self):
        kq = lap(self.ds.tb01, "SO-01", ky=KyBaoCao(t("00:00 01/01"), t("00:00 02/01")))
        self.assertEqual(kq.dong, [])
        self.assertEqual(kq.chi_tieu["so_luot"], 0)


class KyBaoCaoTest(TestCase):
    def test_ky_khong_hop_le(self):
        for tu, den in [("00:00 26/10", "00:00 25/10"), ("00:00 25/10", "00:00 25/10")]:
            with self.assertRaises(ValidationError):
                KyBaoCao(t(tu), t(den))
        with self.assertRaises(ValidationError):
            KyBaoCao(t("00:00 01/01/2025"), t("00:00 03/01/2026"))
        with self.assertRaises(ValidationError):
            KyBaoCao(datetime.datetime(2026, 10, 25), datetime.datetime(2026, 10, 26))

    def test_lua_chon_nhanh(self):
        bay_gio = t("06:00 26/10")  # thứ Hai
        gio = datetime.time(7, 30)
        mong_doi = {
            "hom_nay": ("00:00 26/10", "00:00 27/10"), "hom_qua": ("00:00 25/10", "00:00 26/10"),
            "ca_hien_tai": ("07:30 25/10", "07:30 26/10"), "ca_truoc": ("07:30 24/10", "07:30 25/10"),
            "tuan_nay": ("00:00 26/10", "00:00 02/11"), "thang_nay": ("00:00 01/10", "00:00 01/11"),
            "thang_truoc": ("00:00 01/09", "00:00 01/10"),
        }
        for ma, (tu, den) in mong_doi.items():
            with self.subTest(ma):
                self.assertEqual(KyBaoCao.tu_lua_chon(ma, bay_gio, gio), KyBaoCao(t(tu), t(den)))

    def test_mo_ta(self):
        self.assertEqual(KY_S1.mo_ta(), "Từ 00:00 ngày 25/10/2026 đến hết ngày 25/10/2026")
        self.assertEqual(KyBaoCao(t("07:30 25/10"), t("07:30 26/10")).mo_ta(),
                         "Từ 07:30 ngày 25/10/2026 đến trước 07:30 ngày 26/10/2026")


class SapXepTiengVietTest(TestCase):
    def test_thu_tu_theo_ten(self):
        ten = ["Lương Thế Vinh", "Nguyễn Thị Ánh Tuyết", "Bùi Thị Ơn", "Ưng Hoàng Phúc", "Ông Ích Khiêm",
               "Đặng Quốc Hưng", "Phạm Thị Ngọc Hà"]
        self.assertEqual([x.split()[-1] for x in sorted(ten, key=khoa_ho_ten)],
                         ["Hà", "Hưng", "Khiêm", "Ơn", "Phúc", "Tuyết", "Vinh"])

    def test_d_sau_d_khong_gach(self):
        self.assertEqual(sorted(["Đức", "Dũng", "Em"], key=lambda s: khoa_ho_ten(s)), ["Dũng", "Đức", "Em"])
