r"""Complete primitive null flags in nU have adapted hyperbolic bases.

Unimodularity gives integral duals to a primitive maximal null basis.
Evenness permits corrections making those duals null, so every such flag
has a hyperbolic completion and lies in the coordinate flag's O(nU) orbit.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("rank", (1, 2, 3), ids=("rank_one", "rank_two", "rank_three"))
def test_complete_null_flag_orbits_and_transporters_in_split_unimodular_lattices(rank):
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic
    for _ in range(1, rank):
        ambient = ambient + hyperbolic
    basis = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    group = ambient.O()
    flags = group.isotropic_orbit_representatives(rank, flag=True)
    assert flags.cardinality() == cardinal(1)
    flag = next(iter(flags))
    assert flag.flag_type() == FlagType.complete(rank)
    terms = tuple(flag.terms())
    assert tuple(int(term.module_rank()) for term in terms) == tuple(range(1, rank + 1))
    assert all(term.is_primitive() for term in terms)
    swapped = tuple(point for left, right in zip(basis[::2], basis[1::2], strict=True) for point in (right, left))
    swap = ambient.Aut()(dict(zip(labels, swapped, strict=True)))
    moved = IsotropicFlag(ambient, tuple(swap(point) for point in flag.basis()))
    witness = group.isotropic_equivalence_witness(flag, moved, flag=True)
    assert witness.domain() is ambient and witness.codomain() is ambient
    for source, target in zip(terms, moved.terms(), strict=True):
        assert all(target.inclusion().is_in_image(witness(source.inclusion()(point))) for point in source.module_generators())
        assert all(source.inclusion().is_in_image((~witness)(target.inclusion()(point))) for point in target.module_generators())
    assert all(ambient.b(witness(x), witness(y)) == ambient.b(x, y) for x in basis for y in basis)


def test_complete_rank_three_flag_stabilizer_preserves_every_term():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    basis = tuple(ambient.module_generators())
    flag = IsotropicFlag(ambient, basis[::2])
    group_generators = tuple(ambient.O().isotropic_stabilizer_generators(flag, flag=True))
    assert group_generators
    for generator in group_generators:
        for term in flag.terms():
            assert all(term.inclusion().is_in_image(generator(term.inclusion()(point))) for point in term.module_generators())
            assert all(term.inclusion().is_in_image((~generator)(term.inclusion()(point))) for point in term.module_generators())
        assert all(ambient.b(generator(x), generator(y)) == ambient.b(x, y) for x in basis for y in basis)



def test_two_hyperbolic_planes_have_no_rank_three_isotropic_flag():
    r"""Signature (2,2) bounds the dimension of a null subspace by two."""
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    assert ambient.O().isotropic_orbit_representatives(3, flag=True).cardinality() == cardinal(0)
