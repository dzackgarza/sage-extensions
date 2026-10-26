r"""Local rings at primes of the cusp ``y^3 = x^2`` and of the axes ``xy = 0``.

At the origin ``m = (x, y)`` of the cusp the residue field is ``Q`` and the residue
map is evaluation at the origin: ``x -> 0`` and ``x + 1 -> 1``.  The local ring is
not a field, since ``x`` is a nonzero nonunit, and the origin has height one on
the one-dimensional cusp.

On the axes ``A = Q[x, y]/(xy)``, localizing at the prime ``(x)`` inverts ``y``, so
``x = (xy)/y = 0`` there and ``A_(x) = Q(y)`` is a field.
"""

from sage_extensions.all import *  # noqa: F401,F403


def cusp():
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    return plane.quotient_by_relations([x**2 - y**3])


def test_the_residue_map_at_the_origin_of_the_cusp_is_evaluation_at_the_origin() -> None:
    ring = cusp()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    local = ring.localize_at_prime(ring.ideal(x, y))
    residue = local.residue_map()
    residue_field = local.residue_field()

    assert residue(local(x)) == residue_field.zero()
    assert residue(local(y)) == residue_field.zero()
    assert residue(local(x + ring.one())) == residue_field.one()
    assert not local.is_field()


def test_the_origin_of_the_cusp_has_height_one() -> None:
    ring = cusp()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")

    assert ring.spectrum()(ring.ideal(x, y)).height() == 1


def test_the_maximal_ideal_of_the_local_ring_at_the_origin_contains_x_and_y() -> None:
    ring = cusp()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    local = ring.localize_at_prime(ring.ideal(x, y))

    assert local(x) in local.maximal_ideal()
    assert local(x + ring.one()) not in local.maximal_ideal()


def test_the_local_ring_of_the_axes_at_one_line_is_a_field() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations([x * y])
    local = axes.localize_at_prime(axes.ideal(axes.algebra_generator("x")))

    assert local.is_field()
    assert local(axes.algebra_generator("y")).is_unit()
    assert local(axes.algebra_generator("x")) == local.zero()


def test_the_source_residue_map_of_the_cusp_sends_x_plus_two_to_two() -> None:
    ring = cusp()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    local = ring.localize_at_prime(ring.ideal(x, y))

    assert local.source_residue_map()(x + 2 * ring.one()) == 2 * local.residue_field().one()
