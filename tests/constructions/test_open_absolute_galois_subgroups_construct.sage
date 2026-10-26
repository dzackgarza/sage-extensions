r"""The subgroup G_Q(i) of G_Q has index two and fixes the Gaussian rationals."""

from sage_extensions.all import *  # noqa: F401,F403


def test_gaussian_open_subgroup_retains_ambient_field_and_embedding_data() -> None:
    ambient = AbsoluteGaloisGroup(QQ)
    gaussian = QuadraticField(-1, "i")
    subgroup = ambient.open_subgroup(gaussian)
    inclusion = subgroup.inclusion()
    embedding = subgroup.embedding()

    assert subgroup in OpenAbsoluteGaloisSubgroups(ambient)
    assert subgroup.ambient() is ambient
    assert subgroup.fixed_field() is gaussian
    assert subgroup.index() == 2
    assert inclusion.domain() is subgroup
    assert inclusion.codomain() is ambient
    assert inclusion.is_injective()
    assert embedding.domain() is gaussian
    assert embedding.is_injective()


def test_cubic_open_subgroup_has_index_three() -> None:
    ambient = AbsoluteGaloisGroup(QQ)
    polynomial_ring = QQ.polynomial_ring("x")
    x = polynomial_ring.algebra_generator("x")
    cubic = (x**3 - 2).number_field("c")

    assert ambient.open_subgroup(cubic).index() == 3

