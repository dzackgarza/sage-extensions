r"""The radical of a degenerate lattice and the nondegenerate quotient."""

from sage_extensions.all import *  # noqa: F401,F403
import pytest


def test_affine_A1_lattice_modulo_its_radical_is_the_A1_root_lattice() -> None:
    r"""``[[2, -2], [-2, 2]]`` has radical ``Z(e1 + e2)``, and the quotient is ``<2> = A1``.

    ``b(e1 + e2, e_i) = 0``; in the quotient the class of ``e1`` has norm 2.
    """
    affine = Lattices(ZZ)([[2, -2], [-2, 2]])
    e1, e2 = affine.basis()
    radical = affine.radical()
    (r,) = radical.basis()
    quotient = affine.radical_quotient()
    projection = affine.radical_quotient_projection()

    assert not affine.is_nondegenerate()
    assert radical.module_rank() == 1
    assert radical.inclusion()(r) in (e1 + e2, -e1 - e2)
    assert radical.inclusion().is_primitive()
    assert quotient.module_rank() == 1
    assert quotient.is_nondegenerate()
    assert quotient.is_isometric_to(Lattices(ZZ)([[2]]))
    assert projection.domain() is affine
    assert projection.codomain() is quotient
    assert projection.module_morphism().is_surjective() is True
    assert projection.preserves_forms() is True
    assert projection.module_morphism().kernel().module_rank() == radical.module_rank() == 1
    assert projection(radical.inclusion()(r)) == quotient.zero()
    perpendicular = quotient.orthogonal_complement()
    inclusion = perpendicular.inclusion()
    reduction_projection = quotient.projection()
    for left in affine.module_generators():
        assert projection.module_morphism()(affine.unformed_module()(left)) == quotient._element_of_unformed_module(
            reduction_projection(inclusion.lift(left))
        )
        for right in affine.module_generators():
            assert quotient.b(projection(left), projection(right)) == affine.b(left, right)


def test_nondegenerate_hyperbolic_plane_has_zero_radical() -> None:
    r"""``U`` is unimodular, so its radical is 0 and ``U / rad U = U``."""
    u = Lattices(ZZ)("U")

    assert u.radical().module_rank() == 0
    assert u.radical_quotient().is_isometric_to(u)


def test_nonsymmetric_bilinear_form_does_not_descend_from_left_radical_alone() -> None:
    r"""Quotient descent must kill relations in both arguments of a bilinear form."""
    module = QQ ^ 2
    submodule = QQ ^ 1
    first_label = next(iter(module.module_generating_set()))
    inclusion = submodule.module_category().Mor(submodule, module)(
        lambda label: module.module_generator(first_label)
    )
    form = module.bilinear_forms(QQ)([[0, 0], [1, 0]])
    value_identity = QQ.module_category().Mor(QQ, QQ).identity()

    assert all(form(inclusion(submodule.module_generator(label)), module.module_generator(other)) == 0
               for label in submodule.module_generating_set()
               for other in module.module_generating_set())
    labels = tuple(module.module_generating_set())
    assert form(module.module_generator(labels[1]), module.module_generator(labels[0])) == 1
    assert form.descends_along(inclusion, value_identity) is False
    with pytest.raises(ValueError, match="both arguments"):
        form.descend_along(inclusion, value_identity)


def test_nonsymmetric_radical_quotient_kills_only_the_two_sided_radical() -> None:
    module = QQ ^ 2
    form = module.bilinear_forms(QQ)([[0, 0], [1, 0]])
    formed = FormModules(QQ)(form)

    assert formed.left_radical().module_rank() == 1
    assert formed.right_radical().module_rank() == 1
    assert formed.left_radical().intersection(formed.right_radical()).module_rank() == 0
    quotient = formed.radical_quotient()
    projection = formed.radical_quotient_projection()
    assert quotient.unformed_module().module_rank() == 2
    assert projection.module_morphism().is_injective() is True
    assert projection.module_morphism().is_surjective() is True
    for left in formed.module_generators():
        for right in formed.module_generators():
            assert quotient.b(projection(left), projection(right)) == formed.b(left, right)


