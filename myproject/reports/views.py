from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, FileResponse
from .email_utils import acquire_token, fetch_shared_mailbox_emails, download_attachment
from pdf2docx import Converter
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from .forms import ProjectForm, EmailTemplateForm, RecipientForm, ReportForm
from .models import Project, EmailTemplate, Recipient, Report
from django.core.mail import EmailMessage
from django.contrib import messages
import tempfile
import os
import logging
import urllib.parse
import requests
logger = logging.getLogger(__name__)

# Define a FileSystemStorage instance for temporary files
temp_storage = FileSystemStorage(location=tempfile.gettempdir())


def convert_pdf_to_word(pdf_content, docx_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        temp_pdf.write(pdf_content)
        temp_pdf_path = temp_pdf.name

    cv = Converter(temp_pdf_path)
    cv.convert(docx_path)
    cv.close()
    os.remove(temp_pdf_path)


def email_list(request):
    try:
        token = acquire_token()
        shared_mailbox_email = "dailyreports@watchful.ltd"
        emails = fetch_shared_mailbox_emails(token, shared_mailbox_email)

        # Log the total number of emails fetched
        logger.info(f"Total emails fetched: {len(emails['value'])}")

        # Filter emails to only include those with subjects starting with "Daily reports"
        filtered_emails = [email for email in emails['value'] if email['subject'].startswith("Daily Progress Report")]

        # Log the number of filtered emails
        logger.info(f"Filtered emails count: {len(filtered_emails)}")

        return render(request, 'reports/email_list.html', {'emails': filtered_emails})
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        return render(request, 'reports/error.html', {'error': str(e)})


def download_attachment_view(request, message_id, attachment_id):
    try:
        token = acquire_token()
        shared_mailbox_email = "dailyreports@watchful.ltd"
        attachment_content, attachment_name, content_type = download_attachment(token, shared_mailbox_email, message_id,
                                                                                attachment_id)

        convert_to_word = request.GET.get('convert', 'false').lower() == 'true'
        if convert_to_word:
            docx_name = os.path.splitext(attachment_name)[0] + '.docx'
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_docx:
                temp_docx_path = temp_docx.name
                convert_pdf_to_word(attachment_content, temp_docx_path)

                with open(temp_docx_path, 'rb') as f:
                    response = HttpResponse(f.read(),
                                            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename="{docx_name}"'
                os.remove(temp_docx_path)
        else:
            response = HttpResponse(attachment_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{attachment_name}"'

        return response

    except Exception as e:
        logger.error(f"Error downloading attachment: {e}")
        return render(request, 'reports/error.html', {'error': str(e)})


def view_pdf(request, message_id, attachment_id):
    try:
        token = acquire_token()
        shared_mailbox_email = "dailyreports@watchful.ltd"
        attachment_content, attachment_name, content_type = download_attachment(token, shared_mailbox_email, message_id,
                                                                                attachment_id)

        if content_type == 'application/pdf':
            # Create a temporary file with the attachment content
            temp_file = ContentFile(attachment_content)
            temp_file_name = temp_storage.save(attachment_name, temp_file)

            logger.info(f"Temporary file saved at: {temp_storage.path(temp_file_name)}")

            return FileResponse(open(temp_storage.path(temp_file_name), 'rb'), content_type='application/pdf')
        else:
            return HttpResponse("File is not a PDF", status=400)
    except Exception as e:
        logger.error(f"Error viewing PDF: {e}")
        return render(request, 'reports/error.html', {'error': str(e)})


def serve_pdf(request, filename):
    decoded_filename = urllib.parse.unquote(filename)
    file_path = temp_storage.path(decoded_filename)
    logger.info(f"Trying to serve file from: {file_path}")
    if temp_storage.exists(decoded_filename):
        with open(file_path, 'rb') as f:
            response = FileResponse(f, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        return response
    else:
        logger.error(f"File not found: {file_path}")
        raise Http404("PDF file not found.")


def index(request):
    return render(request, 'reports/index.html')


# New views for managing projects, email templates, and recipients
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'reports/project_list.html', {'projects': projects})


def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'reports/project_form.html', {'form': form})


def email_template_create(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = EmailTemplateForm()
    return render(request, 'reports/email_template_form.html', {'form': form})


def recipient_create(request):
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = RecipientForm()
    return render(request, 'reports/recipient_form.html', {'form': form})


def report_list(request):
    reports = Report.objects.all()
    return render(request, 'reports/report_list.html', {'reports': reports})


def report_create(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            project = report.project
            email_id = form.cleaned_data['email']

            try:
                token = acquire_token()
                shared_mailbox_email = "dailyreports@watchful.ltd"

                # Log the email ID being processed
                logger.info(f"Processing email ID: {email_id}")

                # Fetch the list of attachments for the email
                attachments = fetch_attachments(token, shared_mailbox_email, email_id)
                if not attachments:
                    raise ValueError("No attachments found for the given email ID")

                # Log attachment details
                for attachment in attachments:
                    logger.info(f"Attachment ID: {attachment['id']}, Name: {attachment['name']}")

                # Use the first attachment (or modify logic to select the correct one)
                attachment_id = attachments[0]['id']

                # Download the attachment
                attachment_content, attachment_name, content_type = download_attachment(token, shared_mailbox_email,
                                                                                        email_id, attachment_id)

                if attachment_content is None:
                    raise ValueError("Failed to download attachment content")

                # Send email
                email_template = project.email_templates.first()
                recipients = project.recipients.all()

                if email_template and recipients:
                    subject = email_template.subject
                    body = email_template.body + "\n\n" + report.content
                    to_emails = [recipient.email for recipient in recipients]

                    email = EmailMessage(
                        subject,
                        body,
                        'reports@watchfulapp.com',  # Use your email
                        to_emails,
                    )
                    email.attach(attachment_name, attachment_content, content_type)
                    email.send()

                    messages.success(request, 'Email sent successfully')
                else:
                    messages.error(request, 'No email template or recipients found for this project')

                report.save()
            except Exception as e:
                logger.error(f"Error forwarding report: {e}")
                messages.error(request, f"Error forwarding report: {str(e)}")
        else:
            messages.error(request, 'Form is not valid')
        return redirect('report_create')  # Redirect to the same page
    else:
        form = ReportForm()

    try:
        token = acquire_token()
        shared_mailbox_email = "dailyreports@watchful.ltd"
        emails = fetch_shared_mailbox_emails(token, shared_mailbox_email)

        # Filter emails to only include those with subjects starting with "Daily Progress Report"
        filtered_emails = [email for email in emails['value'] if email['subject'].startswith("Daily Progress Report")]

        email_choices = [(email['id'], email['subject']) for email in filtered_emails]
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        messages.error(request, f"Error fetching emails: {str(e)}")
        email_choices = []

    return render(request, 'reports/report_form.html', {'form': form, 'emails': email_choices})


def fetch_attachments(token, shared_mailbox_email, email_id):
    # Implement the logic to fetch the attachments for the given email_id
    # Placeholder implementation: Replace with actual logic
    url = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox_email}/messages/{email_id}/attachments"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        attachments = response.json().get('value', [])
        return attachments
    else:
        logger.error(f"Failed to fetch attachments: {response.json()}")
        return []


def get_attachment_id(token, shared_mailbox_email, email_id):
    # Implement the logic to fetch the correct attachment ID
    # This function should return the attachment ID for the given email_id
    # Placeholder implementation: Replace with actual logic
    attachment_id = "0"
    return attachment_id


def forward_report(request, report_id, project_id):
    try:
        report = get_object_or_404(Report, id=report_id)
        project = get_object_or_404(Project, id=project_id)
        email_template = project.email_templates.first()
        recipients = project.recipients.all()

        if email_template and recipients:
            subject = email_template.subject
            body = email_template.body + "\n\n" + report.content
            to_emails = [recipient.email for recipient in recipients]

            email = EmailMessage(
                subject,
                body,
                'reports@watchfulapp.com',  # replace with your email
                to_emails,
            )
            email.send()

            return HttpResponse('Email sent successfully')
        else:
            return HttpResponse('No email template or recipients found for this project', status=400)
    except Exception as e:
        logger.error(f"Error forwarding report: {e}")
        return render(request, 'reports/error.html', {'error': str(e)})
