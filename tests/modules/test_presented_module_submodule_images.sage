r"""The quarter-turn orbit of 4Ze + 9Zf retains its index and kernel.

The two lattice positions are (4,9) and (9,4) on the coordinate axes.
Their orbit span is Z^2 and its residue modulus is 36. The central
minus identity fixes both positions and generates the full stabilizer.
"""

from sage_extensions.all import *


def test_nonuniform_residue_submodules_retain_the_full_quarter_turn_stabilizer():
    plane = Lattices(QQ)(2)
    e, f = tuple(plane.module_generators())
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(plane)
    source = space.subobject_on((space(4 * e), space(9 * f)))
    target = space.subobject_on((space(9 * e), space(4 * f)))
    bound = space.subobject_on((space(e), space(f)))
    rotation = plane.O()((-f, e))
    group = plane.O().subgroup((rotation,))
    action = IntegralStructureAction(group, source.inclusion()).with_stable_containing_bound(bound.inclusion())
    representation = action.finite_representation()
    quotient = action.finite_module()
    submodules = representation.orbit_submodules()
    assert quotient.cardinality() == cardinal(36**2)
    assert representation.g_set().cardinality() == cardinal(2)
    assert all(submodule.cardinality() == cardinal(36) for submodule in submodules)
    points = tuple(representation.g_set())
    for position, point in enumerate(points):
        assert representation.g_set().act(rotation * rotation, point) == point
        image = action.quotient_automorphism(rotation)
        destination = int(representation.g_set().act(rotation, point))
        assert all(submodules[destination].inclusion().is_in_image(
            image(submodules[position].inclusion()(generator))
        ) for generator in submodules[position].module_generators())
    group_generators = tuple(action.stabilizer().group_generators())
    assert all((generator(e), generator(f)) in ((e, f), (-e, -f)) for generator in group_generators)
    assert any((generator(e), generator(f)) == (-e, -f) for generator in group_generators)
    witness = action.transporter(target.inclusion())
    assert all(target.inclusion().is_in_image(space(witness(source.inclusion()(generator).underlying_element())))
               for generator in source.module_generators())
    assert all(source.inclusion().is_in_image(space((~witness)(target.inclusion()(generator).underlying_element())))
               for generator in target.module_generators())
    assert all((~witness)(witness(generator)) == generator for generator in (e, f))

