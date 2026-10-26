r"""A finite quotient Z/12 is Artinian of Krull dimension zero."""

from sage_extensions.all import *  # noqa: F401,F403


def test_z_mod_twelve_is_artinian() -> None:
    ring = Zmod(12)

    assert ring in ArtinianRings()
    assert ring in NoetherianRings()
    assert ring.krull_dimension() == 0
    assert ring.cardinality() == cardinal(12)

