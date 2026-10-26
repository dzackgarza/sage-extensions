r"""Classifiers of bilinear and quadratic forms on ``Z/4``."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def cyclic(order):
    r"""``Z/order`` as ``Z / order Z``, with the class of ``1``."""
    line = Modules(ZZ)(ZZ**1)
    (e,) = line.basis()
    quotient = line / line.span((order * e,))
    return quotient, quotient.projection()(e)


def test_divided_square_of_Z_mod_4_is_cyclic_of_order_8() -> None:
    r"""``Gamma^2(Z/4) = Z/8`` on ``gamma(g)``, with ``gamma(2g) = 4 gamma(g)``.

    ``gamma(n g) = n^2 gamma(g)`` and ``gamma(4g) = 0`` give ``16 gamma(g) = 0``,
    while ``gamma(g + g) = 2 gamma(g) + g.g`` and ``4 (g.g) = 0`` cut this to
    order 8: ``Gamma^2(Z) = Z gamma(1)`` modulo ``gamma(4) = 16 gamma(1)`` and
    ``4 . 1 = 8 gamma(1)`` is ``Z/8``.
    """
    module, g = cyclic(4)
    square = module.divided_square()
    universal = square.quadratic(g)

    assert square.cardinality() == 8
    assert universal.additive_order() == 8
    assert square.quadratic(2 * g) == 4 * universal
    assert square.quadratic(3 * g) == 9 * universal


def test_tensor_square_of_Z_mod_4_is_Z_mod_4() -> None:
    r"""``Z/4 (x) Z/4 = Z/4`` on ``g (x) g``."""
    module, g = cyclic(4)
    square = module.tensor_product(module)

    assert square.cardinality() == 4
    assert square.pure_tensor(g, g).additive_order() == 4


@pytest.mark.parametrize(
    "adjunction_name, classifier_order, quotient_classifier_order",
    [("bilinear_free_form_adjunction", 4, 2), ("quadratic_free_form_adjunction", 8, 4)],
)
def test_free_form_adjunctions_on_Z_mod_4_satisfy_the_triangle_identities(
    adjunction_name, classifier_order, quotient_classifier_order
) -> None:
    r"""The free bilinear (quadratic) form on ``Z/4`` takes values in ``Z/4`` (``Z/8``); both triangle identities hold."""
    module, g = cyclic(4)
    quotient, h = cyclic(2)
    adjunction = {
        "bilinear_free_form_adjunction": Modules(ZZ).bilinear_free_form_adjunction(),
        "quadratic_free_form_adjunction": Modules(ZZ).quadratic_free_form_adjunction(),
    }[adjunction_name]
    free = adjunction.left_adjoint()
    underlying = adjunction.right_adjoint()
    free_module = free(module)
    projection = module.Mor(quotient)({g: h})

    assert free_module.value_module().cardinality() == classifier_order
    assert free(quotient).value_module().cardinality() == quotient_classifier_order
    assert adjunction.counit(free_module) * free(adjunction.unit(module)) == free_module.Mor(free_module).identity()
    assert underlying(adjunction.counit(free_module)) * adjunction.unit(underlying(free_module)) == (
        underlying(free_module).Mor(underlying(free_module)).identity()
    )
    assert adjunction.unit(quotient) * projection == underlying(free(projection)) * adjunction.unit(module)
