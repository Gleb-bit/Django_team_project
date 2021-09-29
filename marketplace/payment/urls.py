from django.urls import path

from payment.views import OrderFormView, OrderView, OrderPayView, PaymentProgressView

urlpatterns = [
    path('', OrderFormView.as_view(), name='order-create'),
    path('confirm', OrderView.as_view(), name='order-confirm'),
    path('pay', OrderPayView.as_view(), name='order-pay'),
    path('progress', PaymentProgressView.as_view(), name='progress-payment'),
    path('success/<token>', OrderView.as_view(), {'success': True}, name='order-success'),
    path('error', OrderView.as_view(), {'success': False}, name='order-error'),
]
