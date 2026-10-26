r"""Limits, colimits and adjunctions among modules, group modules, orders and groups."""

from sage_extensions.all import *  # noqa: F401,F403


def _swap_module():
    r"""``ZZ^2 = ZZ e ⊕ ZZ f`` with ``C_2`` acting by ``e ↔ f``."""
    group = Groups.C(2)
    module = Modules(ZZ).free_module(("e", "f"))
    e, f = module.module_generator("e"), module.module_generator("f")
    swap = module.Mor(module)({e: f, f: e})
    action = group.Mor(module.Aut())({group.group_generators()[0]: swap})
    return group, Modules(ZZ[group])(module, action)


def test_equalizer_of_id_and_minus_id_on_zz_is_zero_and_coequalizer_is_z2() -> None:
    r"""``Eq(id, -id) = {x : x = -x} = 0`` and ``Coeq(id, -id) = ZZ/(2) `` on ``ZZ``."""
    line = Modules(ZZ).free_module(("e",))
    e = line.module_generator("e")
    identity = line.Mor(line).identity()
    negation = line.Mor(line)({e: -e})

    assert Modules(ZZ).equalizer(identity, negation).module_rank() == 0
    factors = Modules(ZZ).coequalizer(identity, negation).invariant_factors()
    assert factors.cardinality() == 1
    assert factors[0] == 2


def test_klein_four_sign_action_has_zero_invariants_and_coinvariants_z2_squared() -> None:
    r"""``V_4 = <a, b>`` acting on ``ZZ^2`` by ``a = diag(-1, 1)``, ``b = diag(1, -1)``:
    ``M^G = 0`` and ``M_G = M/(2e, 2f) = (ZZ/2)^2``."""
    group = Groups.V4()
    a, b = tuple(group.group_generators())
    module = Modules(ZZ).free_module(("e", "f"))
    e, f = module.module_generator("e"), module.module_generator("f")
    action = group.Mor(module.Aut())({a: module.Mor(module)({e: -e, f: f}), b: module.Mor(module)({e: e, f: -f})})
    acted = Modules(ZZ[group])(module, action)

    assert acted.module_invariants().module_rank() == 0
    factors = acted.module_coinvariants().invariant_factors()
    assert factors.cardinality() == 2
    assert tuple(factors) == (2, 2)


def test_free_module_on_a_set_is_left_adjoint_to_the_underlying_set() -> None:
    r"""``F ⊣ U`` for ``F : Sets -> Mod_ZZ``: ``φ : F{x, y} -> ZZ^2``, ``x ↦ a + b``,
    ``y ↦ 2a`` corresponds to the function ``x ↦ a + b``, ``y ↦ 2a`` and back;
    the unit and counit are natural and both triangle identities hold."""
    adjunction = Sets().free_module_adjunction(ZZ)
    free, underlying = adjunction.left_adjoint(), adjunction.right_adjoint()
    labels = Sets()(("x", "y"))
    module = Modules(ZZ).free_module(("a", "b"))
    a, b = module.module_generator("a"), module.module_generator("b")
    free_labels = free(labels)
    phi = free_labels.Mor(module)({free_labels.module_generator("x"): a + b, free_labels.module_generator("y"): 2 * a})

    transpose = adjunction.mor_set_isomorphism_forward(phi, labels)
    assert transpose(labels("x")) == a + b
    assert transpose(labels("y")) == 2 * a
    recovered = adjunction.mor_set_isomorphism_inverse(transpose, module)
    assert recovered(free_labels.module_generator("y")) == 2 * a

    source_set, target_set = Sets()((1, 2)), Sets()((3, 4))
    set_map = Sets().Mor(source_set, target_set)(lambda value: target_set(3) if value == 1 else target_set(4))
    left, right = adjunction.unit_transformation().naturality_square(set_map)
    for element in source_set:
        assert left(element) == right(element)

    triangle = underlying(adjunction.counit(module)) * adjunction.unit(underlying(module))
    for probe in (a, b, a + b):
        assert triangle(probe) == probe
    other_triangle = adjunction.counit(free(source_set)) * free(adjunction.unit(source_set))
    for generator in free(source_set).module_generators():
        assert other_triangle(generator) == generator


