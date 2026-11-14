r"""Exact integral membership in a fractional two-generator span.

For L=Z(e/2)+Z((e+f)/3), x*e+y*f lies in L precisely when
3*y and 2*(x-y) are integral. Every other basis coordinate must vanish.
This criterion also applies inside a free module on an infinite basis.
"""

from sage_extensions.all import *

import pytest


@pytest.mark.parametrize("infinite", (False, True), ids=("finite_basis", "infinite_basis"))
def test_fractional_span_lifts_have_exact_integral_coordinates(infinite):
    labels = ZZ if infinite else ("east", "north", "outside")
    module = QQ.free_module(labels)
    selected = (ZZ(17), ZZ(101), ZZ(1000003)) if infinite else labels
    e, f, outside = (module.module_generator(label) for label in selected)
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(module)
    half, third = QQ.one() / 2, QQ.one() / 3
    inclusion = space.subobject_on((space(half * e), space(third * (e + f)))).inclusion()

    admitted = (module.zero(), half * e, third * (e + f), half * e + third * (e + f), f)
    for point in admitted:
        image = space(point)
        assert inclusion.is_in_image(image)
        preimage = inclusion.lift(image)
        assert preimage.parent() is inclusion.domain()
        assert inclusion(preimage) == image

    for point in ((half * half) * e, third * half * e + third * f, outside):
        assert not inclusion.is_in_image(space(point))
