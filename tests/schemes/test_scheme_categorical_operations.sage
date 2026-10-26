r"""Diagonals, graphs, fixed loci, equalizers, inverse images and scheme-theoretic images
of morphisms of affine schemes over QQ."""

from sage_extensions.all import *


def _plane():
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    algebra = plane.coordinate_ring()
    return plane, algebra, algebra.algebra_generator("x"), algebra.algebra_generator("y")


def _cusp_parametrization():
    r"""`t \mapsto (t^2, t^3)`, whose image is the cuspidal cubic `y^2 = x^3`."""
    plane, algebra, x, y = _plane()
    line_ring = QQ.polynomial_ring("t")
    t = line_ring.algebra_generator("t")
    line = line_ring.affine_spectrum()
    return plane, x, y, line, t, line.Mor(plane)(algebra.Mor(line_ring)({"x": t**2, "y": t**3}))


def test_the_diagonal_is_a_codimension_two_section_of_both_projections() -> None:
    plane, _algebra, _x, _y = _plane()
    product = Schemes(QQ).product((plane, plane))
    diagonal = plane.diagonal_morphism()
    identity = plane.Mor(plane).identity()
    image = plane.diagonal_subscheme()

    assert product.projection(0) * diagonal == identity
    assert product.projection(1) * diagonal == identity
    assert image.codimension() == 2
    assert image.relative_dimension() == 2
    assert image.inclusion() * image.corestriction(diagonal) == diagonal


def test_the_graph_of_the_cusp_parametrization_is_a_curve_of_codimension_two() -> None:
    plane, _x, _y, line, _t, parametrization = _cusp_parametrization()
    product = Schemes(QQ).product((line, plane))
    graph = parametrization.graph_morphism()
    image = parametrization.graph_subscheme()

    assert product.projection(0) * graph == line.Mor(line).identity()
    assert product.projection(1) * graph == parametrization
    assert image.relative_dimension() == 1
    assert image.codimension() == 2
    assert image.inclusion() * image.corestriction(graph) == graph


def test_fixed_loci_of_the_swap_and_the_reflection_and_their_equalizer() -> None:
    r"""The swap fixes `V(x - y)`, the reflection `y \mapsto -y` fixes `V(y)`, and the
    equalizer of the two is `V(x - y, x + y)`, the origin."""
    plane, algebra, x, y = _plane()
    swap = plane.Mor(plane)(algebra.Mor(algebra)({"x": y, "y": x}))
    reflect = plane.Mor(plane)(algebra.Mor(algebra)({"x": x, "y": -y}))
    equalizer = Schemes(QQ).equalizer(swap, reflect)

    assert swap.fixed_subscheme().defining_ideal() == algebra.ideal(x - y)
    assert reflect.fixed_subscheme().defining_ideal() == algebra.ideal(y)
    assert equalizer.defining_ideal() == algebra.ideal(x - y, x + y)
    assert equalizer.relative_dimension() == 0
    assert swap * equalizer.inclusion() == reflect * equalizer.inclusion()


def test_the_inverse_image_of_the_origin_under_the_cusp_parametrization_has_length_two() -> None:
    r"""`f^{-1}(0) = V(t^2, t^3) = V(t^2)`, of length 2; `f^{-1}(V(y^2 - x^3))` is all of
    `\mathbb{A}^1` since `t^6 - t^6 = 0`."""
    plane, x, y, line, t, parametrization = _cusp_parametrization()
    line_ring = line.coordinate_ring()
    preimage = parametrization.inverse_image(plane.closed_subscheme(x, y))
    whole = parametrization.inverse_image(plane.closed_subscheme(y**2 - x**3))

    assert preimage.defining_ideal() == line_ring.ideal(t**2)
    assert preimage.coordinate_ring().dimension() == 2
    assert whole.defining_ideal() == line_ring.ideal(line_ring.zero())


def test_the_scheme_theoretic_image_of_the_cusp_parametrization_is_the_cuspidal_cubic() -> None:
    r"""The kernel of `\mathbb{Q}[x, y] \to \mathbb{Q}[t]`, `x \mapsto t^2`, `y \mapsto t^3`,
    is `(y^2 - x^3)`; the map is not a closed immersion because `t` is not in the image
    `\mathbb{Q}[t^2, t^3]`."""
    plane, x, y, _line, _t, parametrization = _cusp_parametrization()
    image = parametrization.scheme_theoretic_image()

    assert image.defining_ideal() == plane.coordinate_ring().ideal(y**2 - x**3)
    assert image.relative_dimension() == 1
    assert image.inclusion() * image.corestriction(parametrization) == parametrization
    assert not parametrization.is_closed_immersion()
