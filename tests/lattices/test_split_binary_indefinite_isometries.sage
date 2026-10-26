from sage_extensions.all import *


def test_split_binary_indefinite_isometry_returns_an_actual_witness() -> None:
    source = Lattices(ZZ)([[0, 2], [2, 0]])
    target = Lattices(ZZ)([[0, 2], [2, 4]])

    assert source.discriminant() == target.discriminant()
    assert source.gram_matrix().determinant() < 0
    assert source.Isom(target).is_empty() is False

    isometry = source.Isom(target).an_element()
    assert isometry.domain() is source
    assert isometry.codomain() is target
    assert (~isometry) * isometry == source.Aut().one()
    for left in source.module_generators():
        for right in source.module_generators():
            assert target.b(isometry(left), isometry(right)) == source.b(left, right)


def test_split_binary_indefinite_nonequivalence_is_decided_exactly() -> None:
    source = Lattices(ZZ)([[0, 2], [2, 0]])
    target = Lattices(ZZ)([[2, 2], [2, 0]])

    assert source.discriminant() == target.discriminant()
    assert source.Isom(target).is_empty() is True