def test_nonsymmetric_radical_quotient_drops_the_common_radical() -> None:
    module = QQ ^ 3
    form = module.bilinear_forms(QQ)(
        [[0, 0, 0], [0, 0, 0], [0, 1, 0]]
    )
    formed = FormModules(QQ)(form)
    common_radical = formed.left_radical().intersection(formed.right_radical())

    assert formed.left_radical().module_rank() == 2
    assert formed.right_radical().module_rank() == 2
    assert common_radical.module_rank() == 1
    quotient = formed.radical_quotient()
    projection = formed.radical_quotient_projection()
    assert quotient.unformed_module().module_rank() == 2
    assert quotient.is_symmetric() is False
    assert quotient.left_radical().intersection(quotient.right_radical()).module_rank() == 0
    assert projection.module_morphism().is_surjective() is True
    assert projection.module_morphism().kernel().module_rank() == 1
    for label in common_radical.module_generating_set():
        assert projection(common_radical.inclusion()(common_radical.module_generator(label))) == quotient.zero()
    for left in formed.module_generators():
        for right in formed.module_generators():
            assert quotient.b(projection(left), projection(right)) == formed.b(left, right)


def test_rational_nondegenerate_form_uses_full_rank_quotient_basis() -> None:
    r"""The field-specific quotient basis keeps all generators when the radical is zero."""
    module = QQ ^ 2
    formed = FormModules(QQ)(module.bilinear_forms(QQ)([[0, 1], [1, 0]]))
    quotient = formed.radical_quotient()
    projection = formed.radical_quotient_projection()

    assert formed.radical().module_rank() == 0
    assert quotient.unformed_module().module_rank() == 2
    assert quotient.gram_tensor().tensor_shape() == (2, 2)
    assert projection.module_morphism().is_injective() is True
    assert projection.module_morphism().is_surjective() is True
    assert quotient.is_isometric_to(formed)


def test_rational_zero_form_has_zero_rank_radical_quotient() -> None:
    r"""When the entire source is radical, the selected quotient basis is empty."""
    module = QQ ^ 3
    formed = FormModules(QQ)(module.bilinear_forms(QQ)([[0, 0, 0], [0, 0, 0], [0, 0, 0]]))
    quotient = formed.radical_quotient()
    projection = formed.radical_quotient_projection()

    assert formed.radical().module_rank() == 3
    assert quotient.unformed_module().module_rank() == 0
    assert quotient.gram_tensor().tensor_shape() == (0, 0)
    assert projection.domain() is formed
    assert projection.codomain() is quotient
    assert projection.module_morphism().is_surjective() is True
    assert projection.module_morphism().kernel().module_rank() == formed.radical().module_rank() == 3
    for generator in formed.module_generators():
        assert projection(generator) == quotient.zero()
    basis_map = quotient._preamble_radical_quotient_basis_map
    assert basis_map.domain().module_rank() == 0
    assert basis_map.codomain().module_rank() == 0