def test_restriction_along_zz_to_zz_sqrt2_doubles_rank_and_is_right_adjoint_to_extension() -> None:
    r"""For ``O = ZZ[sqrt 2]``: restriction of scalars sends ``O^1`` to ``ZZ^2``;
    ``O ⊗_ZZ - ⊣ Res``: ``O ⊗ ZZ^2 -> O``, ``u ↦ p``, ``v ↦ 2p`` round-trips through
    the bijection; unit and counit are natural; both triangle identities hold."""
    order = QuadraticField(2, "a").ring_of_integers()
    structure_map = order.algebra_structure_morphism()
    adjunction = Modules(ZZ).base_change_adjunction(structure_map)
    extension, restriction = adjunction.left_adjoint(), adjunction.right_adjoint()
    source = Modules(ZZ).free_module(("u", "v"))
    target = Modules(order).free_module(("p",))
    p = target.module_generator("p")
    extended_source, restricted_target = extension(source), restriction(target)

    assert restricted_target.module_rank() == 2
    phi = extended_source.Mor(target)({
        extended_source.module_generator("u"): p,
        extended_source.module_generator("v"): 2 * p,
    })
    recovered = adjunction.mor_set_isomorphism_inverse(adjunction.mor_set_isomorphism_forward(phi, source), target)
    for generator in extended_source.module_generators():
        assert recovered(generator) == phi(generator)

    line = Modules(ZZ).free_module(("r",))
    r = line.module_generator("r")
    left, right = adjunction.unit_transformation().naturality_square(
        source.Mor(line)({source.module_generator("u"): r, source.module_generator("v"): 2 * r})
    )
    for generator in source.module_generators():
        assert left(generator) == right(generator)

    first_triangle = restriction(adjunction.counit(target)) * adjunction.unit(restricted_target)
    for generator in restricted_target.module_generators():
        assert first_triangle(generator) == generator
    second_triangle = adjunction.counit(extended_source) * extension(adjunction.unit(source))
    for generator in extended_source.module_generators():
        assert second_triangle(generator) == generator


def test_invariants_of_the_swap_are_zz_times_e_plus_f_and_right_adjoint_to_trivial_action() -> None:
    r"""For ``C_2`` swapping ``e, f``: ``M^G = ZZ(e + f)`` of rank 1, and
    ``triv ⊣ (-)^G`` with both triangle identities."""
    group, acted = _swap_module()
    e, f = acted.module_generator("e"), acted.module_generator("f")
    adjunction = Modules(ZZ).trivial_invariants_adjunction(group)
    invariants = adjunction.right_adjoint()(acted)

    assert invariants.module_rank() == 1
    assert e + f in invariants
    assert e not in invariants
    assert e - f not in invariants

    source = Modules(ZZ).free_module(("n",))
    trivial_source = adjunction.left_adjoint()(source)
    equivariant = trivial_source.Mor(acted)({trivial_source.module_generator("n"): e + f})
    transpose = adjunction.mor_set_isomorphism_forward(equivariant, source)
    recovered = adjunction.mor_set_isomorphism_inverse(transpose, acted)
    assert recovered(trivial_source.module_generator("n")) == e + f

    first_triangle = adjunction.right_adjoint()(adjunction.counit(acted)) * adjunction.unit(invariants)
    for generator in invariants.module_generators():
        assert first_triangle(generator) == generator
    second_triangle = adjunction.counit(trivial_source) * adjunction.left_adjoint()(adjunction.unit(source))
    for generator in trivial_source.module_generators():
        assert second_triangle(generator) == generator


