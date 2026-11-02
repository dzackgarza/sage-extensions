r"""A quotient ring is a cyclic module over its cover, on a generating family.

``R[x]/I`` is an ``R[x]``-module through its quotient map, which is onto, so the
class of ``1`` *generates* it.  That class is a generating family, **not** a
basis: every element of the ideal multiplies it to zero, so the frame states a
surjection ``R[x]^1 ->> A`` whose relations are the ideal's chosen generators.
No freeness or projectivity follows from having one generator — ``ZZ/2`` is not
projective over ``ZZ`` — and the frame a native free algebra selects for itself is
its monomial basis, not this one.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.pure.modules import Modules

import pytest


def _dual_numbers_over_qq():
    polynomials = QQ["x"]
    return polynomials, polynomials.quotient_ring(polynomials.gen() ** 2)


def test_a_polynomial_quotient_is_cyclic_over_its_cover() -> None:
    r"""``QQ[x]/(x^2)`` is generated over ``QQ[x]`` by the class of ``1``.

    One generator is all a *generating* family needs; the class of the unit is
    it, and the frame is not asserted to be a basis.
    """
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


def test_one_generator_over_the_cover_does_not_make_the_quotient_projective() -> None:
    r"""``ZZ/2`` has the single generator ``1`` over ``ZZ`` and is not projective.

    The refusal is the library's own: the projective placement asks
    ``projectivity_decision()``, which answers false for the residue ring.  A
    finite generating family is therefore not read as a free or projective
    basis, which is what the frame above states and no more.
    """
    from sage_extensions.categories.modules.framed.framed_free_modules import (
        FramedFreeModules,
    )
    from sage_extensions.refine import refine

    residues = ZZ.quotient_ring(ZZ.ideal(2))
    assert residues.has_selected_module_resolution() is True
    assert residues.module_generating_set().cardinality() == 1
    with pytest.raises(ValueError):
        refine(residues, FramedFreeModules(ZZ).FinitelyGenerated())
