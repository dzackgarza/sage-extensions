r"""The plane projection's right-coset walk, and the supplied right-coset counterexample.

The plane projection whose completeness `levi_lift_generators` rests on is

.. math:: \Gamma' = \{Q_1 \in GL_2(ZZ) : Q_1 \text{ has an integral lift with } Q_3 = 1\},

a congruence subgroup (`_levi_plane_congruence_level`), and it is presented one
determinant half at a time: the special-linear part `H = \Gamma' \cap SL_2(ZZ)`
from the action of the two elementary shears on its right cosets, and the
determinant-reversing part from the same action started at `diag(-1,1)`.
`right_coset_action` is that walk, and these are its two claims on specimens
small enough to compute the answer independently.

**A right coset is `Hx`, and the comparison is `x y^{-1} in H`.**  The walk
multiplies a representative on the right, `x -> x g`, so the classes it reaches
are the right cosets `Hx = {h x}`, and two elements name the same one exactly
when `x y^{-1} in H`.  The left-coset comparison `y^{-1} x in H` is a different
partition of the same group whenever `H` is not normal, and it is what a left
action would enumerate.  At a reversing element there is a second difference:
`y^{-1} = -adj(y)` because `det y = -1`, so a comparison written with the
adjugate alone has the wrong sign as well as the wrong order.

**The supplied example.**  `H = <[[0,3],[5,5]], [[0,5],[3,3]]>` in
`SL_2(ZZ/8)`, of order twelve and abelian, and `a = [[1,3],[5,6]]`, of
determinant `-1`; the reversing half of `GL_2(ZZ/8)` has 384 classes and the
walk's reach is its 32 right cosets.  So this is not a case that needs a
non-normal subgroup to separate the two spellings: on it the two comparisons
already disagree on 5760 of the 147456 ordered pairs of the reversing half, and
a walk comparing `y^{-1} x` reaches eight cosets, none of them `a`'s.

**The non-abelian cases.**  `SL_2(ZZ/5)` is non-abelian and
`H = <[[1,1],[0,1]]>` has order five there and is not normal, so the left and
right partitions of the same set genuinely differ; the walk is asserted to
enumerate the right one, in the special-linear half and in the reversing half.
"""

from sage_extensions.all import *

_LEVEL = 8
_SEED = matrix([[-1, 0], [0, 1]])
_SHEARS = (matrix([[1, 1], [0, 1]]), matrix([[1, 0], [1, 1]]))


def _class_of(entry, modulus):
    r"""The class of ``entry`` modulo ``modulus``, its four entries in row order."""
    return tuple(int(value) % modulus for value in entry.list())


def _product(first, second, modulus):
    r"""The class of the product of two classes, `(a b; c d)(e f; g h) = (ae+bg, af+bh; ce+dg, cf+dh)`."""
    return (
        (first[0] * second[0] + first[1] * second[2]) % modulus,
        (first[0] * second[1] + first[1] * second[3]) % modulus,
        (first[2] * second[0] + first[3] * second[2]) % modulus,
        (first[2] * second[1] + first[3] * second[3]) % modulus,
    )


def _inverse_of(entry, modulus):
    r"""The class of the inverse of a class of determinant `\pm 1`, modulo ``modulus``."""
    determinant = (entry[0] * entry[3] - entry[1] * entry[2]) % modulus
    scalar = pow(determinant, -1, modulus)
    return (
        scalar * entry[3] % modulus,
        -scalar * entry[1] % modulus,
        -scalar * entry[2] % modulus,
        scalar * entry[0] % modulus,
    )


def _subgroup_of(classes, modulus):
    r"""The subgroup the classes generate, by closure under multiplication."""
    subgroup = {(1, 0, 0, 1)}
    frontier = [(1, 0, 0, 1)]
    while frontier:
        current = frontier.pop()
        for element in classes:
            product = _product(current, element, modulus)
            if product not in subgroup:
                subgroup.add(product)
                frontier.append(product)
    return subgroup


def _classes_of_determinant(modulus, determinant):
    r"""Every class of `GL_2(ZZ/modulus)` whose determinant is ``determinant`` modulo ``modulus``."""
    return {
        (first, second, third, fourth)
        for first in range(modulus)
        for second in range(modulus)
        for third in range(modulus)
        for fourth in range(modulus)
        if (first * fourth - second * third) % modulus == determinant % modulus
    }


def _right_cosets(subgroup, classes, modulus):
    r"""The right cosets `Hx = \{h x\}` of ``subgroup`` named by ``classes``."""
    return {
        frozenset(_product(element, representative, modulus) for element in subgroup)
        for representative in classes
    }


def _left_cosets(subgroup, classes, modulus):
    r"""The left cosets `xH = \{x h\}` of ``subgroup`` named by ``classes``."""
    return {
        frozenset(_product(representative, element, modulus) for element in subgroup)
        for representative in classes
    }


