r"""The spinor kernel `O^+(L)` is not contained in `SO(L)`: a reflection in a vector of negative square sits in it with determinant `-1`.

The real spinor norm is the spinor norm of the quadratic space `L \otimes RR`.  For a nondegenerate
quadratic space over a field of characteristic other than two every isometry is a product of
reflections `s_{v_1} \cdots s_{v_m}`, and

.. math::
    \mathrm{sn}(g) = \prod_{i=1}^{m} c\,q(v_i) \quad \text{modulo squares}

does not depend on the factorization, so `sn` is a group morphism on `O(L)` (O'Meara, *Introduction
to Quadratic Forms*, §55, where `c = 1`; `c` is a normalization).  Over `RR` the square classes are
`RR^\times / RR^{\times 2} = {\pm 1}`, `sn_RR` is a character to the group of order two, and
`O^+(L) = O(L) \cap \ker sn_RR` (Gritsenko--Hulek--Sankaran, *Abelianisation of orthogonal groups*,
arXiv:0810.1614, §1, with `c = -1/2` -- the multiplier that makes a reflection in a negative vector
fix each component of the period domain in signature `(2, n)`).

**A reflection has one factor.**  So `sn_RR(s_v)` is the class of `c\,q(v)`, and with `c = -1/2` it
is `+1` exactly when `q(v) < 0`.  A reflection has determinant `-1` for every `v`.  Hence every
reflection in a vector of negative square is an element of `O^+(L)` with negative determinant, and
the spinor condition does not force the determinant: `O^+(L)` is not contained in `SO(L)`.  The
hyperbolic plane shows it first -- `e - f` has square `-2` -- and `T_{Co}` shows it on the lattice the
Coble rows are computed on, where `h - a_1` has square `-2`.

**The companion half is the positive vector**, and it is what makes the point: `s_{e+f}` has square
`c\,q(e+f) = -1`, so it lies *outside* `O^+(U)`, although its determinant is `-1` as well.  The two
signs of square therefore differ in the character and agree in the determinant, so
`O^+(L) \to {\pm 1}`, `g \mapsto \det g`, is onto whenever `L` has a vector of nonzero square -- the
determinant is independent of the spinor condition, not implied by it.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_reflection_in_a_negative_root_of_the_hyperbolic_plane_is_in_the_spinor_kernel() -> None:
    r"""`U`: `q(e - f) = -2`, so `s_{e-f}` lies in `O^+(U)`, and its determinant is `-1`."""
    lattice = NamedLattices.U
    root = lattice.module_generator(0) - lattice.module_generator(1)
    assert lattice.q(root) == -2
    reflection = lattice.reflection(root)
    assert reflection.determinant() == -1
    assert (reflection in lattice.O_plus()) is True


def test_the_reflection_in_a_positive_vector_of_the_hyperbolic_plane_is_outside_the_spinor_kernel() -> None:
    r"""`U`: `q(e + f) = 2`, so `s_{e+f}` is outside `O^+(U)`, and its determinant is `-1` too."""
    lattice = NamedLattices.U
    vector = lattice.module_generator(0) + lattice.module_generator(1)
    assert lattice.q(vector) == 2
    reflection = lattice.reflection(vector)
    assert reflection.determinant() == -1
    assert (reflection in lattice.O_plus()) is False


def test_the_reflection_in_a_negative_root_of_the_coble_lattice_is_in_the_spinor_kernel() -> None:
    r"""`T_{Co}`: `q(h - a_1) = -2`, so `s_{h-a_1}` lies in `O^+(T_{Co})` with determinant `-1`."""
    lattice = NamedLattices.Tco
    root = lattice.module_generator("h") - lattice.module_generator("a1")
    assert lattice.q(root) == -2
    reflection = lattice.reflection(root)
    assert reflection.determinant() == -1
    assert (reflection in lattice.O_plus()) is True
