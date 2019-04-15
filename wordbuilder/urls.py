from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy

from wordbuilder import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('index')), name='logout'),
    path('dictionary/', views.DictionaryView.as_view(), name='dictionary'),

    path('reset-password/',
         PasswordResetView.as_view(template_name='registration/password-reset-form.html',
                                   email_template_name='registration/password-reset-email.html'),
         name='password_reset'),

    path('reset-password/done/',
         PasswordResetDoneView.as_view(template_name='registration/password-reset-done.html'),
         name='password_reset_done'),

    path('reset-password-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='registration/password-reset-confirm.html'),
         name='password_reset_confirm'),

    path('reset-password-complete/',
         PasswordResetCompleteView.as_view(template_name='registration/password-reset-complete.html'),
         name='password_reset_complete'),
]
