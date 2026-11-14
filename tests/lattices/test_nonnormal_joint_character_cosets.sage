r"""A nonnormal discriminant preimage with determinant one in O(A1 cubed).

The integral orthogonal group is the signed permutation group. The
classes e_i/2 are exactly the three discriminant elements of square -1/2,
so the discriminant orthogonal group is S3. Independent sign changes
supply both determinants above every permutation. Thus the joint image
is C2 times S3. Requiring determinant one and fixing e_0/2 gives a
nonnormal subgroup of index six, with coset coordinates (det(g), rho(g)c_0).
"""

from sage_extensions.all import *


def test_nonnormal_joint_character_cosets_have_the_exact_left_action_and_lifts():
    root = Lattices(ZZ)("A1")
    lattice = root + root + root
    group = lattice.O()
    labels = tuple(lattice.module_generating_set())
    e, f, h = tuple(lattice.module_generators())
    cycle, exchange, sign = tuple(
        group(dict(zip(labels, images, strict=True)))
        for images in ((f, h, e), (e, h, f), (-e, f, h))
    )
    rho = lattice.discriminant_representation()
    target = rho.codomain().subgroup((rho(exchange),))
    assert rho.codomain().cardinality() == cardinal(6)
    assert target.cardinality() == cardinal(2)
    assert rho(cycle) * rho(exchange) * ~rho(cycle) not in target
    subgroup = lattice.SO().intersection(group.discriminant_preimage(target))
    quotient = subgroup.finite_character_quotient()
    character = quotient.character_representation()
    assert character.codomain().cardinality() == cardinal(12)
    for left in (cycle, exchange, sign):
        for right in (cycle, exchange, sign):
            assert character(left * right) == character(left) * character(right)
    classes = tuple(lattice.divided_discriminant_class(point) for point in (e, f, h))
    cosets = group.left_cosets(subgroup)
    assert cosets.cardinality() == cardinal(6)
    base = cosets.base_point()
    lifts = {point: cosets.transporter_witness(base, point) for point in cosets}
    coordinates = {
        point: (lift.determinant(), rho(lift)(classes[0]))
        for point, lift in lifts.items()
    }
    assert Set(tuple(coordinates.values())) == Set(tuple(
        (determinant, point) for determinant in (-ZZ.one(), ZZ.one()) for point in classes
    ))
    for point, lift in lifts.items():
        assert cosets.act(lift, base) == point
        for generator in (cycle, exchange, sign):
            assert coordinates[cosets.act(generator, point)] == (
                generator.determinant() * coordinates[point][0],
                rho(generator)(coordinates[point][1]),
            )
            assert cosets.act(~generator, cosets.act(generator, point)) == point
    for generator in (cycle, exchange, sign):
        assert (cosets.act(generator, base) == base) == (generator in subgroup)


def test_nonnormal_joint_subgroup_generators_retain_the_discriminant_kernel():
    r"""The signed action on the other two axes identifies the subgroup with D8.

    Fixing the first axis modulo the discriminant leaves signed permutations
    on the other axes. Determinant one then fixes the sign on the first
    axis. This is a faithful action of order eight; its discriminant image
    has order two and its full integral kernel has order four.
    """
    root = Lattices(ZZ)("A1")
    lattice = root + root + root
    group = lattice.O()
    labels = tuple(lattice.module_generating_set())
    e, f, h = tuple(lattice.module_generators())
    exchange = group(dict(zip(labels, (e, h, f), strict=True)))
    rho = lattice.discriminant_representation()
    target = rho.codomain().subgroup((rho(exchange),))
    subgroup = lattice.SO().intersection(group.discriminant_preimage(target))
    inclusion = subgroup.inclusion()
    family = tuple(subgroup.group_generators())
    assert all(inclusion(generator).determinant() == ZZ.one() for generator in family)
    assert all(rho(inclusion(generator)) in target for generator in family)
    roots = Sets()((f, -f, h, -h))
    action = FiniteGSets(subgroup)(roots, lambda generator, point: inclusion(generator)(point))
    assert action.permutation_representation().image().cardinality() == cardinal(8)
    assert (rho * inclusion).image().cardinality() == cardinal(2)
