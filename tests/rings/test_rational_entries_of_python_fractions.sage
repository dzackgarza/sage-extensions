r"""Rational entries of a nested Gram matrix may be Python fractions.

A ``Fraction`` names its own numerator and denominator, so the owned ``QQ``
element constructor reads those parts instead of handing the whole value to the
source of the ``ZZ``-localization that presents it.  ``latticedb``'s
``records.derive`` builds the rational model of a card with rational Gram
entries exactly this way: the card stores each entry as a bare ``Fraction``
(lattice-database#37, row 7, #347).
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_python_fraction_is_its_numerator_over_its_denominator() -> None:
    r"""``QQ(Fraction("2/3"))`` is ``QQ(2) / QQ(3)``, not a ``ZZ`` coercion."""
    assert QQ(Fraction("2/3")) == QQ(2) / QQ(3)


def test_a_nested_gram_of_python_fractions_constructs_the_lattice() -> None:
    r"""The A2-dual gram tensor of card ``0001``, scaled by thirds."""
    lattice = Lattices(QQ)(
        [
            [Fraction("2/3"), Fraction("1/3")],
            [Fraction("1/3"), Fraction("2/3")],
        ]
    )

    assert lattice.module_rank() == cardinal(2)
    assert lattice.determinant() == QQ(1) / QQ(3)
