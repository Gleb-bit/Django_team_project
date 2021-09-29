# Generated by Django 3.2.4 on 2021-07-13 19:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compare', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='characteristic',
            options={'verbose_name': 'Characteristic', 'verbose_name_plural': 'Characteristics'},
        ),
        migrations.AlterModelOptions(
            name='compareproduct',
            options={'verbose_name': 'Compare product', 'verbose_name_plural': 'Compare products'},
        ),
        migrations.AlterModelOptions(
            name='productcharacteristic',
            options={'verbose_name': 'Product characteristic', 'verbose_name_plural': 'Product characteristics'},
        ),
        migrations.AlterField(
            model_name='productcharacteristic',
            name='characteristic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_characteristics', to='compare.characteristic', verbose_name='Characteristic'),
        ),
    ]
