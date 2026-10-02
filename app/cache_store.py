"""Generic TTL-cache decorator, shared across all callers regardless of who's asking."""
from cachetools import TTLCache, cached as cachetools_cached
from cachetools.keys import hashkey


def cached(ttl=60, maxsize=128, ignore_first_arg=False):
    """Caches a function's return value for `ttl` seconds, keyed on its arguments.

    Set `ignore_first_arg=True` for functions whose first argument (e.g. an auth
    token) shouldn't affect cache identity, so callers share one cache entry.
    """
    def make_key(*args, **kwargs):
        return hashkey(*(args[1:] if ignore_first_arg else args), **kwargs)

    def decorator(func):
        return cachetools_cached(cache=TTLCache(maxsize=maxsize, ttl=ttl), key=make_key)(func)

    return decorator
