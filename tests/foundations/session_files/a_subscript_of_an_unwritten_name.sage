r"""A session file whose subscript names something the file binds nowhere.

``t`` appears in no binding statement of this file, and the file star-imports
the session, so the parse cannot establish that ``t`` is new.  The name is
therefore Python's to report when the file runs:
``tests/foundations/test_a_session_file_binds_only_what_it_writes.sage`` loads
it and asks for that report.
"""

from sage_extensions.all import *  # noqa: F401,F403

declared = QQ[t]
