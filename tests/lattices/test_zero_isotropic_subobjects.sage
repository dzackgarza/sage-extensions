r"""The zero sublattice is primitive, null and fixed by every isometry.

In <6> it is the unique null sublattice. Its stabilizer is O(<6>)={1,-1},
whose discriminant image on Z/6 also has order two. SO(<6>) is trivial
and still has one orbit on the zero sublattice.
"""

from sage_extensions.all import *


def test_zero_null_subobject_is_the_unique_rank_zero_orbit():
    ambient = Lattices(ZZ)([[6]])
    zero = ambient.primitive_isotropic_subobject()
    assert zero.module_rank() == cardinal(0)
    assert zero.is_primitive()
    for group in (ambient.O(), ambient.SO()):
        orbits = group.isotropic_orbit_representatives(0)
        assert orbits.cardinality() == cardinal(1)
        representative = next(iter(orbits))
        assert representative.module_rank() == cardinal(0)
        witness = group.isotropic_equivalence_witness(zero, representative)
        assert witness in group
        assert all((~witness)(witness(point)) == point for point in ambient.module_generators())


def test_zero_null_stabilizer_has_the_full_discriminant_image():
    ambient = Lattices(ZZ)([[6]])
    zero = ambient.primitive_isotropic_subobject()
    image = zero.stabilizer_discriminant_image()
    assert image.cardinality() == cardinal(2)
    generator = next(iter(ambient.module_generators()))
    minus = ambient.Aut()({label: -generator for label in ambient.module_generating_set()})
    assert ambient.discriminant_representation()(minus) in image
