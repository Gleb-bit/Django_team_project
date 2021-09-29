from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SettingForm(forms.Form):
    """Форма для изменения настроек кеширования и сброса кешей"""

    categories_cache = forms.IntegerField(label=_('Categories cache duration'), help_text=_('seconds'),
                                          widget=forms.NumberInput(attrs={'class': "caches-timeout"}))
    banners_cache = forms.IntegerField(label=_('Banners cache duration'), help_text=_('seconds'),
                                       widget=forms.NumberInput(attrs={'class': "caches-timeout"}))
    shops_cache = forms.IntegerField(label=_('Shops cache duration'), help_text=_('seconds'),
                                     widget=forms.NumberInput(attrs={'class': "caches-timeout"}))
    catalog_cache = forms.IntegerField(label=_('Catalog cache duration'), help_text=_('seconds'),
                                       widget=forms.NumberInput(attrs={'class': "caches-timeout"}))
    product_cache = forms.IntegerField(label=_('Product cache duration'), help_text=_('seconds'),
                                       widget=forms.NumberInput(attrs={'class': "caches-timeout"}))
    delete_categories_cache = forms.BooleanField(label=_("Delete categories cache"), required=False,
                                                 widget=forms.CheckboxInput(attrs={'class': "caches-delete"}))
    delete_banners_cache = forms.BooleanField(label=_("Delete banners cache"), required=False,
                                              widget=forms.CheckboxInput(attrs={'class': "caches-delete"}))
    delete_shops_cache = forms.BooleanField(label=_("Delete shops cache"), required=False,
                                            widget=forms.CheckboxInput(attrs={'class': "caches-delete"}))
    delete_catalog_cache = forms.BooleanField(label=_("Delete catalog cache"), required=False,
                                              widget=forms.CheckboxInput(attrs={'class': "caches-delete"}))
    delete_product_cache = forms.BooleanField(label=_("Delete product cache"), required=False,
                                              widget=forms.CheckboxInput(attrs={'class': "caches-delete"}))

    def clean_categories_cache(self):
        categories_cache = self.cleaned_data['categories_cache']
        if categories_cache <= 0:
            raise ValidationError(_('The cache timeout for categories cannot be less or equal than zero!'))

        return categories_cache

    def clean_banners_cache(self):
        banners_cache = self.cleaned_data['banners_cache']
        if banners_cache <= 0:
            raise ValidationError(_('The cache timeout for banners cannot be less or equal than zero!'))

        return banners_cache

    def clean_shops_cache(self):
        shops_cache = self.cleaned_data['shops_cache']
        if shops_cache <= 0:
            raise ValidationError(_('The cache timeout for shops cannot be less or equal than zero!'))

        return shops_cache

    def clean_catalog_cache(self):
        catalog_cache = self.cleaned_data['catalog_cache']
        if catalog_cache <= 0:
            raise ValidationError(_('The cache timeout for catalog cannot be less or equal than zero!'))

        return catalog_cache

    def clean_product_cache(self):
        product_cache = self.cleaned_data['product_cache']
        if product_cache <= 0:
            raise ValidationError(_('The cache timeout for product cannot be less or equal than zero!'))

        return product_cache

    def clean_cache(self, key: str):
        cache = self.cleaned_data[f'{key}_cache']
        if cache <= 0:
            raise ValidationError(_('The cache timeout for shops cannot be less or equal than zero!'))

        return cache
