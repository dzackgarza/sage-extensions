r"""``O(q).group_generators()`` on the four-element form ``A_{U ⊕ U(2)}`` generates ``O(q)``.

The reported defect (sage-extensions#302) was a time: 32.7 s for

    sage: L = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]])
    sage: O = L.discriminant_group().orthogonal_group()
    sage: O.group_generators()

on a discriminant group of four elements whose orthogonal group has order two.  The step that
paid it was the private engine group's construction
(``TorsionFormOrthogonalGroup._engine_group`` -> ``_engine_orthogonal_group``): the first call
that needs the order or the generators builds that group, and at the commit the defect was
reported on, it went through Sage's general finite-form orthogonal group.  Measured on that
commit, in that order, ``cardinality()`` cost 50.66 s and ``group_generators()`` 0.08 s
thereafter; measured on the tree this file ships with, ``cardinality()`` costs 0.58 s and
``group_generators()`` 0.05 s, because the engine group of an elementary two-primary part is
read from GAP Forms' full classical orthogonal group instead (``_engine_orthogonal_group``:
"An integer-valued elementary two-primary part with nonsingular polar form is a quadratic
space over GF(2); GAP Forms supplies the exact base change from its full classical orthogonal
group").

The generators themselves come from that same group: ``_computed_group_generators`` returns
``_engine_group().gens()`` raised to form automorphisms, so the family is the generators of the
group the library already computes for the form, with nothing cached in front of a slow step.

What is asserted is the property the time was hiding: the subgroup the returned family
generates has the order the call already returns.  Both numbers are computed here -- the
family's group by this group's own subgroup construction, the ambient order by
``cardinality()`` -- so the test types no count of its own.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _four_element_form():
    r"""``A_{U ⊕ U(2)}``: four elements, ``|O(q)| = 2``."""
    return (Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]])).discriminant_group()


def test_the_returned_generators_generate_the_orthogonal_group_of_the_form() -> None:
    r"""The generated subgroup's order equals the order ``cardinality()`` returns."""
    group = _four_element_form().orthogonal_group()
    family = tuple(group.group_generators())

    generated = group.subgroup(family)

    assert generated.cardinality() == group.cardinality()
