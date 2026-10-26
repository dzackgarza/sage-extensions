r"""Group Mor objects represent homomorphisms and their identities."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hom_from_c2_to_s3_has_four_elements() -> None:
    source = Groups.C(2)
    target = Groups.S(3)
    morphisms = source.Mor(target)
    trivial = morphisms.an_element()

    assert morphisms.cardinality() == cardinal(4)
    assert trivial(source.one()) == target.one()


def test_group_identity_is_the_unit_for_composition() -> None:
    group = Groups.C(6)
    identity = group.Mor(group).identity()

    assert identity(group.group_generator()) == group.group_generator()
    assert identity * identity == identity

