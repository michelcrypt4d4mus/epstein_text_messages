from pathlib import Path

DEFAULT_HTML_DIR = Path('docs')
IMAGES_DIR = Path('doc_images')


class HtmlDir:
    """Container to hold state of HTML_DIR value because we can't add class vars to `Site` enum."""
    HTML_DIR = DEFAULT_HTML_DIR

    @classmethod
    def build_path(cls, filename: str) -> Path:
        return cls.HTML_DIR.joinpath(filename)

    @classmethod
    def image_url(cls, filename: str) -> str:
        return str(IMAGES_DIR.joinpath(filename))

    @classmethod
    def local_pic_path(cls, filename: str) -> Path:
        return DEFAULT_HTML_DIR.joinpath(IMAGES_DIR, filename)
