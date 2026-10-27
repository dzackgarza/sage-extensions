r"""Toric varieties of fans and of lattice polytopes.

Values are Cox--Little--Schenck, *Toric Varieties*: the smoothness and
completeness criteria are Thm. 3.1.19 and Thm. 3.4.1, the orbit-cone
correspondence is Thm. 3.2.6, the affine chart of a cone is Prop. 1.3.9, the
three generators of the ``A_1`` chart are Example 1.2.22, and the face
localization is Prop. 1.3.16.
"""

from sage_extensions.all import *

# One rank-two cocharacter lattice for the whole file: a free module is a
# fresh object on every construction, so building it twice would give two
# unrelated categories of fans.
_PLANE_FANS = RationalPolyhedralFans(ZZ.free_module(2))


def _plane_fans():
    return _PLANE_FANS


def test_projective_toric_line_over_a_ring_with_zero_divisors() -> None:
    r"""The fan gluing of P^1_R exists for R=Z/4 without domain placement."""
    R = ZZ.quotient_ring(ZZ.ideal(4))
    line = ToricSchemes(R).an_object()
    assert line in ToricSchemes(R)
    assert line not in Varieties(R)
    assert line.scheme_base_ring() is R
    assert line.fan().cocharacter_lattice().module_rank() == 1


def test_the_projective_plane_of_its_fan_is_a_smooth_complete_toric_surface() -> None:
    plane = _plane_fans().projective_space_fan().toric_variety(QQ)

    assert plane in Schemes(QQ)
    assert plane in ToricSchemes(QQ)
    assert plane in Varieties(QQ)
    assert plane in Surfaces(QQ)
    assert plane in NormalSchemes(QQ)
    assert plane in SmoothSchemes(QQ)
    assert plane in IntegralSchemes(QQ)
    assert plane.dimension() == 2
    assert plane.is_smooth()
    assert plane.is_complete()
    assert plane.is_normal()






def test_the_orbit_cone_correspondence_counts_the_orbits_of_each_dimension() -> None:
    r"""CLS Thm. 3.2.6: cones of dimension ``k`` index orbits of dimension
    ``n - k``, so ``P^2`` has one dense orbit, three one-dimensional orbits and
    three fixed points."""
    plane = _plane_fans().projective_space_fan().toric_variety(QQ)

    assert plane.torus_orbits(2).cardinality() == 1
    assert plane.torus_orbits(1).cardinality() == 3
    assert plane.torus_orbits(0).cardinality() == 3


def test_the_chart_of_a_smooth_cone_is_the_affine_plane() -> None:
    fans = _plane_fans()
    variety = fans((((1, 0), (0, 1)), ((1, 0), (0, -1)))).toric_variety(QQ)
    cone = variety.fan().maximal_cones()[0]
    chart = variety.affine_chart(cone)

    assert variety in Surfaces(QQ)
    assert variety not in Surfaces(QQ).Proper()
    assert variety not in Surfaces(QQ).Projective()
    assert chart in AffineSchemes(QQ)
    assert chart.coordinate_algebra().algebra_generating_set().cardinality() == 2


def test_smooth_full_dimensional_cone_coefficients_are_dual_ray_pairings() -> None:
    r"""On a smooth full-dimensional cone, its dual Hilbert basis is the dual ray basis."""
    fan = _plane_fans().projective_space_fan()
    cone = fan.maximal_cones()[0]
    assert cone.is_smooth()
    assert cone.dimension() == fan.dimension()

    generators = tuple(cone.semigroup_generators())
    rays = tuple(cone.rays())
    assert len(generators) == len(rays) == 2
    for generator in generators:
        coefficients = cone.semigroup_coefficients(generator)
        for basis_character in generators:
            matching_rays = tuple(
                ray
                for ray in rays
                if all(
                    fan.character_cocharacter_value(basis_character, other)
                    == (ZZ.one() if other == ray else ZZ.zero())
                    for other in rays
                )
            )
            assert len(matching_rays) == 1
            assert coefficients[basis_character] == fan.character_cocharacter_value(
                generator, matching_rays[0]
            )


