r"""A DGA identity retains its graded-algebra map and degreewise components."""

from sage_extensions.all import *  # noqa: F401,F403


def _de_rham_dga_identity():
    dga = QQ.polynomial_ring("x").de_rham_algebra()
    identity = DifferentialGradedAlgebras(QQ).Mor(dga, dga).identity()
    return dga, identity


def test_dga_identity_retains_underlying_graded_and_algebra_maps() -> None:
    dga, identity = _de_rham_dga_identity()
    underlying_graded = identity.underlying_graded_algebra_morphism()
    underlying_algebra = identity.underlying_algebra_morphism()
    x = dga(dga.de_rham_source_algebra().algebra_generator("x"))

    assert underlying_graded.domain() is dga
    assert underlying_graded.codomain() is dga
    assert underlying_graded(x) == x
    assert underlying_algebra(x) == x
    assert identity.degree_preservation_decision() is True
    assert identity.differential_compatibility_decision() is True


def test_dga_identity_component_is_identity_on_degree_zero() -> None:
    dga, identity = _de_rham_dga_identity()
    degree_zero = dga.graded_piece(0)
    component = identity.component(0)
    generator = degree_zero.module_generator(0)

    assert component.domain() is degree_zero
    assert component.codomain() is degree_zero
    assert component(generator) == generator


def test_dga_identity_composes_as_the_identity() -> None:
    dga, identity = _de_rham_dga_identity()
    composite = identity * identity
    x = dga(dga.de_rham_source_algebra().algebra_generator("x"))

    assert composite.domain() is dga
    assert composite.codomain() is dga
    assert composite(x) == x
    assert composite.differential_compatibility_decision() is True
