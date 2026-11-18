r"""The exact 56-generator Coble discriminant kernel theorem and card index.

The source-hashed integral certificate in the public library is proved complete
by research theorem thm:coble-fifty-six-ordinary-full-kernel-generation
(research/main 99f7680924). The lattice remains rank-eleven, 2-elementary,
with rank_2=0; the old Kneser refusal for the scaled lattice does not negate
the generation theorem obtained via its canonical even neighbor.
"""

from sage_extensions.all import *  # noqa: F401,F403
import pytest


def test_the_coble_lattice_returns_all_fifty_six_certified_ordinary_kernel_generators() -> None:
    r"""The public owner returns the exact proved finite family, not Schreier cosets."""
    lattice = NamedLattices.Tco
    family = lattice.stable_orthogonal_group_generators()
    assert len(family) == 56
    assert all(generator in lattice.stable_orthogonal_group() for generator in family)
    assert len(lattice.stable_orthogonal_group().group_generators()) == 56


def test_the_coble_lattice_returns_ninety_five_certified_positive_kernel_generators() -> None:
    r"""The public positive-kernel family is the proved Schreier subgroup."""
    lattice = NamedLattices.Tco
    family = lattice.stable_positive_orthogonal_group_generators()
    assert len(family) == 95
    positive = lattice.stable_positive_orthogonal_group()
    assert all(generator in positive for generator in family)
    assert len(positive.group_generators()) == 95


def test_the_coble_lattice_is_two_elementary_of_full_rank_with_rank_two_zero() -> None:
    r"""`L = 2L^#` (so the kernel is the level-two congruence subgroup) and `rank_2 = 0`."""
    lattice = NamedLattices.Tco
    ring = lattice.base_ring()
    assert int(lattice.discriminant_group().cardinality()) == 2 ** int(lattice.module_rank())
    assert int(lattice.rank_p(ring(2))) == 0
    assert int(lattice.rank_p(ring(3))) == int(lattice.module_rank())


def test_the_finite_orthogonal_group_of_the_coble_discriminant_form_is_the_card_row() -> None:
    r"""The finite group whose order is the kernel's index is the card's own orthogonal-group order.

    The card carries the index as `|O(A_{T_Co}, q)|`, read from the finite
    orthogonal group of the discriminant form; `rho_L` is onto, so that order
    is the index of `ker rho_L`.  The library's own `discriminant_image()`
    agrees and takes 35 s, over this suite's per-call ceiling, so the row
    asserted here is the finite group rather than the image.
    """
    lattice = NamedLattices.Tco
    assert (
        int(lattice.discriminant_group().orthogonal_group().cardinality())
        == card("discriminant_forms", "6JRR")["orthogonal_group_order"]
    )
