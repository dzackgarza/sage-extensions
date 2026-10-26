r"""Kähler differentials and the algebraic de Rham complex of small algebras over ``QQ``."""

from sage_extensions.all import *  # noqa: F401,F403


def _axes():
    r"""The coordinate axes ``A = QQ[x, y]/(xy)``."""
    plane = QQ["x,y"]
    x, y = plane.algebra_generator("x"), plane.algebra_generator("y")
    axes = plane.quotient(plane.ideal([x * y]))
    return axes, axes(x), axes(y)


def test_exterior_algebra_of_the_integer_plane_is_alternating() -> None:
    r"""In ``Λ(ZZ^2)``: ``e^2 = 0``, ``ef = -fe``, ``ef ≠ 0`` and ``Λ^3 = 0``."""
    exterior = Modules(ZZ).free_module(("e", "f")).exterior_algebra()
    e = exterior.algebra_generator("e")
    f = exterior.algebra_generator("f")

    assert e * e == exterior.zero()
    assert e * f == -(f * e)
    assert e * f != exterior.zero()
    assert exterior.graded_piece(2).module_rank() == 1
    assert exterior.graded_piece(3).module_rank() == 0


def test_differentials_of_the_axes_satisfy_y_dx_plus_x_dy_equals_zero() -> None:
    r"""``Ω_A = (A dx ⊕ A dy)/(y dx + x dy)`` for ``A = QQ[x,y]/(xy)``, and a
    derivation ``D`` factors uniquely through ``d`` as ``φ_D ∘ d``
    (the universal property of Kähler differentials)."""
    axes, x, y = _axes()
    omega = axes.kahler_differentials()
    d = omega.universal_derivation()
    dx, dy = d(x), d(y)

    assert y * dx + x * dy == omega.zero()
    assert d(x * y) == omega.zero()
    assert dx != omega.zero()
    assert x * dx != omega.zero()

    derivation = axes.derivations()({x: x, y: -y})
    classifier = omega.from_derivation(derivation)
    for element in (x + y, x**2, x**3 + 2 * y**2):
        assert classifier(d(element)) == derivation(element)
    assert derivation(x**2) == 2 * x**2


def test_relative_differentials_of_the_node_degeneration_xy_equals_t() -> None:
    r"""For ``A = QQ[t][x,y]/(xy - t)``: the conormal map sends the relation to
    ``y dx + x dy``, ``Fitt_1(Ω_{A/QQ[t]}) = (x, y)``, and the cotangent space
    has dimension 2 at the node ``(x, y)`` and 1 at ``(x - 1, y)``.

    Derivation: ``Ω`` has the 1×2 presentation matrix ``(y  x)``."""
    base = QQ["t"]
    t = base.gen()
    presentation = base["x,y"]
    x, y = presentation.algebra_generator("x"), presentation.algebra_generator("y")
    algebra = presentation.quotient(presentation.ideal([x * y - t]))
    xbar, ybar = algebra(x), algebra(y)
    omega = algebra.kahler_differentials()
    conormal_map = omega.conormal_morphism()
    relation = conormal_map.domain().module_generator(0)
    ambient = conormal_map.codomain()

    assert conormal_map(relation) == ybar * ambient.module_generator(0) + xbar * ambient.module_generator(1)
    assert omega.fitting_ideal(1) == algebra.ideal([xbar, ybar])

    spectrum = algebra.spectrum()
    node = spectrum(algebra.ideal([xbar, ybar]))
    smooth_point = spectrum(algebra.ideal([xbar - 1, ybar]))
    assert omega.cotangent_space(node).dimension() == 2
    assert omega.cotangent_space(smooth_point).dimension() == 1


def test_de_rham_complex_of_the_plane_has_square_zero_leibniz_differential() -> None:
    r"""On ``Ω^•(QQ[x,y])``: ``d^2 = 0``, ``d(XY) = dX Y + X dY``, ``dX ∧ dX = 0``,
    ``dX ∧ dY ≠ 0``, and ``d(x^2 y) = 2xy dx + x^2 dy``."""
    algebra = QQ["x,y"]
    x, y = algebra.algebra_generator("x"), algebra.algebra_generator("y")
    de_rham = algebra.de_rham_algebra()
    d = de_rham.differential()
    X, Y = de_rham(x), de_rham(y)

    assert d(d(X)) == de_rham.zero()
    assert d(X * Y) == d(X) * Y + X * d(Y)
    assert d(X) * d(X) == de_rham.zero()
    assert d(X) * d(Y) != de_rham.zero()
    assert d(de_rham(x**2 * y)) == 2 * X * Y * d(X) + X * X * d(Y)


