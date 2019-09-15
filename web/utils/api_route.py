from functools import wraps
from typing import Callable

import flask
from flask import make_response, render_template, url_for


def is_api_request() -> bool:
    return flask.request.path.startswith('/api')


def api_endpoint(endpoint: str) -> str:
    return endpoint + '_api'


class ApiRouteView:
    def __init__(self, handler: Callable[..., flask.Response], endpoint: str):
        self.endpoint = endpoint
        self.handler = handler

    def __call__(self, *args, **kwargs) -> flask.Response:
        return self.handler(*args, **kwargs)


def add_api_route(app, path: str, *args, **kwargs) -> Callable[..., ApiRouteView]:
    def decorator(f: Callable[..., flask.Response]) -> ApiRouteView:
        endpoint = kwargs.pop('endpoint', f.__name__)
        view_func = ApiRouteView(f, endpoint)
        app.route(path, *args, **kwargs, endpoint=endpoint)(view_func)
        app.route('/api' + path, *args, **kwargs, endpoint=api_endpoint(endpoint))(view_func)
        return wraps(f)(view_func)

    return decorator


def format_response(template_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> flask.Response:
            response: flask.Response = func(*args, **kwargs)
            if is_api_request():
                return response
            data = response.json
            return make_response(render_template(template_name, **data))

        return wrapper

    return decorator


def build_url(handler: ApiRouteView, **params) -> str:
    prefix = ''
    endpoint = handler.endpoint
    if is_api_request():
        endpoint = api_endpoint(endpoint)
        prefix = f"{flask.request.scheme}://{flask.request.host}"
    return prefix + url_for(endpoint, **params)
