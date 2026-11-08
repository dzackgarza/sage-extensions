r"""Triality on the D4 discriminant form through its Core.

The three nonzero classes have the same quadratic value. A three-cycle
therefore preserves the form and has an inverse distinct from itself.
Normalization must give the same action in both directions on every class.
"""

from sage_extensions.all import *


def test_normalization_preserves_triality_and_its_inverse() -> None:
    form = Lattices(ZZ)("D4").discriminant_quadratic_form()
    group = form.O()
    family = tuple(group.group_generators())
    triality = next(
        left * right
        for left in family
        for right in family
        if (left * right)**2 != group.one()
    )
    normalization = group.normalization_homomorphism()
    values = form.value_module()
    value_identity = values.module_category().Mor(values, values).identity()
    formed = form.category().Mor(form, form)
    forward = formed((triality.forward(), value_identity))
    inverse = formed((triality.inverse_morphism(), value_identity))
    arrow = normalization.domain()(forward, inverse)
    image = normalization(arrow)

    assert image**3 == group.one()
    assert image**2 != group.one()
    for point in form:
        assert image(point) == triality(point)
        assert image.inverse()(point) == triality.inverse()(point)
        assert image.inverse()(image(point)) == point
        assert form.q(image(point)) == form.q(point)
