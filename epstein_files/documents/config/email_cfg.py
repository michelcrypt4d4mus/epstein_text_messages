from dataclasses import asdict, dataclass, field, fields

from epstein_files.documents.config.doc_cfg import SHORT_TRUNCATE_TO, CharRange
from epstein_files.documents.config.communication_cfg import CommunicationCfg


@dataclass(kw_only=True)
class EmailCfg(CommunicationCfg):
    """
    Attributes:
        actual_text (str, optional): In dire cases of broken OCR we just configure the body of the email as a string.
        fwded_text_after (str, optional): If set, any text after this is a fwd of an article or similar.
        has_uninteresting_ccs (bool): If `True` this email's CC: recipients will be marked as 'uninteresting'.
        has_uninteresting_bccs (bool): If `True` this email's BCC: recipients will be marked as 'uninteresting'.
        subject (str, optional): Email subject line.
    """
    actual_text: str | None = None
    fwded_text_after: str | None = None
    has_uninteresting_ccs: bool = False
    has_uninteresting_bccs: bool = False
    subject: str | None = None

    def __post_init__(self):
        super().__post_init__()

        if self.fwded_text_after:
            self.is_valid_for_name_scan = False

    @property
    def truncate_at(self) -> int | CharRange | None:
        if super().truncate_at:
            return super().truncate_at
        elif self.is_fwded_article or self.fwded_text_after:
            return SHORT_TRUNCATE_TO

    # This is necessary because for some dumb reason @dataclass(repr=False) doesn't cut it
    def __repr__(self) -> str:
        return super().__repr__()
