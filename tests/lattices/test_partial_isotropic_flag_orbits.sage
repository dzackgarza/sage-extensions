r"""Primitive partial null flags in 3U admit adapted hyperbolic bases.

The integral Levi GL(3,ZZ) moves each primitive subflag of a maximal
null sublattice to a coordinate subflag. The maximal null stabilizer
has determinant one, so SO(3U) has two such flag orbits.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("dimensions", ((1, 3), (2, 3)))
def test_partial_null_flag_type_is_preserved_by_transport(dimensions):
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    basis = tuple(ambient.module_generators())
    flag_type = FlagType(dimensions)
    flag = ambient.isotropic_flag(*basis[::2], flag_type=flag_type)
    assert flag.flag_type() == flag_type
    assert flag in ambient.isotropic_flag_locus(dimensions)
    labels = tuple(ambient.module_generating_set())
    swapped = (basis[1], basis[0], *basis[2:])
    swap = ambient.Aut()(dict(zip(labels, swapped, strict=True)))
    moved = swap.transport_isotropic_object(flag)
    assert moved.flag_type() == flag_type
    for source, target in zip(flag.terms(), moved.terms(), strict=True):
        assert all(target.inclusion().is_in_image(swap(source.inclusion()(point))) for point in source.module_generators())
        assert all(source.inclusion().is_in_image((~swap)(target.inclusion()(point))) for point in target.module_generators())


@pytest.mark.parametrize("dimensions", ((1, 3), (2, 3)))
def test_special_orthogonal_partial_null_flag_orbits(dimensions):
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    flag_type = FlagType(dimensions)
    full = ambient.O().isotropic_orbit_representatives(flag_type, flag=True)
    assert full.cardinality() == cardinal(1)
    special = ambient.SO().isotropic_orbit_representatives(flag_type, flag=True)
    assert special.cardinality() == cardinal(2)
    first, second = tuple(special)
    assert first.flag_type() == second.flag_type() == flag_type
    assert ambient.SO().isotropic_equivalence_witness(first, second, flag=True) is None
    witness = ambient.O().isotropic_equivalence_witness(first, second, flag=True)
    assert witness in ambient.O()
    for source, target in zip(first.terms(), second.terms(), strict=True):
        assert all(target.inclusion().is_in_image(witness(source.inclusion()(point))) for point in source.module_generators())
        assert all(source.inclusion().is_in_image((~witness)(target.inclusion()(point))) for point in target.module_generators())


def test_one_term_rank_two_null_flags_in_two_u():
    r"""A primitive maximal null plane in 2U extends to a hyperbolic basis."""
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    flag_type = FlagType.plane(2)
    flags = ambient.isotropic_flag_orbit_representatives(flag_type)
    assert flags.cardinality() == cardinal(1)
    flag = next(iter(flags))
    assert flag.flag_type() == flag_type
    assert flag in ambient.isotropic_flag_locus((2,))
    assert tuple(int(term.module_rank()) for term in flag.terms()) == (2,)
