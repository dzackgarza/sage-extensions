r"""The linear map underlying the projection of the fat point onto the reduced point."""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.algebras.algebras import Algebras


def _fat_point_projection():
    r"""``QQ[x]/(x^2) -> QQ[x]/(x) = QQ``, the reduction of the fat point.

    Both ends are their coefficient-ring views: the same rings over ``QQ``,
    retaining the quotient and with it the presentation ``QQ[x]/(x^2)`` that a
    map of ``QQ``-algebras out of the fat point is read against.
    """
    line = QQ["x"]
    x = line.gen()
    fat_point = line.quotient_ring(line.ideal([x**2])).as_algebra_over(QQ)
    point = line.quotient_ring(line.ideal([x])).as_algebra_over(QQ)
    projection = fat_point.Mor(point)(
        {label: point.zero() for label in fat_point.algebra_generating_set()}
    )
    return fat_point, point, projection


def test_projection_of_the_fat_point_sends_one_to_one_and_x_to_zero() -> None:
    r"""As a ``QQ``-linear map, ``a + bx ↦ a``."""
    fat_point, point, projection = _fat_point_projection()
    underlying = Algebras(QQ).underlying_module()(projection)
    x = fat_point(QQ["x"].gen())

    assert underlying(fat_point.one()) == point.one()
    assert underlying(x) == point.zero()
    assert underlying(3 + 5 * x) == 3 * point.one()


def test_kernel_of_the_fat_point_projection_is_the_line_spanned_by_the_nilpotent() -> None:
    r"""``ker(QQ[x]/(x^2) -> QQ) = QQ x``, of rank 1; the map is surjective, not injective."""
    fat_point, point, projection = _fat_point_projection()
    underlying = Algebras(QQ).underlying_module()(projection)
    kernel = underlying.kernel()
    x = fat_point(QQ["x"].gen())

    assert not underlying.is_injective()
    assert underlying.is_surjective()
    assert kernel.module_rank() == 1
    assert x in kernel
    assert fat_point.one() not in kernel
