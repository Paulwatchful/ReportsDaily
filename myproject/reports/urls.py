from django.urls import path
from . import views

urlpatterns = [
    path('emails/', views.email_list, name='email_list'),
    path('', views.index, name='index'),  # Handle the root /reports/ URL
]
