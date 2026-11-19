r"""Folding a root family by an involution of its span that is an isometry of it.

An involution \(g\) of the span \(W\) of the roots \(r_1,\dots,r_n\) folds the family: the orbit
sums \(s_O=\sum_{v\in O}r_v\) are fixed by \(g\), so they lie in the invariant lattice \(W^g\), and
the sums that are roots are the roots of the folded diagram; \((W^g)^\perp\) is the anti-invariant
lattice.  The orbits of an involution have one or two elements, so \(s_O\) is the root itself or
\(r+g(r)\).

The datum of \(g\) is written in either of the two forms its images take.  A **permutation** of the
roots --- the classical diagram involution --- induces the linear map
\(g(\sum_v a_v r_v)=\sum_v a_v r_{\sigma v}\) exactly when it carries the rational relations of the
roots to relations, and it is an isometry exactly when it keeps every pairing.  The **images** of
the roots serve when \(g\) is no permutation of them, a root being carried to its negative or to the
sum of itself with another root; the vertices named must then span the span of the family, since
the images of a spanning subfamily are what determine a linear map.

The two conditions are independent exactly when the span is degenerate.  The rational relations of
the roots are the kernel of their coordinate matrix, while the kernel of their Gram matrix \(G\) is
the preimage of \(W\cap W^\perp\) under \(r\mapsto\langle r,-\rangle\); the two kernels coincide
exactly when \(W\) is nondegenerate.  So over a nondegenerate span every permutation that keeps the
Gram matrix keeps all rational relations too, and the refusal of a Gram-preserving permutation that
breaks a relation has its specimens only over a degenerate span, which is where the one below
lives.

The smallest specimen that decides the isometry is two orthogonal \((-2)\)-roots \(a,b\) of
\(A_1\oplus A_1\), swapped: the orbit sums are the one root \(a+b\), of square \(-4\), and the
invariant and anti-invariant lattices are \(\mathbf Z(a+b)\) and \(\mathbf Z(a-b)\), both of
square \(-4\).  Three roots of \(A_2\) --- \(r_1,r_2,r_1+r_2\) --- decide that a root of the family
may itself be the sum of the two swapped ones: the fold by the swap of \(r_1,r_2\) has the
invariant lattice \(\mathbf Z(r_1+r_2)\), of square \(-2\), and the anti-invariant lattice
\(\mathbf Z(r_1-r_2)\), of square \(q(r_1)+q(r_2)-2b(r_1,r_2)=-6\).  They also decide the
nondegenerate case: their span is all of \(A_2\), and of their six permutations exactly the two that
keep the pairings are folds.

Three permutations are refused, for three different reasons.  The three roots of \(A_2\) have the
affine diagram \(\tilde A_2\), whose automorphism group is all of \(S_3\), while only the two
permutations fixing the pair \(\{r_1,r_2\}\) keep the pairings: the bond is \(|b|\), so a diagram
symmetry may reverse a pairing.  A family whose span is degenerate satisfies relations its pairings
do not see: in the lattice of Gram \([[-2,1,0],[1,-2,0],[0,0,0]]\), the four roots
\(r_1,r_2,r_1+r_2,r_1+z\) have a Gram-preserving permutation that is no isometry of their span ---
it carries the relation \(r_1+r_2-(r_1+r_2)=0\) to \(z\), a nonzero point of the radical.  And a
map given by images may fail to be an isometry at all, or may be no involution, which a fold
requires because it sums over orbits.

An orbit sum that is a multiple of a point of the span is rescaled to that point: a root is
primitive, and the sum of an orbit's two roots has square \(2q(r)+2b(r,g(r))\), which is what
bounds the multiple.  The smallest specimen is two roots \(t+u\), \(t-u\) of the lattice
\(\mathbf Z t\oplus\mathbf Z u\) with \(q(t)=-2\) and \(u\) isotropic: they pair to \(-2\), their
sum is \(2t\), and the fold's root is \(t\).
"""

from sage_extensions.all import *

import pytest


