r"""A cohomology-algebra morphism retains the DGA morphism that induces it."""

from sage_extensions.all import *  # noqa: F401,F403


def _de_rham_cohomology_identity():
    dga = QQ.polynomial_ring("x").de_rham_algebra()
    cohomology = dga.cohomology_algebra()
    identity = CohomologyAlgebras(QQ).Mor(cohomology, cohomology).identity()
    return dga, cohomology, identity


def test_cohomology_identity_retains_its_inducing_dga_identity() -> None:
    dga, cohomology, identity = _de_rham_cohomology_identity()
    underlying = identity.underlying_dga_morphism()

    assert underlying.domain() is dga
    assert underlying.codomain() is dga
    assert underlying.differential_compatibility_decision() is True
    assert identity.domain() is cohomology
    assert identity.codomain() is cohomology


def test_cohomology_morphism_composition_composes_the_inducing_dga_maps() -> None:
    dga, _cohomology, identity = _de_rham_cohomology_identity()
    composite = identity * identity
    underlying = composite.underlying_dga_morphism()

    assert underlying.domain() is dga
    assert underlying.codomain() is dga
    assert underlying.differential_compatibility_decision() is True
