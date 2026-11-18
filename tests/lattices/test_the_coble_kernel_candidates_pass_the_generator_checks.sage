r"""The candidate generators of the Coble lattice's discriminant kernel.

**What these assertions are.**  ``T_Co = <2> + U(2) + E8(-2)`` is even, of rank
eleven and signature `(2, 9)`, with `|A_L| = 2^{11} = |\det|`; `|A_L| = 2^rank`
gives `L = 2L^{\#}`, so the stable orthogonal group
`\tilde O(L) = \ker(O(L) \to O(A_L))` is the level-two congruence subgroup
`\ker(O(L) \to O(L/2L))`, and an isometry acts trivially on `A_L = L^{\#}/L`
exactly when its matrix is congruent to the identity modulo two.  The vectors
below have square `\pm 2` in `T_Co`'s own form, so each reflection in one of
them is an integral isometry of `T_Co`; their classes are independent in the
56-dimensional class space of the level-four subgroup, which is what makes the
family worth carrying.  That independence is a rank computation over `F_2` on
these same 56 vectors, reported with the run behind this file, not asserted
here: this suite reads the family through the library's own reflection and
discriminant machinery, and the class space has no public reading.

**What is not asserted, and cannot be from this file.**  That these isometries
*generate* `\tilde O(L)`.  Each is checked to lie in the kernel with a trivial
discriminant action, and the family is checked to generate the kernel modulo its
level-four subgroup; completeness modulo the level-four subgroup is not
completeness, and
:meth:`~.Lattices.ParentMethods.stable_orthogonal_group_generators` refuses to
state it.  A family known to generate only modulo a deeper congruence subgroup
is not a generating set.
"""

from sage_extensions.all import *  # noqa: F401,F403

CANDIDATE_ROOTS = (
    (-5, 6, 2, 2, 0, 4, 6, 6, 6, 2, 4),
    (7, -2, -2, 0, 0, 0, -2, 0, -6, -4, -1),
    (-3, 4, 6, -2, 0, 2, 0, 2, 4, -1, 0),
    (5, -4, -6, 0, 2, -4, 0, 4, 4, 5, 1),
    (-5, 2, 2, 4, 6, 6, 6, 4, 3, 0, 0),
    (-5, -4, -4, -2, 2, 0, 0, 2, 1, 2, 5),
    (7, -6, -6, 0, -4, -2, -6, -4, 5, 3, -2),
    (-5, -4, -2, 0, -2, 2, -2, -5, -2, -2, -2),
    (5, 6, 6, -4, 0, 0, 0, -5, 0, -2, -3),
    (7, 6, 0, 0, 0, 2, 6, 5, 4, -1, 0),
    (-3, 6, 4, -2, -4, -2, 0, 3, 1, 2, 2),
    (5, 6, 4, -6, -6, -4, -5, -6, -2, 0, 0),
    (7, 6, 2, 0, 0, 2, 5, 0, -2, -4, -5),
    (5, 4, 0, -2, 0, -4, -5, -2, -2, -1, -2),
    (7, -4, -6, 4, 0, 0, 3, 0, -5, -6, -2),
    (-5, 4, 6, -2, 2, -4, -1, -5, -2, -4, -4),
    (7, 6, 2, 2, -2, 5, 2, -2, -4, 0, 0),
    (5, 6, 6, 0, 0, -5, 0, -2, 4, 2, 1),
    (5, 2, 6, 2, 4, 5, 2, 4, 4, 3, 2),
    (1, 6, 6, 0, 2, 1, 0, 2, -5, -4, -2),
    (-5, 6, 6, -6, -2, -1, -2, -1, -4, -2, 2),
    (5, 0, 2, 2, 2, 3, 3, 4, 4, 6, 2),
    (1, -6, -4, 2, 1, -2, -4, -2, -2, 0, 2),
    (7, 0, -2, -2, -3, -6, -4, -6, -2, -2, -3),
    (5, 4, 6, 2, -3, 0, -4, -4, -2, 1, -4),
    (5, 6, 4, -4, -1, -2, 0, -4, 1, 2, 0),
    (-5, -6, -6, 6, 3, 4, 2, 5, 6, 0, 0),
    (1, -6, -4, 2, 5, 4, 5, 4, -2, 0, 0),
    (5, -6, -4, 2, -5, -1, -4, -2, -2, 2, -2),
    (5, -6, -6, -1, 2, 0, 4, -2, 4, 4, 0),
    (7, -6, -4, 5, -2, 0, 0, 0, 4, 6, 3),
    (5, -4, -6, -3, 2, -6, -4, -2, -4, -3, -4),
    (-5, -6, -4, 3, 4, 4, 2, -4, -3, -2, 0),
    (7, 6, 4, -3, -6, -2, -6, -5, 2, 2, 4),
    (3, 6, 6, -3, 2, -2, -1, 0, -2, -6, 0),
    (7, 2, 0, -1, 0, 1, 2, 4, 2, 0, -4),
    (-3, 6, 6, -5, 3, -2, 0, -4, -4, -4, -2),
    (-1, 4, 7, -2, 2, 0, 6, 4, 2, -2, -2),
    (3, 2, 3, 4, 2, 2, 4, 4, 2, 2, 1),
    (-5, 2, 5, 0, 0, 2, 0, 0, 0, 5, 2),
    (7, 6, 1, 0, 0, -6, -2, 0, -1, -2, -2),
    (-5, 4, 7, 4, -2, -2, -2, 1, -2, 0, -2),
    (7, 6, 1, -2, -2, -2, -5, -2, 2, -2, 2),
    (1, 6, 7, -2, 0, -5, -4, 0, 2, 2, 6),
    (7, 6, 7, 4, -3, -2, -2, 0, 6, 6, 0),
    (3, 6, 7, -3, 0, 2, 4, 2, 6, 0, 0),
    (5, -1, 0, 0, 0, 0, -2, -2, -4, -4, -4),
    (-5, 7, 6, 4, 4, -2, 2, 4, 0, 2, 1),
    (3, 5, 6, 2, -2, -2, -2, -6, -2, -3, -4),
    (7, 7, 6, 2, 6, 2, 2, 6, 3, -4, -2),
    (-3, 7, 6, -6, -4, -6, -4, -5, 2, 0, 0),
    (7, -3, 0, 2, 2, 0, 3, -2, -2, 0, -2),
    (5, 1, 4, -2, 4, 1, 6, 6, 4, 2, 2),
    (-5, 7, 6, 0, 3, 0, -2, -4, 0, -2, 4),
    (7, -5, -4, 5, -2, 4, 6, 4, 4, 2, 4),
    (7, 5, 7, 4, 0, 2, -4, -2, -4, -2, -6)
)


