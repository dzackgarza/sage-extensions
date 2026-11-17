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
count what one action built and rendered.  Each instrument that patches does so
with ``pytest.MonkeyPatch.context()``, so a failing action leaves the process as
it found it.
"""

from __future__ import annotations

import builtins
import gc
import json
import weakref
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

# A released object is observable only through a weak reference: identity and
# value say nothing about whether something still holds it.  ``weakref`` and
# ``gc`` are not session names, so they are bound here rather than imported by
# each test that observes a lifetime (``TL01``, ``TL13``).
builtins.weakref = weakref
builtins.gc = gc


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


def built_without_display(named, action):
    r"""Return ``action()`` with the display of ``named`` replaced by a refusal.

    ``named`` is the object a construction states in the name it builds for its
    result: the lattice a shell is cut out of, the discriminant module whose
    isotropic subgroups are enumerated, the isometry whose fixed locus is taken.
    Storing that name is the construction's; rendering it is the reader's, so a
    construction that renders it has computed a display for nobody.  The refusal
    raises where the display is asked for, which is how a test observes that the
    construction asked, and the value of a construction that did not is returned.

    The shadow is set on the named object's own class, so it is that object's
    ``__repr__`` the construction would call -- ``_repr_`` is where the display
    is written, and the inherited ``__repr__`` is what reaches it.

    Sage's own hash is primed first and asked for nothing afterwards:
    ``CategoryObject.__hash__`` is ``hash(repr(self))``, kept once computed, so
    the first hash of an owned object renders it as the runtime's datum and not
    the construction's.  Every display after that one is the construction's own.
    A construction that keys a dictionary on the named object therefore passes,
    and one that names the object in a string does not.
    """
    hash(named)
    owner = named.__class__

    def refuse(self):
        raise AssertionError(
            "the construction asked the object it names for its display"
        )

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(owner, "__repr__", refuse)
        value = action()
    return value


builtins.built_without_display = built_without_display


def presentations_built_by(construction, request):
    r"""Return ``(value, presentations the construction built, the request's)``.

    A finite form's automorphism is built from the engine's matrix and states
    its two presented module maps as computations, asked for on the first
    request that needs one: a construction that presents them has computed two
    morphisms nobody asked for, which is the cost a matrix question must not
    carry.  The presentation is ``_transported_map``, the transport of the
    matrix back through the form's normalization, so counting it counts the
    presentations.

    The request runs inside the same patch, so a test can assert that the
    instrument is live: a first request that presents nothing leaves the
    construction's own count unfalsified.
    """
    from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
        TorsionFormOrthogonalGroup,
    )

    presented = []
    original = TorsionFormOrthogonalGroup._transported_map

    def counted(self, engine_automorphism):
        presented.append(1)
        return original(self, engine_automorphism)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(TorsionFormOrthogonalGroup, "_transported_map", counted)
        value = construction()
        during_construction = len(presented)
        request(value)
        during_request = len(presented) - during_construction
    return value, during_construction, during_request


builtins.presentations_built_by = presentations_built_by
