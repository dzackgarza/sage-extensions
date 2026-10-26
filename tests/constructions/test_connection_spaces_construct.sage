r"""Connection spaces contain the connections on one module over an algebra.

For the free rank-one module over ``QQ[x]``, the trivial connection has zero
generator image, satisfies the Leibniz rule, has zero curvature, and produces
the usual de Rham differential graded module.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _trivial_affine_line_connection():
    algebra = QQ["x"]
    module = algebra.free_module(1)
    connections = module.connections()
    connection = connections({0: connections.target_module().zero()})
    return algebra, module, connections, connection


def test_connection_space_builds_the_trivial_connection_with_all_defining_data() -> None:
    algebra, module, connections, connection = _trivial_affine_line_connection()
    one_forms = algebra.kahler_differentials()
    target = connections.target_module()
    generator = module.module_generator(0)
    x = algebra.algebra_generator("x")

    assert connections in Cat()
    assert connection in connections
    assert connection.algebra() is algebra
    assert connection.module() is module
    assert connection.one_forms() is one_forms
    assert connection.target_module() is target
    assert connection.generator_image(0) == target.zero()
    assert connection(x * generator) == target.pure_tensor(generator, one_forms.differential_generator("x"))


def test_trivial_connection_has_zero_curvature_and_owned_morphism_views() -> None:
    _algebra, module, _connections, connection = _trivial_affine_line_connection()
    as_morphism = connection.as_morphism()
    underlying = connection.underlying_linear_morphism()

    assert connection.is_flat()
    assert connection.curvature_on_generator(0) == connection.curvature_target().zero()
    assert as_morphism.domain() is module
    assert as_morphism.codomain() is connection.target_module()
    assert underlying.domain() is module
    assert underlying.codomain() is connection.target_module()
    assert connection.de_rham_module() in DifferentialGradedModules(connection.algebra().de_rham_algebra())
