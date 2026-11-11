r"""Session abbreviations for the ring tests.

A Python ``fractions.Fraction`` is the stored form a lattice-database card
holds for a rational Gram entry, so a ring test needs the type in scope to
state the owned ``QQ`` element constructor's behaviour (#347).  The test lint
rejects an import of ``fractions`` inside a test file (``TL01``: take every
name from the session), so this module binds the type as a builtin, which is
the mechanism the lint documents: a directory's ``conftest.py`` binds the
session abbreviations its tests use, and the lint reads the allowed names
after the conftests have run.
"""

from __future__ import annotations

import builtins
from fractions import Fraction

builtins.Fraction = Fraction
