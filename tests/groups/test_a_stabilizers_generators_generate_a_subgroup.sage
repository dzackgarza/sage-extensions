r"""A stabilizer's generator family generates a subgroup, with no membership question asked.

A line stabilizer `S = G.stabilizer(x)` builds its generators through its own selected free
cover into the ambient group `G = L.Aut()`: each generator is an element of `L.Aut()` by
that construction.  Forming the subgroup they generate is a statement about the caller's
supplied family, and on an infinite generated group the membership question it used to ask
has no answer — `GeneratedSubgroups.membership_decision` returns an unevaluated proposition
for a general infinite subgroup, so `group.subgroup(family)` raised

    TypeError: membership of Morphism from Lattice ... to Lattice ... in Subgroup of
    Orthogonal group O(...) is undecided; supply a word witness to membership_decision

at `GeneratedSubgroups._engine_subgroup` (sage-extensions#341).  The generators are
elements of `L.Aut()` because the stabilizer constructed them as elements of `L.Aut()`, not
because that question was decided, so the construction reads that datum and asks nothing.

Two specimens, because the failing `group` is a generated subgroup in the first and the
ambient group in the second:

* `U + U` over `QQ` with `G = <tau_1, tau_2, swap>` (the sage-extensions#287 specimen), its
  coset space on the index-two sublattice `2ZZ e_1 + ZZ f_1 + ZZ e_2 + ZZ f_2`, and the
  lattice stabilizer `S` of that sublattice in `G`;
* `T_En = U + U(2) + E8(-2)` with `G = O(T_En)` and the setwise stabilizer `S` of the
  primitive isotropic line `ZZ e` (sage-extensions#341's own acceptance).

What is asserted is what the construction states: the subgroup is a subgroup of the same
group, and its selected generators are the supplied family.  No order and no index is
asserted — an infinite generated subgroup has no decided order here, and asserting one
would be the very question this construction declines to ask.

The reading side is `_supplied_generator`, and a family it admits must carry the
construction that supplied it, not a premise the caller states about it.  A third
specimen, `U` over `ZZ`, is where that distinction is decidable: `O(U)` is finite (the
isometries are `+-1`, the swap and `-swap`, so `|O(U)| = 4`), `G = <-1>` has order 2, and
the swap is not in `G`.  `G.subgroup((swap,))` must therefore refuse, and a construction
that admits every element parented by the ambient group instead answers with a subgroup
of `G` that `G` does not contain.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.rational_integral_stabilizers import IntegralStructureAction

import pytest


def _euclid_specimen():
    r"""`U + U` over `QQ`, the infinite `G = <tau_1, tau_2, swap>`, and the stabilizer of `L'`."""
    gram = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]
    source = Lattices(QQ)(gram)
    space = Modules(QQ).restriction_of_scalars(ZZ.Mor(QQ)(lambda n: QQ(n)))(source)
    labels = tuple(source.module_generating_set())
    e1, f1, e2, f2 = tuple(source.module_generator(label) for label in labels)
    ambient = source.Aut()
    images = (
        {labels[0]: e1, labels[1]: f1 + e2, labels[2]: e2, labels[3]: f2 - e1},
        {labels[0]: e1, labels[1]: f1 - e2, labels[2]: e2, labels[3]: f2 + e1},
        {labels[0]: f1, labels[1]: e1, labels[2]: e2, labels[3]: f2},
    )
    group = ambient.subgroup(tuple(ambient(image) for image in images))
    whole = space.subobject_on([space(e1), space(f1), space(e2), space(f2)])
    selected = space.subobject_on([space(2 * e1), space(f1), space(e2), space(f2)])
    action = IntegralStructureAction(group, selected.inclusion()).with_stable_containing_bound(
        whole.inclusion(), check=True
    )
    return ambient, group, action.finite_representation().lattice_stabilizer()


def test_a_generated_groups_line_stabilizer_generates_a_subgroup():
    r"""`G.subgroup(S.group_generators())` is constructed, `S` the stabilizer of a lattice in `G`."""
    ambient, group, stabilizer = _euclid_specimen()
    generators = tuple(stabilizer.group_generators())

    generated = group.subgroup(generators)

    assert generated.supergroup() is group
    assert frozenset(generated.group_generators()) == frozenset(generators)
    assert all(generator.parent() is ambient for generator in generators)


def test_the_enriques_orthogonal_groups_line_stabilizer_generates_a_subgroup():
    r"""`O(T_En).subgroup(S.group_generators())` is constructed, `S` the stabilizer of a line."""
    lattice = NamedLattices.TEn
    group = lattice.O()
    e = lattice.module_generator(next(iter(lattice.module_generating_set())))
    line = lattice.primitive_isotropic_subobject(e)
    stabilizer = group.stabilizer(line, action="setwise")
    generators = tuple(stabilizer.group_generators())

    generated = group.subgroup(generators)

    assert generated.supergroup() is group
    assert frozenset(generated.group_generators()) == frozenset(generators)


def _hyperbolic_plane_specimen():
    r"""`U` over `ZZ`, its finite `O(U)`, and `G = <-1>` as a subgroup of it."""
    lattice = NamedLattices.U
    ambient = lattice.Aut()
    labels = tuple(lattice.module_generating_set())
    e, f = tuple(lattice.module_generator(label) for label in labels)
    return (
        ambient,
        ambient.subgroup((ambient({labels[0]: -e, labels[1]: -f}),)),
        ambient({labels[0]: f, labels[1]: e}),
    )


def test_a_family_outside_the_group_is_refused() -> None:
    r"""`G.subgroup((swap,))` raises: `G = <-1> <= O(U)` and the swap is not in `G`.

    Membership here is decided, so the refusal is a decision and not a retreat:
    `O(U)` is finite, `G` is its order-two subgroup, and `swap not in G`.  A
    construction that admits any element parented by `G`'s ambient group instead
    returns a subgroup of `G` whose generator is not in `G`.
    """
    ambient, group, swap = _hyperbolic_plane_specimen()

    assert ambient.cardinality() == 4
    assert group.supergroup() is ambient
    assert group.cardinality() == 2
    assert swap not in group

    with pytest.raises(ValueError):
        group.subgroup((swap,))
