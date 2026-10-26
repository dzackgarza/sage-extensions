r"""A projectivization retains the pullback of its source sheaf to the total space."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_projectivization_pulls_source_sheaf_to_total_space() -> None:
    point = QQ.affine_spectrum()
    source = point.associated_module_sheaf(QQ.free_module(("s", "t")))
    total = source.projectivization().domain()
    pulled = total.pulled_source_sheaf()

    assert pulled.scheme() is total
    assert pulled.rank() == 2
