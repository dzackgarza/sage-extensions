r"""Base change of an order in a number field extends objects and morphisms."""

from sage_extensions.all import *  # noqa: F401,F403


def _root_five_field():
    polynomial_ring = QQ.polynomial_ring("x")
    x = polynomial_ring.algebra_generator("x")
    return (x**2 - 5).number_field("a")


def test_root_five_order_base_changes_to_the_number_field() -> None:
    field = _root_five_field()
    selected = field.order_generated_by(field.primitive_element())
    extended = field.base_change_functor(ZZ)(selected)

    assert extended.base_ring() is QQ
    assert extended.module_rank() == 2
    assert extended in Fields()
    assert extended.is_isomorphic(field.as_algebra())


def test_base_change_functor_extends_conjugation() -> None:
    field = _root_five_field()
    selected = field.underlying_algebra(ZZ)
    scalar_extension = field.base_change_functor(ZZ)
    conjugation = selected.Mor(selected)(-field.primitive_element())
    extended = scalar_extension(conjugation)
    source = scalar_extension(selected)
    generator = source.algebra_generator(source.algebra_generating_set()[0])

    assert extended.domain() is source
    assert extended.codomain() is source
    assert extended(generator) == -generator
