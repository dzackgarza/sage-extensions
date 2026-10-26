r"""Flat connections are exactly connections with zero curvature.

On the affine line every connection on a line bundle has curvature in
``Omega^2=0``.  The trivial rank-one connection is therefore an object of the
flat-connection refinement and reports flatness directly.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_trivial_affine_line_connection_lies_in_the_flat_refinement() -> None:
    algebra = QQ["x"]
    module = algebra.free_module(1)
    connections = module.connections()
    connection = connections({0: connections.target_module().zero()})
    structured = ModulesWithConnection(algebra)(connection)

    assert structured in ModulesWithFlatConnection(algebra)
    assert structured.is_flat_connection()
