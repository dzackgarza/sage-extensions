r"""Form modules retain their underlying modules, value module, and form morphism.

The hyperbolic plane gives a unimodular scalar-valued bilinear form with
isotropic basis vectors.  Its identity map is both a fixed-fibre formed morphism
and a fibrewise formed morphism over the identity of ``ZZ``.
"""

from sage_extensions.all import *  # noqa: F401,F403
import pytest


def _hyperbolic_form():
    module = ZZ.free_module(2)
    return FormModules(ZZ)(module.bilinear_hom_space(ZZ)([[0, 1], [1, 0]]))


def test_bilinear_hom_constructor_is_the_only_ingress_to_a_formed_module() -> None:
    module = ZZ.free_module(2)
    gram = tensor(ZZ, (), (2, 2), [[2, 1], [1, 2]])
    hom = module.bilinear_hom_space(ZZ)
    assert hom is module.bilinear_forms(ZZ)
    assert hom.domain() is module.tensor_product(module)

    b = hom(gram)
    formed = FormModules(ZZ)(b)
    assert formed.form() is b and formed.unformed_module() is module
    assert b._as_numerical_tensor() is gram

    with pytest.raises(TypeError):
        FormModules(ZZ)(gram)
    with pytest.raises(TypeError):
        FormModules(ZZ)(lambda x, y: ZZ.zero())
    with pytest.raises(TypeError):
        module.equip_bilinear_form(ZZ, gram)


def test_bilinear_hom_values_must_belong_to_the_base_module_category() -> None:
    module = ZZ.free_module(2)
    with pytest.raises(TypeError):
        module.bilinear_hom_space(QQ)
    with pytest.raises(TypeError):
        Modules(ZZ).Mor(module.tensor_product(module), QQ)


def test_callable_is_admitted_by_the_hom_and_finite_coordinates_are_lazy() -> None:
    module = ZZ.free_module(2)
    calls = []

    def bilinear(left, right):
        calls.append((left, right))
        return left.to_vector()(0) * right.to_vector()(1)

    b = module.bilinear_hom_space(ZZ)(bilinear)
    assert not calls
    assert b(module.module_generator(0), module.module_generator(1)) == ZZ.one()
    calls.clear()
    gram = b._as_numerical_tensor()
    assert gram == tensor(ZZ, (), (2, 2), [[0, 1], [0, 0]])
    assert len(calls) == 4
    assert b._as_numerical_tensor() is gram
    assert len(calls) == 4


def test_infinite_bilinear_hom_callable_never_requires_numerical_coordinates() -> None:
    module = ZZ.free_module(NN)
    b = module.bilinear_hom_space(ZZ)(
        lambda left, right: ZZ.one() if left == right else ZZ.zero()
    )
    assert b(module.module_generator(0), module.module_generator(0)) == ZZ.one()
    assert b(module.module_generator(0), module.module_generator(1)) == ZZ.zero()
    with pytest.raises(TypeError):
        b._as_numerical_tensor()
    assert FormModules(ZZ)(b).unformed_module() is module


def test_form_module_retains_unformed_left_right_and_value_modules() -> None:
    form = _hyperbolic_form()
    module = form.unformed_module()

    assert form in FormModules(ZZ)
    assert form.left_module() is module
    assert form.right_module() is module
    assert form.value_module() == ZZ.regular_module()
    assert form.form().codomain() == form.value_module()
    assert isinstance(form.module_generator(0), form.ElementType)


def test_form_pairing_norm_gram_and_element_predicates_have_hyperbolic_values() -> None:
    form = _hyperbolic_form()
    e, f = form.module_generator(0), form.module_generator(1)

    assert form.b(e, f) == form.pairing(e, f) == ZZ.one()
    assert form.norm(e) == form.q(e) == ZZ.zero()
    assert e.b(f) == ZZ.one()
    assert e.q() == ZZ.zero()
    assert e.is_isotropic()
    assert e.is_orthogonal_to(e)
    assert not e.is_orthogonal_to(f)
    assert e.represents(ZZ.zero())
    assert form.gram_tensor() == tensor(ZZ, (), (2, 2), [[0, 1], [1, 0]])


def test_form_index_raising_lowering_twist_and_fraction_field_raise() -> None:
    form = _hyperbolic_form()
    vector = tensor.vector(ZZ, [3, 7])
    covector = tensor.covector(ZZ, [3, 7])
    twisted = form.twist(3)
    rational = NondegenerateGenericFibreFormModules(ZZ)(form).raise_index_over_fraction_field(covector)

    assert form.lower_index(vector) == tensor.covector(ZZ, [7, 3])
    assert form.raise_index(covector) == tensor.vector(ZZ, [7, 3])
    assert rational == tensor.vector(QQ, [QQ(7), QQ(3)])
    assert twisted.b(twisted.module_generator(0), twisted.module_generator(1)) == 3


