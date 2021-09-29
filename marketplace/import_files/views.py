from pprint import pprint

from django.core.mail import send_mail
from django.shortcuts import render
from django.views import generic

from import_files.forms import FileUploader
from main.models import ImportFiles
from marketplace.tasks import make_import
from marketplace.views import BaseMixin
from django.core import serializers


class ImportFileView(BaseMixin, generic.CreateView):
    model = ImportFiles
    template_name = 'import_files/import_page.html'
    form_class = FileUploader

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():

            files = request.FILES.getlist('files')
            saved_files = {}

            for file in files:
                title = str(file)
                saved_files[title] = file.read().decode('utf8')

            mail = form.cleaned_data['mail']

            make_import.delay(saved_files, mail)

        return render(request, self.template_name, {'form': form})
