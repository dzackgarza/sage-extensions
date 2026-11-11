r"""``primitive_orbit_series`` returns on the catalogued lattices 0016 and 026E (#345).

An indefinite lattice has no bounded positive or negative fibre, so the series
reduces to its ``constant`` term: the orbits of primitive isotropic *lines* under
``O``, ``SO``, ``Otilde``, ``SOtilde`` and their ``+`` pieces, which is the cusp
count a Baily-Borel boundary is made of.  On a lattice that contains a hyperbolic
plane those orbits exist, so the call must return them.

The two specimens are cards of ``dzackgarza/lattice-database`` read by tag:
``0016`` is the hyperbolic plane ``U`` (rank 2, signature ``(1, 1)``) and ``026E``
is ``U + D4(-1) + A1(-1)`` (rank 7, signature ``(1, 6)``).  Each lattice is built
from the card's own ``gram_tensor``, and every term the call returns is compared
with the card's ``integral.primitive_orbits`` row for the same subgroup, so no
count here is typed.

A row the card does not state is recorded, not asserted: the card states all
eight subgroups for both lattices today, and the check below is that each stated
row is compared.
"""

from sage_extensions.all import *

CATALOGUED = ("0016", "026E")


def stated_series(tag):
    r"""The card ``tag``'s primitive-orbit rows, read by tag from the digest."""
    return card("primitive_orbit_series", tag)


def catalogued_lattice(tag):
    r"""The lattice card ``tag`` states, built from its own Gram matrix."""
    return Lattices(ZZ)(stated_series(tag)["gram"])


def test_the_series_returns_on_both_catalogued_lattices() -> None:
    r"""Both calls return, and each term is the card's own row for that subgroup.

    ``026E`` contains ``U`` and ``0016`` is ``U``, so each has primitive isotropic
    vectors: the ``O`` row's ``constant`` is positive on both, which keeps the
    comparison from holding of two empty series.
    """
    for tag in CATALOGUED:
        stated = stated_series(tag)
        lattice = catalogued_lattice(tag)
        series = lattice.primitive_orbit_series()

        assert int(lattice.module_rank()) == int(stated["rank"])
        assert int(series["O"]["constant"]) > 0
        for subgroup, row in stated["rows"].items():
            assert int(series[subgroup]["constant"]) == int(row["constant"]), (tag, subgroup)


def test_the_catalogued_lattices_are_the_ones_the_cards_name() -> None:
    r"""The card's rank, signature and defining form are the lattice's, so the comparison is about that lattice.

    A rank-and-signature check alone would not say the Gram matrix was read: the
    determinant and the diagonal of the form are compared too, and for ``0016``
    the lattice is checked to be the hyperbolic plane by an explicit isotropic
    basis vector of divisibility one.
    """
    for tag in CATALOGUED:
        stated = stated_series(tag)
        lattice = catalogued_lattice(tag)
        basis = tuple(lattice.module_generators())

        assert int(lattice.module_rank()) == int(stated["rank"])
        assert [int(entry) for entry in lattice.signature()] == [int(entry) for entry in stated["signature"]]
        assert int(lattice.determinant()) == int(stated["determinant"])
        assert [
            [int(lattice.b(left, right)) for right in basis] for left in basis
        ] == stated["gram"]

    hyperbolic = catalogued_lattice("0016")
    basis = tuple(hyperbolic.module_generators())
    assert hyperbolic.q(basis[0]) == ZZ(0)
    assert hyperbolic.div(basis[0]) == ZZ(1)
    assert hyperbolic.b(basis[0], basis[1]) == ZZ(1)
