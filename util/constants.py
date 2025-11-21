import re


EPSTEIN_SIGNATURE = re.compile(r"""please note
The information contained in this communication is
confidential, may be attorney-client privileged, may
constitute inside information, and is intended only for
the use of the addressee. It is the property of
JEE
Unauthorized use, disclosure or copying of this
communication or any part thereof is strictly prohibited
and may be unlawful. If you have received this
communication in error, please notify us immediately by(\n\d\s*)?
return e-mail or by e-mail to jeevacation.*gmail.com, and
destroy this communication and all copies thereof,
including all attachments. copyright -all rights reserved""")

EPSTEIN_OLD_SIGNATURE = re.compile(r"""\*+
The information contained in this communication is
confidential, may be attorney-client privileged, may
constitute inside information, and is intended only for
the use of the addressee. It is the property of
Jeffrey Epstein
Unauthorized use, disclosure or copying of this
communication or any part thereof is strictly prohibited
and may be unlawful. If you have received this
communication in error, please notify us immediately by
return e-mail or by e-mail to.*
destroy this communication and all copies thereof,
including all attachments.( copyright -all rights reserved)?""")