def test_scaling_bilinear_forms_retains_the_original_module_and_selected_hom() -> None:
    module = ZZ.free_module(2)
    symmetric = module.equip_bilinear_form(module.bilinear_hom_space(ZZ)([[2, 1], [1, 2]]))
    asymmetric = module.equip_bilinear_form(module.bilinear_hom_space(ZZ)([[1, 2], [0, 1]]))
    symmetry = BilinearFormModules(ZZ).Symmetric()

    for formed in (symmetric, asymmetric):
        triple = formed.twist(3)
        sextuple = triple.twist(2)
        assert triple.unformed_module() is module
        assert triple.form().parent() is formed.form().parent()
        assert sextuple.unformed_module() is module
        assert sextuple.form().parent() is formed.form().parent()
        assert triple.gram_tensor() == 3 * formed.gram_tensor()
        assert sextuple.gram_tensor() == 6 * formed.gram_tensor()
        assert (triple in symmetry) == (formed in symmetry)
        assert triple.twist(ZZ.one()) is triple
        assert triple.twist(-3).gram_tensor() == -9 * formed.gram_tensor()


def test_zero_scaling_of_a_unimodular_form_preserves_symmetry_not_nondegeneracy() -> None:
    lattice = Lattices(ZZ)("U")
    zero = lattice.twist(0)

    assert zero.unformed_module() is lattice.unformed_module()
    assert zero.gram_tensor() == tensor(ZZ, (), (2, 2), [[0, 0], [0, 0]])
    assert zero in BilinearFormModules(ZZ).Symmetric()
    assert zero in Lattices(ZZ).Even().FinitelyGenerated()
    assert not zero.is_nondegenerate()
    assert zero.b(zero.module_generator(0), zero.module_generator(1)) == 0


def test_lattice_scalar_twists_transport_evenness_and_unimodularity_axioms() -> None:
    lattices = Lattices(ZZ)
    form_modules = FormModules(ZZ)
    plane = lattices("U")
    sign_change = plane.twist(-1)
    doubled = plane.twist(2)

    assert sign_change in lattices.Even().FinitelyGenerated()
    assert sign_change in form_modules.Unimodular()
    assert sign_change.is_unimodular()
    assert doubled in lattices.Even().FinitelyGenerated()
    assert doubled in form_modules.Nondegenerate()
    assert doubled not in form_modules.Unimodular()
    assert not doubled.is_unimodular()


def test_finite_free_bilinear_form_is_unimodular_exactly_for_unit_determinant() -> None:
    module = ZZ.free_module(2)
    for gram, expected in (
        ([[1, 0], [0, 1]], True),
        ([[1, 2], [3, 5]], True),
        ([[2, 1], [1, 2]], False),
    ):
        formed = module.equip_bilinear_form(module.bilinear_hom_space(ZZ)(gram))
        assert formed.is_unimodular() is expected
        assert formed.twist(-1).is_unimodular() is expected


def test_even_unimodular_rank_28_twists_retain_the_original_module_and_form_classifier() -> None:
    lattices = Lattices(ZZ)
    hyperbolic = lattices("U")
    negative_e8 = lattices("E8").twist(-1)
    lattice = hyperbolic + hyperbolic + negative_e8 + negative_e8 + negative_e8
    doubled = lattice.twist(2)
    sextuple = doubled.twist(3)

    assert lattice.module_rank() == cardinal(28)
    assert doubled.unformed_module() is lattice.unformed_module()
    assert doubled.form().parent() is lattice.form().parent()
    assert sextuple.unformed_module() is lattice.unformed_module()
    assert sextuple.form().parent() is lattice.form().parent()
    assert doubled.gram_tensor() == 2 * lattice.gram_tensor()
    assert sextuple.gram_tensor() == 6 * lattice.gram_tensor()
    assert doubled in SymmetricBilinearFormModules(ZZ)
    assert doubled.is_even() and doubled.is_nondegenerate()
    assert not doubled.is_unimodular()


