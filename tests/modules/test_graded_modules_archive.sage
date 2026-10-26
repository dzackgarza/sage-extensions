r"""Homogeneous decomposition in the tensor algebra of $\mathbb Q^2$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_concentrated_graded_module_retains_its_selected_degree() -> None:
    category = GradedModules(QQ)
    graded = category.an_object()

    assert graded in category
    assert graded.concentrated_degree() == category.grading_monoid().zero()


def test_x_plus_y_squared_in_the_tensor_algebra_has_components_of_degrees_one_and_two() -> None:
    r"""$T(\mathbb Q^2) = \bigoplus_n (\mathbb Q^2)^{\otimes n}$ is graded by tensor degree; $x + y \otimes y$
    is not homogeneous, has degree 2, and components $x$ in degree 1 and $y \otimes y$ in degree 2.

    Source: Lang, Algebra, XVI.7 (the tensor algebra and its grading).
    """
    T = (QQ**2).tensor_algebra()
    x = T.algebra_generator(0)
    y = T.algebra_generator(1)
    mixed = x + y * y

    assert x.degree() == 1
    assert (y * y).degree() == 2
    assert (x * y * x).degree() == 3
    assert mixed.degree() == 2
    assert x.is_homogeneous()
    assert (x * y - y * x).is_homogeneous()
    assert not mixed.is_homogeneous()

    components = mixed.homogeneous_components()
    assert components[1] == x
    assert components[2] == y * y
    assert mixed.truncate(2) == x
    assert x * y != y * x
