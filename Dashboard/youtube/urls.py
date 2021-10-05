from django.contrib.auth.views import logout_then_login
from django.urls import path
from . import views

app_name = 'youtube'

urlpatterns = [
    path('initial/', views.initial, name='initial'),
    path('daily/', views.daily, name='daily'),
    path('register/', views.register, name='register'),
    path('de_register/', views.de_register, name='de_register'),
    path('dummy_save/',views.save_keywords, name='save_keyword'),
    path('dummy_get/',views.get_keywords, name='get_keyword'),
]


