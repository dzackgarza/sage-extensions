r"""Limits of affine lines over ``Q``: products, equalizers and fibre products, with their
universal properties, and the standard properties of the affine line.

Each limit of affine schemes is ``Spec`` of the corresponding colimit of coordinate rings:
``A^1 x A^1 = Spec Q[s] (x) Q[t]``; the equalizer of ``s -> s^2`` and the identity is
``Spec Q[s]/(s^2 - s)``, two reduced points; the fibre product of ``s -> s^2`` with itself is
``Spec Q[a, b]/(a^2 - b^2)``, the two lines ``a = ±b``.  ``Q[x_1, ..., x_n]`` is a unique
factorization domain, so ``A^n`` is normal with ``Cl = 0`` (Hartshorne, *Algebraic Geometry*,
Prop. II.6.2, checked).
"""

from sage_extensions.all import *


def _line(name):
    ring = QQ[name]
    return ring, ring.algebra_generator(name), AffineSchemes(QQ)(ring)


def test_a_pair_of_maps_into_two_lines_factors_uniquely_through_their_product() -> None:
    r"""``u -> (u^2, u^3)``: the cone map composed with each projection recovers each leg."""
    s_ring, s, first = _line("s")
    t_ring, t, second = _line("t")
    u_ring, u, source = _line("u")
    product = Schemes(QQ).product((first, second))
    to_first, to_second = product.projections()
    left = source.Mor(first)(s_ring.Mor(u_ring)({"s": u**2}))
    right = source.Mor(second)(t_ring.Mor(u_ring)({"t": u**3}))

    induced = product.from_product_cone((left, right))

    assert to_first * induced == left
    assert to_second * induced == right
    assert product.projection_label(to_second) == 1
    assert product.dimension() == 2
    assert first.product_with(second) in ProductSchemes(QQ)
    assert product.number_of_factors() == 2


def test_the_fixed_points_of_squaring_are_zero_and_one() -> None:
    r"""The equalizer of ``s -> s^2`` and ``id`` is ``V(s^2 - s)``: zero-dimensional, with
    ``s^2 = s`` while ``s`` is neither ``0`` nor ``1``."""
    s_ring, s, line = _line("s")
    square = line.Mor(line)(s_ring.Mor(s_ring)({"s": s**2}))

    fixed = Schemes(QQ).equalizer(square, line.categorical_identity_morphism())
    restrict = fixed.inclusion().coordinate_algebra_morphism()
    algebra = fixed.coordinate_algebra()

    assert fixed.dimension() == 0
    assert restrict(s) ** 2 == restrict(s)
    assert restrict(s) != algebra.zero()
    assert restrict(s) != algebra.one()


def test_the_fibre_product_of_squaring_with_itself_is_a_pair_of_lines() -> None:
    r"""``A^1 x_{A^1} A^1`` along ``s -> s^2`` twice: one-dimensional with ``a^2 = b^2`` and
    ``a != ±b``; the square commutes, and the cone ``(id, id)`` factors through it."""
    s_ring, s, line = _line("s")
    square = line.Mor(line)(s_ring.Mor(s_ring)({"s": s**2}))
    identity = line.categorical_identity_morphism()

    pullback = Schemes(QQ).fiber_product(square, square)
    left, right = pullback.fiber_product_projections()
    a = left.coordinate_algebra_morphism()(s)
    b = right.coordinate_algebra_morphism()(s)
    induced = pullback.from_pullback_cone(identity, identity)

    assert pullback.fiber_product_base() is line
    assert pullback.dimension() == 1
    assert square * left == square * right
    assert a**2 == b**2
    assert a != b
    assert a != -b
    assert pullback.left_projection() == left
    assert left * induced == identity
    assert right * induced == identity


def test_the_affine_line_is_separated_integral_of_finite_type_and_quasi_affine() -> None:
    r"""``Q[s]`` is a finitely generated domain; an affine scheme is separated and quasi-affine."""
    s_ring, s, line = _line("s")

    assert line.is_separated()
    assert line.is_integral()
    assert line.is_finite_type()
    assert line.is_quasi_affine()
    assert line.structure_morphism().codomain() is line.base_scheme()


def test_the_affine_line_is_normal() -> None:
    r"""``Q[s]`` is a principal ideal domain, hence integrally closed."""
    s_ring, s, line = _line("s")

    assert line.is_normal()


def test_the_affine_plane_has_trivial_picard_and_class_groups() -> None:
    r"""``Cl(A^2) = 0`` since ``Q[x, y]`` is a UFD (Prop. II.6.2), and ``Pic`` injects into ``Cl``."""
    plane = AffineSpaces(QQ)(2)

    assert plane.class_group().module_rank() == 0
    assert plane.picard_group().module_rank() == 0


def test_affine_space_takes_named_coordinates() -> None:
    r"""``A^2`` with coordinates ``a, b`` has coordinate ring ``Q[a, b]``; ``D(a)`` inverts ``a``."""
    plane = AffineSpaces(QQ)(2, names=("a", "b"))
    ring = plane.coordinate_algebra()
    a = ring.algebra_generator("a")

    assert ring == QQ["a,b"]
    assert plane.basic_open(a).inclusion().coordinate_algebra_morphism()(a).is_unit()
    assert plane.relative_dimension() == 2
