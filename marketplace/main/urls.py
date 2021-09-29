from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, LoginView
from django.urls import path

from .views import IndexView, RegisterUserView, OurPasswordChangeView, OurPasswordChangeDoneView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password-change/', OurPasswordChangeView.as_view(),
         name='password_change'),
    path('password-change-done/', OurPasswordChangeDoneView.as_view(),
         name='password_change_done'),

    path('password-reset/', PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done', PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
]
