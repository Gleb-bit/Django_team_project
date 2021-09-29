from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.views.generic import TemplateView
from loguru import logger

from marketplace.views import BannersContextMixin, BaseMixin
from .forms import RegisterForm
from .models import Product


class IndexView(BaseMixin, BannersContextMixin, TemplateView):
    """ Представление домашней страницы """
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        logger.debug(f'Получение контекста домашней страницы')
        context = super(IndexView, self).get_context_data(**kwargs)
        context['top_products'] = Product.objects.filter(is_active=True).order_by('-sells').order_by('-sort_index')[:8]
        return context


class RegisterUserView(BaseMixin, CreateView):
    """
    Представление для регистрации
    """
    form_class = RegisterForm
    template_name = 'register.html'

    def form_valid(self, form):
        form.save()
        user = authenticate(
            request=self.request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        login(self.request, user)
        return redirect('/')


class OurPasswordChangeView(BaseMixin, PasswordChangeView):
    """Представление для кастомной смены пароля"""

    template_name = 'password_change.html'


class OurPasswordChangeDoneView(BaseMixin, PasswordChangeDoneView):
    """Представление для кастомного подтверждения смены пароля"""

    template_name = 'password_change_done.html'
