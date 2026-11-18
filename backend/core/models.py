from django.db import models

# Create your models here.

from django.db import models


class Website(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Visit(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    page_url = models.URLField()
    captured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit to {self.website.name}"


class PerformanceMetric(models.Model):
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    metric_name = models.CharField(max_length=100)
    value = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=20, default='ms')
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.metric_name}: {self.value} {self.unit}"

class Diagnostic(models.Model):
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='diagnostics'
    )
    metric_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    message = models.TextField()
    recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.metric_name} - {self.status}"