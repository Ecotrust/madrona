from django.db import connection
from django.template import Template, Context
from django.conf import settings

#
# Log all SQL statements direct to the console (when running in DEBUG)
# Intended for use with the django development server.
#

class SQLLogToConsoleMiddleware:
    """
    Add to settings_local like so to log sql commands:

    from madrona.common.default_settings import MIDDLEWARE_CLASSES

    MIDDLEWARE_CLASSES += (
        'madrona.common.middleware.SQLLogToConsoleMiddleware',
    )
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_response(self, request, response):
        if settings.DEBUG and connection.queries:
            time = sum([float(q['time']) for q in connection.queries])
            t = Template("{{count}} quer{{count|pluralize:\"y,ies\"}} in {{time}} seconds:\n\n{% for sql in sqllog %}[{{forloop.counter}}] {{sql.time}}s: {{sql.sql|safe}}{% if not forloop.last %}\n\n{% endif %}{% endfor %}")
            # print t.render(Context({'sqllog':connection.queries,'count':len(connection.queries),'time':time}))
        return response

class IgnoreCsrfMiddleware(object):
    """
    http://djangosnippets.org/snippets/2069/
    CSRF protection requires updating all forms
    Meanwhile the crsf middleware is required for admin to work.
    This middleware class will just ignore csrf, allowing the current views and admin to work
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        request.csrf_processing_done = True
