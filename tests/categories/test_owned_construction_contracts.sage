r"""The matrix ring ``M_2(Q)`` acting on itself."""

from sage_extensions.all import *  # noqa: F401,F403


def matrix_units():
    r"""``R = End_Q(Q^2)`` and its matrix units ``e_ij : v_j |-> v_i``."""
    plane = Modules(QQ)(QQ**2)
    v1, v2 = plane.basis()
    ring = plane.End()
    zero = plane.zero()
    e11 = plane.Mor(plane)({v1: v1, v2: zero})
    e12 = plane.Mor(plane)({v1: zero, v2: v1})
    e21 = plane.Mor(plane)({v1: v2, v2: zero})
    e22 = plane.Mor(plane)({v1: zero, v2: v2})
    return ring, e11, e12, e21, e22


def test_left_regular_module_of_M2Q_has_endomorphism_ring_the_opposite_ring() -> None:
    r"""On ``R = M_2(Q)`` acting on itself: ``e12 e21 = e11``, ``e21 e12 = e22``, ``End_R(R) = R^op``.

    ``End_R(R)`` consists of the right multiplications ``x |-> x a``, and
    ``(x |-> x a) o (x |-> x b) = (x |-> x b a)``.
    """
    ring, e11, e12, e21, e22 = matrix_units()
    regular = Modules(ring)(ring)
    one = regular(ring.one())

    assert e12 * e21 == e11
    assert e21 * e12 == e22
    assert e11 + e22 == ring.one()
    assert e12 * (e21 * one) == regular(e11)
    assert e21 * (e12 * one) == regular(e22)
    assert regular.End().is_isomorphic_to(ring.opposite())
    assert not ring.is_commutative()


def test_twisting_the_regular_module_by_an_inner_automorphism_gives_an_isomorphic_module() -> None:
    r"""With ``s`` the exchange matrix, ``x |-> s x`` is ``R``-linear from ``R`` to ``R`` twisted by ``a |-> s a s``.

    ``s (a x) = (s a s)(s x)`` since ``s^2 = 1``; in the twisted module
    ``e12 . 1 = s e12 s = e21``.
    """
    ring, e11, e12, e21, e22 = matrix_units()
    exchange = e12 + e21
    regular = Modules(ring)(ring)
    twisted = regular.twist_scalar_action(ring.conjugation_morphism(exchange))
    forward = regular.Mor(twisted)({regular(ring.one()): twisted(exchange)})

    assert exchange * exchange == ring.one()
    assert e12 * twisted(ring.one()) == twisted(e21)
    assert forward(e12 * regular(ring.one())) == e12 * forward(regular(ring.one()))
    assert forward(regular(e11)) == twisted(exchange * e11)
    assert forward.is_isomorphism()
    assert twisted.is_isomorphic_to(regular)
