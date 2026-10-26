r"""Projective complete intersections: adjunction, normality, and del Pezzo surfaces.

For a complete intersection \(X\subset\mathbf P^n\) of degrees \(d_1,\dots,d_c\),
\(\omega_X = \mathcal O_X(\sum d_i - n - 1)\) (Hartshorne, *Algebraic Geometry*, Exercise II.8.4).
"""

from sage_extensions.all import *


def _p3():
    space = ProjectiveSpaces(QQ)(3)
    return space, space.homogeneous_coordinate_generators()


def _quadric_cubic_curve():
    space, (x0, x1, x2, x3) = _p3()
    return space.closed_subscheme(x0 * x1 - x2**2, x0**3 + x1**3 + x3**3)


def _fermat_cubic_surface():
    space, (x0, x1, x2, x3) = _p3()
    return space.closed_subscheme(x0**3 + x1**3 + x2**3 + x3**3)


def test_the_quadric_cubic_complete_intersection_curve_in_p3_has_canonical_bundle_o_one() -> None:
    r"""\(C = V(x_0x_1-x_2^2,\ x_0^3+x_1^3+x_3^3)\subset\mathbf P^3\): codimension \(2\), dimension \(1\),
    \(\omega_C = \mathcal O_C(2+3-4) = \mathcal O_C(1)\), and \(C\) is Gorenstein.

    Source: Hartshorne, Exercise II.8.4.
    """
    curve = _quadric_cubic_curve()

    assert tuple(curve.defining_degrees()) == (2, 3)
    assert all(degree.parent() is ZZ for degree in curve.defining_degrees())
    assert curve.complete_intersection_codimension() == 2
    assert curve.dimension() == 1
    assert curve.adjunction_twist_degree() == 1
    assert curve.adjunction_twist_degree().parent() is ZZ
    assert curve.is_gorenstein()


def test_adjunction_on_the_quadric_cubic_curve_reads_minus_four_plus_five_equals_one() -> None:
    r"""\(\omega_{\mathbf P^3}|_C = \mathcal O_C(-4)\), \(\det N_{C/\mathbf P^3} = \mathcal O_C(2)\otimes\mathcal O_C(3) = \mathcal O_C(5)\),
    and \(\omega_C \cong \omega_{\mathbf P^3}|_C\otimes\det N = \mathcal O_C(1)\).

    Source: Hartshorne, Proposition II.8.20 and Exercise II.8.4.
    """
    curve = _quadric_cubic_curve()
    isomorphism = curve.adjunction_isomorphism()

    assert curve.restricted_ambient_canonical_bundle().degree() == -4
    assert curve.normal_determinant_line_bundle().degree() == 5
    assert curve.canonical_line_bundle().degree() == 1
    assert isomorphism.domain() is curve.canonical_line_bundle()
    assert isomorphism.codomain() is curve.adjunction_target()
    assert isomorphism.inverse() * isomorphism == curve.canonical_line_bundle().Mor(curve.canonical_line_bundle()).identity()


def test_the_fermat_cubic_surface_is_a_del_pezzo_surface_of_degree_three() -> None:
    r"""The Fermat cubic surface is smooth with \(-K = \mathcal O(4-3) = \mathcal O(1)\), ample, and
    \(K^2 = \deg X = 3\).

    Source: Hartshorne, Exercise II.8.4; Dolgachev, *Classical Algebraic Geometry*, §8.1.
    """
    cubic = _fermat_cubic_surface()
    anticanonical = cubic.anticanonical_line_bundle()

    assert cubic.dimension() == 2
    assert cubic.is_smooth()
    assert cubic.projective_degree() == 3
    assert cubic.projective_degree().parent() is ZZ
    assert anticanonical.degree() == 1
    assert anticanonical.is_ample()
    assert cubic.is_del_pezzo()
    assert DelPezzoSurfaces(cubic.scheme_base_ring())(cubic).del_pezzo_degree() == 3
    assert DelPezzoSurfaces(cubic.scheme_base_ring())(cubic).del_pezzo_degree().parent() is ZZ


