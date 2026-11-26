r"""The `ker rho` line-orbit row on `T_Co` is the index of the exact finite discriminant image.

`isotropic_orbit_representatives` on `Otilde(L) = ker(O(L) -> O(A_L))` splits the ambient
line orbit `G v` by `Gamma = Otilde(L)`.  Because `Gamma = ker rho`, the double cosets
`Gamma \ G / Stab_G(v)` correspond bijectively to the cosets `rho(G) / rho(Stab_G(v))` --
the orbit--stabilizer correspondence for the action of the quotient `G/ker rho`, which is
`rho(G)` acting through `rho` -- so the number of `Gamma`-orbits is the index
`[rho(G) : rho(Stab_G(v))]`, and one representative per coset is `g v` for an isometry `g`
whose discriminant image lies in that coset.

`T_Co = <2> + (U + E8(-1))(2)` (Dolgachev--Kondo, Izv. Math. 77:3 (2013), section 3, eq.
(3.6), printed p. 513), rank 11, signature (2, 9), has no unimodular
hyperbolic summand. Its unscaled odd unimodular lattice is I_(2,9).
The primitive isotropic vectors form a single ambient orbit by integral
hyperbolic splitting and indefinite unimodular classification
(Peters--Sterk, Theorem 2.3.1). Every primitive vector has divisor two
after scaling. The independent exact integral root-lift certificate in
research, lem:coble-full-finite-image-root-lifts and
lem:coble-explicit-vector-parabolic-image, gives ambient image order
46998591897600, stabilizer image order 89181388800, and 527 nonzero
singular classes. Its proof lifts norm +/-2 roots in the unscaled
lattice, checks integral vector fixing, and computes the finite group
orders on the singular classes. The corresponding finite images are
computed here through the public operations, not supplied to them.
The divided classes have exponent two, so distinct divided classes
distinguish the unoriented stable line orbits. Equality of the stabilizer
image with the class stabilizer proves completeness of the class list.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coble_lattice():
    r"""``T_Co = <2> + (U + E8(-1))(2)``: Dolgachev--Kondo (3.6), p. 513."""
    return Lattices(ZZ)([[2]]) + (NamedLattices.U + NamedLattices.E8).twist(2)


def _is_a_primitive_isotropic_line(lattice, subobject) -> bool:
    r"""Whether ``subobject`` is a rank-one primitive totally isotropic subobject."""
    if subobject.module_rank() != cardinal(1):
        return False
    if subobject.is_primitive() is not True:
        return False
    for label in subobject.module_generating_set():
        vector = subobject.inclusion()(subobject.module_generator(label))
        if lattice.q(vector) != lattice.base_ring().zero():
            return False
        if lattice.b(vector, vector) != lattice.base_ring().zero():
            return False
    return True


def test_the_stable_line_orbit_row_returns_with_the_index_of_the_discriminant_image() -> None:
    r"""The row returns, and its orbit count is ``[rho(O(T_Co)) : rho(Stab(line))]``."""
    lattice = _coble_lattice()
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[1])
    subobject = lattice.primitive_isotropic_subobject(vector)

    ambient_lifts = lattice.Aut().discriminant_image_reflection_lifts()
    fixing_lifts = lattice.Aut().discriminant_image_reflection_lifts(vector)
    assert all(g in lattice.O() for g in ambient_lifts)
    assert all(g(vector) == vector for g in fixing_lifts)
    image_of_group = lattice.Aut().discriminant_image()
    image_of_stabilizer = subobject.stabilizer_discriminant_image()
    order = image_of_group.cardinality().finite_value()
    stabilizer_order = image_of_stabilizer.cardinality().finite_value()
    assert order == 46998591897600
    assert stabilizer_order == 89181388800
    assert all(
        generator in image_of_group for generator in image_of_stabilizer.group_generators()
    )

    lines = lattice.stable_orthogonal_group().isotropic_orbit_representatives(1)

    assert lines.is_empty() is False
    assert all(
        _is_a_primitive_isotropic_line(lattice, representative) for representative in lines
    )
    assert lines.cardinality().finite_value() == order // stabilizer_order
    assert lines.cardinality().finite_value() == 527
    classes = set()
    for line in lines:
        label = tuple(line.module_generating_set())[0]
        vector = line.inclusion()(line.module_generator(label))
        assert lattice.div(vector) == 2
        divided = lattice.divided_discriminant_class(vector)
        assert divided != lattice.discriminant_group().zero()
        assert divided not in classes
        classes.add(divided)
