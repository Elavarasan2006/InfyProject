# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # frontend pages (rendered by Django)
    path('', views.index, name='index'),                    # /
    path('home/', views.home, name='home'),                 # /home/
    path('profile-page/', views.profile_page, name='profile_page'),
    path('predict-page/', views.predict_page, name='predict_page'),
    path('history-page/', views.history_page, name='history_page'),
    path('forgot-password-page/', views.forgot_password_page, name='forgot_password_page'),

    # API endpoints
    path('profile-save/', views.ProfileSaveView.as_view(), name='profile_save'),
    path('profile-get/<str:email>/', views.ProfileGetView.as_view(), name='profile_get'),

    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('history/', views.history_page, name='history'),

   
    path('profile/', views.profile_redirect, name='profile_redirect'),
    path('predict/', views.predict_page, name='predict_redirect'),



    # Forgot-password API
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
]