def test_rational_radical_quotient_rank_subtracts_higher_radical_rank() -> None:
    r"""A rank-four form with a two-dimensional radical descends to a hyperbolic plane."""
    module = QQ ^ 4
    form = module.bilinear_forms(QQ)(
        [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    )
    formed = FormModules(QQ)(form)
    quotient = formed.radical_quotient()
    projection = formed.radical_quotient_projection()

    assert formed.radical().module_rank() == 2
    assert quotient.unformed_module().module_rank() == 4 - 2
    assert quotient.gram_tensor().tensor_shape() == (2, 2)
    assert quotient.is_isometric_to(FormModules(QQ)(
        (QQ ^ 2).bilinear_forms(QQ)([[0, 1], [1, 0]])
    ))
    assert projection.module_morphism().is_surjective() is True
    assert projection.module_morphism().kernel().module_rank() == 2
    for left in formed.module_generators():
        for right in formed.module_generators():
            assert quotient.b(projection(left), projection(right)) == formed.b(left, right)
    lattice_quotient = Lattices(QQ)(quotient)
    assert lattice_quotient.unformed_module().module_rank() == 2
    assert lattice_quotient.gram_tensor().tensor_shape() == (2, 2)
    generators = tuple(lattice_quotient.module_generators())
    assert lattice_quotient.b(generators[0], generators[1]) == quotient.b(generators[0], generators[1])


def test_module_valued_radical_quotient_uses_selected_free_basis() -> None:
    r"""Field re-presentation also preserves forms whose values are modules, not rings."""
    module = QQ ^ 3
    values = QQ ^ 1
    scalar_form = module.bilinear_forms(QQ)([[0, 0, 0], [0, 0, 1], [0, 1, 0]])
    value_generator = values.module_generator(next(iter(values.module_generating_set())))
    form = module.bilinear_forms(values)(
        lambda left, right: value_generator * scalar_form(left, right)
    )
    formed = FormModules(QQ)(form)
    quotient = formed.radical_quotient()
    projection = formed.radical_quotient_projection()

    assert formed.radical().module_rank() == 1
    assert quotient.unformed_module().module_rank() == 2
    assert quotient.form().module() is quotient.unformed_module()
    assert quotient.value_module() is values
    assert projection.preserves_forms() is True
    assert quotient.b(
        projection(formed.module_generator(1)),
        projection(formed.module_generator(2)),
    ) == value_generator
    basis_map = quotient._preamble_radical_quotient_basis_map
    canonical_projection = quotient._preamble_radical_quotient_cokernel_projection
    source_module = formed.unformed_module()
    for label in source_module.module_generating_set():
        generator = source_module.module_generator(label)
        assert basis_map(projection.module_morphism()(generator)) == canonical_projection(generator)
    source_generators = tuple(formed.module_generators())
    for left in source_generators:
        for right in source_generators:
            assert quotient.b(projection(left), projection(right)) == formed.b(left, right)
    for label in formed.radical().module_generating_set():
        assert projection(formed.radical().inclusion()(formed.radical().module_generator(label))) == quotient.zero()


def test_rational_radical_quotient_retains_its_projection() -> None:
    r"""The quotient of the rank-three form with a one-dimensional radical has rank two."""
    lattice = Lattices(QQ)([[0, 0, 0], [0, 0, 1], [0, 1, 0]])
    quotient = lattice.radical_quotient()
    projection = lattice.radical_quotient_projection()
    assert lattice.radical_quotient_projection() is projection

    assert lattice.radical().module_rank() == 1
    assert quotient.module_rank() == 2
    assert projection.domain() is lattice
    assert projection.codomain() is quotient
    assert projection.module_morphism().domain() is lattice.unformed_module()
    assert projection.module_morphism().codomain() is quotient.unformed_module()
    assert projection.module_morphism().is_surjective() is True
    assert projection.module_morphism().kernel().module_rank() == lattice.radical().module_rank() == 1
    assert projection.module_morphism().kernel().is_isomorphic(lattice.radical())
    assert projection.preserves_forms() is True
    assert projection(lattice.module_generator(1)) != quotient.zero()
    assert quotient.b(
        projection(lattice.module_generator(1)),
        projection(lattice.module_generator(2)),
    ) == lattice.b(lattice.module_generator(1), lattice.module_generator(2)) == 1
    source_generators = tuple(lattice.module_generators())
    for left in source_generators:
        for right in source_generators:
            assert quotient.b(projection(left), projection(right)) == lattice.b(left, right)
    radical = lattice.radical()
    for label in radical.module_generating_set():
        assert projection(radical.inclusion()(radical.module_generator(label))) == quotient.zero()
    lattice_quotient = Lattices(QQ)(quotient)
    assert lattice_quotient.module_rank() == quotient.module_rank() == 2
    assert lattice_quotient.unformed_module().module_rank() == 2
    assert lattice_quotient.form().module() is lattice_quotient.unformed_module()
    assert lattice_quotient.gram_tensor().tensor_shape() == (2, 2)
    assert lattice_quotient.is_isometric_to(Lattices(QQ)([[0, 1], [1, 0]]))
    basis_map = quotient._preamble_radical_quotient_basis_map
    canonical_projection = quotient._preamble_radical_quotient_cokernel_projection
    assert canonical_projection.domain() is lattice.unformed_module()
    assert canonical_projection.codomain() is basis_map.codomain()
    for label in lattice.unformed_module().module_generating_set():
        generator = lattice.unformed_module().module_generator(label)
        assert basis_map(lattice.radical_quotient_projection().module_morphism()(generator)) == canonical_projection(generator)
    lattice_generators = tuple(lattice_quotient.module_generators())
    quotient_generators = tuple(quotient.module_generators())
    for i, left in enumerate(lattice_generators):
        for j, right in enumerate(lattice_generators):
            assert lattice_quotient.b(left, right) == quotient.b(
                quotient_generators[i], quotient_generators[j]
            )


def test_rational_formed_module_radical_quotient_retains_its_projection() -> None:
    r"""The generic formed-module quotient retains its map after basis re-presentation."""
    module = QQ ^ 3
    form = module.bilinear_forms(QQ)([[0, 0, 0], [0, 0, 1], [0, 1, 0]])
    formed = FormModules(QQ)(form)
    quotient = formed.radical_quotient()
    projection = formed.radical_quotient_projection()
    assert formed.radical_quotient_projection() is projection

    assert formed.radical().module_rank() == 1
    assert quotient.module_rank() == 2
    assert quotient.unformed_module().module_rank() == 2
    assert quotient.unformed_module() in FramedFreeModules(QQ)
    assert quotient.form().module() is quotient.unformed_module()
    assert quotient.gram_tensor().tensor_shape() == (2, 2)
    assert projection.domain() is formed
    assert projection.codomain() is quotient
    assert projection.module_morphism().is_surjective() is True
    assert projection.module_morphism().kernel().module_rank() == formed.radical().module_rank() == 1
    assert projection.preserves_forms() is True
    source_module = formed.unformed_module()
    basis_map = quotient._preamble_radical_quotient_basis_map
    canonical_projection = quotient._preamble_radical_quotient_cokernel_projection
    assert canonical_projection.domain() is source_module
    assert canonical_projection.codomain() is basis_map.codomain()
    assert canonical_projection.is_surjective() is True
    assert canonical_projection.kernel().module_rank() == formed.radical().module_rank() == 1
    assert canonical_projection.kernel().is_isomorphic(formed.radical())
    for label in basis_map.domain().module_generating_set():
        basis_generator = basis_map.domain().module_generator(label)
        assert basis_map.inverse()(basis_map(basis_generator)) == basis_generator
    for label in basis_map.codomain().module_generating_set():
        quotient_generator = basis_map.codomain().module_generator(label)
        assert basis_map(basis_map.inverse()(quotient_generator)) == quotient_generator
    for label in source_module.module_generating_set():
        generator = source_module.module_generator(label)
        assert basis_map(projection.module_morphism()(generator)) == canonical_projection(generator)
    assert quotient.b(
        projection(formed.module_generator(1)),
        projection(formed.module_generator(2)),
    ) == formed.b(formed.module_generator(1), formed.module_generator(2)) == 1
    source_generators = tuple(formed.module_generators())
    for left in source_generators:
        for right in source_generators:
            assert quotient.b(projection(left), projection(right)) == formed.b(left, right)
    for label in formed.radical().module_generating_set():
        assert projection(formed.radical().inclusion()(formed.radical().module_generator(label))) == quotient.zero()
    lattice_quotient = Lattices(QQ)(quotient)
    assert lattice_quotient.module_rank() == 2
    assert lattice_quotient.unformed_module().module_rank() == 2
    assert lattice_quotient.unformed_module() is quotient.unformed_module()
    assert lattice_quotient.gram_tensor().tensor_shape() == (2, 2)
    quotient_generators = tuple(lattice_quotient.module_generators())
    assert lattice_quotient.b(quotient_generators[0], quotient_generators[1]) == quotient.b(
        quotient_generators[0], quotient_generators[1]
    )
    assert lattice_quotient.is_isometric_to(Lattices(QQ)([[0, 1], [1, 0]]))
    lattice_projection = FormModules(QQ).Mor(lattice, lattice_quotient)(
        (
            projection.module_morphism(),
            lattice.value_module().module_category().Mor(
                lattice.value_module(), lattice.value_module()
            ).identity(),
        )
    )
    assert lattice_projection.domain() is lattice
    assert lattice_projection.codomain() is lattice_quotient
    assert lattice_projection.preserves_forms() is True
    for left in lattice.module_generators():
        for right in lattice.module_generators():
            assert lattice_quotient.b(lattice_projection(left), lattice_projection(right)) == lattice.b(left, right)
