r"""Root-lattice discriminant actions.

Conway--Sloane, SPLAG, chapter 4: ``A_n`` has cyclic glue group and the diagram
automorphism acts by negation; ``D_4`` has trivial Weyl action on its glue but
full triality permutes the three nonzero classes.
"""

from sage_extensions.all import *


def test_a4_discriminant_image_is_negation_on_c5() -> None:
    lattice = Lattices.A4
    form = lattice.discriminant_group()
    image = lattice.Aut().discriminant_image()
    generator = form.module_generators()[0]

    assert form.invariants().cardinality() == 1
    assert form.invariants()[0] == 5
    assert image.cardinality() == 2
    assert Set(image.orbit(generator)) == Set((generator, -generator))


def test_the_weyl_group_of_D4_acts_trivially_on_its_glue_and_triality_permutes_the_three_nonzero_classes() -> None:
    r"""|Aut(D4)| = |W(F4)| = 1152, |W(D4)| = 2^3 * 4! = 192, and
    Aut(D4) / W(D4) = S3 maps isomorphically onto O(q_{D4}) = GL_2(F_2)
    (Conway--Sloane, SPLAG, ch. 4)."""
    lattice = Lattices.D4
    automorphisms = lattice.Aut()
    weyl = lattice.weyl_group()
    full_image = automorphisms.discriminant_image()
    form = lattice.discriminant_group()
    generator = form.module_generators()[0]
    nonzero = Set(element for element in form if element != form.zero())

    assert automorphisms.cardinality() == 1152
    assert weyl.cardinality() == 192
    assert weyl.discriminant_image().cardinality() == 1
    assert full_image.cardinality() == 6
    assert form.orthogonal_group().cardinality() == 6
    assert nonzero.cardinality() == 3
    assert Set(full_image.orbit(generator)) == nonzero


def test_d4_triality_fuses_the_three_order_two_glue_subgroups() -> None:
    lattice = Lattices.D4
    form = lattice.discriminant_group()
    triality = lattice.Aut().discriminant_image()
    subgroup_orbits = form.orbits_on_subobjects(group=triality)
    isotropic_orbits = form.orbits_on_isotropic_subobjects(group=triality)

    assert Set(orbit.cardinality() for orbit in subgroup_orbits) == Set((1, 3))
    assert sum(orbit.cardinality() for orbit in subgroup_orbits) == 5
    assert isotropic_orbits.cardinality() == 1
    assert isotropic_orbits[0].cardinality() == 1
