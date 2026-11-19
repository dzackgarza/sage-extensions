r"""Card 0128's #Gamma-bar_h at degree 4, read by tag, from the groups' orders.

D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces --
computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2,
state in Table 4, printed p. 17, two numbers for each degree: ``#h``, the
classes of primitive polarizations, and ``#Gamma-bar_h``, the conjugacy classes
of the groups those classes define.  The invariant the paper separates the
classes by is the order and the orbit sizes of the group (p. 11).

At degree 4 the card states two classes and two conjugacy classes, and the
order alone separates them: conjugate subgroups are isomorphic, so they have
equal order, and two groups of different order are not conjugate.  That decides
this row without any orbit call, which matters because the plane and flag rows
of the same cards do not return at this size.

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
