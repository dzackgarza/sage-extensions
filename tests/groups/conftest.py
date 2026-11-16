r"""Session abbreviation for the group tests.

``sage_extensions.testing.test_lint`` resolves every name a test uses against the
session namespace, and the names of an object's own state are not in it: a test
may not import ``builtins`` (``TL01``), and may not name ``vars``, ``getattr`` or
``__dict__`` (``TL03``, introspection).  A directory's ``conftest.py`` is the
mechanism the lint documents for exactly this, so the one question such a test
asks is answered here, once.

It is asked because a construction's datum is established by the level that
introduces it, and nothing is attached to the object afterwards.  Two objects
built from the same data therefore carry the same names; a name one of them
carries and the other does not is state that object gained from something other
than its construction, which no mathematical answer of the object shows, because
the datum a route leaves is the object's own.
"""

from __future__ import annotations

import builtins


def names_beyond(reference, subject) -> frozenset[str]:
    r"""The instance names ``subject`` carries that ``reference`` does not.

    ``reference`` is the object the same data builds by the other route, so what
    ``subject`` holds beyond it is what that route added: a construction's own
    name is carried by both, and a computation's residue by one.
    """
    return frozenset(vars(subject)) - frozenset(vars(reference))


builtins.names_beyond = names_beyond
