from dataclasses import dataclass
from epstein_files.documents.config.doc_cfg import DocCfg


@dataclass(kw_only=True)
class PicCfg(DocCfg):
    """Configure a picture to be displayed in the timeline."""
    filename: str
    show_image: bool = True
