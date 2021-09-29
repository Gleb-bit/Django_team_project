from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic import TemplateView
from loguru import logger

from .forms import SettingForm
from marketplace.views import BaseMixin
from services.settings_services import get_actual_settings, process_settings_page


class SettingView(BaseMixin, TemplateView):
    """Представление для страницы управления настройками"""

    form_class = SettingForm
    template_name = 'setting/settings.html'

    def get_context_data(self, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied()
        context = super().get_context_data(**kwargs)
        actual_settings = get_actual_settings()
        form = SettingForm({"categories_cache": actual_settings.categories_cache_timeout,
                            "banners_cache": actual_settings.banners_cache_timeout,
                            "shops_cache": actual_settings.shops_cache_timeout,
                            "catalog_cache": actual_settings.catalog_cache_timeout,
                            "product_cache": actual_settings.product_cache_timeout})
        context['form'] = form
        return context

    def post(self, request):
        setting_form = SettingForm(request.POST)
        context = self.get_context_data()
        context["form"] = setting_form
        if setting_form.is_valid():
            logger.info(f'Изменение настроек пользователем {request.user}')
            context["message"] = process_settings_page(setting_form)

        return render(request, self.template_name, context)
