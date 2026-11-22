r"""Card 0128's Table 4 degree rows, read by tag and compared through the orbit call.

The card is ``0128`` of ``dzackgarza/lattice-database``, the lattice
$U \oplus E_8(-1) = M(1/2)$ of the Enriques paper.  D. Dutour Sikirić and
K. Hulek, *Moduli of polarised Enriques surfaces -- computational aspects*,
J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, Table 4, states for each
degree $2d = 2, \ldots, 72$ the number ``#h``, and the sentence
with the table says which vectors it counts: "the first line shows the number
$\#h$ of orbits of primitive vectors in a given degree".
``tests/cards/lattice-database-enriques.json`` keeps that row as
``primitive_classes``, beside the citation the digest read it from.

Primitivity is not decoration here.  An isometry preserves the content of a
vector, so the square-$2d$ shell is the disjoint union of the classes of
content $c$ with $c^2 \mid 2d$, and the shell holds a non-primitive class from
$2d = 8$ on.  The paper disregards those: "the list of [CDGK, Appendix] also
contains nonprimitive numerical polarizations, which we disregard in our
approach since they do not lead to new moduli spaces" (Section 3.5).  So
the card's row is the orbit count of the primitive stratum, which
``vector_orbit_representatives(2d, content=1)`` returns.

Degree 8 is the smallest degree where the two readings differ -- the shell
holds the content-2 class of a square-2 vector as well -- so the degrees below
decide the reading: 2 is the smallest row of the table, and 8 separates the
primitive stratum from the shell.  The other 34 degrees are the same row of the
same card and are compared by the image job ``enriques-polarization-rows``,
which runs ``tests/enriques_polarization_rows_by_card.py`` over every degree and
every ``gamma-h-N`` card.

This file is a *library-level* test and is not that module's regression guard.
It imports only the session and calls ``NamedLattices.E10.Aut()`` itself, so it
asserts the mathematics of the card's row and cannot see the module's row: a
module that read the shell again would leave every test here green.  The guard
is the module's scheduled ``0128:#h`` row, which runs in the image job and fails
when the stratum is dropped.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_named_lattice_is_the_cards_lattice() -> None:
    r"""$E_{10} = U + E_8(-1)$, the card's $M(1/2)$.

    Card ``0128`` states its lattice as $U \oplus E_8(-1)$, of rank 10 and
    determinant $-1$; the catalogue's $E_{10}$ is $U + E_8$, so the sign of the
    $E_8$ block is what makes the two the same lattice, and it is read off that
    lattice's own signature.
    """
    e8 = NamedLattices.E8
    lattice = NamedLattices.E10

    assert e8.signature_pair().second() == cardinal(8)
    assert lattice.module_rank() == cardinal(10)
    assert lattice.determinant() == ZZ(-1)


def test_the_smallest_degree_row_is_the_cards_orbit_count() -> None:
    r"""Degree 2: one $O(M(1/2))$-orbit of primitive vectors, as the card states."""
    row = card("polarization_counts", "rows")["2"]
    primitive = NamedLattices.E10.Aut().vector_orbit_representatives(2, content=1)

    assert primitive.cardinality() == row["primitive_classes"]


def test_the_degree_eight_row_counts_the_primitive_class_alone() -> None:
    r"""Degree 8: the card's row is the primitive class, and the shell has one more.

    The extra class is the content-2 stratum of a square-2 vector, which is a
    vector of square 8 that is not primitive: content is an isometry invariant,
    so that class is an orbit of the shell and not one of the stratum the card
    counts.
    """
    row = card("polarization_counts", "rows")["8"]
    lattice = NamedLattices.E10
    primitive = lattice.Aut().vector_orbit_representatives(8, content=1)
    shell = lattice.Aut().vector_orbit_representatives(8)

    assert primitive.cardinality() == row["primitive_classes"]
    assert shell.cardinality() > primitive.cardinality()
