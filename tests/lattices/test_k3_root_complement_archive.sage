r"""Primitive ``(-2)`` roots in the K3 lattice and their complements.

The archived known-mathematics suite records the Nikulin complement statement
for a primitive root ``r`` in the K3 lattice: ``<r>`` has Gram ``[-2]`` and
its orthogonal complement has signature ``(3,18)``, discriminant group
``ZZ/2``, and discriminant form anti-isometric to that of ``<r>``.  This is a
different primitive-complement specimen from the positive-square polarization
cases: the signature changes on the opposite side.
"""

from sage_extensions.all import *


def test_primitive_k3_root_has_the_nikulin_complement_discriminant_form() -> None:
    k3 = Lattices.LK3
    e, f = k3.module_generator("e1"), k3.module_generator("f1")
    root = k3.subobject_on((e - f,))
    complement = root.orthogonal_complement()
    root_signature = root.signature_pair()
    complement_signature = complement.signature_pair()

    assert root.is_primitive()
    assert root.gram_matrix().determinant() == -2
    assert root_signature.first() == 0
    assert root_signature.second() == 1

    assert complement.module_rank() == 21
    assert complement_signature.first() == 3
    assert complement_signature.second() == 18
    assert complement.is_even()
    assert abs(complement.gram_matrix().determinant()) == 2
    invariants = complement.discriminant_group().invariants()
    assert invariants.cardinality() == 1
    assert invariants[0] == 2
    assert complement.discriminant_group().is_anti_isometric(
        root.discriminant_group()
    )
