r"""The cusp retains its differential, completion, and conductor at the origin."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cusp_differential_at_the_origin_is_zero() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    cusp = IsolatedHypersurfaceSingularity(ring, y**2 - x**3)
    differential = cusp.differential_at_origin()

    for tangent_vector in cusp.ambient_tangent_space().module_generating_set():
        assert differential(
            cusp.ambient_tangent_space().module_generator(tangent_vector)
        ) == differential.codomain().zero()


def test_cusp_completed_local_ring_is_one_dimensional_and_conductor_nonzero() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    cusp = IsolatedHypersurfaceSingularity(ring, y**2 - x**3)

    assert cusp.completed_local_ring().krull_dimension() == 1
    assert not cusp.conductor_ideal_at_origin().is_zero()
