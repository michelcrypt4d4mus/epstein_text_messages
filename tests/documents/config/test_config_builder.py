from epstein_files.documents.document import Document
from epstein_files.documents.config.config_builder import *


def test_grand_jury(get_doj_file):
    doc: Document = get_doj_file('EFTA00008863').reload()
    assert doc._config.complete_description == 'grand jury proceedings in U.S. v. Ghislaine Maxwell'


def test_inventory(doj_file_id):
    assert inventory(doj_file_id, 'file cabinet').complete_description == 'inventory of the contents of file cabinet'
    _inventory = inventory(doj_file_id, 'file cabinet', 'Epstein will')
    assert _inventory.complete_description == 'inventory of the contents of file cabinet, includes Epstein will'
