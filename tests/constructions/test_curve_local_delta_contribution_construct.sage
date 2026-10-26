r"""A rational cusp contributes its local delta invariant with residue degree one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rational_cusp_local_delta_contribution_retains_its_data() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    cusp = IsolatedHypersurfaceSingularity(ring, y**2 - x**3)
    origin = ring.ideal(x, y)
    contribution = CurveLocalDeltaContribution(cusp, origin)

    assert contribution.singularity() is cusp
    assert contribution.local_point() is origin
    assert contribution.projective_support() is None
    assert contribution.delta_invariant() == 1
    assert contribution.residue_degree() == 1
    assert contribution.weighted_contribution() == 1
