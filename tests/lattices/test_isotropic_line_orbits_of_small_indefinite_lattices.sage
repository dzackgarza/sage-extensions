r"""The primitive isotropic line orbits of ``L_d = U ⊕ U ⊕ ⟨−2d⟩``, against the card rows.

A Baily--Borel 0-cusp is a ``Γ``-orbit of primitive isotropic *lines*, so the
number these tests assert is a count of rank-one isotropic sublattices.  Every
expected count is read from the card of the lattice it is about, by tag: the
five cards ``6JRS``, ``6JRT``, ``6JRU``, ``6JRV`` and ``6JRW`` of
``dzackgarza/lattice-database`` are ``L_d`` for ``d = 1, 2, 4, 9, 36``, and each
states its ``O``, ``Õ`` and ``Õ⁺`` rows under ``integral.primitive_orbits``,
whose ``constant`` is the number of orbits of primitive isotropic lines.  No
count here is typed.

The lattice is built from the card's own ``gram_tensor``, and the rank,
signature, determinant and Gram matrix are compared with the card before the
orbit row is read, so the call runs on the card's lattice rather than on one
substituted for it.  These rows are the database's computed ones -- no published
source states these counts -- and ``certifications.integral.primitive_orbits`` is
the stamp they were computed under.
"""

from sage_extensions.all import *  # noqa: F401,F403

# The five cards of U ⊕ U ⊕ ⟨−2d⟩, and the subgroups whose line rows they state.
LINE_CARDS = ("6JRS", "6JRT", "6JRU", "6JRV", "6JRW")
LINE_GROUPS = ("O", "Otilde", "Otilde+")


def stated_orbits(tag):
    r"""The card ``tag``'s primitive-orbit rows, read by tag from the digest."""
    return card("primitive_orbit_series", tag)


def carded_lattice(tag):
    r"""The lattice card ``tag`` states, built from its own Gram tensor."""
    return Lattices(ZZ)(stated_orbits(tag)["gram"])


def line_representatives(lattice):
    r"""The line-orbit sets of ``O``, ``Õ`` and ``Õ⁺`` on ``lattice``, by card row name."""
    stable = lattice.stable_orthogonal_group()
    return {
        "O": lattice.Aut().isotropic_orbit_representatives(1),
        "Otilde": stable.isotropic_orbit_representatives(1),
        "Otilde+": stable.intersection(lattice.O_plus()).isotropic_orbit_representatives(1),
    }


def check_the_line_rows(tag):
    r"""Compare the three line counts on card ``tag``'s lattice with the card's own rows."""
    stated = stated_orbits(tag)
    lattice = carded_lattice(tag)
    basis = tuple(lattice.module_generators())

    assert sorted(stated["rows"]) == sorted(LINE_GROUPS), tag
    assert int(lattice.module_rank()) == int(stated["rank"]), tag
    assert [int(entry) for entry in lattice.signature()] == [
        int(entry) for entry in stated["signature"]
    ], tag
    assert int(lattice.determinant()) == int(stated["determinant"]), tag
    assert [
        [int(lattice.b(left, right)) for right in basis] for left in basis
    ] == stated["gram"], tag

    representatives = line_representatives(lattice)
    for group in LINE_GROUPS:
        orbits = representatives[group]
        assert orbits.cardinality() == int(stated["rows"][group]["constant"]), (tag, group)
        for line in orbits:
            vector = line.inclusion()(line.module_generator(0))
            assert vector.q() == ZZ(0), (tag, group)
            assert vector.is_primitive() is True, (tag, group)


def test_the_line_counts_of_l_1_are_card_6jrs_s_rows() -> None:
    r"""``L_1``: the three counts are the ``O``, ``Õ`` and ``Õ⁺`` rows of ``6JRS``."""
    check_the_line_rows("6JRS")


def test_the_line_counts_of_l_2_are_card_6jrt_s_rows() -> None:
    r"""``L_2``: the three counts are the rows of ``6JRT``."""
    check_the_line_rows("6JRT")


def test_the_line_counts_of_l_4_are_card_6jru_s_rows() -> None:
    r"""``L_4``: the three counts are the rows of ``6JRU``."""
    check_the_line_rows("6JRU")


def test_the_line_counts_of_l_9_are_card_6jrv_s_rows() -> None:
    r"""``L_9``: the three counts are the rows of ``6JRV``."""
    check_the_line_rows("6JRV")


def test_the_line_counts_of_l_36_are_card_6jrw_s_rows() -> None:
    r"""``L_36``: the three counts are the rows of ``6JRW``."""
    check_the_line_rows("6JRW")


def test_the_two_witness_vectors_of_l_9_are_primitive_isotropic_of_divisibility_three() -> None:
    r"""``v = 3e + 3f + g`` and its negative, on the Gram tensor of card ``6JRV``.

    Both are isotropic and primitive, ``v`` has divisibility three, and the two
    divided classes are distinct and of order three -- the arithmetic the
    divisibility of ``v`` forces, computed by the library rather than assumed.
    """
    lattice = carded_lattice("6JRV")
    labels = tuple(lattice.module_generating_set())
    e, f = lattice.module_generator(labels[0]), lattice.module_generator(labels[1])
    g = lattice.module_generator(labels[4])

    for sign in (1, -1):
        vector = sign * (3 * e + 3 * f + g)
        assert vector.q() == ZZ(0)
        assert vector.is_primitive() is True
        assert lattice.div(vector) == ZZ(3)
        assert int(lattice.divided_discriminant_class(vector).additive_order()) == 3

    first = 3 * e + 3 * f + g
    second = -(3 * e + 3 * f + g)
    assert lattice.divided_discriminant_class(first) != lattice.divided_discriminant_class(second)
