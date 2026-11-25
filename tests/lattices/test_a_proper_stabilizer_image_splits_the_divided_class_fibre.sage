r"""An actual line stabilizer can have a proper image in the divided-class stabilizer.

Put B=U+<-12>, L=B(2), with basis e,f,k. The matrix with columns
(2,3,1), (3,2,1), (12,12,5) is an integral isometry of B.
The integral maps t(e)=e, t(f)=6e+f+k, t(k)=12e+k, and s(e)=f,
s(f)=e, s(k)=k preserve B. The composite a=s*t*g sends e to
3e+32f+4k, so a(e)/2 and e/2 agree modulo L. Yet on the invariant
subgroup B^dual/B in L^dual/L it acts by 5 modulo 12. An integral
isometry stabilizing Ze sends k to b e +/- k with 12 dividing b:
it preserves e-perp, the quotient norm -12, and the dual lattice.
Thus it acts only by +/-1 on B^dual/B. No element of ker rho_L
can carry the first line to the second, for composing with a^(-1)
would give a line stabilizer acting by 5 or its inverse there.
The same argument applies in B, where the divided datum is zero.
The finite-image fallback must decide these two distinct orbits
without requiring the actual image to exhaust the datum stabilizer.

The exact number of orbits in O(L).Ze is eight. Write A_L as
Z/2 e' + Z/2 f' + Z/24 k', with 24q(x,y,z)=24xy-z^2 modulo 48.
A nonzero singular element of order two is one of e', f',
e'+12k', f'+12k', 12k'. The last pairs trivially with all the
order-two elements and cannot be an image of e' because b(e',f')=1/2.
There are eight possible ordered images of (e',f') with pairing 1/2.
For each, orthogonality forces the first two coordinates of the image
of k' (its third coordinate is odd), and its norm requires either
z^2=1 or z^2=25 modulo 48, each giving four residues modulo 24.
Thus |O(A_L)| <= 32. A stabilizer of Ze has h(e)=eps e,
h(k)=12 eps delta c e+delta k, h(f)=6 eps c^2 e+eps f+c k
for eps,delta in {+1,-1} and integral c, by the Gram equations.
Its image depends only on c modulo 2 and delta, with all four
possibilities realized by t and negation of k. The lifts s,g,t give
four distinct images of e'; the lift a fixes e' but lies outside
the image of the line stabilizer. Its datum stabilizer has at least
two cosets of that order-four group, so the ambient image has at
least 4*8=32 elements. Hence the orders are exactly 32 and 4, and
each of the four divided classes carries two stable line orbits.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_divisor_two_fibre_has_distinct_stable_line_orbits():
    lattice = Lattices(ZZ)([[0,2,0],[2,0,0],[0,0,-24]])
    labels = tuple(lattice.module_generating_set())
    e, f, k = tuple(lattice.module_generators())
    group = lattice.Aut()
    g = group(dict(zip(labels, (2*e+3*f+k, 3*e+2*f+k, 12*e+12*f+5*k))))
    t = group(dict(zip(labels, (e, 6*e+f+k, 12*e+k))))
    s = group(dict(zip(labels, (f, e, k))))
    a = s*t*g
    moved = a(e)
    assert moved == 3*e+32*f+4*k
    assert lattice.div(e) == lattice.div(moved) == 2
    assert lattice.divided_discriminant_class(e) == lattice.divided_discriminant_class(moved)
    line = lattice.primitive_isotropic_subobject(e)
    other = lattice.primitive_isotropic_subobject(moved)
    stable = lattice.stable_orthogonal_group()
    quotient = stable.finite_character_quotient()
    assert general_image_certificate(quotient, line) is None
    assert quotient.separates_witness_orbits(a, line) is True
    family = quotient.exact_isotropic_stabilizer_generators(line)
    assert all(line.stabilizes(h) for h in family)
    image = line.stabilizer_discriminant_image()
    rho = lattice.discriminant_representation()
    generated = lattice.discriminant_group().O().subgroup(tuple(rho(h) for h in family))
    assert all(h in generated for h in image.group_generators())
    assert all(h in image for h in generated.group_generators())
    assert image.cardinality() == cardinal(4)
    assert group.discriminant_image().cardinality() == cardinal(32)
    lifts = quotient.splitting_isometries_from_stabilizer_image(
        tuple(quotient.image_space()(lambda _label, g=g: g)
              for g in image.group_generators())
    )
    assert lifts.cardinality() == cardinal(8)
    classes = []
    prior = []
    for lift in lifts:
        point = lift(e)
        assert point.is_primitive() is True and point.q() == 0
        assert lattice.div(point) == 2
        classes.append(lattice.divided_discriminant_class(point))
        for earlier in prior:
            assert rho(~earlier * lift) not in image
        prior.append(lift)
    expected = tuple(lattice.divided_discriminant_class(x)
                     for x in (e, f, g(e), (s*g)(e)))
    assert all(x != y for i, x in enumerate(expected) for y in expected[i+1:])
    assert all(sum(1 for x in classes if x == target) == 2 for target in expected)
    assert all(any(x == target for target in expected) for x in classes)
    assert stable.isotropic_equivalence_witness(line, other) is None


def test_the_determinant_fibre_of_the_hyperbolic_plane_splits():
    lattice = Lattices(ZZ)("U")
    e, f = tuple(lattice.module_generators())
    line = lattice.primitive_isotropic_subobject(e)
    quotient = lattice.SO().finite_character_quotient()
    family = quotient.exact_isotropic_stabilizer_generators(line)
    assert all(line.stabilizes(h) and h.determinant() == 1 for h in family)
    assert quotient.splitting_isometries(family).cardinality() == cardinal(2)
    assert lattice.SO().isotropic_equivalence_witness(
        line, lattice.primitive_isotropic_subobject(f)
    ) is None
