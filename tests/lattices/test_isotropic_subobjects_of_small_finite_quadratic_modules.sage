r"""The isotropic-subobject orbit and setwise stabilizer on ordinary small lattices.

The public sequence is the one #296 delivers, on specimens small enough that the declared
gate runs them in seconds:

    A.isotropic_subobject(generators)     the submodule, refused when ``q`` does not vanish
    O(q).subobject_orbit_action(J)        the owning finite action on the orbit of J
    O(q).orbit(J) / orbit_points(J)       the orbit, as submodules or as element sets
    O(q).stabilizer(J)                    a subgroup of this O(q) whose generators fix J

and the check is the orbit-stabilizer theorem on the returned objects:
``|Stab(J)| * |orbit(J)| = |O(q)|``, with every returned generator fixing J elementwise.

Specimens: ``A_{U(2) + U(2)} = (Z/2)^4``, whose isotropic lines have a genuinely
non-trivial stabilizer; ``A_{U + U(2)} = F_2^2``, the issue's own small specimen, whose
stabilizer is trivial; and the anisotropic forms ``A_{U + U}`` (trivial group),
``A_{A2} = Z/3`` and ``A_{D4} = (Z/2)^2``, where the call must refuse because no nonzero
class is isotropic.  The heavy ``A_{T_Co}`` specimen lives in its own module, where its
wall clock is recorded rather than trimmed.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _first_isotropic_class(form):
    r"""One nonzero class of ``q = 0``, or ``None`` when the form is anisotropic."""
    zero = form.quadratic_value_module().zero()
    for element in form.elements():
        if element != form.zero() and form.q(element) == zero:
            return element
    return None


def _elements_of(subobject):
    r"""The element set of a submodule inside its ambient form."""
    inclusion = subobject.inclusion()
    return frozenset(inclusion(element) for element in subobject.elements())


def _fixes(isometry, elements):
    r"""Whether one automorphism of the ambient form fixes a set of its elements."""
    return frozenset(isometry(element) for element in elements) == elements


def _check_orbit_and_stabilizer(form, group, subobject):
    r"""The delivered sequence and the orbit-stabilizer identity on the returned objects."""
    orbit = group.orbit(subobject)
    stabilizer = group.stabilizer(subobject)
    action = group.subobject_orbit_action(subobject)

    assert stabilizer.supergroup() is group
    elements = _elements_of(subobject)
    for isometry in stabilizer.group_generators():
        assert _fixes(isometry, elements)

    assert int(orbit.cardinality()) == int(action.point_set().cardinality())
    assert int(orbit.cardinality()) == int(group.orbit_points(subobject).cardinality())
    assert subobject in orbit
    assert int(stabilizer.cardinality()) * int(orbit.cardinality()) == int(group.cardinality())
    return orbit, stabilizer


def test_the_four_dimensional_two_elementary_form_has_a_non_trivial_stabilizer() -> None:
    r"""``A_{U(2) + U(2)} = (Z/2)^4``: ``|O(q)| = 72``, an isotropic line of orbit 9 and stabilizer 8."""
    lattice = Lattices(ZZ)("U").twist(2) + Lattices(ZZ)("U").twist(2)
    form = lattice.discriminant_quadratic_form()
    group = form.orthogonal_group()

    assert int(form.cardinality()) == 16
    assert int(group.cardinality()) == 72

    subobject = form.isotropic_subobject([_first_isotropic_class(form)])
    assert subobject.cardinality() > 1

    orbit, stabilizer = _check_orbit_and_stabilizer(form, group, subobject)
    assert int(orbit.cardinality()) > 1
    assert int(stabilizer.cardinality()) > 1
    assert int(orbit.cardinality()) != int(group.cardinality())


def test_the_even_plane_summand_gives_a_trivial_stabilizer() -> None:
    r"""``A_{U + U(2)} = F_2^2``: two isotropic lines interchanged, so ``|Stab| = 1``."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U").twist(2)
    form = lattice.discriminant_quadratic_form()
    group = form.orthogonal_group()

    assert int(form.cardinality()) == 4
    assert int(group.cardinality()) == 2

    subobject = form.isotropic_subobject([_first_isotropic_class(form)])
    orbit, stabilizer = _check_orbit_and_stabilizer(form, group, subobject)
    assert int(orbit.cardinality()) == 2
    assert int(stabilizer.cardinality()) == 1


def test_an_anisotropic_form_refuses_the_isotropic_subobject_call() -> None:
    r"""``A_{A2} = Z/3`` and ``A_{D4} = (Z/2)^2``: every nonzero class has ``q != 0``."""
    for tag in ("A2", "D4"):
        form = Lattices(ZZ)(tag).discriminant_quadratic_form()
        assert _first_isotropic_class(form) is None
        zero = form.quadratic_value_module().zero()
        nonzero = tuple(element for element in form.elements() if element != form.zero())
        assert all(form.q(element) != zero for element in nonzero)
        with pytest.raises(AssertionError):
            form.isotropic_subobject([nonzero[0]])


def test_the_hyperbolic_plane_has_no_nonzero_class_at_all() -> None:
    r"""``A_{U + U}`` is trivial: one class, so there is nothing to be isotropic."""
    form = (Lattices(ZZ)("U") + Lattices(ZZ)("U")).discriminant_quadratic_form()

    assert int(form.cardinality()) == 1
    assert _first_isotropic_class(form) is None
