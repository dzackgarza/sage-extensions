r"""``Q(sqrt 5)`` as a two-dimensional ``Q``-algebra, and multiplication by ``sqrt 5``.

As a ``Q``-algebra ``Q(sqrt 5) = Q[a]/(a^2 - 5)``.  Multiplication by ``sqrt 5`` is a
``Q``-linear endomorphism whose trace and determinant are the field trace ``0``
and norm ``-5`` (the trace and norm of an element are those of its multiplication
map, by definition).  A quadratic field is Galois, so it is its own normal
closure, with Galois group of order two.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_q_root_five_is_the_rational_algebra_q_a_mod_a_squared_minus_five() -> None:
    algebra = QuadraticField(5).as_algebra()
    a = algebra.algebra_generator("a")

    assert algebra in Algebras(QQ)
    assert a * a == 5 * algebra.one()
    assert a != algebra.zero()


def test_multiplication_by_root_five_has_the_field_trace_and_norm() -> None:
    root = QuadraticField(5).primitive_element()
    multiplication = root.multiplication_morphism()

    assert multiplication(root) == 5
    assert multiplication(QuadraticField(5).one()) == root
    assert multiplication.trace() == root.trace()
    assert multiplication.determinant() == root.norm()


def test_a_quadratic_field_is_its_own_normal_closure() -> None:
    field = QuadraticField(5)

    assert field.normal_closure().degree() == 2
    assert field.normal_closure_galois_group().order() == 2
