r"""Form predicates on the countable-rank identity lattice and a reflection in \(U\)."""

from sage_extensions.all import *


def test_the_identity_form_on_countable_rank_is_nondegenerate_definite_and_not_unimodular() -> None:
    r"""On \(\mathbb Z^{(\mathbb N)}\) with \(e_i\cdot e_j=\delta_{ij}\) the correlation
    \(L\to L^\vee=\mathbb Z^{\mathbb N}\) is injective but misses the functional sending
    every \(e_i\) to 1, so the form is nondegenerate and not unimodular.  Twisting by 2
    makes it even, with every \(e_i\) of divisibility 2.
    """
    infinite = Lattices(ZZ)(ZZ**NN)

    assert infinite.is_nondegenerate()
    assert infinite.is_positive_definite()
    assert not infinite.is_negative_definite()
    assert not infinite.is_unimodular()
    assert not infinite.is_even()

    doubled = infinite.twist(2)
    assert doubled.is_even()
    assert not doubled.is_unimodular()
    assert doubled.basis_vector(0).div() == 2


def test_the_reflection_of_u_in_e_plus_f_sends_e_to_minus_f() -> None:
    r"""\(s_r(x)=x-\tfrac{2b(x,r)}{b(r,r)}r\) with \(r=e+f\), \(b(r,r)=2\), \(b(e,r)=1\):
    \(s_r(e)=e-(e+f)=-f\).
    """
    plane = Lattices(ZZ)("U")
    e, f = plane.module_generators()

    assert plane.reflection(e + f)(e) == -f
    assert plane.reflection(e + f)(f) == -e
