# Generated by Django 3.2.4 on 2021-08-04 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_merge_20210731_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='discount',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Discount created datetime'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='banner_images', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='product',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='product_images/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='users_photos/%Y/%m/%d', verbose_name='photo'),
        ),
        migrations.AlterField(
            model_name='shop',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='shop_images/', verbose_name='Image'),
        ),
    ]
