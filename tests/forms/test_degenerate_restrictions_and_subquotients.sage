r"""A genuinely degenerate torsion form from the published Coble discriminant form.

A discriminant form is nondegenerate, and so is ``H^perp/H`` for an isotropic
``H`` — that is the guarantee, and it holds here (the quotient has order 512).
What a nondegenerate ambient form does *not* guarantee is nondegeneracy of an
arbitrary intermediate ``K`` or of a restriction: the span of an isotropic class
``x`` and an orthogonal partner with nonzero ``q`` has polar radical ``<x>`` —
here, of order two — which is a genuine degenerate torsion form on the published
discriminant form, not a constructed toy.

For it, the radical is the kernel of ``b(x, -)``, the reduction descends (``q``
vanishes on that radical), and the isometry decision answers with a typed, checked
witness against the invariant-factor reframing.  That is the radical capability
exercised on a downstream object rather than on a specimen built for it.
"""

from itertools import combinations

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
    TorsionFormIsometry,
    _torsion_form_orthogonal_subobject,
    _torsion_form_subquotient,
)

from sage.matrix.constructor import diagonal_matrix
from sage.rings.integer_ring import ZZ as SageZZ


def _coble_discriminant_form():
    r"""The discriminant form of ``S = <2> + <-2>^{10}``, of order 2048."""
    lattice = Lattices(ZZ)(
        [list(row) for row in diagonal_matrix(SageZZ, [2] + [-2] * 10).rows()]
    )
    return lattice.discriminant_group()


def _isotropic_class_of_order_two(form):
    r"""A nonzero class with ``q = 0``, found among sums of two generators."""
    zero = form.value_module().zero()
    generators = tuple(form.module_generators())
    for left, right in combinations(range(len(generators)), 2):
        element = generators[left] + generators[right]
        if element != form.zero() and (form.q(element) == zero) is True:
            return element
    raise AssertionError("the Coble discriminant form has no isotropic class of order two")


def test_the_maximal_subquotient_is_nondegenerate() -> None:
    r"""``H^perp/H`` for an isotropic order-two subgroup: order 512, no radical."""
    form = _coble_discriminant_form()
    isotropic = _isotropic_class_of_order_two(form)
    subgroup = form.subobject_generated_by((isotropic,))

    assert subgroup.cardinality() == 2
    perpendicular = _torsion_form_orthogonal_subobject(
        form, subgroup, quadratic=True
    )
    assert perpendicular.cardinality() == 1024

    subquotient = _torsion_form_subquotient(form, subgroup, perpendicular, quadratic=True)
    assert subquotient.cardinality() == 512
    assert subquotient.polar_radical().cardinality() == 1


def test_a_small_restriction_can_have_a_radical_and_is_then_reduced_and_decided() -> None:
    r"""The span of the isotropic class and an orthogonal partner: a genuine degenerate form."""
    form = _coble_discriminant_form()
    isotropic = _isotropic_class_of_order_two(form)
    subgroup = form.subobject_generated_by((isotropic,))
    perpendicular = _torsion_form_orthogonal_subobject(form, subgroup, quadratic=True)
    zero = form.value_module().zero()
    partner = next(
        candidate
        for candidate in tuple(
            perpendicular.inclusion()(generator)
            for generator in perpendicular.module_generators()
        )
        if (form.q(candidate) == zero) is not True
    )

    restriction = form.subobject_generated_by((isotropic, partner))

    assert restriction.cardinality() == 4
    radical = restriction.polar_radical()
    assert radical.cardinality() == 2
    embedded = tuple(
        radical.inclusion()(generator) for generator in radical.module_generators()
    )
    assert restriction.form_vanishes_on(embedded) is True

    quotient = restriction.nondegenerate_quotient()
    assert quotient.cardinality() == 2
    assert tuple(quotient.invariants()) == (2,)

    reframed = restriction.invariant_factor_form().codomain()
    assert restriction.is_isomorphic(reframed) is True
    witness = restriction.isometry_to(reframed)
    assert isinstance(witness, TorsionFormIsometry)
    assert witness.is_quadratic() is True
