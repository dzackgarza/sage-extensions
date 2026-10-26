r"""Canonical maps between tensor, symmetric, exterior, and divided powers satisfy their defining relations."""

from sage_extensions.all import *  # noqa: F401,F403


def test_tensor_quotients_and_symmetric_to_divided_have_standard_degree_two_relations() -> None:
    module = Modules(ZZ).free_module(("x", "y"))
    tensor_algebra = module.tensor_algebra()
    symmetric = module.symmetric_algebra()
    exterior = module.exterior_algebra()
    divided = module.divided_power_algebra()
    x_t, y_t = tensor_algebra.algebra_generator("x"), tensor_algebra.algebra_generator("y")
    x_s = symmetric.algebra_generator("x")
    x_d = divided.degree_one_generator("x")
    gamma_2 = divided.divided_power(x_d, 2)

    assert module.tensor_to_symmetric()(x_t * y_t - y_t * x_t) == symmetric.zero()
    assert module.tensor_to_alternating()(x_t * x_t) == exterior.zero()
    assert module.tensor_to_alternating()(x_t * y_t + y_t * x_t) == exterior.zero()
    assert module.symmetric_to_divided()(x_s**2) == 2 * gamma_2


def test_divided_to_symmetric_inverts_symmetric_to_divided_over_rationals() -> None:
    module = Modules(QQ).free_module(("x", "y"))
    symmetric = module.symmetric_algebra()
    divided = module.divided_power_algebra()
    x = symmetric.algebra_generator("x")
    gamma_2 = divided.divided_power(divided.degree_one_generator("x"), 2)

    assert module.divided_to_symmetric()(gamma_2) == x**2 / 2
    assert module.divided_to_symmetric()(module.symmetric_to_divided()(x**2)) == x**2


def test_divided_and_exterior_power_products_have_standard_coefficients_and_signs() -> None:
    module = Modules(ZZ).free_module(("x", "y"))
    x, y = module.module_generators()
    gamma_2_x = module.divided_power_element(2, x)
    wedge_xy = module.exterior_power_product(1, x, 1, y)
    wedge_yx = module.exterior_power_product(1, y, 1, x)

    assert module.divided_power_product(1, x, 1, x) == 2 * gamma_2_x
    assert wedge_xy == -wedge_yx
    assert wedge_xy != module.exterior_power(2).zero()
