import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def gan_ma_tai(apps, schema_editor):
    LichSuXuat = apps.get_model("baocao", "LichSuXuat")
    for ls in LichSuXuat.objects.filter(ma_tai__isnull=True).only("pk"):
        LichSuXuat.objects.filter(pk=ls.pk).update(ma_tai=uuid.uuid4(), phien_ban_mau="1.0")


class Migration(migrations.Migration):
    dependencies = [("baocao", "0002_khoi_ky_theo_phe_duyet")]

    operations = [
        # Bản ghi cũ cần mã tải riêng: thêm cột cho phép rỗng, điền, rồi mới đặt unique.
        migrations.AddField(
            model_name="lichsuxuat", name="ma_tai",
            field=models.UUIDField(null=True, editable=False, verbose_name="mã tải"),
        ),
        migrations.AddField(
            model_name="lichsuxuat", name="phien_ban_mau",
            field=models.CharField(blank=True, max_length=20, verbose_name="phiên bản mẫu"),
        ),
        migrations.RunPython(gan_ma_tai, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="lichsuxuat", name="ma_tai",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="mã tải"),
        ),
        migrations.AddField(
            model_name="lichsuxuat", name="so_lan_tai",
            field=models.PositiveIntegerField(default=0, verbose_name="số lần tải"),
        ),
        migrations.AddField(
            model_name="lichsuxuat", name="tai_lan_cuoi",
            field=models.DateTimeField(blank=True, null=True, verbose_name="tải lần cuối"),
        ),
        migrations.CreateModel(
            name="BanChotXuat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("noi_dung", models.BinaryField(verbose_name="nội dung tệp")),
                ("kich_thuoc", models.PositiveIntegerField(verbose_name="kích thước (byte)")),
                ("du_lieu", models.JSONField(verbose_name="dữ liệu đã chốt")),
                ("tao_luc", models.DateTimeField(default=django.utils.timezone.now, verbose_name="tạo lúc")),
                ("lich_su", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="ban_chot",
                                                 to="baocao.lichsuxuat")),
            ],
            options={"verbose_name": "bản chốt xuất sổ", "verbose_name_plural": "bản chốt xuất sổ"},
        ),
    ]
