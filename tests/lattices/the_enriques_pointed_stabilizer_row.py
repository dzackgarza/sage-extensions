r"""The pointed stabilizer rows of the Enriques period lattice, in the rows tier.

This is the red of #603's pointed call, and it is not collected by pytest: its
file name does not begin with ``test_``.  Its tier is the **rows tier** -- a call
the construction answers in 12 s at the first cusp, above the 20 s per-test gate
(``sage_extensions.testing.suite_budget``), so it belongs in the job that reports
later and not in the per-test gate, as ``tests/coble_kernel_plane_rows.py`` and
the other row scripts do.

**What it shows.**  At `41f21a69` the call below does not return: the pointed
marking at an isotropic vector was handed to `sage-indefinite-port`, which was
still inside the stabilizer computation when stopped at 400 s
(``results/issue603-acceptance.md``).  With the rank-one parabolic's family and
Schreier's transversal the row at `L_1` returns and reproduces the card's number.

**The card.**  `N = U + U(2) + E8(-2)` is the Enriques period lattice, card
``029J``.  Its ``O`` row cites the two `O(N)`-orbits of primitive isotropic lines
"`L_1 = Ze_1` and `L_2 = Ze_3`, with images of their stabilizers in the
discriminant group of index 1 and 527" (Dutour Sikirić--Hulek,
arXiv:2302.01679v2, section 3.6, p. 22), and its ``Otilde+`` row states the same
split as orbit lengths, which ``card_line_orbit_lengths`` reads by tag.  The
stabilizer of the *line* `L_i` is the pointed family at its generator together
with `-id`, which negates the generator and fixes every line, so the index of
their image in the finite `O(A_N)` is the card's.

**Only `L_1` is a row here, and the reason is the next repair.**  `L_2`'s index,
527, is the discriminating one -- a family generating everything else gives the
index 1 of `L_1` too -- and the pointed construction does not reach it at a cost:
`L_2`'s generator has divisibility 2, its `K_I` has rank 10, and `O(K_I)`'s own
generating family is the indefinite port's there, so the call was still inside it
at 400 s in two runs.  The row is offered per cusp (`--cusp L_2`) so that the
measurement can be reproduced, and the card comparison stays narrow until that
recursion is owned.

    python3 tests/lattices/the_enriques_pointed_stabilizer_row.py
    python3 tests/lattices/the_enriques_pointed_stabilizer_row.py --cusp L_2
"""

from __future__ import annotations

import argparse
import time

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.lattice_database import card_line_orbit_lengths

# The two cusps the card cites, by the library's own labels for DSH's e_1 and e_3.
CUSPS = {
    "L_1": 0,
    "L_2": 2,
}


def pointed_generators(lattice, vector):
    r"""The library's generators of the stabilizer of ``vector`` in ``O(L)``."""
    return tuple(lattice.Aut().stabilizer(vector).group_generators())


def run(cusp: str) -> None:
    r"""Assert the pointed row at one cusp against the card's cited index."""
    lattice = NamedLattices.TEn
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[CUSPS[cusp]])
    orthogonal = lattice.Aut()
    discriminant = lattice.discriminant_representation()
    finite = discriminant.codomain()
    stated = sorted(int(length) for length in card_line_orbit_lengths("029J", "Otilde+"))
    reversing = orthogonal(lambda label: -lattice.module_generator(label))

    name = "L_1 = Ze_1" if cusp == "L_1" else "L_2 = Ze_3"
    assert lattice.q(vector) == ZZ(0), f"{name} must be isotropic"
    assert vector.is_primitive() is True, f"{name} must be primitive"
    assert reversing(vector) == -vector, "-id must negate the generator"

    start = time.monotonic()
    family = pointed_generators(lattice, vector)
    elapsed = time.monotonic() - start
    assert family, f"the pointed family at {name} is empty"
    assert all(generator(vector) == vector for generator in family), (
        f"a pointed family member at {name} does not fix it"
    )

    images = tuple(discriminant(generator) for generator in family) + (discriminant(reversing),)
    image = finite.subgroup(images)
    index = finite.cardinality().finite_value() // image.cardinality().finite_value()
    print(f"{name}: {len(family)} generators in {elapsed:.1f} s, stabilizer image index {index}")
    print(f"card 029J's cited indices: {stated}")
    assert index in stated, f"the card cites {stated}, and the pointed row gives {index}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cusp", choices=tuple(CUSPS), default="L_1")
    run(parser.parse_args().cusp)
