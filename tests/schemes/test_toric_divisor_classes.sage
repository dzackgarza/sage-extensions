r"""Class group, Cartier divisors and divisor polytopes of a toric variety.

Values are Cox--Little--Schenck, *Toric Varieties*: the exact sequence
``M -> Div_T(X) -> Cl(X) -> 0`` is Thm. 4.1.3, the Cartier criterion is
Thm. 4.2.8, ``Pic = Cl`` on a smooth fan is Prop. 4.2.6, the polytope of a
divisor is (4.3.2) and its lattice points are a basis of the global sections
by Prop. 4.3.3.
"""


from sage_extensions.all import *

# One rank-two cocharacter lattice for the whole file: a free module is a
# fresh object on every construction, so building it twice would give two
# unrelated categories of fans.
_PLANE_FANS = RationalPolyhedralFans(ZZ.free_module(2))


def _projective_plane():
    return _PLANE_FANS.projective_space_fan().toric_variety(QQ)


def _quadric_cone():
    r"""``U_sigma`` for ``sigma = Cone((1,0),(1,2))``: the ``A_1`` surface singularity."""
    return _PLANE_FANS((((1, 0), (1, 2)),)).toric_variety(QQ)


def _prime_divisors(variety):
    return tuple(
        variety.torus_invariant_prime_divisor(ray) for ray in variety.fan().cones(1)
    )


def test_the_three_lines_of_the_projective_plane_share_one_divisor_class() -> None:
    r"""``div(chi^{e_1^*}) = D_1 - D_0`` on the fan of ``P^2``, so the three
    torus-invariant lines are linearly equivalent and generate ``Cl(P^2)``."""
    plane = _projective_plane()
    classes = plane.class_group()
    first, second, third = (plane.divisor_class(D) for D in _prime_divisors(plane))

    assert first == second
    assert second == third
    assert first != classes.zero()


def test_the_anticanonical_class_of_the_projective_plane_is_three_times_a_line() -> None:
    plane = _projective_plane()
    line = plane.divisor_class(_prime_divisors(plane)[0])

    assert plane.divisor_class(plane.toric_boundary_divisor()) == ZZ(3) * line
    assert plane.divisor_class(plane.canonical_divisor()) == ZZ(-3) * line


def test_squaring_on_projective_line_pulls_back_a_boundary_point_with_multiplicity_two() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(1))
    fan = fans.projective_space_fan()
    cocharacters = fans.cocharacter_lattice()
    label = next(iter(cocharacters.module_generating_set()))
    doubling = cocharacters.module_category().Mor(cocharacters, cocharacters)(
        {label: ZZ(2) * cocharacters.module_generator(label)}
    )
    line = fan.toric_variety(QQ)
    morphism = line.toric_morphism(doubling, line)
    ray = next(iter(fan.cones(1)))
    point = line.torus_invariant_prime_divisor(ray)
    pulled = morphism.pullback_divisor(point)
    bundle = line.invertible_sheaf_of_divisor(point)

    assert pulled == ZZ(2) * point
    assert morphism.pullback_line_bundle(bundle).associated_divisor() == pulled


def test_only_a_fan_whose_rays_span_the_lattice_is_free_of_a_torus_factor() -> None:
    r"""``A^1 x k^*`` is the toric variety of the single ray ``e_1`` in ``ZZ^2``."""
    plane = _projective_plane()
    half_plane = _PLANE_FANS((((1, 0),),)).toric_variety(QQ)

    assert not plane.has_torus_factor()
    assert half_plane.has_torus_factor()


def test_a_ruling_of_the_quadric_cone_is_weil_but_not_cartier() -> None:
    r"""On ``sigma = Cone((1,0),(1,2))`` a character with ``<m,u_1> = -1`` and
    ``<m,u_2> = 0`` would need second coordinate ``1/2``, so ``D_1`` is not
    Cartier while ``2 D_1`` is."""
    cone_surface = _quadric_cone()
    ruling = _prime_divisors(cone_surface)[0]

    assert not cone_surface.is_cartier(ruling)
    assert cone_surface.is_cartier(ZZ(2) * ruling)
    assert cone_surface.is_cartier(cone_surface.toric_boundary_divisor())


def test_every_torus_invariant_divisor_on_a_smooth_toric_surface_is_cartier() -> None:
    plane = _projective_plane()

    for divisor in _prime_divisors(plane):
        assert plane.is_cartier(divisor)
    assert plane.is_cartier(plane.canonical_divisor())


