r"""The selected generator of C6 determines its entire cyclic-group structure."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cyclic_six_walks_its_selected_generator() -> None:
    group = Groups.C(6)
    generator = group.group_generator()

    assert group in CyclicGroups()
    assert group.cardinality() == cardinal(6)
    assert group.order() == 6
    assert group.is_finite()
    assert group.is_abelian()
    assert generator.order() == 6
    assert generator**6 == group.one()

