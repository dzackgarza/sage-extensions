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


def test_forward_integral_with_a_nonunit_determinant_stays_refused_on_differing_frames() -> None:
    r"""``<8> -> <2>`` by ``v |-> 2 v``: forward integral, determinant 2, inverse not integral.

    The general route computes the rational preimage of the inverse and finds
    it non-integral; the unimodular gate answers the same ``None`` from the
    determinant alone.  The opposite direction ``v |-> v/2`` is refused
    already at the forward preimage; both directions are asserted.
    """
    L8 = Lattices(ZZ)([[8]])
    L2 = Lattices(ZZ)([[2]])
    V8 = L8.vector_space()
    V2 = L2.vector_space()
    (l8,) = tuple(V8.module_generating_set())
    (l2,) = tuple(V2.module_generating_set())
    expand = V8.Isom(V2)({l8: V2.scalar_multiple(QQ(2), V2.module_generator(l2))})
    assert expand.integral_restriction(L8, L2) is None
    contract = V2.Isom(V8)({l2: V8.scalar_multiple(QQ(1) / QQ(2), V8.module_generator(l8))})
    assert contract.integral_restriction(L2, L8) is None


def test_differing_frames_with_unit_determinants_still_descend_both_ways() -> None:
    r"""Genuinely congruent distinct frames: ``[[2,0],[0,2]]`` and ``[[4,2],[2,2]]``, both ways.

    ``[[4,2],[2,2]] = Q (2I) Q^T`` with ``Q = [[1,1],[0,1]]``: the same form
    on a genuinely different basis, on a genuinely different object (the two
    Gram matrices differ, so interning cannot collapse them).  The modified
    map is checked against every generator pairing of both lattices, then its
    integral restriction and the restriction of its inverse with both inverse
    compositions verified pointwise.
    """
    La = Lattices(ZZ)([[2, 0], [0, 2]])
    Lb = Lattices(ZZ)([[4, 2], [2, 2]])
    assert La is not Lb
    Va = La.vector_space()
    Vb = Lb.vector_space()
    la1, la2 = tuple(Va.module_generating_set())
    lb1, lb2 = tuple(Vb.module_generating_set())
    fb1, fb2 = Vb.module_generator(lb1), Vb.module_generator(lb2)
    congruence = Va.Isom(Vb)(
        {
            la1: fb1 - fb2,
            la2: fb2,
        }
    )
    # the arrow is a genuine isometry: every pairing of the two bases agrees
    for x_label, y_label in ((la1, la1), (la1, la2), (la2, la2)):
        assert Vb.b(congruence(Va.module_generator(x_label)), congruence(Va.module_generator(y_label))) == Va.b(
            Va.module_generator(x_label), Va.module_generator(y_label)
        ), (x_label, y_label)
    forward = congruence.integral_restriction(La, Lb)
    ia1, ia2 = tuple(La.module_generating_set())
    ib1, ib2 = tuple(Lb.module_generating_set())
    e_a1, e_a2 = La.module_generator(ia1), La.module_generator(ia2)
    e_b1, e_b2 = Lb.module_generator(ib1), Lb.module_generator(ib2)
    assert forward(e_a1) == e_b1 - e_b2 and forward(e_a2) == e_b2
    backward = congruence.inverse().integral_restriction(Lb, La)
    assert backward(e_b1) == e_a1 + e_a2 and backward(e_b2) == e_a2
    # both inverse compositions on the integral models, pointwise
    assert backward(forward(e_a1)) == e_a1 and backward(forward(e_a2)) == e_a2
    assert forward(backward(e_b1)) == e_b1 and forward(backward(e_b2)) == e_b2


def test_over_a_finite_field_the_gate_stays_out_while_the_route_has_a_known_old_failure() -> None:
    r"""Known old failure, not demonstrated functionality: the gate stays out over ``GF(5)``.

    ``M=2`` joins ``<2>`` to ``<3>`` over ``GF(5)`` (``3*2^2 = 12 =_5 2``);
    its determinant ``2`` is a unit of ``GF(5)`` but not ``+-1``; an ungated
    integer reading of it is exactly the ``TypeError: int() ... not
    'OwnedJoinCategory.element_class'`` the gate originally raised on this
    specimen.  With the gate restricted to the owned integers the gate no
    longer fires; today's maintained backward route has a registered old
    defect over this quotient ring (TRAPS.md: the backward restricted-scalars
    composition reads a lattice morphism as a scalar, identical on pre-gate
    code), so the specimen cannot demonstrate a returned isometry.  What it
    pins, and only that: the gate cast never fires, and any error met here is
    that pre-existing route defect, not the gate's.  The defendant branch is
    retained so a future repair of that defect demonstrates the isometry
    pointwise without a test rewrite.
    """
    FF5 = GF(5)
    source = Lattices(FF5)([[2]])
    target = Lattices(FF5)([[3]])
    ring_map = FF5.fraction_field_map()
    V_s = source.base_change(ring_map)
    V_t = target.base_change(ring_map)
    (ls,) = tuple(V_s.module_generating_set())
    (lt,) = tuple(V_t.module_generating_set())
    two = FF5(2)
    scale = V_s.Isom(V_t)({ls: V_t.scalar_multiple(two, V_t.module_generator(lt))})
    (is_label,) = tuple(source.module_generating_set())
    (it_label,) = tuple(target.module_generating_set())
    s_gen = source.module_generator(is_label)
    t_gen = target.module_generator(it_label)
    try:
        forward = scale.integral_restriction(source, target)
    except TypeError as exc:
        # the separate pre-existing route defect (see TRAPS.md): the backward
        # composition over this quotient ring tries to read a morphism as a
        # scalar. The gate's own defect would instead say "not
        # 'OwnedJoinCategory.element_class'" from an integer cast of the
        # determinant.
        assert "raw Sage object" in str(exc), (
            f"expected the pre-existing backward-composition defect, got {exc!r}"
        )
    else:
        # once that separate defect is repaired, the gate still sits out and
        # the isometry is returned with this exact action
        assert forward is not None
        assert forward(s_gen) == target.scalar_multiple(two, t_gen)
        backward = scale.inverse().integral_restriction(target, source)
        assert backward is not None
        assert backward(t_gen) == source.scalar_multiple(FF5(3), s_gen)
