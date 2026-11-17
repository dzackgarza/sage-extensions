r"""A cusp row is its orbits: one point an orbit, admitted as the walk draws it.

``cusps`` yields one representative per orbit, so the cusps of a row are pairwise
distinct orbits, and the row's enumeration needs no table of its points: a cusp's
hash is constant over its universe -- two cusps of one orbit need not share a
span, so a cusp has no cheap canonical key -- and a table of them compares every
cusp of the row with every other, each comparison a transporter question.  The
row is therefore admitted as it is produced, with the cusps' own identity as the
inverse on its image.

Two statements are asserted here, and neither is a restatement of the other.
First, the obligation the admission carries: the cusps the walk yields are
pairwise distinct orbits, which is read off the cusps' own equality, one
question a pair.  An admission that identifies repetitions would hide a walk
that yielded one orbit twice; this one does not identify them, it states there
are none, so a repeated orbit would stand in the row twice and is asserted
absent here.  Second, the inverse the admission supplies: each cusp of the row
answers its own position, is admitted by the row, and names a primitive totally
isotropic sublattice of the row's rank whose own membership in the cusp holds.

The specimens are two lattices of the ``U + U(2) + <-2k>`` family, whose kernel
plane rows hold two and three orbits and whose line rows three and four, and
``E10 = U + E8``, whose kernel plane row is empty -- the one size at which the
admission has no points to admit.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _the_row_is_its_orbits(row, rank) -> None:
    r"""The row's cusps are pairwise distinct orbits of primitive isotropic sublattices of ``rank``."""
    cusps = tuple(row)
    assert all(
        one != other
        for position, one in enumerate(cusps)
        for other in cusps[position + 1 :]
    )
    for position, cusp in enumerate(cusps):
        representative = cusp.representative()
        assert representative.module_rank() == rank
        assert representative.is_primitive() is True
        assert representative.is_totally_isotropic() is True
        assert representative in cusp
        assert cusp in row
        assert row.enumeration_inverse()(cusp) == position


def test_the_plane_cusps_of_a_kernel_row_are_distinct_orbits() -> None:
    r"""Two plane cusps on ``U + U(2) + <-2>``, the kernel's plane row."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U").twist(2) + Lattices(ZZ)([[-2]])
    subgroup = lattice.stable_orthogonal_group()

    row = subgroup.cusps(2)

    assert row.cardinality() == cardinal(2)
    _the_row_is_its_orbits(row, cardinal(2))


def test_the_line_cusps_of_a_kernel_row_are_distinct_orbits() -> None:
    r"""Three line cusps on ``U + U(2) + <-2>``, the kernel's line row."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U").twist(2) + Lattices(ZZ)([[-2]])
    subgroup = lattice.stable_orthogonal_group()

    row = subgroup.cusps(1)

    assert row.cardinality() == cardinal(3)
    _the_row_is_its_orbits(row, cardinal(1))


def test_the_cusps_of_the_next_lattice_of_the_family_are_distinct_orbits() -> None:
    r"""Three plane cusps and four line cusps on ``U + U(2) + <-4>``."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U").twist(2) + Lattices(ZZ)([[-4]])
    subgroup = lattice.stable_orthogonal_group()

    plane_row = subgroup.cusps(2)
    line_row = subgroup.cusps(1)

    assert plane_row.cardinality() == cardinal(3)
    assert line_row.cardinality() == cardinal(4)
    _the_row_is_its_orbits(plane_row, cardinal(2))
    _the_row_is_its_orbits(line_row, cardinal(1))


def test_an_empty_plane_row_is_admitted_with_no_points() -> None:
    r"""``E10 = U + E8`` has no primitive isotropic plane in its kernel's row."""
    lattice = NamedLattices.E10
    subgroup = lattice.stable_orthogonal_group()

    row = subgroup.cusps(2)

    assert row.cardinality() == cardinal(0)
    assert tuple(row) == ()


def test_the_ambient_line_cusps_of_a_lattice_are_distinct_orbits() -> None:
    r"""Two ambient line cusps on ``U + U(2) + <-4>``, the full orthogonal group's row.

    The full group's cusp keeps a representative rather than a span, and its hash
    is constant for the same reason -- representatives are not canonical -- so
    its row is admitted the same way.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U").twist(2) + Lattices(ZZ)([[-4]])

    row = lattice.Aut().cusps(1)

    assert row.cardinality() == cardinal(2)
    _the_row_is_its_orbits(row, cardinal(1))
