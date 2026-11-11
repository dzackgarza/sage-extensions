r"""The setwise stabilizer of a primitive isotropic plane of $T_{\mathrm{En}}$ (#295).

The consumer is the plane half of #286: the divided-class plane call of #321 takes
generators of $G_x = \mathrm{Stab}_{O(L)}(P)$, and the natural source of them is
`Isom(L).stabilizer(P, action="setwise")`.  On $7858c09d97$ and on $d35c72c7$
that call returns for the Coble ambient $B = U \oplus U \oplus I_{0,7}$ but not
for the Enriques period lattice: the port's rank-two branch converts each
rational generator of its integral-structure action to an integral isometry by
`integral_restriction`, and on $T_{\mathrm{En}}$ that conversion did not return:
three periodic faulthandler dumps of one run
(`.tmp/issue295e-stack.log`) name
`isotropic_induction.py:304 _stabilizer_generators -> lattices.py:3202
integral_isometry -> lattice_morphisms.py:1549 integral_restriction -> ... ->
module_morphisms.py:1117 _call_`, so the wall is the per-generator rationality
check of the port's rational stabilizer generators, not the port's orbit
computation.

What is asserted, and what is not:

* every generator the call returns is an isometry of $T_{\mathrm{En}}$ and
  carries the plane onto itself;
* every generator has a discriminant image in $O(q_{T_{\mathrm{En}}})$;
* the plane-orbit row of card `029J` is reproduced when those generators are
  supplied as the stabilizer of the first representative.  The row is read from
  `tests/cards/lattice-database-enriques.json` by tag, and its citation is the
  statement the index agreement is measured against: the images of the
  stabilizers of Sterk's $P_1$ and $P_2$ have index $527 = 17 \cdot 31$ and
  $23715 = 3^2 \cdot 5 \cdot 17 \cdot 31$ in $\rho(O(T_{\mathrm{En}}))$
  (D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces --
  computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679,
  §3.6 (the Tits building), p. 22).  The call closes the sandwich
  $|Q \cdot J_x| \le [Q : \rho(G_x)] \le [Q : \langle\rho(h)\rangle]$ per
  representative, so a returned count is a count of planes only if the supplied
  generators have the stabilizer's own image.

No count of this module's own computation is asserted: the only number here is
the card's.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _enriques_plane_representatives(lattice):
    r"""Sterk's two $O(T_{\mathrm{En}})$-orbit representatives of primitive isotropic planes.

    $P_1 = \mathbb{Z} e_1 + \mathbb{Z} e_3$ and
    $P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z} e_3$ with $w$ a vector of
    $E_8(-2)$ of norm $-8$: H. Sterk, *Compactifications of the period space of
    Enriques surfaces, Part I*, Math. Z. 207 (1991), Proposition 4.6 (p. 29), in
    the standard bases $(e_1, e_2)$ of $U$ and $(e_3, e_4)$ of $U(2)$ that
    Dutour Sikirić--Hulek, §3.6, p. 22, use.
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


def test_every_setwise_stabilizer_generator_is_an_isometry_preserving_the_plane() -> None:
    r"""The public call returns generators of the parabolic at $P_1$, one by one checked.

    Each generator is an isometry of $T_{\mathrm{En}}$, carries $P_1$ onto
    itself, and passes through
    $T_{\mathrm{En}}.\mathrm{discriminant\_representation}()$.  The generators
    are the unipotent radical's Eichler transvections, the reflections of the
    Levi factor on $P_1^\perp/P_1$ and the integral Levi lifts of the elementary
    matrices of $GL(P_1)$.
    """
    lattice = NamedLattices.TEn
    plane = _enriques_plane_representatives(lattice)[0]
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


def test_the_card_029J_plane_row_survives_the_supplied_stabilizer_generators() -> None:
    r"""Card `029J`'s $\widetilde{O}^+$ plane row, with the first stabilizer supplied.

    $\widetilde{O}^+(T_{\mathrm{En}}) = \ker\rho \cap O^+$ has trivial
    discriminant image, so every divided class point is its own orbit and the
    row is the sum of the two ambient orbit sizes, $24242$ (Dutour
    Sikirić--Hulek, §3.6, p. 22).  Supplying generators of the stabilizer of
    $P_1$ closes the sandwich on that representative -- the call raises rather
    than returning a count if $[\rho(O) : \langle\rho(h)\rangle]$ exceeds the
    number of class points in $P_1$'s orbit -- and the second representative is
    closed by the published indices, so the row is the card's.
    """
    lattice = NamedLattices.TEn
    first, second = _enriques_plane_representatives(lattice)
    group = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    assert group.contains_character_kernel()

    family = lattice.Aut().stabilizer(first, action="setwise").group_generators()
    assert family.cardinality() != cardinal(0)

    orbits = group.isotropic_plane_orbits(
        (first, second), stabilizer_generators={0: tuple(family)}
    )

    assert orbits.cardinality() == cardinal(card_plane_orbit_row("029J", "Otilde+"))
    for orbit in orbits:
        assert orbit.representative().is_primitive() is True
