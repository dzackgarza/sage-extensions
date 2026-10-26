from sage_extensions.all import *  # noqa: F403


def test_fraction_field_transpose_is_indexed_by_the_stated_source_order() -> None:
    field = QuadraticField(2, "a")
    maximal_order = field.ring_of_integers()
    nonmaximal_order = field.order_generated_by(2 * field.primitive_element())
    adjunction = Orders().fraction_field_adjunction()
    fraction_field = adjunction.left_adjoint()

    assert maximal_order is not nonmaximal_order
    assert fraction_field(maximal_order) is field
    assert fraction_field(nonmaximal_order) is field

    identity = field.Mor(field).identity()
    maximal_restriction = adjunction.mor_set_isomorphism_forward(
        identity,
        maximal_order,
    )
    nonmaximal_restriction = adjunction.mor_set_isomorphism_forward(
        identity,
        nonmaximal_order,
    )

    assert maximal_restriction.domain() is maximal_order
    assert nonmaximal_restriction.domain() is nonmaximal_order
    assert maximal_restriction.codomain() is maximal_order
    assert nonmaximal_restriction.codomain() is maximal_order
    for basis_element in nonmaximal_order.integral_basis():
        assert nonmaximal_restriction(basis_element) == maximal_order(
            basis_element
        )

    recovered = adjunction.mor_set_isomorphism_inverse(nonmaximal_restriction, field)
    assert recovered(field.primitive_element()) == field.primitive_element()


