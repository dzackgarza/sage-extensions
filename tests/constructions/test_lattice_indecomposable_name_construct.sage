r"""Named root lattices retain their registered indecomposable Gram-block names."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_has_its_registered_indecomposable_name() -> None:
    a2 = Lattices(ZZ)("A2")

    assert a2.indecomposable_name() == "A_{2}"
    assert not a2.is_decomposable()


def test_a2_orthogonal_sum_reports_registered_names_of_both_summands() -> None:
    a2 = Lattices(ZZ)("A2")
    names = (a2 + a2).decomposition_names()

    assert names.cardinality() == cardinal(2)
    assert names[0] == "A_{2}"
    assert names[1] == "A_{2}"
