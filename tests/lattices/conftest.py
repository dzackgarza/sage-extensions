r"""Session abbreviations for the lattice tests.

A test may name the card row it asserts, and may not open the digest itself:
``sage_extensions.testing.test_lint`` rejects a file read inside a test file
(``TL01`` for ``json`` and ``pathlib``, ``TL13`` for ``__file__`` and ``Path``).
The digest is generated, not edited, by
``tests/cards/refresh_lattice_database_enriques.py`` from
``dzackgarza/lattice-database`` at the commit its ``_provenance.ref`` names, so
reading it in one place here keeps every expected number the database's.

This module binds one name, ``card``, as a builtin, which is the mechanism the
lint documents: a directory's ``conftest.py`` binds the session abbreviations its
tests use, and the lint reads the allowed names after the conftests have run.
"""

from __future__ import annotations

import builtins
import json
from pathlib import Path

DIGEST = Path(__file__).resolve().parents[1] / "cards" / "lattice-database-enriques.json"


def card(section: str, tag: str) -> dict:
    r"""Return one card's rows from the digest.

    ``section`` is the digest's key for the row group (``arithmetic_groups``,
    ``polarization_counts``, ``plane_orbits``, ``discriminant_forms``) and
    ``tag`` the card's slug, so a test asks by tag and never by position:

        card("discriminant_forms", "6JRR")["orthogonal_group_order"]
    """
    return json.loads(DIGEST.read_text(encoding="utf-8"))[section][tag]


builtins.card = card