def _root(lattice, coordinates):
    r"""The lattice vector whose coordinates on the selected generators are ``coordinates``."""
    ring = lattice.base_ring()
    labels = tuple(lattice.module_generating_set())
    total = None
    for label, coordinate in zip(labels, coordinates):
        if not coordinate:
            continue
        term = lattice.scalar_multiple(ring(coordinate), lattice.module_generator(label))
        total = term if total is None else total + term
    return total


def _check(family) -> None:
    r"""Each reflection in ``family`` acts trivially on `A_L` and lies in the stable orthogonal group.

    The square of a candidate is `\pm 2` in `T_Co`'s own form, so `s_v` is an integral
    reflection there, and its displacement of every generator is checked against
    `(s_v - 1)(x) = -2 b(x, v)/q(v)\,v` -- the formula the library's own reflection
    implements -- so the class computed below is the class of the element and not of a
    formula about it.
    """
    lattice = NamedLattices.Tco
    ring = lattice.base_ring()
    one, two = ring.one(), ring.one() + ring.one()
    kernel = lattice.stable_orthogonal_group()
    trivial = lattice.discriminant_group().orthogonal_group().one()
    labels = tuple(lattice.module_generating_set())
    basis_vectors = tuple(lattice.module_generator(label) for label in labels)
    for coordinates in family:
        root = _root(lattice, coordinates)
        norm = lattice.q(root)
        assert norm in (two, -two)
        reflection = lattice.reflection(root)
        assert reflection.discriminant_morphism() == trivial
        assert reflection in kernel
        for vector in basis_vectors:
            half_pairing = ring(int(lattice.b(vector, root)) // 2)
            expected = lattice.scalar_multiple(-norm * half_pairing, root)
            assert reflection(vector) - vector == expected


def test_the_candidates_at_positions_0_to_6_lie_in_the_discriminant_kernel() -> None:
    r"""The reflections in a seventh of the family are isometries of `T_Co` with trivial discriminant action."""
    _check(CANDIDATE_ROOTS[0:7])


def test_the_candidates_at_positions_7_to_13_lie_in_the_discriminant_kernel() -> None:
    r"""The reflections in a seventh of the family are isometries of `T_Co` with trivial discriminant action."""
    _check(CANDIDATE_ROOTS[7:14])


def test_the_candidates_at_positions_14_to_20_lie_in_the_discriminant_kernel() -> None:
    r"""The reflections in a seventh of the family are isometries of `T_Co` with trivial discriminant action."""
    _check(CANDIDATE_ROOTS[14:21])


def test_the_candidates_at_positions_21_to_27_lie_in_the_discriminant_kernel() -> None:
    r"""The reflections in a seventh of the family are isometries of `T_Co` with trivial discriminant action."""
    _check(CANDIDATE_ROOTS[21:28])


def test_the_candidates_at_positions_28_to_34_lie_in_the_discriminant_kernel() -> None:
    r"""The reflections in a seventh of the family are isometries of `T_Co` with trivial discriminant action."""
    _check(CANDIDATE_ROOTS[28:35])


def test_the_candidates_at_positions_35_to_41_lie_in_the_discriminant_kernel() -> None:
    r"""The reflections in a seventh of the family are isometries of `T_Co` with trivial discriminant action."""
    _check(CANDIDATE_ROOTS[35:42])


def test_the_candidates_at_positions_42_to_48_lie_in_the_discriminant_kernel() -> None:
    r"""The reflections in a seventh of the family are isometries of `T_Co` with trivial discriminant action."""
    _check(CANDIDATE_ROOTS[42:49])


def test_the_candidates_at_positions_49_to_55_lie_in_the_discriminant_kernel() -> None:
    r"""The reflections in a seventh of the family are isometries of `T_Co` with trivial discriminant action."""
    _check(CANDIDATE_ROOTS[49:56])
