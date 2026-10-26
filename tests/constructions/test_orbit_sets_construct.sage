r"""The orbit set of the natural S3-set is the represented one-point quotient."""

from sage_extensions.all import *  # noqa: F401,F403


def test_natural_s3_orbit_set_exposes_its_quotient_data() -> None:
    group = Groups.S(3)
    g_set = FiniteGSets(group)((1, 2, 3), lambda g, point: g(point))
    orbits = FiniteGSets(group).orbits_functor()(g_set)
    orbit = orbits.orbit_of(1)
    representative = orbit.representative()

    assert orbits in OrbitSets()
    assert orbits.g_set() is g_set
    assert orbits.cardinality() == cardinal(1)
    assert orbits.orbit_points(orbit).cardinality() == cardinal(3)
    assert orbits.ranking_map()(orbit) == 0
    assert orbit.acting_group() is group
    assert orbit.group() is group
    assert orbit.supergroup() is group
    assert orbit.elements() == orbit.members()
    assert orbit.members() == orbit.points()
    assert orbit.members().cardinality() == cardinal(3)
    assert representative in g_set.point_set()
    assert orbit.stabilizer().order() == 2
    transporter = orbit.transporter_from(1)
    assert g_set.act(transporter, 1) == representative
