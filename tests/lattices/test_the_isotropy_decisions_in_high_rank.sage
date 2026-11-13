r"""Isotropy decided by theorem in every rank, and a witness built where the search refuses (#371).

`L.is_isotropic()` answers whether `b(x, x) = 0` has a nonzero rational solution,
and `L.isotropic_vector()` produces one.  Both are exercised here on lattices of
rank ten and above, where deciding isotropy by a witness search alone is not
available: PARI's `qfsolve` — Denis Simon's code, which Sage's
`quadratic_forms.qfsolve` interfaces — refuses above nine variables
(`qfsolve, dim >= 10 is not yet implemented`), which is where
`T_Co.Aut().isotropic_orbit_representatives(2)` stopped in
`results/issue360-coble-plane-row.md`.

**The decision.**  A nondegenerate form over ℤ or ℚ is decided by three
statements, and a search runs only where none of them applies:

* a definite form represents no nonzero zero — that is what definiteness is;
* an indefinite form of rank at least five is isotropic: Meyer's theorem
  (Serre, *A Course in Arithmetic*, Ch. IV, §3.2, Cor. 2, printed p. 43, as
  sage-extensions#371 cites it);
* an indefinite form of rank at most four is decided by Hasse–Minkowski and the
  local invariants (Serre, Ch. IV, §3.2, Thm. 8, printed p. 41), which is what
  `qfsolve` implements.

**The witness.**  Above nine variables the isotropic vector is built rather than
searched for: the form is diagonalized over ℚ, five diagonal directions carrying
both signs span a subspace Meyer makes isotropic, `qfsolve` runs there, and the
diagonalizing change of basis carries the zero back.  Each vector returned below
is checked to lie in its lattice, to be nonzero, to have square zero and to be
primitive — the defining properties of the object asked for.

The companion facts pinned here are the ones that keep the rule honest: a
definite lattice of rank sixteen is *not* isotropic, and an indefinite lattice of
rank two can still be anisotropic, so "indefinite" alone decides nothing at low
rank.
"""

from sage_extensions.all import *  # noqa: F401,F403
import pytest


def _assert_isotropic_witness(lattice) -> None:
    r"""``L.isotropic_vector()`` returns a nonzero primitive vector of square zero."""
    vector = lattice.isotropic_vector()

    assert vector.parent() is lattice
    assert vector != lattice.zero()
    assert lattice.q(vector) == ZZ.zero()
    assert vector.is_primitive() is True


def test_the_unimodular_rank_ten_lattice_is_isotropic_and_has_a_witness() -> None:
    r"""$U \oplus E_8(-1)$, rank ten and signature $(1, 9)$, is isotropic by Meyer's theorem.

    Its rank is above every solver's bound and above five, so the decision is the
    theorem's; the witness is the rank-five subspace reduction's.
    """
    lattice = NamedLattices.U + NamedLattices.E8

    assert int(lattice.module_rank()) == 10
    assert tuple(lattice.signature_pair()) == (1, 9)
    assert lattice.is_isotropic() is True
    _assert_isotropic_witness(lattice)


def test_the_coble_lattice_is_isotropic_and_has_a_witness() -> None:
    r"""$T_{\mathrm{Co}} = \langle 2\rangle \oplus U(2) \oplus E_8(-2)$, rank eleven, is isotropic.

    This is the lattice whose reduction $v^\perp/\mathbf{Z}v \cong I_{1,8}(2)$
    the plane row of sage-extensions#360 asks for, and the one the search refused.
    """
    lattice = NamedLattices.Tco

    assert int(lattice.module_rank()) == 11
    assert tuple(lattice.signature_pair()) == (2, 9)
    assert lattice.is_isotropic() is True
    _assert_isotropic_witness(lattice)


def test_a_definite_lattice_of_high_rank_is_not_isotropic() -> None:
    r"""$E_8(-1) \oplus E_8(-1)$, rank sixteen and definite, represents no zero.

    The negative decision is a theorem's too: a definite form is nonzero on every
    nonzero vector, so no rank needs a search to answer it.
    """
    lattice = NamedLattices.E8 + NamedLattices.E8

    assert int(lattice.module_rank()) == 16
    assert lattice.is_definite() is True
    assert lattice.is_isotropic() is False
    with pytest.raises(ValueError):
        lattice.isotropic_vector()


def test_the_indefinite_rank_two_form_that_is_anisotropic_stays_anisotropic() -> None:
    r"""$\langle 1, -2\rangle$ is indefinite and represents no zero over $\mathbb{Q}$.

    $x^2 = 2y^2$ has no nonzero rational solution, so the rank-at-most-four
    branch must still refuse here: indefiniteness alone is not isotropy below rank
    five, and a rule that answered by signature alone would get this lattice wrong.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, -2]])

    assert int(lattice.module_rank()) == 2
    assert lattice.is_definite() is False
    assert lattice.is_isotropic() is False
    with pytest.raises(ValueError):
        lattice.isotropic_vector()


def test_the_odd_unimodular_lattice_of_signature_one_four_has_a_witness() -> None:
    r"""$I_{1,4} = \langle 1 \rangle \oplus \langle -1 \rangle^{\oplus 4}$ is isotropic: $e_0 + e_1$ has square zero.

    It is odd, so its Gram matrix has an odd diagonal entry.  It is the smallest
    lattice that reaches the rank-five subspace route with an odd form, and the
    form is isotropic by inspection, so a witness must come back.
    """
    lattice = Lattices(ZZ)(diagonal_matrix(ZZ, [1, -1, -1, -1, -1]))

    assert lattice.is_isotropic() is True
    _assert_isotropic_witness(lattice)
