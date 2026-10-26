from sage_extensions.all import *



def _quadratic_algebra_tower():
    scalar_presentation = QQ.free_module(["s"]).symmetric_algebra()
    s = scalar_presentation.algebra_generator("s")
    extension_ring = (scalar_presentation).quotient_by_relations((s**2 - 2,),
    )
    ring_map = extension_ring.algebra_structure_morphism()

    source_presentation = QQ.free_module(["x"]).symmetric_algebra()
    x = source_presentation.algebra_generator("x")
    source = (source_presentation).quotient_by_relations((x**4 - 2,),
    )

    target_presentation = extension_ring.free_module(["y"]).symmetric_algebra()
    y = target_presentation.algebra_generator("y")
    target = (target_presentation).quotient_by_relations((y**2 - extension_ring.algebra_generator("s"),),
    )
    return extension_ring, ring_map, source, target


def _assert_algebra_maps_agree(left, right) -> None:
    assert left.domain() is right.domain()
    assert left.codomain() is right.codomain()
    for label in left.domain().algebra_generating_set():
        generator = left.domain().algebra_generator(label)
        assert left(generator) == right(generator)


def test_algebra_scalar_extension_restriction_has_the_mor_bijection() -> None:
    extension_ring, ring_map, source, target = _quadratic_algebra_tower()
    adjunction = Algebras(ring_map.domain()).Associative().Unital().Commutative().base_change_adjunction(ring_map)
    extension = adjunction.left_adjoint()
    restriction = adjunction.right_adjoint()

    extended_source = extension(source)
    restricted_target = restriction(target)

    # Restriction changes the scalar structure, not the underlying ring.  Its
    # selected QQ-presentation must nevertheless include both the scalar
    # generator s and the original algebra generator y.
    restricted_labels = restricted_target.algebra_generating_set()
    assert int(restricted_labels.cardinality()) == 2
    scalar_label = restricted_labels[0]
    algebra_label = restricted_labels[1]
    assert int(scalar_label.summand_index()) == 0
    assert scalar_label.summand_element() == "s"
    assert int(algebra_label.summand_index()) == 1
    assert algebra_label.summand_element() == "y"
    assert restricted_target.algebra_generator(scalar_label) == target(
        extension_ring.algebra_generator("s")
    )
    assert restricted_target.algebra_generator(algebra_label) == target.algebra_generator("y")
    for relation in restricted_target.relations():
        assert restricted_target.algebra_presentation_morphism()(relation) == 0

    # y^4 = s^2 = 2, so x |-> y defines an S-algebra morphism
    # S tensor_QQ A -> B.  Its transpose is the corresponding QQ-algebra map
    # A -> Res(B), and transposing back recovers the original map.
    phi = extended_source.Mor(target)(
        {"x": target.algebra_generator("y")}
    )
    transpose = adjunction.mor_set_isomorphism_forward(phi, source)
    assert transpose(source.algebra_generator("x")) == restricted_target(
        target.algebra_generator("y")
    )
    recovered = adjunction.mor_set_isomorphism_inverse(transpose, target)
    _assert_algebra_maps_agree(recovered, phi)

    # Check the inverse composite in the other direction as well, using the
    # distinct map x |-> -y.
    psi = source.Mor(restricted_target)(
        {"x": -restricted_target.algebra_generator(algebra_label)}
    )
    inverse_transpose = adjunction.mor_set_isomorphism_inverse(psi, target)
    recovered_psi = adjunction.mor_set_isomorphism_forward(inverse_transpose, source)
    _assert_algebra_maps_agree(recovered_psi, psi)


def test_algebra_scalar_extension_restriction_naturality_and_triangles() -> None:
    _, ring_map, source, target = _quadratic_algebra_tower()
    adjunction = Algebras(ring_map.domain()).Associative().Unital().Commutative().base_change_adjunction(ring_map)
    extension = adjunction.left_adjoint()
    restriction = adjunction.right_adjoint()

    source_involution = source.Mor(source)(
        {"x": -source.algebra_generator("x")}
    )
    left, right = adjunction.unit_transformation().naturality_square(source_involution)
    _assert_algebra_maps_agree(left, right)

    target_involution = target.Mor(target)(
        {"y": -target.algebra_generator("y")}
    )
    left, right = adjunction.counit_transformation().naturality_square(
        target_involution
    )
    _assert_algebra_maps_agree(left, right)

    restricted_target = restriction(target)
    first_triangle = restriction(adjunction.counit(target)) * adjunction.unit(
        restricted_target
    )
    identity_restricted_target = restricted_target.Mor(restricted_target)(
        {
            label: restricted_target.algebra_generator(label)
            for label in restricted_target.algebra_generating_set()
        }
    )
    _assert_algebra_maps_agree(first_triangle, identity_restricted_target)

    extended_source = extension(source)
    second_triangle = adjunction.counit(extended_source) * extension(
        adjunction.unit(source)
    )
    identity_extended_source = extended_source.Mor(extended_source)(
        {
            label: extended_source.algebra_generator(label)
            for label in extended_source.algebra_generating_set()
        }
    )
    _assert_algebra_maps_agree(second_triangle, identity_extended_source)


