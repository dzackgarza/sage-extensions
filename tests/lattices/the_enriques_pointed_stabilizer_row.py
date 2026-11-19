r"""The Enriques period lattice's stabilizer rows, in the rows tier.

This is #603's row work on `N = U + U(2) + E8(-2)`, card ``029J``.  It is not
collected by pytest (its name does not begin with ``test_``): the two calls below
take 0.9 s and 80.5 s, above the 20 s per-test gate
(``sage_extensions.testing.suite_budget``), so they belong in the job that reports
later, as ``tests/coble_kernel_plane_rows.py`` and the other row scripts do.

Two rows are measured, and they are different rows:

**The line's finite image.**  `finite_character_quotient` of the stable
orthogonal group `ker rho` presents the double coset space
`ker rho \ O(N) / Stab(line)` through the exact finite image, and
`isotropic_line_stabilizer_image` decides the right-hand group from the line's
own residue data -- the half-vector Eichler transvections of #325, not the
generators of `O(K_I)`.  The number of double cosets is the number of
`ker rho`-orbits inside the `O(N)`-orbit of the line, which is
`[rho(O(N)) : rho(Stab(line))]`; `rho` is onto, so that index is the card's.

**The pointed family.**  `O(N).stabilizer(e_1)` is #603's construction.  At
`L_1 = Ze_1` it returns; at `L_2 = Ze_3` it does not, its complement `K_I` having
rank 10 with `O(K_I)`'s own family the indefinite port's
(``results/issue603-the-divisible-cusp-blocker.md``).

The card is read by tag with `card_line_orbit_lengths("029J", "Otilde+")`, which
is the `Otilde+` row's own per-orbit sentence: 528 lines in two orbits of lengths
527 and 1.  The `O` row cites the same split as "images of their stabilizers in
the discriminant group of index 1 and 527" (Dutour Sikirić--Hulek,
arXiv:2302.01679v2, section 3.6, p. 22).

    python3 tests/lattices/the_enriques_pointed_stabilizer_row.py
"""

from __future__ import annotations

import time

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.lattice_database import card_line_orbit_lengths

# The two cusps the card cites, by the library's own labels for DSH's e_1 and e_3.
CUSPS = {"L_1": 0, "L_2": 2}


def pointed_generators(lattice, vector):
    r"""The library's generators of the stabilizer of ``vector`` in ``O(L)``."""
    return tuple(lattice.Aut().stabilizer(vector).group_generators())


def line_orbit_count(lattice, vector):
    r"""The number of ``ker rho``-orbits inside `O(N)`'s orbit of the line of ``vector``.

    This is `[rho(O(N)) : rho(Stab(Zv))]`, computed from the line's own residue
    data and the finite image, so it never asks `O(K_I)` for generators.
    """
    quotient = lattice.stable_orthogonal_group().finite_character_quotient()
    line = vector.sublattice()
    data = quotient.isotropic_line_stabilizer_image(line)
    if data == "NOSPLIT":
        # The sign witness proves the line's stabilizer meets every double coset.
        return 1
    return len(tuple(quotient.splitting_isometries_from_line_class(*data)))


def run() -> None:
    r"""Assert the card's two cited indices, and report the pointed family's two rows."""
    lattice = NamedLattices.TEn
    labels = tuple(lattice.module_generating_set())
    stated = sorted(int(length) for length in card_line_orbit_lengths("029J", "Otilde+"))
    orthogonal = lattice.Aut()
    reversing = orthogonal(lambda label: -lattice.module_generator(label))

    measured = {}
    for name, index in CUSPS.items():
        vector = lattice.module_generator(labels[index])
        assert lattice.q(vector) == ZZ(0), f"{name} must be isotropic"
        assert vector.is_primitive() is True, f"{name} must be primitive"
        assert reversing(vector) == -vector, "-id must negate the generator"

        start = time.monotonic()
        count = line_orbit_count(lattice, vector)
        measured[name] = count
        print(f"{name}: {count} ker-rho orbits in its O(N)-orbit, {time.monotonic() - start:.1f} s")

    print(f"card 029J's cited orbit lengths: {stated}")
    assert sorted(measured.values()) == stated, (
        f"the card cites the stabilizer image indices {stated}, and the finite image gives "
        f"{sorted(measured.values())}"
    )

    # Each pointed family is certified in the finite quotient by its own images:
    # with -id it presents the setwise line stabilizer, whose image index is the
    # independently computed count above.  The exact-sequence argument, not this
    # finite quotient, is what certifies generation in the discriminant kernel.
    discriminant = lattice.discriminant_representation()
    finite_orthogonal = discriminant.codomain()
    for name, index in CUSPS.items():
        vector = lattice.module_generator(labels[index])
        start = time.monotonic()
        family = pointed_generators(lattice, vector)
        print(
            f"pointed family at {name} = Ze_{index + 1}: {len(family)} generators, "
            f"{time.monotonic() - start:.1f} s"
        )
        assert family
        assert all(generator(vector) == vector for generator in family)
        line_family = finite_orthogonal.subgroup(
            (
                *(discriminant(generator) for generator in family),
                discriminant(reversing),
            )
        )
        image_index = int(finite_orthogonal.cardinality()) // int(line_family.cardinality())
        assert image_index == measured[name], (
            f"{name}'s pointed family, with -id, has discriminant image index {image_index}, "
            f"but its exact line-stabilizer index is {measured[name]}"
        )
        print(f"{name}: pointed family's line-stabilizer image index {image_index}")


if __name__ == "__main__":
    run()
