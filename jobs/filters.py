import django_filters
from .models import Job


class JobFilter(django_filters.FilterSet):
    min_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="gte")
    max_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="lte")

    class Meta:
        model = Job
        fields = ["is_open", "min_budget", "max_budget"]
