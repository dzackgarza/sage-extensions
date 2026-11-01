r"""``Modules(R).direct_sum_of_cyclics`` is the torsion owner's construction.

A direct sum of cyclic modules ``⨁ᵢ R/(aᵢ)`` is a finitely presented torsion
module, and its diagonal presentation is stated once — by
``Modules(R).FinitelyPresented().Torsion()``.  A caller that names a module by
its *orders* asks ``Modules(R).direct_sum_of_cyclics(orders)``, which is the same
construction and not a second one: it delegates, and the two spellings reach one
object.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _torsion_spelling(ring, orders):
    return Modules(ring).FinitelyPresented().Torsion().direct_sum_of_cyclics(orders)


def test_the_two_spellings_reach_equal_modules() -> None:
    r"""``Modules(ZZ).direct_sum_of_cyclics((6,))`` equals the torsion owner's module.

    Equal, not identical: that construction is not interned, so two calls build
    two equal modules.  What the accessor must not do is build a *different*
    module or restate the presentation, and equality plus the invariant factors
    is what states that.
    """
    accessor = Modules(ZZ).direct_sum_of_cyclics((6,))

    assert accessor == _torsion_spelling(ZZ, (6,))
    assert accessor.invariant_factors() == _torsion_spelling(ZZ, (6,)).invariant_factors()


def test_the_orders_are_the_invariant_factors() -> None:
    r"""``R/(2) + R/(3) = R/(6)``: the diagonal presentation's invariant factors."""
    assert Modules(ZZ).direct_sum_of_cyclics((2, 3)).invariant_factors() == _torsion_spelling(
        ZZ, (2, 3)
    ).invariant_factors()
    assert Modules(ZZ).direct_sum_of_cyclics((6,)).invariant_factors() == _torsion_spelling(
        ZZ, (6,)
    ).invariant_factors()


def test_units_contribute_nothing_and_no_order_gives_the_zero_module() -> None:
    r"""``R/(1) = 0`` so a unit order is dropped; no orders at all is the zero module."""
    assert (
        Modules(ZZ).direct_sum_of_cyclics((1, 6)).invariant_factors()
        == _torsion_spelling(ZZ, (6,)).invariant_factors()
    )
    assert Modules(ZZ).direct_sum_of_cyclics(()).module_rank() == 0


def test_a_zero_order_is_refused_by_the_owner() -> None:
    r"""``R/(0) = R`` is free, not torsion: the construction refuses it, and so does the accessor."""
    with pytest.raises(ValueError):
        _torsion_spelling(ZZ, (0,))

    with pytest.raises(ValueError):
        Modules(ZZ).direct_sum_of_cyclics((0,))
