from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView
from loguru import logger

from marketplace.views import BaseMixin
from main.models import Product, Cart, Warehouse
from services.cart_services import add_product_to_user_cart, get_user_cart, WarehouseOutOfStockException, \
    get_cart_lines, merge_anonymous_user_cart_into_user_cart


class CartDetailView(BaseMixin, TemplateView):
    template_name = 'cart/cart.html'
    model = Cart

    def get_context_data(self, **kwargs):
        context = super(CartDetailView, self).get_context_data(**kwargs)
        cart = get_user_cart(user=self.request.user)
        context['cart'] = cart
        context["lines"] = get_cart_lines(cart=cart)
        return context


class AddToCartView(BaseMixin, FormView):
    def post(self, request, *args, **kwargs):

        product = Product.objects.get(slug=self.kwargs['slug'])
        warehouse = Warehouse.objects.get(id=self.kwargs['warehouse_id'])

        amount = request.POST.get('amount')
        try:
            add_product_to_user_cart(user=request.user, warehouse=warehouse,
                                     product=product, amount=int(amount))
            next_page = request.POST.get('next', '/')
        except WarehouseOutOfStockException as e:
            logger.error(f"{str(e)}")
            params = {
                "message": f"На складе у этого продавца осталось {warehouse.amount}  шт. товара, вы пытаетесь "
                           f"добавить {amount}. Укажите количество не больше чем есть на "
                           f"складе!",
                "back_url": f"{reverse('product', kwargs={'slug': product.slug})}#sellers"
            }
            uri = f"{reverse('cart-error')}?{urlencode(params)}"
            logger.debug("Redirect на страницу ошибок корзины")
            return HttpResponseRedirect(uri)
        return HttpResponseRedirect(next_page)


class CartErrorView(BaseMixin, TemplateView):
    """Представление для отображения ошибок работы с корзиной"""

    template_name = 'cart/cart_error.html'

    def get_context_data(self, **kwargs):
        context = super(CartErrorView, self).get_context_data()
        context["message"] = self.request.GET.get("message")
        context["back_url"] = self.request.GET.get("back_url")
        return context


class MergeAnonymousCartView(View):
    """Представление для вызова слияния корзины неавторизованного пользователя в корзину авторизованного пользователя"""

    def get(self, request):
        user = request.user
        logger.info(f"Вызываем вливание корзины анонимного пользователя в корзину пользователя '{user}'")
        merge_anonymous_user_cart_into_user_cart(user=user)
        logger.debug("Redirect на index")
        return HttpResponseRedirect(reverse("index"))
