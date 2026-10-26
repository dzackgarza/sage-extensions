r"""The linear map underlying the projection of the fat point onto the reduced point."""

from sage_extensions.all import *  # noqa: F401,F403


def _fat_point_projection():
    r"""``QQ[x]/(x^2) -> QQ[x]/(x) = QQ``, the reduction of the fat point."""
    line = QQ["x"]
    x = line.gen()
    fat_point = line.quotient(line.ideal([x**2]))
    point = line.quotient(line.ideal([x]))
    projection = fat_point.Mor(point)({fat_point(x): point.zero()})
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
