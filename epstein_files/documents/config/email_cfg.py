from dataclasses import asdict, dataclass, field, fields
from typing import ClassVar

from epstein_files.documents.config.doc_cfg import SHORT_TRUNCATE_TO
from epstein_files.documents.config.communication_cfg import CommunicationCfg, Platform
from epstein_files.util.helpers.rich_helpers import CharRangeAuto


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
    platform: Platform = Platform.EMAIL  # Different default
    subject: str | None = None

    PREFIX_NOTE_WITH_CATEGORY: ClassVar[bool] = False

    def __post_init__(self):
        super().__post_init__()

        if self.show_full_panel:
            self._debug_log(f"show_full_panel=True, overriding because unecessary")  # TODO: this sucks
            self.show_full_panel = False

        if self.fwded_text_after:
            self.is_valid_for_name_scan = False

    @property
    def char_range(self) -> CharRangeAuto | None:
        """`truncate_to` as `(0, truncate_to)` tuple if truncate_to is an `int`."""
        if super().char_range:
            return super().char_range
        elif self.is_fwded_article or self.fwded_text_after:
            return (0, SHORT_TRUNCATE_TO)

    @property
    def truthy_props(self) -> dict[str, bool | str | None]:
        props = super().truthy_props

        if props.get('platform') == Platform.EMAIL:
            del props['platform']

        return props

    # This is necessary because for some dumb reason @dataclass(repr=False) doesn't cut it
    def __repr__(self) -> str:
        return super().__repr__()
