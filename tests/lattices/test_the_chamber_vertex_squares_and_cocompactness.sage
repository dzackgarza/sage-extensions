r"""The chamber's vertex squares and cocompactness of the two rank-ten cusp lattices.

`is_cocompact` is stated on the squares of the vertices of the fundamental chamber: an
ideal vertex is a vertex of square zero, lying on the light cone instead of inside it
(:meth:`HyperbolicLattices.ParentMethods.is_cocompact`).  Its computation reads those
vertices as the extreme rays of the cone dual to the wall normals, contracts each ray
against the Gram, and raises the result back into the owned ring.

On Sterk's two cusp lattices `U + E8(-2)` (the `(r, a, delta) = (10, 8, 0)`
2-elementary type, database card `0124`) and `U(2) + E8(-2)` (type `(10, 10, 0)`, card
`0125`), `vinberg_simple_roots` returned the ten walls of the chamber while both
`is_cocompact` and that vertex computation raised

    TypeError: unable to find a common ring for all elements

inside it (sage-extensions#299).  These tests are that regression: `is_cocompact` returns
a decision on both lattices, and it agrees with the vertex squares read through the
public chamber owner, which is a second route to the same rays — the cone's
`primitive_rays()` rather than the dual cone's engine rays.  The lattices are built from
their Gram matrices through `HyperbolicLattices(ZZ)(Lattices(ZZ)(rows))`, which is how the
research record builds them.

The ideal-vertex counts these lattices have are *not* asserted here.  They would be read
from the cards by tag, and cards `0124` and `0125` carry the genus symbol, mass,
discriminant form and root-span rows but no cusp-chamber block: the row that would hold
the count, `integral.cusp_chambers.<subgroup>.ideal_vertices`, exists only on card `029J`,
and there it is a wall count with a printed page, not a vertex count.  So the counts this
operation measures are recorded in `results/issue299-chamber-vertex-rings.md` instead, and
what is asserted here is what has an oracle: the calls return, the two routes agree, and
the rays are what a chamber of a hyperbolic reflection group must have.
"""

from sage_extensions.all import *  # noqa: F401,F403

# The bounds the issue's record uses.  The search completes inside them, which the first
# test asserts through the chamber's own completeness flag rather than assuming.
_MAX_ROOTS = 20
_MAX_DECOMPOSITIONS = 2000


def _hyperbolic_from_gram(named):
    r"""``named`` as a hyperbolic lattice built from its Gram matrix through ``Lattices(ZZ)``."""
    rank = int(named.module_rank())
    gram = named.gram_tensor()
    rows = [[int(gram[i, j]) for j in range(rank)] for i in range(rank)]
    return HyperbolicLattices(ZZ)(Lattices(ZZ)(rows))


def _cusp_lattices():
    r"""`U + E_8(-2)` (card `0124`) and `U(2) + E_8(-2)` (card `0125`), from their Grams."""
    return (
        _hyperbolic_from_gram(NamedLattices.U_E8_2),
        _hyperbolic_from_gram(NamedLattices.E10_2),
    )


def _chamber_ray_squares(lattice):
    r"""The squares of the fundamental chamber's primitive vertex rays, and the chamber."""
    chamber = lattice.fundamental_chamber(
        max_roots=_MAX_ROOTS, max_decompositions=_MAX_DECOMPOSITIONS
    )
    squares = tuple(lattice.b(ray, ray) for ray in chamber.primitive_rays())
    return chamber, squares


def test_the_chamber_rays_of_the_two_cusp_lattices_square_into_one_component() -> None:
    r"""The completed chamber's rays are at least `rank` in number and all on one side.

    The chamber is a fundamental polyhedron of `W(L)` — its wall set is complete at these
    bounds, and the test reads that flag rather than assuming it — so it is a convex cone
    inside *one* component of the light cone.  Its rays therefore have squares of one
    sign, all `0` or all of that sign: `0` is an ideal vertex, on the cone, and the sign of
    the nonzero squares is the lattice's own, positive for a `(1,n)` form and negative for
    `(n,1)`, which is why `is_cocompact` reads only whether a square is zero.

    A full-dimensional pointed cone in `R^rank` has at least `rank` extreme rays, so a
    chamber that answers with fewer has collapsed.
    """
    for lattice in _cusp_lattices():
        chamber, squares = _chamber_ray_squares(lattice)

        assert chamber.is_complete_wall_set() is True
        assert sum(1 for _ in squares) >= int(lattice.module_rank())
        assert all(square >= ZZ(0) for square in squares) or all(
            square <= ZZ(0) for square in squares
        )


def test_cocompactness_is_the_decision_on_those_rays() -> None:
    r"""`is_cocompact` returns a decision, holding exactly when no vertex square is zero.

    The decision is computed from the dual cone's own ray list, while the squares above
    come from the chamber's `primitive_rays()`; two routes to the same vertices, so their
    agreement is a check on both.  An answer still carried as a proposition — what
    `is_cocompact` returns when the search did not complete — is not a decision.
    """
    for lattice in _cusp_lattices():
        _chamber, squares = _chamber_ray_squares(lattice)

        cocompact = lattice.is_cocompact(
            max_roots=_MAX_ROOTS, max_decompositions=_MAX_DECOMPOSITIONS
        )

        assert cocompact in (True, False)
        assert cocompact == all(square != ZZ(0) for square in squares)
