r"""The antipodal classes of square $-2$ of $I^\perp/I$, and the parabolic that acts on them.

At a primitive totally isotropic plane $I$ of $T_{\mathrm{En}} = U \oplus U(2) \oplus
E_8(-2)$ the quotient $I^\perp/I$ is negative definite of rank $8$, so it carries finitely
many vectors of square $-2$; $-1$ lies in every congruence subgroup of $O(T_{\mathrm{En}})$,
so the units a stabilizer can move are the antipodal pairs.  `antipodal_root_class_pairs()`
returns those pairs and `antipodal_root_class_orbits(family)` the orbits of the group a
family generates on them.

The five planes are Sterk's five one-cusp types, H. Sterk, *Compactifications of the period
space of Enriques surfaces, Part I*, Math. Z. 207 (1991), (4.2.3) with (4.3.17); the
coordinate pairs are those of the project's one-cusp computation, transcribed in the basis
$(e, f, e', f', \alpha_1, \ldots, \alpha_8)$ of Definition 2.3 of Alexeev--Engel--Garza--
Schäffler, *Compact moduli of Enriques surfaces of degree 2*, Nagoya Math. J. 259 (2025).

The family tested is the one the public call returns, and the three factors of
`parabolic_completeness_decision()` are asserted beside it: the family's transitivity is a
statement about the group it generates, and it is the three factors -- the radical, the
plane actions, the quotient images -- that say that group is the whole parabolic rather
than a subgroup that happens to be transitive.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _plane(lattice, first, second):
    r"""The plane spanned by two coordinate vectors on the lattice's generating set."""
    module_generators = tuple(lattice.module_generators())

    def vector_of(coordinates):
        total = lattice.zero()
        for index, coefficient in enumerate(coordinates):
            if coefficient:
                total = total + coefficient * module_generators[index]
        return total

    return lattice.primitive_isotropic_subobject(vector_of(first), vector_of(second))


def _first_type(lattice):
    r"""Type $\{2,4,5\}$ of (4.3.17)."""
    return _plane(
        lattice,
        (0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0),
        (-2, -2, 0, -2, -1, -1, 0, 0, 0, 0, 0, 0),
    )


def _second_type(lattice):
    r"""Type $\{4,5\}$ of (4.3.17)."""
    return _plane(
        lattice,
        (0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0),
        (-2, -2, -2, 0, -1, 0, 0, 0, 1, 0, 0, 0),
    )


def _third_type(lattice):
    r"""Type $\{3,5\}$ of (4.3.17)."""
    return _plane(
        lattice,
        (2, 2, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0),
        (-2, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0),
    )


def _fourth_type(lattice):
    r"""Type $\{3,4\}$ of (4.3.17)."""
    return _plane(
        lattice,
        (0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0),
        (-2, -2, -1, -1, -1, 0, 1, 0, 0, 0, 0, 0),
    )


def _fifth_type(lattice):
    r"""Type $\{5,5\}$ of (4.3.17)."""
    return _plane(
        lattice,
        (-2, 2, -2, -2, 1, 1, 0, 0, 0, 0, 0, 0),
        (-2, -2, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0),
    )


def _assert_eight_pairs_and_transitive(plane) -> None:
    r"""The quotient has eight antipodal pairs and the returned family moves one to all."""
    lattice = NamedLattices.TEn
    pairs = plane.antipodal_root_class_pairs()
    assert pairs.cardinality() == cardinal(8)
    family = lattice.Aut().stabilizer(plane, action="setwise").group_generators()
    assert family
    orbits = plane.antipodal_root_class_orbits(family)
    assert orbits.cardinality() == cardinal(1)


def _assert_the_three_factors(plane) -> None:
    r"""The family is the whole parabolic: radical, plane actions and quotient images."""
    assert plane.unipotent_radical_index() == cardinal(1)
    assert plane.levi_plane_action_index(trivial_on_quotient=True) == cardinal(1)
    assert plane.levi_quotient_image_index(trivial_on_plane=True) == cardinal(1)
    assert plane.is_parabolic_complete() is True


def test_the_first_type_acts_transitively_and_is_the_whole_parabolic() -> None:
    r"""Type $\{2,4,5\}$: eight pairs, one orbit, three factors $1$."""
    plane = _first_type(NamedLattices.TEn)
    _assert_eight_pairs_and_transitive(plane)
    _assert_the_three_factors(plane)


def test_the_second_type_acts_transitively_and_is_the_whole_parabolic() -> None:
    r"""Type $\{4,5\}$: eight pairs, one orbit, three factors $1$."""
    plane = _second_type(NamedLattices.TEn)
    _assert_eight_pairs_and_transitive(plane)
    _assert_the_three_factors(plane)


def test_the_third_type_acts_transitively_and_is_the_whole_parabolic() -> None:
    r"""Type $\{3,5\}$: eight pairs, one orbit, three factors $1$."""
    plane = _third_type(NamedLattices.TEn)
    _assert_eight_pairs_and_transitive(plane)
    _assert_the_three_factors(plane)


def test_the_fourth_type_acts_transitively_and_is_the_whole_parabolic() -> None:
    r"""Type $\{3,4\}$: eight pairs, one orbit, three factors $1$."""
    plane = _fourth_type(NamedLattices.TEn)
    _assert_eight_pairs_and_transitive(plane)
    _assert_the_three_factors(plane)


def test_the_fifth_type_acts_transitively_and_is_the_whole_parabolic() -> None:
    r"""Type $\{5,5\}$: eight pairs, one orbit, three factors $1$."""
    plane = _fifth_type(NamedLattices.TEn)
    _assert_eight_pairs_and_transitive(plane)
    _assert_the_three_factors(plane)
