r"""The finite character image decides a witness with no stabilizer to adjust by.

``Otilde+(T_Co) = ker(rho, sn_RR)`` is cut out of ``O(T_Co)`` by the joint
character ``chi = (rho, sn_RR)``, whose discriminant factor is the orthogonal
group of ``A_{T_Co}`` of order 46998591897600.  The Coble incidence rows ask
``adjust_witness_into_subgroup`` at every witness: given a witness carrying one
subobject onto another and the target's stabilizer family, is some element of
that family times the witness in the subgroup?

With no stabilizer to adjust by, that question is membership of the witness in
the subgroup itself, and the finite image answers it: the adjustment exists
when the witness's character image is the subgroup's own.  ``Otilde`` is the
kernel of the discriminant representation and ``Otilde+`` the kernel of that
representation together with the real spinor norm, so ``Otilde+`` has index two
in ``Otilde`` and ``Otilde``'s generating family holds witnesses on both
sides -- which is what makes the decision non-vacuous here.
"""

from sage_extensions.all import *


def test_the_character_image_decides_an_unadjusted_witness_at_the_coble_kernel():
    lattice = NamedLattices.Tco
    subgroup = lattice.stable_positive_orthogonal_group()
    kernel = lattice.stable_orthogonal_group()
    quotient = subgroup.finite_character_quotient()
    inside_image = quotient.image(subgroup.one())
    decisions = tuple(
        (
            quotient.image(generator) == inside_image,
            quotient.witness_meets_subgroup(generator, ()),
        )
        for generator in kernel.group_generators()
    )
    assert any(inside for inside, _adjusted in decisions)
    assert not all(inside for inside, _adjusted in decisions)
    assert all(inside == adjusted for inside, adjusted in decisions)
