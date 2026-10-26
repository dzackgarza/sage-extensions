r"""Conway--Sloane local excess/oddity formula retained from the archive suite.

For odd ``p`` the local excess is ``sum n_q(q-1)+4k_p`` modulo eight; for
``p=2`` the oddity is ``sum t_q+4k_2``.  Here ``k_p`` counts antisquare
constituents.  The formula is recomputed from the canonical Jordan tuples and
compared with the owned genus value.
"""

from sage_extensions.all import *


def _local_excess_from_constituents(constituents, prime: int) -> int:
    total = 0
    antisquares = 0
    for constituent in constituents:
        valuation, dimension, sign = constituent[:3]
        scale = prime**valuation
        if valuation % 2 == 1 and sign == -1:
            antisquares += 1
        if prime == 2:
            total += constituent[4]
        else:
            total += dimension * (scale - 1)
    return (total + 4 * antisquares) % 8


def test_local_excess_matches_conway_sloane_formula() -> None:
    rows = (
        (Lattices.A1.twist(-1), 2, 1),
        (Lattices.D4.twist(-1), 2, 4),
        (Lattices.E7.twist(-1), 2, 7),
        (Lattices.E8.twist(-1), 2, 0),
        (Lattices.A2.twist(-1), 3, 6),
        (Lattices.E6.twist(-1), 3, 2),
        (Lattices.E8.twist(-1), 5, 0),
        (Lattices.U, 2, 0),
        (Lattices.U + Lattices(ZZ)([[2]]), 2, 1),
    )

    for lattice, prime, expected in rows:
        constituents = tuple(
            tuple(int(entry) for entry in constituent)
            for constituent in lattice.genus().local_symbol(prime).canonical_symbol()
        )
        assert _local_excess_from_constituents(constituents, prime) == expected
        assert lattice.genus().excess(prime) % 8 == expected
