r"""A module with connection retains exactly its module and selected connection.

The trivial connection on a free rank-one module over ``QQ[x]`` is flat, so the
same object lies in both the connection category and its flat refinement.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _structured_trivial_connection():
    algebra = QQ["x"]
    module = algebra.free_module(1)
    connections = module.connections()
    connection = connections({0: connections.target_module().zero()})
    return algebra, module, connection, ModulesWithConnection(algebra)(connection)


def test_module_with_connection_retains_connection_and_unformed_module() -> None:
    algebra, module, connection, structured = _structured_trivial_connection()

    assert structured in ModulesWithConnection(algebra)
    assert structured.connection() is connection
    assert structured.unformed_module() is module
    assert structured.Mor(structured).identity() * structured.Mor(structured).identity() == structured.Mor(structured).identity()
