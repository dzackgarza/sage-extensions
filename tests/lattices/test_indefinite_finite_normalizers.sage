r"""Normalizers of noncyclic finite subgroups of O(L) for indefinite L (port #50).

L = U + U, H = <-1 + 1, 1 + -1>. Elements commuting with H preserve both eigenspaces, so
C(H) = O(U) x O(U), of order 16 since O(U) = {+-1, +-swap}. The exchange of the two
summands conjugates -1 + 1 to 1 + -1, and an automorphism of H sending a generator to the
central -1 is not realized, because it would empty an eigenspace. So N(H) has order 32.
"""

from sage_extensions.all import *


def _closure_size(lattice, generators):
    framing = tuple(lattice.module_generators())
    key = lambda g: tuple(str(g(x)) for x in framing)
    one = lattice.O().one()
    seen = dict([(key(one), one)])
    frontier = [one]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            following = current * generator
            if key(following) not in seen:
                seen[key(following)] = following
                frontier.append(following)
    return len(seen)


def test_normalizer_of_the_klein_four_sign_group_on_two_hyperbolic_planes():
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e1, f1, e2, f2 = tuple(lattice.module_generators())
    labels = tuple(lattice.module_generating_set())
    group = lattice.O()
    left = group(dict(zip(labels, (-e1, -f1, e2, f2), strict=True)))
    right = group(dict(zip(labels, (e1, f1, -e2, -f2), strict=True)))
    exchange = group(dict(zip(labels, (e2, f2, e1, f1), strict=True)))
    normalizer = group.normalizer(group.subgroup((left, right)))
    generators = tuple(normalizer.group_generators())
    assert all(g in normalizer for g in generators)
    assert exchange in normalizer
    assert _closure_size(lattice, generators) == 32