def test_the_fermat_quartic_surface_has_trivial_canonical_class_and_is_not_del_pezzo() -> None:
    r"""A quartic surface in \(\mathbf P^3\) has \(\omega = \mathcal O(4-4) = \mathcal O\), so \(-K\) is not ample.

    Source: Hartshorne, Exercise II.8.4; Example V.1.4.4 (quartic surfaces are K3).
    """
    space, (x0, x1, x2, x3) = _p3()
    quartic = space.closed_subscheme(x0**4 + x1**4 + x2**4 + x3**4)

    assert quartic.dimension() == 2
    assert quartic.adjunction_twist_degree() == 0
    assert quartic.anticanonical_twist_degree() == 0
    assert not quartic.is_del_pezzo()


def test_the_quadric_cone_is_normal_and_gorenstein_but_not_smooth() -> None:
    r"""\(V(x_0x_1 - x_2^2)\subset\mathbf P^3\) is singular at its vertex \((0:0:0:1)\), a point of codimension \(2\);
    as a hypersurface it is \(S_2\) and Gorenstein, so by Serre's criterion it is normal.

    Source: Hartshorne, Proposition II.8.23 (Serre's criterion); Matsumura, *Commutative Ring Theory*, Thm. 23.8.
    """
    space, (x0, x1, x2, _x3) = _p3()
    cone = space.closed_subscheme(x0 * x1 - x2**2)

    assert not cone.is_smooth()
    assert cone.is_normal()
    assert cone.is_gorenstein()


def test_the_cuspidal_plane_cubic_is_gorenstein_but_not_normal() -> None:
    r"""\(V(y^2z - x^3)\subset\mathbf P^2\) has a cusp at \((0:0:1)\); a singular curve is not normal,
    while every plane curve is Gorenstein.

    Source: Hartshorne, Theorem I.6.2A (a one-dimensional noetherian local domain is normal iff regular).
    """
    plane = ProjectiveSpaces(QQ)(2)
    x, y, z = plane.homogeneous_coordinate_generators()
    cusp = plane.closed_subscheme(y**2 * z - x**3)

    assert not cusp.is_smooth()
    assert not cusp.is_normal()
    assert cusp.is_gorenstein()


def test_two_quadrics_in_p4_meet_in_a_gorenstein_del_pezzo_surface_of_degree_four_with_a1_points() -> None:
    r"""\(S = V(BD - AE,\ C^2 - AE)\subset\mathbf P^4\) is a surface of degree \(4\) with
    \(-K_S = \mathcal O_S(5 - 2 - 2) = \mathcal O_S(1)\), ample.  It is singular at \((0:0:0:0:1)\), where on
    \(E = 1\) it is \(C^2 = BD\), an \(A_1\) point; so \(S\) is a Gorenstein del Pezzo surface of degree \(4\).

    Source: Hartshorne, Exercise II.8.4; Hidaka--Watanabe, *Normal Gorenstein surfaces with ample
    anti-canonical divisor*, Tokyo J. Math. 4 (1981).
    Derivation of the singular point: the differentials of the two quadrics there are both \(-dA\).
    """
    space = ProjectiveSpaces(QQ)(4, names=("A", "B", "C", "D", "E"))
    A, B, C, D, E = space.homogeneous_coordinate_generators()
    surface = space.closed_subscheme(B * D - A * E, C**2 - A * E)
    anticanonical = surface.anticanonical_line_bundle()

    assert tuple(surface.defining_degrees()) == (2, 2)
    assert surface.dimension() == 2
    assert surface in ProperSurfaces(QQ)
    assert surface in ProjectiveSurfaces(QQ)
    assert surface.projective_degree() == 4
    assert surface.is_gorenstein()
    assert not surface.is_smooth()
    assert anticanonical.degree() == 1
    assert anticanonical.is_ample()
    assert surface.is_gorenstein_del_pezzo()
    assert not surface.is_del_pezzo()
    assert surface.del_pezzo_degree() == 4
