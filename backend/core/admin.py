from django.contrib import admin
from .models import Website , Visit , PerformanceMetric ,Diagnostic

# Register your models here.
admin.site.register(Website)
admin.site.register(Visit)
admin.site.register(PerformanceMetric)
admin.site.register(Diagnostic)