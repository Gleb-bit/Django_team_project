from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from django_svg_image_form_field import SvgAndImageFormField

from main.models import Category


class RegisterForm(UserCreationForm):
    """Форма для расширения стандартной формы регистрации"""
    photo = forms.ImageField(label=_('Photo'), required=False)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = []
        field_classes = {
            'img': SvgAndImageFormField,
        }
