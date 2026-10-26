r"""The identity functor is a faithful object and arrow of its functor category."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_functor_is_faithful_and_lives_in_its_functor_category() -> None:
    identity = Sets().identity_functor()

    assert identity.is_faithful()
    assert identity.object() in identity.functor_category()


def test_identity_functor_arrow_retains_the_same_functor() -> None:
    identity = Sets().identity_functor()
    arrow = identity.arrow()

    assert arrow.domain() is Sets()
    assert arrow.codomain() is Sets()
    assert arrow.functor() is identity
