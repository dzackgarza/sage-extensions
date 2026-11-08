r"""Target-stabilizer correction for a nonnormal subgroup of O(A1 cubed).

Fixing e/2 in the discriminant and determinant one allows f -> h,
but forbids e -> h. The full stabilizer of h consists of signed
permutations of e and f. Both decisions concern the same target.
"""

from sage_extensions.all import *


def test_nonnormal_character_transporter_has_the_exact_positive_and_negative_decisions():
    root = Lattices(ZZ)("A1")
    lattice = root + root + root
    group = lattice.O()
    e, f, h = tuple(lattice.module_generators())
    cycle = group((f, h, e))
    exchange = group((e, h, f))
    rho = lattice.discriminant_representation()
    target = rho.codomain().subgroup((rho(exchange),))
    subgroup = lattice.SO().intersection(group.discriminant_preimage(target))
    known = group((-e, h, f))
    assert known in subgroup
    assert known(f) == h
    stabilizer = tuple(group(images) for images in ((f, e, h), (-e, f, h), (e, -f, h)))
    assert all(element(h) == h for element in stabilizer)
    assert rho(cycle) * rho(exchange) * ~rho(cycle) not in target
    quotient = subgroup.finite_character_quotient()
    witness = quotient.adjust_witness_into_subgroup(cycle, stabilizer)
    assert witness in subgroup
    assert witness(f) == h
    assert (~witness)(h) == f
    basis = (e, f, h)
    assert all((~witness)(witness(point)) == point for point in basis)
    assert all(lattice.b(witness(x), witness(y)) == lattice.b(x, y) for x in basis for y in basis)
    assert quotient.adjust_witness_into_subgroup(cycle * cycle, stabilizer) is None
