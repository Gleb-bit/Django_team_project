from django.urls import path

from import_files.views import ImportFileView

urlpatterns = [
    path('import/', ImportFileView.as_view(), name='import')
]
