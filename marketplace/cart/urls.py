from django.urls import path

from .views import CartDetailView, AddToCartView, CartErrorView, MergeAnonymousCartView


urlpatterns = [
    path('cart', CartDetailView.as_view(), name='cart'),
    path('add/<slug:slug>/<int:warehouse_id>', AddToCartView.as_view(), name='add-to-cart'),
    path('error', CartErrorView.as_view(), name='cart-error'),
    path('merge-cart', MergeAnonymousCartView.as_view(), name='merge-cart'),
]
