r"""Archive reconciliation for discriminant normal forms and correlation maps."""

from sage_extensions.all import *


def _assert_form_isometry(normalization) -> None:
    source = normalization.domain()
    target = normalization.codomain()
    for generator in source.module_generators():
        assert normalization.inverse()(normalization(generator)) == generator
    for left in source.module_generators():
        for right in source.module_generators():
            assert source.b(left, right) == target.b(
                normalization(left), normalization(right)
            )


def test_archived_discriminant_normal_form_is_an_actual_form_isometry() -> None:
    for lattice in (Lattices.A2, Lattices.D4):
        form = lattice.discriminant_bilinear_form()
        normalization = form.normal_form()

        _assert_form_isometry(normalization)
        assert tuple(normalization.codomain().invariants()) == tuple(form.invariants())


def test_archived_invariant_factor_form_uses_a_minimal_framing_isometrically() -> None:
    form = Lattices.D4.discriminant_bilinear_form()
    normalization = form.invariant_factor_form()
    normalized = normalization.codomain()

    _assert_form_isometry(normalization)
    assert normalized.invariants() == form.invariants()
    assert normalized.module_generators().cardinality() == normalized.invariants().cardinality()


def test_archived_correlation_matrix_is_the_gram_matrix_and_dual_form_is_inverse() -> None:
    for lattice in (Lattices.A2, Lattices.D4, Lattices.U_2):
        correlation = lattice.correlation_morphism()
        linear = correlation.domain().module_category().Mor(
            correlation.domain(), correlation.codomain()
        )(correlation)
        gram = lattice.gram_matrix()

        assert linear.matrix() == gram
        assert lattice.dual_lattice().gram_matrix() == gram.inverse()


def test_archived_discriminant_of_a_direct_sum_has_the_two_primary_factors() -> None:
    left = Lattices.A2
    right = Lattices.A3
    combined = (left + right).discriminant_group()
    primary = combined.primary_components()

    assert combined.cardinality() == (
        left.discriminant_group().cardinality()
        * right.discriminant_group().cardinality()
    )
    assert primary[ZZ(3)].cardinality() == left.discriminant_group().cardinality()
    assert primary[ZZ(2)].cardinality() == right.discriminant_group().cardinality()
