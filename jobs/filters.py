import django_filters
from django.db.models import Count
from .models import Job


class JobFilter(django_filters.FilterSet):
    min_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="gte")
    max_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="lte")

    min_applicants = django_filters.NumberFilter(method="filter_min_applicants")
    max_applicants = django_filters.NumberFilter(method="filter_max_applicants")

    class Meta:
        model = Job
        fields = ["is_open", "min_budget", "max_budget"]

    def filter_min_applicants(self, queryset, name, value):
        return queryset.annotate(applicant_count=Count("applications")).filter(
            applicant_count__gte=value
        )

    def filter_max_applicants(self, queryset, name, value):
        return queryset.annotate(applicant_count=Count("applications")).filter(
            applicant_count__lte=value
        )