def _the_supplied_subgroup():
    r"""`H = <[[0,3],[5,5]], [[0,5],[3,3]]>` in `SL_2(ZZ/8)`, and the reversing class `a = [[1,3],[5,6]]`."""
    subgroup = _subgroup_of(
        (
            _class_of(matrix([[0, 3], [5, 5]]), _LEVEL),
            _class_of(matrix([[0, 5], [3, 3]]), _LEVEL),
        ),
        _LEVEL,
    )
    return subgroup, _class_of(matrix([[1, 3], [5, 6]]), _LEVEL)


def _reaches(subgroup, modulus):
    r"""The membership predicate of ``subgroup``, read on a matrix of the walk."""
    return lambda entry: _class_of(entry, modulus) in subgroup


def test_the_walk_reaches_the_reversing_right_coset_of_the_supplied_example() -> None:
    r"""The reversing half of `GL_2(ZZ/8)` is 32 right cosets of `H`, and the walk reaches all of them.

    `a` is in the reversing half and `H a` is its non-empty right coset; the walk
    started at `diag(-1,1)` reaches it exactly when it compares `x y^{-1}`,
    which is the comparison the plane projection needs.
    """
    subgroup, reversing = _the_supplied_subgroup()
    representatives, tables, _ = right_coset_action(
        _SHEARS, _reaches(subgroup, _LEVEL), start=_SEED
    )
    reached = {
        frozenset(_product(element, _class_of(entry, _LEVEL), _LEVEL) for element in subgroup)
        for entry in representatives
    }
    half = _classes_of_determinant(_LEVEL, _LEVEL - 1)
    assert reached == _right_cosets(subgroup, half, _LEVEL)
    assert frozenset(
        _product(element, reversing, _LEVEL) for element in subgroup
    ) in reached


def test_the_walk_enumerates_the_special_linear_right_cosets_of_the_supplied_example() -> None:
    r"""The same subgroup's special-linear half: the walk from the identity reaches its 32 right cosets."""
    subgroup, _ = _the_supplied_subgroup()
    representatives, tables, _ = right_coset_action(_SHEARS, _reaches(subgroup, _LEVEL))
    reached = {
        frozenset(_product(element, _class_of(entry, _LEVEL), _LEVEL) for element in subgroup)
        for entry in representatives
    }
    half = _classes_of_determinant(_LEVEL, 1)
    assert reached == _right_cosets(subgroup, half, _LEVEL)
    assert all(
        _product(
            _class_of(representatives[index], _LEVEL),
            _class_of(_SHEARS[position], _LEVEL),
            _LEVEL,
        )
        in frozenset(
            _product(element, _class_of(representatives[target], _LEVEL), _LEVEL)
            for element in subgroup
        )
        for position in (0, 1)
        for index, target in tables[position].items()
    )


def test_the_supplied_example_separates_the_right_and_left_coset_comparisons() -> None:
    r"""On this specimen the two comparisons disagree, so the walk's answer is not the left one.

    `x y^{-1} in H` and `y^{-1} x in H` are conjugates, so they agree for every
    pair when `H` is normal; here they differ on 5760 of the 147456 ordered pairs
    of the reversing half, and the right coset partition the walk enumerates is
    not the left one.
    """
    subgroup, _ = _the_supplied_subgroup()
    half = _classes_of_determinant(_LEVEL, _LEVEL - 1)
    assert sum(
        1
        for first in half
        for second in half
        if (_product(first, _inverse_of(second, _LEVEL), _LEVEL) in subgroup)
        != (_product(_inverse_of(second, _LEVEL), first, _LEVEL) in subgroup)
    ) == 5760
    assert _right_cosets(subgroup, half, _LEVEL) != _left_cosets(subgroup, half, _LEVEL)


def test_the_walk_enumerates_the_right_cosets_of_a_non_normal_subgroup() -> None:
    r"""In the non-abelian `SL_2(ZZ/5)`, `H = <[[1,1],[0,1]]>` has order five and is not normal.

    The walk from the identity must enumerate the 24 right cosets of `H`, and
    from `diag(-1,1)` the 48 right cosets of `H` in the reversing half of
    `GL_2(ZZ/5)`; in each, the right partition is not the left one.
    """
    subgroup = _subgroup_of((_class_of(matrix([[1, 1], [0, 1]]), 5),), 5)
    assert subgroup <= _classes_of_determinant(5, 1)
    special = _classes_of_determinant(5, 1)
    reversing = _classes_of_determinant(5, 5 - 1)
    representatives, _, _ = right_coset_action(_SHEARS, _reaches(subgroup, 5))
    reached = {
        frozenset(_product(element, _class_of(entry, 5), 5) for element in subgroup)
        for entry in representatives
    }
    assert reached == _right_cosets(subgroup, special, 5)
    assert reached != _left_cosets(subgroup, special, 5)
    reversing_representatives, _, _ = right_coset_action(
        _SHEARS, _reaches(subgroup, 5), start=_SEED
    )
    reversing_reached = {
        frozenset(_product(element, _class_of(entry, 5), 5) for element in subgroup)
        for entry in reversing_representatives
    }
    assert reversing_reached == _right_cosets(subgroup, reversing, 5)
    assert reversing_reached != _left_cosets(subgroup, reversing, 5)
