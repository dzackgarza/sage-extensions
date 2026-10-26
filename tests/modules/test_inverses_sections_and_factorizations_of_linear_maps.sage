r"""Inverses, preimages, sections, retractions and factorizations of maps of free modules.

A linear map $f$ of free modules of equal rank is invertible over $R$ exactly when
$\det f \in R^\times$; the preimage of $w$ under an isomorphism is $f^{-1}(w)$.  A surjection of
free modules $p$ splits: a section $s$ has $p s = \mathrm{id}$, and a split injection $i$ has a
retraction $r$ with $r i = \mathrm{id}$.  A map $f: A \to X$ factors through a monomorphism
$j: B \to X$, $f = j k$, exactly when $f(A) \subseteq j(B)$, and then $k$ is unique.  Every value is computed by hand.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_the_inverse_of_a_determinant_one_map_of_the_rational_plane() -> None:
    r"""$f(e_0) = 2e_0 + e_1$, $f(e_1) = e_0 + e_1$ has $\det f = 1$ and $f^{-1}(e_0) = e_0 - e_1$,
    since $f(e_0 - e_1) = e_0$."""
    plane = QQ ^ 2
    x, y = plane.module_generator(0), plane.module_generator(1)
    f = plane.End()({0: 2 * x + y, 1: x + y})

    assert f.determinant() == 1
    assert f.is_surjective()
    assert f.inverse()(x) == x - y
    assert f.inverse()(y) == 2 * y - x
    assert f * f.inverse() == plane.End().one()
    assert (2 * f)(x) == 4 * x + 2 * y


def test_the_preimage_of_e0_under_a_determinant_one_map_is_e0_minus_e1() -> None:
    r"""$f(e_0 - e_1) = (2e_0 + e_1) - (e_0 + e_1) = e_0$."""
    plane = QQ ^ 2
    x, y = plane.module_generator(0), plane.module_generator(1)
    f = plane.End()({0: 2 * x + y, 1: x + y})

    assert f.preimage(x) == x - y


def test_the_swap_of_the_rational_plane_is_an_involution_in_its_automorphism_group() -> None:
    r"""$\sigma: e_0 \leftrightarrow e_1$ has $\sigma^2 = 1$ and $(\sigma + f)(e_0) = 2e_0 + 2e_1$."""
    plane = QQ ^ 2
    x, y = plane.module_generator(0), plane.module_generator(1)
    swap = plane.Aut()(plane.End()({0: y, 1: x}))
    f = plane.End()({0: 2 * x + y, 1: x + y})

    assert swap * swap == plane.Aut().one()
    assert (plane.End()({0: y, 1: x}) + f)(x) == 2 * x + 2 * y


def test_the_swap_of_the_rational_plane_has_order_two() -> None:
    r"""$\sigma \neq 1$ and $\sigma^2 = 1$."""
    plane = QQ ^ 2
    x, y = plane.module_generator(0), plane.module_generator(1)

    assert plane.Aut()(plane.End()({0: y, 1: x})).order() == 2


def test_a_projection_of_the_rational_three_space_onto_the_plane_has_a_section() -> None:
    r"""$p(e_0) = e_0$, $p(e_1) = e_1$, $p(e_2) = e_0 + e_1$ is onto, so $p s = \mathrm{id}$."""
    space, plane = QQ ^ 3, QQ ^ 2
    x, y = plane.module_generator(0), plane.module_generator(1)
    projection = space.Mor(plane)({0: x, 1: y, 2: x + y})

    assert projection * projection.section() == plane.End().one()


def test_the_inclusion_of_the_plane_into_three_space_has_a_retraction() -> None:
    r"""$i(e_j) = e_j$ for $j = 0, 1$ is a split injection, so $r i = \mathrm{id}$."""
    space, plane = QQ ^ 3, QQ ^ 2
    inclusion = plane.Mor(space)({0: space.module_generator(0), 1: space.module_generator(1)})

    assert inclusion.retraction() * inclusion == plane.End().one()


def test_an_inclusion_factors_through_itself_by_the_identity() -> None:
    r"""$i = i \circ \mathrm{id}$ and the factor is unique."""
    space, plane = QQ ^ 3, QQ ^ 2
    inclusion = plane.Mor(space)({0: space.module_generator(0), 1: space.module_generator(1)})

    assert inclusion.factor_through(inclusion) == plane.End().one()


def test_diag_2_1_factors_through_the_shear_of_the_integer_plane() -> None:
    r"""$g(u) = u + v$, $g(v) = v$ is an automorphism of $\mathbb Z^2$; $h = \operatorname{diag}(2, 1)$ equals
    $g k$ with $k = g^{-1} h$: $k(u) = 2u - 2v$, $k(v) = v$."""
    lattice = ZZ ^ 2
    u, v = lattice.module_generator(0), lattice.module_generator(1)
    g = lattice.End()({0: u + v, 1: v})
    h = lattice.End()({0: 2 * u, 1: v})
    k = h.factor_through(g)

    assert h.determinant() == 2
    assert not h.is_surjective()
    assert g * k == h
    assert k(u) == 2 * u - 2 * v
    assert k(v) == v


def test_the_inverse_of_a_unimodular_integer_map_is_integral() -> None:
    r"""$g(u) = u + v$, $g(v) = v$ has $\det g = 1$ and $g^{-1}(u) = u - v$ in $\mathbb Z^2$."""
    lattice = ZZ ^ 2
    u, v = lattice.module_generator(0), lattice.module_generator(1)
    g = lattice.End()({0: u + v, 1: v})

    assert g.inverse()(u) == u - v
    assert g.inverse() * g == lattice.End().one()


def test_the_inclusion_of_the_doubled_line_does_not_factor_through_twice_the_line() -> None:
    r"""$j: \mathbb Z \to \mathbb Z^2$, $1 \mapsto 2u$ has image $2\mathbb Z u \not\ni u$, so
    $f: 1 \mapsto u$ does not factor through $j$, while $1 \mapsto 4u$ factors by $2$."""
    line, lattice = ZZ ^ 1, ZZ ^ 2
    u = lattice.module_generator(0)
    j = line.Mor(lattice)({0: 2 * u})
    doubled = line.Mor(lattice)({0: 4 * u})

    assert doubled.factor_through(j)(line.module_generator(0)) == 2 * line.module_generator(0)
    with pytest.raises(ValueError):
        line.Mor(lattice)({0: u}).factor_through(j)