def test_countable_rank_lattice_twist_retains_its_pairing_rule_without_enumerating_a_gram() -> None:
    lattice = Lattices(ZZ)(ZZ**NN)
    doubled = lattice.twist(2)
    sextuple = doubled.twist(3)

    assert not lattice.module_rank().is_finite()
    assert doubled.unformed_module() is lattice.unformed_module()
    assert sextuple.unformed_module() is lattice.unformed_module()
    assert doubled.form_scale() == ZZ(2)
    assert sextuple.form_scale() == ZZ(6)
    assert doubled.basis_vector(0) ** 2 == ZZ(2)
    assert sextuple.basis_vector(1) ** 2 == ZZ(6)
    assert doubled.b(doubled.basis_vector(1), doubled.basis_vector(2)) == ZZ.zero()
    assert doubled.is_even() and doubled.is_nondegenerate()
    assert not lattice.is_unimodular()
    assert not doubled.is_unimodular()
    assert doubled.twist(1) is doubled


def test_finite_bilinear_hom_retains_its_actual_defining_covariant_tensor() -> None:
    module = ZZ.free_module(2)
    gram = tensor(ZZ, (), (2, 2), [[2, 1], [1, 2]])
    bilinear = module.bilinear_forms(ZZ)(gram)
    formed = module.equip_bilinear_form(module.bilinear_hom_space(ZZ)(gram))

    assert bilinear.gram_tensor() is gram
    assert formed.form().gram_tensor() is gram
    assert formed.gram_tensor() is gram
    assert bilinear.domain() is module.tensor_product(module)
    assert bilinear(module.module_generator(0), module.module_generator(1)) == ZZ.one()
    assert formed.twist(3).form().gram_tensor() is formed.twist(3).gram_tensor()


def test_finite_module_valued_bilinear_hom_keeps_selected_pair_coordinates() -> None:
    module = ZZ.free_module(2)
    target = ZZ.free_module(1)
    e = target.module_generator(0)
    pairing = module.bilinear_forms(target)([[e, 2*e], [3*e, 4*e]])
    selected = pairing.coordinate_values()

    for pair in pairing.domain().module_generating_set():
        x = int(pair.component(0))
        y = int(pair.component(1))
        assert selected[pair] == (1 + 2*x + y)*e
        assert pairing(module.module_generator(x), module.module_generator(y)) == selected[pair]


def test_finite_bilinear_tensor_respects_actual_selected_generator_labels() -> None:
    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

    labels = finite_ordered_set(("left", "right"))
    module = ZZ.free_module(labels)
    gram = tensor(ZZ, (), (2, 2), [[1, 2], [3, 4]])
    pairing = module.bilinear_forms(ZZ)(gram)
    e = module.module_generator(labels[0])
    f = module.module_generator(labels[1])

    assert pairing.gram_tensor() is gram
    assert pairing(e, f) == ZZ(2)
    assert pairing(f, e) == ZZ(3)


def test_integrality_of_finite_scalar_valued_form_reads_the_selected_tensor() -> None:
    module = ZZ.free_module(2)
    integral_gram = tensor(QQ, (), (2, 2), [[1, 0], [0, 2]])
    nonintegral_gram = tensor(QQ, (), (2, 2), [[QQ(1)/2, 0], [0, 2]])
    values = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(QQ)
    integral = module.equip_bilinear_form(module.bilinear_hom_space(values)(integral_gram))
    nonintegral = module.equip_bilinear_form(module.bilinear_hom_space(values)(nonintegral_gram))

    assert integral.form().gram_tensor() is integral_gram
    assert nonintegral.form().gram_tensor() is nonintegral_gram
    assert integral.is_base_ring_valued()
    assert not nonintegral.is_base_ring_valued()


def test_form_base_change_keeps_the_pairing_over_the_rationals() -> None:
    form = _hyperbolic_form()
    inclusion = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    changed = form.base_change(inclusion)

    assert changed in FormModules(QQ)
    assert changed.b(changed.module_generator(0), changed.module_generator(1)) == QQ.one()


def test_fixed_and_fibered_formed_identity_morphisms_preserve_the_form() -> None:
    form = _hyperbolic_form()
    module = form.unformed_module()
    values = form.value_module()
    module_identity = Modules(ZZ).Mor(module, module).identity()
    value_identity = values.Mor(values).identity()
    fixed = form.formed_mor(module_identity, value_identity)
    fibered = form.fibered_formed_mor(
        form,
        ZZ.Mor(ZZ).identity(),
        module_identity,
        value_identity,
    )

    assert fixed in form.Mor(form)
    assert fibered.domain() is form
    assert fibered.codomain() is form
    assert fixed.preserves_form_exactly()
    assert fibered.preserves_form_exactly()
    assert form.Mono(form).identity().preserves_form_exactly()
