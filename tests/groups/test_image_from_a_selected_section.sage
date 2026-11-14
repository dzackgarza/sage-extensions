r"""Squaring C6 has its even-power subgroup as image, of order three.

A chosen root on that image is a set section. Its domain determines
image membership; the images of source generators generate that same subgroup.
"""

from sage_extensions.all import *


def test_squaring_image_retains_its_section_and_finite_group_structure():
    group = Groups.C(6)
    generator = group.group_generators()[0]
    square = group.Mor(group)(lambda element: element**2)
    image_locus = Set(tuple(generator**(2*exponent) for exponent in range(3)))
    roots = {generator**(2*exponent): generator**exponent for exponent in range(3)}
    square.select_section(Sets().Mor(image_locus, group)(lambda element: roots[element]))
    image = square.image()
    assert image in Groups().Finite()
    for exponent in range(6):
        assert (generator**exponent in image) == (exponent % 2 == 0)
    assert image.cardinality() == cardinal(3)
    assert group.subgroup(tuple(image.group_generators())).cardinality() == cardinal(3)
    for element in image_locus:
        assert square(square.lift(element)) == element
