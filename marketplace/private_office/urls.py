from django.urls import path

from payment.views import OrderView
from private_office.views import DetailPrivateOfficeView, LastViewedProductsView, ProfileUpdateView, OrderListView

urlpatterns = [
    path('private_office/', DetailPrivateOfficeView.as_view(), name='private_office'),
    path('last_products/', LastViewedProductsView.as_view(), name='last_products'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('orders/', OrderListView.as_view(), name='order-history'),
    path('orders/<int:pk>', OrderView.as_view(), name='order'),
    # path('private_office/<int:pk>', DetailPrivateOfficeView.as_view(), name='private_office'),
    # path('profile/<int:pk>', ProfileUpdateView.as_view(), name='profile'),
]
