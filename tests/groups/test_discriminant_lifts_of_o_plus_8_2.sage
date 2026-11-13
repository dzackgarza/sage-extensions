r"""Lifts along O(L) -> O(A_L) for L = U + E8(-2), whose O(A_L) is O^+_8(2).

A_L = (Z/2)^8 with the even form of plus type, so O(q_L) = O^+_8(2), of order
2 * 2^12 * (2^4 - 1) * (2^2 - 1)(2^4 - 1)(2^6 - 1) = 348364800. Because L
contains U, O(L) -> O(q_L) is surjective (Nikulin, Theorem 1.14.2), so every
group generator of O(A_L) has a lift. O^+_8(2) acts faithfully on the 255
nonzero elements of A_L, so reading generator words in O(A_L) needs only a
permutation model of degree 255.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.timeout(300)
def test_every_generator_of_o_plus_8_2_lifts_to_an_isometry_inducing_it() -> None:
    L = Lattices(ZZ)("U") + Lattices(ZZ)("E8").twist(-2)
    target = L.discriminant_group().orthogonal_group()
    group_generators = target.group_generators()

    lifts = L.O().discriminant_orthogonal_group_generator_lifts()

    assert int(target.cardinality()) == 348364800
    for label in group_generators.index_set():
        assert lifts.value(label).discriminant_morphism() == group_generators.value(label)
