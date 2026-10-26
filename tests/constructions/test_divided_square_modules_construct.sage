r"""The divided square classifies quadratic maps.

For ``M=ZZ^2``, the universal quadratic map ``gamma_2:M->Gamma^2(M)`` satisfies
``gamma_2(2x)=4 gamma_2(x)`` and its polarization is
``gamma_2(x+y)-gamma_2(x)-gamma_2(y)``.  Any quadratic map factors uniquely
through this module.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _divided_square_of_plane():
    module = ZZ.free_module(2)
    return module, module.divided_square()


def test_divided_square_retains_its_source_and_universal_quadratic_map() -> None:
    module, square = _divided_square_of_plane()
    x, y = module.module_generator(0), module.module_generator(1)

    assert square in DividedSquareModules(ZZ)
    assert square.divided_square_source() is module
    assert square.quadratic(2 * x) == 4 * square.quadratic(x)
    assert square.polar(x, y) == square.quadratic(x + y) - square.quadratic(x) - square.quadratic(y)
    assert isinstance(square.quadratic(x), square.ElementType)


def test_quadratic_map_factors_through_the_divided_square() -> None:
    module, square = _divided_square_of_plane()
    x, y = module.module_generator(0), module.module_generator(1)

    def value(vector):
        a, b = vector.to_vector()
        return a**2 + a * b + b**2

    quadratic = module.quadratic_map(ZZ, value)
    factor = square.from_quadratic(quadratic, ZZ.regular_module())

    for vector in (x, y, x + y, 2 * x - y):
        assert factor(square.quadratic(vector)) == quadratic(vector)


def test_divided_square_module_morphisms_have_identity() -> None:
    _module, square = _divided_square_of_plane()
    identity = square.Mor(square).identity()

    assert identity(square.zero()) == square.zero()
    assert identity * identity == identity
