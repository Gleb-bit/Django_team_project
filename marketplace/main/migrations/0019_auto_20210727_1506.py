# Generated by Django 3.2.4 on 2021-07-27 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20210723_1337'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('price', models.FloatField(verbose_name='price')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
            ],
        ),
        migrations.AlterField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='birth date'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=255, verbose_name='comment')),
                ('total_price', models.FloatField(verbose_name='total price')),
                ('date', models.DateTimeField(auto_now=True, verbose_name='date')),
                ('text_error', models.CharField(max_length=255, verbose_name='text_error')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='main.profile', verbose_name='customer')),
                ('delivery_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='main.deliverymethod', verbose_name='delivery method')),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='main.paymentmethod', verbose_name='payment method')),
                ('payment_state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='main.paymentstate', verbose_name='payment state')),
            ],
        ),
    ]