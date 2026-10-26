r"""The blowup of `\mathbb{P}^2_{\mathbb{Q}}` at the point `(1:1:1)`.

Source: Hartshorne, *Algebraic Geometry*, V.3.2, V.3.3, V.3.6: for
`\pi: X = \mathrm{Bl}_p \mathbb{P}^2 \to \mathbb{P}^2`,
`\operatorname{Pic} X = \mathbb{Z} H \oplus \mathbb{Z} E` with `H^2 = 1`,
`H \cdot E = 0`, `E^2 = -1`, `K_X = \pi^* K + E = -3H + E`, and a curve of degree
`d` with multiplicity `m` at `p` has strict transform `dH - mE`.
"""

from sage_extensions.all import *


def _blowup():
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    blowup = plane.blowup(plane.point((1, 1, 1)))
    return plane, blowup


def test_blowup_of_the_plane_has_exceptional_curve_of_square_minus_one() -> None:
    plane, blowup = _blowup()
    hyperplane = blowup.blowup_morphism().pullback(plane.hyperplane_class())
    exceptional = blowup.exceptional_divisor_class()

    assert blowup.picard_group().module_rank() == 2
    assert blowup.intersection_number(hyperplane, hyperplane) == 1
    assert blowup.intersection_number(hyperplane, exceptional) == 0
    assert blowup.intersection_number(exceptional, exceptional) == -1


def test_strict_transform_of_a_cuspidal_cubic_through_the_cusp_is_3h_minus_2e() -> None:
    r"""The cubic `(y-z)^2 z = (x-z)^3` has a cusp at `p`, so its strict transform is
    `3H - 2E`, with `(3H - 2E) \cdot E = 2` and `(3H - 2E)^2 = 9 - 4 = 5`."""
    plane, blowup = _blowup()
    x, y, z = plane.homogeneous_coordinate_generators()
    cusp = plane.closed_subscheme((y - z) ** 2 * z - (x - z) ** 3)
    hyperplane = blowup.blowup_morphism().pullback(plane.hyperplane_class())
    exceptional = blowup.exceptional_divisor_class()
    strict = blowup.strict_transform(cusp).divisor_class()

    assert blowup.curve_multiplicity_at_center(cusp) == 2
    assert strict == 3 * hyperplane - 2 * exceptional
    assert blowup.intersection_number(strict, exceptional) == 2
    assert blowup.intersection_number(strict, strict) == 5
    assert blowup.total_transform(cusp).divisor_class() == 3 * hyperplane


def test_blowup_of_the_plane_at_a_point_is_a_del_pezzo_surface_of_degree_eight() -> None:
    r"""`K_X = -3H + E`, so `K_X^2 = 9 - 1 = 8`, and `-K_X` is ample."""
    plane, blowup = _blowup()
    hyperplane = blowup.blowup_morphism().pullback(plane.hyperplane_class())
    exceptional = blowup.exceptional_divisor_class()
    canonical = blowup.canonical_class()

    assert canonical == -3 * hyperplane + exceptional
    assert blowup.intersection_number(canonical, canonical) == 8
    assert (-canonical).is_ample()


def test_exceptional_curve_is_an_effective_cartier_divisor() -> None:
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    blowup = ProjectivePointBlowups(QQ)(plane.point_morphism((1, 1, 1)))
    exceptional = blowup.exceptional_divisor()
    ideal_sheaf = exceptional.ideal_sheaf()
    multidegree = ideal_sheaf.multidegree()

    assert exceptional in EffectiveCartierDivisors(blowup)
    assert exceptional.inclusion().codomain() is blowup
    assert ideal_sheaf in QuasiCoherentSheaves(blowup).Invertible()
    assert tuple(multidegree[label] for label in multidegree.index_set()) == (-1, 1)
    assert exceptional.picard_class() == blowup.exceptional_picard_class()
