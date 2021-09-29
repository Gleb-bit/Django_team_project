from django.contrib import admin

from .models import Characteristic, ProductCharacteristic, CompareProduct


admin.site.register(Characteristic)
admin.site.register(ProductCharacteristic)
admin.site.register(CompareProduct)
