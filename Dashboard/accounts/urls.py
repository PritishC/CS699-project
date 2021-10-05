from django.contrib.auth.views import logout_then_login
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Login
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', logout_then_login, name='logout'),
    # Signup
    path('signup/', views.Signup.as_view(), name='signup'),
    path('signup/done', views.SignupActivationConfirm.as_view(), name='signup_activation_confirm'),
    path('signup/complete/<token>', views.SignupActivationComplete.as_view(), name='signup_activation_complete'),
    # Password Reset
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    # Profile
    path('profile/', views.profile, name="profile")
]


