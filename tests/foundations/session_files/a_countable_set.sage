r"""A session file that builds the set of cardinality ``aleph0``.

The subscript's index is a name the session supplies, so the file builds the set
and binds nothing of its own; ``tests/foundations/test_a_session_file_binds_only_what_it_writes.sage``
loads it and asks the set for its cardinality.
"""

from sage_extensions.all import *  # noqa: F401,F403

countable = Sets.Δ[aleph0]
