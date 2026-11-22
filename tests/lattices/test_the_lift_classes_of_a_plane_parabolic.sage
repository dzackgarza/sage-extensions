r"""The plane actions that admit an integral lift, and the family that reaches them.

The plane projection of the parabolic's image $M$ is not $\GL(I)$: an isometry carrying
$I$ onto itself with a trivial class action has a plane action $Q_1$ whose blocks are
determined by the block equations of Dutour Sikirić--Hulek, *Moduli of polarised Enriques
surfaces -- computational aspects*, Theorem 4.9, equations $(E_2)$ and $(E_3)$, so only
those $Q_1$ that survive them can occur.  On $T_{\mathrm{En}}$ at a plane with
$|\det J| = 2$ the surviving group is $\Gamma(2)$ or $\Gamma^1(2)$ -- H. Sterk,
*Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207 (1991),
(4.3.17) and (4.7) -- so the comparison is modulo $2$, where those two differ by the
single class of $\begin{pmatrix}1&0\\1&1\end{pmatrix}$.

`liftable_plane_action_classes()` is the first set and `plane_action_class_image()` is the
second; together with the $\Gamma(2)$ certificate of `levi_plane_action_index` they say
the plane projection of the family's image *is* the plane projection of $M$, which is what
`parabolic_completeness_decision` compares.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _plane_of_the_first_class(lattice):
    r"""Return $\mathbb{Z}e + \mathbb{Z}e'$, Sterk (4.6)'s first representative."""
    basis_elements = list(lattice.module_generators())
    return lattice.primitive_isotropic_subobject(basis_elements[0], basis_elements[2])


def _second_representative_of_the_first_class(lattice):
    r"""Return $\mathbb{Z}e + \mathbb{Z}\bar\alpha$, Sterk's second vector for cusp four.

    H. Sterk, Math. Z. 207 (1991), (4.3.8): $2e' + f' + \bar\alpha_1$ with $\bar\alpha_1$
    the $(-8)$-vector of (4.3.4), read in the library's basis.
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
    return lattice.primitive_isotropic_subobject(e, alpha)


def test_the_family_reaches_every_liftable_plane_action_class() -> None:
    r"""At both representatives the family's classes contain the liftable ones.

    The liftable classes are read off the block equations, so they are the plane actions
    the parabolic can exhibit; the family's classes are the ones it does exhibit.  The
    containment is the plane half of "the family's image is $M$", and at these planes it
    holds although neither set is all of $\GL_2(\mathbb{F}_2)$.
    """
    lattice = NamedLattices.TEn
    split = _plane_of_the_first_class(lattice)
    nonsplit = _second_representative_of_the_first_class(lattice)

    assert split.liftable_plane_action_classes() <= split.plane_action_class_image()
    assert nonsplit.liftable_plane_action_classes() <= nonsplit.plane_action_class_image()


def test_the_public_stabilizer_call_returns_the_parabolic_family() -> None:
    r"""`setwise_stabilizer` answers at the representative that does not split.

    The call is the one the cusp data is read through.  Its members must be isometries of
    $T_{\mathrm{En}}$ carrying the plane onto itself, and the family must come back rather
    than the construction being abandoned for a route that does not return here.
    """
    lattice = NamedLattices.TEn
    plane = _second_representative_of_the_first_class(lattice)
    ambient = lattice.Aut()
    family = ambient.stabilizer(plane, action="setwise").group_generators()

    assert family
    assert all(member.parent() is ambient for member in family)
    assert all(plane.stabilizes(member) for member in family)
