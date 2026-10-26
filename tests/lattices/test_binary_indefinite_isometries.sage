from sage_extensions.all import *


def test_binary_indefinite_isometry_has_an_exact_integral_witness() -> None:
    source = Lattices(ZZ)([[2, 1], [1, -2]])
    target = Lattices(ZZ)([[2, 3], [3, 2]])

    assert source.signature_pair() == target.signature_pair()
    assert source.determinant() == target.determinant() == -5
    assert source.discriminant() == target.discriminant() == 5
    assert not source.is_definite()
    assert not target.is_definite()

    isometries = source.Isom(target)
    assert isometries.is_empty() is False
    witness = isometries.an_element()

    assert witness.domain() is source
    assert witness.codomain() is target
    assert witness.cokernel().is_zero()
    for left in source.module_generators():
        for right in source.module_generators():
            assert target.b(witness(left), witness(right)) == source.b(left, right)


def test_binary_indefinite_different_discriminants_are_not_isometric() -> None:
    source = Lattices(ZZ)([[2, 1], [1, -2]])
    target = Lattices(ZZ)([[2, 1], [1, -3]])

    assert source.discriminant() != target.discriminant()
    assert source.Isom(target).is_empty() is True
