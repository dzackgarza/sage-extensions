r"""Coherent cohomology of a nonreduced affine scheme."""

from sage_extensions.all import *


def test_the_structure_sheaf_of_the_dual_numbers_has_rank_one_global_sections_and_no_higher_cohomology() -> None:
    r"""On \(X = \operatorname{Spec} A\), \(A = \mathbf Q[e]/(e^2)\): \(H^0(X,\mathcal O_X) = A\), free of rank \(1\)
    over \(A\), and \(H^i(X,\mathcal O_X) = 0\) for \(i>0\).

    Source: Hartshorne, *Algebraic Geometry*, III.3.5 (Serre's affine vanishing).
    """
    R = QQ["e"]
    e = R.gen()
    A = R.quotient(R.ideal(e**2))
    X = Schemes(QQ)(A)
    structure = X.structure_sheaf()

    assert structure.cohomology(0).module_rank() == 1
    assert structure.cohomology(1).is_zero()
    assert structure.cohomology(2).is_zero()
