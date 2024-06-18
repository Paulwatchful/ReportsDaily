from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EmailTemplate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='email_templates')
    subject = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return f"{self.project.name} - {self.subject}"

class Recipient(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='recipients')
    email = models.EmailField()

    def __str__(self):
        return f"{self.project.name} - {self.email}"

class Report(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)

    def __str__(self):
        return self.title
