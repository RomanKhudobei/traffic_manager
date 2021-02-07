from functools import wraps

from django.utils import translation


def translate_to(language_code):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            translation.activate(language_code)
            result = func(*args, **kwargs)
            translation.deactivate()

            return result
        return wrapper

    return decorator
