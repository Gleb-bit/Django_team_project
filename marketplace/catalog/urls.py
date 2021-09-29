from django.urls import path

from catalog.views import CatalogListView, ProductDetailView, FilterFormView, ReviewCreateView, \
    calculate_all_discounted_prices, AddRecentProductView

urlpatterns = [
    path('', CatalogListView.as_view(), name='catalog'),
    path('filter', FilterFormView.as_view(), name='filter'),
    path('calculate-discounts', calculate_all_discounted_prices),
    path('<slug:slug>', ProductDetailView.as_view(), name='product'),
    path('<slug:slug>/add-recent', AddRecentProductView.as_view(), name='add-to-recent'),
    path('<slug:slug>/reviews/add', ReviewCreateView.as_view(), name='add-review'),
    path('calculate-discounts', calculate_all_discounted_prices)
]
