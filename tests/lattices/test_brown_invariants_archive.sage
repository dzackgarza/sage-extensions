r"""Finite quadratic-form facts retained from the archived mathematics suite.

Miranda--Morrison, *Embeddings of Integral Quadratic Forms*, gives
``Br(u_k)=0`` and ``Br(v_1)=4``; Nikulin's Milgram theorem identifies the
Brown invariant of an even lattice discriminant form with its signature
modulo eight.  These assertions exercise the live owned discriminant forms.
"""

from sage_extensions.all import *


def test_elementary_u_k_forms_have_brown_invariant_zero_and_are_isotropic() -> None:
    for exponent in (1, 2, 3):
        scale = 2**exponent
        lattice = Lattices(ZZ)([[0, scale], [scale, 0]])
        form = lattice.discriminant_group()
        invariants = form.invariants()

        assert invariants.cardinality() == 2
        assert invariants[0] == invariants[1] == scale
        assert form.brown_invariant() == 0
        assert not form.is_anisotropic()


def test_v1_is_the_anisotropic_d4_form_of_brown_invariant_four() -> None:
    form = Lattices.D4.discriminant_group()
    invariants = form.invariants()

    assert invariants.cardinality() == 2
    assert invariants[0] == invariants[1] == 2
    assert form.brown_invariant() == 4
    assert form.is_anisotropic()


def test_milgram_matches_brown_invariant_with_signature_modulo_eight() -> None:
    specimens = (
        Lattices.A5,
        Lattices.D4,
        Lattices(ZZ)([[0, 2], [2, 0]]),
        Lattices(ZZ)([[-2]]),
    )

    for lattice in specimens:
        positive, negative = lattice.signature_pair()
        assert lattice.discriminant_group().brown_invariant() == (
            int(positive) - int(negative)
        ) % 8
