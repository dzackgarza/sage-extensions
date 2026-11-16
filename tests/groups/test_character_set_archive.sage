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


def test_a_character_equals_the_character_its_class_function_builds() -> None:
    r"""The character that a character's own class function builds is that character.

    A character of $G$ is determined by its values on the conjugacy classes,
    and its class function by its values on the classes' representatives; the
    hash already reads those values.

    Source: Milne, *Group Theory*, v4.01, Proposition 7.44, p. 116.
    """
    group = Groups.S(3)

    for character in group.irreducible_characters():
        rebuilt = character.parent()(character.class_function())

        assert rebuilt == character
        assert character == rebuilt
        assert not rebuilt != character
        assert hash(rebuilt) == hash(character)


def test_characters_built_by_different_routes_with_equal_values_are_equal() -> None:
    r"""$S_3$'s trivial character and its character of degree $1$ that takes $1$ on a transposition are one character, $\chi_1 + \chi_2$ read back by ``character`` from its values is $\chi_1 + \chi_2$, and the two characters of degree $1$ are unequal since they differ on a transposition.

    Source: Milne, *Group Theory*, v4.01, Proposition 7.44, p. 116.
    """
    group = Groups.S(3)
    transposition = next(element for element in group if element.order() == 2)
    irreducibles = tuple(group.irreducible_characters())
    trivial = group.trivial_character()
    linear = next(
        character
        for character in irreducibles
        if character.degree() == 1 and character(transposition) == 1
    )
    sign = next(
        character
        for character in irreducibles
        if character.degree() == 1 and character(transposition) == -1
    )

    assert trivial == linear
    assert linear == trivial
    assert trivial != sign

    combined = linear + sign
    representatives = group.conjugacy_classes_representatives()
    written = group.character(
        tuple(combined(representative) for representative in representatives)
    )

    assert written == combined
    assert combined == written
    assert written != linear


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
