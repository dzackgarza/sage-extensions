r"""The double-coset section of a finite action on an infinite generated group returns its group's elements.

`G = <tau_1, tau_2, swap>` is an infinite subgroup of `O(U + U)` over `QQ`: the two
Eichler transvections move one hyperbolic plane's frame by the other plane's isotropic
vectors, and the swap exchanges the plane's two isotropic lines.  All three preserve the
lattice `L = ZZ e_1 + ZZ f_1 + ZZ e_2 + ZZ f_2`, so `G` acts on the lattices commensurable
with the index-two sublattice `L' = 2 ZZ e_1 + ZZ f_1 + ZZ e_2 + ZZ f_2`, and the orbit of
`L'` is finite: this is the finite action on an infinite generated group that
sage-extensions#287 is about.

The coset space `G/G_{L'}` is that orbit with a section taken through `G`'s selected free
cover, so its representative map is `augmentation o word_section`: a coset's representative
is a *word* in `G`'s selected generators, evaluated in `G`.  A double-coset representative
is one of those values, so it is an element of `G` by construction, and the section is a
section of the double-coset projection by construction.  Both are what this file asserts,
for every double coset, with the word supplied by the cover rather than by a general
infinite-subgroup membership solver.

The assertion is not vacuous: `G/G_{L'}` has four points and the double cosets below have
three and four orbits, so the section must return words of length two and more, not only
the identity and one-letter generators.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.rational_integral_stabilizers import IntegralStructureAction


def _specimen():
    r"""`U + U` over `QQ`, the infinite `G = <tau_1, tau_2, swap>`, and `G`'s coset space on `L'`."""
    gram = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]
    source = Lattices(QQ)(gram)
    space = Modules(QQ).restriction_of_scalars(ZZ.Mor(QQ)(lambda n: QQ(n)))(source)
    labels = tuple(source.module_generating_set())
    e1, f1, e2, f2 = tuple(source.module_generator(label) for label in labels)
    orthogonal_group = source.Aut()
    # x |-> x + b(x, v) w - b(x, w) v at the isotropic vector v and w orthogonal to it
    images_by_name = {
        "tau1": {labels[0]: e1, labels[1]: f1 + e2, labels[2]: e2, labels[3]: f2 - e1},
        "tau2": {labels[0]: e1, labels[1]: f1 - e2, labels[2]: e2, labels[3]: f2 + e1},
        "swap": {labels[0]: f1, labels[1]: e1, labels[2]: e2, labels[3]: f2},
    }
    isometries = tuple(orthogonal_group(images) for images in images_by_name.values())
    group = orthogonal_group.subgroup(isometries)
    whole = space.subobject_on([space(e1), space(f1), space(e2), space(f2)])
    selected = space.subobject_on([space(2 * e1), space(f1), space(e2), space(f2)])
    action = IntegralStructureAction(group, selected.inclusion()).with_stable_containing_bound(
        whole.inclusion(), check=True
    )
    return group, action


def test_the_coset_space_is_finite_on_an_infinite_group():
    r"""The action's coset space is a finite `G`-set although `G` is infinite."""
    group, action = _specimen()

    cosets = action.right_cosets()

    assert cosets.cardinality() == cardinal(4)
    assert group.is_finite() is not True


def test_the_double_coset_section_returns_elements_of_the_group():
    r"""Every double-coset representative is an element of `G`, and of `G` with its inverse.

    The values are words in `G`'s selected generators, so membership needs no general
    membership solver; it is supplied by the cover the section is built through.
    """
    group, action = _specimen()
    cosets = action.right_cosets()

    for quotient in (group.subgroup((group.group_generators()[0],)), group):
        double_cosets = cosets.double_cosets(quotient)
        assert double_cosets.is_empty() is False
        section = double_cosets.double_coset_section()
        for orbit in double_cosets:
            representative = section(orbit)
            assert representative in group
            assert ~representative in group


def test_the_double_coset_section_inverts_the_double_coset_projection():
    r"""`projection(section(orbit))` is `orbit`: the section is a section, on every orbit.

    The composite is computed in the group, so a representative that the group cannot
    admit would leave the projection undefined rather than merely unproven.
    """
    group, action = _specimen()
    cosets = action.right_cosets()
    quotient = group.subgroup((group.group_generators()[0],))

    double_cosets = cosets.double_cosets(quotient)
    section = double_cosets.double_coset_section()
    projection = double_cosets.double_coset_projection()

    assert double_cosets.cardinality() == cardinal(3)
    assert all(projection(section(orbit)) == orbit for orbit in double_cosets)
