r"""Families of projective complete intersections over \(\mathbf Q[t]\) and their fibres."""

from sage_extensions.all import *


def _plane_over_the_parameter_line():
    parameter = QQ["t"]
    plane = ProjectiveSpaces(parameter)(2, names=("x", "y", "z"))
    ring = plane.homogeneous_coordinate_ring()
    x, y, z = plane.homogeneous_coordinate_generators()
    return parameter, plane, ring(parameter.gen()), x, y, z


def _hesse_family():
    parameter, plane, t, x, y, z = _plane_over_the_parameter_line()
    return parameter, plane.closed_subscheme(x**3 + y**3 + z**3 - 3 * t * x * y * z)


def test_the_hesse_cubic_family_has_relative_dimension_one_and_trivial_canonical_twist() -> None:
    r"""A plane cubic \(C\subset\mathbf P^2\) is a curve with \(\omega_C = \mathcal O_C(3-3) = \mathcal O_C\).

    Source: Hartshorne, *Algebraic Geometry*, II.8.20 and Example II.8.20.3 (adjunction for plane curves).
    """
    _parameter, family = _hesse_family()

    assert tuple(family.defining_degrees()) == (3,)
    assert family.relative_dimension() == 1
    assert family.adjunction_twist_degree() == 0


def test_the_hesse_fibre_at_zero_is_smooth_and_at_one_is_singular() -> None:
    r"""At \(t = 0\) the fibre is the Fermat cubic, smooth; at \(t = 1\) it is
    \(x^3+y^3+z^3-3xyz = (x+y+z)(x^2+y^2+z^2-xy-yz-zx)\), singular where the line meets the conic.

    Source: Artebani--Dolgachev, *The Hesse pencil of plane cubic curves*, arXiv:math/0611590, §2.
    """
    parameter, family = _hesse_family()
    smooth = family.base_change(parameter.Mor(QQ)({"t": QQ.zero()}))
    singular = family.base_change(parameter.Mor(QQ)({"t": QQ.one()}))

    assert tuple(smooth.defining_degrees()) == (3,)
    assert tuple(singular.defining_degrees()) == (3,)
    assert smooth.is_smooth()
    assert not singular.is_smooth()


def test_tx_ty_one_minus_t_generate_a_height_three_ideal_but_are_not_a_regular_sequence() -> None:
    r"""In \(S = \mathbf Q[t][x,y,z]\), \((tx, ty, 1-t) = (1-t, x, y)\) has height \(3\), and \((1-t,x,y)\) is a regular
    sequence; \((tx, ty, 1-t)\) is not, since \(ty\cdot x = y\cdot tx \in (tx)\) while \(x\notin(tx)\).

    Derivation: modulo \(1-t\), \(t\equiv 1\); the displayed relation.
    """
    _parameter, plane, t, x, y, _z = _plane_over_the_parameter_line()
    ring = plane.homogeneous_coordinate_ring()

    assert ring.ideal(t * x, t * y, 1 - t) == ring.ideal(1 - t, x, y)
    assert ring.ideal(1 - t, x, y).height() == 3
    assert ring.is_regular_sequence((1 - t, x, y))
    assert not ring.is_regular_sequence((t * x, t * y, 1 - t))


def test_the_family_tx_equals_zero_has_the_whole_plane_as_its_fibre_at_zero_and_a_line_at_one() -> None:
    r"""\(V(tx)\subset\mathbf P^2_{\mathbf Q[t]}\) is not flat over \(t = 0\): its fibre there is \(V(0) = \mathbf P^2\),
    of dimension \(2\), while its fibre at \(t = 1\) is the line \(V(x)\), of dimension \(1\).

    Derivation: substitute \(t = 0\) and \(t = 1\) in \(tx\).
    """
    parameter, plane, t, x, _y, _z = _plane_over_the_parameter_line()
    family = plane.closed_subscheme(t * x)

    special = family.base_change(parameter.Mor(QQ)({"t": QQ.zero()}))
    general = family.base_change(parameter.Mor(QQ)({"t": QQ.one()}))

    assert special.dimension() == 2
    assert general.dimension() == 1
    assert not family.is_flat()
