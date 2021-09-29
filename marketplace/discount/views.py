from django.views.generic import ListView, DetailView

from main.models import Discount
from marketplace.views import BaseMixin
from services.discount_services import get_all_active_discounts


class DiscountListView(BaseMixin, ListView):
    """"Представление для списка скидок"""

    template_name = 'discount/discount_list.html'
    paginate_by = 12
    context_object_name = "discounts"

    def get_queryset(self):

        return get_all_active_discounts()


class DiscountDetailView(BaseMixin, DetailView):
    """Представление для детальной страницы скидки"""

    template_name = 'discount/discount_detail.html'
    model = Discount
    context_object_name = 'discount'
