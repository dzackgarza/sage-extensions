r"""The real sequence spaces ``ell^p``: conjugates, forms, membership, and a geometric norm.

``ell^p`` is the space of ``a: NN -> RR`` with ``sum |a_n|^p < oo`` (bounded for
``p = oo``); ``ell^p x ell^q -> RR`` is Hölder's pairing exactly when
``1/p + 1/q = 1``, and ``<a, c> = sum a_n c_n`` makes ``ell^2`` a formed module.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_holder_conjugates_of_sequence_spaces() -> None:
    r"""``ell^3`` pairs with ``ell^{3/2}``, ``ell^1`` with ``ell^oo``; ``ell^2`` is self-conjugate."""
    assert ell(3, NN, RR).conjugate_sequence_space() is ell(QQ(3) / 2, NN, RR)
    assert ell(1, NN, RR).conjugate_sequence_space() is ell(oo, NN, RR)
    assert ell(oo, NN, RR).conjugate_sequence_space() is ell(1, NN, RR)
    assert ell(2, NN, RR).conjugate_sequence_space() is ell(2, NN, RR)
    assert ell(2, NN, RR).pairing_module() is ell(2, NN, RR)
    assert ell(4, NN, RR).integrability_exponent() == 4


def test_the_notation_ell_p_names_one_space_per_exponent() -> None:
    r"""``ell^2 (x) ell^2`` is ``ell^2`` with its form."""
    assert ell(2, NN, RR) * ell(2, NN, RR) is ell(2, NN, RR)


def test_only_ell2_is_a_formed_module() -> None:
    r"""``sum a_n c_n`` converges on ``ell^2 x ell^2`` only; every ``ell^p`` is a real vector space."""
    assert ell(2, NN, RR) in FormModules(RR)
    assert ell(1, NN, RR) not in FormModules(RR)
    assert ell(oo, NN, RR) not in FormModules(RR)
    assert ell(3, NN, RR) in VectorSpaces(RR)


def test_exponents_off_the_holder_line_give_no_pairing() -> None:
    r"""``1/1 + 1/2 != 1``: ``ell^1 x ell^2`` is not a Hölder pairing."""
    with pytest.raises(TypeError):
        ell(1, NN, RR) * ell(2, NN, RR)


def test_exponent_zero_defines_no_sequence_space() -> None:
    r"""``ell^p`` is defined for ``p > 0``."""
    with pytest.raises(ValueError):
        ell(0, NN, RR)


def test_the_ell1_and_ell_infinity_pairing_is_a_paired_module() -> None:
    r"""``ell^1 x ell^oo -> RR``, ``(a, c) -> sum a_n c_n``, is Hölder's pairing at ``(1, oo)``."""
    assert ell(1, NN, RR) * ell(oo, NN, RR) in PairedModules(RR)


def test_a_geometric_sequence_takes_its_values() -> None:
    r"""``a_n = e^{-n}`` has ``a_2 = e^{-2}``."""
    f1(n) = exp(-n)

    assert ell(2, NN, RR)(f1)(2) == exp(-2)


def test_the_squared_ell2_norm_of_a_geometric_sequence() -> None:
    r"""``sum_{n >= 0} e^{-2n} = 1 / (1 - e^{-2})``."""
    f1(n) = exp(-n)
    geometric = ell(2, NN, RR)(f1)

    assert ell(2, NN, RR).b(geometric, geometric) == 1 / (1 - exp(-2))


def test_the_sine_sequence_is_not_square_summable() -> None:
    r"""``sin(n)^2 + sin(n+1)^2 >= sin(1)^2 / 2 > 0`` for every ``n``, so ``sum sin(n)^2 = oo``."""
    f1(n) = sin(n)

    assert f1 not in ell(2, NN, RR)


def test_the_identity_sequence_is_not_summable() -> None:
    r"""``sum n`` diverges: ``a_n = n`` is not in ``ell^1``."""
    f1(n) = n

    assert f1 not in ell(1, NN, RR)
