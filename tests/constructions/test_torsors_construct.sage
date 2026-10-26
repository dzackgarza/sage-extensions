r"""A finite group acting on itself by left translation is its canonical torsor."""

from sage_extensions.all import *  # noqa: F401,F403


def test_regular_s3_action_is_a_six_point_torsor() -> None:
    group = Groups.S(3)
    torsor = FiniteGSets(group)(tuple(group), lambda g, point: g * point)
    point = torsor.an_element()
    target = group.group_generators()[0]

    assert torsor in Torsors(group)
    assert torsor.cardinality() == cardinal(6)
    assert point in torsor.point_set()
    assert torsor.transporter(group.one(), target) == target
    assert torsor.is_free_action()
    assert torsor.is_transitive_action()

