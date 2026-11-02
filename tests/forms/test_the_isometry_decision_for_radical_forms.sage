r"""The isometry decision for torsion forms whose polar form has a radical.

The normal-form engine states only nondegenerate polar forms, so a degenerate
form used to be refused outright.  It is now decided from represented data:

* ``False`` needs a proof, and three are used — the order, the invariant factors
  of the module, and the invariants of the polar radical (an isometry maps the
  radical onto the radical because it preserves the polar form) — plus, where the
  form vanishes on the radical and therefore descends, the quotient form.
* ``True`` needs a witness: both forms are transported to their invariant-factor
  framings, where the module is presented by the same generators and relations,
  a module automorphism of that framing is tried, and the composite is admitted
  by the typed isometry constructor with ``check``.  A form is never called
  isometric because its invariants agree.
* Anything else is reported as undecided, with the reason, rather than guessed.

The specimens are the degenerate cases that a lattice or subform produces:
``Z/4`` with ``q = 1/2`` (radical ``{0, 2}``, ``q`` vanishing there), the two
unit twists ``1/2`` and ``3/2`` on ``Z/4`` (same order, same invariants, same
radical — separated by the quotient form), ``(Z/2)^2`` diagonal and skew (the
radical order separates them), and ``(Z/4)^2`` with ``diag(1/2, 1/2)``.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.framed.formed import (
    TorsionBilinearFormModules,
    TorsionQuadraticFormModules,
)
from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
    TorsionFormIsometry,
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


def _dual_numbers():
    return _quadratic([[4]], [[HALF]])


def test_a_degenerate_form_is_isometric_to_a_copy_with_a_typed_witness() -> None:
    r"""``Z/4`` with ``q = 1/2``: the witness preserves ``q`` and its inverse composes."""
    first, second = _dual_numbers(), _dual_numbers()

    assert first is not second
    assert first.is_isomorphic(second) is True
    witness = first.isometry_to(second)
    assert isinstance(witness, TorsionFormIsometry)
    assert witness.domain() is first
    assert witness.codomain() is second

    generator = first.module_generators()[0]
    image = witness.forward()(generator)
    assert second.q(image) == first.q(generator)
    assert witness.inverse()(image) == generator


def test_the_radical_order_separates_a_form_from_its_zero_form() -> None:
    r"""``q = 1/2`` has radical ``{0, 2}``; the zero form's radical is all of ``Z/4``."""
    form = _dual_numbers()
    zero = _quadratic([[4]], [[0]])

    assert form.polar_radical().cardinality() == 2
    assert zero.polar_radical().cardinality() == 4
    assert form.is_isomorphic(zero) is False
    assert form.isometry_to(zero) is None


def test_differing_module_invariants_are_not_isometric() -> None:
    r"""``Z/4`` and ``(Z/2)^2`` have different invariant factors."""
    form = _dual_numbers()
    other = _quadratic([[2, 0], [0, 2]], [[HALF, 0], [0, HALF]])

    assert tuple(form.invariants()) == (4,)
    assert tuple(other.invariants()) == (2, 2)
    assert form.is_isomorphic(other) is False
    assert form.isometry_to(other) is None


def test_the_quotient_form_separates_the_two_unit_twists() -> None:
    r"""``1/2`` and ``3/2`` on ``Z/4`` agree in order, invariants and radical, and differ after reduction."""
    form = _dual_numbers()
    twisted = _quadratic([[4]], [[3 * HALF]])

    assert form.cardinality() == twisted.cardinality()
    assert tuple(form.invariants()) == tuple(twisted.invariants())
    assert form.polar_radical().cardinality() == twisted.polar_radical().cardinality()
    assert form.nondegenerate_quotient().is_isomorphic(
        twisted.nondegenerate_quotient()
    ) is False

    assert form.is_isomorphic(twisted) is False
    assert form.isometry_to(twisted) is None


def test_two_forms_of_one_module_with_different_radicals_are_separated() -> None:
    r"""``(Z/2)^2`` diagonal has trivial radical; the skew Gram has one of order two."""
    diagonal = _quadratic([[2, 0], [0, 2]], [[HALF, 0], [0, HALF]])
    skew = _quadratic([[2, 0], [0, 2]], [[HALF, HALF], [HALF, HALF]])

    assert diagonal.polar_radical().cardinality() == 1
    assert skew.polar_radical().cardinality() == 2
    assert diagonal.is_isomorphic(skew) is False
    assert skew.is_isomorphic(diagonal) is False


