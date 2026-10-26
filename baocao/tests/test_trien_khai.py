"""Phần Python của bộ triển khai Windows: đọc qlcbcs.env, chế độ sản xuất, chạy bằng Waitress.

Các script PowerShell trong trien_khai/windows không chạy được ở đây (môi trường Linux);
kiểm thử này chỉ bao phần Python mà các script đó gọi.
"""
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from qlcbcs.cau_hinh import doc_tep_moi_truong

GOC = Path(__file__).resolve().parents[2]
KHOA = "k" * 50


def _moi_truong(**them):
    """Môi trường sạch cho tiến trình con: bỏ mọi biến QLCBCS_* của tiến trình kiểm thử."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("QLCBCS_")}
    env["QLCBCS_TEP_CAU_HINH"] = os.devnull
    env.update(them)
    return env


class DocTepCauHinhTest(SimpleTestCase):
    def test_doc_tep(self):
        with tempfile.TemporaryDirectory() as tam:
            tep = Path(tam) / "qlcbcs.env"
            # Notepad trên Windows có thể lưu kèm BOM và xuống dòng CRLF.
            tep.write_bytes("﻿# chú thích\r\nQLCBCS_A=1\r\n\r\nQLCBCS_B = \"có dấu cách\" \r\n"
                            "QLCBCS_C='x=y'\r\nQLCBCS_D=giữ\r\n".encode("utf-8"))
            with mock.patch.dict(os.environ, {"QLCBCS_D": "đã đặt sẵn"}, clear=False):
                da_nap = doc_tep_moi_truong(tep)
                self.assertEqual(da_nap, ["QLCBCS_A", "QLCBCS_B", "QLCBCS_C"])
                self.assertEqual((os.environ["QLCBCS_A"], os.environ["QLCBCS_B"], os.environ["QLCBCS_C"]),
                                 ("1", "có dấu cách", "x=y"))
                self.assertEqual(os.environ["QLCBCS_D"], "đã đặt sẵn")  # biến môi trường được ưu tiên
                for k in da_nap:
                    del os.environ[k]

    def test_dong_sai_va_tep_khong_ton_tai(self):
        with tempfile.TemporaryDirectory() as tam:
            tep = Path(tam) / "qlcbcs.env"
            tep.write_text("QLCBCS_A=1\nkhong co dau bang\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {}, clear=False), self.assertRaisesRegex(ValueError, ":2: thiếu dấu"):
                doc_tep_moi_truong(tep)
            self.assertEqual(doc_tep_moi_truong(Path(tam) / "khong_co.env"), [])


class CheDoSanXuatTest(SimpleTestCase):
    def nap_settings(self, **env):
        return subprocess.run([sys.executable, "-c", "import qlcbcs.settings"], cwd=GOC, capture_output=True,
                              text=True, env=_moi_truong(**env), timeout=60)

    def test_tu_choi_khoa_mac_dinh_va_debug(self):
        kq = self.nap_settings(QLCBCS_CHE_DO="san_xuat")
        self.assertNotEqual(kq.returncode, 0)
        self.assertIn("cần QLCBCS_SECRET_KEY riêng", kq.stderr)
        kq = self.nap_settings(QLCBCS_CHE_DO="san_xuat", QLCBCS_SECRET_KEY=KHOA, QLCBCS_DEBUG="1")
        self.assertIn("Không bật QLCBCS_DEBUG", kq.stderr)
        with tempfile.TemporaryDirectory() as tam:
            kq = self.nap_settings(QLCBCS_CHE_DO="san_xuat", QLCBCS_SECRET_KEY=KHOA, QLCBCS_THU_MUC_NHAT_KY=tam)
            self.assertEqual(kq.returncode, 0, kq.stderr)

    def test_doc_cau_hinh_tu_tep_env(self):
        with tempfile.TemporaryDirectory() as tam:
            tep = Path(tam) / "qlcbcs.env"
            tep.write_text(f"QLCBCS_CHE_DO=san_xuat\nQLCBCS_SECRET_KEY={KHOA}\nQLCBCS_ALLOWED_HOSTS=may-chu,10.0.0.5\n"
                           f"QLCBCS_THU_MUC_NHAT_KY={tam}\n", encoding="utf-8")
            kq = subprocess.run([sys.executable, "-c",
                                 "import qlcbcs.settings as s; print(s.ALLOWED_HOSTS, s.SECRET_KEY == 'k' * 50)"],
                                cwd=GOC, capture_output=True, text=True, timeout=60,
                                env=_moi_truong(QLCBCS_TEP_CAU_HINH=str(tep)))
            self.assertEqual(kq.stdout.strip(), "['may-chu', '10.0.0.5'] True", kq.stderr)


class WaitressTest(SimpleTestCase):
    """Chạy chay_may_chu.py thật (như tác vụ chạy nền trên Windows) và gọi qua HTTP."""

    def test_may_chu_tra_trang_va_tep_tinh(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            cong = s.getsockname()[1]
        with tempfile.TemporaryDirectory() as tam:
            env = _moi_truong(QLCBCS_CHE_DO="san_xuat", QLCBCS_SECRET_KEY=KHOA, QLCBCS_DIA_CHI="127.0.0.1",
                              QLCBCS_CONG=str(cong), QLCBCS_THU_MUC_TINH=str(Path(tam) / "tinh"),
                              QLCBCS_THU_MUC_NHAT_KY=str(Path(tam) / "nhat_ky"))
            subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput", "-v0"], cwd=GOC, env=env,
                           check=True, timeout=120)
            tien_trinh = subprocess.Popen([sys.executable, "chay_may_chu.py"], cwd=GOC, env=env,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            try:
                goc = f"http://127.0.0.1:{cong}"
                for _ in range(60):
                    try:
                        trang = urllib.request.urlopen(f"{goc}/admin/login/", timeout=5)
                        break
                    except (urllib.error.URLError, ConnectionError):
                        time.sleep(0.5)
                else:
                    self.fail("Máy chủ không phản hồi")
                self.assertEqual(trang.status, 200)
                self.assertEqual(trang.headers["Server"], "QLCBCS")
                self.assertEqual(trang.headers["X-Frame-Options"], "DENY")
                css = urllib.request.urlopen(f"{goc}/static/admin/css/base.css", timeout=5)
                self.assertEqual(css.status, 200)  # WhiteNoise phục vụ tệp tĩnh dù DEBUG tắt
                # Chưa đăng nhập: màn hình xuất sổ chuyển về trang đăng nhập, không lộ dữ liệu.
                opener = urllib.request.build_opener(_KhongChuyenHuong)
                with self.assertRaises(urllib.error.HTTPError) as loi:
                    opener.open(f"{goc}/so/xuat/", timeout=5)
                self.assertEqual(loi.exception.code, 302)
                self.assertIn("/admin/login/", loi.exception.headers["Location"])
                # Tên máy không có trong ALLOWED_HOSTS bị từ chối.
                yeu_cau = urllib.request.Request(f"{goc}/admin/login/", headers={"Host": "may-la"})
                with self.assertRaises(urllib.error.HTTPError) as loi:
                    urllib.request.urlopen(yeu_cau, timeout=5)
                self.assertEqual(loi.exception.code, 400)
            finally:
                tien_trinh.terminate()
                tien_trinh.wait(timeout=10)

    def test_loi_khoi_dong_duoc_ghi_ra_tep(self):
        with tempfile.TemporaryDirectory() as tam:
            env = _moi_truong(QLCBCS_CHE_DO="san_xuat", QLCBCS_THU_MUC_NHAT_KY=tam)  # thiếu khoá bí mật
            kq = subprocess.run([sys.executable, "chay_may_chu.py"], cwd=GOC, env=env, capture_output=True,
                                text=True, timeout=60)
            self.assertNotEqual(kq.returncode, 0)  # Task Scheduler thấy lỗi và khởi động lại
            nhat_ky = (Path(tam) / "khoi_dong.log").read_text(encoding="utf-8")
            self.assertIn("Không khởi động được", nhat_ky)
            self.assertIn("QLCBCS_SECRET_KEY", nhat_ky)


class _KhongChuyenHuong(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None
