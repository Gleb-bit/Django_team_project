# Generated by Django 3.2.4 on 2021-08-26 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20210825_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouse',
            name='discounted_price',
            field=models.FloatField(default=0, verbose_name='Discounted price'),
            preserve_default=False,
        ),
    ]
