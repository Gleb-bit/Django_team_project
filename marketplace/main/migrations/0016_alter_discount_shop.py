# Generated by Django 3.2.4 on 2021-07-14 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20210714_0731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.shop', verbose_name='Shop'),
        ),
    ]