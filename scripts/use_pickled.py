# If this file is imported the pickled EpsteinFiles data will be used
from os import environ
environ.setdefault('PICKLED', 'true')

from epstein_files.epstein_files import EpsteinFiles


epstein_files = EpsteinFiles.get_files()
