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


def test_a_foreign_host_object_is_refused_rather_than_admitted() -> None:
    r"""The comparison normalizes the exact operands the contract names and no
    others: a host object that is not an exact number is simply not equal.

    With the operands read through the retained completion map, everything the
    public ingress can build now carries its source expression, so an
    undecidable comparison is no longer reachable from here; what must not
    happen instead is a host object being converted and answered about.
    """
    ring = Zp(5)
    assert (ring.one() == "x") is False
    assert (ring.one() == [1]) is False


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


def test_an_ordinary_quotient_ring_keeps_its_own_unit_map() -> None:
    r"""The completion's structure map belongs to the completion's owner.

    It was briefly installed on ``QuotientRings.ParentMethods``, where it asked
    every ordinary quotient for a completion source; this pins the quotient's
    own contract and the completion's override separately.
    """
    four = ZZ.one() + ZZ.one() + ZZ.one() + ZZ.one()
    quotient = ZZ.quotient_ring(ZZ.ideal(four))
    unit = quotient.unit_morphism()
    assert unit.domain() is ZZ
    assert unit.codomain() is quotient
    assert unit(ZZ.one()) == quotient.one()


def test_the_completion_structure_map_is_its_completion_map() -> None:
    ring = Zp(5)
    unit = ring.unit_morphism()
    assert unit.domain() is ZZ
    assert unit.codomain() is ring
    two = unit(ZZ.one() + ZZ.one())
    assert two == ring.one() + ring.one()
    assert two.exact_source_expression() == ZZ.one() + ZZ.one()


def test_a_completion_of_a_polynomial_ring_is_not_reinterpreted_as_integers() -> None:
    r"""A completion whose source is not ``ZZ`` keeps its own source expressions.

    The exact integer and rational literals still cross -- they are exact
    numbers of any such source -- but an element of a rational function field is
    not read as a fraction of integers.
    """
    polynomial = ZZ["x"]
    completion = polynomial.adic_completion(polynomial.ideal(polynomial.gen()))
    assert completion.completion_source() is polynomial
    assert completion.one() == 1
    assert completion.one() != completion.zero()


def test_the_prime_of_zp_must_be_an_exact_integer() -> None:
    r"""``5.9`` is not the prime ``5``, and neither is ``11/2``."""
    assert Zp(QQ(5) / QQ(1)) == Zp(5)
    for not_a_prime in (5.9, QQ(11) / QQ(2)):
        try:
            Zp(not_a_prime)
        except TypeError:
            pass
        else:
            assert False, f"Zp accepted {not_a_prime!r} as a prime"
