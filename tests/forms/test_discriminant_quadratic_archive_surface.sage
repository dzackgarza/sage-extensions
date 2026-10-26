r"""The discriminant quadratic form of ``D4``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_brown_invariant_of_the_D4_discriminant_form_is_its_signature_mod_8() -> None:
    r"""Milgram: ``Br(q_{D4}) = sign(D4) mod 8``; ``A_{D4} = (Z/2)^2`` is anisotropic.

    The three nonzero classes all have ``q = 1 mod 2Z``, so the Gauss sum is
    ``(1 - 3)/2 = -1 = exp(2 pi i * 4/8)``, and ``sign(D4) = +-4``.
    """
    lattice = Lattices(ZZ)("D4")
    form = lattice.discriminant_quadratic_form()
    positive, negative = lattice.signature_pair()

    assert form.cardinality() == 4
    assert form.brown_invariant() == (int(positive) - int(negative)) % 8
    assert form.brown_invariant() == 4
    assert form.is_anisotropic()
