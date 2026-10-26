r"""ADE log pairs expose the standard aliases of their retained base and Dynkin data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_e6_log_pair_aliases_recover_its_retained_data() -> None:
    pair = ADELogPairs(QQ)("E", 6)

    assert pair.base() is pair
    assert pair.scheme() is pair.log_scheme()
    assert pair.rank() == pair.dynkin_rank() == 6
    assert pair.is_affine() == pair.is_affine_type()
    assert pair.dynkin_diagram() == pair.coxeter_diagram()
    assert pair.polarizing_polytope() is pair.polygon()
    assert pair.vertices() == pair.polygon().vertices()