def _folded_into(lattice, folding):
    r"""Return the folded roots carried back into ``lattice``, the roots' own lattice."""
    return tuple(
        folding.span().inclusion()(folding.invariant_lattice().inclusion()(root))
        if folding.span() is not lattice
        else folding.invariant_lattice().inclusion()(root)
        for root in folding.roots()
    )


def test_the_fold_of_two_orthogonal_roots_by_their_swap() -> None:
    plane = Lattices(ZZ)([[-2, 0], [0, -2]])
    first, second = plane.module_generators()
    folding = CoxeterDiagrams().from_roots((first, second)).fold((1, 0))

    assert folding.isometry()(first) == second
    assert folding.isometry()(second) == first
    assert folding.isometry() * folding.isometry() == folding.isometry().parent().identity()
    assert folding.span() is plane
    assert folding.invariant_lattice().gram_tensor() == tensor(ZZ, (), (1, 1), [[-4]])
    assert folding.anti_invariant_lattice().gram_tensor() == tensor(ZZ, (), (1, 1), [[-4]])
    assert folding.discarded_sums() == ()
    assert tuple(root.q() for root in _folded_into(plane, folding)) == (-4,)
    assert folding.folded_diagram().cardinality() == 1


def test_the_fold_of_three_roots_of_a2_by_the_swap_of_two_of_them() -> None:
    lattice = Lattices(ZZ)("A2")
    first, second = lattice.module_generators()
    diagram = CoxeterDiagrams().from_roots((first, second, first + second))
    folding = diagram.fold((1, 0, 2))

    assert diagram.Aut().order() == 6
    assert folding.isometry()(first) == second
    assert folding.isometry()(first + second) == first + second
    assert folding.invariant_lattice().gram_tensor() == tensor(ZZ, (), (1, 1), [[-2]])
    assert folding.anti_invariant_lattice().gram_tensor() == tensor(ZZ, (), (1, 1), [[-6]])
    assert tuple(root.q() for root in _folded_into(lattice, folding)) == (-2,)
    assert folding.folded_diagram().cardinality() == 1


def test_a_diagram_symmetry_that_reverses_a_pairing_is_refused() -> None:
    r"""\(\tilde A_2\)'s other four symmetries keep the bonds and not the pairings of the roots."""
    lattice = Lattices(ZZ)("A2")
    first, second = lattice.module_generators()
    diagram = CoxeterDiagrams().from_roots((first, second, first + second))

    assert diagram.Aut().order() == 6
    for permutation in ((0, 2, 1), (2, 1, 0), (2, 0, 1), (1, 2, 0)):
        with pytest.raises(ValueError):
            diagram.fold(permutation)


def test_a_permutation_that_keeps_the_pairings_and_breaks_a_relation_is_refused() -> None:
    r"""The swap of \(r_1\) and \(r_1+z\) keeps the pairings of the four roots and breaks a relation.

    The relation \(r_1+r_2-(r_1+r_2)=0\) becomes \(z\) under the swap, and \(z\) is a nonzero
    point of the radical: the four roots' span is degenerate, which is exactly where Proposition 1
    leaves room for a Gram-preserving permutation that is no isometry of it.
    """
    lattice = Lattices(ZZ)([[-2, 1, 0], [1, -2, 0], [0, 0, 0]])
    first, second, radical = lattice.module_generators()
    roots = (first, second, first + second, first + radical)
    permutation = (3, 1, 2, 0)
    images = tuple(roots[position] for position in permutation)

    assert all(
        lattice.b(roots[left], roots[right]) == lattice.b(images[left], images[right])
        for left in range(4)
        for right in range(4)
    )
    assert images[0] + images[1] - images[2] == radical
    with pytest.raises(ValueError):
        CoxeterDiagrams().from_roots(roots).fold(permutation)


