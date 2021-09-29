from django.urls import path

from . import views

urlpatterns = [
    path('delete-cartline', views.AjaxDeleteLineFromCart.as_view(), name='ajax-delete-cartline'),
    path('get-cart-cost', views.AjaxGetCartCostView.as_view(), name='ajax-get-cart-cost'),
    path('get-cart-size', views.AjaxGetCartSizeView.as_view(), name='ajax-get-cart-size'),
    path('clear-cart', views.AjaxClearCartView.as_view(), name='ajax-clear-cart'),
    path('change-cartline-quantity', views.AjaxChangeCartLineQuantityView.as_view(),
         name='ajax-change-cartline-quantity'),
    path('get-cart', views.AjaxGetUserCartView.as_view(), name='ajax-get-cart'),
    path('get-warehouses-modal-content', views.AjaxGetWarehousesModalHTMLContentView.as_view(),
         name='ajax-get-warehouses-modal-content'),
    path('add-to-cart', views.AjaxAddToCartView.as_view(), name='ajax-add-to-cart'),
    path('get-order-cost', views.AjaxOrderCostView.as_view(), name='ajax-get-order-cost'),
    path('get-empty-cart-message', views.AjaxGetEmptyCartMessageView.as_view(), name='ajax-get-empty-cart-message'),
]
