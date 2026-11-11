r"""The plane stabilizer of Sterk's $P_2$ of $T_{\mathrm{En}}$ fills $O(P_2^\perp/P_2)$ (#352).

At a primitive isotropic plane $I$ of an even lattice $L$, an isometry with $g(I)=I$ descends
to $I^\perp/I$, so the setwise stabilizer $M=\operatorname{Stab}_{O(L)}(I)$ has an image in
$O(I^\perp/I)$.  The returned generators of the stabilizer generate it *by construction*
(`select_group_generators` states the family it was handed), so their images generate that
image, and the family of `parabolic_stabilizer_generators` sits inside the same stabilizer --
which gives the sandwich

    $\langle \rho_{\mathrm{levi}}(\text{parabolic family}) \rangle \subseteq M \subseteq O(I^\perp/I)$.

Both ends are computed here.  At $P_2 = \mathbb{Z}(2e_1+2e_2+w) + \mathbb{Z}e_3$ with
$w = e_5 + e_6$ of square $-8$ (H. Sterk, *Compactifications of the period space of Enriques
surfaces, Part I*, Math. Z. 207 (1991), Proposition 4.6, p. 29, in the bases used by
D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, §3.6, p. 22) the quotient
$K = P_2^\perp/P_2$ is negative definite of rank 8 and determinant 64, so $O(K)$ is finite;
its order and the order of the subgroup each family generates are compared, and no count is
typed.  At this plane the two orders agree, so $M$ is all of $O(P_2^\perp/P_2)$ and the
parabolic's returned generators already reach it -- which is what
`levi_quotient_image_index()` reports as the index $1$.

This settles the quotient factor of `is_parabolic_complete()` by computation.  The predicate
stays False at $P_2$: the factor that remains is the unipotent radical (#353), whose rank is a
statement about a torsion-free nilpotent lattice and is not made here.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _second_representative(lattice):
    r"""Sterk's $P_2$: the plane that does not split off $T_{\mathrm{En}}$."""
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    return lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third)


def test_the_plane_stabilizer_reaches_the_whole_quotient_orthogonal_group() -> None:
    r"""Both families' images have the order of $O(P_2^\perp/P_2)$, and the index is one."""
    lattice = NamedLattices.TEn
    plane = _second_representative(lattice)
    reduction = plane.isotropic_reduction()
    orthogonal = reduction.quotient_lattice().Aut()
    levi = reduction.levi_action()

    def image_of(family):
        return orthogonal.subgroup(tuple(levi(generator) for generator in family))

    parabolic = image_of(tuple(plane.parabolic_stabilizer_generators()))
    stabilizer = image_of(
        tuple(lattice.Aut().stabilizer(plane, action="setwise").group_generators())
    )
    total = orthogonal.cardinality()

    assert parabolic.cardinality() == total
    assert stabilizer.cardinality() == total
    assert cardinal(plane.levi_quotient_image_index()) == cardinal(1)
