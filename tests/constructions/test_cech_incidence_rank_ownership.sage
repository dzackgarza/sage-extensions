r"""Čech incidence uses the selected ranks of covering-family labels."""

from sage_extensions.all import *  # noqa: F401,F403


def test_distinguished_cover_cech_incidence_and_terminal_covered_object() -> None:
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    cover = line.distinguished_open_cover(x, ring.one() - x)
    site = cover.cech_site()

    pair, first, second, total = (
        site((0, 1)), site((0,)), site((1,)), site(())
    )
    assert site.le(pair, first)
    assert site.le(pair, second)
    assert site.le(first, total)
    assert site.le(second, total)
    assert not site.le(first, pair)
    assert not site.le(total, first)
