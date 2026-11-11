r"""The Enriques line rows are read from card 029J by tag, totals and per-orbit splits.

`029J`'s `Otilde+` row is the one #310's `Otilde(T_En)^+` line row is compared with: 528
primitive isotropic lines and 24242 primitive isotropic planes for `Otilde^+(N)` on
`N = U + U(2) + E8(-2)`, "the space M~_En = Otilde^+(N)\D_N ... has 528 0-dimensional cusps
(isotropic lines) and 24242 1-dimensional cusps (isotropic planes); under O^+_10(F_2) the 528
lines fall in two orbits, of lengths 527 and 1" (D. Dutour Sikirić, K. Hulek, *Moduli of
polarised Enriques surfaces — computational aspects*, arXiv:2302.01679v2, section 3.6, p. 22).

The card states a row's total as a structured field and the split of that total in the row's
own citation.  `card_line_orbit_row` reads the field, `card_line_orbit_lengths` reads the
citation, and the reading is checked against the field it belongs to.  Neither number is typed
here: every one is read from the digest at the pinned database commit.

The card also states the same rows for two Scattone lattices, where the line row is stated
without a plane count (`6JRX`'s `Otilde+`), so a reader that only knows plane rows cannot see
it at all.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_the_otilde_plus_line_row_and_its_split_come_from_the_card() -> None:
    r"""`Otilde+` states 528 lines in two orbits, and the two are the `O`-orbits.

    The `O` row of the same card states the number of `O(N)`-orbits of primitive isotropic
    lines, which the `Otilde+` sentence calls the two orbits the 528 fall in: so the count of
    the split and the `O` row must agree, and the lengths must add up to the `Otilde+` total.
    """
    total = card_line_orbit_row("029J", "Otilde+")
    lengths = card_line_orbit_lengths("029J", "Otilde+")
    o_orbits = card_line_orbit_row("029J", "O")

    assert sum(lengths) == total
    assert sum(1 for _ in lengths) == o_orbits
    assert all(length > 0 for length in lengths)


def test_the_plane_row_of_the_same_card_keeps_its_own_split() -> None:
    r"""The plane row's split is read from the same citation block and sums to its total."""
    total = card_plane_orbit_row("029J", "Otilde+")
    lengths = card_plane_orbit_lengths("029J", "Otilde+")

    assert sum(lengths) == total
    assert max(lengths) > min(lengths)


def test_a_line_row_stated_without_planes_is_still_read() -> None:
    r"""`6JRX` states `Otilde+` as one line and no plane row, and both readers say so.

    This is the row the digest used to drop: `plane_orbits` kept only group rows that state
    ``planes``, and `6JRX`'s `Otilde+` states ``constant`` alone.
    """
    assert card_line_orbit_row("6JRX", "Otilde+") == card_line_orbit_row("6JRX", "O+")
    with pytest.raises(KeyError):
        card_plane_orbit_row("6JRX", "Otilde+")
