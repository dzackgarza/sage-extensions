r"""The plane class index is read the same way by two independent computations.

`[Stab_{O(q)}(J) : rho(Stab_Gamma(P))]` has two owners in the library and this
test sets them against each other at one plane:

* the plane's own parabolic states `|Stab_{O(q)}(D(P))|` as the bound its
  generators' discriminant images are compared with
  (`stabilizer_discriminant_image_orders`), and states their quotient;
* the character quotient states the same stabilizer by meeting the condition
  subgroup with the certified parabolic's image (`plane_class_index`).

A third computation, independent of both, is the stabilizer of the class set
inside `O(q)` itself, asked of the finite group.  The test builds `J` from the
plane's own divided classes through the lattice's `divided_discriminant_class`,
so neither the class set nor the order comes from the object under test.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u2():
    r"""`U + U(2)`: one `O(L)`-orbit of primitive isotropic planes."""
    return Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]])


def _plane(lattice):
    r"""One primitive isotropic plane of the lattice, as a subobject."""
    return next(iter(lattice.Aut().cusps(2))).representative()


def _class_set(lattice, plane):
    r"""`J = [P/2]`: the span of the plane's three nonzero divided classes."""
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


def test_the_parabolic_and_the_quotient_state_the_same_class_stabilizer():
    r"""Both routes give `|Stab_{O(q)}(J)|`, and the finite group agrees.

    The parabolic's bound is the order of the stabilizer of the plane's divided
    classes; the quotient's is the image order times the index it returns; and
    `O(q)`'s own setwise stabilizer of the class set is the third reading.  All
    three are asked here of one plane, so a route that returned a different
    number would be visible.
    """
    lattice = _u_u2()
    plane = _plane(lattice)
    classes = _class_set(lattice, plane)
    subgroup = lattice.stable_orthogonal_group()
    quotient = subgroup.finite_character_quotient()

    _classes, quotient_stabilizer, image_order, index = quotient.plane_class_index(plane)
    parabolic_stabilizer, parabolic_image = plane.stabilizer_discriminant_image_orders()
    smooth_order = lattice.discriminant_group().O().stabilizer_of_classes(
        tuple(classes)
    ).cardinality()

    assert quotient_stabilizer == int(parabolic_stabilizer)
    assert int(smooth_order) == int(parabolic_stabilizer)
    assert quotient_stabilizer == image_order * index
    assert int(parabolic_image) * index == int(parabolic_stabilizer)
