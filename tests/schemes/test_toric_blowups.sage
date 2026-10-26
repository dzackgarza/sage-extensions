from sage_extensions.all import *


def _projective_plane():
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    return fans.projective_space_fan().toric_variety(QQ)


def test_blowup_of_a_torus_fixed_point_of_p2_is_the_star_subdivision_with_blowdown() -> None:
    plane = _projective_plane()
    center = plane.fan().maximal_cones()[0]

    blowup = plane.toric_fixed_point_blowup(center)

    assert blowup in Blowups(QQ)
    assert blowup in ToricFixedPointBlowups(QQ)
    assert blowup.blowup_source() is plane
    assert blowup.blowup_center().inclusion().codomain() is plane
    assert blowup.blowup_center_cone() is center
    assert blowup.blowup_morphism().domain() is blowup
    assert blowup.blowup_morphism().codomain() is plane
    assert blowup.fan().is_smooth()
    assert blowup.fan().is_complete()
    assert blowup.fan().cones(1).cardinality() == plane.fan().cones(1).cardinality() + 1


def test_exceptional_curve_has_self_intersection_minus_one_and_picard_rank_increases() -> None:
    plane = _projective_plane()
    blowup = plane.toric_fixed_point_blowup(plane.fan().maximal_cones()[0])

    exceptional = blowup.exceptional_weil_divisor()
    exceptional_subscheme = blowup.exceptional_divisor()
    ideal_sheaf = exceptional_subscheme.ideal_sheaf()

    assert exceptional_subscheme in EffectiveCartierDivisors(blowup)
    assert exceptional_subscheme.inclusion().codomain() is blowup
    assert ideal_sheaf in QuasiCoherentSheaves(blowup).Invertible()
    assert ideal_sheaf.associated_divisor() == -exceptional
    assert exceptional_subscheme.picard_class() == blowup.exceptional_picard_class()
    assert blowup.exceptional_self_intersection() == -1
    assert blowup.weil_multiplicity(exceptional, blowup.exceptional_ray()) == 1
    assert int(blowup.picard_group().module_rank()) == int(plane.picard_group().module_rank()) + 1


def _ray_with_vector(fan, vector):
    for ray in fan.cones(1):
        (primitive,) = tuple(ray.rays())
        if primitive == vector:
            return ray
    raise AssertionError("ray not found")


def test_total_and_strict_transforms_distinguish_the_exceptional_multiplicity() -> None:
    plane = _projective_plane()
    center = plane.fan().maximal_cones()[0]
    blowup = plane.toric_fixed_point_blowup(center)
    center_vector = tuple(center.rays())[0]
    source_ray = _ray_with_vector(plane.fan(), center_vector)
    boundary = plane.torus_invariant_prime_divisor(source_ray)

    strict = blowup.strict_transform_divisor(boundary)
    total = blowup.blowup_morphism().pullback_divisor(boundary)
    exceptional = blowup.exceptional_weil_divisor()

    assert total == strict + exceptional
    assert blowup.divisor_intersection(strict, strict) == 0
    assert blowup.divisor_intersection(strict, exceptional) == 1


def test_picard_pullback_is_orthogonal_to_the_exceptional_class() -> None:
    plane = _projective_plane()
    blowup = plane.toric_fixed_point_blowup(plane.fan().maximal_cones()[0])
    source_picard = plane.picard_group()
    source_label = next(iter(source_picard.module_generating_set()))
    hyperplane = source_picard.module_generator(source_label)
    pulled = blowup.picard_pullback_morphism()(hyperplane)
    exceptional = blowup.exceptional_picard_class()
    pairing = blowup.picard_intersection_pairing()

    assert pairing(pulled, pulled) == 1
    assert pairing(pulled, exceptional) == 0
    assert pairing(exceptional, exceptional) == -1


def test_first_projective_plane_blowup_has_del_pezzo_degree_eight() -> None:
    plane = _projective_plane()
    first = plane.toric_fixed_point_blowup(plane.fan().maximal_cones()[0])

    assert first.is_del_pezzo()
    assert Surfaces(first.scheme_base_ring()).DelPezzo()(first).del_pezzo_degree() == 8
    assert int(first.picard_group().module_rank()) == 2
