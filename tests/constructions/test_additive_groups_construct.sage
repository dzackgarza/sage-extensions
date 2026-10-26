r"""The additive group of the integers has inverses and zero."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integers_form_an_additive_group() -> None:
    element = ZZ(7)

    assert ZZ in AdditiveGroups()
    assert element + (-element) == ZZ.zero()
    assert ZZ.zero() + element == element
    assert isinstance(element, ZZ.ElementType)

