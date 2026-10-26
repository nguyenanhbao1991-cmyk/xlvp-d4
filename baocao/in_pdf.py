"""Vẽ ``TaiLieu`` ra PDF bằng ReportLab (REQ-EXP-04, BR-XF-04).

PDF được tạo trực tiếp, không chuyển đổi từ Word: không cần chương trình ngoài
trên máy chủ LAN, phông được nhúng, bố cục cố định.
"""
import io
from pathlib import Path
from xml.sax.saxutils import escape

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, LongTable, NextPageTemplate, PageBreak, PageTemplate, Paragraph, Spacer,
    Table, TableStyle,
)
from reportlab.platypus.doctemplate import LayoutError

from . import bo_cuc
from .bo_cuc import Bang, Doan, GiuCung
from .trinh_bay import KhoiKy

PHONG = "QLSerif"
_TEP_PHONG = {
    PHONG: "LiberationSerif-Regular.ttf",
    PHONG + "-Dam": "LiberationSerif-Bold.ttf",
    PHONG + "-Nghieng": "LiberationSerif-Italic.ttf",
    PHONG + "-DamNghieng": "LiberationSerif-BoldItalic.ttf",
}
_KICH_THUOC = {"A4": A4, "A3": A3}


class LoiTaoPdf(Exception):
    pass


def _thu_muc_phong():
    return Path(getattr(settings, "QLCBCS_THU_MUC_PHONG", Path(__file__).parent / "fonts"))


def tep_phong_can_co():
    return [_thu_muc_phong() / tep for tep in _TEP_PHONG.values()]


def _dang_ky_phong():
    if PHONG in pdfmetrics.getRegisteredFontNames():
        return
    thu_muc = _thu_muc_phong()
    for ten, tep in _TEP_PHONG.items():
        duong_dan = thu_muc / tep
        if not duong_dan.exists():
            raise LoiTaoPdf(f"Thiếu phông chữ {duong_dan}. Không tạo PDF khi không nhúng được phông tiếng Việt.")
        pdfmetrics.registerFont(TTFont(ten, str(duong_dan)))
    pdfmetrics.registerFontFamily(PHONG, normal=PHONG, bold=PHONG + "-Dam", italic=PHONG + "-Nghieng",
                                  boldItalic=PHONG + "-DamNghieng")


def _kieu(co_chu=10, can=TA_LEFT, dam=False, nghieng=False, truoc=0, sau=0):
    ten = PHONG + ("-DamNghieng" if dam and nghieng else "-Dam" if dam else "-Nghieng" if nghieng else "")
    return ParagraphStyle(
        f"{ten}-{co_chu}-{can}-{truoc}-{sau}", fontName=ten, fontSize=co_chu, leading=co_chu * 1.22,
        alignment=can, spaceBefore=truoc, spaceAfter=sau, splitLongWords=True,
    )


_CAN = {"trai": TA_LEFT, "giua": TA_CENTER, "phai": TA_RIGHT}
_KIEU_DOAN = {
    "ten_so": dict(co_chu=14, can=TA_CENTER, dam=True, truoc=6, sau=2),
    "giua": dict(co_chu=10.5, can=TA_CENTER, sau=4),
    "thuong": dict(co_chu=10),
    "nghieng": dict(co_chu=10, nghieng=True),
    "muc": dict(co_chu=11, dam=True, truoc=8, sau=3),
    "nho": dict(co_chu=8.5),
    "dam": dict(co_chu=10, dam=True, truoc=4),
    "phai": dict(co_chu=10, can=TA_RIGHT),
}


# Phông nhúng không có glyph U+FFFD; dùng "□" để ký tự đã thay vẫn nhìn thấy được.
_KY_TU_THAY = "\u25a1"


def _markup(dong, nhan_manh="", co_chu_dong_sau=None):
    phan = []
    for i, chu in enumerate(dong):
        chu = escape(chu.replace("\ufffd", _KY_TU_THAY))
        if nhan_manh:
            chu = chu.replace(escape(nhan_manh), f"<b><u>{escape(nhan_manh)}</u></b>")
        if i and co_chu_dong_sau:
            chu = f'<font size="{co_chu_dong_sau}">{chu}</font>'
        phan.append(chu)
    return "<br/>".join(phan)


def _doan(doan):
    return Paragraph(_markup(doan.chu.split("\n")), _kieu(**_KIEU_DOAN[doan.kieu]))


def _o(o, co_chu, dam=False):
    return Paragraph(_markup(o.dong, o.nhan_manh, o.co_chu_dong_sau),
                     _kieu(co_chu, _CAN[o.can], dam=dam or o.dam, nghieng=o.nghieng))


