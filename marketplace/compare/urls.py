from django.urls import path

from .views import CompareView, RemoveCompareProductView, AddCompareProductView


urlpatterns = [
    path('', CompareView.as_view(), name='compare'),
    path('remove/<int:pk>', RemoveCompareProductView.as_view(), name='compare-remove'),
    path('add/<int:pk>', AddCompareProductView.as_view(), name='compare-add'),
]
