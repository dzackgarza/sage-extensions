r"""The \(2U \oplus K\) Eichler model: \(2U\) as the determinant form on \(M_2(\mathbb Z)\)
with \(\mathrm{SL}_2(\mathbb Z) \times \mathrm{SL}_2(\mathbb Z)\) acting by
\((g, h)\cdot X = g X h^{-1}\), and \(O(K)\) acting on the complement."""

from sage_extensions.all import *


def test_the_left_and_right_SL2_actions_are_homomorphisms_that_commute() -> None:
    r"""\(\det(gXh^{-1}) = \det X\), so both actions are isometric; left and right
    multiplication commute by associativity."""
    model = Lattices(ZZ)("A1").two_u_eichler_model()
    group = model.special_linear_group()
    first, second = group.group_generators()[0], group.group_generators()[1]
    identity = model.lattice().O().one()

    assert model.left_action(first * second) == model.left_action(first) * model.left_action(second)
    assert model.right_action(first * second) == model.right_action(first) * model.right_action(second)
    assert model.left_action(~first) == ~model.left_action(first)
    assert model.right_action(~first) == ~model.right_action(first)
    assert model.left_action(group.one()) == identity
    assert model.right_action(group.one()) == identity
    assert model.left_action(first) != identity

    for left_generator in (first, second):
        for right_generator in (first, second):
            assert (
                model.left_action(left_generator) * model.right_action(right_generator)
                == model.right_action(right_generator) * model.left_action(left_generator)
            )


def test_both_SL2_factors_fix_the_complement_pointwise() -> None:
    model = Lattices(ZZ)("A1").two_u_eichler_model()
    lattice = model.lattice()
    inclusion = lattice.injection(2)

    for group_element in model.special_linear_group().group_generators():
        for generator in model.orthogonal_complement().module_generators():
            embedded = inclusion(generator)
            assert model.left_action(group_element)(embedded) == embedded
            assert model.right_action(group_element)(embedded) == embedded


def test_eichler_transvections_in_the_complement_directions_are_stable_isometries() -> None:
    r"""An Eichler transvection \(E_{e,k}\) with \(e\) isotropic and \(k \perp e\) fixes
    \(e\) and acts trivially on \(L^\vee/L\) (Eichler; Gritsenko–Hulek–Sankaran,
    Invent. Math. 169 (2007), §3)."""
    model = Lattices(ZZ)("A1").two_u_eichler_model()
    lattice = model.lattice()
    isotropic = model.hyperbolic_basis()[0]
    identity_discriminant_action = lattice.O().one().discriminant_morphism()

    for transvection in model.complement_eichler_transvections():
        assert transvection in lattice.O()
        assert transvection(isotropic) == isotropic
        assert transvection.discriminant_morphism() == identity_discriminant_action


def test_approximate_generating_family_uses_exact_two_u_perpendicular_frames() -> None:
    model = Lattices(ZZ)("A2").two_u_eichler_model()
    lattice = model.lattice()
    family = model.approximate_generating_family()
    isometries = tuple(family)
    linear_generators = tuple(model.special_linear_group().group_generators())
    e, f, e_prime, f_prime = model.hyperbolic_basis()
    complement = model.orthogonal_complement()
    inclusion = model.complement_inclusion()
    embedded = tuple(inclusion(point) for point in complement.module_generators())
    perpendicular_frames = (
        (e, e_prime, f_prime),
        (f, e_prime, f_prime),
        (e, f, e_prime),
        (e, f, f_prime),
    )

    assert all(model.left_action(generator) in isometries for generator in linear_generators)
    assert all(model.right_action(generator) in isometries for generator in linear_generators)
    assert all(
        model.eichler_transvection(isotropic, orthogonal) in isometries
        for isotropic, frame in zip(
            model.hyperbolic_basis(),
            perpendicular_frames,
            strict=True,
        )
        for orthogonal in (*frame, *embedded)
    )
    assert all(isometry in lattice.O() for isometry in isometries)


