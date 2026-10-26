r"""Reflection and discriminant-form sign conventions retained from the archive.

For a root ``v``, the reflection is ``x - 2 b(x,v)/q(v) v``.  On the
negative-definite ``A2`` framing this sends the first simple root to its
negative and the second to their sum.  Twisting a lattice by ``-1`` negates
its discriminant quadratic form, so the two sign conventions are related by
anti-isometry rather than ordinary isometry.
"""

from sage_extensions.all import *


def test_a2_root_reflection_has_the_defining_action() -> None:
    lattice = Lattices.A2
    first, second = lattice.module_generators()
    reflection = lattice.reflection(first)

    assert reflection(first) == -first
    assert reflection(second) == first + second
    witness = 2 * first - 3 * second
    assert reflection(reflection(witness)) == witness


def test_twisting_a2_negates_its_discriminant_quadratic_form() -> None:
    negative = Lattices.A2.discriminant_group()
    positive = Lattices.A2.twist(-1).discriminant_group()

    assert negative.is_anti_isometric(positive)
    assert not negative.is_anti_isometric(negative)
    assert negative.twist(-1).is_isomorphic(positive)
