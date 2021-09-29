from django.urls import path

from . import views

urlpatterns = [
    path('shop-list', views.ShopListView.as_view(), name='shop-list'),
    path('shop-detail/<int:pk>', views.ShopDetailView.as_view(), name='shop-detail')
]
