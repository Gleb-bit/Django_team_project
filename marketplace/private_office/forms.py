from django import forms

from main.models import Profile


class ProfileForm(forms.ModelForm):
    """Форма для изменения профиля пользователя"""
    delete_avatar = forms.BooleanField(required=False)

    class Meta:
        model = Profile
        widgets = {
            'first_name': forms.TextInput(attrs={'class': "form-input", 'id': "name", 'name': "name", 'type': "text",
                                                 'data-validate': "require"}),
            'last_name': forms.TextInput(attrs={'class': "form-input", 'id': "name", 'name': "name", 'type': "text",
                                                'data-validate': "require"}),
            'patronymic': forms.TextInput(attrs={'class': "form-input", 'id': "name", 'name': "name", 'type': "text",
                                                 'data-validate': "require"}),
            'photo': forms.FileInput(
                attrs={'class': "Profile-file form-input", 'id': "avatar", 'name': "avatar", 'type': "file",
                       'data-validate': "onlyImgAvatar"}),
            'phone': forms.TextInput(attrs={'class': "form-input", 'id': "phone", 'name': "phone", 'type': "text"}),
            'mail': forms.DateTimeInput(
                attrs={'class': "form-input", 'id': "mail", 'name': "mail", 'type': "text"}),
            'delete_avatar': forms.CheckboxInput()
        }
        fields = ['first_name', 'last_name', 'patronymic', 'photo', 'phone', 'birth_date', 'mail']
