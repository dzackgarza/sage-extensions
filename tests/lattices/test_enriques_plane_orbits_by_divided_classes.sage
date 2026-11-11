r"""The Enriques plane rows of the arithmetic-group cards, by the divided-class orbit call.

Two rows, read by tag:

* ``dzackgarza/lattice-database`` tag ``029J`` (the Enriques period lattice
  $N = U \oplus U(2) \oplus E_8(-2)$, rank 12, signature $(2,10)$,
  $\lvert\det\rvert = 1024$), ``integral.primitive_orbits.gamma-en-2.planes``
  $= 9$;
* tag ``otilde-plus-t-en`` (the arithmetic group $\widetilde{O}^+(N)$, listed in
  ``029J``'s ``arithmetic_groups`` index, whose row is
  ``integral.primitive_orbits.Otilde+.planes`` on the same card) $= 24242$.

The call compared with each row is
``<group>.isotropic_plane_orbits(representatives)``: the subgroup's orbits of
primitive isotropic planes, computed as the orbits on the finite divided-class
sets of the two $O(N)$-orbit representatives.  The representatives are Sterk's,
*Compactifications of the period space of Enriques surfaces, Part I*,
Math. Z. 207 (1991), Proposition 4.6 (p. 29): $P_1 = \mathbb{Z} e_1 +
\mathbb{Z} e_3$ and $P_2 = \mathbb{Z}(2 e_1 + 2 e_2 + w) + \mathbb{Z} e_3$ with
$w$ of norm $-8$ in $E_8(-2)$, in the standard bases $(e_1, e_2)$ of $U$ and
$(e_3, e_4)$ of $U(2)$ that Dutour Sikirić--Hulek, *Moduli of polarised
Enriques surfaces -- computational aspects*, J. London Math. Soc. 110 (2024),
arXiv:2302.01679, §3.6 (the Tits building), p. 22, use.  The numbers asserted
below are the cards', never the computation's own output.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _enriques_plane_representatives(lattice):
    r"""Sterk's two $O(N)$-orbit representatives of primitive isotropic planes.

    ``(e_1, e_2)`` is a standard basis of $U$ -- both isotropic, pairing one --
    and ``(e_3, e_4)`` of $U(2)$, pairing two, so an isotropic generator of each
    summand spans with the other a primitive totally isotropic plane.  ``w`` is
    the sum of two orthogonal simple roots of $E_8(-2)$, of norm $-8$; then
    $2 e_1 + 2 e_2 + w$ has $(2 e_1 + 2 e_2)^2 + w^2 = 8 - 8 = 0$ and is
    primitive.
    """
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    assert lattice.q(w) == ZZ(-8)
    return (
        lattice.primitive_isotropic_subobject(first, third),
        lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third),
    )


def _divided_classes(lattice, plane):
    r"""The divided discriminant classes $[u/\mathrm{div}(u)]$ of a plane, with the zero class."""
    inclusion = plane.inclusion()
    basis = [inclusion(vector) for vector in inclusion.domain().module_generators()]
    return tuple(
        [lattice.discriminant_group().zero()]
        + [lattice.divided_discriminant_class(vector) for vector in (basis[0], basis[1], basis[0] + basis[1])]
    )


def _assert_primitive_isotropic_plane(plane, lattice) -> None:
    r"""``plane`` is a primitive, totally isotropic rank-two subobject of ``lattice``."""
    assert plane.module_rank() == cardinal(2)
    assert plane.is_primitive() is True
    for left in plane.module_generating_set():
        for right in plane.module_generating_set():
            assert lattice.b(
                plane.inclusion()(plane.module_generator(left)),
                plane.inclusion()(plane.module_generator(right)),
            ) == ZZ(0)


def _gamma_en_2():
    r"""``Gamma_{En,2}``, Alexeev--Engel--Garza--Schaffler, Nagoya Math. J. 259 (2025), Def. 2.6.

    The image in $O(T_{\mathrm{En}})$ of $\{g \in O(L) : g I_{\mathrm{En}} =
    I_{\mathrm{En}} g,\ g(h) = h\}$ at the degree-two polarization $h$, built by
    the coinvariant construction rather than from a description of its image in
    $O(q)$.
    """
    invariant = Involutions.I_En.invariant_lattice()
    basis_elements = list(invariant.module_generators())
    marks = []
    for left, left_vector in enumerate(basis_elements):
        for right, right_vector in enumerate(basis_elements):
            if right <= left:
                continue
            if (
                invariant.q(left_vector) == ZZ.zero()
                and invariant.q(right_vector) == ZZ.zero()
                and invariant.b(left_vector, right_vector) != ZZ.zero()
            ):
                marks.append((left, right, invariant.b(left_vector, right_vector)))
    left, right, _pairing = next(entry for entry in marks if entry[2] == ZZ(2))
    h_invariant = basis_elements[left] + basis_elements[right]
    polarized = Involutions.I_En.polarized(invariant.inclusion()(h_invariant))
    return polarized.coinvariant_extension_subgroup()


def _otilde_plus():
    r"""$\widetilde{O}^+(T_{\mathrm{En}}) = \ker \rho \cap O^+(T_{\mathrm{En}})$."""
    lattice = NamedLattices.TEn
    return lattice.stable_orthogonal_group().intersection(lattice.O_plus())


def test_the_two_representatives_are_primitive_isotropic_planes_with_different_classes() -> None:
    r"""Sterk's $P_1$ and $P_2$ are primitive isotropic planes with different class sets.

    The hypothesis of the row tests is that the representatives are what the
    citation says they are, so it is checked directly: both are primitive
    totally isotropic rank-two subobjects, and their divided discriminant class
    sets differ, which is why they lie in different $O(N)$-orbits.
    """
    lattice = NamedLattices.TEn
    first, second = _enriques_plane_representatives(lattice)
    _assert_primitive_isotropic_plane(first, lattice)
    _assert_primitive_isotropic_plane(second, lattice)
    assert _divided_classes(lattice, first) != _divided_classes(lattice, second)


def test_the_gamma_en_2_plane_row_is_nine() -> None:
    r"""``029J``, row ``gamma-en-2``: ``planes: 9`` primitive isotropic planes modulo $\Gamma_{En,2}$.

    $\Gamma_{En,2}$ is Alexeev--Engel--Garza--Schaffler, Def. 2.6, with
    $F_{\mathrm{En},2} = \mathbb{D}(T_{\mathrm{En}})/\Gamma_{\mathrm{En},2}$ of
    Def. 2.7; Cor. 3.12 describes its boundary, and the nine
    one-dimensional cusps are the count stated in §3.3, p. 590.
    """
    lattice = NamedLattices.TEn
    group = _gamma_en_2()
    assert group.contains_character_kernel()

    orbits = group.isotropic_plane_orbits(_enriques_plane_representatives(lattice))

    assert orbits.cardinality() == cardinal(9)


def test_the_otilde_plus_plane_row_is_24242() -> None:
    r"""``otilde-plus-t-en``: ``planes: 24242`` primitive isotropic planes modulo $\widetilde{O}^+(N)$.

    The row is Dutour Sikirić--Hulek, §3.6, p. 22: the space
    $\widetilde{\mathcal{M}}_{\mathrm{En}} = \widetilde{O}^+(N) \backslash
    \mathbb{D}_N$ has $528$ zero-dimensional and $24242$ one-dimensional cusps,
    and the $24242$ isotropic planes fall into the two
    $O^+_{10}(\mathbb{F}_2)$-orbits of lengths $527$ and $23715$.  This
    subgroup has trivial discriminant image, so each class point is its own
    orbit.
    """
    lattice = NamedLattices.TEn
    group = _otilde_plus()
    assert group.contains_character_kernel()

    orbits = group.isotropic_plane_orbits(_enriques_plane_representatives(lattice))

    assert orbits.cardinality() == cardinal(24242)


def test_a_split_orbit_realizes_its_plane() -> None:
    r"""A $\Gamma_{En,2}$-orbit away from the representatives is realized by a plane.

    Nine orbits come out of two ambient ones, so most of them are reached by an
    isometry rather than being the representative itself.  The realized plane is
    checked to be a primitive totally isotropic rank-two subobject of
    $T_{\mathrm{En}}$ whose divided class set differs from $P_1$'s, and the
    orbit of $P_1$ itself reports $P_1$'s own class set.
    """
    lattice = NamedLattices.TEn
    group = _gamma_en_2()
    representatives = _enriques_plane_representatives(lattice)
    orbits = tuple(group.isotropic_plane_orbits(representatives))

    assert orbits[0].representative().inclusion().codomain() is lattice
    assert orbits[0].divided_classes() == _divided_classes(lattice, representatives[0])
    transported = orbits[4].representative()
    _assert_primitive_isotropic_plane(transported, lattice)
    assert _divided_classes(lattice, transported) != _divided_classes(lattice, representatives[0])
