r"""The arrow category, slices, coslices, subobjects and the core of $\mathbf{Set}$.

A morphism $f \to g$ of $\mathrm{Ar}(C)$ is a pair of edges $(l, r)$ with
$r \circ f = g \circ l$, and squares compose edgewise.  A morphism of the
slice $C/X$ from $f : A \to X$ to $h : B \to X$ is $k : A \to B$ with
$h \circ k = f$; dually for the coslice $X/C$.  The core of $C$ has the
isomorphisms of $C$ as arrows.  Subobjects of a set form a preorder: there
is exactly one arrow $A \hookrightarrow B$ over $X$ when $A \subseteq B$ and
none otherwise.  All of these are the definitions of the constructions.

Throughout, $f : \{0, 1, 2\} \to \{0, 1\}$ sends $0 \mapsto 0$ and
$1, 2 \mapsto 1$, and $\sigma$ is the transposition of $\{0, 1\}$.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _collapse():
    three = Sets.Δ[2]
    two = Sets.Δ[1]
    return Sets().Mor(three, two)(lambda x: two(0) if x == 0 else two(1))


def _transposition():
    two = Sets.Δ[1]
    return Sets().Mor(two, two)(lambda x: two(1) if x == 0 else two(0))


def test_squares_in_the_arrow_category_compose_edgewise() -> None:
    r"""$(g, \mathrm{id}) \circ (f, g) = (g f, g)$ as squares $f \to g \to \mathrm{id}_{1}$."""
    two = Sets.Δ[1]
    point = Sets.Δ[0]
    collapse = _collapse()
    terminal = Sets().Mor(two, point)(lambda _x: point(0))
    identity = Sets().Mor(point, point).identity()
    arrows = Sets().ArrowCategory()
    first = arrows.Mor(arrows(collapse), arrows(terminal))(collapse, terminal)
    second = arrows.Mor(arrows(terminal), arrows(identity))(terminal, identity)
    composite = second * first

    assert first.left() == collapse
    assert first.right() == terminal
    assert composite.left() == terminal * collapse
    assert composite.right() == terminal
    assert composite == arrows.Mor(arrows(collapse), arrows(identity))(terminal * collapse, terminal)


def test_a_pair_of_edges_that_does_not_commute_is_not_a_square() -> None:
    r"""$\sigma \circ f \ne f \circ \mathrm{id}$, since $\sigma f(0) = 1 \ne 0 = f(0)$."""
    collapse = _collapse()
    arrows = Sets().ArrowCategory()
    identity = Sets().Mor(Sets.Δ[2], Sets.Δ[2]).identity()

    assert arrows.Mor(arrows(collapse), arrows(_transposition() * collapse))(identity, _transposition()).right() == _transposition()
    with pytest.raises(ValueError):
        arrows.Mor(arrows(collapse), arrows(collapse))(identity, _transposition())


def test_slice_morphisms_are_maps_over_the_base_and_coslice_morphisms_maps_under_it() -> None:
    r"""Swapping $1, 2$ is an endomorphism of $f$ in $\mathbf{Set}/\{0, 1\}$; swapping $0, 1$ is not."""
    three = Sets.Δ[2]
    two = Sets.Δ[1]
    point = Sets.Δ[0]
    collapse = _collapse()
    slice_category = Sets().SliceOver(two)
    over = Sets().Mor(three, three)(lambda x: three(0) if x == 0 else (three(2) if x == 1 else three(1)))
    not_over = Sets().Mor(three, three)(lambda x: three(1) if x == 0 else (three(0) if x == 1 else three(2)))
    coslice = Sets().CosliceUnder(point)
    at_zero_of_three = Sets().Mor(point, three)(lambda _p: three(0))
    at_zero_of_two = Sets().Mor(point, two)(lambda _p: two(0))

    assert slice_category.Mor(slice_category(collapse), slice_category(collapse))(over).left() == over
    with pytest.raises(ValueError):
        slice_category.Mor(slice_category(collapse), slice_category(collapse))(not_over)
    assert coslice.Mor(coslice(at_zero_of_three), coslice(at_zero_of_two))(collapse).right() == collapse


def test_a_transposition_is_an_involution_in_the_core_of_sets() -> None:
    two = Sets.Δ[1]
    core = Sets().Core()
    transposition = core.Mor(two, two)(_transposition(), _transposition())

    assert transposition * transposition == core.identity(two)
    assert transposition(two(0)) == two(1)


def test_a_point_lies_in_a_two_point_subset_of_three_points_and_not_conversely() -> None:
    three = Sets.Δ[2]
    point = Sets.Δ[0]
    two = Sets.Δ[1]
    subobjects = Sets().Subobjects(three)
    zero = subobjects(Sets().Mor(point, three)(lambda _p: three(0)))
    zero_and_one = subobjects(Sets().Mor(two, three)(lambda x: three(x)))

    assert subobjects.Mor(zero, zero_and_one).cardinality() == cardinal(1)
    assert subobjects.Mor(zero_and_one, zero).cardinality() == cardinal(0)


def test_a_transposition_is_an_isomorphism_arrow_and_an_endomorphism_arrow() -> None:
    arrows = Sets().ArrowCategory()

    assert arrows(_transposition()) in Sets().IsoArrowCategory()
    assert arrows(_transposition()) in Sets().EndArrowCategory()
    assert arrows(_collapse()) not in Sets().IsoArrowCategory()
    assert arrows(_collapse()) not in Sets().EndArrowCategory()
