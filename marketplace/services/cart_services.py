# модуль для работы с корзиной
from typing import Tuple, Union

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F, Q, Sum, QuerySet
from django.utils.translation import gettext_lazy as _
from loguru import logger

from main.models import Cart, CartLine, Product, Warehouse, Discount
from marketplace.settings import MEDIA_URL
from services.user_services import handle_anonymous, _get_anonymous_user


class WarehouseOutOfStockException(Exception):
    """Класс исключения, когда пользователь пытается добавить в корзину товара больше, чем есть на складе продавца"""
    pass


@handle_anonymous
@transaction.atomic
def add_product_to_user_cart(user: User, warehouse: Warehouse, product: Product, amount: int = 1) -> None:
    """
    Метод добавления продуктов со склада Warehouse в корзину пользователя user в количестве amount
    Важно: параметр user должен передаваться как именованный

    :param user: Пользователь
    :param warehouse: склад продавца с которого надо списать товар в корзину пользователя
    :param product: товар
    :param amount: количество товара. По умолчанию 1
    :return: None
    """

    cart = get_user_cart(user=user)
    if amount < 1:
        logger.warning(f"В метод add_product_to_user_cart передано amount={amount}. Выход из метода")
        return

    if warehouse.amount < amount:
        raise WarehouseOutOfStockException(f"Пользователь '{user}' попытался добавить в корзину товар {product.name}"
                                           f" со склада продавца '{warehouse}' в количестве {amount}, на складе только "
                                           f"{warehouse.amount} штук")
    try:
        cartline = CartLine.objects.get(cart=cart, product=product, shop=warehouse.shop)
        cartline.quantity = F('quantity') + amount
        cartline.save()
        logger.debug(f"В корзину пользователя '{user}', к продукту '{product.name}' магазина '{warehouse.shop.name}'"
                     f" добавлено {amount} штук, по цене {warehouse.price}")
    except CartLine.DoesNotExist:
        CartLine.objects.create(cart=cart, shop=warehouse.shop, product=product,
                                price=warehouse.price, quantity=amount)
        logger.debug(
            f"В корзину пользователя '{user}', добавлен продукт '{product.name}' магазина '{warehouse.shop.name}'"
            f" в количестве {amount} штук, по цене {warehouse.price}")
    cost_delta = warehouse.price * amount
    logger.debug(f"Со склада '{warehouse}' списываем товар '{product.name}' в количестве {amount} штук")
    warehouse.amount = F('amount') - amount
    warehouse.save()
    logger.debug(f"Увеличиваем стоимость корзины '{cart}' на {cost_delta}")
    cart.cost = F('cost') + cost_delta
    cart.save()


@transaction.atomic
def delete_cart_line(cart_line: CartLine) -> None:
    """
    Метод для удаления объекта cart_line

    :param cart_line: запись корзины пользователя
    :return: None
    """

    cart = cart_line.cart
    warehouse = get_warehouse_by_cart_line(cart_line=cart_line)
    logger.debug(f"Увеличиваем количество товара на '{cart_line.quantity}', для склада warehouse = {warehouse}")
    warehouse.amount = F('amount') + cart_line.quantity
    warehouse.save()
    cost_delta = cart_line.price * cart_line.quantity
    logger.debug(f"Уменьшаем стоимость корзины '{cart}' на {cost_delta}")
    cart.cost = F('cost') - cost_delta
    cart.save()
    logger.debug(f"удаление cart_line: {cart_line}")
    cart_line.delete()


@transaction.atomic
def change_product_amount_in_cartline(cart_line: CartLine, new_quantity: int) -> Tuple[bool, str, Union[None, int]]:
    """
    Метод для изменения количества товара в позиции корзины пользователя

    :param cart_line: Экземпляр модели CartLine - позиции корзины пользоватея
    :param new_quantity: новое количество товара для позиции корзины
    :return: Кортеж: флаг успеха, сообщение, новое количество товара на складе в случае успеха или None в случае неудачи
    """

    success_message = _("Changes applied")
    logger.debug("change_product_amount_in_cartline log")
    logger.debug(f"cart_line до изменений: {cart_line}")
    logger.debug(f"Запрашиваемое значение товара: {new_quantity}")

    if new_quantity == 0:
        logger.debug("Новое значение товара 0, удаление cart_line")
        delete_cart_line(cart_line)
        return True, '', None

    warehouse = get_warehouse_by_cart_line(cart_line=cart_line)
    logger.debug(f"Склад: {warehouse}")
    quantity_delta = new_quantity - cart_line.quantity
    logger.debug(f"quantity_delta = {quantity_delta}")
    if warehouse.amount < quantity_delta:
        logger.debug("Недотостаточно товара на складе, выход из метода")
        return False, _("Not enough products"), None

    # товара на складе достаточно, можно менять
    logger.debug("Товара на складе достаточно, производим изменения")
    warehouse.amount -= quantity_delta
    warehouse.save()
    logger.debug(f"Уменьшено количество тована на складе на {quantity_delta}")

    cart_line.quantity += quantity_delta
    cart_line.save()
    logger.debug(f"К позиции корзины добавлено {quantity_delta} шт товара")

    cart: Cart = cart_line.cart
    logger.debug(f"Корзина до изменения: {cart}")
    cost_delta = cart_line.price * quantity_delta
    cart.cost += cost_delta
    cart.save()
    logger.debug(f"К стоимости корзины добавлено {cost_delta}")

    return True, success_message, warehouse.amount


