r"""A session file whose subscript names a generator the file binds nowhere.

``t`` appears in no binding statement of this file and the session publishes no
``t``, so ``QQ[t]`` is the polynomial ring written as it is written: the research
dialect declares ``t`` its generator.
``tests/foundations/test_a_session_file_binds_only_what_it_writes.sage`` loads
this file and asks the loaded scope for the ring and for the generator.
"""

from sage_extensions.all import *  # noqa: F401,F403

declared = QQ[t]
