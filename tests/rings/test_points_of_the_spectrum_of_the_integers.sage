r"""The points of ``Spec Z``: the generic point ``(0)`` and the closed points ``(p)``.

``Z`` is a Dedekind domain of dimension one, so a nonzero prime ``(p)`` has height
one and a closed point (its closure ``Spec F_p`` has dimension zero), while ``(0)``
has height zero and is dense (its closure is all of ``Spec Z``, of dimension one).
The generic point specializes to every closed point and no closed point
specializes to another.  The local ring ``Z_(p)`` is a discrete valuation ring,
hence regular with embedding dimension one, and the order of vanishing at ``(p)``
is the ``p``-adic valuation: ``ord_5(50) = 2`` and ``ord_5(3) = 0``.  The residue
field at ``(5)`` is ``F_5`` and at ``(0)`` is ``Q``.

``Z/6`` has exactly two primes, ``(2)`` and ``(3)``, so its spectrum has two points.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_heights_and_closure_dimensions_of_the_points_of_spec_z() -> None:
    spectrum = ZZ.spectrum()
    five = spectrum(ZZ.ideal(ZZ(5)))
    generic = spectrum.generic_point()

    assert five.height() == 1
    assert generic.height() == 0
    assert five.closure_dimension() == 0
    assert generic.closure_dimension() == 1


def test_the_generic_point_specializes_to_every_closed_point() -> None:
    spectrum = ZZ.spectrum()
    two = spectrum(ZZ.ideal(ZZ(2)))
    five = spectrum(ZZ.ideal(ZZ(5)))
    generic = spectrum.generic_point()

    assert generic.specializes_to(five)
    assert generic.specializes_to(two)
    assert not five.specializes_to(two)
    assert not five.specializes_to(generic)
    assert spectrum.le(generic, five)
    assert not spectrum.le(five, two)


def test_the_local_ring_at_a_closed_point_is_a_regular_ring_of_embedding_dimension_one() -> None:
    five = ZZ.spectrum()(ZZ.ideal(ZZ(5)))

    assert five.is_regular()
    assert five.embedding_dimension() == 1
    assert five.is_locally_factorial()


def test_the_order_of_vanishing_at_five_is_the_five_adic_valuation() -> None:
    five = ZZ.spectrum()(ZZ.ideal(ZZ(5)))

    assert five.order_of_vanishing(ZZ(50)) == 2
    assert five.order_of_vanishing(ZZ(3)) == 0
    assert five.order_of_vanishing(ZZ(50) * ZZ(125)) == five.order_of_vanishing(ZZ(50)) + 3


def test_the_residue_fields_of_spec_z() -> None:
    spectrum = ZZ.spectrum()
    five = spectrum(ZZ.ideal(ZZ(5)))
    residue = five.residue_map()

    assert residue(ZZ(7)) == residue(ZZ(2))
    assert residue(ZZ(10)) == five.residue_field().zero()
    assert spectrum.generic_point().residue_field() is QQ


def test_z_mod_six_has_two_prime_points() -> None:
    assert ZZ.ideal(ZZ(6)).quotient_ring().spectrum().cardinality() == 2


def test_the_residue_field_at_five_has_five_elements() -> None:
    assert ZZ.spectrum()(ZZ.ideal(ZZ(5))).residue_field().cardinality() == 5
