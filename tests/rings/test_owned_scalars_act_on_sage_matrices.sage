r"""An owned scalar acts on a Sage matrix, and the coercion cases around it.

Every integer literal in a session belongs to this library's integers, not to
Sage's, so ``2 * M`` for a Sage matrix ``M`` used to fail with ``unsupported
operand parent(s)`` while ``M * 2`` and ``2 * M[0, 0]`` worked.  Sage's coercion
model asks the *actor's* parent for an action, and a Sage ``MatrixSpace`` has
none from an owned ring; the owned ring now states it, scaling the matrix in the
matrix's own base ring.  This is the same shape as the power action the monoid
owner states for owned exponents, and it changes no caller's scalar type.

Two things are pinned besides the scaling itself.  The action is offered only
when the matrix's base ring can read the scalar — an owned base by coercion, a
Sage base when it coerces from the owned ring's engine realization — so a matrix
whose base cannot read it declines instead of receiving a guessed action.  And
the zero-argument ``matrix_space()``, which Sage's ``MatrixSpace`` coercion
probes for on any parent, answers the ``1 x 1`` space over the ring: Sage then
declines through its own test, and no coercion between a ring and a Sage matrix
space is created.
"""

import operator

from sage_extensions.all import *  # noqa: F401,F403

from sage.matrix.constructor import matrix as sage_matrix
from sage.matrix.matrix_space import MatrixSpace
from sage.rings.finite_rings.finite_field_constructor import GF as sage_GF
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ

import pytest


def _integer_matrix():
    return sage_matrix(SageZZ, [[1, 2], [3, 4]])


def test_an_owned_scalar_scales_a_sage_matrix_on_either_side() -> None:
    r"""``2 * M`` and ``M * 2`` are the entrywise product, in ``M``'s own space."""
    matrix_ = _integer_matrix()
    expected = sage_matrix(SageZZ, [[2, 4], [6, 8]])

    assert 2 * matrix_ == expected
    assert matrix_ * 2 == expected
    assert (2 * matrix_).parent() is matrix_.parent()
    assert (matrix_ * 2).parent() is matrix_.parent()
    assert -matrix_ == sage_matrix(SageZZ, [[-1, -2], [-3, -4]])
    assert matrix_ + matrix_ == expected


def test_the_scaling_is_the_matrix_base_rings_arithmetic() -> None:
    r"""Over ``QQ`` a half multiplies as a half; over ``GF(2)`` an even integer is zero."""
    rational = sage_matrix(SageQQ, [[int(1), int(2)]])
    # The expected matrix is built by Sage's own scalar multiplication: the
    # literals inside a Sage constructor are this library's integers, and those
    # do not coerce into a Sage ring (a separate contract from the action).
    expected = rational * (SageQQ(int(1)) / SageQQ(int(2)))
    assert (QQ(1) / QQ(2)) * rational == expected

    mod_two = sage_matrix(sage_GF(2), [[int(1), int(0)], [int(0), int(1)]])
    zero = sage_matrix(sage_GF(2), [[int(0), int(0)], [int(0), int(0)]])
    assert 2 * mod_two == zero
    assert mod_two * 2 == zero


def test_the_zero_argument_matrix_space_is_the_one_by_one_space_over_the_ring() -> None:
    r"""The probe Sage's matrix coercion makes answers with a matrix space of this ring."""
    one_by_one = ZZ.matrix_space()
    assert one_by_one.base_ring() is ZZ
    assert one_by_one.module_generating_set().cardinality() == 1

    three_by_two = ZZ.matrix_space(3, 2)
    assert three_by_two.base_ring() is ZZ
    assert three_by_two.module_generating_set().cardinality() == 6


def test_no_coercion_and_no_action_is_invented_by_the_probe() -> None:
    r"""The probe declines, and only multiplication is answered."""
    space = MatrixSpace(SageZZ, 2, 2)

    assert space.has_coerce_map_from(SageZZ) is True
    assert space.has_coerce_map_from(ZZ) is False
    assert ZZ.get_action(space, operator.add, True) is None
    assert ZZ.get_action(space, operator.sub, True) is None


def test_a_matrix_base_that_cannot_read_the_scalar_declines() -> None:
    r"""``GF(2)`` reads integers but not ``1/2``: the product refuses instead of guessing."""
    mod_two = sage_matrix(sage_GF(2), [[int(1), int(0)], [int(0), int(1)]])

    with pytest.raises(TypeError):
        (QQ(1) / QQ(2)) * mod_two


def test_an_owned_matrix_still_scales_by_an_owned_scalar() -> None:
    r"""The library's own matrix space keeps its scalar action unchanged."""
    space = ZZ.matrix_space(2, 2)
    element = space.an_element()

    assert 3 * element == element + element + element


def test_the_route_from_an_owned_scalar_into_a_sage_ring_is_the_engine_adapter() -> None:
    r"""``SageZZ(x)`` reads the integer protocol; ``SageQQ(x)`` is not a coercion here.

    Sage's ``Integer`` reads ``x._integer_``, which this library's integers
    implement, so an owned integer converts into Sage's ``ZZ``.  Sage's ``QQ``
    reads no such protocol: ``SageQQ(x)`` would need a coercion from the owned
    ring into ``QQ``, and none is installed — silently coercing library scalars
    into ``QQ`` is exactly what this library does not do.  The supported route is
    the engine realization, which is what the matrix action uses internally.
    """
    three = ZZ(3)

    assert SageZZ(three) == int(3)
    assert three.parent()._engine_element(three) == int(3)
    with pytest.raises(ValueError):
        SageQQ(three)
