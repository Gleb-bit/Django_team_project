# Generated by Django 3.2.4 on 2021-07-12 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_product_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='user',
        ),
        migrations.AddField(
            model_name='review',
            name='author',
            field=models.CharField(max_length=100, null=True, verbose_name='Author'),
        ),
        migrations.AddField(
            model_name='review',
            name='email',
            field=models.EmailField(max_length=254, null=True, verbose_name='Email'),
        ),
    ]
