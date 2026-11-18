"""The integral hyperbolic index of an odd unimodular plane.

The expected value is ``0``, and the source of that value is the following
argument, which uses nothing from the implementation.

``L = <1> + <-1>`` has rank two and determinant ``-1``.  A hyperbolic-plane
summand ``U`` of ``L`` is a primitive rank-two sublattice, and both ``L`` and
``U`` are unimodular, so the index ``[L : U]`` satisfies
``[L : U]^2 = |det U| / |det L| = 1``; hence ``L = U``.  But ``U`` is even: its
Gram matrix ``[[0, 1], [1, 0]]`` has zero diagonal, so every vector of ``U``
has even square, while ``q(e_0) = 1`` in ``L``.  No hyperbolic plane is a
summand of ``L``, and the index is ``0``, both at the inertia bound
``min(1, 1) = 1`` and at the parity bound of a rank-two odd unimodular lattice.

The lattice is isotropic, ``q(e_0 + e_1) = 0``, which is what separates this
input from the vacuous case of a lattice with no null vector at all.
"""

from sage_extensions.all import *


def test_the_odd_unimodular_plane_has_no_hyperbolic_plane_summand() -> None:
    lattice = Lattices(ZZ)([[1, 0], [0, -1]])

    assert lattice.is_isotropic() is True
    assert lattice.integral_hyperbolic_index() == 0
