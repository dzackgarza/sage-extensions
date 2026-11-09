r"""The unpolarized Enriques rows of card ``029J``, through the public orbit calls.

``dzackgarza/lattice-database``, tag ``029J`` -- the Enriques period lattice
$N = U \oplus U(2) \oplus E_8(-2) \cong \mathrm{I}_{2,10}(2)$, rank 12,
signature $(2,10)$, $|\det| = 1024$ -- states its rows under
``integral.primitive_orbits``, keyed by arithmetic group, with the paper on
every row.  ``constant`` is the number of orbits of primitive isotropic lines
(the zero-dimensional Baily--Borel boundary components) and ``planes`` the
number of orbits of primitive isotropic planes (the one-dimensional ones)::

    O           constant: 2      planes: 2
    gamma-en-2  constant: 5      planes: 9
    Otilde+     constant: 528    planes: 24242

The ``O`` row is H. Sterk, *Compactifications of the period space of Enriques
surfaces, Part I*, Math. Z. 207 (1991), 1--36, Propositions 4.5 (p. 28) and
4.6 (p. 29): two orbits of primitive isotropic lines and two of primitive
isotropic planes modulo $O(N)$, realised on the lines $L_1 = \mathbb{Z} e_1$
and $L_2 = \mathbb{Z} e_3$ and the planes $P_1 = \mathbb{Z} e_1 + \mathbb{Z} e_3$
and $P_2 = \mathbb{Z}(2 e_1 + 2 e_2 + w) + \mathbb{Z} e_3$ with $w$ of norm $4$
in $E_8$.  The ``gamma-en-2`` row is Sterk's Proposition 4.2.3 with
Remark 4.2.4, p. 16 (five $0$-cusps of $\Gamma_{En,2}$) and
Alexeev--Engel--Garza--Schaffler, *Compact moduli of Enriques surfaces of
degree 2*, Nagoya Math. J. 249 (2025), §3.3, p. 590 ("There are five $0$-cusps
... There are also 9 distinct $1$-cusps"); the ``Otilde+`` row is
D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces --
computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679,
§3.6 (the Tits building), p. 22, for
$\widetilde{O}^+(N) \backslash D_N$.

Each test below reads one row of the card and compares it with one public
call.  No count is derived here: the numbers asserted are the card's, and the
call is what has to agree.
"""

from sage_extensions.all import *

# The card's rows, (row tag, lines, planes), read from tag 029J.
_ROWS = (
    ("O", 2, 2),
)


def _primitive_isotropic_rank_two(planes, lattice) -> None:
    r"""Every returned plane is a primitive, totally isotropic rank-two subobject."""
    for plane in planes:
        assert plane.module_rank() == cardinal(2)
        assert plane.is_primitive() is True
        labels = plane.module_generating_set()
        for left in labels:
            for right in labels:
                assert lattice.b(
                    plane.inclusion()(plane.module_generator(left)),
                    plane.inclusion()(plane.module_generator(right)),
                ) == ZZ(0)


def _primitive_isotropic_lines(lines, lattice) -> None:
    r"""Every returned line is a primitive isotropic rank-one subobject."""
    for line in lines:
        assert line.module_rank() == cardinal(1)
        assert line.is_primitive() is True
        for label in line.module_generating_set():
            assert lattice.q(line.inclusion()(line.module_generator(label))) == ZZ(0)


def test_the_o_row_states_two_primitive_isotropic_lines() -> None:
    r"""``029J``, row ``O``: ``constant: 2`` primitive isotropic lines modulo $O(N)$."""
    tag, expected_lines, _planes = _ROWS[0]
    lattice = NamedLattices.TEn
    lines = lattice.Aut().isotropic_orbit_representatives(1)

    assert lines.cardinality() == cardinal(expected_lines)
    _primitive_isotropic_lines(lines, lattice)


def test_the_o_row_states_two_primitive_isotropic_planes() -> None:
    r"""``029J``, row ``O``: ``planes: 2`` primitive isotropic planes modulo $O(N)$."""
    tag, _lines, expected_planes = _ROWS[0]
    lattice = NamedLattices.TEn
    planes = lattice.Aut().isotropic_orbit_representatives(2)

    assert planes.cardinality() == cardinal(expected_planes)
    _primitive_isotropic_rank_two(planes, lattice)
