r"""The identity lattice map induces a toric endomorphism of projective plane."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_identity_lattice_map_induces_a_toric_endomorphism() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    lattice = plane.cocharacter_lattice()
    lattice_identity = lattice.Mor(lattice).identity()
    toric_identity = plane.toric_morphism(lattice_identity, plane)

    assert toric_identity.domain() is plane
    assert toric_identity.codomain() is plane
