r"""Sections of ``O(a, b)`` on ``P^1 x P^1``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sections_of_o_4_4_and_o_8_8_on_p1_times_p1_have_dimensions_25_and_81() -> None:
    r"""``h^0(P^1 x P^1, O(a, b)) = (a + 1)(b + 1)`` for ``a, b >= 0``: 25 for ``(4, 4)``, 81 for ``(8, 8)``.

    Derivation: Künneth, ``H^0(O(a, b)) = H^0(P^1, O(a)) ⊗ H^0(P^1, O(b))``
    (Hartshorne III.5.1 for ``h^0(P^1, O(a)) = a + 1``).  The section ring of
    ``O(4, 4)`` has these as its degree-1 and degree-2 pieces.
    """
    P1 = Schemes(QQ).projective_space(1)
    Q = P1.product(P1)
    bundle = Q.O(4, 4)
    ring = bundle.section_ring()

    assert bundle.global_sections().dimension() == 25
    assert Q.O(8, 8).global_sections().dimension() == 81
    assert ring.graded_piece(1).dimension() == 25
    assert ring.graded_piece(2).dimension() == 81
    assert Q.O(1, 0).global_sections().dimension() == 2
    assert Q.O(-1, 3).global_sections().dimension() == 0
