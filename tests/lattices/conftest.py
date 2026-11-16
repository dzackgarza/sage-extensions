r"""Session abbreviations for the lattice tests.

A test may name the card row it asserts, and may not open the digest itself:
``sage_extensions.testing.test_lint`` rejects a file read inside a test file
(``TL01`` for ``json`` and ``pathlib``, ``TL13`` for ``__file__`` and ``Path``).
The digest is generated, not edited, by
``tests/cards/refresh_lattice_database_enriques.py`` from
``dzackgarza/lattice-database`` at the commit its ``_provenance.ref`` names, so
reading it in one place here keeps every expected number the database's.

This module binds two names as builtins, which is the mechanism the lint
documents: a directory's ``conftest.py`` binds the abbreviations its tests use,
and the lint reads the allowed names after the conftests have run.  ``card`` is a
row of the digest; ``owned_ring_crossings`` counts the constructions between the
engine's data and the owned ring that one action makes, which a test asks for as
a call count and may not name itself.
"""

from __future__ import annotations

import builtins
import json
from contextlib import contextmanager
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


_ABSENT = object()


@contextmanager
def _patched(owner, name, replacement):
    r"""Shadow ``owner.name`` for the block, and restore it however the block ends.

    A call count is an instrument and never a mock: the replacement calls what it
    shadows.  The attribute is restored in ``finally``, so a failing action leaves
    the process as it found it, and an attribute the owner inherits is removed
    again rather than written onto the owner.
    """
    held = owner.__dict__.get(name, _ABSENT)
    setattr(owner, name, replacement)
    try:
        yield
    finally:
        if held is _ABSENT:
            if name in owner.__dict__:
                delattr(owner, name)
        else:
            setattr(owner, name, held)


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

    with _patched(parent_methods, "subobject_on", counted):
        value = action()
    return value, sum(built)


builtins.spans_built_by = spans_built_by


def displays_rendered_by(action):
    r"""Return ``action()`` and the number of lattice displays it rendered.

    A lattice's rendering computes its signature from its Gram, so counting it is
    how a test observes that a construction rendered nothing.  The patch lives
    here for the reason ``spans_built_by``'s does.
    """
    from sage_extensions.all import Lattices, ZZ

    parent_methods = Lattices(ZZ).ParentMethods
    original = parent_methods.__repr__
    rendered = []

    def counted(self):
        rendered.append(1)
        return original(self)

    with _patched(parent_methods, "__repr__", counted):
        value = action()
    return value, sum(rendered)


builtins.displays_rendered_by = displays_rendered_by


def cokernels_built_by(action, morphism):
    r"""Return ``action()`` and the number of cokernels it built of ``morphism``'s class.

    A module morphism's cokernel is built by its ``cokernel``, which retains the
    quotient it built; a decision about that cokernel which constructs no
    quotient therefore leaves this count at zero, and that is the contract a test
    of such a decision asserts.  The shadow is set on the arrow's own class, not
    on a method class: an element class is realized per construction, so a
    method class shadowed afterwards would not be the one the arrow resolves.
    """
    owner = type(morphism)
    entry = getattr(owner, "cokernel")
    built = []

    def counted(self, *arguments, **keywords):
        built.append(1)
        return entry.__get__(self, owner)(*arguments, **keywords)

    with _patched(owner, "cokernel", counted):
        value = action()
    return value, sum(built)


builtins.cokernels_built_by = cokernels_built_by


def owned_ring_crossings(action):
    r"""Return ``action()`` and the number of owned-ring crossings it made.

    A crossing is one construction between the engine's data and the owned ring:
    ``ring_foundation._owned_engine_element`` raises an engine value into the
    owned ring, and it is what an arrangement that did a computation's own
    arithmetic in the owned ring multiplies by the size of that computation.
    A lattice test asks the number for one Eichler transvection, whose matrix
    has ``rank^2`` entries but whose crossings are one decision per generator.

    The name of that crossing is private, so a test may not write it (``TL01``,
    ``TL02``): the patch lives here, beside the card reader, and it restores the
    function it shadows whatever the action does.  A test asserts on the number,
    which is a call count and never a time.
    """
    from sage_extensions.categories.rings import ring_foundation

    counted = []
    original = ring_foundation._owned_engine_element

    def crossing(*arguments, **keywords):
        counted.append(1)
        return original(*arguments, **keywords)

    ring_foundation._owned_engine_element = crossing
    try:
        value = action()
    finally:
        ring_foundation._owned_engine_element = original
    return value, sum(counted)


builtins.owned_ring_crossings = owned_ring_crossings
