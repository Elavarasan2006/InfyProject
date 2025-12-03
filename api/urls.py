from django.urls import path, include
from . import views
from .chatbot import chat_handler
from . import chatbot

urlpatterns = [
    # -------------------------
    # FRONTEND PAGES
    # -------------------------
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('profile-page/', views.profile_page, name='profile_page'),
    path('predict-page/', views.predict_page, name='predict_page'),
    path('history-page/', views.history_page, name='history_page'),
    # path('forgot-password-page/', views.forgot_password_page, name='forgot_password_page'),
    path('visualizations/', views.visualizations_page, name='visualizations'),
    path('api/visualization-data/<str:email>/', views.visualization_data, name='visualization_data'),

    # -------------------------
    # ML PREDICTION & HISTORY APIs
    # -------------------------
    path('api/predict/', views.predict_job_api, name='predict_job_api'),
    path('api/save-prediction/', views.save_prediction, name='save_prediction'),
    path('api/history-get/<str:email>/', views.history_get, name='history_get'),
    path('api/history-clear/<str:email>/', views.history_clear, name='history_clear'),
    
    # -------------------------
    # NEW ENDPOINTS FOR HISTORY SYSTEM
    # -------------------------
    path('api/current-user/', views.get_current_user, name='current_user'),
    path('api/setup-demo-data/', views.setup_demo_data, name='setup_demo_data'),
    
    # -------------------------
    # PREDICTION HISTORY API (NEW)
    # -------------------------
    path('api/prediction-history/', views.prediction_history_api, name='prediction_history_api'),
    path('api/clear-predictions/', views.clear_all_predictions, name='clear_all_predictions'),

    # -------------------------
    # PROFILE MANAGEMENT
    # -------------------------
    path('profile-save/', views.ProfileSaveView.as_view(), name='profile_save'),
    path('profile-get/<str:email>/', views.ProfileGetView.as_view(), name='profile_get'),
    path('profile/', views.profile_redirect, name='profile_redirect'),

    # -------------------------
    # AUTH
    # -------------------------
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('predict/', views.predict_job, name='predict_job'),
    path('chat/', chatbot.chat_handler, name='chat_handler'),

    # Predictor App
    path('predictor/', include('predictor.urls')),
    path('visualizations/', views.visualizations_page, name='visualizations'),
    path('api/visualization-data/<str:email>/', views.visualization_data, name='visualization_data'),

    # -------------------------
    # FORGOT PASSWORD
    # -------------------------
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
]









