r"""Finite presentation is classified by the target of a degree-one resolution."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finitely_presented_resolution_classifier_is_the_target_projection() -> None:
    finitely_presented = Modules(ZZ).FinitelyPresented()
    resolutions = finitely_presented.resolution_category()
    classifier = finitely_presented.resolution_classifier()

    assert classifier is resolutions.target_functor()
    assert classifier.domain() is resolutions
    assert classifier.codomain() is Modules(ZZ)
