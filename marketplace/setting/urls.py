from django.urls import path

from . import views


urlpatterns = [
    path('settings', views.SettingView.as_view(), name='settings'),  # страница настроек
]
