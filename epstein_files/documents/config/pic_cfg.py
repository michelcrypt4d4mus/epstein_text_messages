from dataclasses import dataclass

from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.output.html.html_dir import HtmlDir

IMG_EXTENSIONS = [
    'gif',
    'jpeg',
    'jpg',
    'png',
    'webp',
]


@dataclass(kw_only=True)
class PicCfg(DocCfg):
    """Configure a picture to be displayed in the timeline."""
    date: str
    show_image: bool = True

    @property
    def has_valid_id(self) -> bool:
        return any(self.id.endswith(ext) for ext in IMG_EXTENSIONS)

    @property
    def image_url(self) -> str:
        return str(HtmlDir.image_url(f"{self.id}.png"))

PIC_CFGS = [
    PicCfg(id='Epstein_and_MBS.webp', date='2016-09-01', date_uncertain='approximate'),
]
