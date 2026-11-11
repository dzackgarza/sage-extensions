r"""The setwise stabilizer of a primitive isotropic plane of $T_{\mathrm{En}}$ that does not split (#326).

Sterk's two representatives $P_1 = \mathbb{Z}e_1 + \mathbb{Z}e_3$ and
$P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z}e_3$ of the orbits of primitive
isotropic planes of $T_{\mathrm{En}}$ behave differently for the parabolic
construction of `isotropic_parabolics`: $P_1$ splits off the lattice,
$P_1 \perp \langle e_2, e_4\rangle \perp E_8(-2)$, and $P_2$ does not.  The
difference is the block $K = b(U, K)$ of the block form, which vanishes exactly
in the split case; for $P_2$ no complement of $P_2^\perp$ is orthogonal to
$P_2^\perp/P_2$, so `splitting_complement` answers ``None``.

What is asserted, and where it comes from.  An isometry preserving a primitive
isotropic plane has, in a basis $(U \mid P \mid K)$ with $U$ a $\mathbb{Z}$-complement
of $P^\perp$ and $K$ a basis of $P^\perp/P$ lifted into $P^\perp$, the block form

$$g = \begin{pmatrix} P_1 & P_2 & P_3\\ 0 & Q_1 & 0\\ 0 & Q_2 & Q_3\end{pmatrix},
\qquad J = P_1 J Q_1^t,\quad K = P_1 J Q_2^t + P_1 K Q_3^t + P_3 A Q_3^t,$$

with the third block equation a linear system for $P_2$ that always has a
rational solution and an integral one only on a finite-index subgroup of plane
actions: D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces
-- computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2,
**Theorem 4.9** (`theorem_isotropic_k_planes`), proof, printed **p. 22**, in
their row-vector convention.  This module asserts that the plane's own lift
family is nonempty at $P_2$ and that every generator the public call returns is
an isometry of $T_{\mathrm{En}}$, carries $P_2$ onto itself, and has a
discriminant image; it asserts no count and no index of its own computation.

Before this unit the lift family at $P_2$ was empty: `levi_lift_generators`
returned nothing whenever the plane did not split, so the public call kept the
indefinite port's route, which on the recorded runs did not return (#295,
`results/issue295-enriques-plane-parabolic.md`; `TRAPS.md`).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _enriques_plane_representatives(lattice):
    r"""Sterk's two $O(T_{\mathrm{En}})$-orbit representatives of primitive isotropic planes.

    $P_1 = \mathbb{Z} e_1 + \mathbb{Z} e_3$ and
    $P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z} e_3$ with $w$ a vector of
    $E_8(-2)$ of norm $-8$: H. Sterk, *Compactifications of the period space of
    Enriques surfaces, Part I*, Math. Z. 207 (1991), Proposition 4.6 (p. 29), in
    the standard bases $(e_1, e_2)$ of $U$ and $(e_3, e_4)$ of $U(2)$ that
    Dutour Sikirić--Hulek section 3.6, p. 22, use.
    """
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    assert lattice.q(w) == ZZ(-8)
    return (
        lattice.primitive_isotropic_subobject(first, third),
        lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third),
    )


def _is_an_isometry(lattice, generator) -> bool:
    r"""Whether ``generator`` preserves the form of ``lattice`` on a generating set."""
    vectors = tuple(lattice.module_generators())
    images = tuple(generator(vector) for vector in vectors)
    return all(
        lattice.b(image, other) == lattice.b(vector, source)
        for vector, image in zip(vectors, images, strict=True)
        for source, other in zip(vectors, images, strict=True)
    )


def _carries_plane_onto_itself(plane, generator) -> bool:
    r"""Whether ``generator`` maps the plane into itself by an invertible endomorphism.

    $\iota(g(P)) \subseteq \iota(P)$ with an invertible induced endomorphism is
    the set equality $g(P) = P$: the image is a submodule of the same rank, and
    invertibility of the induced map forces its index to be one.
    """
    inclusion = plane.inclusion()
    domain = inclusion.domain()
    labels = tuple(domain.module_generating_set())
    images = [generator(inclusion(domain.module_generator(label))) for label in labels]
    if not all(inclusion.is_in_image(image) for image in images):
        return False
    matrix_entries = [
        [int(inclusion.lift(image).to_vector()(label)) for image in images] for label in labels
    ]
    (a, b), (c, d) = matrix_entries
    return abs(a * d - b * c) == 1


def test_the_plane_that_does_not_split_has_integral_levi_lifts() -> None:
    r"""$P_2$ has no complement orthogonal to $P_2^\perp/P_2$, and still has integral lifts.

    The lift of a plane action $M$ is the block matrix of Theorem 4.9 (Dutour
    Sikirić--Hulek, arXiv:2302.01679v2, printed p. 22) solved over the integers;
    at $P_2$ the block $K = b(U, K)$ is nonzero and the $P_3$ block it forces is
    what the split case never needed.
    """
    lattice = NamedLattices.TEn
    plane = _enriques_plane_representatives(lattice)[1]
    assert plane.is_primitive() is True
    assert plane.splitting_complement() is None

    lifts = plane.levi_lift_generators()
    assert lifts != ()
    for lift in lifts:
        assert _is_an_isometry(lattice, lift) is True
        assert _carries_plane_onto_itself(plane, lift) is True


def test_the_setwise_stabilizer_of_the_plane_that_does_not_split_has_generators() -> None:
    r"""The public call at $P_2$ returns generators of the setwise stabilizer, each checked.

    Every generator is an isometry of $T_{\mathrm{En}}$, carries $P_2$ onto
    itself, and passes through
    $T_{\mathrm{En}}.\mathrm{discriminant\_representation}()$.  The generators
    are the unipotent radical's Eichler transvections, the reflections of the
    Levi factor on $P_2^\perp/P_2$, and the integral lifts of the Levi factor on
    $P_2$ -- the last the block equations of Dutour Sikirić--Hulek, Theorem 4.9,
    printed p. 22, which a plane that does not split needs with its nonzero $K$
    block.
    """
    lattice = NamedLattices.TEn
    plane = _enriques_plane_representatives(lattice)[1]
    assert plane.module_rank() == cardinal(2)
    assert plane.is_primitive() is True

    family = lattice.Aut().stabilizer(plane, action="setwise").group_generators()
    assert family.cardinality() != cardinal(0)

    orthogonal = lattice.discriminant_group().orthogonal_group()
    rho = lattice.discriminant_representation()
    for generator in family:
        assert _is_an_isometry(lattice, generator) is True
        assert _carries_plane_onto_itself(plane, generator) is True
        assert rho(generator) in orthogonal
