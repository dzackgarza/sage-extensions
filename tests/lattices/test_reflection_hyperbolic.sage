r"""Reflection groups of hyperbolic lattices, and Vinberg's enumeration.

Vinberg's algorithm enumerates the walls of a fundamental polyhedron for
\(W(L)\).  It is a semi-decision procedure: it halts with a certificate when
the polyhedron closes, so a completed search proves reflectivity while a
bounded one proves nothing.  The tests below state what a completed search
delivers on \(U\oplus A_1\), and check Vinberg's root-length bound against the
two Bogachev-Kolpakov ternary lattices, where the bound is what makes "does
this lattice have a root" a finite question.

Allcock's edgewalk answers the same question and terminates on every input, so
it decides where Vinberg's algorithm semi-decides.

Sources: Vinberg, *On groups of unit elements of certain quadratic forms*,
Mat. Sb. 87 (1972); Vinberg, *Hyperbolic reflection groups*, Russian Math.
Surveys 40 (1985); Bogachev and Kolpakov, *Thin hyperbolic reflection groups*,
arXiv:2112.14642v4, sections 6.1 and 6.2.
"""

from sage_extensions.all import *


def u_plus_a1():
    r"""Return \(U\oplus A_1\), of signature \((1,2)\), as a hyperbolic lattice.

    The reflection algorithms are methods of ``HyperbolicLattices``, whose domain
    is a lattice of signature \((n,1)\) or \((1,n)\) (V. V. Nikulin, *Reflection
    groups in hyperbolic spaces and the denominator formula for Lorentzian
    Kac--Moody Lie algebras*, Izvestiya: Mathematics 60 (1996), no. 2,
    arXiv:alg-geom/9503003v6, §1.1, (1.1.1), preprint p. 3).  The orthogonal sum
    of two lattices is a ``Lattices`` object, so the sum is handed to the
    category that owns the algorithms.
    """
    return HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + Lattices(ZZ)("A1"))


def test_vinbergs_criterion_bounds_the_root_lengths_of_the_bogachev_kolpakov_lattices() -> None:
    r"""Every root length divides twice the exponent of the discriminant group.

    Bogachev and Kolpakov, arXiv:2112.14642v4 section 6.2, citing Vinberg.  For
    the section 6.1 lattice the invariant factors are \(1, 49, 49\), so every
    root length divides \(98\), whose six divisors are \(1,2,7,14,49,98\); for
    the section 6.2 lattice they are \(1, 49, 2401\), so every root length
    divides \(4802 = 2\cdot 7^4\), which has \(2\cdot5=10\) divisors.
    """
    with_roots = Lattices.BogachevKolpakovNonReflective
    without_roots = Lattices.BogachevKolpakovWithoutRoots

    lengths = with_roots.possible_root_lengths()
    assert lengths.cardinality() == 6
    for length in (1, 2, 7, 14, 49, 98):
        assert length in lengths

    lengths = without_roots.possible_root_lengths()
    assert lengths.cardinality() == 10
    for length in (1, 2, 7, 14, 49, 98, 343, 686, 2401, 4802):
        assert length in lengths
    assert 4 not in lengths
    assert 21 not in lengths


def test_the_root_length_forty_nine_form_does_not_represent_one() -> None:
    r"""\(q = 49m_2^2 + 14m_1m_3 - 28m_2m_3 + 6m_3^2\) never takes the value \(1\).

    Bogachev and Kolpakov, *Thin hyperbolic reflection groups*,
    arXiv:2112.14642v4, §6.2, p. 9, state it of this form: "However, \(q\) does
    not integrally represent \(1\)".  The paper's reason is the local one:
    modulo \(7\), \(q\equiv 6m_3^2\), and \(6\cdot\{0,1,2,4\}=\{0,6,5,3\}\) omits
    \(1\), so \(q\) fails over \(\mathbb Z_7\) and hence over \(\mathbb Z\).

    Only the integral verdict is asserted, which is what the paper states and what
    :meth:`represents` decides.  The local half of the argument is not asked of
    this library: ``localize_at_prime`` on a lattice returns the localization of
    its underlying *module*, which carries no form, and :meth:`represents` is
    implemented over \(\mathbb Z\), \(\mathbb Q\), \(\mathbb A\) and
    \(\mathbb R\) (Serre, *A Course in Arithmetic*, Ch. IV, §1, pp. 27--34, with
    Ch. IV §2 for the \(p\)-adic case), refusing any other ring by assertion.

    With \(q(x)=b(x,x)\) the Gram matrix is
    \(\begin{psmallmatrix}0&0&7\\0&49&-14\\7&-14&6\end{psmallmatrix}\), of
    determinant \(7\cdot(0\cdot(-14)-49\cdot7)=-7^4\).
    """
    lattice = Lattices(ZZ)([[0, 0, 7], [0, 49, -14], [7, -14, 6]])

    assert lattice.determinant() == -2401
    assert not lattice.represents(1)


def test_vinberg_enumeration_closes_the_polyhedron_of_u_plus_a1() -> None:
    r"""The search on \(U\oplus A_1\) completes, which certifies reflectivity.

    Each wall of the fundamental polyhedron is the mirror of a root, so each
    accepted vector is a root, its reflection is an involution of \(O(L)\)
    negating it, and its length obeys Vinberg's bound.  A polyhedron in
    \(\mathbb H^2\) has at least three walls.
    """
    lattice = u_plus_a1()
    roots = lattice.vinberg_simple_roots(max_decompositions=200)

    assert lattice.signature_pair().first() == 1
    assert lattice.signature_pair().second() == 2
    assert lattice.is_reflective(max_decompositions=200) is True
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


def test_u_plus_a1_is_reflective_but_not_cocompact() -> None:
    r"""\(U\) is isotropic, so the fundamental polyhedron of \(U\oplus A_1\) has an
    ideal vertex: it has finite volume and is not compact (Vinberg 1985, section 1).
    """
    lattice = u_plus_a1()

    assert lattice.is_reflective(max_decompositions=200) is True
    assert lattice.is_cocompact(max_decompositions=200) is False


def test_the_edgewalk_and_vinbergs_algorithm_agree_that_u_plus_a1_is_reflective() -> None:
    r"""Both decide reflectivity of \(U\oplus A_1\) positively, and the walls the
    edgewalk reports are roots whose reflections are involutions of \(O(L)\).
    """
    lattice = u_plus_a1()

    assert lattice.edgewalk_is_reflective() is True
    assert lattice.is_reflective(max_decompositions=200) is True

    walls = lattice.edgewalk_simple_roots()
    assert walls.cardinality() >= 3
    identity = lattice.O().one()
    for wall in walls:
        assert wall.is_root()
        reflection = lattice.reflection(wall)
        assert reflection * reflection == identity
        assert reflection(wall) == -wall
