from django.db import models


class ContactSubmission(models.Model):
    SERVICE_CHOICES = [
        ('seo-audit', 'SEO Audit'),
        ('content-strategy', 'Content Strategy'),
        ('leadnexus', 'LeadNexus Implementation'),
        ('full-stack', 'Full Stack Development'),
        ('ai-integration', 'AI & Automation'),
    ]

    name        = models.CharField(max_length=50)
    email       = models.EmailField()
    phone       = models.CharField(max_length=20, blank=True, default='')
    service     = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    message     = models.TextField(max_length=1000)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read     = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'

    def __str__(self):
        return f"{self.name} — {self.get_service_display()} ({self.submitted_at.strftime('%d %b %Y')})"
