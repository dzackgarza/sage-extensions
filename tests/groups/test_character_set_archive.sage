r"""Ordinary characters of $S_3$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_s3_has_three_irreducible_characters_of_degrees_one_one_two() -> None:
    r"""$S_3$ has three conjugacy classes, hence three irreducible characters, of degrees $1, 1, 2$ with $1 + 1 + 4 = 6$.

    Source: Fulton–Harris, *Representation Theory*, §1.3.
    """
    group = Groups.S(3)
    characters = group.irreducible_characters()

    assert characters.cardinality() == 3
    assert sorted(character.degree() for character in characters) == [1, 1, 2]
    assert sum(character.degree() ** 2 for character in characters) == 6
    assert all(character(group.one()) == character.degree() for character in characters)


def test_a_sum_of_two_irreducible_characters_has_exactly_those_constituents() -> None:
    r"""$\chi = \mathbb{1} + \chi_{\mathrm{std}}$ (a linear plus the standard character) has degree $3$ and constituents $\{\mathbb{1}, \chi_{\mathrm{std}}\}$."""
    group = Groups.S(3)
    characters = group.irreducible_characters()
    linear = next(character for character in characters if character.degree() == 1)
    standard = next(character for character in characters if character.degree() == 2)
    combined = linear + standard
    constituents = combined.irreducible_constituents()

    assert combined.degree() == 3
    assert constituents.cardinality() == 2
    assert linear in constituents
    assert standard in constituents
