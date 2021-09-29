from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.utils.translation import gettext_lazy as _
from loguru import logger

from main.models import CartLine, DeliveryMethod
from services.cart_services import delete_cart_line, get_user_cart_cost, get_user_cart_total_amount, clear_user_cart, \
    change_product_amount_in_cartline, get_user_cart, get_warehouse_list_modal_html_content, \
    get_modal_header_text, handle_ajax_add_to_cart
from services.payment_services import get_cost_with_delivery


class AjaxDeleteLineFromCart(View):
    """
    Представление для обработки post Ajax запросов на удаление позиции из корзины.
    В параметре cartline_id надо указать id модели CartLine.
    """

    def post(self, request):
        logger.debug(f"request.POST = {request.POST}")
        cart_line = CartLine.objects.get(id=request.POST.get("cartline_id"))
        user = request.user
        logger.debug(f"Пользователь '{user}' вызвал удаление cart_line: {cart_line}")
        delete_cart_line(cart_line)
        return JsonResponse({}, status=200)


class AjaxGetCartCostView(View):
    """
    Представление для обработки get Ajax запросов на получение стоимости корзины.
    Стоимость корзины будет в ответе в параметре cart_cost.
    """

    def get(self, request):
        user: User = request.user
        cart_cost = get_user_cart_cost(user=user)
        logger.debug(f"Пользователь '{user}' вызвал получение стоимости корзины, стоимость корзины {cart_cost}")
        return JsonResponse({"cart_cost": cart_cost,
                             }, status=200)


class AjaxGetCartSizeView(View):
    """
    Представление для обработки Ajax запросов на получение количества товаров в корзине
    Количество товаров в корзине будет в ответе в параметре cart_size.
    """

    def get(self, request):
        user: User = request.user
        cart_size = get_user_cart_total_amount(user=user)
        logger.debug(f"Пользователь '{user}' вызвал получение количества товаров в корзине,"
                     f"товаров {cart_size}")
        return JsonResponse({"cart_size": cart_size}, status=200)


class AjaxClearCartView(View):
    """
    Представление для обработки Ajax запросов для очищения корзины.
    """

    def post(self, request):
        user: User = request.user
        logger.debug(f"Пользователь '{user}' вызвал очистку корзины")
        clear_user_cart(user=user)
        return JsonResponse({}, status=200)


class AjaxChangeCartLineQuantityView(View):
    """
    Представление для обработки Ajax запросов для изменния количества товара по позиции корзины
    Для изменения количества надо в параметре cartline_id надо указать id модели CartLine;
    в параметре new_quantity - новое количество товара по позиции корзины;
    """

    def post(self, request):
        user: User = request.user
        cart_line = CartLine.objects.get(id=request.POST.get("cartline_id"))
        new_quantity = int(request.POST.get("new_quantity"))
        logger.debug(f"Пользователь '{user}' вызвал изменение CartLine: '{cart_line}', установка "
                     f"количества в {new_quantity}")
        success, message, new_stock_balance = change_product_amount_in_cartline(cart_line=cart_line,
                                                                                new_quantity=new_quantity)
        logger.debug(f"success = {success}")
        logger.debug(f"message = {message}")
        logger.debug(f"new_stock_balance = {new_stock_balance}")
        return JsonResponse({"success": success,
                             "message": message,
                             "new_stock_balance": new_stock_balance},
                            status=200)


class AjaxGetUserCartView(View):
    """
    Предствление для Ajax запросов для получения корзины пользователя.
    В ответе в параметре discount_cost будет стоимость корзины со скидками,
    в параметре old_cost стоимость корзины без скидок
    """

    def get(self, request):
        user = request.user
        cart = get_user_cart(user=user)
        logger.debug(f"Пользователь '{user}' запросил корзину {cart}")
        return JsonResponse({"discount_cost": cart.discount_cost, "old_cost": cart.cost}, status=200)


class AjaxGetWarehousesModalHTMLContentView(View):
    """
    Представлние для Ajax запросов для получения html складов по товару.
    Для получения информации надо передать в параметре 'product_id' id товара.
    В ответе в параметре modal_content будет html текст,
    в параметре modal_header_text заголовок для модального окна
    """

    def get(self, request):
        product_id = request.GET.get("product_id")
        modal_html_content = get_warehouse_list_modal_html_content(product_id=product_id)
        modal_header_text = get_modal_header_text(product_id=product_id)
        return JsonResponse({
            "modal_content": modal_html_content,
            "modal_header_text": modal_header_text
        }, status=200)


class AjaxAddToCartView(View):
    """
    Представление для Ajax запросов для добавления товаров в корзину
    Для выполнения необходимо передать:
    product_id: id товара
    warehouse_id: id склада с которого необходимо произвести списание товара
    amount: количество товара
    Параметры ответа:
    message: текст сообщения
    success: флаг успеха(True/False)
    new_stock_balance: новый остаток на складе( при success=True)
    """

    def post(self, request):
        success, message, new_stock_balance = handle_ajax_add_to_cart(
            user=request.user,
            product_id=request.POST.get("product_id"),
            warehouse_id=request.POST.get("warehouse_id"),
            amount=request.POST.get("amount")
        )
        return JsonResponse({"message": message,
                             "success": success,
                             "new_stock_balance": new_stock_balance
                             }, status=200)


class AjaxGetEmptyCartMessageView(View):
    """
    Представление для Ajax запросов для получения сообщения о пустой корзине
    Параметры ответа:
    message: текст сообщения о пустой корзине
    """

    def get(self, request):
        return JsonResponse({"message": _("Your cart is empty")}, status=200)


class AjaxOrderCostView(View):
    """
    Представление для обработки Ajax запросов для вычисления стоимости заказа с учетом доставки.
    """

    def post(self, request):
        cart = get_user_cart(user=request.user)
        delivery = request.POST.get('delivery')
        delivery_method = DeliveryMethod.objects.get(name=delivery)
        total_price = get_cost_with_delivery(cart, delivery_method)
        logger.debug(
            f'Получение стоимости заказа с учетом доставки. '
            f'delivery_method: {delivery_method}, total_price: {total_price}'
        )
        return JsonResponse({'total_price': total_price}, status=200)
