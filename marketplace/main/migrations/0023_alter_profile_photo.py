# Generated by Django 3.2.4 on 2021-08-01 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_alter_profile_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ImageField(blank=True, default='icons/user_icon.png', upload_to='users_photos/%Y/%m/%d', verbose_name='photo'),
        ),
    ]
