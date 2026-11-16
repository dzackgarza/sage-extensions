r"""A finitely generated framed ring enumerates its points through its framing.

The framing of a free module gives each of its points coordinates in the base
ring, and enumerating those coordinates enumerates the module.  A ring that is
finitely generated and free over its base ring is such a module -- $\mathbf{Z}$
is free of rank one over itself and $\mathbf{Q}(i)$ is free of rank two over
$\mathbf{Q}$ -- so its points are enumerated, and each point the enumeration
yields is an element of the ring, built from the coordinates the framing gives
it.

What is asserted is that enumeration and not a listing of coordinates: every
point yielded is an element of the ring, the points are pairwise different, and
the point whose framing coordinates are $(1, 1)$ is the ring element
$1 + i$, not a pair of scalars read off a basis.

A ring whose framing has no finite basis is not enumerated by it: the general
ring states no enumeration of its points, and
``tests/rings/test_a_ring_states_no_enumeration_of_its_points.sage`` states that
of $\mathbf{Z}[x]$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_integers_enumerate_their_points_through_the_rank_one_framing() -> None:
    r"""$\mathbf{Z}$ is free of rank one over itself, so its frame lists its points.

    The framing is $\{1\}$, so a point's coordinates are a single integer $n$
    and the point is $n \cdot 1$.  The enumeration therefore lists integers,
    never coordinates: the first nine points are pairwise different elements of
    $\mathbf{Z}$, and the integers $-4, \ldots, 4$ are among them -- nine
    integer coordinates, nine points.
    """
    points = tuple(point for _, point in zip(range(9), ZZ))

    assert all(point in ZZ for point in points)
    assert all(
        point != other
        for position, point in enumerate(points)
        for other in points[:position]
    )
    assert all(
        any(point == ZZ(value) for point in points) for value in range(-4, 5)
    )


def test_the_gaussian_rationals_enumerate_their_points_through_their_framing() -> None:
    r"""$\mathbf{Q}(i)$ is free of rank two over $\mathbf{Q}$, framed by $\{1, i\}$.

    A point's coordinates $(a, b)$ are two rationals and the point is $a + b i$,
    an element of the field.  The enumeration lists field elements -- pairwise
    different, all of them in $\mathbf{Q}(i)$ -- and the four points whose
    coordinates lie in $\{0, 1\}$ are the field's $0$, $1$, $i$ and $1 + i$.
    """
    field = QuadraticField(-1)
    a = field.primitive_element()
    points = tuple(point for _, point in zip(range(25), field))

    assert a**2 == field(-1)
    assert all(point in field for point in points)
    assert all(
        point != other
        for position, point in enumerate(points)
        for other in points[:position]
    )
    assert all(
        any(point == value for point in points)
        for value in (field.zero(), field.one(), a, field(1 + a))
    )