def test_coinvariants_of_the_swap_identify_e_and_f_and_are_left_adjoint_to_trivial_action() -> None:
    r"""For ``C_2`` swapping ``e, f``: ``M_G = M/(e - f) ≅ ZZ``, the unit sends ``e``
    and ``f`` to the same class, and ``(-)_G ⊣ triv`` with both triangle identities."""
    group, acted = _swap_module()
    e, f = acted.module_generator("e"), acted.module_generator("f")
    adjunction = Modules(ZZ[group]).coinvariants_trivial_adjunction()
    coinvariants = adjunction.left_adjoint()(acted)
    unit = adjunction.unit(acted)

    assert coinvariants.module_rank() == 1
    assert unit(e) == unit(f)
    assert unit(e) != unit(e).parent().zero()

    target = Modules(ZZ).free_module(("n",))
    trivial_target = adjunction.right_adjoint()(target)
    first_triangle = adjunction.right_adjoint()(adjunction.counit(target)) * adjunction.unit(trivial_target)
    for generator in trivial_target.module_generators():
        assert first_triangle(generator) == generator
    second_triangle = adjunction.counit(coinvariants) * adjunction.left_adjoint()(unit)
    for generator in coinvariants.module_generators():
        assert second_triangle(generator) == generator


def test_coefficient_extension_of_a_group_module_to_zz_sqrt2_has_restriction_of_rank_four() -> None:
    r"""Extending the swap module ``ZZ^2`` along ``ZZ -> ZZ[sqrt 2]`` gives ``O^2`` with
    ``C_2`` still swapping; restricting back gives ``ZZ^4``; the extension of
    multiplication by 2 is multiplication by 2; both triangle identities hold."""
    group, acted = _swap_module()
    order = QuadraticField(2, "a").ring_of_integers()
    adjunction = Modules(ZZ[group]).coefficient_base_change_adjunction(order.algebra_structure_morphism())
    extension, restriction = adjunction.left_adjoint(), adjunction.right_adjoint()
    extended = extension(acted)
    restricted = restriction(extended)
    doubling = acted.Mor(acted)({acted.module_generator("e"): 2 * acted.module_generator("e"), acted.module_generator("f"): 2 * acted.module_generator("f")})

    assert restricted.module_rank() == 4
    for generator in extended.module_generators():
        assert extension(doubling)(generator) == 2 * generator
    first_triangle = restriction(adjunction.counit(extended)) * adjunction.unit(restricted)
    for generator in restricted.module_generators():
        assert first_triangle(generator) == generator
    second_triangle = adjunction.counit(extended) * extension(adjunction.unit(acted))
    for generator in extended.module_generators():
        assert second_triangle(generator) == generator


def test_tensor_symmetric_and_exterior_algebras_differ_on_the_image_of_a_product() -> None:
    r"""For ``f : ZZ^2 -> ZZ^2``, ``x ↦ u + v``, ``y ↦ 2v``: ``F(f)(xy) = (u + v)(2v)``,
    which is ``2uv + 2v⊗v`` in ``T``, ``2uv + 2v^2`` in ``Sym``, and ``2 u∧v`` in ``Λ``
    (``v ∧ v = 0``)."""
    source = Modules(ZZ).free_module(("x", "y"))
    target = Modules(ZZ).free_module(("u", "v"))
    f = source.Mor(target)({
        source.module_generator("x"): target.module_generator("u") + target.module_generator("v"),
        source.module_generator("y"): 2 * target.module_generator("v"),
    })

    for functor, has_square in (
        (Modules(ZZ).tensor_algebra(), True),
        (Modules(ZZ).symmetric_algebra(), True),
        (Modules(ZZ).exterior_algebra(), False),
    ):
        x, y = functor(source).algebra_generator("x"), functor(source).algebra_generator("y")
        u, v = functor(target).algebra_generator("u"), functor(target).algebra_generator("v")
        assert functor(f)(x * y) == 2 * u * v + 2 * v * v
        assert (v * v != functor(target).zero()) == has_square
    exterior = Modules(ZZ).exterior_algebra()
    u, v = exterior(target).algebra_generator("u"), exterior(target).algebra_generator("v")
    x, y = exterior(source).algebra_generator("x"), exterior(source).algebra_generator("y")
    assert exterior(f)(x * y) == 2 * u * v


