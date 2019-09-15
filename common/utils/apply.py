from functools import wraps


def apply(func):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return func(f(*args, **kwargs))

        return wrapper

    return decorator
