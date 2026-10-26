r"""Relative projectivization retains the symmetric algebra of its source sheaf."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_projectivization_has_rank_two_symmetric_algebra() -> None:
    point = QQ.affine_spectrum()
    source = point.associated_module_sheaf(QQ.free_module(("s", "t")))
    total = source.projectivization().domain()
    symmetric = total.symmetric_algebra()

    assert symmetric in SymmetricAlgebras(QQ)
    assert symmetric.algebra_generators().cardinality() == cardinal(2)
