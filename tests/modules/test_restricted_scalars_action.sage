r"""The restricted-scalars action multiplies by the image of the scalar.

``Res_{ZZ -> QQ}(QQ)`` is the field read over the integers: ``r`` acts as
multiplication by ``r`` in ``QQ``.  The action is the extension module's action
composed with the retained scalar map, so the arithmetic is the field's,
``2 * (1/2) = 1``, and not a reconstruction from ``ZZ``-coordinates.
"""

from sage_extensions.all import *


def test_the_restricted_scalars_action_multiplies_by_the_image_of_the_scalar() -> None:
    view = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(QQ)
    action = view.scalar_action()
    group = view.underlying_additive_group()
    half = group(QQ(1) / 2)
    assert view.module_over_extension() is QQ
    assert action.domain() is ZZ
    assert action(ZZ(2))(half) == group(QQ.one())
    assert action(ZZ(3))(half) == group(QQ(3) / 2)
    assert action(ZZ(-1))(half) == group(-QQ(1) / 2)


def test_the_restricted_scalars_scalar_multiple_agrees_with_the_action() -> None:
    view = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(QQ)
    element = view(QQ(1) / 2)
    assert view.scalar_multiple(ZZ(2), element) == view(QQ.one())
    assert ZZ(2) * element == view(QQ.one())
