from sage_extensions.all import *


def test_subobject_orthogonal_complement_defers_to_the_inclusion() -> None:
    lattice = Lattices(ZZ)(3)
    e0, e1, e2 = lattice.module_generators()
    subobject = lattice.subobject_on((e0 + e1,))

    perpendicular = subobject.orthogonal_complement()
    via_inclusion = subobject.inclusion().orthogonal_complement()

    assert perpendicular.inclusion().codomain() is lattice
    assert via_inclusion.inclusion().codomain() is lattice
    assert perpendicular.module_rank() == 2
    assert all(
        subobject.inclusion()(source).b(perpendicular.inclusion()(target)) == 0
        for source in subobject.module_generators()
        for target in perpendicular.module_generators()
    )
    assert perpendicular.inclusion().is_in_image(e0 - e1)
    assert perpendicular.inclusion().is_in_image(e2)


def test_discriminant_class_constructs_an_overlattice_inclusion() -> None:
    lattice = Lattices(ZZ)([[8]])
    discriminant = lattice.discriminant_module()
    class_generator = discriminant.module_generator(
        next(iter(discriminant.module_generating_set()))
    )

    inclusion = lattice.overlattice(4 * class_generator)

    assert inclusion.domain() is lattice
    assert inclusion.index() == 2
    assert inclusion.codomain().gram_tensor()[0, 0] == 2


def test_the_complement_of_the_image_of_a_noninjective_map_into_U_is_the_isotropic_line() -> None:
    r"""\(x, y \mapsto e\) has image \(\mathbb Z e\); in \(U\), \(e^\perp = \mathbb Z e\)
    because \(b(ae + bf, e) = b\)."""
    source = Modules(ZZ)(ZZ**2)
    plane = Lattices(ZZ)("U")
    e, f = plane.module_generators()
    x, y = source.module_generators()
    morphism = source.Mor(plane)({x: e, y: e})

    perpendicular = morphism.orthogonal_complement()

    assert perpendicular.module_rank() == 1
    assert perpendicular.is_totally_isotropic()
    assert perpendicular.inclusion().is_in_image(e)
    assert not perpendicular.inclusion().is_in_image(f)


def test_isotropic_reduction_of_a_line_in_u_plus_u_is_u() -> None:
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    isotropic_vector = lattice.module_generators()[0]
    isotropic_line = lattice.subobject_on((isotropic_vector,))

    reduction = isotropic_line.isotropic_reduction()

    assert reduction.module_rank() == 2
    assert reduction.gram_tensor() == tensor(ZZ, (), (2, 2), [[0, 1], [1, 0]])
    assert reduction.signature_pair() == signature_pair(1, 1)
    assert reduction.is_unimodular()


def test_primitive_a1_and_a2_complements_in_e8_have_e7_and_e6_discriminants() -> None:
    e8 = Lattices(ZZ)("E8")
    module_generators = e8.module_generators()

    a1 = e8.subobject_on((module_generators[0],))
    e7 = a1.orthogonal_complement()

    assert a1.is_primitive()
    assert e7.is_primitive()
    assert e7.module_rank() == 7
    assert abs(e7.determinant()) == 2
    e7_factors = e7.discriminant_module().invariant_factors()
    assert e7_factors.cardinality() == 1
    assert e7_factors[0] == 2

    adjacent_pair = next(
        (module_generators[left_position], module_generators[right_position])
        for left_position in range(int(module_generators.cardinality()))
        for right_position in range(left_position + 1, int(module_generators.cardinality()))
        if module_generators[left_position].b(
            module_generators[right_position]
        ) != 0
    )
    a2 = e8.subobject_on(adjacent_pair)
    e6 = a2.orthogonal_complement()

    assert a2.is_primitive()
    assert e6.is_primitive()
    assert e6.module_rank() == 6
    assert abs(e6.determinant()) == 3
    e6_factors = e6.discriminant_module().invariant_factors()
    assert e6_factors.cardinality() == 1
    assert e6_factors[0] == 3


