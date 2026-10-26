r"""Localizations of polynomial algebras and of their quotients.

In ``Z[1/2][x, 1/x]`` both ``2`` and ``x`` are units and ``3`` is not.  On the axes
``A = Q[x, y]/(xy)``, inverting ``x`` kills ``y``, since ``y = (xy)/x = 0`` in
``A_x``.  On the hyperbola ``Q[x, y]/(xy - 1)`` the class of ``x`` is already a
unit with inverse ``y``.  ``Q(x) = Frac Q[x]`` is a field.  The cusp
``Q[x, y]/(x^2 - y^3)`` is a domain of Krull dimension one (it is the image of
``Q[t^2, t^3] -> Q[t]``), so its fraction field is a field and its local ring at
the origin has dimension one.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_inverting_x_over_z_one_half() -> None:
    coefficients = ZZ.localization(ZZ(2))
    polynomials = coefficients["x"]
    x = polynomials.algebra_generator("x")
    laurent = polynomials.localization(x)

    assert laurent(x).is_unit()
    assert laurent(polynomials(2)).is_unit()
    assert not laurent(polynomials(3)).is_unit()
    assert not laurent(x + 1).is_unit()
    assert laurent(x).inverse_of_unit() * laurent(x) == laurent.one()


def test_inverting_x_on_the_axes_makes_x_a_unit() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations([x * y])
    localization = axes.localization(axes.algebra_generator("x"))
    to_localization = localization.localization_map()

    assert to_localization(axes.algebra_generator("x")).is_unit()
    assert not to_localization(axes.algebra_generator("x") + axes.one()).is_unit()


def test_inverting_x_on_the_axes_kills_y() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations([x * y])
    localization = axes.localization(axes.algebra_generator("x"))

    assert localization.localization_map()(axes.algebra_generator("y")) == localization.zero()


def test_x_is_a_unit_on_the_hyperbola_with_inverse_y() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    hyperbola = plane.quotient_by_relations([x * y - 1])
    xbar = hyperbola.algebra_generator("x")
    ybar = hyperbola.algebra_generator("y")

    assert xbar.is_unit()
    assert xbar.inverse_of_unit() == ybar
    assert not (xbar + ybar).is_unit()


def test_the_rational_function_field_in_one_variable() -> None:
    line = QQ["x"]
    x = line.algebra_generator("x")
    functions = line.fraction_field()

    assert functions.is_field()
    assert functions(x).is_unit()
    assert (functions.one() / functions(x)) * functions(x) == functions.one()


def test_the_cusp_is_a_one_dimensional_domain() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    cusp = plane.quotient_by_relations([x**2 - y**3])

    assert cusp.is_integral_domain()
    assert cusp.krull_dimension() == 1
    assert cusp.fraction_field().is_field()
    assert cusp.algebra_generator("x") ** 2 == cusp.algebra_generator("y") ** 3


def test_x_is_a_nonunit_and_x_plus_one_a_unit_at_the_origin_of_the_cusp() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    cusp = plane.quotient_by_relations([x**2 - y**3])
    origin = cusp.ideal(cusp.algebra_generator("x"), cusp.algebra_generator("y"))
    local = cusp.localize_at_prime(origin)

    assert not local(cusp.algebra_generator("x")).is_unit()
    assert local(cusp.algebra_generator("x") + cusp.one()).is_unit()


def test_the_local_ring_of_the_cusp_at_the_origin_has_krull_dimension_one() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    cusp = plane.quotient_by_relations([x**2 - y**3])
    origin = cusp.ideal(cusp.algebra_generator("x"), cusp.algebra_generator("y"))

    assert cusp.localize_at_prime(origin).krull_dimension() == 1
