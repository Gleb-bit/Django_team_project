from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import IndexView, RegisterUserView, OurPasswordChangeView, OurPasswordChangeDoneView, OurLoginView, \
    OurPasswordResetCompleteView, OurPasswordResetView, OurPasswordResetConfirmView, OurPasswordResetDoneView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', OurLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password-change/', OurPasswordChangeView.as_view(),
         name='password_change'),
    path('password-change-done/', OurPasswordChangeDoneView.as_view(),
         name='password_change_done'),

    path('password-reset/', OurPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', OurPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', OurPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done', OurPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
