from django import forms
from django.utils.translation import gettext_lazy as _

from main.models import Review


class ReviewCreateForm(forms.ModelForm):
    """ Форма создания отзыва """
    class Meta:
        model = Review
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'id': 'review', 'placeholder': _('Review')}),
            'author': forms.TextInput(attrs={'class': 'form-input', 'id': 'name', 'placeholder': _('Name')}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'id': 'email', 'placeholder': _('Email')}),
        }
        fields = ['text', 'author', 'email']
