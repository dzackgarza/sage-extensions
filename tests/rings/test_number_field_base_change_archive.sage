r"""The order ``ZZ[sqrt 5]`` of ``QQ(sqrt 5)`` and its base change to ``QQ``."""

from sage_extensions.all import *  # noqa: F401,F403


def _quadratic_field():
    polynomial_ring = QQ.polynomial_ring("x")
    x = polynomial_ring.algebra_generator("x")
    return (x**2 - 5).number_field("a")


def test_root_five_order_has_index_two_in_the_maximal_order() -> None:
    r"""``O_{QQ(sqrt 5)} = ZZ[(1 + sqrt 5)/2]`` has discriminant ``5`` and
    ``ZZ[sqrt 5]`` has discriminant ``20 = 2^2 * 5``, so the index is ``2``
    (Neukirch, *Algebraic Number Theory*, I.2.12 and I.2.10)."""
    field = _quadratic_field()
    a = field.primitive_element()
    selected = field.order_generated_by(a)
    maximal = field.ring_of_integers()
    golden = (field.one() + a) / 2

    assert not selected.is_maximal()
    assert maximal.is_maximal()
    assert selected.discriminant() == 20
    assert maximal.discriminant() == 5
    assert selected.index_in(maximal) == 2
    assert golden in maximal
    assert golden not in selected


def test_root_five_order_tensored_with_the_rationals_is_the_number_field() -> None:
    r"""``ZZ[sqrt 5] (x)_ZZ QQ = QQ[x]/(x^2 - 5) = QQ(sqrt 5)``: localization at
    ``ZZ - {0}`` of an order is its fraction field (Neukirch, I.12)."""
    field = _quadratic_field()
    selected = field.order_generated_by(field.primitive_element())
    extended = field.base_change_functor(ZZ)(selected)

    assert extended.base_ring() is QQ
    assert extended.module_rank() == 2
    assert extended in Fields()
    assert extended.is_isomorphic(field.as_algebra())


def test_number_field_base_change_functor_acts_on_a_nonidentity_order_map() -> None:
    field = _quadratic_field()
    selected = field.underlying_algebra(ZZ)
    scalar_extension = field.base_change_functor(ZZ)
    conjugation = selected.Mor(selected)(-field.primitive_element())
    extended = scalar_extension(conjugation)

    source = scalar_extension(selected)
    generator = source.algebra_generator(source.algebra_generating_set()[0])
    assert extended.domain() is source
    assert extended.codomain() is source
    assert extended(generator) == -generator
