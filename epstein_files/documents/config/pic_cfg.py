from dataclasses import dataclass
from typing import Literal

from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.output.html.html_dir import IMAGES_DIR, HtmlDir
from epstein_files.people.names import *
from epstein_files.util.helpers.file_helper import is_picture, is_valid_id

ImgExt = Literal['jpg', 'jpeg', 'gif', 'webp', 'png']

# Maybe some day these PDFs could be converted to images
POSSIBLE_IMAGE_CONVERSIONS = [
    'EFTA00315076',
]


@dataclass(kw_only=True)
class PicCfg(DocCfg):
    """Configure a picture to be displayed in the timeline."""
    date: str
    file_type: ImgExt = 'png'
    is_horizontal: bool = False

    def __post_init__(self):
        return super().__post_init__()

    @property
    def image_filename(self) -> str:
        return f"{self.id}.{self.file_type}"

    @property
    def image_url(self) -> str:
        if is_valid_id(self.id):
            return str(HtmlDir.image_url(self.image_filename))
        else:
            return str(IMAGES_DIR.joinpath(self.image_filename))

    @property
    def has_valid_id(self) -> bool:
        return True  # TODO: check file exists


PIC_CFGS = [
    EmailCfg(
        id='EFTA02647641',
        note='sent after MBS successfully purged his political rivals in Saudi Arabia',
        pic_cfg=PicCfg(
            id='EFTA02647641',
            date='2016-09-01',
            date_uncertain='approximate',
            file_type='webp',
        ),
    ),
    PicCfg(
        id='sawed_open_safe',
        author=FBI,
        date='2019-07-06',
        is_displayed_as_img = True,
        is_interesting=15,
        note="photo of Jeffrey Epstein's sawed-open safe with hard drives and binders that were not seized due to not being specified in the warrant piled on top",
    ),
    PicCfg(
        id='trump_birthday_note',
        author=DONALD_TRUMP,
        date='2003-01-20',
        is_displayed_as_img = True,
        is_interesting=20,
        note='birthday letter to Jeffrey Epstein',
    ),
]
