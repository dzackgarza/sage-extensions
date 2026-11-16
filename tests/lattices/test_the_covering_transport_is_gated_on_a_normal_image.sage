r"""A plane's covering is transported only where the subgroup is invariant under conjugation.

The flags at a plane cusp are the orbits of the lines of the plane under the
subgroup's stabilizer of it, and the incidence carries one plane's family to
another plane by the composite of the two planes' lifts.  Carried so, the
family is the target plane's own exactly when conjugation by an ambient
isometry preserves the subgroup: an element ``g`` of the source's stabilizer
acts at the target as ``m g m^-1`` with ``m`` the carrying isometry, so the
carried family's orbits are the target stabilizer's only when that conjugate is
again in the subgroup.

A kernel of a character is normal in the orthogonal group whatever the
character is, and so is the preimage of any normal subgroup of the finite
image; that is what ``OrthogonalCharacterQuotient.preserves_conjugation``
decides.  A preimage of a *proper* subgroup is decided by that subgroup's
normality in the finite image, so properness alone does not separate the two
answers, and this test states the non-normality rather than the properness: an
ambient generator conjugates one of the image's generators out of the image.

The specimen is ``U + U(2) + <-2> + <-2>``, whose discriminant image has order
twelve: enough for a point stabilizer to be a proper image, which is the case a
transported covering must not be used in.  ``U + U + <-4> + <-4>`` has an image
of order eight and is non-abelian as well.

The proper *normal* image is the other side of the same statement, and it is
its own specimen: ``tests/lattices/test_the_preimage_of_a_normal_image_is_normal.sage``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u2_m2_m2():
    r"""``U + U(2) + <-2> + <-2>``: rank six, discriminant group of order sixteen."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)(((0, 2), (2, 0)))
        + Lattices(ZZ)(((-2,),))
        + Lattices(ZZ)(((-2,),))
    )


def _class_of(lattice, label):
    r"""The discriminant class of a named module generator's primitive dual."""
    return lattice.discriminant_class(
        lattice.primitive_dual(lattice.module_generator(label))
    )


def test_a_kernel_is_invariant_and_a_proper_preimage_is_not() -> None:
    r"""The two kernels answer yes; a preimage of a proper point stabilizer answers no."""
    lattice = _u_u2_m2_m2()
    image = lattice.discriminant_group().orthogonal_group()
    assert image.cardinality() == cardinal(12)

    kernels = (
        lattice.stable_orthogonal_group(),
        lattice.stable_orthogonal_group().intersection(lattice.O_plus()),
    )
    for subgroup in kernels:
        quotient = subgroup.finite_character_quotient()
        assert quotient.subgroup_image_order() == 1
        assert quotient.preserves_conjugation() is True

    point = frozenset((_class_of(lattice, 2), _class_of(lattice, 3)))
    stabilizer = lattice.Aut().discriminant_point_stabilizer(point)
    quotient = stabilizer.finite_character_quotient()
    assert quotient.index() > 1
    assert quotient.subgroup_image_order() > 1
    # The image is not normal in the finite image: some generator of the
    # orthogonal group of the discriminant form conjugates a generator of this
    # stabilizer's image out of it.  Properness alone would not say this, and
    # the preimage of a proper *normal* image is invariant.
    stabilizer_image = stabilizer.discriminant_image()
    assert stabilizer_image.cardinality() == quotient.subgroup_image_order()
    assert any(
        ambient * stabilizer_generator * ~ambient not in stabilizer_image
        for ambient in image.group_generators()
        for stabilizer_generator in stabilizer_image.group_generators()
    )
    assert quotient.preserves_conjugation() is False
