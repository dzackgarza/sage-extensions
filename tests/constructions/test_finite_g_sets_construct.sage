r"""The natural and regular S3-actions expose the complete finite-G-set interface."""

from sage_extensions.all import *  # noqa: F401,F403


def _natural_action():
    group = Groups.S(3)
    return group, FiniteGSets(group)((1, 2, 3), lambda g, point: g(point))


def test_natural_s3_set_exposes_orbits_stabilizers_and_permutation_action() -> None:
    group, natural = _natural_action()
    generator = group.group_generators()[0]
    orbits = natural.orbits()
    stabilizers = natural.orbit_stabilizers()
    permutation = natural.permutation_representation()
    identity = natural.Mor(natural).identity()

    assert natural in FiniteGSets(group)
    assert natural.point_set().cardinality() == cardinal(3)
    assert natural.is_parent_of(1)
    assert natural.is_transitive_action()
    assert not natural.is_free_action()
    assert not natural.is_torsor()
    assert natural.fixed_points().cardinality() == cardinal(0)
    assert orbits.cardinality() == cardinal(1)
    assert stabilizers.cardinality() == cardinal(1)
    assert stabilizers[orbits.orbit_of(1)].order() == 2
    assert natural.stabilizer(1).order() == 2
    assert natural.ranking_map()(1) == 0
    assert natural.act(generator, 1) == generator(1)
    assert permutation(generator)(1) == natural.act(generator, 1)
    assert identity(1) == 1
    witness = natural.transporter_witness(1, 2)
    assert natural.act(witness, 1) == 2


def test_regular_s3_set_is_a_torsor_with_unique_transporters() -> None:
    group = Groups.S(3)
    regular = FiniteGSets(group)(tuple(group), lambda g, point: g * point)
    target = group.group_generators()[0]
    transporter = regular.transporter(group.one(), target)

    assert regular.is_free_action()
    assert regular.is_transitive_action()
    assert regular.is_torsor()
    assert transporter == target
