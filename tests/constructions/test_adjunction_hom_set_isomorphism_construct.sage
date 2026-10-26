r"""The free-module adjunction transposes maps of sets and module maps bijectively."""

from sage_extensions.all import *  # noqa: F401,F403


def test_free_module_adjunction_hom_set_isomorphism_round_trip() -> None:
    adjunction = Sets().free_module_adjunction(ZZ)
    two = Sets.Δ[1]
    point = Sets.Δ[0]
    line = adjunction.left_adjoint()(point)
    basis_vector = adjunction.unit(point)(point(0))
    values = Sets().Mor(two, adjunction.right_adjoint()(line))(
        lambda index: 2 * basis_vector if index == 0 else -basis_vector
    )
    transpose = adjunction.mor_set_isomorphism_inverse(values, line)
    recovered = adjunction.mor_set_isomorphism_forward(transpose, two)

    assert transpose(adjunction.unit(two)(two(0))) == 2 * basis_vector
    assert transpose(adjunction.unit(two)(two(1))) == -basis_vector
    assert recovered(two(0)) == values(two(0))
    assert recovered(two(1)) == values(two(1))
