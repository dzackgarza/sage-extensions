from sage_extensions.all import *


def polynomials():
    return QQ.free_module(("x",)).symmetric_algebra()


def trivial_connection():
    r"""$\nabla = d$ on the free module of rank one over $\mathbb Q[x]$: $\nabla(e) = 0$."""
    module = polynomials().free_module(Sets.Δ[0])
    connections = module.connections()
    return connections(lambda label: connections.target_module().zero())


def with_connection():
    connection = trivial_connection()
    return ModulesWithConnection(connection.algebra())(connection)


def test_the_connection_lives_over_the_polynomial_ring() -> None:
    assert trivial_connection().algebra() == polynomials()


def test_the_categories_of_the_module_with_connection() -> None:
    assert with_connection() in ModulesWithConnection(polynomials())


def test_every_connection_on_a_line_over_a_curve_is_flat() -> None:
    r"""The curvature lies in $\Omega^2_{\mathbb Q[x]} = 0$."""
    assert with_connection() in ModulesWithFlatConnection(polynomials())


def test_the_module_with_connection_has_one_endomorphism_category() -> None:
    structured = with_connection()
    endomorphisms = structured.Mor(structured)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert structured.Mor(structured) is endomorphisms
    assert identity * identity == identity
