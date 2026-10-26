r"""The permutation character of the natural S3-action is constant on its three conjugacy classes."""

from sage_extensions.all import *  # noqa: F401,F403


def test_natural_s3_permutation_character_has_values_three_one_zero() -> None:
    group = Groups.S(3)
    module = QQ.free_module(3)

    def action(g, vector):
        return module.Mor(module)(
            {label: module.module_generator(int(g(label + 1)) - 1) for label in range(3)}
        )(vector)

    representation = Modules(QQ[group])(module, action)
    character = representation.character()
    transposition = next(g for g in group.group_generators() if g.order() == 2)
    three_cycle = next(g for g in group.group_generators() if g.order() == 3)

    assert character.degree() == 3
    assert character(group.one()) == 3
    assert character(transposition) == 1
    assert character(three_cycle) == 0
    assert character.conjugacy_class_representatives().cardinality() == cardinal(3)
    assert len(tuple(character.values())) == 3
