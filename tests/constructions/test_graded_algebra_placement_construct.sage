r"""Degree and homogeneity belong to graded modules, not only graded algebras."""

from sage_extensions.all import *  # noqa: F401,F403


def test_degree_and_homogeneity_are_sited_on_graded_modules() -> None:
    module = GradedModules(QQ).an_object()
    generator = next(iter(module.module_generators()))

    assert module in GradedModules(QQ)
    assert module not in GradedAlgebras(QQ)
    assert module.homogeneous_degree(generator) == module.grading_monoid().zero()
    assert generator.degree() == module.grading_monoid().zero()
    assert generator.is_homogeneous()
