r"""A quotient ring is a cyclic module over its cover.

``R[x]/I`` is an ``R[x]``-module through its quotient map, which is onto, so the
class of ``1`` generates it: its canonical basis is ``{1}``.  That is the frame
``module_category()`` reports — ``Modules(R[x])`` — and the one
``module_generating_set()`` reads.  A native free algebra keeps the basis its own
module construction selects, which is not this one.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.pure.modules import Modules


def _dual_numbers_over_qq():
    polynomials = QQ["x"]
    return polynomials, polynomials.quotient_ring(polynomials.gen() ** 2)


def test_a_polynomial_quotient_is_cyclic_over_its_cover() -> None:
    r"""``QQ[x]/(x^2)`` is generated over ``QQ[x]`` by the class of ``1``."""
    polynomials, algebra = _dual_numbers_over_qq()

    assert algebra.module_category() == Modules(algebra.base_ring())
    assert algebra.has_selected_module_resolution() is True

    labels = algebra.module_generating_set()
    assert labels.cardinality() == 1
    assert algebra.module_generator(next(iter(labels))) == algebra.one()


def test_the_same_frame_is_stated_over_a_prime_field_and_over_the_integers() -> None:
    r"""``F_2[y]/(y^2)`` over ``F_2[y]`` and ``ZZ/6`` over ``ZZ``: one generator, the unit."""
    field_polynomials = GF(2)["y"]
    field_quotient = field_polynomials.quotient_ring(field_polynomials.gen() ** 2)
    assert field_quotient.has_selected_module_resolution() is True
    assert field_quotient.module_generating_set().cardinality() == 1
    assert (
        field_quotient.module_generator(
            next(iter(field_quotient.module_generating_set()))
        )
        == field_quotient.one()
    )

    residues = ZZ.quotient_ring(ZZ.ideal(6))
    assert residues.has_selected_module_resolution() is True
    assert residues.module_generating_set().cardinality() == 1
    assert (
        residues.module_generator(next(iter(residues.module_generating_set())))
        == residues.one()
    )


def test_a_native_free_algebra_keeps_the_basis_its_own_construction_selects() -> None:
    r"""A polynomial ring's frame is its monomial basis over the coefficient ring."""
    polynomials = QQ["x,y"]

    assert polynomials.has_selected_module_resolution() is True
    # Its chosen basis is over QQ, indexed by the monomials, not the single
    # class of the unit that a quotient states over its cover.
    assert polynomials.module_generating_set().cardinality().is_finite() is False
