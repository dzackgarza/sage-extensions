r"""Sections, restrictions and stalks of the structure sheaf of the affine plane over ``Q``.

Source: Stacks Project, Tag 01HV (Lemma 26.5.4): on ``X = Spec R``,
``Gamma(X, O_X) = R``, ``Gamma(X, M~) = M``, ``O_X(D(f)) = R_f``, the restriction maps between
distinguished opens are the localization maps, and the stalk at ``p`` is ``R_p``.  A map
``R_f -> R_g`` over ``R`` exists exactly when ``f`` becomes a unit in ``R_g``.
"""

from pytest import raises

from sage_extensions.all import *


def test_global_sections_of_the_structure_sheaf_are_the_coordinate_ring() -> None:
    r"""``Gamma(A^2, O) = Q[x, y]`` and ``O(D(x)) = Q[x, y]_x``, in which ``x`` is a unit."""
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    plane = AffineSchemes(QQ)(ring)
    sheaf = plane.structure_sheaf()
    d_x = plane.distinguished_open(x)

    assert sheaf.global_sections() is ring
    assert sheaf.sections_on_distinguished_open(d_x) is d_x.coordinate_algebra()
    assert sheaf.restriction_map(plane, d_x)(x).is_unit()


def test_restriction_from_d_x_to_d_xy_inverts_y() -> None:
    r"""``D(xy) <= D(x)``, and the restriction ``Q[x, y]_x -> Q[x, y]_{xy}`` makes ``y`` a unit;
    the restriction from an open to itself is the identity."""
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)
    sheaf = plane.structure_sheaf()
    d_x = plane.distinguished_open(x)
    d_xy = plane.distinguished_open(x * y)
    sections = d_x.coordinate_algebra()

    assert sheaf.restriction_map(d_x, d_xy)(sections(y)).is_unit()
    assert sheaf.restriction_map(d_x, d_xy)(sections(x)).is_unit()
    assert sheaf.restriction_map(d_x, d_x) == sections.Mor(sections).identity()


def test_there_is_no_restriction_from_d_x_to_d_y() -> None:
    r"""``D(y)`` is not contained in ``D(x)``: ``x`` is not a unit in ``Q[x, y]_y``."""
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)

    with raises(ValueError):
        plane.structure_sheaf().restriction_map(plane.distinguished_open(x), plane.distinguished_open(y))


def test_restrictions_compose() -> None:
    r"""Restricting ``X -> D(x) -> D(xy)`` is restricting ``X -> D(xy)``: a presheaf is a functor."""
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)
    sheaf = plane.structure_sheaf()
    d_x = plane.distinguished_open(x)
    d_xy = plane.distinguished_open(x * y)

    assert sheaf.restriction_map(d_x, d_xy) * sheaf.restriction_map(plane, d_x) == sheaf.restriction_map(plane, d_xy)


def test_the_global_sections_of_the_sheaf_of_a_module_are_the_module() -> None:
    r"""``Gamma(Spec R, M~) = M`` for ``M = R^2``; an affine scheme is a locally ringed space."""
    ring = QQ["x,y"]
    plane = AffineSchemes(QQ)(ring)
    module = ring.free_module(2)
    sheaves = QuasiCoherentSheaves(plane)

    assert sheaves.global_sections(sheaves.associated_sheaf(module)) is module
    assert plane in LocallyRingedSpaces()
    assert plane in RingedSpaces()


def test_the_stalk_at_the_origin_is_a_two_dimensional_local_ring_with_residue_field_q() -> None:
    r"""``O_{A^2, (x, y)} = Q[x, y]_{(x, y)}``: local of Krull dimension 2 with residue field ``Q``."""
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)
    origin = plane.underlying_space()(ring.ideal(x, y))
    stalk = plane.stalk(origin)

    assert stalk.krull_dimension() == 2
    assert stalk.residue_field() == QQ