def test_character_cocharacter_value_is_the_owned_functional_evaluation() -> None:
    r"""The scalar pairing is exactly evaluation in the selected dual frames."""
    fan = _plane_fans().projective_space_fan()
    characters = tuple(fan.character_lattice().module_generating_set())
    cocharacters = tuple(fan.lattice().module_generating_set())
    integers = ZZ

    for i, character_label in enumerate(characters):
        character = fan.character_lattice().module_generator(character_label)
        for j, cocharacter_label in enumerate(cocharacters):
            cocharacter = fan.lattice().module_generator(cocharacter_label)
            value = fan.character_cocharacter_value(character, cocharacter)
            assert value.parent() is integers
            assert value == character(cocharacter)
            assert int(value) == (1 if i == j else 0)


def test_overlap_characters_stay_in_the_selected_face_localization() -> None:
    r"""Transition characters have the literal coordinate-algebra parent of their overlap."""
    from sage_extensions.categories.schemes.toric.toric_schemes import (
        _affine_chart,
        _character_on_overlap,
        _face_localization,
    )

    fan = _plane_fans().projective_space_fan()
    source, target = tuple(fan.maximal_cones())[:2]
    face = source.intersection(target)
    localization = _face_localization(face, source, QQ).coordinate_algebra()

    for character in target.semigroup_generators():
        image = _character_on_overlap(character, face, source, QQ)
        assert image.parent() is localization

    invalid = next(
        -character
        for character in source.semigroup_generators()
        if any(
            fan.character_cocharacter_value(character, ray) > 0
            for ray in face.rays()
        )
    )
    try:
        _character_on_overlap(invalid, face, source, QQ)
    except AssertionError as error:
        assert "not in the dual cone of the face" in str(error)
    else:
        raise AssertionError("an overlap character outside the face dual cone was accepted")


def test_overlap_character_assignment_preserves_semigroup_addition() -> None:
    r"""The overlap character map respects chi^(m+n)=chi^m chi^n exactly."""
    from sage_extensions.categories.schemes.toric.toric_schemes import (
        _character_on_overlap,
        _face_localization,
    )

    fan = _plane_fans().projective_space_fan()
    source, target = tuple(fan.maximal_cones())[:2]
    face = source.intersection(target)
    localization = _face_localization(face, source, QQ).coordinate_algebra()
    generators = tuple(target.semigroup_generators())

    for left in generators:
        for right in generators:
            left_image = _character_on_overlap(left, face, source, QQ)
            right_image = _character_on_overlap(right, face, source, QQ)
            sum_image = _character_on_overlap(left + right, face, source, QQ)
            assert left_image.parent() is localization
            assert right_image.parent() is localization
            assert sum_image.parent() is localization
            assert sum_image == left_image * right_image


