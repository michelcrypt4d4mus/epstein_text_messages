from dataclasses import dataclass, field
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

from epstein_files.documents.emails.email_header import EmailHeader
from epstein_files.documents.email import Email
from epstein_files.util.logging import logger
from epstein_files.util.constant.strings import AUTHOR
from epstein_files.util.helpers.string_helper import collapse_newlines

HEADER_FIELDS = [AUTHOR, 'sent_at', 'to', 'subject']


@dataclass
class DropsiteEmail(Email):
    _eml: EmailMessage = field(init=False)

    @property
    def eml(self) -> EmailMessage:
        if '_eml' not in dir(self):
            with open(self.file_path, 'rb') as fp:
                self._eml = BytesParser(policy=policy.default).parse(fp)

        return self._eml

    def raw_text(self) -> str:
        """Reload the raw data from the underlying file and return it."""
        # TODO: this isn't the raw text... should be the following line
        # return self.eml.as_string()
        body = self.eml.get_body(('plain', 'related', 'html')).get_content()
        return self.with_header(f"\n{body}")

    def _extract_header(self) -> EmailHeader:
        """Extract an `EmailHeader` from the OCR text."""
        bcc = self.eml['bcc'].split(';') if self.eml['bcc'] else None
        cc = self.eml['cc'].split(';') if self.eml['cc'] else None
        field_names = HEADER_FIELDS + (['bcc'] if bcc else []) + (['cc'] if cc else [])
        self.warn(f"header keys: {self.eml.keys()}")

        return EmailHeader(
            author=self.eml['from'],
            bcc=bcc,
            cc=cc,
            field_names=field_names,
            sent_at=self.eml['date'],
            subject=self.eml['subject'],
            to=self.eml['to'].split(';') if self.eml['to'] else None,
        )

    def _load_file(self) -> str:
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        text = self.raw_text()
        # TODO: this should be in _repair()
        # text = self.repair_ocr_text(OCR_REPAIRS, text.strip())
        lines = [line.strip() if self.STRIP_WHITESPACE else line for line in text.split('\n')]
        logger.debug(f"File ID: {self.file_id}")

        for i, line in enumerate(lines):
            logger.debug(f'[{i}] "{line}"')

        return collapse_newlines('\n'.join(lines))

    def _repair(self) -> None:
        """Can optionally be overloaded in subclasses to further improve self.text."""
        pass
