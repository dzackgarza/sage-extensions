r"""Morphisms of modules with connection are horizontal linear maps.

The identity on a module with the trivial affine-line connection is horizontal;
as a connection morphism it retains both structured endpoints and its underlying
linear morphism.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _module_with_trivial_connection():
    algebra = QQ["x"]
    module = algebra.free_module(1)
    connections = module.connections()
    connection = connections({0: connections.target_module().zero()})
    structured = ModulesWithConnection(algebra)(connection)
    return structured


def test_connection_mor_identity_retains_underlying_linear_map_and_endpoints() -> None:
    structured = _module_with_trivial_connection()
    hom = structured.Mor(structured)
    identity = hom.identity()
    as_morphism = identity.as_morphism()
    underlying = identity.underlying_linear_morphism()

    assert hom in Cat()
    assert identity.domain() is structured
    assert identity.codomain() is structured
    assert as_morphism == underlying
    assert underlying * underlying == underlying
    assert identity * identity == identity
