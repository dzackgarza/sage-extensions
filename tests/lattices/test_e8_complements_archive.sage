r"""Nikulin discriminant anti-isometries for primitive complements in ``E8``.

The live lattice-surface regressions already retain the primitive ``A1`` and
``A2`` complements and their ``E7``/``E6`` discriminants.  This archive unit
adds the remaining mathematical comparison: in an even unimodular lattice,
the discriminant forms of a primitive complement pair are anti-isometric.
"""

from sage_extensions.all import *


def _adjacent_pair(lattice):
    return next(
        (left, right)
        for left in lattice.module_generators()
        for right in lattice.module_generators()
        if left != right and left.b(right) != 0
    )


def test_e8_a1_complement_discriminants_are_anti_isometric() -> None:
    e8 = Lattices.E8
    a1 = e8.subobject_on((e8.module_generator(0),))
    e7 = a1.orthogonal_complement()

    assert e7.discriminant_group().is_anti_isometric(a1.discriminant_group())


def test_e8_a2_complement_discriminants_are_anti_isometric() -> None:
    e8 = Lattices.E8
    a2 = e8.subobject_on(_adjacent_pair(e8))
    e6 = a2.orthogonal_complement()

    assert e6.discriminant_group().is_anti_isometric(a2.discriminant_group())
