from django.urls import include, path, re_path
from . import views
from .subviews import youtube_views

app_name = 'dashboard'

urlpatterns = [
    path('home/', views.index, name='index'),
    path('youtube/home/', youtube_views.home, name='youtube_home'),
    path('youtube/daily/', youtube_views.daily, name='youtube_daily'),
]
