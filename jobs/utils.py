from django.core.cache import cache

def clear_public_jobs_cache():
    cache.clear()
