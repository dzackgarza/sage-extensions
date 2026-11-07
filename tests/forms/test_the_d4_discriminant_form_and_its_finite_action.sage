r"""The D4 discriminant form, built through the lattice API, and its finite action.

``Lattices(ZZ)("D4").discriminant_quadratic_form()`` is the public entry the
finite-form tests and their hashing regressions take.  It failed at the
restricted regular-module identification (#305): the value module of a form was
restricted to scalars along a second map that agreed with the algebra's
structure morphism pointwise but was not that morphism, so the module refused
to identify itself with its own scalars.

The specimen is small and the assertions are computed: the group of four
classes, the polar pairing nondegenerate on it, and ``O(q)`` acting on those
classes with the two orbits of an odd two-dimensional form.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_scalar_structure_is_the_algebra_s_own_after_an_equal_copy() -> None:
    r"""A restriction along an equal copy of ``ZZ -> QQ`` leaves one scalar structure.

    Two ring maps that agree pointwise are one map mathematically, and a
    restriction of scalars is interned once per map, so the first restriction along
    *any* copy of the scalar structure answers every later one.  The module it
    builds identifies itself with its scalars through
    ``regular_module_identification``, which asserts that its ``ring_map`` is
    ``QQ.algebra_structure_morphism()``: interning along a copy makes that
    identification refuse the module the algebra's own structure asked for.  The
    consumer below states its own copy first, exactly as a caller may, and the
    discriminant form must still construct.
    """
    field = ZZ.fraction_field()
    copy = ZZ.Mor(field)(lambda scalar: field(scalar))
    assert copy == field.algebra_structure_morphism()

    Modules(field).restriction_of_scalars(copy)

    form = Lattices(ZZ)("D4").discriminant_quadratic_form()
    assert int(form.cardinality()) == 4


def test_the_d4_discriminant_form_builds_and_its_polar_pairing_has_trivial_radical() -> None:
    r"""``A_{D4} = (Z/2)^2``: four classes, and the polar pairing has trivial radical.

    The two forms of a quadratic discriminant form take values in *different*
    groups, and this specimen shows it: ``q`` lands in ``Q/2Z`` and the polar form
    ``b`` in ``Q/Z``, so their zero elements are not interchangeable and the two
    value modules are distinct objects.  In ``Q/Z`` the polar form of a quadratic
    form is alternating, ``b(x,x) = 0``, which is where the ``2 q(x)`` of the
    quadratic normalization goes; the nondegeneracy that matters is that the
    radical ``{x : b(x,y) = 0 for all y}`` is trivial.
    """
    form = Lattices(ZZ)("D4").discriminant_quadratic_form()

    assert int(form.cardinality()) == 4
    classes = tuple(form.elements())
    zero = form.zero()
    polar_zero = form.b(zero, zero)
    assert form.quadratic_value_module() is not form.bilinear_value_module()
    assert form.q(zero) != polar_zero
    for left in classes:
        assert form.b(left, left) == polar_zero
        if left == zero:
            continue
        assert any(form.b(left, right) != polar_zero for right in classes)


def test_the_orthogonal_group_of_the_d4_discriminant_form_acts_on_its_classes() -> None:
    r"""``O(q_{D4})`` is an odd two-dimensional orthogonal group: two orbits on four classes."""
    form = Lattices(ZZ)("D4").discriminant_quadratic_form()
    group = form.orthogonal_group()

    assert int(group.cardinality()) > 1
    action = group.element_action()
    orbits = action.orbits()
    assert int(orbits.cardinality()) == 2
    assert int(action.point_set().cardinality()) == int(form.cardinality())
