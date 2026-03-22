from dataclasses import dataclass, field
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

from epstein_files.documents.emails.email_header import EmailHeader
from epstein_files.documents.email import Email
from epstein_files.util.logging import logger
from epstein_files.util.constant.strings import AUTHOR

HEADERS_TO_CHECK = [
    'Authentication-Results',
    'Content-Transfer-Encoding',
    'Content-Type',
    'DKIM-Signature',
    'DomainKey-Signature',
    'Received',
    'References',
    'X-Mailer',
]

DEFAULT_EML_HEADERS = HEADERS_TO_CHECK + ['Date', 'From', 'Subject', 'To', 'MIME-Version', 'Content-Length']
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

    def extract_header(self) -> EmailHeader:
        """Extract an `EmailHeader` from the OCR text."""
        bcc = self.eml['bcc'].split(';') if self.eml['bcc'] else None
        cc = self.eml['cc'].split(';') if self.eml['cc'] else None
        field_names = HEADER_FIELDS + (['bcc'] if bcc else []) + (['cc'] if cc else [])

        for header in self.eml.keys():
            if header not in DEFAULT_EML_HEADERS:
                self._warn(f"unexpected header {header}: '{self.eml[header]}'")

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
        body = self.eml.get_body(('plain', 'related', 'html')).get_content()
        return f"{self.header.rewrite_header()}\n{body}"
