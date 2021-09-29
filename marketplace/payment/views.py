import json
from secrets import token_urlsafe

import requests
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from loguru import logger

from main.models import Order, DeliveryMethod, PaymentMethod, PaymentState
from marketplace.views import BaseMixin
from payment.forms import OrderForm, DELIVERY_METHODS, PAYMENT_METHODS, PaymentCardForm
from services.cart_services import get_user_cart, get_cart_lines
from services.payment_services import create_customer, create_order, confirm_payment

PAYMENT_STATES = [
    ('payed', _('Paid up')),
    ('not payed', _('Not paid')),
]
SERVER_URL = 'http://127.0.0.1:5000'


class OrderFormView(BaseMixin, FormView):
    """ Представление формы создания заказа """
    template_name = 'payment/order.html'
    form_class = OrderForm
    success_url = '/payment/confirm'

    def get(self, request, *args, **kwargs):
        if 'reg' in request.GET:
            logger.debug(f'Инициализация формы для авторизованного пользователя')
            if request.user.is_authenticated:
                self.initial = self.get_initial()
                self.initial['fio'] = ' '.join(
                    (request.user.profile.last_name, request.user.profile.first_name, request.user.profile.patronymic)
                )
                self.initial['phone'] = request.user.profile.phone
                self.initial['mail'] = request.user.profile.mail
            else:
                return redirect(reverse('login') + '?next=/payment/?reg=1')
        return super(OrderFormView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        logger.debug(f'Получение контекста формы создания заказа')
        context = super(OrderFormView, self).get_context_data(**kwargs)
        cart = get_user_cart(user=self.request.user)
        context['cart'] = cart
        context["lines"] = get_cart_lines(cart=cart)
        return context

    def form_valid(self, form):
        logger.debug(f'Форма создания заказа валидна')
        name_list = form.cleaned_data['fio'].split()
        mail = form.cleaned_data['mail']
        phone = form.cleaned_data['phone']
        delivery = form.cleaned_data['delivery']
        city = form.cleaned_data['city']
        address = form.cleaned_data['address']
        pay = form.cleaned_data['pay']
        if self.request.user.is_authenticated:
            customer = self.request.user.profile
        else:
            customer = create_customer(name_list, mail, phone)
        create_order(customer, delivery, pay, city, address)
        return super(OrderFormView, self).form_valid(form)


class OrderView(BaseMixin, TemplateView):
    """ Представление детальной страницы заказа """
    template_name = 'payment/oneorder.html'

    def get_context_data(self, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)
        customer = self.request.user.profile
        if 'pk' in kwargs:
            order = Order.objects.get(id=kwargs['pk'])
        else:
            order = customer.order.order_by('-tm')[0]
        logger.debug(f'Получение контекста заказа #{order.id}')
        context['fio'] = f'{customer.last_name} {customer.first_name} {customer.patronymic}'
        context['customer'] = customer
        context['order'] = order
        context['date'] = order.tm.strftime('%d.%m.%y')
        context['delivery'] = self.get_delivery_method_str(order.delivery_method)
        context['payment'] = self.get_payment_method_str(order.payment_method)
        context['payment_error'] = False
        cart = order.cart
        context['cart'] = cart
        context["lines"] = get_cart_lines(cart=cart)
        if 'success' in self.kwargs:
            if 'token' in self.kwargs:
                context = confirm_payment(
                    order, self.request.session, self.kwargs['success'], self.kwargs['token'], context)
            else:
                context['payment_error'] = True
                context['payment_error_text'] = _('Payment failed because if invalid authorisation token')
        context['payment_state'] = self.get_payment_state_str(order.payment_state)
        return context

    @staticmethod
    def get_delivery_method_str(delivery_method: DeliveryMethod) -> str:
        """
        Получение переведенного названия способа доставки
        :param delivery_method: объект способа доставки
        :return: переведенное название способа доставки
        """
        for method in DELIVERY_METHODS:
            if method[0] == delivery_method.name:
                return method[1]

    @staticmethod
    def get_payment_method_str(payment_method: PaymentMethod) -> str:
        """
        Получение переведенного названия способа оплаты
        :param payment_method: объект способа оплаты
        :return: переведенное название способа оплаты
        """
        for method in PAYMENT_METHODS:
            if method[0] == payment_method.name:
                return method[1]

    @staticmethod
    def get_payment_state_str(payment_state: PaymentState) -> str:
        """
        Получение переведенного названия статуса оплаты
        :param payment_state: объект статуса оплаты
        :return: переведенное название статуса оплаты
        """
        for state in PAYMENT_STATES:
            if state[0] == payment_state.name:
                return state[1]


class OrderPayView(BaseMixin, FormView):
    """ Представление процесса оплаты """
    template_name = 'payment/payment.html'
    form_class = PaymentCardForm

    def get_context_data(self, **kwargs):
        context = super(OrderPayView, self).get_context_data(**kwargs)
        customer = self.request.user.profile
        order = customer.order.order_by('-tm')[0]
        context['order'] = order
        return context

    def post(self, request, *args, **kwargs):
        token = token_urlsafe(16)
        card = self.request.POST['numero1'].replace(' ', '')
        self.request.session['payment_credentials'] = {
            'token': token,
            'card': card,
        }
        response = requests.post(
            f'{SERVER_URL}/payment-credentials', json=json.dumps(self.request.session['payment_credentials']))
        if response.status_code == 201:
            return redirect(reverse('progress-payment'))
        else:
            return redirect(reverse('order-error'))


class PaymentProgressView(BaseMixin, TemplateView):
    """ Представление ожидания результата оплаты """
    template_name = 'payment/progressPayment.html'

    def get_context_data(self, **kwargs):
        logger.debug(f'Старт процесса оплаты заказа')
        context = super(PaymentProgressView, self).get_context_data(**kwargs)
        context['card'] = self.request.session['payment_credentials']['card']
        context['server_url'] = SERVER_URL
        return context
