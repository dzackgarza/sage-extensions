r"""Vinberg's algorithm over the ring of integers of a real quadratic field."""

from sage_extensions.all import *


def test_vinberg_on_the_belolipetsky_lattice_over_the_golden_integers_finds_four_simple_roots() -> None:
    r"""Over \(\mathcal O = \mathbb Z[\varphi]\), \(\varphi = (1+\sqrt5)/2\), the chain Gram
    with off-diagonal entries \(-1, -\varphi, -1\) is the \([3,5,3]\) diagram: signature
    \((3,1)\) at \(\sqrt5 \mapsto +\sqrt5\) and positive definite at the conjugate place.
    The simple roots are \(-e_1, -e_2, -e_3\) and
    \(v = ((s+3)/2,\ s+3,\ 3(s+1)/2,\ (s-1)/2)\), \(b(v,v) = 3 - \sqrt5\), pairing
    nonpositively with the others (direct computation of the Gram values).
    """
    field = QuadraticField(5, "s")
    s = field.primitive_element()
    order = field.maximal_order()
    phi = (1 + s) / 2
    lattice = Lattices(order)(
        [
            [2, -1, 0, 0],
            [-1, 2, -phi, 0],
            [0, -phi, 2, -1],
            [0, 0, -1, 2],
        ]
    )
    place = next(p for p in field.embeddings(AA) if p(s) > 0)
    conjugate = next(p for p in field.embeddings(AA) if p(s) < 0)

    assert lattice.base_change(place).signature_pair() == signature_pair(3, 1)
    assert lattice.base_change(conjugate).signature_pair() == signature_pair(4, 0)

    complete, roots = lattice.number_field_vinberg(place).vinberg_simple_roots(count=4)

    assert complete
    assert roots.cardinality() == 4
    expected = (
        lattice((-1, 0, 0, 0)),
        lattice((0, -1, 0, 0)),
        lattice((0, 0, -1, 0)),
        lattice((order((s + 3) / 2), order(s + 3), order(3 * (s + 1) / 2), order((s - 1) / 2))),
    )
    assert all(root == expected[position] for position, root in enumerate(roots))
    assert expected[3].b(expected[3]) == 3 - s
    assert all(place(root.b(root)) > 0 for root in roots)
    assert all(
        place(left.b(right)) <= 0
        for left in roots
        for right in roots
        if left != right
    )
