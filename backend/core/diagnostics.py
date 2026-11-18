from .models import PerformanceMetric, Diagnostic


def analyze_visit(visit):

    metrics = PerformanceMetric.objects.filter(visit=visit)

    thresholds = {
        "DNS": 200,
        "TCP": 200,
        "TLS": 300,
        "TTFB": 800,
        "Page Load": 3000,
    }

    recommendations = {
        "DNS": "Check DNS configuration and DNS resolution delays.",
        "TCP": "Check network connectivity and connection establishment.",
        "TLS": "Check TLS handshake and secure connection delays.",
        "TTFB": "Check server response time and network latency.",
        "Page Load": "Optimize page resources such as images, CSS and JavaScript.",
    }

    results = []

    for metric in metrics:

        name = metric.metric_name
        value = metric.value

        if name not in thresholds or value is None:
            continue

        if value > thresholds[name]:
            status = "Warning"
            message = (
                f"{name} is taking longer than the "
                f"expected threshold ({value} ms)."
            )
        else:
            status = "Good"
            message = f"{name} is within the configured threshold ({value} ms)."

        diagnostic = Diagnostic.objects.create(
            visit=visit,
            metric_name=name,
            status=status,
            message=message,
            recommendation=recommendations[name]
        )

        results.append(diagnostic)

    return results