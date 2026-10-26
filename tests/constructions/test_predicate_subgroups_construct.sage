r"""Point stabilizers give finite predicate subgroups with literal predicates and intersections."""

from sage_extensions.all import *  # noqa: F401,F403


def test_s4_point_stabilizer_retains_its_defining_predicate() -> None:
    group = Groups.S(4)
    stabilizer = group.predicate_subgroup(
        lambda g: g(1) == 1,
        "fixes the point 1",
    )
    predicate = stabilizer.defining_predicate()
    moving = next(g for g in group if g(1) != 1)

    assert stabilizer.cardinality() == cardinal(6)
    assert stabilizer.is_finite()
    assert stabilizer.one() == group.one()
    assert predicate(group.one())
    assert not predicate(moving)


def test_intersection_of_two_s4_point_stabilizers_fixes_both_points() -> None:
    group = Groups.S(4)
    fixes_one = group.predicate_subgroup(lambda g: g(1) == 1, "fixes 1")
    fixes_two = group.predicate_subgroup(lambda g: g(2) == 2, "fixes 2")
    intersection = fixes_one.intersection(fixes_two)

    assert intersection.order() == 2
    assert all(g(1) == 1 and g(2) == 2 for g in intersection)

