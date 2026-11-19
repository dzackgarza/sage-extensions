r"""The pointwise Levi lift at an odd line, where the correction is a radical element.

**The lemma.**  Let `L` be an integral lattice over `ZZ` of any parity, `v` a
primitive isotropic vector of divisibility `d`, `J = v^perp`,
`w` a partner with `b(v,w) = d`, and

    X = {u in J : b(u,J) <= d ZZ,  q(u) + 2 b(w,u) in 2d ZZ},

which is the parameter lattice of the radical: `E_{v,u}` is an integral
isometry of `L` exactly for `u` in `X`, and `u |-> E_{v,u}` kills exactly
`Z v`.  Then for any `g~` in `O(L \otimes QQ)` with `g~(v) = v`:

  (a) if `g~ E_{v,x_0}` is integral for one `x_0` in `J \otimes QQ`, it is
      integral for every `x` in `x_0 + X`;
  (b) conversely, if `x_1` and `x_2` are both admissible then
      `E_{v,x_1} E_{v,x_2}^{-1} = E_{v,x_1 - x_2}` is integral, so
      `x_1 - x_2` lies in `X`.

Hence the admissible parameters are either empty or one coset of `X`, and the
question whether a rational lift can be corrected is a finite search over the
cosets of `X` inside `(1/N) J`.

(a) is the composition law `E_{v,x} E_{v,y} = E_{v,x+y}` of Gritsenko--Hulek--
Sankaran, arXiv:0810.1614, section 3.1, equation (5), printed p. 9, read with
`E_{v,u}` integral for `u` in `X` by equation (4), printed p. 8; (b) is the
same law with `x_2` replaced by `-x_2`, since `E_{v,x}^{-1} = E_{v,-x}`.

The specimens are the two odd divisible lines of the earlier rows.  Their
lift does not exist at `999c928`: the marked-line torsor decides integrality by
cosets of the *transvection* kernel, whose coset argument asserts that the
target is even (`isotropic_lifts.py:525`), so an odd target raises instead of
answering.  With the cosets taken modulo `X` no parity enters.
"""

from sage_extensions.all import *  # noqa: F401,F403

ODD_DIVISIBILITY_TWO = [[0, 2, 0], [2, 0, 0], [0, 0, 3]]
ODD_DIVISIBILITY_THREE = [[0, 3, 0], [3, 0, 0], [0, 0, 3]]


def _assert_the_lifts_answer(gram, divisibility) -> None:
    r"""Every generator of `O(K_I)` with an integral lift has one, fixing the vector."""
    lattice = Lattices(ZZ)(gram)
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[0])
    subobject = lattice.primitive_isotropic_subobject(vector)
    reduction = subobject.isotropic_reduction()
    quotient = reduction.quotient_lattice()

    assert lattice.is_even() is False
    assert vector.q() == ZZ(0)
    assert vector.is_primitive() is True
    assert vector.div() == ZZ(divisibility)

    lifted = tuple(
        reduction.pointwise_levi_lift(generator)
        for generator in tuple(quotient.O().group_generators())
    )
    assert all(lift(vector) == vector for lift in lifted)
    assert tuple(
        reduction.levi_action()(lift) for lift in lifted
    ) == tuple(quotient.O().group_generators())
    assert all(
        lattice.b(lift(left), lift(right)) == lattice.b(left, right)
        for lift in lifted
        for left in lattice.module_generators()
        for right in lattice.module_generators()
    )


def test_the_odd_divisibility_two_line_has_its_integral_levi_lifts() -> None:
    r"""`U(2) + <3>`: odd, divisibility two, and `O(K_I) = {+-1}` lifts integrally."""
    _assert_the_lifts_answer(ODD_DIVISIBILITY_TWO, 2)


def test_the_odd_divisibility_three_line_has_its_integral_levi_lifts() -> None:
    r"""`U(3) + <3>`: divisibility three, so the correction is not a divisibility-two accident."""
    _assert_the_lifts_answer(ODD_DIVISIBILITY_THREE, 3)
