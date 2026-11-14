r"""The `ker rho` line-orbit row is a quotient of the exact finite discriminant image (#310).

`isotropic_orbit_representatives` on the stable orthogonal group `Otilde(L) = ker(O(L) -> O(A_L))`
splits the ambient line orbit `G v` by `Gamma = Otilde(L)`.  Because `Gamma = ker rho`, the
double cosets `Gamma \ G / Stab_G(v)` correspond bijectively to the cosets
`rho(G) / rho(Stab_G(v))`: the orbit--stabilizer correspondence for the action of `G/ker rho`,
which acts on `G v` through `rho`.  So the number of `Gamma`-orbits is the index
`[rho(G) : rho(Stab_G(v))]`, and one representative per coset is `g v` for an isometry `g`
whose discriminant image lies in that coset.

Both images are computable without the ambient group's selected generating family:
`stabilizer_discriminant_image()` is the action-groupoid construction of
``thm:schreier-discriminant-image`` (research#750) and `discriminant_image()` is the
character quotient's own computed image of `rho(O(L))`.

The specimen is `U(2) + <-6>`, of rank three.  It exhibits no *unimodular* hyperbolic plane,
so `isotropic_line_stabilizer_image` refuses it (Eichler's criterion needs two, #315), and the
row falls back to `splitting_isometries`, which stops inside
`_splitting_isometries_in_im_rho -> _im_rho_engine_and_section` demanding the ambient
generator family (`.tmp/p310-probe7.log`).  Its discriminant group has order 24, so a trivial
image cannot pass for a nontrivial one.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""``U(2) + <-6>``, with its first basis vector, which is primitive isotropic."""
    lattice = Lattices(ZZ)([[0, 2, 0], [2, 0, 0], [0, 0, -6]])
    labels = tuple(lattice.module_generating_set())
    return lattice, lattice.module_generator(labels[0])


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
    r"""The row returns, and its orbit count is ``[rho(O(L)) : rho(Stab(line))]``."""
    lattice, vector = _specimen()
    subobject = lattice.primitive_isotropic_subobject(vector)

    # The two exact finite images, neither of which needs the ambient generating family.
    image_of_group = lattice.Aut().discriminant_image()
    image_of_stabilizer = subobject.stabilizer_discriminant_image()
    order = image_of_group.cardinality().finite_value()
    stabilizer_order = image_of_stabilizer.cardinality().finite_value()
    # The stabilizer's image lies in the group's image; the index is the orbit count.
    assert all(
        generator in image_of_group for generator in image_of_stabilizer.group_generators()
    )

    lines = lattice.stable_orthogonal_group().isotropic_orbit_representatives(1)

    assert lines.is_empty() is False
    assert all(
        _is_a_primitive_isotropic_line(lattice, representative) for representative in lines
    )
    assert lines.cardinality().finite_value() == order // stabilizer_order
