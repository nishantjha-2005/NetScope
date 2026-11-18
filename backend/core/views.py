from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes    
)
from rest_framework.response import Response
from rest_framework import status
from .models import Visit , Diagnostic
from .diagnostics import analyze_visit

from django.db.models import Count , Avg
from django.shortcuts import render

from .models import Website , Visit , PerformanceMetric

from .serializers import(
    WebsiteSerializer,
    VisitSerializer,
    PerformanceMetricSerializer
)

# Create your views here.
def dashboard(request):

    total_websites = Website.objects.count()

    total_visits = Visit.objects.count()

    websites = Website.objects.all().order_by('-created_at')

    website_data = []

    for website in websites:
        latest_visit = website.visits.order_by('-captured_at').first()

        page_load = None

        if latest_visit:
            page_load = latest_visit.metrics.filter(
                metric_name = "Page Load"
            ).first()
        if not latest_visit:
            website_status = "Not visited"

        elif not page_load or page_load.value is None:
            website_status = "Data unavailable"

        elif page_load.value > 3000:
            website_status = "Slow"

        else:
            website_status = "Normal"

        website_data.append({
            "name": website.name,
            "page_load": page_load.value if page_load else None,
            "status": website_status,
        })

    page_load_average = PerformanceMetric.objects.filter(
        metric_name = "Page Load"
    ).aggregate(Avg("value"))["value__avg"]

    average_load_time = (
        round(page_load_average / 1000 , 2)
        if page_load_average is not None
        else 0
    )

    issues_detected = Diagnostic.objects.filter(
        status="Warning"
    ).count()

    recent_diagnostics = Diagnostic.objects.select_related(
        "visit"
    ).order_by("-created_at")[:10]

    # Get the latest 10 website visits
    recent_visits = Visit.objects.select_related(
        "website"
    ).prefetch_related(
        "diagnostics",
        "metrics"
    ).order_by("-captured_at")[:10]

    recent_metrics = PerformanceMetric.objects.filter(
        metric_name="Page Load"
    ).select_related("visit").order_by("-recorded_at")[:10]

    chart_labels = []
    chart_values = []

    for metric in reversed(recent_metrics):
        chart_labels.append(
            metric.recorded_at.strftime("%d %b %H:%M")
        )
        chart_values.append(round(metric.value / 1000, 2))

    context = {
        'total_websites': total_websites,
        'total_visits': total_visits,
        'average_load_time': average_load_time,
        'issues_detected': issues_detected,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'recent_diagnostics': recent_diagnostics,
        'websites' : website_data,
        'recent_visits': recent_visits,
    }

    print("WEBSITE DATA:", website_data)
    print("WEBSITE DATA TYPE:", type(website_data))

    return render(request , 'core/dashboard.html', context)


def performance_details(request, visit_id):

    try:
        visit = Visit.objects.select_related(
            'website'
        ).get(id=visit_id)

    except Visit.DoesNotExist:
        return render(request, 'core/performance_details.html', {
            'error': 'Visit not found.'
        })

    metrics = PerformanceMetric.objects.filter(
        visit=visit
    ).order_by('recorded_at')

    context = {
        'visit': visit,
        'metrics': metrics,
    }

    return render(
        request,
        'core/performance_details.html',
        context
    )


class WebsiteViewSet(viewsets.ModelViewSet):
    queryset = Website.objects.all().order_by('-created_at')
    serializer_class = WebsiteSerializer
    permission_classes = [AllowAny]
    authentication_classes= []


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all().order_by('-captured_at')
    serializer_class = VisitSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class PerformanceMetricViewSet(viewsets.ModelViewSet):
    queryset = PerformanceMetric.objects.all().order_by('-recorded_at')
    serializer_class = PerformanceMetricSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def perform_create(self, serializer):
        serializer.save()
        
        

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def run_diagnostics(request, visit_id):

    try:
        visit = Visit.objects.get(id=visit_id)
    except Visit.DoesNotExist:
        return Response(
            {"error": "Visit not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Avoid duplicating diagnostics when the same visit is analyzed again.
    Diagnostic.objects.filter(visit=visit).delete()

    results = analyze_visit(visit)

    data = [
        {
            "metric_name": item.metric_name,
            "status": item.status,
            "message": item.message,
            "recommendation": item.recommendation
        }
        for item in results
    ]

    return Response({
        "visit_id": visit.id,
        "total_diagnostics": len(data),
        "diagnostics": data
    })

