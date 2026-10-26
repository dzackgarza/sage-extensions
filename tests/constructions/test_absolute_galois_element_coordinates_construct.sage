r"""A finite-field Frobenius element can retain a compatible realized finite-stage coordinate."""

from sage_extensions.all import *  # noqa: F401,F403


def test_frobenius_extends_and_recovers_a_finite_stage_coordinate() -> None:
    galois = AbsoluteGaloisGroup(GF(5))
    frobenius = galois.frobenius()
    stage = galois.finite_extension(2)
    restriction = galois.restriction_map(stage)
    coordinate = restriction(frobenius)

    assert frobenius.restriction_coordinate(stage) is None
    frobenius.extend_coordinate(restriction, coordinate)
    assert stage in frobenius.realized_stages()
    assert frobenius.restriction_coordinate(stage) == coordinate
