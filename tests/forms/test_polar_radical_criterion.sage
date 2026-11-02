r"""When a torsion form's polar form is nondegenerate, decided from retained data.

The decision procedure of a typed torsion form goes through Sage's finite
quadratic module, which represents only *non-degenerate* polar forms: its module
is the cokernel of the Gram matrix.  Whether that applies is not a question about
the rational rank of a Gram matrix.  On ``Z/4`` with ``b(x, x) = x^2/2`` the
Gram matrix ``(1/2)`` is invertible, and yet ``2`` pairs to zero with every
generator: the radical is ``{0, 2}``.  What decides it is the retained finite
presentation together with the value group: writing ``M = Z^n/D`` in the
invariant-factor framing, clearing the Gram's denominators as ``H/N``, and letting
``m`` be the modulus of the polar form's values, the radical is the kernel of
``x |-> H^T x`` from ``(Z/D)^n`` to ``(Z/Nm)^n``, so it is trivial exactly when
``D_i * gcd(s_i, Nm) == Nm`` for every Smith invariant ``s_i`` of ``H^T``.

A form with a radical is still a form — the descent law is a separate condition
and is enforced at construction — but the engine's normal form does not apply to
it, and the shared API says so instead of answering ``False`` or raising a
cardinality error.  The verdict must not depend on which Gram representative or
generator frame states the same form, which is what these tests pin.
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

HALF = QQ(1) / QQ(2)


def _quadratic(relations, gram):
    return TorsionQuadraticFormModules(ZZ).from_relations_and_gram(
        relations, gram, FractionFieldQuotients(ZZ)(2)
    )


def _bilinear(relations, gram):
    return TorsionBilinearFormModules(ZZ).from_relations_and_gram(
        relations, gram, FractionFieldQuotients(ZZ)(1)
    )


def _polar_radical(form, elements):
    r"""Return the elements pairing to zero with every generator."""
    generators = tuple(form.module_generators())
    zero = form.b(generators[0], generators[0]) * 0
    return tuple(
        element
        for element in elements
        if all((form.b(element, generator) == zero) is True for generator in generators)
    )


def test_an_invertible_gram_can_have_a_nonzero_polar_radical() -> None:
    r"""``Z/4`` with ``q(x) = x^2/2``: Gram ``(1/2)``, radical ``{0, 2}``."""
    form = _quadratic([[4]], [[HALF]])
    generator = form.module_generators()[0]

    assert form.q(2 * generator) == form.value_module()(QQ(2) * QQ(2) / QQ(2))
    radical = _polar_radical(form, tuple(multiple * generator for multiple in range(4)))
    assert len(radical) == 2
    assert 2 * generator in radical

    # ``q`` vanishes on the radical here and is additive there: restricting to the
    # radical loses nothing, but that is a fact to check, not to assume.
    assert all(form.q(element) == form.value_module().zero() for element in radical)
    assert all(
        (form.q(left + right) == (form.q(left) + form.q(right))) is True
        for left in radical
        for right in radical
    )

    with pytest.raises(TypeError, match="non-degenerate polar forms"):
        form.is_isomorphic(form)


def test_a_two_torsion_form_with_the_same_gram_is_nondegenerate() -> None:
    r"""``Z/2`` with ``q(x) = x^2/2``: the same Gram, a trivial radical, a decision."""
    first = _quadratic([[2]], [[HALF]])
    second = _quadratic([[2]], [[HALF]])

    generator = first.module_generators()[0]
    elements = tuple(multiple * generator for multiple in range(2))
    assert first is not second
    assert _polar_radical(first, elements) == (first.zero(),)
    assert first.is_isomorphic(second) is True


def test_the_verdict_is_invariant_under_an_equivalent_representative() -> None:
    r"""Adding a multiple of the relation to the Gram states the same form and the same verdict."""
    plain = _quadratic([[4]], [[HALF]])
    shifted = _quadratic([[4]], [[HALF + QQ(2)]])  # 2 = 4 * (1/2): unchanged modulo 2

    generator = plain.module_generators()[0]
    other = shifted.module_generators()[0]
    assert plain.q(generator) == shifted.q(other)
    assert plain.b(generator, generator) == shifted.b(other, other)
    with pytest.raises(TypeError, match="non-degenerate polar forms"):
        shifted.is_isomorphic(plain)


def test_the_verdict_is_invariant_under_a_generator_change() -> None:
    r"""The unit ``3`` of ``Z/4`` rescales the Gram by ``9`` and changes nothing else."""
    plain = _quadratic([[4]], [[HALF]])
    rescaled = _quadratic([[4]], [[QQ(9) / QQ(2)]])

    generator = plain.module_generators()[0]
    other = rescaled.module_generators()[0]
    assert rescaled.q(other) == plain.q(generator)
    with pytest.raises(TypeError, match="non-degenerate polar forms"):
        rescaled.is_isomorphic(plain)


def test_the_bilinear_flavour_separates_the_two_torsion_orders() -> None:
    r"""``b`` on ``Z/4`` has radical ``{0, 2}``; on ``Z/2`` it does not."""
    with pytest.raises(TypeError, match="non-degenerate polar forms"):
        _bilinear([[4]], [[HALF]]).is_isomorphic(_bilinear([[4]], [[HALF]]))
    assert _bilinear([[2]], [[HALF]]).is_isomorphic(_bilinear([[2]], [[HALF]])) is True


def test_a_mixed_order_perfect_pairing_is_accepted() -> None:
    r"""``Z/2 + Z/4`` with the diagonal pairing ``1/2, 1/4`` is perfect.

    Clearing denominators gives ``H = diag(2, 1)`` with ``N = 4`` and Smith
    invariants ``(1, 2)``, while the module's invariants are ``(2, 4)``.  The
    Smith order is not the invariant order — a Smith transformation mixes
    coordinates — so a criterion that pairs ``D_i`` with ``s_i`` position by
    position rejects this perfect form.  The order of the radical is
    ``prod_i D_i * gcd(s_i, N) / N^n = 8 * 2 / 16 = 1``.
    """
    first = _bilinear([[2, 0], [0, 4]], [[QQ(1) / QQ(2), 0], [0, QQ(1) / QQ(4)]])
    second = _bilinear([[2, 0], [0, 4]], [[QQ(1) / QQ(2), 0], [0, QQ(1) / QQ(4)]])

    generators = tuple(first.module_generators())
    assert len(_polar_radical(first, tuple(first.elements()))) == 1
    assert first is not second
    assert first.is_isomorphic(second) is True


def test_the_mixed_order_verdict_survives_a_generator_permutation() -> None:
    r"""The same pairing with the two generators exchanged."""
    permuted = _bilinear([[4, 0], [0, 2]], [[QQ(1) / QQ(4), 0], [0, QQ(1) / QQ(2)]])

    assert len(_polar_radical(permuted, tuple(permuted.elements()))) == 1
    assert permuted.is_isomorphic(permuted) is True


def test_the_mixed_order_verdict_survives_a_unit_rescaling() -> None:
    r"""``3`` is a unit of ``Z/4`` with ``9 = 1`` modulo ``4``: the same form."""
    rescaled = _bilinear([[2, 0], [0, 4]], [[QQ(1) / QQ(2), 0], [0, QQ(9) / QQ(4)]])

    assert len(_polar_radical(rescaled, tuple(rescaled.elements()))) == 1
    assert rescaled.is_isomorphic(rescaled) is True


def test_a_mixed_order_form_with_a_vanishing_block_is_still_refused() -> None:
    r"""``diag(1/2, 0)`` on ``Z/2 + Z/4``: the whole ``Z/4`` is radical."""
    degenerate = _bilinear([[2, 0], [0, 4]], [[QQ(1) / QQ(2), 0], [0, 0]])

    radical = _polar_radical(degenerate, tuple(degenerate.elements()))
    assert len(radical) == 4
    with pytest.raises(TypeError, match="non-degenerate polar forms"):
        degenerate.is_isomorphic(degenerate)
