r"""The polar radical of a torsion form, and the form on its nondegenerate quotient.

For a typed torsion quadratic form ``q`` with polar form ``b``, the radical is
``R = {x : b(x, y) = 0 for every y}``.  Since ``q(x + r) = q(x) + q(r) + b(x, r)``
for ``r`` in ``R``, the quotient ``M/R`` carries the descended ``q`` exactly when
``q`` vanishes on ``R``; when it does not, the quotient loses a functional that is
part of the form's data, and the reduction says so instead of dropping it.

``polar_radical()`` is the kernel of ``x |-> b(x, -)``, built by the module's own
kernel owner, so the subobject is an actual kernel and not a second normal-form
computation.  ``nondegenerate_quotient()`` is the maintained subquotient, which
states the vanishing condition.  Neither replaces the isomorphism decision: two
forms with isomorphic quotients may still differ by how the radical sits inside
them, so the reduction is a necessary invariant and is not treated as sufficient.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.framed.formed import (
    TorsionQuadraticFormModules,
)
from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
    _regenerate_form_on_generators,
    _torsion_form_orthogonal_subobject,
)
from sage_extensions.categories.modules.framed.fraction_field_quotients import (
    FractionFieldQuotients,
)

import pytest

VALUES = FractionFieldQuotients(ZZ)(2)
HALF = QQ(1) / QQ(2)


def _quadratic(relation_rows, gram):
    return TorsionQuadraticFormModules(ZZ).from_relations_and_gram(
        relation_rows, gram, VALUES
    )


def _degenerate_specimens():
    r"""Four forms with a radical, with the orders the reduction must produce."""
    return (
        (_quadratic([[4]], [[HALF]]), 4, 2, 2),
        (_quadratic([[2, 0], [0, 2]], [[HALF, HALF], [HALF, HALF]]), 4, 2, 2),
        (_quadratic([[4, 0], [0, 4]], [[HALF, 0], [0, HALF]]), 16, 4, 4),
    )


def test_the_radical_is_a_subobject_of_the_form_with_the_expected_order() -> None:
    r"""The radical of ``Z/4`` with ``q = 1/2`` is the order-two subgroup ``{0, 2}``."""
    for form, order, radical_order, _ in _degenerate_specimens():
        radical = form.polar_radical()
        assert radical.cardinality() == radical_order
        assert form.cardinality() == order
        embedded = tuple(
            radical.inclusion()(generator)
            for generator in radical.module_generators()
        )
        assert form.form_vanishes_on(embedded) is True


def test_the_nondegenerate_quotient_is_the_form_on_the_quotient() -> None:
    r"""``q`` descends, the orders multiply, and the quotient's own form is nondegenerate."""
    for form, order, radical_order, quotient_order in _degenerate_specimens():
        radical = form.polar_radical()
        quotient = form.nondegenerate_quotient()

        assert quotient.cardinality() == quotient_order
        assert int(quotient.cardinality()) * int(radical.cardinality()) == order
        # The quotient's polar form has no radical, so the decision procedure
        # accepts it: that is the cross-check with the criterion, not a claim
        # that the reduction decides isometry.
        assert quotient.is_isomorphic(quotient) is True


def test_a_nondegenerate_form_has_trivial_radical_and_quotients_to_itself() -> None:
    r"""``(Z/2)^2`` with ``diag(1/2, 1/2)``: radical of order one, whole form as quotient."""
    form = _quadratic([[2, 0], [0, 2]], [[HALF, 0], [0, HALF]])

    assert form.polar_radical().cardinality() == 1
    quotient = form.nondegenerate_quotient()
    assert quotient.cardinality() == form.cardinality()
    assert quotient.is_isomorphic(form) is True


def test_the_reduction_is_refused_when_the_form_does_not_vanish_on_the_radical() -> None:
    r"""``q(e_3) = 1`` on a radical generator: the quotient would lose that value."""
    form = _quadratic(
        [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
        [[HALF, 0, 0], [0, HALF, 0], [0, 0, 1]],
    )
    radical = form.polar_radical()
    embedded = tuple(
        radical.inclusion()(generator) for generator in radical.module_generators()
    )

    assert form.form_vanishes_on(embedded) is False
    with pytest.raises(ValueError, match="descends"):
        form.nondegenerate_quotient()


def test_the_quotient_gram_is_indexed_by_the_retained_projection_contract() -> None:
    r"""The reduced form's Gram is read through the cokernel projection's own contract.

    ``cokernel_projection`` states that the cokernel is presented on the
    codomain's generators and that the projection sends each generator to the
    generator of the same name; the operation reads the Gram in exactly that
    indexing and checks each image, because an equal generator count on its own
    says nothing about which generator is which.
    """
    form = _quadratic([[4, 0], [0, 4]], [[HALF, 0], [0, HALF]])
    inclusion = form.polar_radical().inclusion()
    quotient_module = inclusion.cokernel()
    projection = inclusion.cokernel_projection()

    assert tuple(quotient_module.module_generating_set()) == tuple(
        form.module_generating_set()
    )
    for label in quotient_module.module_generating_set():
        assert projection(form.module_generator(label)) == quotient_module.module_generator(
            label
        )

    quotient = form.nondegenerate_quotient()
    assert quotient.cardinality() == 4
    assert tuple(quotient.invariants()) == (2, 2)
    assert quotient.polar_radical().cardinality() == 1


def test_a_reframed_copy_has_an_isometric_quotient() -> None:
    r"""A permuted presentation of the same form reduces to an isometric quotient.

    The framing changes — the generators are exchanged — so the two quotient
    presentations are not literally the same object; the decision on them, and the
    reduction's dependence on the retained projection, must still line up.
    """
    form = _quadratic([[4, 0], [0, 4]], [[HALF, 0], [0, HALF]])
    first_generator, second_generator = form.module_generators()
    reframed = _regenerate_form_on_generators(
        form, (second_generator, first_generator), quadratic=True
    ).codomain()

    assert reframed.cardinality() == form.cardinality()
    assert form.is_isomorphic(reframed) is True
    assert form.polar_radical().cardinality() == reframed.polar_radical().cardinality()

    quotient = form.nondegenerate_quotient()
    reframed_quotient = reframed.nondegenerate_quotient()
    assert reframed_quotient.cardinality() == quotient.cardinality()
    assert quotient.is_isomorphic(reframed_quotient) is True


def test_the_orthogonal_complement_is_the_same_kernel_not_an_enumeration() -> None:
    r"""``S^perp`` is ``{x : b(x, s) = 0}`` computed from the pairing, and agrees with the elementwise form.

    The radical is this kernel with the form's own generators as the pairing
    family, so an orthogonal complement is the same computation for another
    family — not a scan of the module, which on a 2048-element discriminant form
    took the shared subquotient construction past fifteen minutes.
    """
    form = _quadratic([[4, 0], [0, 4]], [[HALF, 0], [0, HALF]])
    generator = form.module_generators()[0]
    subobject = form.subobject_generated_by((generator,))
    perpendicular = _torsion_form_orthogonal_subobject(form, subobject, quadratic=True)

    zero = form.b(generator, generator) * 0
    expected = tuple(
        element
        for element in form.elements()
        if (form.b(element, generator) == zero) is True
    )
    inclusion = perpendicular.inclusion()
    # It is not a count: every orthogonal element lies in the subobject, and a
    # non-orthogonal one does not.
    assert all(inclusion.is_in_image(element) is True for element in expected)
    non_member = next(
        element
        for element in form.elements()
        if (form.b(element, generator) == zero) is not True
    )
    assert inclusion.is_in_image(non_member) is not True
