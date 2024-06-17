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
    email = forms.CharField(max_length=255, widget=forms.HiddenInput())
    attachment_id = forms.CharField(max_length=255, widget=forms.HiddenInput())  # Add this field

    class Meta:
        model = Report
        fields = ['title', 'content', 'project', 'email', 'attachment_id']  # Include attachment_id

class ForwardEmailForm(forms.Form):
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    recipients = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated emails'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].label = "Email Subject"
        self.fields['body'].label = "Email Body"
        self.fields['recipients'].label = "Recipients"