def test_base_changed_eichler_generators_are_scalar_extensions() -> None:
    model = Lattices(ZZ)("A2").two_u_eichler_model()
    source = model.lattice()
    ring_map = ZZ.fraction_field_map()
    target = source.base_change(ring_map)
    source_family = model.approximate_generating_family()
    target_family = model.approximate_generating_family_after_base_change(ring_map)
    source_labels = tuple(source.module_generating_set())
    target_labels = tuple(target.module_generating_set())

    def scalar_extend(element):
        coordinates = element.to_vector()
        return target.linear_combination(
            {
                target_label: ring_map(coordinates(source_label))
                for source_label, target_label in zip(
                    source_labels,
                    target_labels,
                    strict=True,
                )
                if coordinates(source_label)
            }
        )

    assert source_family.index_set() == target_family.index_set()
    for label in source_family.index_set():
        for source_generator, target_generator in zip(
            source.module_generators(),
            target.module_generators(),
            strict=True,
        ):
            assert target_family[label](target_generator) == scalar_extend(
                source_family[label](source_generator)
            )


def test_minus_one_on_A2_extends_by_the_identity_and_acts_nontrivially_on_the_discriminant() -> None:
    r"""\(-1\) acts on \(A_{A_2} \cong \mathbb Z/3\) by \(-1 \ne 1\)."""
    complement = Lattices(ZZ)("A2")
    model = complement.two_u_eichler_model()
    lattice = model.lattice()
    minus_one = complement.O()(tuple(-generator for generator in complement.module_generators()))
    lifted = model.complement_action(minus_one)

    for hyperbolic_generator in model.hyperbolic_basis():
        assert lifted(hyperbolic_generator) == hyperbolic_generator
    inclusion = lattice.injection(2)
    for generator in complement.module_generators():
        assert lifted(inclusion(generator)) == inclusion(minus_one(generator))

    assert model.complement_action(complement.O().one()) == lattice.O().one()
    assert model.complement_action(minus_one * minus_one) == lifted * lifted
    assert lifted.discriminant_morphism() != lattice.O().one().discriminant_morphism()


def test_covering_classes_of_2U_plus_A2_have_primitive_roots_of_matching_divisibility() -> None:
    r"""For primitive \(v\), \(v/\operatorname{div}(v)\) is a discriminant class of order
    \(\operatorname{div}(v)\); the covering classes are those represented this way."""
    complement = Lattices(ZZ)("A2")
    model = complement.two_u_eichler_model()
    representatives = model.covering_vector_representatives(ZZ(-2))

    assert representatives.cardinality() > 0
    for discriminant_class in representatives.index_set():
        vector = representatives[discriminant_class]
        assert vector.q() == -2
        assert vector.is_primitive()
        assert vector.div() == discriminant_class.additive_order()
        assert discriminant_class in complement.covering_discriminant_classes(ZZ(-2))


def test_2U_plus_E8_has_one_covering_class_of_square_two() -> None:
    r"""\(2U \oplus E_8\) is unimodular, so every primitive vector has divisibility 1 and
    by Eichler's criterion the primitive vectors of square 2 form one orbit."""
    model = Lattices(ZZ)("E8").two_u_eichler_model()
    representatives = model.covering_vector_representatives(ZZ(2))

    assert representatives.cardinality() == 1
    vector = next(iter(representatives))
    assert vector.q() == 2
    assert vector.div() == 1
    assert vector.is_primitive()


def test_O_of_2U_plus_A2_surjects_onto_O_of_its_discriminant_form() -> None:
    r"""\(L = 2U \oplus A_2\) is even indefinite with \(\operatorname{rk} L \ge
    \ell(A_L) + 2\), so \(O(L) \to O(A_L)\) is surjective (Nikulin, Integral
    symmetric bilinear forms, Thm. 1.14.2)."""
    model = Lattices(ZZ)("A2").two_u_eichler_model()
    lattice = model.lattice()
    target = lattice.discriminant_group().O()
    lifts = lattice.O().discriminant_orthogonal_group_generator_lifts()

    group_generators = target.group_generators()
    assert lifts.index_set() == group_generators.index_set()
    for label in lifts.index_set():
        witness = lifts.value(label)
        assert witness in lattice.O()
        assert witness.discriminant_morphism() == group_generators.value(label)
