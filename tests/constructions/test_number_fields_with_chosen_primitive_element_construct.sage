r"""Q(i) retains the primitive element i and its defining polynomial x^2+1."""

from sage_extensions.all import *  # noqa: F401,F403


def test_gaussian_field_retains_selected_primitive_element() -> None:
    field = QuadraticField(-1, "i")
    i = field.primitive_element()
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    images = field.embedding_images(CC)

    assert field in NumberFieldsWithChosenPrimitiveElement()
    assert field.defining_polynomial() == x**2 + 1
    assert i * i == -field.one()
    assert images.cardinality() == cardinal(2)
    assert set(images) == set(i.conjugates(CC))