def test_standard_smooth_toric_picard_groups_come_from_the_character_divisor_quotient() -> None:
    affine_plane = _PLANE_FANS((((1, 0), (0, 1)),)).toric_variety(QQ)
    projective_plane = _projective_plane()
    product_of_lines = _PLANE_FANS.hirzebruch_surface_fan(0).toric_variety(QQ)

    assert affine_plane.picard_group().module_rank() == 0
    assert affine_plane.class_group().module_rank() == 0
    assert projective_plane.picard_group().module_rank() == 1
    assert projective_plane.class_group().module_rank() == 1
    assert product_of_lines.picard_group().module_rank() == 2
    assert product_of_lines.class_group().module_rank() == 2


def test_the_sections_of_a_line_on_the_projective_plane_are_the_three_linear_forms() -> None:
    r"""``h^0(P^2, O(1)) = 3`` and ``h^0(P^2, O(3)) = 10``: the polytope of a
    single torus-invariant line is a unimodular triangle and the polytope of
    the boundary is its third dilate."""
    plane = _projective_plane()
    characters = plane.character_lattice()

    for divisor in _prime_divisors(plane):
        assert plane.divisor_polytope(divisor).n_integral_points() == 3
        assert plane.divisor_section_characters(divisor).cardinality() == 3
        sections = plane.divisor_section_space(divisor)
        assert sections.dimension() == 3
        assert sections.module_generating_set() == plane.divisor_section_characters(divisor)

    boundary = plane.toric_boundary_divisor()
    assert plane.divisor_polytope(boundary).n_integral_points() == 10
    assert characters.zero() in plane.divisor_section_characters(boundary)
    assert plane.divisor_section_space(boundary).dimension() == 10


def test_the_square_of_the_line_bundle_of_a_line_is_the_bundle_of_twice_the_line() -> None:
    r"""``O(D)^{\otimes 2} = O(2D)`` for a torus-invariant line ``D`` of ``P^2``, with
    ``h^0(O(D)) = 3`` and ``h^0(O(2D)) = 6`` (CLS Prop. 4.3.3)."""
    plane = _projective_plane()
    line = _prime_divisors(plane)[0]
    bundle = plane.invertible_sheaf_of_divisor(line)
    square = plane.invertible_sheaf_of_divisor(ZZ(2) * line)

    assert bundle.associated_divisor() == line
    assert bundle.tensor_power(2) == square
    assert bundle.global_sections().dimension() == 3
    assert square.global_sections().dimension() == 6


def test_the_polytope_of_an_ample_divisor_has_the_fan_as_its_normal_fan() -> None:
    r"""``O(1)`` on ``P^2`` is ample, and by CLS Thm. 6.2.1 the normal fan of the
    polytope of an ample divisor on a complete toric variety is the fan itself.
    Each torus-invariant line of ``P^2`` is a unimodular triangle's divisor."""
    plane = _projective_plane()

    for divisor in _prime_divisors(plane):
        polytope = plane.divisor_polytope(divisor)
        assert polytope.n_vertices() == 3
        assert polytope.normal_fan().is_isomorphic(plane.fan())


def test_a_line_is_ample_on_the_projective_plane_and_the_canonical_class_is_not() -> None:
    r"""``O(1)`` and ``O(3)`` are ample and generated by global sections;
    ``K = -3H`` is neither.  The support function of ``K`` on the cone spanned
    by ``e_1`` and ``e_2`` is ``m = (1,1)``, which pairs to ``-2`` against the
    third ray where convexity would need at least ``1``."""
    plane = _projective_plane()
    line = _prime_divisors(plane)[0]

    assert plane.is_ample(line)
    assert plane.is_basepoint_free(line)
    assert plane.is_ample(plane.toric_boundary_divisor())
    assert not plane.is_basepoint_free(plane.canonical_divisor())
    assert not plane.is_ample(plane.canonical_divisor())


def test_projective_plane_intersections_are_the_normalized_areas_of_divisor_polytopes() -> None:
    plane = _projective_plane()
    line = _prime_divisors(plane)[0]
    cubic = plane.toric_boundary_divisor()

    assert plane.ample_divisor_self_intersection(line) == 1
    assert plane.ample_divisor_intersection(line, cubic) == 3
    assert plane.ample_divisor_self_intersection(cubic) == 9


