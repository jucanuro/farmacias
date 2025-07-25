# Generated by Django 4.2.23 on 2025-07-09 01:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inventario", "0003_alter_producto_codigo_barras_and_more"),
        ("compras", "0003_alter_detallecompra_cantidad_recibida_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="detallecompra",
            name="presentacion",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="inventario.unidadpresentacion",
                verbose_name="Presentación",
            ),
        ),
    ]
