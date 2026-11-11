r"""The primitive isotropic line orbits of the Hilbert model ``U + (O_F, Tr)``.

``L_F = U + (O_F, Tr)`` is the rank-four even lattice of Witt index one carried
by the two-by-two Hermitian matrices of a real quadratic field: with
``X = [[a, beta], [conj(beta), d]]`` and ``q(X) = -2 det X``, the basis
``(E_11, E_22, 1, omega)`` has the Gram matrix built below.  It has no second
hyperbolic plane, so the Eichler envelope that classifies isotropic orbits on
``U + U + K`` does not reach it; the count of its primitive isotropic lines is
the cusp count of the Hilbert modular group instead:

* Bruinier, *Hilbert modular forms and their applications*, in *The 1-2-3 of
  Modular Forms* (Universitext, Springer, 2008), pp. 105-179, §2.7, printed pp. 143-144: the
  Hilbert lattice is ``L = ZZ + ZZ + O_F`` inside ``V = QQ + QQ + F`` with
  ``Q(a, b, nu) = nu conj(nu) - a b``, and ``Gamma_F = SL_2(O_F) = Spin_L``.
  This library's form is ``q = 2Q``, so the Gram matrix below is twice the
  source's; isotropy and the orthogonal group are unchanged.  ``Spin_L <= O(L)``,
  so ``O(L)`` has no more orbits of isotropic lines than ``Gamma_F``.
* Bruinier, ibid., Corollary 1.4 (§1.1, printed pp. 106-109): the number of
  cusps of ``Gamma_F`` is the class number ``h(F)``.  Cusps are the
  ``Gamma_F``-orbits of ``P^1(F)`` (§1.1, printed p. 106), the rational boundary
  points of the projective model are ``P^1(F)`` (ibid. (1.9)), and those are the
  rational isotropic lines (ibid. Lemma 2.20 and §2.7).  A rational isotropic
  line meets ``L`` in a rank-one primitive sublattice, so the ``Gamma_F``-orbits
  of primitive isotropic lines of ``L`` number ``h(F)``.  The printed pages are
  the publisher's contents pages for the sections: Corollary 1.4 is the last
  numbered statement of §1.1, which runs from p. 106 to the page where §1.2
  begins, p. 109.  Hirzebruch-Van de Ven, *Hilbert modular surfaces and the
  classification of algebraic surfaces*, Invent. Math. 23 (1974), 1-29,
  pp. 12-13, states the same count on an exact printed page, without a statement
  number, for ``K = QQ(sqrt p)`` with ``p = 1 mod 4`` prime.

Hence on a field of class number one there is exactly one ``O(L)``-orbit of
primitive isotropic lines, and every returned line must be primitive, generated
by a primitive isotropic vector of ``L``, of divisibility one.  On
``F = QQ(sqrt(10))``, of class number two, the count is not one and the call
must not answer with a single line.
"""

import pytest

from sage_extensions.all import *


_CASES = (
    (5, 5),
    (2, 8),
)


def _hilbert_model(discriminant):
    r"""``U + (O_F, Tr)`` in the basis ``(E_11, E_22, 1, omega)``, ``F = QQ(sqrt d)``."""
    if discriminant % 4 == 1:
        trace_of_omega, trace_of_norm = 1, (1 - discriminant) // 2
    else:
        trace_of_omega, trace_of_norm = 0, -discriminant // 2
    return Lattices(ZZ)(
        [
            [0, -1, 0, 0],
            [-1, 0, 0, 0],
            [0, 0, 2, trace_of_omega],
            [0, 0, trace_of_omega, trace_of_norm],
        ]
    )


def test_the_hilbert_model_of_class_number_one_has_the_single_cusp() -> None:
    r""":math:`F = QQ(\sqrt 5)` and :math:`F = QQ(\sqrt 2)`: one line, checked."""
    for radicand, discriminant in _CASES:
        field = QuadraticField(radicand, "s")
        assert int(field.discriminant()) == discriminant
        assert int(field.class_number()) == 1

        lattice = _hilbert_model(discriminant)
        assert int(lattice.module_rank()) == 4
        assert int(lattice.witt_index()) == 1
        assert int(lattice.determinant()) == discriminant

        lines = lattice.Aut().isotropic_orbit_representatives(1)
        assert lines.cardinality() == 1
        for line in lines:
            assert int(line.module_rank()) == 1
            assert line.is_primitive() is True
            vector = line.inclusion()(line.module_generator(0))
            assert vector.q() == ZZ(0)
            assert vector.is_primitive() is True
            assert lattice.div(vector) == ZZ(1)


def test_a_hilbert_model_of_class_number_two_does_not_answer_with_one_line() -> None:
    r""":math:`F = QQ(\sqrt{10})` has class number two: the count is not one."""
    field = QuadraticField(10, "s")
    assert int(field.discriminant()) == 40
    assert int(field.class_number()) == 2

    lattice = _hilbert_model(40)
    assert int(lattice.module_rank()) == 4
    assert int(lattice.witt_index()) == 1

    with pytest.raises(NotImplementedError):
        lattice.Aut().isotropic_orbit_representatives(1)
