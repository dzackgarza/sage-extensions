r"""Card 0128's #Gamma-bar_h rows, read by tag, from finite-group conjugacy.

D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces --
computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2,
state in Table 4, printed p. 17, two numbers for each degree: ``#h``, the
classes of primitive polarizations, and ``#Gamma-bar_h``, the conjugacy classes
of the groups those classes define.  Equation (5) and Question 2.1 identify the
latter with conjugacy classes of the finite discriminant images; Section 3.3
computes that relation.  Orders and orbit sizes are only invariants used in
their computation, not the equivalence relation.

At degree 4 the card states two classes and two conjugacy classes, and the
order alone separates them: conjugate subgroups are isomorphic, so they have
equal order, and two groups of different order are not conjugate.  At degrees
12 and 20, Table 3 identifies exactly one pair of polarization orbits and leaves
the remaining classes distinct; the tests below decide the entire partitions
by finite-subgroup conjugacy, not by orders or isotropic-orbit counts.

The card's lattice is $M(1/2) = U \oplus E_8(-1)$, whose basis is the paper's
$g_1, \ldots, g_{10}$ (equation (7), p. 9), and a polarization of degree $2d$ is
a primitive vector of square $2d$ in it.  The catalogue's $E_{10}$ is that
lattice; the invariant lattice $M = U(2) \oplus E_8(-2)$ that
`Involutions.I_En.polarized` reads is $2M(1/2)$, so the same polarization has
square $4d$ in $M$, and that is the square asked for below.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _class_group_orders(degree):
    r"""The orders of the groups the card's primitive classes of ``degree`` define.

    A class is read on $M$, where its representatives have square $4d$, and its
    group is the preimage $\Gamma_h$ of the coinvariant construction: the
    order returned is $|\bar\Gamma_h| = |\rho(\Gamma_h)|$, which the card states
    as its ``cardinality``.
    """
    invariant = Involutions.I_En.invariant_lattice()
    orders = []
    for representative in invariant.Aut().vector_orbit_representatives(
        2 * degree, content=1
    ):
        polarized = Involutions.I_En.polarized(invariant.inclusion()(representative))
        orders.append(polarized.coinvariant_extension_subgroup().discriminant_image().order())
    return orders


def _class_relation(degree):
    r"""The primitive vector orbits and the conjugacy relation of their group images.

    DSH equation (5) makes the discriminant image of the full preimage
    $\Gamma_h$ equal to $\bar\Gamma_h = \pi_M(O(M,h))$.  Question 2.1 and
    Section 3.3 then define the group classes by conjugacy in the common finite
    orthogonal group, which is the relation the public conjugation action decides.
    """
    invariant = Involutions.I_En.invariant_lattice()
    representatives = invariant.Aut().vector_orbit_representatives(
        2 * degree, content=1
    )
    images = tuple(
        Involutions.I_En.polarized(invariant.inclusion()(representative))
        .coinvariant_extension_subgroup()
        .discriminant_image()
        for representative in representatives
    )
    quotient = images[0].supergroup().subgroup_conjugation_g_set().orbits()
    return representatives, tuple(quotient.orbit_of(image) for image in images)


def _assert_table3_has_one_identified_pair(degree):
    r"""The whole Table 3 partition and both Table 4 numbers of one deciding degree."""
    representatives, orbits = _class_relation(degree)
    row = card("polarization_counts", "rows")[f"{degree}"]
    class_count = sum(
        1
        for position, orbit in enumerate(orbits)
        if all(orbit != previous for previous in orbits[:position])
    )
    identified_pairs = sum(
        1
        for position, orbit in enumerate(orbits)
        for previous in orbits[:position]
        if orbit == previous
    )

    assert representatives.cardinality() == row["primitive_classes"]
    assert class_count == row["group_classes"]
    # Table 3, printed p. 16: at degrees 12 and 20 exactly two vector orbits
    # give one conjugacy class, and every other pair gives distinct classes.
    assert identified_pairs == 1


def test_the_degree_twelve_group_classes_are_the_finite_conjugacy_classes() -> None:
    r"""Degree 12: four vector orbits, three group classes, one identified pair."""
    _assert_table3_has_one_identified_pair(12)


def test_the_degree_twenty_group_classes_are_the_finite_conjugacy_classes() -> None:
    r"""Degree 20: five vector orbits, four group classes, one identified pair."""
    _assert_table3_has_one_identified_pair(20)


def test_the_degree_four_classes_define_groups_of_different_orders() -> None:
    r"""#Gamma-bar_h at degree 4 is the number of the classes' distinct orders.

    The card states two classes and two conjugacy classes of groups; the two
    orders computed here are different, so no two of the classes are
    conjugate and the row's count is the number of classes.
    """
    row = card("polarization_counts", "rows")["4"]
    first, second = _class_group_orders(4)

    assert row["group_classes"] == row["primitive_classes"]
    assert first != second
