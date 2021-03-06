# Generated by Django 3.2.4 on 2021-07-07 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_merge_20210707_0644'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='shop',
        ),
        migrations.AddField(
            model_name='cartline',
            name='shop',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.shop', verbose_name='Shop'),
        ),
        migrations.AddField(
            model_name='review',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is active'),
        ),
        migrations.AlterField(
            model_name='review',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='main.product', verbose_name='Product'),
        ),
    ]
