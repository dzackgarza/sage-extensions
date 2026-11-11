r"""The `ker rho` line-orbit row on `T_Co` is the index of the exact finite discriminant image.

`isotropic_orbit_representatives` on `Otilde(L) = ker(O(L) -> O(A_L))` splits the ambient
line orbit `G v` by `Gamma = Otilde(L)`.  Because `Gamma = ker rho`, the double cosets
`Gamma \ G / Stab_G(v)` correspond bijectively to the cosets `rho(G) / rho(Stab_G(v))` --
the orbit--stabilizer correspondence for the action of the quotient `G/ker rho`, which is
`rho(G)` acting through `rho` -- so the number of `Gamma`-orbits is the index
`[rho(G) : rho(Stab_G(v))]`, and one representative per coset is `g v` for an isometry `g`
whose discriminant image lies in that coset.

`T_Co = <2> + (U + E8(-1))(2)` (Dolgachev--Kondo, Izv. Math. 77:3 (2013), section 3, eq.
(3.6), printed p. 513), rank 11, signature (2, 9), whose marked `U(2)` line `<e_1>` is the
line of #322.  It exhibits no *unimodular* hyperbolic plane, so
`isotropic_line_stabilizer_image` refuses it -- Eichler's criterion needs two of them in the
lattice itself (#315) -- and the row falls back to `splitting_isometries`, which stops:
`_splitting_isometries_in_im_rho_from_image` evaluates `rho` on the ambient group's
generating family and does not return (`.tmp/p310-probe9.log`, still inside that frame at
420 s).

Both finite images it needs are computable without that family:
`lattice.Aut().discriminant_image()` and `subobject.stabilizer_discriminant_image()`
(``thm:schreier-discriminant-image``, research#750).  The index they give is the orbit count
this file asks the row for.
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
    subobject = lattice.primitive_isotropic_subobject(lattice.module_generator(labels[1]))

    image_of_group = lattice.Aut().discriminant_image()
    image_of_stabilizer = subobject.stabilizer_discriminant_image()
    order = image_of_group.cardinality().finite_value()
    stabilizer_order = image_of_stabilizer.cardinality().finite_value()
    # The stabilizer's image lies in the group's image, so the quotient is the index.
    assert all(
        generator in image_of_group for generator in image_of_stabilizer.group_generators()
    )

    lines = lattice.stable_orthogonal_group().isotropic_orbit_representatives(1)

    assert lines.is_empty() is False
    assert all(
        _is_a_primitive_isotropic_line(lattice, representative) for representative in lines
    )
    assert lines.cardinality().finite_value() == order // stabilizer_order