def _bang(bang, rong):
    tong = sum(c.ty_le for c in bang.cot)
    rong_cot = [rong * c.ty_le / tong for c in bang.cot]
    du_lieu, kieu = [], []
    if bang.nhom_tieu_de:
        hang, cot = [], 0
        for nhan, so_cot in bang.nhom_tieu_de:
            hang += [Paragraph(escape(nhan), _kieu(bang.co_chu, TA_CENTER, dam=True))] + [""] * (so_cot - 1)
            if so_cot > 1:
                kieu.append(("SPAN", (cot, 0), (cot + so_cot - 1, 0)))
            cot += so_cot
        du_lieu.append(hang)
    if bang.co_tieu_de:
        du_lieu.append([Paragraph(_markup(c.tieu_de.split("\n")), _kieu(bang.co_chu - 0.5, TA_CENTER, dam=True))
                        for c in bang.cot])
    so_tieu_de = len(du_lieu)
    for hang in bang.dong:
        du_lieu.append([_o(o, bang.co_chu) for o in hang])
    kieu += [
        ("FONTNAME", (0, 0), (-1, -1), PHONG),  # cả ô rỗng, tránh phông mặc định không nhúng
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    if bang.khung:
        kieu.append(("GRID", (0, 0), (-1, -1), 0.5, colors.black))
    if so_tieu_de:
        kieu += [("BACKGROUND", (0, 0), (-1, so_tieu_de - 1), colors.HexColor("#D9D9D9")),
                 ("VALIGN", (0, 0), (-1, so_tieu_de - 1), "MIDDLE")]
    lop = LongTable if len(du_lieu) > 50 else Table
    return lop(du_lieu, colWidths=rong_cot, repeatRows=so_tieu_de, hAlign="LEFT", style=TableStyle(kieu))


def _khoi_ky(khoi, rong):
    n = len(khoi.o)
    du_lieu = [
        [Paragraph(escape(o.chuc_danh), _kieu(10, TA_CENTER, dam=True)) for o in khoi.o],
        [Paragraph("(Ký, ghi rõ họ tên)", _kieu(9, TA_CENTER, nghieng=True)) for _ in khoi.o],
        ["" for _ in khoi.o],
        [Paragraph(escape(o.ten or "..............................."), _kieu(10, TA_CENTER)) for o in khoi.o],
    ]
    bang = Table(du_lieu, colWidths=[rong / n] * n, rowHeights=[None, None, 22 * mm, None],
                 style=TableStyle([("FONTNAME", (0, 0), (-1, -1), PHONG)]))
    return [Spacer(1, 4 * mm), Paragraph(escape(khoi.dong_ngay), _kieu(10, TA_RIGHT, nghieng=True)), bang,
            Spacer(1, 3 * mm)]


def _flowable(khoi, rong):
    if isinstance(khoi, Doan):
        return [_doan(khoi)]
    if isinstance(khoi, Bang):
        return [_bang(khoi, rong), Spacer(1, 2 * mm)]
    if isinstance(khoi, KhoiKy):
        return _khoi_ky(khoi, rong)
    if isinstance(khoi, GiuCung):
        return [KeepTogether([f for k in khoi.khoi for f in _flowable(k, rong)])]
    raise TypeError(khoi)


def _ma_mau(phan):
    return f"{phan.kho}-{phan.huong}"


def _kich_thuoc(phan):
    co = _KICH_THUOC[phan.kho]
    return landscape(co) if phan.huong == "ngang" else portrait(co)


def _lop_canvas(chan_trang):
    class CanvasDanhSoTrang(Canvas):
        """Vẽ chân trang "Trang x/y" sau khi biết tổng số trang."""

        def __init__(self, *args, **kwargs):
            # Không để canvas tham chiếu Helvetica (phông không nhúng) làm phông khởi tạo;
            # BaseDocTemplate truyền tường minh initialFontName=None.
            kwargs["initialFontName"] = kwargs.get("initialFontName") or PHONG
            kwargs["initialFontSize"] = kwargs.get("initialFontSize") or 10
            super().__init__(*args, **kwargs)
            self._cac_trang = []

        def showPage(self):
            self._cac_trang.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            tong = len(self._cac_trang)
            for trang in self._cac_trang:
                self.__dict__.update(trang)
                rong, _cao = self._pagesize
                self.setFont(PHONG, 8)
                self.drawCentredString(rong / 2, 8 * mm, f"{chan_trang} · Trang {self._pageNumber}/{tong}")
                super().showPage()
            super().save()

    return CanvasDanhSoTrang


def tao_pdf(tai_lieu):
    _dang_ky_phong()
    bo_dem = io.BytesIO()

    def ve_dau_trang(canvas, doc):
        if canvas.getPageNumber() > 1:  # Từ trang 2: đầu trang rút gọn (BR-IN-04).
            rong, cao = canvas._pagesize
            canvas.setFont(PHONG, 8)
            canvas.drawString(bo_cuc.LE_TRAI_MM * mm, cao - 9 * mm, tai_lieu.dau_trang_rut_gon)

    mau, story = {}, []
    for i, phan in enumerate(tai_lieu.phan):
        ma = _ma_mau(phan)
        if ma not in mau:
            rong, cao = _kich_thuoc(phan)
            khung = Frame(bo_cuc.LE_TRAI_MM * mm, bo_cuc.LE_DUOI_MM * mm,
                          rong - (bo_cuc.LE_TRAI_MM + bo_cuc.LE_PHAI_MM) * mm,
                          cao - (bo_cuc.LE_TREN_MM + bo_cuc.LE_DUOI_MM) * mm,
                          leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id=ma)
            mau[ma] = PageTemplate(id=ma, frames=[khung], pagesize=(rong, cao), onPage=ve_dau_trang)
        if i > 0:
            story += [NextPageTemplate(ma), PageBreak()]
        rong_vung = bo_cuc.rong_vung_in(phan.kho, phan.huong) * mm
        for khoi in phan.khoi:
            story += _flowable(khoi, rong_vung)

    dau = _ma_mau(tai_lieu.phan[0])
    doc = BaseDocTemplate(
        bo_dem, pageTemplates=[mau[dau]] + [m for k, m in mau.items() if k != dau],
        pagesize=mau[dau].pagesize, title=tai_lieu.tieu_de, author=tai_lieu.tac_gia,
        subject=tai_lieu.chu_de, creator="QL CBCS LAN", keywords="Mẫu nghiệp vụ nội bộ",
        initialFontName=PHONG, initialFontSize=10,
    )
    try:
        doc.build(story, canvasmaker=_lop_canvas(tai_lieu.chan_trang))
    except LayoutError as loi:
        raise LoiTaoPdf(f"Không dàn trang được: một khối nội dung lớn hơn một trang ({loi}).") from loi
    return bo_dem.getvalue()
