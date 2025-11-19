from os import environ


is_debug = len(environ.get('DEBUG') or '') > 0
