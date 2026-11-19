r"""The `Gamma_{Co,2}` plane row is not one orbit per liftable class `J`.

`Gamma_{Co,2} = rho^{-1}(Stab_{O(q)}(J_0))` is the one row whose finite image is
not trivial, and its plane row therefore behaves differently from the two kernel
rows': a kernel row's cusps are the liftable classes `J` times the ambient index
(`tests/lattices/test_the_plane_class_index_counts_the_fibre.sage`), whereas
`Gamma_{Co,2}` has far fewer cusps than classes.

This file measures that on the smallest specimen where the two numbers differ:
`U + U(2) + <-4>` has `|O(q)| = 12` with `|Stab(J_0)| = 4`, so three liftable
classes `J`, and the row returns two planes.  Each returned plane has its own
class `J`, built from its divided classes, and the two are distinct -- the row is
a set of orbits over *some* of the classes, not one over each.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""`U + U(2) + <-4>`: three liftable plane classes and two planes in the row."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[-4]])
    )


def _class_of(lattice, plane):
    r"""`J = [P/2]` for one plane, as the span of its three nonzero divided classes."""
    form = lattice.discriminant_group()
    inclusion = plane.inclusion()
    domain = inclusion.domain()
    basis = tuple(
        inclusion(domain.module_generator(label))
        for label in domain.module_generating_set()
    )
    closure = {form.zero()}
    for vector in (basis[0], basis[1], basis[0] + basis[1]):
        generator = lattice.divided_discriminant_class(vector)
        closure |= {element + generator for element in closure}
    return frozenset(closure)


def _base_class(lattice):
    r"""`J_0`, the class of the `U(2)` block: the point `Gamma_{Co,2}` is cut out by."""
    form = lattice.discriminant_group()
    labels = tuple(lattice.module_generating_set())
    pair = next(
        (left, right)
        for left in labels
        for right in labels
        if left < right
        and lattice.q(lattice.module_generator(left)) == ZZ.zero()
        and lattice.q(lattice.module_generator(right)) == ZZ.zero()
        and lattice.b(lattice.module_generator(left), lattice.module_generator(right)) == ZZ(2)
    )
    closure = {form.zero()}
    for label in pair:
        generator = lattice.discriminant_class(
            lattice.primitive_dual(lattice.module_generator(label))
        )
        closure |= {element + generator for element in closure}
    return frozenset(closure)


def test_the_coble_2_row_has_fewer_planes_than_liftable_classes():
    r"""Three classes `J`, two planes: the row is not the class count.

    The class count is `|O(q)| / |Stab(J_0)|`, computed from the finite group;
    the row is the public orbit call; and each plane's own class is built from
    its divided classes.  The two classes the row occupies are the ones that are
    not the base class, which is why the row is smaller than the class count
    while the kernel rows are class count times eight.
    """
    lattice = _specimen()
    base = _base_class(lattice)
    subgroup = lattice.Aut().discriminant_point_stabilizer(base)
    form = lattice.discriminant_group()
    engine = form.O()

    classes = int(engine.cardinality()) // int(
        engine.stabilizer_of_classes(tuple(base)).cardinality()
    )
    planes = tuple(subgroup.isotropic_orbit_representatives(2))
    occupied = tuple(_class_of(lattice, plane) for plane in planes)
    row = subgroup.cusps(2)

    assert classes == int(3)
    assert row.cardinality() == cardinal(2)
    assert occupied[0] != occupied[1]
    assert occupied[0] != base
    assert occupied[1] != base
