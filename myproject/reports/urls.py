from django.urls import path
from . import views

urlpatterns = [
    path('emails/', views.email_list, name='email_list'),
    path('emails/download/<str:message_id>/<str:attachment_id>/', views.download_attachment_view, name='download_attachment'),
    path('emails/view/<str:message_id>/<str:attachment_id>/', views.view_pdf, name='view_pdf'),
    path('serve_pdf/<str:filename>/', views.serve_pdf, name='serve_pdf'),
    path('', views.index, name='index'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.project_create, name='project_create'),
    path('projects/edit/<int:id>/', views.project_edit, name='project_edit'),
    path('projects/delete/<int:id>/', views.project_delete, name='project_delete'),
    path('email-templates/add/', views.email_template_create, name='email_template_create'),
    path('recipients/add/', views.recipient_create, name='recipient_create'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/add/', views.report_create, name='report_create'),
    path('reports/forward/<int:report_id>/<int:project_id>/', views.forward_report, name='forward_report'),
]
