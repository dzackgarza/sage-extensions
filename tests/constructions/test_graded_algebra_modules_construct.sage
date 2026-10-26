r"""Graded algebra modules retain the selected graded algebra and right action.

The regular differential graded module of a de Rham algebra is, after forgetting
its differential, the regular graded right module over that same algebra.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_regular_de_rham_module_retains_graded_algebra_and_right_action() -> None:
    algebra = QQ["x"].de_rham_algebra()
    module = algebra.regular_dg_module()
    action = module.right_action()
    zero = module.zero()

    assert module in GradedAlgebraModules(algebra)
    assert module.graded_algebra() is algebra
    assert action(zero, algebra.one()) == zero
    assert module.act(zero, algebra.one()) == zero
