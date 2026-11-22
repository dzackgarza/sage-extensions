r"""The parabolic's generators at a plane whose image in $\GL(I)$ is a proper subgroup.

At a primitive isotropic plane $I$ the parabolic $P_I = \mathrm{Stab}_{O(L)}(I)$ maps onto
a subgroup $M \subseteq \GL(I) \times O(I^\perp/I)$ with kernel the unipotent radical, and
a family generates $P_I$ exactly when its image is $M$ and it contains the radical (Milne,
*Group Theory*, v4.01, Theorem 1.47 with Corollary 1.48, applied to $P_I \to M$).

$M$ is **not** the whole product on the planes of $T_{\mathrm{En}}$: H. Sterk,
*Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207 (1991),
**(4.7)** gives $\Gamma^1(2)$ for the class of $\mathbb{Z}e + \mathbb{Z}e'$ modulo
$O(L_-)$ and $\SL(F)$ otherwise, and **(4.3.17)** gives $\Gamma(2)$ for the plane type
$\{2,4,5\}$ and $\Gamma^1(2)$ for the types $\{4,5\}$, $\{3,5\}$ and $\{3,4\}$ of
$\Gamma_{En,2}$.  So on those planes $\GL(I)$ is never filled, and a decision that asks
for it refuses a correct family.

Both representatives of that class are pinned here.  The plane $\mathbb{Z}e +
\mathbb{Z}e'$ splits off the lattice; the plane $\mathbb{Z}e + \mathbb{Z}\bar\alpha$ with
$\bar\alpha$ Sterk's second vector for the fourth cusp does not, so nothing about it
follows from the split case and its factors have to be computed.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _plane_of_the_first_class(lattice):
    r"""Return $\mathbb{Z}e + \mathbb{Z}e'$, Sterk (4.6)'s first representative.

    In the library's basis $(e, f, e', f', \alpha_1, \ldots, \alpha_8)$ of
    $T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)$ these are the first and the third
    generator; the plane is totally isotropic, so its Gram matrix vanishes.
    """
    basis_elements = list(lattice.module_generators())
    return lattice.primitive_isotropic_subobject(basis_elements[0], basis_elements[2])


def _second_representative_of_the_first_class(lattice):
    r"""Return $\mathbb{Z}e + \mathbb{Z}\bar\alpha$, $\bar\alpha$ Sterk's fourth cusp vector.

    H. Sterk, Math. Z. 207 (1991), (4.2.3), lists $e' + 2f' + \gamma$ with $\gamma$ of
    square $-8$ among the five cusp vectors; (4.3.8) draws that cusp's chamber at the
    second representative $2e' + f' + \bar\alpha_1$, which is the vector used here.  It is
    primitive isotropic, it is orthogonal to $e$, and the plane it spans with $e$ contains
    a divisibility-one isotropic vector, so by (4.6) and (4.7) it is the same
    $O(L_-)$-class as $\mathbb{Z}e + \mathbb{Z}e'$ -- with the same image $\Gamma^1(2)$.
    """
    basis_elements = list(lattice.module_generators())
    e = basis_elements[0]
    alpha = (
        basis_elements[2]
        + 2 * basis_elements[3]
        - 4 * basis_elements[4]
        - 5 * basis_elements[5]
        - 7 * basis_elements[6]
        - 10 * basis_elements[7]
        - 8 * basis_elements[8]
        - 6 * basis_elements[9]
        - 4 * basis_elements[10]
        - 2 * basis_elements[11]
    )
    assert lattice.q(alpha) == ZZ.zero()
    assert lattice.b(e, alpha) == ZZ.zero()
    return lattice.primitive_isotropic_subobject(e, alpha)


def test_the_nonsplit_representative_of_the_class_is_complete() -> None:
    r"""The plane $\mathbb{Z}e + \mathbb{Z}\bar\alpha$ has a generated parabolic.

    The plane has no splitting complement, so its three factors are computed rather than
    assumed: the radical by its parameter lattice and centre, the plane actions of the
    members trivial on $I^\perp/I$, and the quotient images of the members that fix $I$
    pointwise.  On this class the plane actions generate $\Gamma^1(2)$, of index three in
    $\GL_2(\mathbb{Z})$ -- Sterk (4.7) -- so the image is a proper subgroup of
    $\GL(I) \times O(I^\perp/I)$ and the family is the parabolic all the same: the image to
    compare with is the stabilizer's, not the product.
    """
    lattice = NamedLattices.TEn
    plane = _second_representative_of_the_first_class(lattice)

    assert plane.splitting_complement() is None
    assert plane.is_parabolic_complete() is True
    assert plane.parabolic_obstruction() is None


def test_the_split_representative_keeps_its_proper_plane_action_image() -> None:
    r"""At $\mathbb{Z}e + \mathbb{Z}e'$ the plane actions have index three and are complete.

    This is the guard against repairing the previous test by weakening the decision: the
    plane actions of the members trivial on $I^\perp/I$ generate a subgroup of index three
    in $\GL_2(\mathbb{Z})$, which is Sterk (4.7)'s $\Gamma^1(2)$ and not $\GL_2(\mathbb{Z})$,
    and the family is complete at that index.
    """
    lattice = NamedLattices.TEn
    plane = _plane_of_the_first_class(lattice)

    assert plane.levi_plane_action_index(trivial_on_quotient=True) == cardinal(3)
    assert plane.levi_quotient_image_index(trivial_on_plane=True) == cardinal(1)
    assert plane.is_parabolic_complete() is True


def test_a_plane_whose_image_is_the_whole_product_is_still_complete() -> None:
    r"""A plane on which $\GL(I)$ *is* filled keeps its answer.

    $\mathbb{Z}e' + \mathbb{Z}(2e + 2f + \alpha)$ has $J = 2 \cdot 1_2$, so no congruence
    condition on the plane action follows from the second block equation of Dutour
    Sikirić--Hulek, Theorem 4.9, and the plane actions fill $\GL_2(\mathbb{Z})$: the image
    there is the whole product and the family is the parabolic.  The decision has to give
    the same answer on this plane after it stops asking for the product everywhere.
    """
    lattice = NamedLattices.TEn
    basis_elements = list(lattice.module_generators())
    second = basis_elements[2]
    fifth = (
        2 * basis_elements[0]
        + 2 * basis_elements[1]
        - 4 * basis_elements[4]
        - 5 * basis_elements[5]
        - 7 * basis_elements[6]
        - 10 * basis_elements[7]
        - 8 * basis_elements[8]
        - 6 * basis_elements[9]
        - 4 * basis_elements[10]
        - 2 * basis_elements[11]
    )
    plane = lattice.primitive_isotropic_subobject(second, fifth)

    assert plane.levi_plane_action_index(trivial_on_quotient=True) == cardinal(1)
    assert plane.is_parabolic_complete() is True
