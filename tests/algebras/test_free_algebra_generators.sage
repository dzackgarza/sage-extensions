r"""A free algebra or polynomial ring states its generators from its retained family.

``gen`` and ``gens`` read ``algebra_generating_set`` and ``algebra_generator`` —
the generator names the construction selected and the elements they raise to — so
a polynomial ring answers with its own indeterminate rather than with anything
borrowed from the underlying computer-algebra model.  The argument of ``gen`` is
a position in that ordered family, which is what ``R.gen(0)``, ``R.gen(1)`` mean
for a multivariate ring.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_a_polynomial_ring_states_its_indeterminate() -> None:
    polynomials = ZZ["x"]
    labels = tuple(polynomials.algebra_generating_set())

    assert len(labels) == 1
    assert polynomials.gen() == polynomials.algebra_generator(labels[0])
    assert polynomials.gen(0) == polynomials.gen()
    assert polynomials.gens() == (polynomials.gen(),)


def test_a_multivariate_ring_states_its_generators_in_order() -> None:
    polynomials = ZZ["x,y"]
    labels = tuple(polynomials.algebra_generating_set())

    assert len(labels) == 2
    assert polynomials.gen(0) == polynomials.algebra_generator(labels[0])
    assert polynomials.gen(1) == polynomials.algebra_generator(labels[1])
    assert polynomials.gens() == (polynomials.gen(0), polynomials.gen(1))
    assert polynomials.gen(0) != polynomials.gen(1)


def test_the_generator_is_the_construction_s_own_element() -> None:
    r"""Generating it twice gives the same element, and it generates the ring.

    A borrowed host generator would fail the first check for a non-Sage
    realization; an arbitrary element would fail the second.
    """
    polynomials = GF(5)["t"]
    generator = polynomials.gen()

    assert generator.parent() is polynomials
    assert polynomials.gen() == generator
    assert polynomials.gen() * polynomials.gen() == generator**2
    assert generator**2 != polynomials.zero()


def test_an_out_of_range_generator_is_refused() -> None:
    with pytest.raises(AssertionError):
        ZZ["x"].gen(1)
