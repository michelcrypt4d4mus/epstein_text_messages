import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Mapping

from rich.text import Text

from epstein_files.output.rich import join_texts, no_bold, prefix_with, styled_dict
from epstein_files.util.constant.strings import ALT_LINK_STYLE, ARCHIVE_LINK_COLOR, DOJ_DATASET_ID_REGEX
from epstein_files.util.constant.urls import *
from epstein_files.util.env import DOJ_PDFS_20260130_DIR, site_config
from epstein_files.util.helpers.file_helper import (coerce_file_stem, coerce_url_slug, extract_file_id, extract_efta_id,
     file_size, file_size_to_str, is_doj_file, is_house_oversight_file, is_local_extract_file)
from epstein_files.util.helpers.link_helper import link_text_obj, parenthesize
from epstein_files.util.logging import logger

FILE_PROPS = [
    'file_id',
    'file_size',
    'filename',
    'is_doj_file',
    'is_local_extract_file'
]


@dataclass
class FileInfo:
    """
    Attributes:
        local_path (Path): local path of the document's underlying .txt file
        doj_2026_dataset_id (int, optional): DataSet number for DOJ files
        file_id (str): file_id (str): ID string - 6 numbers with zero padding for HOUSE_OVERSIGHT, full EFTAXXXXX for DOJ files
    """
    local_path: Path
    doj_2026_dataset_id: int | None = None
    file_id: str = field(init=False)

    def __post_init__(self):
        self.file_id = extract_file_id(self.local_path)

        # Extract the DOJ dataset ID from the path
        if self.is_doj_file:
            if (data_set_match := DOJ_DATASET_ID_REGEX.search(str(self.local_path))):
                self.doj_2026_dataset_id = int(data_set_match.group(1))
                logger.info(f"Extracted data set ID {self.doj_2026_dataset_id} for {self.url_slug}")
            else:
                self.warn(f"Couldn't find a data set ID in path '{self.local_path}'! Cannot create valid links.")

    @property
    def as_dict(self) -> Mapping[str, str | Path]:
        props = {k: v for k, v in asdict(self).items() if v}
        props.update({k: getattr(self, k) for k in FILE_PROPS if getattr(self, k)})
        props.update(self.paths)
        props.update(self.urls)

        if self.url_slug != self.file_id:
            props['url_slug'] = self.url_slug

        return props

    @property
    def efta_id(self) -> int:
        if self.is_doj_file:
            return extract_efta_id(self.file_id)
        else:
            raise ValueError(f"{self.file_id} is not an EFTA prefix file!")

    @property
    def external_url(self) -> str:
        """The primary external URL to use when linking to this document's source."""
        if self.is_doj_file and self.doj_2026_dataset_id:
            return doj_2026_file_url(self.doj_2026_dataset_id, self.url_slug)
        else:
            return self.url_for_id(self.url_slug)

    @property
    def file_size(self) -> int:
        try:
            return file_size(self.local_path)
        except FileNotFoundError as e:
            self.warn(str(e))
            return -1

    @property
    def file_size_str(self) -> str:
        return file_size_to_str(self.file_size)

    @property
    def file_stem(self) -> str:
        return coerce_file_stem(self.file_id)

    @property
    def filename(self) -> str:
        return self.local_path.name

    @property
    def is_doj_file(self) -> bool:
        return is_doj_file(self.file_stem)

    @property
    def is_house_oversight_file(self) -> bool:
        return is_house_oversight_file(self.file_stem)

    @property
    def is_local_extract_file(self) -> bool:
        """True if extracted from other file (identifiable from filename e.g. HOUSE_OVERSIGHT_012345_1.txt)."""
        return is_local_extract_file(self.filename)

    @property
    def local_pdf_path(self) -> Path | None:
        """Path to the source PDF (only applies to DOJ files that were manually extracted)."""
        if self.is_doj_file and DOJ_PDFS_20260130_DIR:
            return next((p for p in DOJ_PDFS_20260130_DIR.glob('**/*.pdf') if p.stem == self.file_stem), None)

    @property
    def paths(self) -> Mapping[str, Path]:
        return {k: Path(v) for k, v in self._props_with_suffix('path').items() if v}

    @property
    def url_slug(self) -> str:
        return coerce_url_slug(self.file_id)

    @property
    def urls(self) -> Mapping[str, str]:
        urls = {k: str(v) for k, v in self._props_with_suffix('url').items() if v}
        urls = {k: (v if v.startswith('http') else f"https://{v}") for k, v in urls.items()}
        return urls

    def epsteinify_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str = '') -> Text:
        return self._build_link(epsteinify_doc_url, style, link_txt)

    def epstein_media_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str = '') -> Text:
        return self._build_link(epstein_media_doc_url, style, link_txt)

    def epstein_web_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str = '') -> Text:
        return self._build_link(epstein_web_doc_url, style, link_txt)

    def rollcall_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str = '') -> Text:
        return self._build_link(rollcall_doc_url, style, link_txt)

    def external_link_markup(self, style: str = '', id_only: bool = False) -> str:
        link_txt = self.file_id if id_only else self.file_stem
        return link_markup(self.external_url, link_txt, style=no_bold(style))

    def external_link_txt(self, style: str = '', id_only: bool = False) -> Text:
        return Text.from_markup(self.external_link_markup(style, id_only))

    def build_external_links(self, style: str = '', with_alt_links: bool = False, id_only: bool = False) -> Text:
        """Returns colored links to epstein.media and alternates in a Text object."""
        links = [self.external_link_txt(style, id_only)]

        if with_alt_links:
            if self.doj_2026_dataset_id:
                jmail_url = jmail_doj_2026_file_url(self.doj_2026_dataset_id, self.file_id)
                jmail_link = link_text_obj(jmail_url, JMAIL, style=f"{style} dim" if style else ARCHIVE_LINK_COLOR)
                links.append(jmail_link)
            else:
                links.append(self.epsteinify_link(style=ALT_LINK_STYLE, link_txt=EPSTEINIFY))
                links.append(self.epstein_web_link(style=ALT_LINK_STYLE, link_txt=EPSTEIN_WEB))

                # TODO: pass the Document so we can reinstate this?
                # if self._class_name == 'Email':
                #     links.append(self.rollcall_link(style=ALT_LINK_STYLE, link_txt=ROLLCALL))

        links = links if site_config.max_alt_links is None else links[0:site_config.max_alt_links + 1]
        links = [links[0]] + [parenthesize(link) for link in links[1:]]
        base_txt = Text('', style='white' if with_alt_links else ARCHIVE_LINK_COLOR)
        return base_txt.append(join_texts(links))

    def log(self, msg: str, level: int = logging.INFO):
        """Log a message with with this document's filename as a prefix."""
        logger.log(level, f"{self.file_stem} {msg}")

    def warn(self, msg: str) -> None:
        """Print a warning message prefixed by info about this `file_id`."""
        self.log(msg, level=logging.WARNING)

    def _build_link(self, fxn: Callable[[str], str], style: str = ARCHIVE_LINK_COLOR, link_txt: str = '') -> Text:
        return link_text_obj(fxn(self.url_slug), link_txt or self.file_stem, style)

    def _props_with_suffix(self, suffix: str) -> Mapping[str, str | Path]:
        return {k: getattr(self, k) for k in dir(self) if k.endswith(suffix)}

    def __rich__(self) -> Text:
        """Text obj with local paths and URLs."""
        txt_lines = styled_dict(self.as_dict, sep=': ')
        return prefix_with(txt_lines, ' ', pfx_style='grey', indent=2)

    def __str__(self) -> str:
        lines = [f"{k:>40}: {v}" for k, v in asdict(self).items() if k != 'file_id']
        return '\n'.join(lines)

    @classmethod
    def url_for_id(cls, url_slug: str) -> str:
        """Exists to codify the choice of which site to prefer. TODO: this doesn't work for DOJ files..."""
        return epstein_media_doc_url(url_slug)
