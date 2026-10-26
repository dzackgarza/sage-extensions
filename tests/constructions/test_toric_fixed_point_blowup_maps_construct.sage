r"""The toric blowup of P^2 retains its blowdown, exceptional class, and strict transforms."""

from sage_extensions.all import *  # noqa: F401,F403


def _blowup_of_projective_plane():
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cone = next(
        cone
        for cone in plane.fan().maximal_cones()
        if cone.rays()[0] + cone.rays()[1]
        == plane.cocharacter_lattice()((-1, 0))
    )
    return plane, cone, plane.toric_fixed_point_blowup(cone)


def test_blowdown_and_exceptional_class_data() -> None:
    plane, _cone, blowup = _blowup_of_projective_plane()

    assert blowup.blowdown() == blowup.blowup_morphism()
    assert blowup.blowdown().codomain() is plane
    assert blowup.exceptional_divisor().picard_class() == blowup.exceptional_picard_class()
    assert blowup.picard_pullback_morphism().domain() is plane.picard_group()
    assert blowup.picard_pullback_morphism().codomain() is blowup.picard_group()


def test_strict_transform_of_invariant_line_keeps_its_ray() -> None:
    plane, cone, blowup = _blowup_of_projective_plane()
    ray = next(
        ray
        for ray in cone.faces(1)
        if ray.rays()[0] == plane.cocharacter_lattice()((-1, -1))
    )
    upstairs = next(
        candidate
        for candidate in blowup.fan().cones(1)
        if candidate.rays()[0] == blowup.cocharacter_lattice()((-1, -1))
    )

    assert blowup.strict_transform_divisor(
        plane.torus_invariant_prime_divisor(ray)
    ) == blowup.torus_invariant_prime_divisor(upstairs)
