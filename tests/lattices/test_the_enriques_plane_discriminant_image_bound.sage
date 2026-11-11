r"""The discriminant image of an Enriques plane's stabilizer, bounded from both sides (#331).

The plane-orbit call of #286 consumes $\rho(G_P) \subseteq O(q_{T_{\mathrm{En}}})$, not a
generating set of $G_P$.  Two subgroups bound it without any generation claim:

* **upper**: every $g \in \mathrm{Stab}_{O(L)}(P)$ permutes the divided discriminant
  classes $[u/\mathrm{div}(u)]$ of the plane's primitive directions, so
  $\rho(G_P) \subseteq \mathrm{Stab}_{O(q)}(D(P))$, whose index in $O(q)$ is the size
  of the $O(q)$-orbit of $D(P)$;
* **lower**: the images of the generators `parabolic_stabilizer_generators` returns,
  each of them an isometry of $T_{\mathrm{En}}$ carrying $P$ onto itself.

The two plane representatives are Sterk's $P_1$ and $P_2$ (H. Sterk,
*Compactifications of the period space of Enriques surfaces, Part I*,
Math. Z. 207 (1991), Proposition 4.6, p. 29).  Dutour Sikirić--Hulek,
arXiv:2302.01679v2, section 3.6 (the Tits building), p. 22, state the indices of
their stabilizer images in the discriminant group: $527$ for $P_1$ and
$23715 = 3^2\cdot5\cdot17\cdot31$ for $P_2$.  Those two numbers are card `029J`'s
cited values and are read here by tag, together with the two plane rows the card
states: two $O$-orbits of planes and $24242 = 527 + 23715$ one-dimensional cusps
under $\widetilde{O}^+$.

The orbit sizes are computed from the permutation action of $O(q)$ on its own
discriminant group, not taken from the page; the test compares them with the
card's rows by tag.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _representatives(lattice):
    r"""Sterk's two primitive isotropic planes $P_1$ and $P_2$ of $T_{\mathrm{En}}$.

    $P_1 = \mathbb{Z} e_1 + \mathbb{Z} e_3$ and
    $P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z} e_3$ with $w$ a vector of
    $E_8(-2)$ of norm $-8$: H. Sterk, Math. Z. 207 (1991), Proposition 4.6
    (p. 29), in the bases $(e_1, e_2)$ of $U$ and $(e_3, e_4)$ of $U(2)$ used by
    Dutour Sikirić--Hulek, section 3.6, p. 22.
    """
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    assert lattice.q(w) == ZZ(-8)
    return (
        lattice.primitive_isotropic_subobject(first, third),
        lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third),
    )


def test_the_plane_classes_and_their_cusp_count_are_card_029J_s_rows() -> None:
    r"""Two $O$-orbits of planes, and $527 + 23715$ one-dimensional cusps.

    $527$ and $23715$ are the indices Dutour Sikirić--Hulek, section 3.6, p. 22,
    give for the stabilizer images of $P_1$ and $P_2$ in the discriminant group;
    $24242$ is card `029J`'s $\widetilde{O}^+$ plane row, read by tag, and it is
    their sum.
    """
    lattice = NamedLattices.TEn
    first, second = _representatives(lattice)

    index_first = first.stabilizer_discriminant_index()
    index_second = second.stabilizer_discriminant_index()

    assert index_first == 527
    assert index_second == 23715
    assert index_first + index_second == card_plane_orbit_row("029J", "Otilde+")
    assert card_plane_orbit_row("029J", "O") == cardinal(2)