@handle_anonymous
def get_user_cart_total_amount(user: User) -> int:
    """
    Функция для получения общего количество товаров в корзине пользователя user
    Важно: параметр user должен передаваться как именованный

    :param user: Пользоваетель, экзмепляр модели User
    :return: Общее количество товаров в корзине пользователя user
    """

    cart = get_user_cart(user=user)
    total_amount = CartLine.objects.filter(cart=cart).aggregate(Sum('quantity'))["quantity__sum"]

    return total_amount if total_amount else 0


@handle_anonymous
def get_user_cart_cost(user: User) -> float:
    """
    Функция для получения стоимости корзины пользователя user
    Важно: параметр user должен передаваться как именованный
    """

    cart = get_user_cart(user=user)
    return cart.discount_cost


@handle_anonymous
@transaction.atomic
def clear_user_cart(user: User) -> None:
    """
    Метод для очистки корзины пользователя
    Важно: параметр user должен передаваться как именованный

    :param user: пользователь
    :return: None
    """
    logger.debug("clear_user_cart log")
    cart = get_user_cart(user=user)
    cart_lines = CartLine.objects.filter(cart=cart)
    for cart_line in cart_lines:
        logger.debug(f"Обработка позиции: {cart_line}")
        warehouse = get_warehouse_by_cart_line(cart_line=cart_line)
        logger.debug(f"Добавляем {cart_line.quantity} шт товара на склад {warehouse}")
        warehouse.amount = F('amount') + cart_line.quantity
        warehouse.save()
        cost_delta = cart_line.quantity * cart_line.price
        cart.cost = F('cost') - cost_delta
        cart.save()
        logger.debug(f"Стоимость корзины уменьшена на {cost_delta}")
    cart_lines.delete()
    logger.info(f"Выполнена отчистка корзины пользователя {user}")


@handle_anonymous
def get_user_cart(user: User) -> Cart:
    """
    Функция получения корзины пользователя
    Если корзины не существует, будет создана новая
    Важно: параметр user должен передаваться как именованный
    """

    logger.debug("get_user_cart log")
    try:
        cart = Cart.objects.get(user=user, is_payed=False)
    except Cart.DoesNotExist:
        logger.info(f"У пользователя не существовало корзины, создана новая")
        cart = Cart.objects.create(user=user, is_payed=False, cost=0)
    cart.discount_cost = get_discount_cart_cost(cart=cart)
    logger.debug(f"cart = {cart}")
    logger.debug(f"cart.cost = {cart.cost}, cart.discount_cost = {cart.discount_cost}")
    return cart


def get_cart_lines(cart: Cart) -> QuerySet[CartLine]:
    """
    Функция получения позиций корзины.
    Ко всем записям добавляется атрибут warehouse_amount = количество товара на складе продавца
    К позициям для которых у товара есть скидка добавлятся атрибут discount_price = цена на товар продавца по скидке,
    если скидки нет, то устанавливается цена как есть
    """
    lines: QuerySet[CartLine] = cart.lines.all()
    logger.debug("get_cart_lines log")
    logger.debug(f"cart = {cart}")

    for line in lines:
        logger.debug(f"line = {line}")
        warehouse = get_warehouse_by_cart_line(cart_line=line)
        line.warehouse_amount = warehouse.amount
        line_product = line.product
        logger.debug(f"line_product = {line_product}")
        warehouse_discounts = get_discounts_for_warehouse(warehouse=warehouse)
        if warehouse_discounts:
            best_discount = get_best_warehouse_discount(warehouse_discounts=warehouse_discounts)
            best_discount_percent = best_discount.percent
            logger.debug(f"На товар действует скидка {best_discount_percent}%")
            line.discount_price = line.price * (100 - best_discount_percent) / 100
            line.discount_percent = best_discount_percent
            logger.debug(f"line.discount_price установлена в {line.discount_price}")
        else:
            logger.debug(f"На товар этого склада нет скидки, line.discount_price = line.price ({line.price})")
            line.discount_price = line.price

    return lines


