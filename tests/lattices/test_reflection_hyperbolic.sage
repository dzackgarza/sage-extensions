r"""Reflection groups of hyperbolic lattices, and Vinberg's enumeration.

Vinberg's algorithm enumerates the walls of a fundamental polyhedron for
\(W(L)\).  It is a semi-decision procedure: it halts with a certificate when the
polyhedron closes, so a completed search proves reflectivity while a bounded one
proves nothing.  The tests below check what a completed search delivers on
\(U\oplus A_1\), and Vinberg's root-length bound on the two Bogachev--Kolpakov
ternary lattices, where the bound is what makes "does this lattice have a root" a
finite question.

Allcock's edgewalk answers the same question and terminates on every input, so it
decides where Vinberg's algorithm semi-decides.

Every expected value is read by tag or computed here: the reflective verdict on
\(U\oplus A_1\) is card `0026`'s certified ``hyperbolic.reflective``, and the
root-length bound is the exponent of each lattice's own discriminant group.

Sources: Vinberg, *On groups of unit elements of certain quadratic forms*,
Mat. Sb. 87 (1972); Vinberg, *Hyperbolic reflection groups*, Russian Math.
Surveys 40 (1985); Bogachev and Kolpakov, *Thin hyperbolic reflection groups*,
arXiv:2112.14642v4, §6.2, p. 9.
"""

from sage_extensions.all import *


def u_plus_a1():
    r"""Return \(U\oplus A_1\) as a hyperbolic lattice, built through the owning category.

    The reflection algorithms are methods of ``HyperbolicLattices``, whose domain
    is a lattice of signature \((n,1)\) or \((1,n)\) (V. V. Nikulin, *Reflection
    groups in hyperbolic spaces and the denominator formula for Lorentzian
    Kac--Moody Lie algebras*, Izvestiya: Mathematics 60 (1996), no. 2,
    arXiv:alg-geom/9503003v6, §1.1, (1.1.1), preprint p. 3), and the sum is
    handed to that category.
    """
    return HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + Lattices(ZZ)("A1"))


def card_0026():
    r"""Card `0026`'s row, the lattice \(U\oplus A_1(-1)\) and its certified verdict."""
    return card("hyperbolic_reflectivity", "0026")


def test_vinbergs_criterion_bounds_the_root_lengths_of_the_bogachev_kolpakov_lattices() -> None:
    r"""Every root length divides twice the exponent of the discriminant group.

    Bogachev and Kolpakov, *Thin hyperbolic reflection groups*,
    arXiv:2112.14642v4, §6.2, p. 9, citing Vinberg: a root length divides twice
    the last invariant factor of the Gram matrix, which is the exponent of the
    discriminant group.  The bound is read from each lattice's own discriminant
    module, and the lengths it reports are measured against that bound, so no
    length, divisor or count is typed here.
    """
    for lattice in (Lattices.BogachevKolpakovNonReflective, Lattices.BogachevKolpakovWithoutRoots):
        bound = ZZ(2) * lattice.discriminant_module().exponent()
        lengths = lattice.possible_root_lengths()

        assert int(bound) > 1
        assert all(int(bound) % int(length) == 0 for length in lengths)


def test_vinberg_enumeration_closes_the_polyhedron_of_u_plus_a1() -> None:
    r"""The search on \(U\oplus A_1\) completes, which certifies reflectivity.

    Each wall of the fundamental polyhedron is the mirror of a root, so each
    accepted vector is a root, its reflection is an involution of \(O(L)\)
    negating it, and its length obeys Vinberg's bound.  The verdict is card
    `0026`'s ``hyperbolic.reflective``, and the lattice is checked to be that
    card's lattice by its Gram.
    """
    stated = card_0026()
    lattice = u_plus_a1()
    roots = lattice.vinberg_simple_roots(max_decompositions=200)
    basis = tuple(lattice.module_generators())

    assert [
        [int(lattice.b(left, right)) for right in basis] for left in basis
    ] == stated["gram"]
    assert lattice.is_reflective(max_decompositions=200) is bool(stated["reflective"])
    assert roots.cardinality() >= 3

    lengths = lattice.possible_root_lengths()
    identity = lattice.O().one()
    for root in roots:
        assert root.is_root()
        assert abs(root.q()) in lengths
        reflection = lattice.reflection(root)
        assert reflection in lattice.O()
        assert reflection * reflection == identity
        assert reflection(root) == -root


def test_u_plus_a1_is_reflective() -> None:
    r"""\(U\oplus A_1\) is reflective, by card `0026`'s certified field.

    The Vinberg search on this lattice completes, and the verdict it returns is
    compared with the card's rather than typed.
    """
    stated = card_0026()
    lattice = u_plus_a1()

    assert lattice.is_reflective(max_decompositions=200) is bool(stated["reflective"])


def test_the_edgewalk_and_vinbergs_algorithm_agree_that_u_plus_a1_is_reflective() -> None:
    r"""Both decide reflectivity of \(U\oplus A_1\) as card `0026` states it.

    The two routes are independent — the edgewalk terminates on every input and
    Vinberg's search only on a certificate — so their agreement with the card is
    two measurements of the same verdict.  The walls the edgewalk reports are
    roots whose reflections are involutions of \(O(L)\).
    """
    stated = card_0026()
    lattice = u_plus_a1()

    assert lattice.edgewalk_is_reflective() is bool(stated["reflective"])
    assert lattice.is_reflective(max_decompositions=200) is bool(stated["reflective"])

    walls = lattice.edgewalk_simple_roots()
    assert walls.cardinality() >= 3
    identity = lattice.O().one()
    for wall in walls:
        assert wall.is_root()
        reflection = lattice.reflection(wall)
        assert reflection * reflection == identity
        assert reflection(wall) == -wall
