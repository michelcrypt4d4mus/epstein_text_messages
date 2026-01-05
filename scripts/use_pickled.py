# Helpful imports for scripts
from dotenv import load_dotenv
load_dotenv()

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.rich import console


epstein_files = EpsteinFiles.get_files()
