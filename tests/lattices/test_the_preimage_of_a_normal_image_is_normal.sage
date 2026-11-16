r"""The preimage of a normal subgroup of a finite image is normal in ``O(L)``.

A subgroup built from character data is ``Gamma = chi^-1(S)`` for the finite
character ``chi`` of the quotient that split its row, and ``chi`` maps ``O(L)``
onto that image.  A surjection carries normal subgroups to normal subgroups and
carries the preimages of normal subgroups back: so ``Gamma`` is invariant under
conjugation by ``O(L)`` exactly when ``S`` is normal in ``chi(O(L))``, and a
proper image can be normal.

The specimen is ``A_1^3``, whose discriminant form has orthogonal group the
permutation group ``S_3`` on the three classes of square ``-1/2``.  The cycle
``e_0 -> e_1 -> e_2`` generates the three-element subgroup ``C_3 = A_3``, which
is normal in ``S_3`` and proper: its preimage has index two, so it is no kernel
of a character, and the invariance is a statement about its image alone.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _a1_cubed():
    r"""``A_1^3``: three copies of the rank-one lattice of Gram matrix ``(2)``."""
    root = Lattices(ZZ)("A1")
    return root + root + root


def test_the_preimage_of_a_proper_normal_image_is_invariant() -> None:
    r"""``C_3`` is normal in ``S_3``, so its preimage is a normal subgroup of index two."""
    lattice = _a1_cubed()
    group = lattice.O()
    labels = tuple(lattice.module_generating_set())
    first, second, third = tuple(lattice.module_generators())
    cycle = group(dict(zip(labels, (second, third, first), strict=True)))
    rho = lattice.discriminant_representation()
    assert rho.codomain().cardinality() == cardinal(6)
    target = rho.codomain().subgroup((rho(cycle),))
    assert target.cardinality() == cardinal(3)
    assert all(
        rho(generator) * rho(cycle) * ~rho(generator) in target
        for generator in group.group_generators()
    )
    subgroup = group.discriminant_preimage(target)
    quotient = subgroup.finite_character_quotient()
    assert quotient.index() == 2
    assert quotient.subgroup_image_order() == 3
    assert quotient.preserves_conjugation() is True
