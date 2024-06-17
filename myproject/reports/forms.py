from django import forms
from .models import Project, EmailTemplate, Recipient, Report
from .email_utils import acquire_token, fetch_shared_mailbox_emails

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['project', 'subject', 'body']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
        }

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['project', 'email']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ReportForm(forms.ModelForm):
    email = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))
    project = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Report
        fields = ['title', 'content', 'project', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fetch emails for the email field choices
        token = acquire_token()
        shared_mailbox_email = "dailyreports@watchful.ltd"
        emails = fetch_shared_mailbox_emails(token, shared_mailbox_email)['value']
        email_choices = [(email['id'], email['subject']) for email in emails if email['subject'].startswith("Daily Progress Report")]
        self.fields['email'].choices = email_choices
