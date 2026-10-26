r"""Fibres of ``Spec ZZ[i] -> Spec ZZ``, base change of ``P^1``, and pullback of families along ``x -> x^2``.

Sources and derivations.  Hartshorne, *Algebraic Geometry*, II.3 (the fibre of
``f: X -> Y`` over ``y`` is ``X x_Y Spec k(y)``, and Theorem II.3.3,
``Spec A x_{Spec R} Spec B = Spec(A tensor_R B)``).  For ``X = Spec ZZ[x]/(x^2 + 1)``:
the generic fibre is ``Spec QQ(i)``, a point of degree 2 over ``QQ``; the fibre over
``(5)`` is ``Spec F_5[x]/((x - 2)(x + 2))``, two rational points; over ``(3)`` it is
``Spec F_9``, one point of degree 2; over ``(2)`` it is ``Spec F_2[x]/((x + 1)^2)``, one
point that is not reduced.  ``P^n_QQ x_QQ Spec K = P^n_K``.  For ``g: S' -> S`` the functor
``Sigma_g`` (compose with ``g``) is left adjoint to ``g^*`` (pull back along ``g``); this
is the universal property of the fibre product read in the two slices, and the unit
and counit satisfy the triangle identity ``counit_{Sigma X} o Sigma(unit_X) = id``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _gaussian_integers():
    ring = ZZ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    return ring.affine_spectrum().closed_subscheme(x**2 + ring.one())


def test_the_generic_fibre_of_the_gaussian_integers_is_one_point_of_degree_two() -> None:
    r"""``Spec ZZ[i] x_ZZ Spec QQ = Spec QQ(i)``: one point, degree 2 over ``QQ``."""
    generic = SchemesOverIntegralDomains(ZZ)(_gaussian_integers()).generic_fiber()

    assert generic.scheme_base_ring() is QQ
    assert generic.dimension() == 0
    assert generic.degree() == 2
    assert generic.irreducible_components().cardinality() == 1


def test_five_splits_three_is_inert_and_two_ramifies_in_the_gaussian_integers() -> None:
    r"""The fibres over ``(5)``, ``(3)``, ``(2)`` have 2, 1, 1 points, all of total degree 2; only the last is non-reduced."""
    gaussian = _gaussian_integers()
    over_five = gaussian.fiber_over_ideal(ZZ.ideal(5))
    over_three = gaussian.fiber_over_ideal(ZZ.ideal(3))
    over_two = gaussian.fiber_over_ideal(ZZ.ideal(2))

    assert over_five.irreducible_components().cardinality() == 2
    assert over_three.irreducible_components().cardinality() == 1
    assert over_two.irreducible_components().cardinality() == 1
    assert over_five.degree() == 2 and over_three.degree() == 2 and over_two.degree() == 2
    assert over_five.is_reduced() and over_three.is_reduced()
    assert not over_two.is_reduced()


def test_the_projective_line_over_qq_becomes_the_projective_line_over_qq_sqrt_2() -> None:
    r"""``P^1_QQ x_QQ Spec QQ(sqrt 2) = P^1_{QQ(sqrt 2)}``, with its projection back to ``P^1_QQ``."""
    field = QuadraticField(2, "s")
    ring_map = QQ.Mor(field)(lambda element: field(element))
    line = ProjectiveSpaces(QQ)(1)
    changed = line.base_change(ring_map)

    assert changed.scheme_base_ring() is field
    assert changed.is_isomorphic(ProjectiveSpaces(field)(1))
    assert changed.left_projection().codomain() is line


def test_pulling_back_the_point_one_along_squaring_gives_two_points() -> None:
    r"""``g: A^1 -> A^1``, ``t -> t^2``: ``g^*(V(x - 1)) = V(t^2 - 1)``, two points, and the counit is its projection."""
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    squaring = line.Mor(line)(ring.Mor(ring)({"x": x**2}))
    adjunction = squaring.slice_base_change_adjunction()
    family = line.scheme_category().SliceOver(line)(line.closed_subscheme(x - ring.one()).inclusion())

    pulled_back = adjunction.right_adjoint()(family)

    assert pulled_back.arrow().codomain() is line
    assert pulled_back.arrow().domain().degree() == 2
    assert adjunction.counit(family).domain() == adjunction.left_adjoint()(pulled_back)


def test_the_composition_pullback_adjunction_satisfies_a_triangle_identity() -> None:
    r"""``counit_{Sigma X} o Sigma(unit_X) = id_{Sigma X}`` for ``X = (A^1 --id--> A^1)`` and ``g: t -> t^2``."""
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    squaring = line.Mor(line)(ring.Mor(ring)({"x": x**2}))
    adjunction = squaring.slice_base_change_adjunction()
    family = line.scheme_category().SliceOver(line)(line.Mor(line).identity())
    composed = adjunction.left_adjoint()(family)

    triangle = adjunction.counit(composed) * adjunction.left_adjoint()(adjunction.unit(family))

    assert triangle == composed.parent().Mor(composed, composed).identity()
