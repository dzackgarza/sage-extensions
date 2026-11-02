r"""Descent of a quadratic form to a finite quotient, and the value module it forces.

A quadratic map ``q`` on the cover of ``M = coker(r)`` defines a form on ``M``
exactly when it is constant on classes: for every relation ``r`` and every
generator ``x``, ``q(r) = 0`` and the polar value ``q(x + r) - q(x) - q(r)``
vanishes.  The library states that law (``_quadratic_descends``) and
``from_module`` now enforces it, because a form that fails it is not a function
on its own module: ``x == y`` would hold while ``q(x) != q(y)``.

The law also decides which value module is honest for a given torsion module.
On ``(Z/3)^2`` with ``q = diag(1/3, 1/3)`` the relation ``3 e_0 = 0`` forces
``q(3 e_0) = 9 q(e_0) = 3 = 1 mod 2`` in ``Q/2Z``, so no ``Q/2Z``-valued form
with those values descends; in ``Q/Z`` the same relation reads ``3 = 0`` and the
form is well defined.  On ``2``-torsion, ``q(2 e_0) = 4 q(e_0) = 0 mod 2``, so
``Q/2Z`` — the even-lattice case — descends.  The bilinear counterpart is a
different law: ``b`` descends on ``(Z/3)^2`` in ``Q/Z`` while ``q`` does not
descend in ``Q/2Z``, which is what makes the quadratic law an extra condition.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.framed.formed import (
    TorsionBilinearFormModules,
    TorsionQuadraticFormModules,
)
from sage_extensions.categories.modules.framed.fraction_field_quotients import (
    FractionFieldQuotients,
)

import pytest


def _quadratic(relation_rows, gram, modulus):
    values = FractionFieldQuotients(ZZ)(modulus)
    return TorsionQuadraticFormModules(ZZ).from_relations_and_gram(
        relation_rows, gram, values
    )


def _quotients_of_the_three_torsion():
    r"""``(Z/3)^2`` with ``q = diag(1/3, 1/3)`` as a Gram matrix over ``QQ``."""
    third = QQ(1) / QQ(3)
    return [[3, 0], [0, 3]], [[third, 0], [0, third]]


def _descent_violations(form, order):
    r"""Return the pairs of *equal* elements whose ``q`` values differ."""
    first, second = form.module_generators()
    violations = []
    for left in range(order):
        for right in range(order):
            element = left * first + right * second
            for shift in range(1, order):
                shifted = element + shift * order * first
                if (element == shifted) is not True:
                    continue
                if (form.q(element) == form.q(shifted)) is not True:
                    violations.append((element, shifted))
    return tuple(violations)


def test_a_quadratic_form_that_does_not_descend_is_refused() -> None:
    r"""``q`` valued in ``Q/2Z`` on ``(Z/3)^2`` is not a function on the classes."""
    relations, gram = _quotients_of_the_three_torsion()

    with pytest.raises(ValueError, match="does not define a quadratic form"):
        _quadratic(relations, gram, 2)


def test_the_value_module_that_descends_makes_q_a_function_of_the_class() -> None:
    r"""The same Gram over ``Q/Z`` descends: ``4/3`` and ``1/3`` are one point there."""
    relations, gram = _quotients_of_the_three_torsion()
    form = _quadratic(relations, gram, 1)
    values = form.value_module()

    assert _descent_violations(form, 3) == ()
    assert values(QQ(4) / QQ(3)) == values(QQ(1) / QQ(3))
    assert all(form.q(generator) == values(QQ(1) / QQ(3)) for generator in form.module_generators())


def test_two_torsion_keeps_its_quadratic_values() -> None:
    r"""On ``(Z/2)^2`` the refinement survives: ``q(x) = 1/2`` is well defined."""
    half = QQ(1) / QQ(2)
    form = _quadratic([[2, 0], [0, 2]], [[half, 0], [0, half]], 2)
    values = form.value_module()

    assert _descent_violations(form, 2) == ()
    assert all(form.q(generator) == values(half) for generator in form.module_generators())


def test_the_bilinear_law_is_a_different_condition_on_the_same_module() -> None:
    r"""``b`` descends on ``(Z/3)^2`` over ``Q/Z`` while ``q`` needs its own law."""
    relations, gram = _quotients_of_the_three_torsion()
    values = FractionFieldQuotients(ZZ)(1)
    bilinear = TorsionBilinearFormModules(ZZ).from_relations_and_gram(
        relations, gram, values
    )
    first, second = bilinear.module_generators()

    assert bilinear.b(first, first) == values(QQ(1) / QQ(3))
    assert bilinear.b(first + 3 * first, second) == bilinear.b(first, second)
