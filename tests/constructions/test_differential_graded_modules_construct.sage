r"""Differential graded modules retain their DGA, graded module, and differential.

The regular module of the de Rham algebra of ``QQ[x]`` is a differential graded
module over that DGA; its differential in degree zero lands in degree one and
squares to zero.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _regular_de_rham_module():
    dga = QQ["x"].de_rham_algebra()
    return dga, dga.regular_dg_module()


def test_regular_dg_module_retains_dga_unformed_module_and_differential_component() -> None:
    dga, module = _regular_de_rham_module()
    differential = module.differential_component(0)

    assert module in DifferentialGradedModules(dga)
    assert module.dga() is dga
    assert module.is_differential_graded_module()
    assert module.unformed_module() in GradedModules(dga.base_ring())
    assert differential.domain() == module.graded_piece(0)
    assert differential.codomain() == module.graded_piece(1)


def test_differential_graded_module_morphisms_have_identity() -> None:
    _dga, module = _regular_de_rham_module()
    identity = module.Mor(module).identity()

    assert identity.domain() is module
    assert identity.codomain() is module
    assert identity * identity == identity
