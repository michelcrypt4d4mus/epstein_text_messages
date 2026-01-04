# If this file is imported the pickled EpsteinFiles data will be used
from os import environ
environ.setdefault('PICKLED', 'true')

from dotenv import load_dotenv
load_dotenv()

from epstein_files.epstein_files import EpsteinFiles


epstein_files = EpsteinFiles.get_files()