def test_de_rham_differential_descends_through_the_axes() -> None:
    r"""On ``QQ[x,y]/(xy)``, ``XY = 0`` and so ``dX Y + X dY = d(XY) = 0``."""
    axes, x, y = _axes()
    de_rham = axes.de_rham_algebra()
    d = de_rham.differential()
    X, Y = de_rham(x), de_rham(y)

    assert X * Y == de_rham.zero()
    assert d(X) * Y + X * d(Y) == de_rham.zero()
    assert d(X) * Y != de_rham.zero()


def test_de_rham_cohomology_of_the_rational_dual_numbers() -> None:
    r"""For ``A = QQ[x]/(x^2)``: ``2x dx = d(x^2) = 0`` so ``Ω = QQ dx``; ``d`` is
    onto ``Ω``, giving ``H^0 = QQ`` and ``H^1 = 0``."""
    polynomials = QQ["x"]
    x = polynomials.gen()
    dual_numbers = polynomials.quotient(polynomials.ideal([x**2]))
    xbar = dual_numbers(x)
    omega = dual_numbers.kahler_differentials()
    dx = omega.universal_derivation()(xbar)

    assert xbar * dx == omega.zero()
    assert dx != omega.zero()
    de_rham = dual_numbers.de_rham_algebra()
    assert de_rham.cohomology(0).module_rank() == 1
    assert de_rham.cohomology(1).module_rank() == 0


def test_differentials_of_the_axes_localized_at_x() -> None:
    r"""On ``D(x) ⊂ Spec QQ[x,y]/(xy)``: ``y = 0``, so ``dy = 0``;
    ``d(1/x) = -dx/x^2``; and ``Fitt_1(Ω) = (x, y)`` becomes the unit ideal."""
    axes, x, y = _axes()
    localized = axes.localization(x)
    omega = localized.kahler_differentials()
    d = omega.universal_derivation()
    inverse_x = localized.one() / localized(x)

    assert d(localized(y)) == omega.zero()
    assert d(inverse_x) == -(inverse_x * inverse_x) * d(localized(x))
    assert d(localized(x) * inverse_x) == omega.zero()
    assert localized.one() in omega.fitting_ideal(1)


def test_de_rham_functor_sends_x_to_t_squared_and_dx_to_2t_dt() -> None:
    r"""``Ω^•`` is a functor: ``φ : x ↦ t^2`` induces ``x ↦ t^2``, ``dx ↦ 2t dt``."""
    source, target = QQ["x"], QQ["t"]
    x, t = source.gen(), target.gen()
    morphism = source.Mor(target)({x: t**2})
    de_rham = Algebras(QQ).Commutative().de_rham()
    source_dr, target_dr = de_rham(source), de_rham(target)
    mapped = de_rham(morphism)
    T = target_dr(t)

    assert mapped(source_dr(x)) == T * T
    assert mapped(source_dr.differential()(source_dr(x))) == 2 * T * target_dr.differential()(T)


def test_de_rham_is_left_adjoint_to_the_degree_zero_algebra() -> None:
    r"""``Hom_DGA(Ω^•_A, B) ≅ Hom_Alg(A, B^0)``: the bijection round-trips on
    ``x ↦ t^2`` and both triangle identities hold."""
    source, degree_zero = QQ["x"], QQ["t"]
    x, t = source.gen(), degree_zero.gen()
    adjunction = Algebras(QQ).Commutative().de_rham_adjunction()
    target = adjunction.left_adjoint()(degree_zero)
    source_dr = adjunction.left_adjoint()(source)
    algebra_map = source.Mor(degree_zero)({x: t**2})

    transpose = adjunction.mor_set_isomorphism_inverse(algebra_map, codomain=target)
    recovered = adjunction.mor_set_isomorphism_forward(transpose, source)
    X = source_dr(x)
    assert recovered(x) == t**2
    assert transpose(source_dr.differential()(X)) == target.differential()(target(t**2))

    left_triangle = adjunction.counit(source_dr) * adjunction.left_adjoint()(adjunction.unit(source))
    assert left_triangle(X) == X
    assert left_triangle(source_dr.differential()(X)) == source_dr.differential()(X)
    right_triangle = adjunction.right_adjoint()(adjunction.counit(target)) * adjunction.unit(degree_zero)
    assert right_triangle(t) == t
