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
cited values, and they are read here by tag from the row's own `orbit_lengths`
field, which `dzackgarza/lattice-database` d6a5393 states for both the `O` and
the $\widetilde{O}^+$ rows beside the row total ($24242$ one-dimensional cusps
under $\widetilde{O}^+$, two $O$-orbits of planes).  Nothing in this module types
either number, and nothing parses a sentence for it.

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
    give for the stabilizer images of $P_1$ and $P_2$ in the discriminant group.
    Card `029J` states them in its $\widetilde{O}^+$ row as the lengths of the two
    orbits of its $24242$ planes; the two computed indices are compared with that
    stated pair by tag, and their sum with the card's row total.
    """
    lattice = NamedLattices.TEn
    first, second = _representatives(lattice)

    index_first = first.stabilizer_discriminant_index()
    index_second = second.stabilizer_discriminant_index()
    stated = card_plane_orbit_lengths("029J", "Otilde+")

    assert sorted([int(index_first), int(index_second)]) == sorted(stated)
    assert index_first + index_second == card_plane_orbit_row("029J", "Otilde+")
    assert card_plane_orbit_row("029J", "O") == cardinal(2)



def test_the_plane_that_does_not_split_has_an_exact_discriminant_image() -> None:
    r"""At $P_2$ the image of the returned generators is the whole bound.

    $\rho(G_{P_2}) \subseteq \mathrm{Stab}_{O(q)}(D(P_2))$ of order
    $|O(q)|/23715 = 1981808640$, and the images of the generators
    `parabolic_stabilizer_generators` returns generate a subgroup of that order.
    Equal orders decide the image without any claim that those generators
    generate $G_{P_2}$ itself, which stays open
    (`parabolic_obstruction`).  The index $23715$ is card `029J`'s cited value for
    $P_2$ (Dutour Sikirić--Hulek, section 3.6, p. 22), read here by tag as the
    larger of the two lengths the card states for its $\widetilde{O}^+$ plane
    orbits: the card's $O$ row names $P_1$ before $P_2$ and gives the images'
    indices in that order, and $P_2$'s is the larger of the pair.
    """
    lattice = NamedLattices.TEn
    _first, second = _representatives(lattice)

    upper, lower = second.stabilizer_discriminant_image_orders()

    assert second.stabilizer_discriminant_index() == max(
        card_plane_orbit_lengths("029J", "Otilde+")
    )
    assert upper == lower
    assert second.stabilizer_discriminant_image_is_exact() is True
    assert second.stabilizer_discriminant_image_index() == 1
