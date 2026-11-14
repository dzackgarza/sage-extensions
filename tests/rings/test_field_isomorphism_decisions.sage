r"""Field isomorphism is decided by what the fields state, or not at all.

Two presentations of one field are isomorphic and their defining polynomials say
nothing about it: ``Q(sqrt 5)`` and ``Q(sqrt 20)`` are the same field, while
``Q(sqrt 5)`` and ``Q(sqrt 2)`` have the same degree and characteristic and are
not isomorphic.  So the decision may not be a comparison of presentations, and it
may not be a guess from shared invariants: characteristic and cardinality refute,
the retained number-field realizations decide, and everything else states the
proposition.  An undecided pair reported as non-isomorphic would be a false
theorem, which is the one thing this owner must not produce.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.logic import Propositions

import pytest


def _root_five():
    return QuadraticField(5)


def test_the_order_tensored_with_the_rationals_is_its_field() -> None:
    r"""``ZZ[sqrt 5] (x)_ZZ QQ`` is ``QQ(sqrt 5)``, however it is presented."""
    field = _root_five()
    order = field.order_generated_by(field.primitive_element())
    extended = field.base_change_functor(ZZ)(order)

    assert extended.is_isomorphic(field.as_algebra())
    assert extended.is_isomorphic(field)
    assert field.is_isomorphic(extended)


def test_one_field_in_two_presentations_is_isomorphic() -> None:
    r"""``Q(sqrt 20) = Q(sqrt 5)`` although the defining polynomials differ."""
    assert _root_five().is_isomorphic(QuadraticField(20))
    assert QuadraticField(20).is_isomorphic(_root_five())
    assert _root_five().is_isomorphic(_root_five().as_algebra())


def test_fields_of_one_degree_and_characteristic_can_fail_to_be_isomorphic() -> None:
    assert not _root_five().is_isomorphic(QuadraticField(2))
    assert not _root_five().is_isomorphic(QuadraticField(-5))
    assert not QuadraticField(2).is_isomorphic(_root_five())


def test_a_field_is_not_isomorphic_to_a_ring_that_is_not_one() -> None:
    assert not _root_five().is_isomorphic(ZZ)
    assert not ZZ.is_isomorphic(_root_five())


def test_finite_fields_are_refuted_by_characteristic_and_cardinality() -> None:
    assert GF(4).is_isomorphic(GF(4))
    assert not GF(4).is_isomorphic(GF(9))
    assert not GF(4).is_isomorphic(GF(8))
    assert not GF(8).is_isomorphic(GF(4))


def test_an_undecided_pair_states_the_proposition_and_is_not_refuted() -> None:
    r"""``QQ`` against ``Q(sqrt 5)`` is undecided here, and must not be ``False``.

    Neither operand's retained realization decides it -- ``QQ``'s engine is not a
    number field -- so the answer is the proposition.  Answering ``False`` there
    would be a theorem about all fields that this owner has not established.
    """
    field = _root_five()

    for left, right in ((QQ, field), (field, QQ)):
        answer = left.is_isomorphic(right)
        assert answer in Propositions
        assert answer is not True
        assert answer is not False


def test_a_non_ring_operand_is_refused() -> None:
    with pytest.raises(TypeError):
        _root_five().is_isomorphic("Q(sqrt 5)")


def test_the_isomorphic_to_alias_states_the_same_decision() -> None:
    assert _root_five().is_isomorphic_to(QuadraticField(20))
    assert not _root_five().is_isomorphic_to(QuadraticField(-5))
