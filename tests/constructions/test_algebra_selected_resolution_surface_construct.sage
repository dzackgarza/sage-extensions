r"""A framed algebra exposes its selected algebra-resolution data coherently."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polynomial_algebra_selected_resolution_controls_generators_and_framing() -> None:
    algebra = QQ.polynomial_ring("x")
    owner = Algebras(QQ).Associative().Unital().Commutative()
    resolution = algebra.selected_algebra_resolution()
    labels = algebra.algebra_generating_set()
    label = labels[0]
    x = algebra.algebra_generator(label)

    assert algebra.algebra_framing_owner() is owner
    assert resolution.target() is algebra
    assert algebra.algebra_framing_source() is resolution.level(0)
    assert algebra.algebra_framing_morphism() is resolution.augmentation()
    module_resolution = algebra.selected_module_resolution()
    assert module_resolution.target() is algebra
    assert module_resolution.level(0) is algebra.framing_source()
    assert module_resolution.augmentation().domain() is algebra.framing_source()
    assert module_resolution.augmentation().codomain() is algebra
    assert algebra.number_of_algebra_generators() == cardinal(1)
    assert algebra.finite_algebra_generators().cardinality() == cardinal(1)
    assert algebra.product_on_algebra_generators(label, label) == x * x
