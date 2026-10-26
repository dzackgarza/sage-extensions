r"""DGA Mor objects preserve multiplication and commute with the differential."""

from sage_extensions.all import *  # noqa: F401,F403


def test_de_rham_dga_identity_commutes_with_the_differential() -> None:
    dga = QQ.polynomial_ring("x").de_rham_algebra()
    identity = dga.Mor(dga).identity()
    x = dga(dga.de_rham_source_algebra().algebra_generator("x"))
    differential = dga.differential()

    assert identity.domain() is dga
    assert identity.codomain() is dga
    assert identity(differential(x)) == differential(identity(x))
    assert identity(dga.one()) == dga.one()
    assert identity * identity == identity

