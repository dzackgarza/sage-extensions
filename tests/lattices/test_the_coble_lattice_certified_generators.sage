r"""The Coble lattice's certified discriminant-kernel generators, on the lattice the source builds.

``T_Co = <2> + U(2) + E8(-2)`` is even, of rank eleven and signature ``(2, 9)``,
with ``|A_L| = 2^11``; ``L = 2L^#`` then identifies ``A_L`` with ``L/2L``, so
the stable orthogonal group ``ker rho_L`` is the level-two congruence subgroup.
Its 56 ordinary integral generators are proved complete by
``thm:coble-fifty-six-ordinary-full-kernel-generation`` in `dzackgarza/research`,
through the canonical even neighbour ``U^2 + D7(-1)``, the Eichler transvections
of its level-two kernel and the spin congruence subgroup property; the
matrices are retained as a source-hashed package certificate.

The certificate is a list of integral matrices, so it names isometries of the
lattice with this Gram matrix, in this order of the module generators.  What
this file asserts is that the family is returned for ``T_Co`` built from the
source's formula --- Dolgachev--Kondo, *Enriques surfaces and Borel--Weil--Bott
type duality*, Izv. Math. 77:3 (2013), section 3, equation (3.6), printed
p. 513 --- and not only for the catalogue entry, which is the same lattice with
a name on it; that every generator is an isometry of that lattice lying in its
kernel; and that the kernel's own selected resolution is the family, so
``group_generators()`` answers with it rather than with a Schreier family of the
finite image's 46 998 591 897 600 cosets.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coble_lattice():
    r"""``T_Co = <2> + (U + E8(-1))(2)``: Dolgachev--Kondo (3.6), p. 513, in the catalogue's block order."""
    return Lattices(ZZ)([[2]]) + (NamedLattices.U + NamedLattices.E8).twist(2)


def test_the_coble_lattice_built_from_the_source_returns_its_fifty_six_kernel_generators() -> None:
    r"""The family is returned for the lattice in that basis, whichever construction presents it."""
    lattice = _coble_lattice()
    family = lattice.stable_orthogonal_group_generators()
    assert sum(1 for _generator in family) == 56
    kernel = lattice.stable_orthogonal_group()
    assert all(generator in kernel for generator in family)
    assert sum(1 for _generator in kernel.group_generators()) == 56


def test_the_coble_lattice_generators_are_its_integral_isometries() -> None:
    r"""Each generator preserves the form of that lattice, so it is an integral isometry of it."""
    lattice = _coble_lattice()
    isometries = lattice.O()
    assert all(generator in isometries for generator in lattice.stable_orthogonal_group_generators())


def test_the_named_coble_lattice_returns_the_same_fifty_six_kernel_generators() -> None:
    r"""The catalogue entry, which is that lattice with a name on it, answers the same family."""
    lattice = NamedLattices.Tco
    assert sum(1 for _generator in lattice.stable_orthogonal_group_generators()) == 56
    assert sum(1 for _generator in lattice.stable_orthogonal_group().group_generators()) == 56


def test_the_coble_lattice_returns_ninety_five_certified_positive_kernel_generators() -> None:
    r"""The positive kernel's family is the order-two Schreier subfamily of the same certificate."""
    lattice = NamedLattices.Tco
    family = lattice.stable_positive_orthogonal_group_generators()
    assert sum(1 for _generator in family) == 95
    positive = lattice.stable_positive_orthogonal_group()
    assert all(generator in positive for generator in family)
    assert sum(1 for _generator in positive.group_generators()) == 95
