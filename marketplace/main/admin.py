from django.contrib import admin
from django.contrib.admin import TabularInline
from django.utils.translation import gettext_lazy as _

from .forms import CategoryForm
from .models import Category, Product, Discount, Shop, Warehouse, Banner, Profile, Review, RecentProduct, Cart, CartLine
from compare.models import ProductCharacteristic


admin.site.register(RecentProduct)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'image', 'link', 'is_active')
    actions = ['set_active_status', 'remove_active_status']

    def set_active_status(self, request, queryset):
        queryset.update(is_active=True)

    def remove_active_status(self, request, queryset):
        queryset.update(is_active=False)

    set_active_status.short_description = _('Set banners is_active flag')
    remove_active_status.short_description = _('Remove banners is_active flag')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    list_display_links = ('id', 'user')
    search_fields = ('user', )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


class ChildInline(TabularInline):
    model = Category


class ProductInline(TabularInline):
    model = Product


class WarehouseInline(TabularInline):
    model = Warehouse


class ProductCharacteristicInline(TabularInline):
    model = ProductCharacteristic


class CartInline(TabularInline):
    model = CartLine


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'parent_category', 'sort_index']
    list_filter = ['parent_category']
    form = CategoryForm
    inlines = [ChildInline, ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'img', 'description', 'is_active']
    list_filter = ['category']
    inlines = [WarehouseInline, ProductCharacteristicInline]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop', 'product', 'percent', 'date_start', 'date_end', 'date_created',  'title',
                    'description']
    list_filter = ['product']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'img', 'description', 'phone', 'address', 'email']
    inlines = [WarehouseInline]


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'shop', 'price', 'amount']
    list_filter = ['product', 'shop']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created', 'is_payed', 'cost']
    list_filter = ['user']
    inlines = [CartInline]
