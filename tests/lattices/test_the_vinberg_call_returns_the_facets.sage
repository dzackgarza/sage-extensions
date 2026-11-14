r"""The roots Vinberg's algorithm returns are the facets of the polyhedron they cut out (#401).

Vinberg's algorithm writes down a sequence of normals (38), and E. B. Vinberg,
*On the groups of unit elements of certain quadratic forms*, Math. USSR Sb. 16
(1972), Proposition 4 (p. 28) states of that sequence only that the polyhedron
\(P\) is the intersection of the half-spaces of *all* its roots.  It does not
state that each root of the sequence is a facet of \(P\), and in general it is
not: a half-space the other walls already imply cuts nothing, and dropping it
leaves the same \(P\).  So what is pinned here is the statement the chamber call
makes — every root it returns is a facet, and it returns one root per facet —
and it is read off the chamber's own cone rather than off the enumeration:

* the cone a chamber retains *is* the intersection of the half-spaces of the
  roots it returns, so its ``facet_covectors`` are exactly the half-spaces its
  H-representation needs.  A chamber whose root count equals its facet count is
  therefore a chamber every one of whose roots is a facet;
* the face a single wall cuts has codimension one exactly when that wall is a
  facet, ``face_on_covector(...).dimension()`` being one less than the cone's,
  and a half-space implied by the others cuts a face of codimension two or more.

The second criterion is pinned on a family that does carry a redundant member.
On \(U\oplus A_1\oplus A_1\) the chamber's four walls imply the half-space of the
root \(a_1+a_2\) of square \(-2-2=-4\): the wall \(a_1\) gives \(b(a_1,x)\geq 0\)
and the wall \(a_2-a_1\) gives \(b(a_2,x)\geq b(a_1,x)\), so \(b(a_1+a_2,x)\geq
2b(a_1,x)\geq 0\).  That root is therefore not a facet, and the cone built with
it as a fifth wall still has four facets, the face on it being the subface
where the two walls \(a_1\) and \(a_2-a_1\) both vanish, of dimension \(2\).

\(U\oplus A_1\oplus A_1\) is the lattice `test_nondegenerate_marking_stabilizers.sage`
builds.  No Vinberg sequence in this suite carries a root that is not a facet —
every chamber the tests build returns its own accepted count — so the redundant
member here is supplied by hand, as a root of that lattice, and not by the
enumeration.  The record of which sequences were measured is
`results/issue401-vinberg-facets.md`.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_plus_a1_plus_a1():
    r"""\(U\oplus A_1\oplus A_1\), refined to a hyperbolic lattice, with its two `(-2)` roots."""
    lattice = HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + Lattices(ZZ)("A1") + Lattices(ZZ)("A1"))
    first, second = tuple(
        vector for vector in lattice.module_generators() if lattice.q(vector) == ZZ(-2)
    )
    assert lattice.b(first, second) == ZZ.zero()
    return lattice, first, second


def _chamber_is_its_facets(lattice):
    r"""Check that the chamber of ``lattice`` returns one root per facet, each cutting one."""
    hyperbolic = HyperbolicLattices(ZZ)(lattice)
    chamber = hyperbolic.fundamental_chamber()
    walls = tuple(chamber.wall_roots())
    facets = tuple(chamber.facet_covectors())
    correlation = hyperbolic.algebraic_correlation_morphism()

    assert chamber.is_complete_wall_set() is True
    assert cardinal(sum(1 for _ in walls)) == cardinal(sum(1 for _ in facets))
    assert all(
        int(chamber.face_on_covector(correlation(root)).dimension())
        == int(chamber.dimension()) - 1
        for root in walls
    )


def test_the_walls_of_u_plus_a1_are_its_facets() -> None:
    r"""The triangle of \(U\oplus A_1\), three walls and three facets.

    This is `test_reflection_hyperbolic.sage`'s and
    `test_hyperbolic_archive_reconciliation.sage`'s lattice.  No wall count is
    typed here: both conditions are read off the chamber.
    """
    _chamber_is_its_facets(Lattices(ZZ)("U") + Lattices(ZZ)("A1"))


def test_the_walls_of_u_plus_e8_are_its_facets() -> None:
    r"""The ten walls of \(II_{1,9}\), read off as ten facets.

    `test_hyperbolic_root_lengths_and_vinberg.sage` asserts the ten walls from
    the other side, as the reflection group's Coxeter diagram.
    """
    _chamber_is_its_facets(Lattices(ZZ)("U") + Lattices(ZZ)("E8"))


def test_the_walls_of_u_plus_e8_minus_2_are_its_facets() -> None:
    r"""The ten walls of card `0124`'s cusp lattice \(U\oplus E_8(-2)\).

    This is the cusp lattice whose chamber `test_the_subgroup_cusp_chamber.sage`
    restricts to the reflections of a subgroup.
    """
    _chamber_is_its_facets(NamedLattices.U_E8_2)


def test_the_walls_of_u_2_plus_e8_minus_2_are_its_facets() -> None:
    r"""The ten walls of card `0125`'s cusp lattice \(U(2)\oplus E_8(-2)\).

    The same lattice under the second name `test_the_chamber_vertex_squares_and_cocompactness.sage`
    builds, and the reduction `test_the_isotropic_reduction_image.sage` filters.
    """
    _chamber_is_its_facets(NamedLattices.E10_2)


def test_a_half_space_the_other_walls_imply_is_not_a_facet() -> None:
    r"""The redundant root is dropped by the facet test and its face has codimension two.

    The four walls of the chamber of \(U\oplus A_1\oplus A_1\) imply the
    half-space of the root \(a_1+a_2\), so the cone cut out by those four walls
    and by that extra root is the same cone: it has four facets either way, and
    the face the extra root cuts is the intersection with \(b(a_1+a_2,-)=0\),
    which on the chamber is \(b(a_1,-)=b(a_2,-)=0\) and has dimension \(2\) in a
    cone of dimension \(4\).
    """
    lattice, first, second = _u_plus_a1_plus_a1()
    total = first + second
    chamber = lattice.fundamental_chamber()
    walls = tuple(chamber.wall_roots())
    correlation = lattice.algebraic_correlation_morphism()

    assert lattice.q(total) == ZZ(-4)
    assert total.is_primitive() is True
    assert all(total != root for root in walls)

    extended = walls + (total,)
    cone = lattice.rational_polyhedral_cone(
        tuple(correlation(root) for root in extended), wall_roots=extended
    )

    assert cardinal(sum(1 for _ in cone.wall_roots())) == cardinal(sum(1 for _ in walls)) + cardinal(1)
    assert cardinal(sum(1 for _ in cone.facet_covectors())) == cardinal(sum(1 for _ in walls))
    assert int(cone.face_on_covector(correlation(total)).dimension()) == int(cone.dimension()) - 2
