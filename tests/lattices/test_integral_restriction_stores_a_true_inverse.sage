r"""``integral_restriction``'s fast path stores an inverse that is one.

On finite equal ranks over the owned integers the unimodular reading builds the
backward factor by inverting the coordinate matrix.  The forward pass fills
``coordinates`` with the images in its *rows* (row ``i`` is the image of the
``i``-th source generator), so the backward images are the rows of the inverse,
not its columns: the columns give ``(F^-1)^T``, which is the inverse exactly
when the coordinate matrix is symmetric.  ``-id`` and a root reflection in a
symmetric frame are symmetric, so they pass either way, and the two lattices of
the congruence test are read through two *separate* calls rather than through
the stored backward — which is why the defect survived those specimens.

An ``A_2`` simple-root reflection is the discriminating specimen: in the
simple-root basis its coordinate matrix ``[[-1, 1], [0, 1]]`` is not symmetric,
it is integral, and its determinant is ``-1``, so the fast path runs.  Its
stored inverse must be its inverse, on both generators and in both
compositions.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


@pytest.mark.parametrize("ring", (ZZ, QQ, RR), ids=("integral", "rational", "exact-real"))
def test_composition_carries_the_actual_basis_through_distinct_isometric_presentations(ring) -> None:
    r"""The maps e->u, f->-v and u->x+y, v->y compose to e->x+y, f->-y."""
    source = Lattices(ring)([[2, -1], [-1, 2]], module_generators=("east", "north"))
    middle = Lattices(ring)([[2, 1], [1, 2]], module_generators=("up", "right"))
    target = Lattices(ring)([[2, -1], [-1, 2]], module_generators=("west", "south"))
    e, f = tuple(source.module_generators())
    u, v = tuple(middle.module_generators())
    x, y = tuple(target.module_generators())
    first = source.Isom(middle)(dict(zip(tuple(source.module_generating_set()), (u, -v), strict=True)))
    second = middle.Isom(target)(dict(zip(tuple(middle.module_generating_set()), (x + y, y), strict=True)))

    composite = second * first

    assert composite.domain() is source
    assert composite.codomain() is target
    assert composite(e) == x + y
    assert composite(f) == -y
    for point in (e, f, 2 * e - 3 * f):
        assert composite(point) == second(first(point))
        assert (~composite)(composite(point)) == point


@pytest.mark.parametrize("ring", (ZZ, QQ), ids=("integral", "rational"))
def test_the_a2_coxeter_inverse_has_its_prescribed_basis_action(ring) -> None:
    r"""For g(e)=f, g(f)=-e-f, the inverse sends e to -e-f and f to e."""
    lattice = Lattices(ring)([[2, -1], [-1, 2]], module_generators=("east", "north"))
    labels = tuple(lattice.module_generating_set())
    e, f = tuple(lattice.module_generators())
    coxeter = lattice.Isom(lattice)({labels[0]: f, labels[1]: -e - f})

    inverse = ~coxeter

    assert inverse(e) == -e - f
    assert inverse(f) == e
    for point in (e, f, 2 * e - 3 * f):
        assert inverse(coxeter(point)) == point
        assert coxeter(inverse(point)) == point


def test_a_non_symmetric_unimodular_isometry_stores_its_true_inverse() -> None:
    r"""The ``A_2`` reflection ``alpha_1 |-> -alpha_1``, ``alpha_2 |-> alpha_1 + alpha_2``."""
    lattice = Lattices(ZZ)([[2, -1], [-1, 2]])
    space = lattice.vector_space()
    first, second = tuple(space.module_generating_set())
    alpha_1, alpha_2 = space.module_generator(first), space.module_generator(second)
    reflection = space.Isom(space)(
        {
            first: space.scalar_multiple(QQ(-1), alpha_1),
            second: alpha_1 + alpha_2,
        }
    )
    for left, right in ((first, first), (first, second), (second, second)):
        grown = (space.module_generator(left), space.module_generator(right))
        assert space.b(reflection(grown[0]), reflection(grown[1])) == space.b(*grown)

    restricted = lattice.integral_isometry(reflection)
    integral_first, integral_second = tuple(lattice.module_generating_set())
    e_1, e_2 = lattice.module_generator(integral_first), lattice.module_generator(integral_second)
    assert restricted(e_1) == lattice.scalar_multiple(ZZ(-1), e_1)
    assert restricted(e_2) == e_1 + e_2

    inverse = restricted.inverse()
    assert inverse(restricted(e_1)) == e_1
    assert inverse(restricted(e_2)) == e_2
    assert restricted(inverse(e_1)) == e_1
    assert restricted(inverse(e_2)) == e_2
    assert inverse(lattice.scalar_multiple(ZZ(-1), e_1)) == e_1
    assert inverse(e_1 + e_2) == e_2


def test_a_non_symmetric_cycle_of_order_three_stores_its_true_inverse() -> None:
    r"""The ``A_2`` Coxeter element ``alpha_1 |-> alpha_2``, ``alpha_2 |-> -alpha_1 - alpha_2``."""
    lattice = Lattices(ZZ)([[2, -1], [-1, 2]])
    space = lattice.vector_space()
    first, second = tuple(space.module_generating_set())
    alpha_1, alpha_2 = space.module_generator(first), space.module_generator(second)
    coxeter = space.Isom(space)(
        {
            first: alpha_2,
            second: space.scalar_multiple(QQ(-1), alpha_1 + alpha_2),
        }
    )
    for left, right in ((first, first), (first, second), (second, second)):
        grown = (space.module_generator(left), space.module_generator(right))
        assert space.b(coxeter(grown[0]), coxeter(grown[1])) == space.b(*grown)

    restricted = lattice.integral_isometry(coxeter)
    integral_first, integral_second = tuple(lattice.module_generating_set())
    e_1, e_2 = lattice.module_generator(integral_first), lattice.module_generator(integral_second)
    assert restricted(e_1) == e_2
    assert restricted(e_2) == lattice.scalar_multiple(ZZ(-1), e_1 + e_2)

    inverse = restricted.inverse()
    assert inverse(restricted(e_1)) == e_1
    assert inverse(restricted(e_2)) == e_2
    assert restricted(inverse(e_1)) == e_1
    assert restricted(inverse(e_2)) == e_2
    # the cube is the identity, reached through the returned arrows
    images = (e_1, e_2)
    for _ in range(3):
        images = tuple(inverse(value) for value in (restricted(images[0]), restricted(images[1])))
    assert images == (e_1, e_2)


def test_a_rank_three_non_symmetric_cycle_stores_its_true_inverse() -> None:
    r"""A three-cycle of ``<2> + <2> + <2>``: non-symmetric in rank three as well."""
    lattice = Lattices(ZZ)([[2, 0, 0], [0, 2, 0], [0, 0, 2]])
    space = lattice.vector_space()
    first, second, third = tuple(space.module_generating_set())
    cycle = space.Isom(space)(
        {
            first: space.module_generator(second),
            second: space.module_generator(third),
            third: space.module_generator(first),
        }
    )
    restricted = lattice.integral_isometry(cycle)
    integral_first, integral_second, integral_third = tuple(lattice.module_generating_set())
    e_1 = lattice.module_generator(integral_first)
    e_2 = lattice.module_generator(integral_second)
    e_3 = lattice.module_generator(integral_third)
    assert restricted(e_1) == e_2
    assert restricted(e_2) == e_3
    assert restricted(e_3) == e_1

    inverse = restricted.inverse()
    assert inverse(e_1) == e_3
    assert inverse(e_2) == e_1
    assert inverse(e_3) == e_2
    for value in (e_1, e_2, e_3):
        assert inverse(restricted(value)) == value
        assert restricted(inverse(value)) == value
    # the fourth power is the identity, reached through the returned arrows
    images = (e_1, e_2, e_3)
    for _ in range(3):
        images = tuple(restricted(value) for value in images)
    assert images == (e_1, e_2, e_3)