def test_the_pairing_test_and_the_relation_test_decide_alike_over_a_nondegenerate_span() -> None:
    r"""Of the six permutations of \(A_2\)'s three roots, exactly the two that keep the pairings fold.

    The roots \(r_1,r_2,r_1+r_2\) span all of \(A_2\), which is nondegenerate, so the rational
    relations are the kernel of their Gram matrix and a permutation that keeps the pairings keeps
    them.  The two that do are the identity and the swap of \(r_1,r_2\), and each fold's isometry
    carries every root to its image under that permutation; the other four are refused.
    """
    lattice = Lattices(ZZ)("A2")
    first, second = lattice.module_generators()
    roots = (first, second, first + second)
    diagram = CoxeterDiagrams().from_roots(roots)
    lifted = ()

    for permutation in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)):
        images = tuple(roots[position] for position in permutation)
        keeps_pairings = all(
            lattice.b(roots[left], roots[right]) == lattice.b(images[left], images[right])
            for left in range(3)
            for right in range(3)
        )
        if not keeps_pairings:
            with pytest.raises(ValueError):
                diagram.fold(permutation)
            continue
        folding = diagram.fold(permutation)
        isometry = folding.isometry()

        assert all(isometry(roots[position]) == images[position] for position in range(3))
        assert isometry * isometry == isometry.parent().identity()
        lifted = lifted + (permutation,)

    assert sorted(lifted) == [(0, 1, 2), (1, 0, 2)]


def test_a_mapping_of_the_vertices_names_the_same_fold_as_the_tuple_of_its_images() -> None:
    plane = Lattices(ZZ)([[-2, 0], [0, -2]])
    first, second = plane.module_generators()
    diagram = CoxeterDiagrams().from_roots((first, second))

    assert diagram.fold({0: 1, 1: 0}).roots().cardinality() == diagram.fold((1, 0)).roots().cardinality()


def test_the_fold_by_images_that_are_no_permutation_of_the_roots() -> None:
    r"""A root may go to its negative: \(b\mapsto -b\) is no permutation of the two roots."""
    plane = Lattices(ZZ)([[-2, 0], [0, -2]])
    first, second = plane.module_generators()
    folding = CoxeterDiagrams().from_roots((first, second)).fold({0: first, 1: -second})

    assert folding.isometry()(first) == first
    assert folding.isometry()(second) == -second
    assert folding.invariant_lattice().gram_tensor() == tensor(ZZ, (), (1, 1), [[-2]])
    assert folding.anti_invariant_lattice().gram_tensor() == tensor(ZZ, (), (1, 1), [[-2]])
    assert tuple(root.q() for root in _folded_into(plane, folding)) == (-2,)
    assert folding.folded_diagram().cardinality() == 1
    assert tuple(int(sum.q()) for sum in folding.discarded_sums()) == (0,)


def test_an_orbit_sum_that_is_a_multiple_of_a_root_is_rescaled() -> None:
    r"""An orbit that is not orthogonal may sum to a multiple of a root, and the fold rescales it.

    In the lattice \(\mathbf Z t\oplus\mathbf Z u\) with \(q(t)=-2\) and \(u\) isotropic, the roots
    \(t+u\) and \(t-u\) pair to \(-2\), so their swap is an isometry and the diagram of the two
    roots has an infinite bond.  Their orbit sum is \(2t\), which is no root, and the fold's root
    is \(t\), of square \(-2\), which the involution fixes; the anti-invariant lattice is
    \(\mathbf Z u\).
    """
    lattice = Lattices(ZZ)([[-2, 0], [0, 0]])
    t, u = lattice.module_generators()
    first, second = t + u, t - u
    folding = CoxeterDiagrams().from_roots((first, second)).fold((1, 0))

    assert int(lattice.q(first)) == -2
    assert int(lattice.q(second)) == -2
    assert int(lattice.b(first, second)) == -2
    assert (first + second).is_primitive() is not True
    assert folding.isometry()(first) == second
    assert _folded_into(lattice, folding) == (t,)
    assert tuple(root.q() for root in folding.roots()) == (-2,)
    assert folding.discarded_sums() == ()
    assert folding.folded_diagram().cardinality() == 1


def test_a_map_that_is_no_isometry_is_refused_when_it_is_given_by_images() -> None:
    plane = Lattices(ZZ)([[-2, 0], [0, -2]])
    first, second = plane.module_generators()
    diagram = CoxeterDiagrams().from_roots((first, second))

    with pytest.raises(ValueError):
        diagram.fold({0: 2 * first, 1: -second})
    with pytest.raises(ValueError):
        diagram.fold({0: first})
