from typing import List

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from loguru import logger

from main.models import Profile, Order, PaymentMethod, PaymentState, DeliveryMethod, Cart, Warehouse
from services.cart_services import get_user_cart, get_discount_cart_cost


def create_customer(name_list: List[str], mail: str, phone: str) -> Profile:
    """
    Создание нового профиля покупателя
    :param name_list: список ФИО
    :param mail: Электронная почта
    :param phone: телефон
    :return: Объект профиля
    """
    try:
        customer = Profile.objects.get(mail=mail)
    except Profile.DoesNotExist:
        user = User.objects.create_user(mail)
        customer = user.profile
        customer.first_name = name_list[1]
        customer.last_name = name_list[0]
        customer.patronymic = name_list[2]
        customer.mail = mail
        customer.phone = phone
        customer.save()
    logger.info(
        f'Создан профиль покупателя. {customer.last_name} {customer.first_name} {customer.patronymic} {customer.mail}')
    return customer


def create_order(customer: Profile, delivery: str, pay: str, city: str, address: str) -> Order:
    """
    Создание нового заказа
    :param customer: профиль покупателя
    :param delivery: название способа доставки
    :param pay: название способа оплаты
    :param city: город
    :param address: адрес
    :return: объект заказа
    """
    cart = get_user_cart(user=customer.user)
    delivery_method = DeliveryMethod.objects.get(name=delivery)
    cost = get_cost_with_delivery(cart, delivery_method)
    order = Order.objects.create(
        customer=customer,
        cart=cart,
        total_price=cost,
        payment_method=PaymentMethod.objects.get(name=pay),
        delivery_method=delivery_method,
        payment_state=PaymentState.objects.get(name='not payed'),
        city=city,
        address=address,
    )
    logger.info(f'Создан заказ #{order.id}')
    cart.is_payed = True
    cart.save()
    return order


def get_cost_with_delivery(cart: Cart, delivery: DeliveryMethod) -> float:
    """
    Получение стоимости заказа с учетом доставки
    :param cart: объект корзины
    :param delivery: объект способа доставки
    :return: стоимость
    """
    logger.debug('Получение стоимости заказа с учетом доставки')
    cost = get_discount_cart_cost(cart)
    if cost >= delivery.free_shipping_threshold:
        return cost + delivery.extra_price
    elif get_free_shipping(cart):
        return cost + delivery.extra_price
    elif get_shops_set(cart):
        return cost + delivery.extra_price
    else:
        return cost + delivery.extra_price + delivery.base_price


def get_free_shipping(cart: Cart) -> bool:
    """
    Проверка наличия условия бесплатной доставки в товарах корзины
    :param cart: объект корзины
    :return: булево значение возможности бесплатной доставки
    """
    logger.debug('Проверка наличия условия бесплатной доставки в товарах корзины')
    for line in cart.lines.all():
        warehouse = Warehouse.objects.get(product=line.product, shop=line.shop)
        if not warehouse.free_shipping:
            return False
    else:
        return True


def get_shops_set(cart: Cart) -> bool:
    """
    Проверка товаров в корзине из одного ли они магазина
    :param cart: объект корзины
    :return: булево значение того из одного ли магазина товары
    """
    logger.debug('Проверка товаров в корзине из одного ли они магазина')
    shops = set()
    for line in cart.lines.all():
        shops.add(line.shop)
    if len(shops) == 1:
        return True
    else:
        return False


def confirm_payment(order: Order, session, success: bool, token: str, context: dict) -> dict:
    """
    Подтверждение оплаты
    :param order: объект заказа
    :param session: объект сессии
    :param success: булево значение успешной оплаты
    :param token: токен авторизации оплаты
    :param context: контекст представления
    :return: обновленный контекст представления
    """
    logger.debug('Подтверждение оплаты')
    if success:
        if token == session['payment_credentials']['token']:
            order.payment_state = PaymentState.objects.get(name='payed')
            order.save()
            logger.info(f'Заказ #{order.id} успешно оплачен')
        else:
            logger.error('Токен авторизации не опознан')
            context['payment_error'] = True
            context['payment_error_text'] = _('Payment failed because of invalid authorisation token')
    else:
        logger.error('Оплата не прошла')
        context['payment_error'] = True
        context['payment_error_text'] = _('Payment failed because of suspicion of your crying intolerance')
    return context
