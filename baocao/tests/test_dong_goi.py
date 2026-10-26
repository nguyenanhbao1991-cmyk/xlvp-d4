"""Đóng gói ngoại tuyến (trien_khai/dong_goi.py) và kiểm tra gói trước khi cài (kiem_tra_goi.py)."""
import importlib.util
import tempfile
import zipfile
from pathlib import Path

from django.test import SimpleTestCase

GOC = Path(__file__).resolve().parents[2]


def _nap(ten):
    spec = importlib.util.spec_from_file_location(ten, GOC / "trien_khai" / f"{ten}.py")
    mo_dun = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mo_dun)
    return mo_dun


dong_goi = _nap("dong_goi")
kiem_tra_goi = _nap("kiem_tra_goi")


class KiemTraGoiTest(SimpleTestCase):
    def tao_goi(self, tam):
        goc = Path(tam)
        (goc / "goi").mkdir()
        (goc / "goi" / "django-5.2-py3-none-any.whl").write_bytes(b"wheel")
        (goc / "cai_dat_he_thong").mkdir()
        (goc / "cai_dat_he_thong" / "python-3.12.10-amd64.exe").write_bytes(b"exe")
        (goc / "manage.py").write_text("print('x')\n", encoding="utf-8")
        (goc / "PHIEN_BAN.txt").write_text("ma_nguon=abc\npython=3.12\nnen_tang=win_amd64\n", encoding="utf-8")
        dong_goi.ghi_manifest(goc)
        return goc

    def test_goi_dat(self):
        with tempfile.TemporaryDirectory() as tam:
            goc = self.tao_goi(tam)
            self.assertEqual(kiem_tra_goi.kiem_tra(goc, "3.12", 64), [])
            # Sau khi cài, các tệp sinh ra ngoài goi/ và cai_dat_he_thong/ không làm gói hỏng.
            (goc / "qlcbcs.env").write_text("QLCBCS_DB_PASSWORD=x", encoding="utf-8")
            (goc / "nhat_ky").mkdir()
            (goc / "nhat_ky" / "qlcbcs.log").write_text("", encoding="utf-8")
            self.assertEqual(kiem_tra_goi.kiem_tra(goc, "3.12", 64), [])

    def test_phat_hien_thieu_hong_va_tep_la(self):
        with tempfile.TemporaryDirectory() as tam:
            goc = self.tao_goi(tam)
            (goc / "manage.py").write_text("print('bị sửa')\n", encoding="utf-8")
            (goc / "cai_dat_he_thong" / "python-3.12.10-amd64.exe").unlink()
            (goc / "goi" / "goi-la-1.0-py3-none-any.whl").write_bytes(b"?")
            loi = kiem_tra_goi.kiem_tra(goc, "3.12", 64)
            self.assertIn("Sai mã SHA-256 (tệp hỏng hoặc bị sửa): manage.py", loi)
            self.assertIn("Thiếu tệp: cai_dat_he_thong/python-3.12.10-amd64.exe", loi)
            self.assertIn("Tệp lạ không có trong gói: goi/goi-la-1.0-py3-none-any.whl", loi)

    def test_sai_phien_ban_python(self):
        with tempfile.TemporaryDirectory() as tam:
            goc = self.tao_goi(tam)
            self.assertEqual(kiem_tra_goi.kiem_tra(goc, "3.13", 64),
                             ["Gói dành cho Python 3.12 nhưng đang chạy Python 3.13."])
            self.assertEqual(kiem_tra_goi.kiem_tra(goc, "3.12", 32),
                             ["Gói dành cho Python 64-bit nhưng đang chạy Python 32-bit."])

    def test_khong_co_manifest(self):
        with tempfile.TemporaryDirectory() as tam:
            self.assertIn("Không có MANIFEST-SHA256.txt", kiem_tra_goi.kiem_tra(Path(tam), "3.12", 64)[0])


class DongGoiTest(SimpleTestCase):
    def test_chi_dong_goi_tep_duoc_git_quan_ly(self):
        tep, nhan = dong_goi.danh_sach_tep_nguon(cho_phep_thay_doi=True)
        ten = {p.as_posix() for p in tep}
        self.assertIn("manage.py", ten)
        self.assertIn("baocao/fonts/LiberationSerif-Regular.ttf", ten)
        self.assertIn("qlcbcs.env.mau", ten)
        for bi_mat in ("qlcbcs.env", ".env"):
            self.assertNotIn(bi_mat, ten)
        self.assertFalse(any(x.startswith((".venv/", "nhat_ky/", "staticfiles/", "goi/", "dist/")) for x in ten))
        self.assertFalse(any("__pycache__" in x for x in ten))
        self.assertTrue(nhan)

    def test_tao_zip_va_kiem_tra_sau_giai_nen(self):
        """Đóng gói (không tải thư viện), giải nén như trên máy chủ, rồi kiểm tra gói."""
        with tempfile.TemporaryDirectory() as tam:
            tam = Path(tam)
            bo_cai = tam / "postgresql-16-windows-x64.exe"
            bo_cai.write_bytes(b"bo cai")
            tep_zip, ma = dong_goi.dong_goi("3.12", [bo_cai], tam / "dist", cho_phep_thay_doi=True, tai=False,
                                            bao=lambda _: None)
            self.assertEqual((tam / "dist" / f"{tep_zip.name}.sha256").read_text().split()[0], ma)
            self.assertEqual(dong_goi.sha256(tep_zip), ma)
            dich = tam / "QLCBCS"
            with zipfile.ZipFile(tep_zip) as z:
                z.extractall(dich)
            self.assertEqual(kiem_tra_goi.kiem_tra(dich, "3.12", 64), [])
            self.assertTrue((dich / "cai_dat_he_thong" / "postgresql-16-windows-x64.exe").is_file())
            self.assertIn("python=3.12", (dich / "PHIEN_BAN.txt").read_text(encoding="utf-8"))
            # Script PowerShell giữ BOM UTF-8 trong gói (PowerShell 5.1 cần để đọc đúng tiếng Việt).
            self.assertTrue((dich / "trien_khai/windows/cai_dat.ps1").read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_tu_choi_khi_con_thay_doi_chua_commit(self):
        tep_tam = GOC / "tep_tam_chua_commit.txt"
        tep_tam.write_text("x", encoding="utf-8")
        try:
            with self.assertRaisesRegex(dong_goi.LoiDongGoi, "chưa commit"):
                dong_goi.danh_sach_tep_nguon(cho_phep_thay_doi=False)
        finally:
            tep_tam.unlink()

    def test_tham_so_phien_ban_python(self):
        with self.assertRaises(SystemExit):
            dong_goi.main(["--python", "2.7"])


