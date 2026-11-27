r"""The section of a surjection of sets is an arrow of $\mathbf{Set}$, not a table of preimages.

A section of $e: X \to Y$ is a map $s: Y \to X$ with $e \circ s = id_Y$; then
every point of $Y$ is the value $e(s(y))$ at the point $s(y)$ chosen in its
fibre, so a section is a witness that $e$ is surjective.  Two specimens:
parity $\{0, \dots, 5\} \to \{0, 1\}$, whose section the owner derives once
from the preimage table, and $n \mapsto \lfloor n/2 \rfloor$ on $\mathbb{Z}$,
whose fibres are infinite and whose section is a chosen datum.
"""

import pytest

from sage_extensions.all import *


def test_the_derived_section_of_parity_is_an_arrow_of_sets() -> None:
    r"""Parity $\{0, \dots, 5\} \to \{0, 1\}$ has a section, and the composite is $id_{\{0,1\}}$."""
    source = Sets.Δ[5]
    target = Sets.Δ[1]
    parity = Sets().Mor(source, target)(lambda point: target(point % 2))
    identity = Sets().Mor(target, target).identity()
    section = parity.section()
    composite = parity * section

    assert parity.is_surjective() is True
    assert section.parent() is Sets().Mor(target, source)
    assert section.domain() is target
    assert section.codomain() is source
    assert composite.parent() is Sets().Mor(target, target)
    assert composite.domain() is target and composite.codomain() is target
    assert composite.is_identity() is True
    assert (composite == identity) is True
    assert section.is_injective() is True
    assert all(parity(section(point)) == point for point in target)
    assert all(int(section(point)) % 2 == int(point) for point in target)
    assert Sets().Mor(target, target)(
        lambda point: parity(section(point))
    ) == identity


def test_the_section_of_a_surjection_onto_the_integers_is_a_chosen_arrow_of_sets() -> None:
    r"""$n \mapsto \lfloor n/2 \rfloor$ is onto $\mathbb{Z}$, and $m \mapsto 2m$ is a section of it.

    The fibres are infinite, so no preimage table enumerates them: the section is
    a chosen map, and it decides the surjectivity that the map's own data leaves
    as a proposition.
    """
    integers = ZZ
    half = Sets().Mor(integers, integers)(lambda point: ZZ(point) // 2)
    doubling = Sets().Mor(integers, integers)(lambda point: 2 * ZZ(point))
    identity = Sets().Mor(integers, integers).identity()

    assert half.is_surjective() is not True
    half.select_section(doubling)
    section = half.section()

    assert half.has_selected_section() is True
    assert half.selected_section() is section
    assert section is doubling
    assert section.domain() is half.codomain()
    assert section.codomain() is half.domain()
    assert half.is_surjective() is True
    assert half in Sets().Epi(integers, integers)
    assert (half * section) == identity
    assert (half * section).is_identity() is True
    assert all(
        half(section(ZZ(point))) == ZZ(point) for point in (-3, 0, 1, 7, 10**6)
    )
    assert all(half(ZZ(2 * point)) == ZZ(point) for point in (-3, 0, 1, 7, 10**6))


def test_a_choice_that_is_not_a_section_is_refused_and_a_map_with_a_missing_value_has_none() -> None:
    r"""Over $\{0,1\}$ the equation is decided: the constant choice is refused, and so is a missing value."""
    source = Sets.Δ[5]
    target = Sets.Δ[1]
    parity = Sets().Mor(source, target)(lambda point: target(point % 2))
    constant = Sets().Mor(target, source)(lambda _point: source(0))

    with pytest.raises(ValueError):
        parity.select_section(constant)
    assert parity.has_selected_section() is False

    three = Sets.Δ[2]
    drops_two = Sets().Mor(source, three)(lambda point: three(min(int(point), 1)))
    with pytest.raises(ValueError):
        drops_two.section()


def test_sections_compose_and_the_composite_splits_the_composite_surjection() -> None:
    r"""Sections compose: if $s_1$ splits $e_1$ and $s_2$ splits $e_2$, then $s_1 s_2$ splits $e_2 e_1$.

    On finite ordinals the equation $e_2 e_1 s_1 s_2 = id$ is decided at every
    point, so this is the right-inverse equation read off the values and not off
    the recorded datum.
    """
    eight = Sets.Δ[7]
    four = Sets.Δ[3]
    two = Sets.Δ[1]
    mod_four = Sets().Mor(eight, four)(lambda point: four(point % 4))
    mod_two = Sets().Mor(four, two)(lambda point: two(point % 2))
    composite = mod_two * mod_four
    section = mod_four.section() * mod_two.section()
    identity = Sets().Mor(two, two).identity()

    assert section.domain() is two
    assert section.codomain() is eight
    assert composite.domain() is eight and composite.codomain() is two
    assert (composite * section) == identity
    assert (composite * section).is_identity() is True
    assert all(composite(section(point)) == point for point in two)
    assert all(int(section(point)) % 4 == int(point) for point in two)


def test_the_section_of_an_infinite_group_surjection_is_an_arrow_of_underlying_sets() -> None:
    r"""$F(a,b) \twoheadrightarrow F(a)$, $b \mapsto 1$, splits by $a \mapsto a$: $U(e) U(s) = id_{U(F(a))}$.

    The section is the underlying map of an actual group morphism, so it composes
    with that group's inclusion, and the set equation is decided although
    $F(a)$ is infinite.
    """
    free_two = Groups.Free(2)
    free_one = Groups.Free(1)
    first, second = tuple(free_two.free_basis())
    label = tuple(free_one.free_basis())[0]
    generator = free_one.free_generator(label)
    projection = free_two.Mor(free_one)(
        {first: generator, second: free_one.one()}
    )
    inclusion = free_one.Mor(free_two)({label: free_two.free_generator(first)})
    forget = Groups().underlying_set()
    underlying = forget(projection)
    section = forget(inclusion)

    assert forget(free_two) is free_two
    assert underlying.domain() is free_two and underlying.codomain() is free_one
    assert underlying in Sets().Mor(free_two, free_one)
    assert section.domain() is free_one and section.codomain() is free_two
    assert underlying.is_surjective() is not True
    underlying.select_section(section)
    assert underlying.section() is section
    assert underlying.is_surjective() is True
    assert underlying in Sets().Epi(free_two, free_one)
    assert (underlying * section) == Sets().Mor(free_one, free_one).identity()
    assert all(
        underlying(section(generator**power)) == generator**power
        for power in (-2, 0, 1, 3)
    )