def test_a_degenerate_form_of_higher_rank_is_decided() -> None:
    r"""``(Z/4)^2`` with ``diag(1/2, 1/2)``: radical of order four, copy is isometric."""
    first = _quadratic([[4, 0], [0, 4]], [[HALF, 0], [0, HALF]])
    second = _quadratic([[4, 0], [0, 4]], [[HALF, 0], [0, HALF]])

    assert first.polar_radical().cardinality() == 4
    assert first.is_isomorphic(second) is True
    witness = first.isometry_to(second)
    assert isinstance(witness, TorsionFormIsometry)
    for generator in first.module_generators():
        assert second.q(witness.forward()(generator)) == first.q(generator)


def test_an_undecided_pair_is_reported_as_undecided_not_as_isometric() -> None:
    r"""Three generators of order ``16``: wider searches are refused, not guessed.

    The identity of the two framings decides a copy at once; a *different* form on
    the same module needs a search wider than the transport cap, and the answer is
    then the undecided error, which says so.
    """
    copy = _quadratic(
        [[16, 0, 0], [0, 16, 0], [0, 0, 16]],
        [[QQ(1) / QQ(8), 0, 0], [0, QQ(1) / QQ(8), 0], [0, 0, QQ(1) / QQ(8)]],
    )
    same_data = _quadratic(
        [[16, 0, 0], [0, 16, 0], [0, 0, 16]],
        [[QQ(1) / QQ(8), 0, 0], [0, QQ(1) / QQ(8), 0], [0, 0, QQ(1) / QQ(8)]],
    )
    assert copy.is_isomorphic(same_data) is True

    other = _quadratic(
        [[16, 0, 0], [0, 16, 0], [0, 0, 16]],
        [[QQ(1) / QQ(8), 0, 0], [0, QQ(1) / QQ(8), 0], [0, 0, QQ(3) / QQ(8)]],
    )
    with pytest.raises(TypeError, match="undecided"):
        copy.is_isomorphic(other)


def test_the_bilinear_flavour_reduces_and_decides_the_same_way() -> None:
    r"""``b`` on ``Z/4``: the radical is order two, the quotient exists, and the decision answers.

    A bilinear form always descends to ``M/R`` — its polar form vanishes on its own
    radical by definition — so the reduction is available there without the
    quadratic vanishing condition, while the witness remains a typed isometry of
    the bilinear flavour.
    """
    values = FractionFieldQuotients(ZZ)(1)

    def bilinear(relation_rows, gram):
        return TorsionBilinearFormModules(ZZ).from_relations_and_gram(
            relation_rows, gram, values
        )

    first, second = bilinear([[4]], [[HALF]]), bilinear([[4]], [[HALF]])
    zero = bilinear([[4]], [[0]])

    assert first.polar_radical().cardinality() == 2
    assert first.nondegenerate_quotient().cardinality() == 2
    assert first.is_isomorphic(second) is True
    witness = first.isometry_to(second)
    assert isinstance(witness, TorsionFormIsometry)
    assert witness.is_quadratic() is False
    generator = first.module_generators()[0]
    assert second.b(witness.forward()(generator), witness.forward()(generator)) == first.b(
        generator, generator
    )

    assert zero.polar_radical().cardinality() == 4
    assert first.is_isomorphic(zero) is False
    assert first.isometry_to(zero) is None


def test_an_isometry_through_a_coordinate_transposition_is_found() -> None:
    r"""``diag(1/2, 3/2)`` and ``diag(3/2, 1/2)`` on ``(Z/4)^2``: carried by a transposition.

    No diagonal rescaling can carry ``1/2`` to ``3/2`` (the units of ``Z/4`` square
    to 1), so the scale candidates fail, and the swap of the two equal-invariant
    coordinates is the transport that verifies.  Quotient forms are isomorphic too,
    which is necessary but not the witness itself.
    """
    first = _quadratic([[4, 0], [0, 4]], [[HALF, 0], [0, 3 * HALF]])
    second = _quadratic([[4, 0], [0, 4]], [[3 * HALF, 0], [0, HALF]])

    assert first.polar_radical().cardinality() == second.polar_radical().cardinality()
    assert first.nondegenerate_quotient().is_isomorphic(
        second.nondegenerate_quotient()
    ) is True

    assert first.is_isomorphic(second) is True
    witness = first.isometry_to(second)
    assert isinstance(witness, TorsionFormIsometry)
    assert [
        second.q(witness.forward()(generator))
        for generator in first.module_generators()
    ] == [first.q(generator) for generator in first.module_generators()]
