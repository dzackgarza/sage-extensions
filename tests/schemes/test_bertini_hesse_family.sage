r"""The Hesse pencil of plane cubics \(x^3+y^3+z^3 - 3t\,xyz\) and its discriminant."""

from sage_extensions.all import *


def test_the_hesse_pencil_has_discriminant_t_cubed_minus_one() -> None:
    r"""The member \(x^3+y^3+z^3-3t\,xyz\) is singular exactly when \(t^3 = 1\) (over the affine parameter line):
    \(t = 0\) is the smooth Fermat cubic, and at \(t = 1\) the cubic factors as
    \((x+y+z)(x^2+y^2+z^2-xy-yz-zx)\).

    Source: Artebani--Dolgachev, *The Hesse pencil of plane cubic curves*, arXiv:math/0611590, §2.
    """
    family = HesseBertiniFamily()

    assert family.discriminant() == family.parameter() ** 3 - family.parameter_ring().one()
    assert family.parameter_is_good(QQ.zero())
    assert not family.parameter_is_good(QQ.one())


def test_the_general_hesse_member_is_a_smooth_cubic_and_the_exceptional_member_is_singular() -> None:
    r"""Both are plane cubics (degree \(3\)); the general member is smooth, the exceptional member is not.

    Source: Artebani--Dolgachev, *The Hesse pencil of plane cubic curves*, arXiv:math/0611590, §2.
    """
    family = HesseBertiniFamily()
    smooth = family.general_member()
    singular = family.exceptional_member()

    assert tuple(smooth.defining_degrees()) == (3,)
    assert tuple(singular.defining_degrees()) == (3,)
    assert smooth.is_smooth()
    assert not singular.is_smooth()