def test_fraction_field_is_left_adjoint_to_ring_of_integers_with_embedding_naturality_and_triangles() -> None:
    field = QuadraticField(2, "a")
    order = field.ring_of_integers()
    adjunction = Orders().fraction_field_adjunction()
    fraction_field = adjunction.left_adjoint()
    ring_of_integers = adjunction.right_adjoint()

    assert fraction_field(order) is field
    assert ring_of_integers(field) is order

    identity = fraction_field(order).Mor(field).identity()
    restricted = adjunction.mor_set_isomorphism_forward(identity, order)
    recovered = adjunction.mor_set_isomorphism_inverse(restricted, field)
    for basis_element in order.integral_basis():
        assert restricted(basis_element) == basis_element
    assert recovered(field.primitive_element()) == field.primitive_element()

    conjugation = next(
        embedding
        for embedding in field.Mor(field).embeddings()
        if embedding(field.primitive_element()) != field.primitive_element()
    )
    left, right = adjunction.counit_transformation().naturality_square(conjugation)
    assert left(field.primitive_element()) == right(field.primitive_element())

    restricted_conjugation = ring_of_integers(conjugation)
    left, right = adjunction.unit_transformation().naturality_square(
        restricted_conjugation
    )
    for basis_element in order.integral_basis():
        assert left(basis_element) == right(basis_element)

    first_triangle = ring_of_integers(adjunction.counit(field)) * adjunction.unit(
        ring_of_integers(field)
    )
    for basis_element in order.integral_basis():
        assert first_triangle(basis_element) == basis_element

    second_triangle = adjunction.counit(fraction_field(order)) * fraction_field(
        adjunction.unit(order)
    )
    assert second_triangle(field.primitive_element()) == field.primitive_element()


def test_abelianization_is_left_adjoint_to_the_inclusion_of_abelian_groups() -> None:
    group = Groups.S(3)
    target = Groups.C(6)
    adjunction = Groups().abelianization_adjunction()
    abelianization = adjunction.left_adjoint()(group)

    assert abelianization.order() == 2
    assert abelianization.is_abelian()

    unit = adjunction.unit(group)
    group_generators = group.group_generators()
    assert unit(group_generators[0]) == abelianization.one()
    assert unit(group_generators[1]) != abelianization.one()

    target_generator = target.group_generators()[0]

    assert adjunction.right_adjoint()(target) is target
    sign_to_six = group.Mor(target)(
        {
            group_generators[0]: target.one(),
            group_generators[1]: target_generator**3,
        }
    )
    factored = adjunction.mor_set_isomorphism_inverse(sign_to_six, target)
    recovered = adjunction.mor_set_isomorphism_forward(factored, group)
    for generator in group_generators:
        assert recovered(generator) == sign_to_six(generator)

    conjugation = group.Aut().one()
    assert conjugation in group.Mor(group)
    left, right = adjunction.unit_transformation().naturality_square(conjugation)
    for generator in group_generators:
        assert left(generator) == right(generator)

    target_endomorphism = target.Mor(target)(
        {target_generator: target_generator**5}
    )
    left, right = adjunction.counit_transformation().naturality_square(
        target_endomorphism
    )
    for element in left.domain():
        assert left(element) == right(element)

    first_triangle = adjunction.right_adjoint()(adjunction.counit(target)) * adjunction.unit(
        adjunction.right_adjoint()(target)
    )
    for generator in target.group_generators():
        assert first_triangle(generator) == generator

    second_triangle = adjunction.counit(abelianization) * adjunction.left_adjoint()(
        adjunction.unit(group)
    )
    for element in abelianization:
        assert second_triangle(element) == element

