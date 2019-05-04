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
    path('words/<str:word>/', views.WordDataView.as_view(), name='word_data'),
    path('user_words/', views.UserWordView.as_view(), name='user_words'),
    path('user_words/<int:word_set_pk>/', views.UserWordView.as_view(), name='get_user_words'),
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

    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile-update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('update_word_progress/', views.ProgressUpdateAjaxView.as_view(), name='update_word_progress'),
    path('trainings/', views.TrainingsView.as_view(), name='trainings'),
    path('trainings/word_constructor/<str:category>/', views.WordConstructorView.as_view(), name='word_constructor'),
    path('trainings/pronunciation/<str:category>/', views.PronunciationView.as_view(), name='pronunciation'),
    path('wordsets/', views.WordSetView.as_view(), name='wordsets'),
    path('add-wordset/', views.WordSetCreateView.as_view(), name='add_wordset'),
    path('update-wordset/<int:word_set_id>', views.WordSetUpdateView.as_view(), name='update_wordset'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('catalog/<int:word_set_id>', views.WordSetDetailView.as_view(), name='wordset_detail'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
]
