from os import environ


deep_debug = len(environ.get('DEEP_DEBUG') or '') > 0
is_debug = deep_debug or len(environ.get('DEBUG') or '') > 0

include_redacted_emails = len(environ.get('EMAILS') or '') > 0
