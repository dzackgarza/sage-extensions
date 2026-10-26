r"""Graded modules retain degree pieces and homogeneous decomposition.

The tensor algebra ``T(QQ^2)`` is graded by tensor degree.  Its generators have
degree one, their products add degrees, and ``x + y^2`` decomposes into degree
one and degree two components.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _tensor_algebra():
    return (QQ**2).tensor_algebra()


def test_graded_module_exposes_index_monoid_pieces_generators_and_parity() -> None:
    graded = _tensor_algebra()
    x = graded.algebra_generator(0)
    degree = graded.homogeneous_degree(x)
    parity = graded.parity_homomorphism()

    assert graded in GradedModules(QQ)
    assert graded.is_graded()
    assert degree == 1
    assert graded.combine_degrees(degree, degree) == 2
    assert degree in graded.grading_index_set()
    assert graded.grading_monoid() is not None
    assert graded.graded_piece(2).module_rank() == 4
    assert graded.degree_on_module_generator(x) == degree
    assert len(tuple(graded.module_generators_of_degree(1))) == 2
    assert parity(1) != parity(2)


def test_concentrated_graded_module_remembers_its_unique_degree() -> None:
    category = GradedModules(QQ)
    graded = category.an_object()

    assert graded.concentrated_degree() == category.grading_monoid().zero()


def test_graded_elements_expose_degree_components_homogeneity_and_truncation() -> None:
    graded = _tensor_algebra()
    x = graded.algebra_generator(0)
    y = graded.algebra_generator(1)
    mixed = x + y * y
    components = mixed.homogeneous_components()

    assert x.degree() == 1
    assert mixed.degree() == 2
    assert x.is_homogeneous()
    assert not mixed.is_homogeneous()
    assert components[1] == x
    assert components[2] == y * y
    assert mixed.truncate(2) == x
