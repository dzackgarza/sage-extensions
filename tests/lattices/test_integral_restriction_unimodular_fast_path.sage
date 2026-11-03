r"""The unimodular reading of ``integral_restriction`` is the maintained answer, faster.

Over the integers a square integral matrix has an integral two-sided inverse
exactly when its determinant is ``+-1``; that inverse is the coordinate matrix
of the second rational preimage the general route pays for.  On finite equal
ranks ``integral_restriction(now)`` reads the forward factor alone: a unit
determinant is a lattice isomorphism by integer matrix inversion, and a
non-unit determinant is ``None`` without further work.  These tests pin that
the answers are the maintained ones (isometries returned equal pointwise;
non-integral maps refused), on specimens where both fire realistically.
"""

from sage_extensions.all import *


def test_the_swap_and_its_negate_are_returned_with_their_maintained_actions() -> None:
    r"""Unit-determinant forwards come back as the same isometries as before ($U$)."""
    L = Lattices(ZZ)([[0, 1], [1, 0]])
    V = L.vector_space()
    labels = tuple(V.module_generating_set())
    first, second = labels
    e1, e2 = V.module_generator(first), V.module_generator(second)
    swap_V = V.Isom(V)({first: e2, second: e1})
    neg_swap_V = V.Isom(V)({first: V.scalar_multiple(QQ(-1), e2), second: V.scalar_multiple(QQ(-1), e1)})

    swap_L = L.integral_isometry(swap_V)
    neg_swap_L = L.integral_isometry(neg_swap_V)
    integral_first, integral_second = tuple(L.module_generating_set())
    b1, b2 = L.module_generator(integral_first), L.module_generator(integral_second)
    assert swap_L(b1) == b2 and swap_L(b2) == b1
    assert neg_swap_L(b1) == -b2 and neg_swap_L(b2) == -b1
    # the restricted maps are genuine isometries of the lattice
    for x in (b1, b2):
        assert L.b(swap_L(x), swap_L(x)) == L.b(x, x)
    assert L.b(swap_L(b1), swap_L(b2)) == L.b(b1, b2)
    # direct construction of the same isometry agrees pointwise
    swap_direct = L.O()({b1: b2, b2: b1})
    for x in (b1, b2):
        assert swap_L(x) == swap_direct(x)


def test_a_higher_rank_isometry_is_returned_on_the_fast_route() -> None:
    r"""The equal-rank unimodular route is not tied to rank 2 (rank-3 definite)."""
    L = Lattices(ZZ)([[2, 0, 0], [0, 2, 0], [0, 0, 2]])
    V = L.vector_space()
    labels = tuple(V.module_generating_set())
    a, b, c = labels
    cycle_V = V.Isom(V)({a: V.module_generator(b), b: V.module_generator(c), c: V.module_generator(a)})
    cycle_L = L.integral_isometry(cycle_V)
    ia, ib, ic = tuple(L.module_generating_set())
    x1, x2, x3 = L.module_generator(ia), L.module_generator(ib), L.module_generator(ic)
    assert cycle_L(x1) == x2 and cycle_L(x2) == x3 and cycle_L(x3) == x1


def test_the_dilation_stays_refused_on_both_fire_positions() -> None:
    r"""A coordinate of ``1/2`` keeps the forward preimage None, as maintained.

    The scaling ``e1 |-> 2 e1, e2 |-> e2/2`` is a rational isometry of ``U``;
    its forward restriction is not integral, so both the general route and the
    unimodular gate return ``None`` before any inverse work.
    """
    L = Lattices(ZZ)([[0, 1], [1, 0]])
    V = L.vector_space()
    labels = tuple(V.module_generating_set())
    first, second = labels
    e1, e2 = V.module_generator(first), V.module_generator(second)
    dilation = V.Isom(V)(
        {
            first: V.scalar_multiple(QQ(2), e1),
            second: V.scalar_multiple(QQ(1) / QQ(2), e2),
        }
    )
    assert dilation.integral_restriction(L, L) is None
    try:
        L.integral_isometry(dilation)
    except ValueError:
        pass
    else:
        raise AssertionError("the dilation must not descend onto the integral lattice")
