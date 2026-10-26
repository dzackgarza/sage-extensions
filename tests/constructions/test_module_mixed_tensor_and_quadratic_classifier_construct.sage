r"""Modules expose their mixed tensor algebra and the universal divided-square classifier for quadratic maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_mixed_tensor_algebra_multiplies_vector_and_covector_to_outer_product() -> None:
    module = QQ.free_module(2)
    vector = module((1, 2))
    covector = module.dual_module()((3, 4))
    algebra = module.mixed_tensor_algebra()
    product = algebra.include(vector) * algebra.include(covector)

    assert product.homogeneous_component((1, 1)) == vector.tensor_product(covector)
    assert product.homogeneous_component((1, 1)).trace() == 11


def test_quadratic_map_round_trips_through_its_divided_square_classifier() -> None:
    module = Modules(ZZ)(ZZ**2)
    x, y = module.basis()

    def quadratic_value(value):
        a, b = value.to_vector()
        return a**2 + 3 * a * b + 2 * b**2

    quadratic = module.quadratic_map(ZZ, quadratic_value)
    classifier = quadratic.classifying_morphism()
    recovered = module.quadratic_map_from_morphism(classifier)

    assert recovered(x + y) == 6
    assert recovered(2 * x - y) == 0
    assert all(
        recovered(value) == quadratic(value)
        for value in (x, y, x + y, 2 * x - y)
    )
