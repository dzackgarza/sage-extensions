r"""Affine schemes: spectra, products, fiber products, and fibers of a family."""

from sage_extensions.all import *


def test_global_functions_on_affine_space_are_polynomials_and_on_projective_space_are_constants() -> None:
    r"""\(\Gamma(\mathbf A^2_{\mathbf Q},\mathcal O) = \mathbf Q[x,y]\) and \(\Gamma(\mathbf P^3_{\mathbf Q},\mathcal O) = \mathbf Q\).

    Source: Hartshorne, *Algebraic Geometry*, II.2.3 and II.5.13.
    """
    plane = Schemes(QQ)(QQ["x,y"])
    projective = ProjectiveSpaces(QQ)(3)

    assert plane.structure_sheaf().global_sections() == QQ["x,y"]
    assert projective.structure_sheaf().global_sections() == QQ


def test_the_product_of_two_fat_points_is_the_spectrum_of_the_tensor_product() -> None:
    r"""\(\operatorname{Spec}\mathbf Q[x]/(x^2)\times_{\mathbf Q}\operatorname{Spec}\mathbf Q[y]/(y^3)
    = \operatorname{Spec}\mathbf Q[x,y]/(x^2,y^3)\), in which \(x^2 = 0\), \(y^3 = 0\) and \(xy^2 \ne 0\);
    the projections pull back \(x\) and \(y\) to the generators of the two tensor factors.

    Source: Hartshorne, *Algebraic Geometry*, II.3.3 (fiber products of affine schemes).
    """
    Rx = QQ["x"]
    Ry = QQ["y"]
    left = Schemes(QQ)(Rx.quotient(Rx.ideal(Rx.gen() ** 2)))
    right = Schemes(QQ)(Ry.quotient(Ry.ideal(Ry.gen() ** 3)))

    product = Schemes(QQ).product((left, right))
    first, second = product.projections()
    x = first.coordinate_algebra_morphism()(left.coordinate_algebra().gen())
    y = second.coordinate_algebra_morphism()(right.coordinate_algebra().gen())
    zero = product.coordinate_algebra().zero()

    assert x**2 == zero
    assert y**3 == zero
    assert x * y**2 != zero
    assert y**2 != zero


def test_the_fiber_product_of_x_squared_and_y_cubed_is_the_cusp_with_its_normalization() -> None:
    r"""Over \(\operatorname{Spec}\mathbf Q[s]\), the fiber product of \(s\mapsto x^2\) and \(s\mapsto y^3\)
    is the cusp \(x^2 = y^3\), and the cone \(x\mapsto t^3\), \(y\mapsto t^2\) from \(\mathbf A^1\)
    induces the unique map to it compatible with both projections.

    Source: Hartshorne, *Algebraic Geometry*, II.3.3 (fiber product of affine schemes is Spec of the tensor product).
    """
    common = QQ["s"]
    left_algebra = QQ["x"]
    right_algebra = QQ["y"]
    target_algebra = QQ["t"]
    s = common.gen()
    x = left_algebra.gen()
    y = right_algebra.gen()
    t = target_algebra.gen()

    spec = Algebras(QQ).spectrum()
    left_map = spec(common.Mor(left_algebra)({"s": x**2}))
    right_map = spec(common.Mor(right_algebra)({"s": y**3}))

    pullback = Schemes(QQ).fiber_product(left_map, right_map)
    left_projection, right_projection = pullback.fiber_product_projections()
    left_pullback = left_projection.coordinate_algebra_morphism()
    right_pullback = right_projection.coordinate_algebra_morphism()
    assert left_pullback(x) ** 2 == right_pullback(y) ** 3
    assert left_pullback(x) != right_pullback(y)
    assert (left_map * left_projection).coordinate_algebra_morphism()(s) == (
        right_map * right_projection
    ).coordinate_algebra_morphism()(s)

    target_to_left = spec(left_algebra.Mor(target_algebra)({"x": t**3}))
    target_to_right = spec(right_algebra.Mor(target_algebra)({"y": t**2}))
    induced = pullback.from_pullback_cone(target_to_left, target_to_right)
    assert (left_projection * induced).coordinate_algebra_morphism()(x) == t**3
    assert (right_projection * induced).coordinate_algebra_morphism()(y) == t**2


