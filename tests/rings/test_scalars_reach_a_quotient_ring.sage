r"""The scalar tower reaches a quotient ring, one and two steps up.

A quotient ``A/I`` receives ``A`` along its retained quotient map, and with it
everything ``A`` receives canonically: the composite of two ring maps is a ring
map, and it is canonical because both factors are.  The quotient used to carry
its quotient map and *no* coercion at all, so

  * ``(Z/5)[t]/(t^2)`` could not be added to an integer;
  * comparing one of its elements with an owned scalar zero answered ``False``
    while comparing it with the host integer ``0`` answered ``True``;
  * and the assertion ``tbar**2 == 0`` failed, in a ``.sage`` file whose literal
    ``0`` is this library's ``ZZ(0)``, not a Python int.

Nothing about the arithmetic was wrong: the class of ``t^2`` is zero, and
``quotient.zero() == quotient(t*t)`` always said so.  What was missing was the
map from the tower.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_field_of_five_elements_receives_the_integers() -> None:
    r"""One step: ``ZZ -> ZZ/5`` is the quotient map, so ``ZZ/5`` receives ``ZZ``."""
    field = GF(5)

    assert field.has_coerce_map_from(ZZ) is True
    assert field(ZZ(3)) == field(3)
    assert field(ZZ(5)) == field.zero()


def test_a_two_step_quotient_receives_the_integers_and_its_own_source() -> None:
    r"""Two steps: ``ZZ -> (Z/5)[t] -> (Z/5)[t]/(t^2)``, both canonical."""
    field = GF(5)
    polynomial = field.polynomial_ring("t")
    quotient = polynomial.quotient_ring(polynomial.algebra_generator("t") ** 2)

    assert quotient.has_coerce_map_from(polynomial) is True
    assert quotient.has_coerce_map_from(field) is True
    assert quotient.has_coerce_map_from(ZZ) is True
    assert quotient.zero() == ZZ(0)
    # And nothing else arrives: a ring of characteristic 5 receives no map from
    # ``QQ``, so its zero is not the rational zero either.
    assert quotient.has_coerce_map_from(QQ) is False
    assert (quotient.zero() == QQ(0)) is False


def test_an_integer_adds_to_a_class_and_the_literal_zero_compares() -> None:
    r"""``t + 1`` in ``(Z/5)[t]/(t^2)``, and ``tbar**2 == 0`` as written.

    The second assertion is the one from
    ``test_quotient_residue_field_dual_numbers_and_adic_completion``, kept
    exactly as written there: in a ``.sage`` file its ``0`` is the owned
    ``ZZ(0)``, so it needs the tower map rather than an element comparison.
    """
    field = GF(5)
    polynomial = field.polynomial_ring("t")
    t = polynomial.algebra_generator("t")
    quotient = polynomial.quotient_ring(t ** 2)
    tbar = quotient.quotient_map()(t)

    assert tbar != 0
    assert tbar**2 == 0
    assert tbar + ZZ(1) == quotient.quotient_map()(t + 1)
    assert tbar + ZZ(1) != tbar
