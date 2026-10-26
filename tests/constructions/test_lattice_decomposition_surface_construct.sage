r"""An orthogonal direct sum retains its represented lattice decomposition."""

from sage_extensions.all import *  # noqa: F401,F403


def _double_a2():
    a2 = Lattices(ZZ)("A2")
    return a2, a2 + a2


def test_orthogonal_sum_exposes_its_represented_decomposition() -> None:
    a2, double = _double_a2()
    decomposition = double.decomposition()

    assert decomposition is not None
    assert double.is_decomposable()
    assert double.biproduct_factors().cardinality() == cardinal(2)
    assert double.biproduct_factors()[0] is a2
    assert double.biproduct_factors()[1] is a2


def test_orthogonal_sum_exposes_indecomposable_summands_and_names() -> None:
    _a2, double = _double_a2()
    summands = double.indecomposable_summands()
    names = double.decomposition_names()

    assert summands.cardinality() == cardinal(2)
    assert names.cardinality() == cardinal(2)