def get_discounts_for_warehouse(warehouse: Warehouse) -> QuerySet[Discount]:
    """Функция получения списка скидок по складу, то есть на товар конкретного продавца"""

    product = warehouse.product
    all_product_discounts: QuerySet[Discount] = product.get_active_discounts()
    warehouse_discounts = all_product_discounts.filter(Q(shop=warehouse.shop) | Q(shop=None))
    return warehouse_discounts


def get_best_warehouse_discount(warehouse_discounts: QuerySet[Discount]) -> Discount:
    """Функция получения лучшей скидки по всем скидкам этого склада"""

    return warehouse_discounts.order_by('-percent').first()


def get_discount_cart_cost(cart: Cart) -> float:
    """
    Функция для получения цены корзины со скидкой.
    Если на позиции корзины нет скидок, то вернётся цена корзины как есть
    """
    cart_lines = get_cart_lines(cart=cart)
    discount_cart_cost = sum([line.discount_price * line.quantity for line in cart_lines])

    return discount_cart_cost


@transaction.atomic
def merge_anonymous_user_cart_into_user_cart(user: User) -> None:
    """Метод для слияния корзины неавторизованного пользователя с корзиной пользователя user"""

    logger.debug("merge_anonymous_user_cart_into_user_cart log")
    anonymous_user = _get_anonymous_user()
    anonymous_user_cart = get_user_cart(user=anonymous_user)
    anonymous_cart_lines: QuerySet[CartLine] = anonymous_user_cart.lines.all()

    if not anonymous_cart_lines:
        logger.info("У неавторизованного пользователя нет позиций в корзине, выходим")
        return

    logger.info(f"Начинаем вливать позиции корзины неавторизованного пользователя в корзину пользователя '{user}'")
    for line in anonymous_cart_lines:
        _merge_user_cart_line_by_cartline(user=user, line=line)
    logger.debug("Вливание выполнено")

    # не вызывается clear_user_cart, что бы не увеличить количество товара на складах продавцов,
    # потому что количество товара в корзине пользователя user изменяется напрямую, а не через склад продавца
    anonymous_cart_lines.delete()
    anonymous_user_cart.cost = 0
    anonymous_user_cart.save()
    logger.info("Очищена корзина неавторизованного пользователя")


def get_warehouse_by_cart_line(cart_line: CartLine) -> Warehouse:
    """Получение склада(Warehouse) по позиции корзины (объекту CartLine)"""

    warehouse = Warehouse.objects.get(shop=cart_line.shop, product=cart_line.product)

    return warehouse


def _merge_user_cart_line_by_cartline(user: User, line: CartLine) -> None:
    """
    Вспомогательный метод для слияния корзин неавторизованного пользователя и авторизаванного пользователя
    Обновляет позицию корзины пользователя user или создаёт новую позицию, если нужной позиции нет
    """

    cart = get_user_cart(user=user)
    warehouse = get_warehouse_by_cart_line(line)
    product = line.product
    amount = line.quantity

    logger.debug("_merge_user_cart_line_by_cartline log")
    logger.debug(f"user_cart = {cart}")
    logger.debug(f"warehouse = {warehouse}")
    logger.debug(f"product = {product}")
    logger.debug(f"amount = {amount}")

    try:
        cartline = CartLine.objects.get(cart=cart, product=product, shop=warehouse.shop)
        cartline.quantity = F('quantity') + amount
        cartline.save()
        logger.debug(
            f"В корзину пользователя '{user}', к продукту '{product.name}' магазина '{warehouse.shop.name}'"
            f" добавлено {amount} штук, по цене {cartline.price}")
    except CartLine.DoesNotExist:
        CartLine.objects.create(cart=cart, shop=warehouse.shop, product=product,
                                price=warehouse.price, quantity=amount)
        logger.debug(
            f"В корзину пользователя '{user}', добавлен продукт '{product.name}' магазина '{warehouse.shop.name}'"
            f" в количестве {amount} штук, по цене {warehouse.price}")

    # обновляем стоимость корзины пользователя
    cost_delta = line.price * amount  # что бы брать цену по позиции корзины анонима
    logger.debug(f"Увеличиваем стоимость корзины '{cart}' на {cost_delta}")
    cart.cost = F('cost') + cost_delta
    cart.save()


def get_warehouse_list_by_product_id(product_id: int) -> QuerySet[Warehouse]:
    """
    Функция для получения списка складов по id товара product_id.
    Добавляется атрибут discount_price - цена по скидке, если скидки нет то discount_price = price,
    для соотвествующего склада
    """

    warehouse_list = Warehouse.objects.filter(product=product_id).filter(amount__gt=0)
    for warehouse in warehouse_list:
        add_discount_price_to_warehouse(warehouse=warehouse)
    return warehouse_list


