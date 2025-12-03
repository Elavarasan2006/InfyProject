from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_job, name='predict_job_api'),
]


