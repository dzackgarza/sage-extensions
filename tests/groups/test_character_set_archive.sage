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


def test_a_character_equals_the_character_built_from_its_class_function() -> None:
    r"""A character is its class function: the values $(1, 1, 1)$, $(1, -1, 1)$ and $(2, 0, -1)$ of $S_3$'s irreducible characters on the classes of $1$, a transposition and a $3$-cycle determine them, so each is the character that its own class function builds.

    Source: Fulton–Harris, *Representation Theory*, §2.3.
    """
    group = Groups.S(3)

    for character in group.irreducible_characters():
        rebuilt = character.parent()(character.class_function())

        assert rebuilt == character
        assert character == rebuilt
        assert not rebuilt != character
        assert hash(rebuilt) == hash(character)


def test_characters_of_s3_are_equal_exactly_when_they_agree_on_its_elements() -> None:
    r"""The value family on the conjugacy classes determines an ordinary character, so two irreducible characters of $S_3$ are equal exactly when they agree on every element of $S_3$."""
    group = Groups.S(3)
    characters = tuple(group.irreducible_characters())

    for left in characters:
        for right in characters:
            agree = all(left(element) == right(element) for element in group)

            assert (left == right) == agree


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
