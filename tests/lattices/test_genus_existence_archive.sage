r"""Nikulin genus existence for the discriminant form of ``A2``.

``A2`` is negative definite, so its discriminant form has Brown invariant
``-2 = 6 (mod 8)``.  By Milgram's formula a lattice of signature ``(p, n)``
with this form requires ``p - n = 6 (mod 8)``, and since every rank here
exceeds the length ``1`` of the form this is sufficient (Nikulin 1979,
Thm. 1.10.1).  Adjoining ``U`` leaves the discriminant form unchanged.
"""

from sage_extensions.all import *


def test_a2_discriminant_genus_exists_exactly_when_the_signature_satisfies_milgram() -> None:
    discriminant = Lattices(ZZ)("A2").discriminant_group()
    expected = {
        (0, 2): True,
        (2, 0): False,
        (1, 3): True,
        (3, 1): False,
        (2, 4): True,
        (0, 6): False,
    }

    assert discriminant.brown_invariant() == 6
    for signature, exists in expected.items():
        assert discriminant.is_discriminant_form_of_even_lattice(signature_pair(*signature)) is exists


def test_adjoining_hyperbolic_planes_to_a2_realizes_the_indefinite_genera() -> None:
    discriminant = Lattices(ZZ)("A2").discriminant_group()
    a2 = Lattices(ZZ)("A2")
    u = Lattices(ZZ)("U")

    assert Lattices(ZZ).genus(signature_pair(1, 3), discriminant) == (a2 + u).genus()
    assert Lattices(ZZ).genus(signature_pair(2, 4), discriminant) == (a2 + u + u).genus()