def test_toric_face_transition_maps_are_mutual_inverses() -> None:
    r"""The two exact overlap pullbacks compose to identities on both selected opens."""
    from sage_extensions.categories.schemes.toric.toric_schemes import (
        _affine_chart,
        _character_on_overlap,
        _face_localization,
        _face_supporting_character_monomial,
        _face_transition,
    )

    fan = _plane_fans().projective_space_fan()
    source, target = tuple(fan.maximal_cones())[:2]
    face = source.intersection(target)
    assert repr(_affine_chart(source, QQ))
    transition = _face_transition(source, target, QQ)
    source_open = _face_localization(face, source, QQ)
    target_open = _face_localization(face, target, QQ)

    assert transition.forward().domain() is source_open
    assert transition.forward().codomain() is target_open
    assert transition.inverse().domain() is target_open
    assert transition.inverse().codomain() is source_open
    pullback = transition.forward().coordinate_algebra_morphism()
    target_chart = _affine_chart(target, QQ).coordinate_algebra()
    for label, character in zip(
        target_chart.algebra_generating_set(), target.semigroup_generators(), strict=True
    ):
        assert pullback(target_chart.algebra_generator(label)) == _character_on_overlap(
            character, face, source, QQ
        )
    assert transition.inverse().forward() * transition.forward() == source_open.Mor(
        source_open
    ).identity()
    assert transition.forward() * transition.inverse().forward() == target_open.Mor(
        target_open
    ).identity()

    # The primed-even A_4 polygon has a normal-fan cone with three Hilbert
    # generators and the toric relation s0*s1 = s2^2. Its supporting character
    # must be built in the actual quotient algebra without asking for a second
    # finite-presentation resolution merely to multiply those generator classes.
    singular_polygon = LatticePolygons(ZZ.free_module(2))(
        ((2, 2), (0, 1), (0, 0), (3, 0))
    )
    singular_cones = tuple(singular_polygon.normal_fan().maximal_cones())
    singular_cone = next(
        cone for cone in singular_cones if len(tuple(cone.semigroup_generators())) == 3
    )
    adjacent = singular_cones[(singular_cones.index(singular_cone) + 1) % len(singular_cones)]
    singular_face = singular_cone.intersection(adjacent)
    singular_chart = _affine_chart(singular_cone, QQ)
    supporting = _face_supporting_character_monomial(
        singular_face, singular_cone, singular_chart
    )
    assert supporting.parent() is singular_chart.coordinate_algebra()
    singular_open = _face_localization(singular_face, singular_cone, QQ)
    assert singular_open in Schemes(QQ)
    singular_transition = _face_transition(singular_cone, adjacent, QQ)
    assert singular_transition.forward().domain() is singular_open
    assert singular_transition.inverse().forward() * singular_transition.forward() == (
        singular_open.Mor(singular_open).identity()
    )


def test_the_chart_of_the_a_one_cone_is_the_quadric_cone() -> None:
    r"""CLS Example 1.2.22: ``S_sigma`` needs three characters with one
    relation, so the chart is a hypersurface in three variables rather than an
    affine plane."""
    fans = _plane_fans()
    variety = fans((((0, 1), (2, -1)),)).toric_variety(QQ)
    cone = variety.fan().maximal_cones()[0]
    chart = variety.affine_chart(cone)

    assert chart in AffineSchemes(QQ)
    assert chart.coordinate_algebra().algebra_generating_set().cardinality() == 3
    assert not variety.is_smooth()


def test_singular_rank_two_cone_coefficients_reconstruct_hilbert_generators() -> None:
    r"""Exact unimodular-pair coordinates expand each Hilbert generator itself."""
    fan = _plane_fans()((((0, 1), (2, -1)),))
    cone = fan.maximal_cones()[0]
    assert cone.dimension() == 2
    assert not cone.is_smooth()
    generators = tuple(cone.semigroup_generators())
    zero = cone.character_lattice().zero()

    characters = set(generators)
    characters.add(generators[0] + generators[-1])

    for character in characters:
        coefficients = cone.semigroup_coefficients(character)
        assert all(int(coefficients[generator]) >= 0 for generator in generators)
        reconstructed = sum(
            (int(coefficients[generator]) * generator for generator in generators),
            zero,
        )
        assert reconstructed == character






def test_the_standard_identifications_are_decided_by_fan_isomorphism() -> None:
    fans = _plane_fans()
    plane = fans.projective_space_fan().toric_variety(QQ)
    first_hirzebruch = fans.hirzebruch_surface_fan(1).toric_variety(QQ)

    assert plane.is_projective_space()
    assert plane.is_weighted_projective_space((1, 1, 1))
    assert not plane.is_hirzebruch_surface(1)
    assert first_hirzebruch.is_hirzebruch_surface(1)
    assert not first_hirzebruch.is_projective_space()
    assert not plane.is_isomorphic_to(first_hirzebruch)
    assert plane.is_isomorphic_to(fans.projective_space_fan().toric_variety(QQ))


