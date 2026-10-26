"""Prime fields and local integer quotients.

An integer class modulo p^k is a unit exactly when p does not divide it.
Thus the nonunits form the unique maximal ideal (p), with residue field F_p.
Modulo 6 the distinct maximal ideals (2) and (3) prevent locality.
"""

from sage_extensions.categories.rings.ring_foundation import (
    GF,
    Zmod,
    OwnedRings,
    PrimeFields,
    _owned_integers,
)


def test_integer_residue_constructions() -> None:
    integers = _owned_integers()
    field = GF(5)
    assert field is Zmod(5) is PrimeFields()(5)
    assert field is integers.quotient_ring(integers.ideal(5))
    assert field in PrimeFields()
    assert field in OwnedRings().Division()
    assert field(2).multiplicative_order() == 4
    assert field(4).sqrt() ** 2 == field(4)

    local = Zmod(9)
    assert local in OwnedRings().Commutative().Local()
    assert local.maximal_ideal() == local.ideal(local(3))
    assert local.residue_field() is GF(3)

    composite = Zmod(6)
    assert composite not in OwnedRings().Commutative().Local()
    assert composite not in OwnedRings().Division()
