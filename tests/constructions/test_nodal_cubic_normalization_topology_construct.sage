r"""The rational nodal cubic retains the pointed topology of its P1 normalization."""

from sage_extensions.all import *  # noqa: F401,F403


def test_nodal_cubic_normalization_morphism_has_the_expected_source() -> None:
    topology = NodalCubicIntegralTopology()
    normalization = topology.normalization_scheme()
    morphism = topology.normalization_morphism()

    assert morphism.domain() is normalization
    assert morphism.codomain() is topology.scheme()


def test_nodal_cubic_normalization_pointed_fundamental_group_is_trivial() -> None:
    topology = NodalCubicIntegralTopology()
    fundamental_group = topology.normalization_fundamental_group()

    assert fundamental_group.space() is topology.normalization_scheme()
    assert fundamental_group.base_point() is topology.normalization_base_point()
    assert fundamental_group.group().order() == 1


def test_normalization_induces_the_pointed_fundamental_group_map() -> None:
    topology = NodalCubicIntegralTopology()
    induced = topology.normalization_fundamental_group_map()

    assert induced.domain() is topology.normalization_fundamental_group().group()
    assert induced.codomain() is topology.fundamental_group().group()