def test_the_normal_fan_of_a_polytope_uses_inner_normals() -> None:
    r"""The facet ``x + 2y = 2`` of ``conv{(0,0),(2,0),(0,1)}`` has inner
    normal ``-e_1 - 2 e_2``; the outer normal ``e_1 + 2 e_2`` is not a ray of
    the normal fan.  The cone on ``e_1`` and ``-e_1 - 2e_2`` has determinant
    ``-2``, so the toric variety, ``P(1,1,2)``, is singular."""
    lattice = ZZ.free_module(2)
    polygon = ConvexPolytopes(lattice)(((0, 0), (2, 0), (0, 1)))
    fan = polygon.normal_fan()
    cocharacters = fan.cocharacter_lattice()
    first, second = tuple(cocharacters.module_generating_set())
    inner = cocharacters.linear_combination({first: ZZ(-1), second: ZZ(-2)})
    outer = cocharacters.linear_combination({first: ZZ(1), second: ZZ(2)})

    assert fan.rays().cardinality() == 3
    assert inner in fan.rays()
    assert outer not in fan.rays()
    assert not polygon.toric_variety(QQ).is_smooth()


def test_the_toric_variety_of_the_standard_triangle_is_the_projective_plane() -> None:
    r"""The normal fan of ``conv{(0,0),(1,0),(0,1)}`` has rays ``e_1``, ``e_2``
    and ``-e_1-e_2``, which is the fan of ``P^2``."""
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (1, 0), (0, 1)))
    variety = triangle.toric_variety(QQ)

    assert variety.is_projective_space()
    assert variety.fan().is_isomorphic(_plane_fans().projective_space_fan())
    assert variety.is_smooth()






def test_a_nonidentity_toric_morphism_retains_its_chart_pullback() -> None:
    r"""On ``P^1``, doubling ``N`` induces ``chi^m |-> chi^(2m)`` on a chart."""

    fans = RationalPolyhedralFans(ZZ.free_module(1))
    fan = fans.projective_space_fan()
    cocharacters = fans.cocharacter_lattice()
    label = next(iter(cocharacters.module_generating_set()))
    doubling = cocharacters.module_category().Mor(cocharacters, cocharacters)(
        {
            label: ZZ(2) * cocharacters.module_generator(label),
        }
    )
    variety = fan.toric_variety(QQ)
    morphism = variety.toric_morphism(doubling, variety)
    source_cone = fan.maximal_cones()[0]
    target_cone = morphism.chart_target(source_cone)
    source_algebra = variety.affine_chart(source_cone).coordinate_algebra()
    target_algebra = variety.affine_chart(target_cone).coordinate_algebra()
    source_generator = source_algebra.algebra_generator(
        next(iter(source_algebra.algebra_generating_set()))
    )
    target_generator = target_algebra.algebra_generator(
        next(iter(target_algebra.algebra_generating_set()))
    )

    assert morphism.lattice_morphism() is doubling
    assert morphism.chart_pullback(source_cone)(target_generator) == source_generator**2
    assert morphism.chart_morphism(source_cone).domain() is variety.affine_chart(source_cone)
    assert morphism.chart_morphism(source_cone).codomain() is variety.affine_chart(target_cone)


def test_an_incompatible_lattice_map_is_refused_rather_than_forced() -> None:
    r"""The fan of ``P^1`` in a rank-one lattice is not carried into the fan of
    the affine line by the identity: the ray ``-e_1`` lies in no cone."""
    line_fans = RationalPolyhedralFans(ZZ.free_module(1))

    projective_line = line_fans.projective_space_fan()
    affine_line = line_fans((((1,),),))
    cocharacters = line_fans.cocharacter_lattice()
    identity = cocharacters.module_category().Mor(cocharacters, cocharacters).identity()

    assert not projective_line.is_compatible_with(identity, affine_line)
    assert affine_line.is_compatible_with(identity, projective_line)
