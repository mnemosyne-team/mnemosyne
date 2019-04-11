from django.urls import path

from wordbuilder import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
