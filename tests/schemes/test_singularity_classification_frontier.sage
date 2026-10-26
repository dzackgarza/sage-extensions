r"""Right equivalence of plane curve germs, and the regular/smooth boundary."""

from sage_extensions.all import *


def test_a_sheared_a2_becomes_x2_plus_y3_after_x_to_x_plus_y() -> None:
    r"""`(x - y)^2 + y^3` becomes `x^2 + y^3` under `x \mapsto x + y`, so it is right
    equivalent to `A_2` and has Milnor number 2."""
    plane = QQ.polynomial_ring(("x", "y"))
    x, y = plane.algebra_generator("x"), plane.algebra_generator("y")
    sheared = IsolatedHypersurfaceSingularity(plane, (x - y) ** 2 + y**3)
    equivalence = sheared.ade_type_via_linear_right_equivalence(
        {"x": x + y, "y": y},
        {"x": x - y, "y": y},
    )

    assert equivalence.ade_type() == ("A", 2)
    assert equivalence.forward()(sheared.equation()) == x**2 + y**3
    assert sheared.milnor_number() == 2


def test_equal_milnor_and_tjurina_numbers_do_not_classify_plane_curve_germs() -> None:
    r"""`x^2 + y^5` (`A_4`) and `xy(x - y)` (`D_4`) both have `\mu = \tau = 4`, but one
    branch and three branches respectively (Greuel--Lossen--Shustin, I.2.4)."""
    plane = QQ.polynomial_ring(("x", "y"))
    x, y = plane.algebra_generator("x"), plane.algebra_generator("y")
    a4 = IsolatedHypersurfaceSingularity(plane, x**2 + y**5)
    d4 = IsolatedHypersurfaceSingularity(plane, x * y * (x - y))

    assert a4.milnor_number() == d4.milnor_number() == 4
    assert a4.tjurina_number() == d4.tjurina_number() == 4
    assert a4.number_of_branches_at_origin() == 1
    assert d4.number_of_branches_at_origin() == 3


def test_regular_purely_inseparable_field_extension_is_not_smooth_over_its_base() -> None:
    prime_field = GF(2)
    parameters = prime_field.polynomial_ring(("a",))
    a = parameters.algebra_generator("a")
    base = parameters.fraction_field()
    a_in_base = parameters.fraction_field_map()(a)
    line = base.polynomial_ring(("x",))
    x = line.algebra_generator("x")
    extension = (line).quotient_by_relations((x**2 - a_in_base,))

    assert extension.is_field()
    scheme = (extension).affine_spectrum(base_ring=base)
    generic = scheme.underlying_space().generic_point()
    assert scheme.is_regular_at(generic)

    nonsmooth = scheme.singular_subscheme()
    assert nonsmooth.inclusion().codomain() is scheme
    assert nonsmooth.defining_ideal_owned() == extension.ideal(extension.zero())
