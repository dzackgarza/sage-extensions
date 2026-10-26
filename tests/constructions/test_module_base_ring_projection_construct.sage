r"""The varying-ring module projection sends each module to its scalar ring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_module_base_ring_projection_has_the_expected_domain_and_codomain() -> None:
    projection = ModuleBaseRingProjection()

    assert projection.domain() is ModulesOverCommutativeRings()
    assert projection.codomain() is CommutativeRings()


def test_module_base_ring_projection_sends_a_free_integer_module_to_zz() -> None:
    projection = ModuleBaseRingProjection()
    module = ZZ.free_module(2)

    assert projection(module) is ZZ