def test_hirzebruch_zero_picard_pairing_is_the_hyperbolic_plane() -> None:
    surface = _PLANE_FANS.hirzebruch_surface_fan(0).toric_variety(QQ)
    divisors = tuple(
        surface.torus_invariant_prime_divisor(ray)
        for ray in surface.fan().cones(1)
    )
    pairing = surface.picard_intersection_pairing()
    projection = surface.torus_invariant_cartier_class_projection()
    classes = tuple(projection(divisor) for divisor in divisors)

    # The two ruling classes f_1, f_2 satisfy f_i^2 = 0 and f_1 f_2 = f_2 f_1 = 1.
    assert any(
        pairing(left, left) == 0
        and pairing(right, right) == 0
        and pairing(left, right) == 1
        and pairing(right, left) == 1
        for left in classes
        for right in classes
    )


def test_projective_plane_chow_groups_are_owned_integral_cycle_quotients() -> None:
    plane = _projective_plane()

    for degree in (0, 1, 2):
        group = plane.chow_group(degree)
        assert group.cycle_dimension() == degree
        assert group.module_rank() == 1
        assert group.invariant_factors().cardinality() == 1
        assert group.invariant_factors()[0] == ZZ.zero()


def test_projective_plane_invariant_curves_surject_onto_the_chow_group() -> None:
    plane = _projective_plane()
    cycles = plane.torus_invariant_cycle_group(1)
    projection = plane.torus_invariant_cycle_class_map(1)
    rays = tuple(cycles.module_generating_set())

    assert cycles.cycle_dimension() == 1
    assert cycles.module_rank() == 3
    assert projection.is_surjective()
    images = tuple(projection(cycles.module_generator(ray)) for ray in rays)
    assert images[0] == images[1] == images[2]


def test_hirzebruch_surface_chow_group_has_rank_two_in_curve_degree() -> None:
    surface = _PLANE_FANS.hirzebruch_surface_fan(0).toric_variety(QQ)

    assert surface.chow_group(0).module_rank() == 1
    assert surface.chow_group(1).module_rank() == 2
    assert surface.chow_group(2).module_rank() == 1


def test_projective_plane_cox_ring_is_class_group_graded() -> None:
    plane = _projective_plane()
    cox = plane.cox_ring()
    labels = tuple(cox.algebra_generating_set())

    assert cox.grading_monoid() is plane.class_group()
    first_degree = cox.generator_degree(labels[0])
    assert first_degree == plane.divisor_class(_prime_divisors(plane)[0])
    assert all(cox.generator_degree(label) == first_degree for label in labels)
    assert cox.homogeneous_degree(cox.algebra_generator(labels[0]) ** 3) == ZZ(3) * first_degree
    assert cox.homogeneous_degree(
        cox.algebra_generator(labels[0]) * cox.algebra_generator(labels[1])
    ) == ZZ(2) * first_degree


def test_projective_plane_hyperplane_section_ring_has_the_expected_graded_pieces() -> None:
    plane = _projective_plane()
    line = plane.hyperplane_divisor()
    ring = plane.section_ring(line)
    labels = tuple(ring.algebra_generating_set())

    assert ring.section_divisor() == line
    assert all(ring.generator_degree(label) == 1 for label in labels)
    assert ring.graded_piece(1).module_rank() == 3
    assert ring.graded_piece(2).module_rank() == 6
    assert ring.homogeneous_degree(
        ring.algebra_generator(labels[0]) * ring.algebra_generator(labels[1])
    ) == 2


def test_projective_plane_sections_are_actual_homogeneous_cox_polynomials() -> None:
    plane = _projective_plane()
    line = plane.hyperplane_divisor()
    source = plane.divisor_section_space(line)
    polynomial_space = plane.homogeneous_polynomial_section_space(line)
    identification = plane.section_homogeneous_polynomial_isomorphism(line)
    cox = plane.cox_ring()

    assert source.dimension() == 3
    assert polynomial_space.dimension() == 3
    for character in source.module_generating_set():
        monomial = plane.cox_monomial_of_section(line, character)
        assert cox.homogeneous_degree(monomial) == plane.divisor_class(line)
        assert identification.forward()(source.module_generator(character)) == (
            polynomial_space.module_generator(monomial)
        )


def test_projective_plane_line_bundle_cohomology_is_an_owned_vector_space() -> None:
    plane = _projective_plane()
    line = plane.hyperplane_divisor()
    canonical = plane.canonical_divisor()

    h0_line = plane.line_bundle_cohomology(line, 0)
    h1_line = plane.line_bundle_cohomology(line, 1)
    h2_canonical = plane.line_bundle_cohomology(canonical, 2)

    assert h0_line.dimension() == 3
    assert h1_line.dimension() == 0
    assert h2_canonical.dimension() == 1
    dimensions = plane.line_bundle_cohomology_dimensions(line)
    assert tuple(int(degree) for degree in dimensions.index_set()) == (0, 1, 2)
    assert tuple(dimensions) == (NN(3), NN(0), NN(0))


