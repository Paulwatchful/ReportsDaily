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
    email = forms.CharField(required=True)  # Ensure this is required to capture email

    class Meta:
        model = Report
        fields = ['project', 'email', 'content']

    def __init__(self, *args, **kwargs):
        email_choices = kwargs.pop('email_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['email'].choices = email_choices
