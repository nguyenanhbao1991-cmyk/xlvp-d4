"""Cấu hình Django cho QL CBCS LAN.

Giá trị nhạy cảm và thông số kết nối CSDL đọc từ biến môi trường, hoặc từ tệp ``qlcbcs.env``
(xem ``qlcbcs.env.mau`` và ``docs/trien_khai_windows.md``).
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .cau_hinh import nap_cau_hinh

BASE_DIR = Path(__file__).resolve().parent.parent
nap_cau_hinh(BASE_DIR)


def _bat(ten, mac_dinh="0"):
    return os.environ.get(ten, mac_dinh).strip().lower() in ("1", "true", "yes", "co", "có")


def _danh_sach(ten, mac_dinh=""):
    return [x.strip() for x in os.environ.get(ten, mac_dinh).split(",") if x.strip()]


KHOA_PHAT_TRIEN = "chi-dung-cho-moi-truong-phat-trien"
# "san_xuat" trên máy chủ thật: bắt buộc khoá bí mật riêng, bật cookie an toàn.
CHE_DO = os.environ.get("QLCBCS_CHE_DO", "phat_trien")
SECRET_KEY = os.environ.get("QLCBCS_SECRET_KEY", KHOA_PHAT_TRIEN)
DEBUG = _bat("QLCBCS_DEBUG")
ALLOWED_HOSTS = _danh_sach("QLCBCS_ALLOWED_HOSTS", "localhost,127.0.0.1")

if CHE_DO == "san_xuat":
    if SECRET_KEY == KHOA_PHAT_TRIEN or len(SECRET_KEY) < 40:
        raise ImproperlyConfigured("Chế độ sản xuất cần QLCBCS_SECRET_KEY riêng, dài ít nhất 40 ký tự.")
    if DEBUG:
        raise ImproperlyConfigured("Không bật QLCBCS_DEBUG ở chế độ sản xuất.")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ravao",
    "baocao",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Waitress không phục vụ tệp tĩnh; WhiteNoise phục vụ CSS/JS của trang quản trị từ STATIC_ROOT.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "qlcbcs.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "qlcbcs.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("QLCBCS_DB_NAME", "qlcbcs"),
        "USER": os.environ.get("QLCBCS_DB_USER", "qlcbcs"),
        "PASSWORD": os.environ.get("QLCBCS_DB_PASSWORD", "qlcbcs"),
        "HOST": os.environ.get("QLCBCS_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("QLCBCS_DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
]

LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Ho_Chi_Minh"  # BR-KY-01. Trên Windows cần gói tzdata (đã có trong requirements.txt).
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = Path(os.environ.get("QLCBCS_THU_MUC_TINH", BASE_DIR / "staticfiles"))
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "admin:login"

# Máy dùng chung tại cổng: phiên hết hạn khi đóng trình duyệt và sau 8 giờ.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = int(os.environ.get("QLCBCS_PHIEN_GIAY", 8 * 3600))
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
# Chỉ bật khi truy cập qua HTTPS (ví dụ IIS/reverse proxy phía trước có chứng chỉ).
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = _bat("QLCBCS_HTTPS")
if _bat("QLCBCS_HTTPS") and _bat("QLCBCS_SAU_PROXY"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = _danh_sach("QLCBCS_CSRF_TRUSTED_ORIGINS")

THU_MUC_NHAT_KY = Path(os.environ.get("QLCBCS_THU_MUC_NHAT_KY", BASE_DIR / "nhat_ky"))
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"thuong": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "thuong"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
}
if CHE_DO == "san_xuat":
    THU_MUC_NHAT_KY.mkdir(parents=True, exist_ok=True)
    LOGGING["handlers"]["tep"] = {
        "class": "logging.handlers.RotatingFileHandler", "formatter": "thuong", "encoding": "utf-8",
        "filename": str(THU_MUC_NHAT_KY / "qlcbcs.log"), "maxBytes": 5 * 1024 * 1024, "backupCount": 10,
    }
    LOGGING["root"]["handlers"].append("tep")
