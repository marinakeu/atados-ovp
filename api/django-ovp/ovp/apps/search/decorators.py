from functools import wraps
from django.core.cache import cache


def cached(func):
    """
    Used to decorate .get_queryset method on search viewsets.

    Caches a queryset.
    """
    @wraps(func)
    def _impl(self, *args, **kwargs):
        key = self.get_cache_key()
        ttl = 120

        result = None
        if key:
            result = cache.get(key)

        if result:
            return result

        result = func(self, *args, **kwargs)
        cache.set(key, result, ttl)

        return result
    return _impl
