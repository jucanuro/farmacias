# Generated by Django 4.2.23 on 2025-07-09 00:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("compras", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="compra",
            name="numero_factura_proveedor",
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
