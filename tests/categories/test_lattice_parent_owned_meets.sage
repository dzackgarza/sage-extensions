r"""Sublattices and orthogonal sums of small root lattices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_root_of_A2_and_its_orthogonal_complement_span_an_index_two_sublattice() -> None:
    r"""For a root ``a1`` of ``A2``: ``(Z a1)^perp = Z(a1 + 2 a2)`` of norm ``+-6``.

    ``(a1 + 2 a2)^2 = 2 - 4 + 8 = 6`` up to the sign convention, so
    ``A1 + <6>`` has determinant 12 and index 2 in ``A2`` (``det A2 = 3``).
    """
    a2 = Lattices(ZZ)("A2")
    a1, _ = a2.basis()
    root_line = a2.sublattice_from((a1,))
    complement = a2.orthogonal_complement(root_line)
    (c,) = complement.basis()
    sum_inclusion = a2.sublattice_from((a1, complement.inclusion()(c)))

    assert root_line.is_isometric_to(Lattices(ZZ)("A1"))
    assert root_line.inclusion().is_primitive()
    assert abs(complement.determinant()) == 6
    assert abs(sum_inclusion.determinant()) == 12
    assert sum_inclusion.inclusion().index() == 2


def test_two_hyperbolic_planes_form_the_even_unimodular_lattice_of_signature_2_2() -> None:
    r"""``U + U`` is even, unimodular, of signature ``(2, 2)``."""
    u = Lattices(ZZ)("U")
    sum_ = u + u

    assert sum_.rank() == 4
    assert sum_.is_even()
    assert sum_.is_unimodular()
    assert sum_.signature_pair().first() == 2
    assert sum_.signature_pair().second() == 2
