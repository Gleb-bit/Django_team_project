from django import forms
from django.utils.translation import gettext_lazy as _

DELIVERY_METHODS = [
    ('regular', _('Regular shipping')),
    ('express', _('Express delivery')),
]

PAYMENT_METHODS = [
    ('online', _('Online payment by card')),
    ('someone', _("Online payment from a random someone else's account")),
]


class OrderForm(forms.Form):
    """ Форма создания заказа """
    fio = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-input', 'id': 'name', 'placeholder': _('Full name'), 'data-validate': 'require'}
    ))
    phone = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-input', 'id': 'phone', 'placeholder': _("Phone"), 'data-validate': 'require'}
    ))
    mail = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-input', 'id': 'mail', 'placeholder': _('Email'), 'data-validate': 'require'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-input', 'id': 'password', 'placeholder': _('Here you can change your password')}
    ), required=False)
    passwordReply = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-input', 'id': 'passwordReply', 'placeholder': _('Please re-enter your password')}
    ), required=False)
    delivery = forms.ChoiceField(widget=forms.RadioSelect(), choices=DELIVERY_METHODS, initial='regular')
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'city', 'data-validate': 'require'}))
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'id': 'address', 'data-validate': 'require'}))
    pay = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_METHODS, initial='online')


class PaymentCardForm(forms.Form):
    card = forms.IntegerField()