def test_the_special_fiber_of_xy_equals_t_over_t_zero_is_the_node_xy_equals_zero() -> None:
    r"""The fiber of \(\operatorname{Spec}\mathbf Q[t][x,y]/(xy-t)\to\operatorname{Spec}\mathbf Q[t]\) over \(t = 0\)
    is the fiber product with \(\operatorname{Spec}\mathbf Q[t]/(t)\), namely \(\mathbf Q[x,y]/(xy)\):
    \(xy = 0\) there while \(x \ne 0\) and \(y \ne 0\), and \(t\) pulls back to \(0\).

    Source: Hartshorne, *Algebraic Geometry*, II.3 (the fibre of a morphism over a point).
    """
    parameter = QQ["t"]
    t = parameter.gen()
    family_ring = parameter["x,y"]
    x, y = family_ring.algebra_generator("x"), family_ring.algebra_generator("y")
    family = Schemes(parameter)(family_ring.quotient(family_ring.ideal(x * y - t)))
    zero = Schemes(parameter)(parameter.quotient(parameter.ideal(t)))

    special_fiber = Schemes(parameter).fiber_product(
        family.structure_morphism(),
        zero.structure_morphism(),
    )
    to_family, to_zero = special_fiber.fiber_product_projections()
    special_algebra = special_fiber.coordinate_algebra()
    pull = to_family.coordinate_algebra_morphism()
    x0 = pull(family.coordinate_algebra()(x))
    y0 = pull(family.coordinate_algebra()(y))

    assert x0 * y0 == special_algebra.zero()
    assert x0 != special_algebra.zero()
    assert y0 != special_algebra.zero()
    assert (family.structure_morphism() * to_family).coordinate_algebra_morphism()(t) == special_algebra.zero()
    assert special_fiber.from_pullback_cone(to_family, to_zero) == special_fiber.categorical_identity_morphism()


def test_xy_zero_fiber_has_represented_singular_closed_subscheme() -> None:

    presentation = QQ.polynomial_ring(("x", "y"))
    x = presentation.algebra_generator("x")
    y = presentation.algebra_generator("y")
    special_algebra = (presentation).quotient_by_relations((x * y,))
    special_fiber = (special_algebra).affine_spectrum(base_ring=QQ)
    x0 = special_algebra.algebra_generator("x")
    y0 = special_algebra.algebra_generator("y")

    singular = special_fiber.singular_subscheme()

    assert singular.inclusion().codomain() is special_fiber
    assert singular.defining_ideal_owned() == special_algebra.ideal(x0, y0)
    assert tuple(singular.defining_equations()) == (y0, x0)
    assert singular.coordinate_algebra().krull_dimension() == 0
    assert special_fiber.relative_differentials().fitting_ideal(1) == (
        special_algebra.ideal(x0, y0)
    )


def test_xy_equals_t_family_is_flat_with_relative_nonsmooth_node() -> None:
    from pytest import raises


    parameter = QQ.polynomial_ring("t")
    t = parameter.algebra_generator("t")
    presentation = parameter.polynomial_ring(("x", "y"))
    x = presentation.algebra_generator("x")
    y = presentation.algebra_generator("y")
    family_algebra = (presentation).quotient_by_relations((x * y - t,))
    family = (family_algebra).affine_spectrum(base_ring=parameter)
    xbar = family_algebra.algebra_generator("x")
    ybar = family_algebra.algebra_generator("y")

    assert family.is_flat()
    nonsmooth = family.relative_nonsmooth_subscheme()
    assert nonsmooth.inclusion().codomain() is family
    assert nonsmooth.defining_ideal_owned() == family_algebra.ideal(xbar, ybar)
    assert family.relative_differentials().fitting_ideal(1) == family_algebra.ideal(
        xbar,
        ybar,
    )
    nonsmooth_algebra = nonsmooth.coordinate_algebra()
    assert nonsmooth_algebra.algebra_structure_morphism()(t) == nonsmooth_algebra.zero()

    killed_presentation = parameter.polynomial_ring(("z", "w"))
    nonflat_algebra = (killed_presentation).quotient_by_relations((t,))
    nonflat = (nonflat_algebra).affine_spectrum(base_ring=parameter)
    assert not nonflat.is_flat()
    with raises(AssertionError):
        nonflat.relative_nonsmooth_subscheme()


