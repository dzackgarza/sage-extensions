r"""Relative Proj of a trivial rank-two bundle over a point is the projective line."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_trivial_bundle_projectivizes_to_projective_line() -> None:
    point = QQ.affine_spectrum()
    source = point.associated_module_sheaf(QQ.free_module(("s", "t")))
    projection = source.projectivization()
    total = projection.domain()

    assert total in RelativeProjectivizations(QQ)
    assert total.projectivization_projection() == projection
    assert total.projectivization_source_sheaf() is source
    assert total.is_isomorphic(ProjectiveSpaces(QQ)(1))
    assert total.tautological_line_bundle().rank() == 1
    assert total.universal_quotient().is_surjective()
