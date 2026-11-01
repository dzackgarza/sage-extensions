r"""The five-adic integers, and the lattice over them from research issue 614.

The original specimen is cell 23 of ``preamble-lattices.ipynb``::

    R = Zp(5)
    I2p.<ep, fp> = Lattices(R)(R^2)
    assert ep * ep == 1
    assert ep * fp == 0
    assert fp * fp == 1

It used to raise ``RecursionError`` inside the completion's own construction,
and once that was repaired the acceptance still gave ``False`` instead of
``True``.  Both were owner defects:

* the categorical ``Algebras._mul_`` shadowed the completion's primitive
  product, so an element coercion rebuilt the product through the module the
  algebra is stated on and asked for the base ring, re-entering itself.  It is a
  realization hook now, and the realization's product answers;
* ``_completion_equal`` coerced its operand with ``parent(other)`` and turned a
  refusal -- the session boundary refusing a raw host integer -- into ``False``.
  It now normalizes the operands the public contract names through the retained
  completion map, and answers the undecided proposition when the comparison
  cannot be decided;
* the identity form's entries and the completion's unit carry their exact
  source datum, so ``ep * ep == 1`` is *decided* rather than merely consistent
  with the working precision.
"""

from sage.all import latex

from sage_extensions.all import Lattices, QQ, Zp, ZZ
from sage_extensions.logic import Predicate


def test_the_five_adic_integers_construct() -> None:
    ring = Zp(5)
    assert ring.one() == ZZ.one()
    assert ring.one().exact_source_expression() == ZZ.one()
    assert ring.zero().exact_source_expression() == ZZ.zero()


def test_exact_operands_are_read_through_the_completion_map_in_both_orders() -> None:
    ring = Zp(5)
    one = ring.one()
    # owned integer, raw session integer, both orders
    assert one == ZZ.one()
    assert ZZ.one() == one
    assert one == 1
    two = ring.one() + ring.one()
    assert two != 3 and 3 != two
    # exact rationals: a unit denominator names an element, 1/2 here
    assert (one * two) == QQ(2) / QQ(1)
    assert two == QQ(2) / QQ(1)
    assert one != QQ(1) / QQ(2)
    # a non-unit denominator names no integer of the completion
    assert one != QQ(1) / QQ(5)


def test_an_undecidable_comparison_is_the_proposition_not_a_negative() -> None:
    r"""A raw host integer enters without exact provenance, so equality with an
    exactly known element cannot be decided; it must not answer ``False``."""
    ring = Zp(5)
    unknown = ring(ZZ.one())
    decision = unknown == ring.one()
    assert isinstance(decision, Predicate)


def test_the_original_lattice_constructs_computes_and_displays() -> None:
    ring = Zp(5)
    lattice = Lattices(ring)(ring**2)
    ep, fp = tuple(lattice.module_generators())

    assert ep * ep == 1
    assert ep * fp == 0
    assert fp * fp == 1

    text = repr(lattice)
    assert "rank 2" in text
    rendered = str(latex(lattice))
    assert "rk}(L) = 2" in rendered
    assert "disc}(L)" in rendered
