from dataclasses import dataclass
from typing import Literal

from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.util.helpers.file_helper import is_picture
from epstein_files.output.html.html_dir import HtmlDir

ImgExt = Literal['jpg', 'jpeg', 'gif', 'webp', 'png']


@dataclass(kw_only=True)
class PicCfg(DocCfg):
    """Configure a picture to be displayed in the timeline."""
    date: str
    file_type: ImgExt = 'png'
    show_image: bool = True

    def __post_init__(self):
        return super().__post_init__()

    @property
    def image_filename(self) -> str:
        return f"{self.id}.{self.file_type}"

    @property
    def image_url(self) -> str:
        import pdb;pdb.set_trace()
        return str(HtmlDir.image_url(self.image_filename))


PIC_CFGS = [
    EmailCfg(
        id='EFTA02647641',
        note='sent after MBS successfully purged his political rivals in Saudi Arabia',
        pic_cfg=PicCfg(
            id='EFTA02647641', # TODO: show image
            date='2016-09-01',
            date_uncertain='approximate',
            file_type='webp',
        ),
    ),
]
