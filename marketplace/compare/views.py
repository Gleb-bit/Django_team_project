from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import ListView
from loguru import logger

from marketplace.views import BaseMixin
from services.compare_services import get_compare_products_count, remove_product_from_compare, get_compare_products, \
    get_compare_products_characteristics, add_product_to_compare, get_philosophical_phrase
from .models import CompareProduct


class CompareView(BaseMixin, ListView):
    """Представление для страницы сравнения товаров"""

    template_name = 'compare/compare.html'
    model = CompareProduct
    context_object_name = "compare_products"

    def get_queryset(self):
        return get_compare_products(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        logger.debug(f"У пользователя '{self.request.user}' {get_compare_products_count(self.request.user)}"
                     f" товаров в сравнении")
        context["characteristics"] = get_compare_products_characteristics(self.request.user)
        if not context["characteristics"]:
            context["philosophical_phrase"] = get_philosophical_phrase()
        return context


class RemoveCompareProductView(View):
    """Представление для удаления товара из списка сравнения"""

    def post(self, request, *arg, **kwargs):
        user = self.request.user
        product_id = self.kwargs.get("pk")
        remove_product_from_compare(product_id=product_id, user=user)
        next_page = request.POST.get('next', '/')
        return HttpResponseRedirect(next_page)


class AddCompareProductView(View):
    """Представление для добавления товара в список сравнения"""

    def post(self, request, *arg, **kwargs):
        user = self.request.user
        product_id = self.kwargs.get("pk")
        add_product_to_compare(product_id=product_id, user=user)
        next_page = request.POST.get('next', '/')
        return HttpResponseRedirect(next_page)