def test_diagonal_isotropic_class_glues_a1_four_to_an_index_two_even_overlattice() -> None:
    a1 = Lattices(ZZ)("A1")
    lattice = a1 + a1 + a1 + a1
    discriminant = lattice.discriminant_module()

    factors = discriminant.invariant_factors()
    assert factors.cardinality() == 4
    assert all(factor == 2 for factor in factors)
    diagonal_class = sum(discriminant.module_generators(), discriminant.zero())

    assert diagonal_class.additive_order() == 2
    assert diagonal_class.q() == discriminant.quadratic_value_module().zero()

    inclusion = lattice.overlattice(diagonal_class)
    overlattice = inclusion.codomain()

    assert inclusion.index() == 2
    assert overlattice.module_rank() == 4
    assert overlattice.is_even()
    assert abs(overlattice.determinant()) == 4
    overlattice_factors = overlattice.discriminant_module().invariant_factors()
    assert overlattice_factors.cardinality() == 2
    assert all(factor == 2 for factor in overlattice_factors)


def test_nonprincipal_ideal_in_q_sqrt_minus_five_has_a_computable_fractional_inverse() -> None:
    field = QuadraticField(-5, "a")
    a = field.primitive_element()
    order = field.ring_of_integers()
    ideal = order.ideal(2, 1 + a)

    assert field.class_number() == 2
    assert not ideal.is_principal()
    assert ideal in ProjectiveModules(order)
    assert order(2) in ideal
    assert order(1 + a) in ideal
    assert order.one() not in ideal

    inverse = ~ideal
    assert not inverse.is_principal()
    assert inverse in ProjectiveModules(order)

    product = ideal * inverse
    assert product.is_principal()
    assert product.principal_generator().is_unit()
    assert order.one() in product


def test_ZZ_sqrt5_is_a_nonmaximal_order_missing_the_golden_ratio() -> None:
    r"""\((1+\sqrt5)/2\) is a root of \(x^2 - x - 1\), so it is integral but not in
    \(\mathbb Z[\sqrt5]\); \(\operatorname{disc}\mathbb Z[\sqrt5] = 20 = 2^2\cdot 5\)
    while \(\operatorname{disc}\mathbb Q(\sqrt5) = 5\) (Neukirch, ANT, I.2)."""
    field = QuadraticField(5, "a")
    a = field.primitive_element()
    order = field.order_generated_by(a)
    golden_ratio = (1 + a) / 2

    assert not order.is_maximal()
    assert golden_ratio not in order
    assert golden_ratio in field.maximal_order()
    assert field.maximal_order().is_maximal()
    assert field.discriminant() == 5


def test_real_quadratic_field_has_exact_embeddings_and_its_actual_galois_group() -> None:
    field = QuadraticField(5, "a")

    images = field.embedding_images(AA)
    assert field.embedding_images(AA).cardinality() == 2
    assert all(image**2 == 5 for image in images)
    assert sum(images) == 0
    assert field.ramified_primes() == Set((ZZ(5),))

    galois_group = field.galois_group()
    assert galois_group.cardinality() == field.degree() == 2


def test_swap_involution_on_u_is_an_automorphism_with_rank_one_invariants_and_coinvariants() -> None:
    group = Groups.C(2)
    plane = Lattices(ZZ)("U")
    labels = plane.module_generating_set()
    first, second = plane.module_generators()
    swap_isometry = plane.Aut()({labels[0]: second, labels[1]: first})

    def swap(group_element, vector):
        if group_element == group.one():
            return vector
        return swap_isometry(vector)

    group_lattice = Lattices(ZZ[group])(plane, swap)
    involution = group_lattice.group().group_generators()[0]

    assert group_lattice.action().domain() is group
    assert group_lattice.action().codomain() is group_lattice.Aut()
    action = group_lattice.action_of(involution)
    assert action.parent() is group_lattice.Aut()
    left, right = group_lattice.module_generators()
    assert action(left) == right
    assert action(right) == left
    assert group_lattice.is_invariant(group_lattice((1, 1)))
    assert not group_lattice.is_invariant(group_lattice((1, -1)))

    invariants = group_lattice.module_invariants()
    coinvariants = group_lattice.module_coinvariants()
    assert invariants.module_rank() == 1
    assert coinvariants.module_rank() == 1
    assert coinvariants.is_torsion_free()
