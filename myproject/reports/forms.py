from django import forms
from .models import Project, EmailTemplate, Recipient, Report

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['project', 'subject', 'body']

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['project', 'email']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'content', 'project']
