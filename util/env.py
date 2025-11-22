from os import environ


is_build = len(environ.get('BUILD_HTML') or '') > 0
deep_debug = len(environ.get('DEEP_DEBUG') or '') > 0
is_debug = deep_debug or len(environ.get('DEBUG') or '') > 0
