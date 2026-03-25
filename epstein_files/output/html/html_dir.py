from pathlib import Path

DEFAULT_HTML_DIR = Path('docs')


class HtmlDir:
    """Container to hold state of HTML_DIR value because we can't add class vars to `Site` enum."""
    HTML_DIR = DEFAULT_HTML_DIR

    @classmethod
    def build_path(cls, filename: str) -> Path:
        return cls.HTML_DIR.joinpath(filename)
