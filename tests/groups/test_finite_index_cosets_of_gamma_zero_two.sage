r"""Double cosets ``H \ GL_2(ZZ) / B`` for finite-index ``H``: the cusps of ``Gamma_0(2)``.

Closure specimen of the TODO node ``finite-index-orbits-on-projective-line``.
Written unexecuted under DEV-58; its execution is owed at terminal T.

Let ``J = ZZ e_0 + ZZ e_1`` and ``G = GL(J) = GL_2(ZZ)``, matrices acting on
coordinate columns, and ``B = Stab_G(ZZ e_0)``, the upper triangular matrices
with diagonal entries ``+-1``.

Sources (opened 2026-10-14):

- ``[SL_2(ZZ) : Gamma_0(p)] = p + 1`` for prime ``p``: TauCeti
  ``CongruenceSubgroup.Gamma0_prime_index``
  (``TauCeti/NumberTheory/ModularForms/CongruenceSubgroups/Basic.lean``);
  Milne, *Modular Functions and Modular Forms* v1.31, p. 87,
  ``(Gamma(1) : Gamma_0(N)) = N prod_{p | N} (1 + 1/p)``; Stein, *Modular
  Forms: A Computational Approach*, Section 6.1, p. 93.  For ``N = 2`` the
  index is 3.
- The cusps of a finite-index ``Gamma`` are its orbits on ``P^1(QQ)``, and
  ``SL_2(ZZ)`` acts transitively on ``P^1(QQ)``: Milne, Remark 2.11, p. 31;
  Stein, Lemma 1.12 and the definition of ``C(Gamma)``, p. 5.
- ``Gamma_0(N)`` has ``sum_{d | N} phi(gcd(d, N/d))`` cusps: Milne, p. 88.
  For ``N = 2`` this is ``phi(1) + phi(1) = 2``.

Derivations (not citations):

1. ``[GL_2(ZZ) : SL_2(ZZ)] = 2``: ``det`` maps ``GL_2(ZZ)`` onto ``{+1, -1}``
   (``diag(1, -1)`` has determinant ``-1``) with kernel ``SL_2(ZZ)``.  Hence
   ``[GL_2(ZZ) : Gamma_0(2)] = 2 * 3 = 6``; this is the caller-stated index.
2. ``H \ G / B`` is the set of ``H``-orbits on ``G / B = P^1(QQ)``: ``G``
   acts transitively on ``P^1(QQ)`` (``SL_2(ZZ)`` already does), the
   stabilizer of ``infinity = [e_0]`` is ``B``, and ``HgB |-> H . g(infinity)``
   is a bijection.  The left factor is ``H`` itself, so the count is the
   number of ``H``-orbits on ``P^1(QQ)``, the cusp count of ``H``; the
   elements of ``G`` of determinant ``-1`` enter only through ``G / B``.
   (``e = diag(1, -1)`` normalizes ``Gamma_0(2)`` and fixes ``infinity`` and
   ``0``, so even ``<Gamma_0(2), e>`` would have the same two orbits.)
   For ``H = Gamma_0(2)`` the count is 2.  For ``H = SL_2(ZZ)`` it is 1, by
   transitivity.

Generators of ``H``: ``T = [[1, 1], [0, 1]]``, ``U = [[1, 0], [2, 1]]`` and
``-I`` lie in ``Gamma_0(2)`` (lower left entry even).  That they generate it
is not taken from an opened source: it is the caller-stated index 6, since a
proper subgroup of ``Gamma_0(2)`` has index greater than 6 in ``G``.  ``S`` and
``T`` generate ``SL_2(ZZ)``: Mathlib
``Matrix.SpecialLinearGroup.SL2Z_generators``; Conrad, *SL_2(ZZ)*, Cor. 2.3.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_double_cosets_of_gamma_zero_two_are_its_two_cusps():
    points = Sets.Δ[1]
    first, second = points(0), points(1)
    plane = ZZ.free_module(points)
    e_0, e_1 = plane.module_generator(first), plane.module_generator(second)
    general_linear = plane.general_linear_group()

    def automorphism(image_of_e_0, image_of_e_1):
        return general_linear({first: image_of_e_0, second: image_of_e_1})

    translation = automorphism(e_0, e_0 + e_1)
    lower = automorphism(e_0 + 2 * e_1, e_1)
    minus_identity = automorphism(-e_0, -e_1)
    gamma_zero_two = general_linear.subgroup((translation, lower, minus_identity))
    line_stabilizer = general_linear.flag_stabilizer((plane.subobject_on(Set((e_0,))),))

    general_linear.select_left_cosets(general_linear.finite_index_left_cosets(gamma_zero_two, 6))

    assert general_linear.double_cosets(gamma_zero_two, line_stabilizer).cardinality() == cardinal(2)


def test_the_double_cosets_of_sl2z_are_its_one_cusp():
    points = Sets.Δ[1]
    first, second = points(0), points(1)
    plane = ZZ.free_module(points)
    e_0, e_1 = plane.module_generator(first), plane.module_generator(second)
    general_linear = plane.general_linear_group()

    def automorphism(image_of_e_0, image_of_e_1):
        return general_linear({first: image_of_e_0, second: image_of_e_1})

    rotation = automorphism(e_1, -e_0)
    translation = automorphism(e_0, e_0 + e_1)
    special_linear = general_linear.subgroup((rotation, translation))
    line_stabilizer = general_linear.flag_stabilizer((plane.subobject_on(Set((e_0,))),))

    general_linear.select_left_cosets(general_linear.finite_index_left_cosets(special_linear, 2))

    assert general_linear.double_cosets(special_linear, line_stabilizer).cardinality() == cardinal(1)
