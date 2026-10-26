r"""Base change of affine schemes along a ring map: ``Spec A x_{Spec R} Spec R' = Spec(A tensor_R R')``.

Source: Hartshorne, *Algebraic Geometry*, Theorem II.3.3 (fibred products exist, and
for affine schemes ``Spec A x_{Spec R} Spec B = Spec(A tensor_R B)``).  Hence
``Spec ZZ x_{Spec ZZ} Spec QQ = Spec QQ``, ``A^1_QQ x Spec K = A^1_K``, and for
``K = QQ(sqrt 2)`` the point ``Spec QQ[x]/(x^2 - 2)`` becomes
``Spec K[x]/((x - sqrt 2)(x + sqrt 2)) = Spec K x Spec K``, two rational points.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _to_quadratic_field():
    field = QuadraticField(2, "s")
    return field, QQ.Mor(field)(lambda element: field(element))


def test_the_generic_point_of_spec_zz_is_spec_qq() -> None:
    r"""``Spec ZZ x_{Spec ZZ} Spec QQ = Spec(ZZ tensor_ZZ QQ) = Spec QQ``: a point over ``QQ``.

    The object and the functor spelling agree, and the result is a fibre product over ``QQ``.
    """
    to_rationals = ZZ.Mor(QQ)(lambda element: QQ(element))
    integers = ZZ.affine_spectrum()
    change = Schemes(ZZ).base_change_functor(to_rationals)
    generic = change(integers)

    assert integers.base_change(to_rationals) is generic
    assert generic in FiberProductSchemes(QQ)
    assert generic.scheme_base_ring() is QQ
    assert generic.coordinate_algebra() is QQ
    assert generic.dimension() == 0
    assert change.base_morphism().domain() is QQ.affine_spectrum()


def test_the_base_change_square_of_spec_zz_along_spec_qq_commutes() -> None:
    r"""``X_QQ -> Spec ZZ -> Spec ZZ`` equals ``X_QQ -> Spec QQ -> Spec ZZ``, and ``X_QQ -> Spec QQ`` is an isomorphism."""
    to_rationals = ZZ.Mor(QQ)(lambda element: QQ(element))
    integers = ZZ.affine_spectrum()
    change = Schemes(ZZ).base_change_functor(to_rationals)
    generic = change(integers)

    assert integers.structure_morphism() * generic.left_projection() == change.base_morphism() * generic.right_projection()
    assert generic.right_projection().is_isomorphism()


def test_base_change_sends_the_identity_to_the_identity() -> None:
    r"""A functor preserves identities: ``(id_{Spec ZZ})_QQ = id``."""
    to_rationals = ZZ.Mor(QQ)(lambda element: QQ(element))
    integers = ZZ.affine_spectrum()
    change = Schemes(ZZ).base_change_functor(to_rationals)
    generic = change(integers)

    assert change(integers.Mor(integers).identity()) == generic.Mor(generic).identity()


def test_the_affine_line_over_qq_becomes_the_affine_line_over_a_quadratic_field() -> None:
    r"""``A^1_QQ x_QQ K = Spec K[x]``: a line over ``K``, whose first projection sends ``x`` to ``x``."""
    field, ring_map = _to_quadratic_field()
    ring = QQ.polynomial_ring("x")
    line = ring.affine_spectrum()
    changed = line.base_change(ring_map)
    x = changed.coordinate_algebra().algebra_generator("x")

    assert changed.scheme_base_ring() is field
    assert changed.dimension() == 1
    assert changed.left_projection().coordinate_algebra_morphism()(ring.algebra_generator("x")) == x


def test_x_squared_minus_two_splits_into_two_rational_points_over_qq_sqrt_2() -> None:
    r"""``V(x^2 - 2)`` is one closed point of degree 2 over ``QQ`` and two rational points over ``QQ(sqrt 2)``."""
    field, ring_map = _to_quadratic_field()
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    point = ring.affine_spectrum().closed_subscheme(x**2 - 2)
    changed = point.base_change(ring_map)

    assert point.irreducible_components().cardinality() == 1
    assert changed.irreducible_components().cardinality() == 2
    assert changed.degree() == 2
