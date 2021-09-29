import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic
from django.urls import reverse

from main.models import Profile, Cart, Discount, Order
from marketplace.views import BaseMixin
from private_office.forms import ProfileForm
from services.utils import RecentProductsEngine


class DetailPrivateOfficeView(BaseMixin, LoginRequiredMixin, generic.DetailView):
    """Представление для просмотра личного кабинета"""

    template_name = 'private_office/private_office_list.html'
    model = Profile

    NUMBER_RECENT_PRODUCTS_TO_SHOW = 3

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        self.object = self.get_object(self.queryset)
        context = super().get_context_data()
        return context

    def get(self, request, *args, **kwargs):
        last_order = Order.objects.filter(customer=request.user.profile).order_by('tm').last()

        account_data = Profile.objects.only('user').filter(user=request.user).first()
        recent_products = RecentProductsEngine.get_recent_products_to_display(request.user,
                                                                              self.NUMBER_RECENT_PRODUCTS_TO_SHOW)

        context = {
            'last_order': last_order,
            'account_data': account_data,
            'recent_products': recent_products
        }

        context = {**context, **self.get_context_data()}

        return render(request, self.template_name, context)


class LastViewedProductsView(BaseMixin, generic.ListView):
    """Представление для просмотра последних просмотренных товаров"""

    template_name = 'private_office/last_products.html'
    context_object_name = 'last_products'

    def get_queryset(self):
        queryset = RecentProductsEngine.get_recent_products_to_display(self.request.user)
        return queryset


class ProfileUpdateView(BaseMixin, LoginRequiredMixin, generic.UpdateView):
    """Представление для изменения профиля"""

    model = Profile
    template_name = 'private_office/profile.html'
    context_object_name = 'profile_data'
    form_class = ProfileForm
    success_url = '/private_office/profile/'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        obj = form.save(commit=False)
        to_delete_photo = form.cleaned_data.get('delete_avatar')

        if to_delete_photo:
            obj.photo = obj.photo.field.default

        obj.save()

        return super().form_valid(form)


class OrderListView(BaseMixin, generic.ListView):
    """Представление для просмотра совершенных заказов"""

    template_name = 'private_office/historyorder.html'
    context_object_name = 'order_list'

    def get_queryset(self):
        queryset = Order.objects.filter(customer=self.request.user.profile).order_by('-tm')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        return context
