from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.people.entity import Entity


def test_configured_entities(epstein_files):
    txts = epstein_files.get_id('029744', required_type=MessengerLog)
    assert Entity.coerce_entity_names(txts.entities) == ["Jeffrey Epstein", "Miles Guo", "Steve Bannon"]
