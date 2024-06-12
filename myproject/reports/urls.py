from django.urls import path
from . import views

urlpatterns = [
    path('emails/', views.email_list, name='email_list'),
    path('emails/download/<str:message_id>/<str:attachment_id>/', views.download_attachment_view, name='download_attachment'),
    path('emails/view/<str:message_id>/<str:attachment_id>/', views.view_pdf, name='view_pdf'),
    path('serve_pdf/<str:filename>/', views.serve_pdf, name='serve_pdf'),  # Add this line
    path('', views.index, name='index'),  # Handle the root /reports/ URL
]
