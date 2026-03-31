"""
Constants used to build internal links within one html page.
"""
from enum import auto, StrEnum

AUTHORS_USING_SIGNATURES = 'Authors Seen Using Email Signatures'
SELECTIONS_FROM = 'Selections from '
HIS_EMAILS = 'His Emails'
HIS_TEXT_MESSAGES = 'His Text Messages'
FILES_THAT_ARE_NEITHER_EMAILS_NOR = 'Files That Are Neither Emails Nor Text Messages'
TO_FROM = 'to/from'


class PageSections(StrEnum):
    EMAILS = auto()
    EMAIL_SIGNATURES = auto()
    OTHER_FILES = auto()
    TEXT_MESSAGES = auto()


# Search terms that take you to the desired section via magic URL comment arg
SECTION_ANCHORS = {
    PageSections.EMAILS: SELECTIONS_FROM + HIS_EMAILS,
    PageSections.EMAIL_SIGNATURES: AUTHORS_USING_SIGNATURES,
    PageSections.TEXT_MESSAGES: SELECTIONS_FROM + HIS_TEXT_MESSAGES,
    PageSections.OTHER_FILES: FILES_THAT_ARE_NEITHER_EMAILS_NOR,
}
