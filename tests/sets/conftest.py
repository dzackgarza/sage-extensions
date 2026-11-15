r"""Session abbreviations for the set tests.

``sage_extensions.testing.test_lint`` resolves every name a test uses against the
session namespace, and ``weakref`` and ``gc`` are not in it: a test may not import
them (``TL01``) and may not name them absent a binding (``TL13``).  A directory's
``conftest.py`` is the mechanism the lint documents for exactly this, so the two
names are bound here once rather than in each test that observes a lifetime.

They are here because a released object is only observable through a weak
reference: identity and value say nothing about whether something still holds it.
"""

from __future__ import annotations

import builtins
import gc
import weakref

builtins.weakref = weakref
builtins.gc = gc
