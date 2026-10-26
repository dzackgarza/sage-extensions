r"""Direct and inverse images of submodules along a map of free modules."""

from sage_extensions.all import *  # noqa: F401,F403


def test_direct_image_is_left_adjoint_to_inverse_image_on_submodules() -> None:
    r"""For ``f: e1 |-> 2u, e2 |-> v`` on ``Z^2``: ``f^{-1}<4u, v> = <2e1, e2>``, of index 2.

    ``f_*`` is left adjoint to ``f^*`` on the posets of submodules:
    ``f(A) <= B`` iff ``A <= f^{-1}(B)``, checked on an ``A`` inside and an
    ``A`` outside; ``A <= f^{-1} f A`` and ``f f^{-1} B = B cap im f``.
    """
    source = Modules(ZZ)(ZZ**2)
    target = Modules(ZZ)(ZZ**2)
    e1, e2 = source.basis()
    u, v = target.basis()
    f = source.Mor(target)({e1: 2 * u, e2: v})
    adjunction = f.subobject_image_adjunction()
    direct = adjunction.left_adjoint()
    inverse = adjunction.right_adjoint()

    inside = source.span((2 * e1 + e2,))
    outside = source.span((e1,))
    b = target.span((4 * u, v))
    preimage = inverse(b)

    assert preimage.inclusion().index() == 2
    assert 2 * e1 in preimage.inclusion().image()
    assert e2 in preimage.inclusion().image()
    assert e1 not in preimage.inclusion().image()

    assert direct(inside) <= b
    assert inside <= preimage
    assert not direct(outside) <= b
    assert not outside <= preimage
    assert outside <= inverse(direct(outside))
    assert direct(preimage) <= b
    assert b <= direct(preimage)
    assert direct(source.span((e1, e2))).inclusion().index() == 2


def test_intersection_of_two_index_two_submodules_is_twice_the_lattice() -> None:
    r"""``<2e1, e2> cap <e1, 2e2> = 2Z^2``, of index 4 in ``Z^2``."""
    ambient = Modules(ZZ)(ZZ**2)
    e1, e2 = ambient.basis()
    left = ambient.span((2 * e1, e2))
    right = ambient.span((e1, 2 * e2))

    intersection = left.intersection(right)
    image = intersection.inclusion().image()

    assert intersection.inclusion().index() == 4
    assert 2 * e1 in image
    assert 2 * e2 in image
    assert e1 + e2 not in image
    assert e1 not in image
    assert e2 not in image
