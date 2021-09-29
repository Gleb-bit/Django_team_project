from django.contrib import admin

from main.models import Order, PaymentMethod, DeliveryMethod, PaymentState


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentState)
class PaymentStateAdmin(admin.ModelAdmin):
    pass