def add_discount_price_to_warehouse(warehouse: Warehouse) -> None:
    """Метод для добавления атрибута discount_price - цена по скидке, если скидки нет то discount_price = price"""

    warehouse_discounts = get_discounts_for_warehouse(warehouse=warehouse)
    if warehouse_discounts:
        best_discount = get_best_warehouse_discount(warehouse_discounts=warehouse_discounts)
        best_discount_percent = best_discount.percent
        warehouse.discount_price = warehouse.price * (100 - best_discount_percent) / 100
    else:
        warehouse.discount_price = warehouse.price


def get_warehouse_list_modal_html_content(product_id: int) -> str:
    """Функция для получения html содержимого модального окна списка складов"""

    warehouse_list = get_warehouse_list_by_product_id(product_id=product_id)
    if not warehouse_list:
        modal_html = f"<p>{_('The product is out of stock')}</p>"
        return modal_html

    modal_html = """
    <form class="form Cart" action="#" method="post">
    """
    for warehouse in warehouse_list:
        modal_html += get_warehouse_line_html(warehouse=warehouse)
    modal_html += """</form>"""
    logger.debug(f"modal_html = {modal_html}")
    return modal_html


def get_warehouse_line_html(warehouse: Warehouse) -> str:
    """Функция для получения html для строки склада warehouse"""

    warehouse_line_html = f"""
    <div class="Cart-product">
    <div class="Cart-block Cart-block_row">
        <div class="Cart-block Cart-block_seller">
            <a class="Cart-title" href="/shop/shop-detail/{warehouse.shop.id}">
                <strong>{ warehouse.shop.name }</strong>
            </a>
        </div>
        <div class="Cart-block">
            <img src="{ MEDIA_URL }{ warehouse.shop.img }" alt="{ warehouse.shop.name }" style="width: 50px" />
        </div>
        <div class="Cart-block">
            {_('Stock balance')}:
            <span class="Stock-balance" data-warehouse-id="{warehouse.id}" >{ warehouse.amount }</span>
        </div>
        <div class="Cart-block Cart-block_price">"""
    if warehouse.discount_price != warehouse.price:
        warehouse_line_html += f"""<div class="Cart-price">{ warehouse.discount_price}$</div>
        <div class="Cart-price Cart-price_old">{ warehouse.price }$</div>
        """
    else:
        warehouse_line_html += f"""<div class="Cart-price">{ warehouse.price }$</div>"""

    warehouse_line_html += f"""</div>
        <div class="Cart-block Cart-block_amount" data-warehouse-id="{warehouse.id}">
        <div class="Cart-amount">
        <div class="Amount">
        <button class="Amount-remove" type="button">
        </button>
        <input class="Amount-input form-input" name="amount" type="text" value=1 data-warehouse-id="{warehouse.id}">
        <button class="Amount-add" type="button">
        </button>
        </div>
        <span class="Cart-accept-message" data-warehouse-id="{warehouse.id}"></span>
        </div>
        </div>
        <div class="Cart-block">
        <button class="btn btn_primary btn__add-to-cart" data-warehouse-id="{warehouse.id}">
          <img class="btn-icon" src="{ MEDIA_URL }icons/card/cart_white.svg" alt="cart_white.svg"/>
          <span class="btn-content">{_('Add to cart')}</span>
        </button>
        </div>
    </div>
    </div>
    """
    return warehouse_line_html


def get_modal_header_text(product_id: int) -> str:
    """Функция для получения текста заголовка модального окна добавления товара в корзину"""

    product = Product.objects.get(id=product_id)
    header_text = product.name + _(" add to cart")
    return header_text


def handle_ajax_add_to_cart(user: User, product_id: int, warehouse_id: int, amount: int) -> Tuple[bool, str, Union[int, None]]:
    """
    Метод для обработки ajax запроса по добавению товара в корзину
    """
    logger.debug("handle_ajax_add_to_cart log")
    product = Product.objects.get(id=product_id)
    warehouse = Warehouse.objects.get(id=warehouse_id)
    logger.debug(f"user = {user}; product = {product}; warehouse = {warehouse}; amount = {amount}")
    try:
        amount = int(amount)
        if amount < 1:
            return False, _("Incorrect value"), None
        add_product_to_user_cart(user=user, warehouse=warehouse, product=product, amount=int(amount))
        new_stock_balance = Warehouse.objects.get(id=warehouse_id).amount
        return True, _("Products added"), new_stock_balance
    except WarehouseOutOfStockException as e:
        logger.error(f"{str(e)}")
        return False, _("Not enough products"), None
    except ValueError as e:
        logger.error(f"{str(e)}")
        return False, _("Incorrect value"), None
