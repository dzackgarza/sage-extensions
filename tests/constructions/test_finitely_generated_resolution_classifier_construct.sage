r"""Finite generation is classified by the target of a degree-zero resolution."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finitely_generated_resolution_classifier_is_the_target_projection() -> None:
    finitely_generated = Modules(ZZ).FinitelyGenerated()
    resolutions = finitely_generated.resolution_category()
    classifier = finitely_generated.resolution_classifier()

    assert classifier is resolutions.target_functor()
    assert classifier.domain() is resolutions
    assert classifier.codomain() is Modules(ZZ)
