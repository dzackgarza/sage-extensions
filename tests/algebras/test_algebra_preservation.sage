r"""Centres of associative and nonassociative algebras."""

from sage_extensions.all import *  # noqa: F401,F403


def test_center_of_the_two_by_two_matrix_algebra_is_the_scalars() -> None:
    r"""``Z(M_2(QQ)) = QQ * I``, of dimension 1: a matrix commuting with every
    matrix unit ``E_ij`` is scalar."""
    matrices = QQ.matrix_space(2)
    center = matrices.center()
    inclusion = center.center_inclusion()

    assert center.module_rank() == 1
    assert inclusion(center.one()) == matrices.identity()
    assert matrices.matrix_unit(0, 1) * matrices.matrix_unit(1, 0) != matrices.matrix_unit(1, 0) * matrices.matrix_unit(0, 1)


def test_commutative_nonassociative_algebra_has_the_whole_module_as_commutant() -> None:
    r"""On ``QQ<x, y>`` with ``x^2 = y``, ``xy = yx = x``, ``y^2 = 0``:

    the product is commutative, so the commutant ``{z : zw = wz for all w}`` is
    the whole rank-2 module; it is not associative, since
    ``(x x) y = y y = 0`` while ``x (x y) = x x = y``.
    """
    module = Modules(QQ).free_module(("x", "y"))
    x = module.module_generator("x")
    y = module.module_generator("y")
    algebra = Algebras(QQ)(
        module,
        {("x", "x"): y, ("x", "y"): x, ("y", "x"): x, ("y", "y"): module.zero()},
    )

    assert algebra.product(algebra.product(x, x), y) == module.zero()
    assert algebra.product(x, algebra.product(x, y)) == y
    assert algebra.center().module_rank() == 2
