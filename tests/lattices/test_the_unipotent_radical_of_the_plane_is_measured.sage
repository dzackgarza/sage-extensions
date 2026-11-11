r"""What is measured about the unipotent radical at Sterk's $P_2$ of $T_{\mathrm{En}}$ (#353).

The radical of the setwise stabilizer is
$U_I = \ker(P_I \to \GL(I) \times O(I^\perp/I))$, the kernel of the plane stabilizer's action
on the plane and on $P^\perp/P$.  This file records what the public calls decide there, and what
they refuse:

* every generator returned by `unipotent_radical_generators()` fixes the plane pointwise and
  acts trivially on $P_2^\perp/P_2$, so it lies in the radical — both properties are computed
  here on the plane's own basis, not taken from the method that selected them (#337 asked
  whether they lie outside it; at $P_2$ they do not);
* the generators of `parabolic_stabilizer_generators()` that lie in the radical are counted
  here by the same two computations, and the kernel subgroup's own membership agrees with that
  count, so the two independent readings agree;
* the index of the returned family in the radical is **not** available:
  `unipotent_radical_index()` refuses and names the port operation that would supply the
  radical's own generating family (`EichlerRecursion.isotropic_quotient_kernel_generators`,
  which this runtime does not provide), and the cited generation of the radical by Eichler
  transvections — Scattone, Mem. Amer. Math. Soc. 374, §3.7, Proposition 3.7.3, as the
  repository quotes it — needs two orthogonal hyperbolic planes (Dutour Sikirić–Hulek,
  arXiv:2302.01679v2, Lemma 4.2 and proof, p. 28), which $T_{\mathrm{En}}$ does not have
  (rank$_2 = 2$, no second hyperbolic plane: Gritsenko–Hulek–Sankaran, arXiv:0810.1614v1,
  Proposition 5.6, p. 17).

So `is_parabolic_complete()` stays `False` at $P_2$ and `parabolic_obstruction()` names the
radical.  The plane-action factor (index $1$ by the $\Gamma(2)$ certificate) and the quotient
factor (index $1$ by computed orders) are already decided; the radical is the last one.
"""

from sage_extensions.all import *  # noqa: F401,F403
import pytest


def _second_representative(lattice):
    r"""Sterk's $P_2$: the plane that does not split off $T_{\mathrm{En}}$."""
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    return lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third)


def test_the_returned_unipotent_generators_lie_in_the_radical() -> None:
    r"""Each one fixes the plane pointwise and acts trivially on $P_2^\perp/P_2$."""
    lattice = NamedLattices.TEn
    plane = _second_representative(lattice)
    basis = tuple(
        plane.inclusion()(plane.module_generator(label))
        for label in plane.module_generating_set()
    )

    def fixes_pointwise(automorphism):
        return all(automorphism(vector) == vector for vector in basis)

    returned = tuple(plane.unipotent_radical_generators())
    returned_count = sum(1 for _ in returned)
    assert sum(1 for generator in returned if fixes_pointwise(generator)) == returned_count
    assert sum(
        1
        for generator in returned
        if plane.acts_trivially_on_isotropic_reduction(generator)
    ) == returned_count

    family = tuple(plane.parabolic_stabilizer_generators())
    radical = plane.unipotent_radical()
    by_predicate = sum(
        1
        for generator in family
        if fixes_pointwise(generator)
        and plane.acts_trivially_on_isotropic_reduction(generator)
    )
    by_membership = sum(1 for generator in family if generator in radical)

    assert cardinal(by_predicate) == cardinal(by_membership)
    assert cardinal(returned_count) == cardinal(
        sum(1 for generator in returned if generator in radical)
    )


def test_the_radical_index_refuses_and_names_the_missing_operation() -> None:
    r"""No index is claimed: the radical's own generating family is not in this runtime."""
    plane = _second_representative(NamedLattices.TEn)

    with pytest.raises(ValueError):
        plane.unipotent_radical_index()

    assert plane.is_parabolic_complete() is False
    assert bool(plane.parabolic_obstruction()) is True
