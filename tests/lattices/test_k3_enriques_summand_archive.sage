r"""The Enriques lattice as a unimodular summand of the K3 lattice.

The archive records the standard decomposition
``L_K3 ~= E10 + (U + U + E8(-1))``.  Both summands are even unimodular, so
there is no finite glue ambiguity: their orthogonal sum already has the K3
lattice's signature and isometry class.
"""

from sage_extensions.all import *


def test_enriques_lattice_and_its_unimodular_complement_sum_to_k3_lattice() -> None:
    enriques = Lattices.E10
    complement = Lattices.U + Lattices.U + Lattices.E8
    enriques_signature = enriques.signature_pair()
    complement_signature = complement.signature_pair()

    assert enriques_signature.first() == 1
    assert enriques_signature.second() == 9
    assert complement_signature.first() == 2
    assert complement_signature.second() == 10
    assert enriques.is_even() and enriques.is_unimodular()
    assert complement.is_even() and complement.is_unimodular()
    assert enriques.discriminant_group().invariants().cardinality() == 0
    assert complement.discriminant_group().invariants().cardinality() == 0
    assert (enriques + complement).is_isometric(Lattices.LK3) is True
