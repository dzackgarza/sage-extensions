r"""Integral preimages in Z/2 plus Z retain the free-coordinate divisibility."""

from sage_extensions.all import *


def test_preimages_in_z_mod_two_plus_z_have_even_free_coordinate():
    r"""The image of (a,b) -> (a mod 2,2b) consists of the even free fibres."""
    source = ZZ**2
    e, f = tuple(source.module_generators())
    quotient = source.subobject_on((2 * e,)).inclusion().cokernel()
    projection = quotient.cokernel_projection()
    morphism = source.Mor(quotient)({0: projection(e), 1: projection(2 * f)})

    for target in (projection(e), projection(f), projection(e + 4 * f), projection(2 * f), projection(e - f)):
        if target in (projection(f), projection(e - f)):
            assert morphism.is_in_image(target) is False
        else:
            assert morphism.is_in_image(target) is True
            assert morphism(morphism.preimage(target)) == target


def test_named_framing_of_z_mod_two_plus_z_has_its_exact_shear_involution():
    r"""The map (a mod 2,b) -> (a+b mod 2,b) has square the identity."""
    free = ZZ.free_module(("torsion", "free"))
    e = free.module_generator("torsion")
    f = free.module_generator("free")
    quotient = free.subobject_on((2 * e,)).inclusion().cokernel()
    projection = quotient.cokernel_projection()
    shear = quotient.Mor(quotient)({"torsion": projection(e), "free": projection(e + f)})
    for a, b in ((0, 0), (1, 0), (0, 1), (3, -5), (2**80 + 1, 2**90)):
        point = projection(a * e + b * f)
        assert shear(point) == projection((a + b) * e + b * f)
        assert shear(shear(point)) == point
        assert shear(point + projection(2 * e)) == shear(point)


def test_residue_submodules_at_modulus_six_have_their_exact_transporters():
    r"""Swapping e,f interchanges <2e,3f> and <3e,2f> in (Z/6)^2."""
    plane = Lattices(QQ)([[0, 1], [1, 0]])
    labels = tuple(plane.module_generating_set())
    e, f = tuple(plane.module_generators())
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(plane)
    reference = space.subobject_on((space(e), space(f)))
    source = space.subobject_on((space(2 * e), space(3 * f)))
    swap = plane.Aut()({labels[0]: f, labels[1]: e})
    action = IntegralStructureAction(plane.Aut().subgroup((swap,)), source.inclusion()).with_stable_containing_bound(reference.inclusion())
    finite = action.finite_representation()
    residue = action.finite_quotient_action()
    quotient = residue.quotient_module()
    projection = residue.quotient_projection()
    first = residue.reference_inclusion().lift(space(e))
    second = residue.reference_inclusion().lift(space(f))
    assert residue.modulus() == 6
    assert finite.g_set().cardinality() == 2
    assert all(submodule.cardinality() == 6 for submodule in finite.orbit_submodules())
    for module_generators in ((2 * first, 3 * second), (2 * first + 3 * second, 4 * first + 9 * second), (2 * first, 3 * second + 6 * (2**80 + 1) * first)):
        target = quotient.subobject_on(tuple(projection(point) for point in module_generators))
        witness = finite.transporter_to(target)
        assert witness is not None and witness(e) == e and witness(f) == f
    target = quotient.subobject_on((projection(3 * first), projection(2 * second)))
    witness = finite.transporter_to(target)
    assert witness is not None and witness(e) == f and witness(f) == e
    outside = quotient.subobject_on((projection(3 * first), projection(3 * second)))
    assert finite.transporter_to(outside) is None

