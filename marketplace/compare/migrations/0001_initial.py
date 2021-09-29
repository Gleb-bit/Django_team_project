# Generated by Django 3.2.4 on 2021-07-13 19:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0011_auto_20210707_0655'),
    ]

    operations = [
        migrations.CreateModel(
            name='Characteristic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Characteristic name')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCharacteristic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100, verbose_name='Characteristic value')),
                ('characteristic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compare.characteristic', verbose_name='Characteristic')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characteristics', to='main.product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='CompareProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='Date added')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.product', verbose_name='Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compare_products', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
