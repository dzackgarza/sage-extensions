r"""The plane cusp y^2=x^3 has its standard local singularity invariants."""

from sage_extensions.all import *  # noqa: F401,F403


def _cusp():
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    return ring, x, y, IsolatedHypersurfaceSingularity(ring, y**2 - x**3)


def test_cusp_retains_equation_and_jacobian_data() -> None:
    ring, x, y, cusp = _cusp()

    assert cusp.polynomial_ring() is ring
    assert cusp.equation() == y**2 - x**3
    assert set(cusp.jacobian_generators()) == {-3 * x**2, 2 * y}


def test_cusp_is_singular_with_two_dimensional_zariski_tangent_space() -> None:
    _ring, _x, _y, cusp = _cusp()
    tangent = cusp.zariski_tangent_space()
    embedding = cusp.zariski_tangent_embedding()

    assert cusp.is_singular_at_origin()
    assert not cusp.is_regular_at_origin()
    assert cusp.ambient_tangent_space().dimension() == 2
    assert tangent.dimension() == 2
    assert embedding.domain() is tangent
    assert embedding.codomain() is cusp.ambient_tangent_space()


def test_cusp_has_mu_two_tau_two_delta_one_and_one_branch() -> None:
    ring, x, y, cusp = _cusp()
    origin = ring.ideal(x, y)

    assert cusp.milnor_number() == 2
    assert cusp.tjurina_number() == 2
    assert cusp.local_tjurina_number() == 2
    assert cusp.delta_invariant() == 1
    assert cusp.delta_invariant_at(origin) == 1
    assert cusp.delta_contribution_over_base(origin) == 1
    assert cusp.number_of_branches_at_origin() == 1


def test_cusp_milnor_and_tjurina_algebras_have_dimension_two() -> None:
    _ring, _x, _y, cusp = _cusp()

    assert cusp.milnor_algebra().vector_space_dimension() == 2
    assert cusp.tjurina_algebra().vector_space_dimension() == 2
