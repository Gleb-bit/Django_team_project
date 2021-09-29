from django import forms

from main.models import ImportFiles


class FileUploader(forms.ModelForm):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = ImportFiles
        fields = ['files', 'mail', 'status']
        widgets = {
            'status': forms.TextInput(attrs={'readonly': 'readonly'})
        }
