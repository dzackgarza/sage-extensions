r"""Archive reconciliation for the former monolithic algebra-syntax session.

The archived test mixed four mathematical owners in one notebook surface:
free/presented algebras, ring/algebra structure maps, fractional ideals, and
number-field arithmetic.  Those constructions now live at their dedicated
owners; these specimens retain the cross-owner user syntax without restoring a
second algebra object system.
"""

from sage_extensions.all import *

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/tests/test_preamble_algebra_syntax.sage",
    "live_owner": "tests/algebras/test_preamble_algebra_syntax_archive.py",
    "disposition": "reconciled-live-owner",
}






def test_fractional_ideal_membership_uses_the_module_span_not_the_input_tuple() -> None:
    ideal = ZZ.fractional_ideal(ZZ(2), ZZ(3))
    half = ZZ.fractional_ideal(QQ(1) / 2)

    assert ZZ(1) in ideal
    assert QQ(1) / 2 not in ideal
    assert half.module_generating_set().cardinality() == 1
    assert half.module_generator(next(iter(half.module_generating_set()))) == QQ(1) / 2


def test_univariate_algorithms_and_number_field_arithmetic_return_owned_values() -> None:
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    cubic = (x - 1) * (x - 2) * (x - 3)
    quotient, remainder = cubic.quo_rem((x - 1) * (x - 2))
    field = QuadraticField(5, "a")
    primitive = field.primitive_element()

    assert quotient.parent() is polynomials
    assert remainder == polynomials.zero()
    assert cubic.factor().reconstruct() == cubic
    assert field.degree() == 2
    assert primitive.norm() == QQ(-5)
    assert primitive.trace() == QQ.zero()
    assert field.ring_of_integers().integral_basis().cardinality() == 2
