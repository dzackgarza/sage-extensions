r"""Quadratic maps on ``Z^2`` and the divided-square classifier."""

from sage_extensions.all import *  # noqa: F401,F403


def test_quadratic_map_is_recovered_from_its_classifying_morphism_on_the_divided_square() -> None:
    r"""``q(ax + by) = a^2 + 3ab + 2b^2`` corresponds to ``Gamma^2(Z^2) -> Z``: ``gamma(x) |-> 1``, ``gamma(y) |-> 2``, ``xy |-> 3``.

    ``Gamma^2(Z^2)`` is free of rank 3 on ``gamma(x), gamma(y), xy``; the
    polar form has ``b(x, y) = q(x + y) - q(x) - q(y) = 6 - 1 - 2 = 3``, and
    ``q(2x - y) = 4 - 6 + 2 = 0``.
    """
    module = Modules(ZZ)(ZZ**2)
    x, y = module.basis()

    def quadratic_value(value):
        a, b = value.to_vector()
        return a**2 + 3 * a * b + 2 * b**2

    quadratic = module.quadratic_map(ZZ, quadratic_value)
    classifier = quadratic.classifying_morphism()
    square = module.divided_square()
    recovered = module.quadratic_map_from_morphism(classifier)

    assert square.module_rank() == 3
    assert classifier(square.quadratic(x)) == 1
    assert classifier(square.quadratic(y)) == 2
    assert classifier(square.quadratic(x + y) - square.quadratic(x) - square.quadratic(y)) == 3
    for value in (x, y, x + y, 2 * x - y, 5 * x + 7 * y):
        assert recovered(value) == quadratic(value)
    assert recovered(x + y) == 6
    assert recovered(2 * x - y) == 0
