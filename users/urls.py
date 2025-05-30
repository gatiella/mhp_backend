from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import ResetPasswordRedirectView, VerifyEmailView

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    #path('reset-password/<uuid:token>/', views.ResetPasswordView.as_view(), name='reset-password'),
    #path('reset-redirect/<uuid:token>/', ResetPasswordRedirectView.as_view(), name='reset-redirect'),  
    path('web-reset/<uuid:token>/', views.WebResetPasswordFormView.as_view(), name='web-reset'),
]