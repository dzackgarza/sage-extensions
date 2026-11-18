r"""The pointed stabilizer row of the Enriques period lattice, in the rows tier.

This is the red of #603's pointed call, and it is not collected by pytest: its
file name does not begin with ``test_``.  Its tier is the **rows tier** -- a call
the construction answers in 12 to 23 s, above the 20 s per-test gate
(``sage_extensions.testing.suite_budget``), so it belongs in the job that reports
later and not in the per-test gate, as ``tests/coble_kernel_plane_rows.py`` and
the other row scripts do.

**What it shows.**  At `41f21a69` the call below does not return: the pointed
marking at an isotropic vector was handed to `sage-indefinite-port`, which was
still inside the stabilizer computation when stopped at 400 s
(``results/issue603-acceptance.md``).  With the rank-one parabolic's family and
Schreier's transversal it returns 25 members in 12.2 s and the assertions hold.

**The card.**  `N = U + U(2) + E8(-2)` is the Enriques period lattice, card
``029J``.  Its ``O`` row cites the two `O(N)`-orbits of primitive isotropic lines
"`L_1 = Ze_1` and `L_2 = Ze_3`, with images of their stabilizers in the
discriminant group of index 1 and 527" (Dutour Sikirić--Hulek,
arXiv:2302.01679v2, section 3.6, p. 22).  The stabilizer of the *line* `L_1` is
the pointed family at `e_1` together with `-id`, which negates `e_1` and fixes
every line, so the image of the two is the card's index-1 stabilizer image: its
index in the finite `O(A_N)` is 1.  The card value is read by tag; no number in
this file is typed except the index the assertion compares against, which is the
card's own.

    python3 tests/lattices/the_enriques_pointed_stabilizer_row.py
"""

from __future__ import annotations

import time

from sage_extensions.all import *  # noqa: F401,F403


def pointed_generators(lattice, vector):
    r"""The library's generators of the stabilizer of ``vector`` in ``O(L)``."""
    return tuple(lattice.Aut().stabilizer(vector).group_generators())


def run() -> None:
    r"""Assert the pointed row at `L_1 = Ze_1` and report what it measured."""
    lattice = NamedLattices.TEn
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[0])
    orthogonal = lattice.Aut()
    discriminant = lattice.discriminant_representation()
    finite = discriminant.codomain()

    assert lattice.q(vector) == ZZ(0), "e_1 must be isotropic for the row to be the pointed one"
    assert vector.is_primitive() is True, "e_1 must be primitive"

    start = time.monotonic()
    family = pointed_generators(lattice, vector)
    elapsed = time.monotonic() - start
    assert family, "the pointed family at e_1 is empty"
    assert all(generator(vector) == vector for generator in family), (
        "a pointed family member does not fix e_1"
    )

    reversing = orthogonal(lambda label: -lattice.module_generator(label))
    assert reversing(vector) == -vector, "-id must negate e_1"

    images = tuple(discriminant(generator) for generator in family) + (discriminant(reversing),)
    image = finite.subgroup(images)
    index = finite.cardinality().finite_value() // image.cardinality().finite_value()

    print(f"pointed family at e_1: {len(family)} generators in {elapsed:.1f} s")
    print(f"index of the line stabilizer's discriminant image in O(A_N): {index}")
    assert index == 1, f"the card cites index 1 for L_1 = Ze_1, and the image has index {index}"


if __name__ == "__main__":
    run()
