r"""Subgroups of $S_4$ cut out by a predicate, as a kernel, or as a stabilizer.

The even permutations form $A_4$, of order $4!/2 = 12$; it contains the
$3$-cycles and no transposition.  The sign map $S_4 \to C_2$ is determined
by sending the transposition $(1\,2)$ and the $4$-cycle $(1\,2\,3\,4)$ (both
odd) to the generator, and its kernel is again $A_4$, which is nonabelian
($(1\,2\,3)(1\,2)(3\,4) \ne (1\,2)(3\,4)(1\,2\,3)$).  The stabilizer of the
point $4$ is $S_3$, of order $6$, and $A_4 \cap S_3 = A_3$ has order $3$.
The centralizer of $(1\,2)(3\,4)$ is the dihedral group of order $8$ that
contains it, since its class has $3$ elements and $24 / 3 = 8$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _sign(group):
    two = Groups.C(2)
    generator = two.group_generators()[0]
    return group.Mor(two)({group((1, 2)): generator, group((1, 2, 3, 4)): generator})


def test_the_even_permutations_of_s4_form_a_subgroup_of_order_twelve() -> None:
    group = Groups.S(4)
    even = group.predicate_subgroup(lambda x: x.sign() == 1, "even permutations")

    assert even.order() == 12
    assert even.is_finite()
    assert sum(1 for _element in even) == 12
    assert group((1, 2, 3)) in even
    assert group((1, 2)) not in even
    assert even.one() == group.one()
    assert even(group((1, 2, 3))) == group((1, 2, 3))


def test_the_kernel_of_the_sign_of_s4_is_the_nonabelian_group_of_order_twelve() -> None:
    kernel = _sign(Groups.S(4)).kernel()

    assert kernel.order() == 12
    assert kernel.cardinality() == cardinal(12)
    assert not kernel.is_abelian()


def test_the_even_permutations_fixing_four_form_a3() -> None:
    group = Groups.S(4)
    even = group.predicate_subgroup(lambda x: x.sign() == 1, "even permutations")
    fixing_four = group.stabilizer(4)

    assert fixing_four.order() == 6
    assert even.intersection(fixing_four).order() == 3


def test_the_centralizer_of_a_double_transposition_in_s4_has_order_eight() -> None:
    group = Groups.S(4)

    assert group.centralizer(group([(1, 2), (3, 4)])).order() == 8


def test_normalizer_retains_its_conjugation_action_functor() -> None:
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2)),))
    normalizer = group.normalizer(subgroup)
    action = normalizer.stabilizer_action()
    point = action.domain().an_object()
    identity = action.domain().Mor(point, point)(group.one())

    assert normalizer.stabilized_object() is subgroup
    assert action.domain() is group.classifying_category()
    assert action.codomain() is Sets()
    assert action(identity)(subgroup) is subgroup
    assert normalizer.inclusion().codomain() is group
    restricted = normalizer.restricted_stabilizer_action()
    assert restricted.domain() is normalizer.classifying_category()
    assert restricted.codomain() is action.codomain()
    assert restricted(restricted.domain().an_object()) is action(action.domain().an_object())
    point = restricted.domain().an_object()
    for element in normalizer:
        arrow = restricted.domain().Mor(point, point)(element)
        assert restricted(arrow)(subgroup) == subgroup
