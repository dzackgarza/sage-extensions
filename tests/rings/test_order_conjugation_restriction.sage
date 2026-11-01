r"""Conjugation restricts to the maximal order, and the order's scalar boundary works.

`integers.Mor(integers)(conjugation)` for `QQ(sqrt 5)` used to recurse: the
order's element ingress asked for the unit morphism, whose evaluation is the
module action, which constructs an element again.  The primitive boundary is
`_OwnedRingElement._lmul_`, which now reads the engine's own base action instead
of constructing `r * 1` in the ring.

The ring equations of the restricted conjugation are the acceptance: it is the
field conjugation on the image, it fixes and negates what it must, it is
multiplicative and unital, and it is injective by construction.
"""

from sage_extensions.all import QuadraticField


def _specimen():
    field = QuadraticField(5)
    root = field.primitive_element()
    conjugation = field.Mor(field)(-root)
    integers = field.ring_of_integers()
    return field, root, conjugation, integers


def test_the_scalar_boundary_matches_repeated_addition_in_the_order() -> None:
    r"""`r * m` through the engine equals `m + m`, which never went through it."""
    field, root, conjugation, integers = _specimen()
    two_field = field.one() + field.one()
    golden = integers((field.one() + root) / two_field)
    two = integers.one() + integers.one()

    assert integers.scalar_multiple(two, golden) == golden + golden
    assert two * golden == golden + golden
    assert integers.scalar_multiple(integers.zero(), golden) == integers.zero()
    assert integers.scalar_multiple(integers.one(), golden) == golden


def test_conjugation_restricts_to_the_order_and_its_ring_equations_hold() -> None:
    field, root, conjugation, integers = _specimen()
    restricted = integers.Mor(integers)(conjugation)
    two_field = field.one() + field.one()
    golden = integers((field.one() + root) / two_field)

    assert restricted.field_embedding() == conjugation
    assert restricted.is_injective() is True

    assert restricted(golden) == integers((field.one() - root) / two_field)
    assert restricted(golden) + golden == integers.one()
    assert restricted(integers.one()) == integers.one()
    assert restricted(integers.zero()) == integers.zero()
    assert restricted(golden * golden) == restricted(golden) * restricted(golden)

    # Conjugation fixes the rational integers and negates the generator.
    assert restricted(integers(field.one())) == integers.one()
    assert restricted(integers(root)) == integers(-root)
