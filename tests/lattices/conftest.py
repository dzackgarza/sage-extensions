r"""Session abbreviations and instruments for the lattice tests.

A test may name the card row it asserts, and may not open the digest itself:
``sage_extensions.testing.test_lint`` rejects a file read inside a test file
(``TL01`` for ``json`` and ``pathlib``, ``TL13`` for ``__file__`` and ``Path``).
The digest is generated, not edited, by
``tests/cards/refresh_lattice_database_enriques.py`` from
``dzackgarza/lattice-database`` at the commit its ``_provenance.ref`` names, so
reading it in one place here keeps every expected number the database's.

This module binds the session's names as builtins, which is the mechanism the
lint documents: a directory's ``conftest.py`` binds the abbreviations its tests
use, and the lint reads the allowed names after the conftests have run.
``card`` is a row of the digest; ``spans_built_by`` and ``displays_rendered_by``
count what one action built and rendered; ``owned_ring_crossings`` counts the
constructions between the engine's data and the owned ring.  Each instrument
patches with ``pytest.MonkeyPatch.context()``, so a failing action leaves the
process as it found it.
"""

from __future__ import annotations

import builtins
import json
from pathlib import Path

import pytest

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


def spans_built_by(action):
    r"""Return ``action()`` and the number of spans it built.

    A span of finitely many vectors of a lattice is built by
    ``Lattices.ParentMethods.subobject_on``.  A test asks for the count through
    this name, which is private to the arrangement and not to the mathematics,
    so the patch lives here (``TL02``, ``TL13``).
    """
    from sage_extensions.all import Lattices, ZZ

    parent_methods = Lattices(ZZ).ParentMethods
    original = parent_methods.subobject_on
    built = []

    def counted(self, generating_set):
        built.append(1)
        return original(self, generating_set)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(parent_methods, "subobject_on", counted)
        value = action()
    return value, len(built)


builtins.spans_built_by = spans_built_by


def displays_rendered_by(lattice, action):
    r"""Return ``action()`` and the number of displays ``lattice``'s class rendered.

    A lattice's display is its ``_repr_``, which computes the signature from the
    Gram, so counting it is how a test observes that a construction rendered
    nothing.  The shadow is set on the lattice's own class: ``_repr_`` is where
    the display is, while ``ParentMethods.__repr__`` is the inherited
    ``object.__repr__``, and a replacement of that would count a call which is
    not the display.
    """
    owner = lattice.__class__
    display = owner._repr_
    rendered = []

    def counted(self):
        rendered.append(1)
        return display(self)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(owner, "_repr_", counted)
        value = action()
    return value, len(rendered)


builtins.displays_rendered_by = displays_rendered_by


def owned_ring_crossings(action):
    r"""Return ``action()`` and the number of owned-ring crossings it made.

    A crossing is one construction between the engine's data and the owned ring:
    ``ring_foundation._owned_engine_element`` raises an engine value into the
    owned ring, and it is what an arrangement that did a computation's own
    arithmetic in the owned ring multiplies by the size of that computation.
    A lattice test asks the number for one Eichler transvection, whose matrix
    has ``rank^2`` entries but whose crossings are one decision per generator.

    The name of that crossing is private, so a test may not write it (``TL01``,
    ``TL02``): the patch lives here, beside the card reader.  A test asserts on
    the number, which is a call count and never a time.
    """
    from sage_extensions.categories.rings import ring_foundation

    counted = []
    original = ring_foundation._owned_engine_element

    def crossing(*arguments, **keywords):
        counted.append(1)
        return original(*arguments, **keywords)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(ring_foundation, "_owned_engine_element", crossing)
        value = action()
    return value, len(counted)


builtins.owned_ring_crossings = owned_ring_crossings