def test_coordinate_hyperplane_restriction_has_the_expected_kernel_and_cokernel() -> None:
    plane = _projective_plane()
    projective_plane = plane.complete_linear_system(plane.hyperplane_divisor())
    restriction = projective_plane.coordinate_hyperplane_section_restriction(2, 0)

    assert restriction.domain().dimension() == 6
    assert restriction.codomain().dimension() == 3
    assert restriction.kernel().dimension() == 3
    assert restriction.cokernel().is_zero()


def test_coordinate_point_jets_cut_out_imposed_multiplicity_conditions() -> None:
    plane = _projective_plane()
    projective_plane = plane.complete_linear_system(plane.hyperplane_divisor())
    jets = projective_plane.coordinate_point_jet_evaluation(3, 0, 2)
    singular_at_point = projective_plane.sections_vanishing_to_order(3, 0, 2)

    assert jets.domain().dimension() == 10
    assert jets.codomain().dimension() == 3
    assert jets.is_surjective()
    assert singular_at_point.dimension() == 7
    assert singular_at_point.inclusion().codomain().dimension() == 10


def test_higher_jets_record_the_expected_truncated_local_monomials() -> None:
    plane = _projective_plane()
    projective_plane = plane.complete_linear_system(plane.hyperplane_divisor())
    jets = projective_plane.coordinate_point_jet_evaluation(3, 0, 3)

    assert jets.codomain().dimension() == 6
    assert jets.kernel().dimension() == 4
    assert jets.cokernel().is_zero()


def test_imposed_double_point_sections_form_the_expected_projective_parameter_space() -> None:
    plane = _projective_plane()
    projective_plane = plane.complete_linear_system(plane.hyperplane_divisor())
    system = projective_plane.imposed_multiplicity_linear_system(3, 0, 2)

    assert system.relative_dimension() == 6
    assert system.ambient_section_space().dimension() == 10
    assert system.constrained_section_space().dimension() == 7
    assert system.constrained_section_space() is system.imposed_jet_evaluation().kernel()
    assert system.imposed_vanishing_order() == 2


def test_projective_plane_quadratic_section_ring_uses_the_saturated_semigroup() -> None:
    plane = _projective_plane()
    conic = ZZ(2) * plane.hyperplane_divisor()
    ring = plane.section_ring(conic)

    assert ring.graded_piece(1).module_rank() == 6
    assert ring.algebra_generating_set().cardinality() == 6
    assert ring.relations().cardinality() > 0


def test_a_principal_divisor_is_basepoint_free_and_never_ample() -> None:
    r"""``O_X(div(chi^m))`` is the structure sheaf, generated by one global
    section and not ample on a complete surface.  Its support function is
    linear, hence convex and not strictly convex."""
    plane = _projective_plane()
    characters = plane.character_lattice()
    label = next(iter(characters.module_generating_set()))
    principal = plane.character_divisor_morphism()(
        characters.module_generator(label)
    )

    assert plane.is_cartier(principal)
    assert plane.is_basepoint_free(principal)
    assert not plane.is_ample(principal)


def test_the_quadric_cone_has_class_group_z_mod_2_and_trivial_picard_group() -> None:
    r"""For ``sigma = Cone((1,0),(1,2))``, ``Cl = ZZ^2 / <(1,1),(0,2)> = ZZ/2``,
    generated by a ruling, while every Cartier divisor on the affine toric
    variety ``U_sigma`` is principal, so ``Pic = 0`` (CLS Prop. 4.2.2, Ex. 4.1.5)."""
    cone_surface = _quadric_cone()
    ruling = cone_surface.divisor_class(_prime_divisors(cone_surface)[0])

    assert cone_surface.class_group().cardinality() == 2
    assert ruling != cone_surface.class_group().zero()
    assert cone_surface.picard_group().cardinality() == 1


def test_the_cox_ring_of_p1_times_p1_has_two_generators_in_each_ruling_degree() -> None:
    r"""The four rays of the fan of ``P^1 x P^1`` give Cox generators of degrees
    ``(1,0), (1,0), (0,1), (0,1)`` in ``Cl = ZZ^2`` (CLS Example 5.2.2)."""
    surface = _PLANE_FANS.hirzebruch_surface_fan(0).toric_variety(QQ)
    cox = surface.cox_ring()
    labels = cox.algebra_generating_set()
    degrees = tuple(cox.generator_degree(label) for label in labels)

    assert cox.grading_monoid() is surface.class_group()
    assert labels.cardinality() == 4
    assert all(degrees.count(degree) == 2 for degree in degrees)
