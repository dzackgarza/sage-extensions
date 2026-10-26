r"""The averaging operator on the regular representation of $S_3$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_averaging_operator_of_s3_squares_to_six_times_itself_and_kills_augmentation() -> None:
    r"""$N = \sum_{g \in S_3} g$ on $\mathbb{Q}[S_3]$ satisfies $N^2 = |S_3|\,N = 6N$ and $N(1 - g) = 0$; its image is the invariants, of dimension $1$."""
    group = Groups.S(3)
    module = Modules(QQ)(Sets()(tuple(group)))

    def act(group_element, vector):
        return module.Mor(module)(
            {label: module.module_generator(group_element * label) for label in group}
        )(vector)

    representation = Modules(QQ[group])(module, act)
    unit = representation.module_generator(group.one())
    total = sum(representation.module_generator(label) for label in group)
    averaging = Modules(QQ[group]).Mor(representation, representation)({label: total for label in group})
    translate = representation.action_of(group.group_generators()[0])

    assert averaging(unit - translate(unit)) == representation.zero()
    assert averaging(averaging(unit)) == 6 * averaging(unit)
    assert averaging.image().module_rank() == 1
    assert representation.is_invariant(total)
    assert not representation.is_invariant(unit)
