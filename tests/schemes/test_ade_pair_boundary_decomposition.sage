r"""The toric ADE pairs ``(Y, C)`` of pure shape and the decomposition of their boundary.

Source: Alexeev--Thompson, *ADE surfaces and their moduli* (2017), Lemma 3.4 and Definitions
3.5--3.6.  ``Y`` is the toric surface of a lattice polygon ``P`` with a distinguished vertex
``p_*``; ``C`` is the invariant divisor of the sides through ``p_*`` and ``C'`` that of the other
sides, so ``C + C'`` is the whole toric boundary and ``K_Y + C + C' ~ 0``; the sides not through
``p_*`` are at lattice distance 2 from it, whence ``L = -2(K_Y + C) ~ 2 C'``.  In type III (the
ADE shapes) ``C`` has exactly two components.
"""

from sage_extensions.all import *


def _blue_component_count(pair):
    surface = pair.log_scheme()
    blue = pair.blue_divisor()
    return sum(surface.weil_multiplicity(blue, ray) for ray in surface.fan().cones(1))


def test_the_sides_through_the_distinguished_vertex_and_the_rest_make_up_the_boundary() -> None:
    r"""``C + C' = sum_rho D_rho`` for the ``A_1``, ``A_2``, ``D_4`` and ``E_6`` pairs."""
    for letter, rank in (("A", 1), ("A", 2), ("D", 4), ("E", 6)):
        pair = ADELogPairs(QQ)(letter, rank)
        surface = pair.log_scheme()

        assert pair.blue_divisor() + pair.complementary_divisor() == surface.toric_boundary_divisor()
        assert pair.blue_divisor() + pair.complementary_divisor() == -surface.canonical_divisor()


def test_an_ade_pair_has_two_sides() -> None:
    r"""In type III the divisor ``C`` has two components, the left and right sides (Def. 3.6)."""
    for letter, rank in (("A", 1), ("D", 4), ("E", 6)):
        assert _blue_component_count(ADELogPairs(QQ)(letter, rank)) == 2


def test_the_distinguished_point_is_a_vertex_of_the_polygon() -> None:
    r"""``p_*`` is a distinguished vertex of ``P`` (Lemma 3.4)."""
    for letter, rank in (("A", 2), ("D", 4), ("E", 6)):
        pair = ADELogPairs(QQ)(letter, rank)

        assert pair.distinguished_point() in pair.polygon().vertices()


def test_the_pair_records_its_dynkin_type() -> None:
    r"""The pair of type ``X_n`` has letter ``X``, rank ``n``, and is not of affine type unless asked."""
    pair = ADELogPairs(QQ)("E", 6)

    assert pair.dynkin_letter() == "E"
    assert pair.dynkin_rank() == 6
    assert not pair.is_affine_type()
    assert ADELogPairs(QQ)("A", 3, affine=True).is_affine_type()
    assert pair.is_base()
    assert not pair.is_cover()
    assert pair.codimension_in_toric_scheme() == 0


def test_the_toric_surface_is_the_one_of_the_normal_fan_of_the_polygon() -> None:
    r"""``Y`` is the polarized toric surface of ``P``, so its fan is the normal fan of ``P``."""
    pair = ADELogPairs(QQ)("D", 4)

    assert pair.log_scheme().fan().is_isomorphic(pair.polygon().normal_fan())


def test_the_pyramid_over_the_polygon_is_a_three_dimensional_cone_over_it() -> None:
    r"""The cone over ``P`` with apex ``(p_*, 2)`` is three-dimensional with one more vertex than ``P``."""
    for letter, rank in (("A", 1), ("D", 4)):
        pair = ADELogPairs(QQ)(letter, rank)
        pyramid = pair.pyramid()

        assert pyramid.dimension() == 3
        assert pyramid.n_vertices() == pair.polygon().n_vertices() + 1
        assert pyramid.is_lattice_polytope()


def test_the_branch_divisor_is_linearly_equivalent_to_twice_the_other_sides() -> None:
    r"""``-2(K_Y + C) ~ 2 C'`` in ``Cl(Y)`` (Lemma 3.4)."""
    pair = ADELogPairs(QQ)("A", 1)
    surface = pair.log_scheme()
    branch = -2 * (surface.canonical_divisor() + pair.blue_divisor())

    assert surface.divisor_class(branch) == surface.divisor_class(2 * pair.complementary_divisor())


def test_the_at21_enhancement_of_a1_is_a_log_pair_on_the_same_surface() -> None:
    r"""The enhancement keeps ``(Y, C)`` and adds the branch data of Lemma 3.4."""
    enhanced = ADELogPairs(QQ).at21("A", 1)
    base_pair = enhanced.base_pair()

    assert enhanced in ToricLogPairs(QQ)
    assert enhanced.base_ring() is QQ
    assert base_pair in ADELogPairs(QQ)
    assert enhanced.log_scheme() is base_pair.log_scheme()
    assert enhanced.blue_divisor() is base_pair.blue_divisor()
    assert enhanced.complementary_divisor() is base_pair.complementary_divisor()
    assert enhanced.scheme().divisor_class(enhanced.branch_divisor_class()) == enhanced.scheme().divisor_class(
        2 * enhanced.complementary_divisor()
    )
    assert enhanced.branch_line_bundle().base_ring() is QQ
    assert enhanced.branch_line_bundle().scheme() is enhanced.scheme()
    assert enhanced.branch_line_bundle().associated_divisor() == enhanced.branch_divisor_class()
    coefficients = enhanced.log_boundary_coefficient_ring()
    assert coefficients.algebra_framing_source() is coefficients
    assert coefficients.algebra_framing_morphism() == coefficients.Mor(coefficients).identity()
    module_resolution = coefficients.selected_module_resolution()
    assert module_resolution.target() is coefficients
    assert module_resolution.level(0) is coefficients.framing_source()
    assert module_resolution.augmentation().domain() is coefficients.framing_source()
    assert module_resolution.augmentation().codomain() is coefficients
    generator_morphism = coefficients.algebra_generator_morphism()
    assert generator_morphism.domain() is coefficients.algebra_generating_set()
    assert generator_morphism.codomain() is coefficients
    assert generator_morphism("epsilon") == coefficients.algebra_generator("epsilon")


def test_at21_a_zero_minus_and_primed_even_polygon_conventions() -> None:
    r"""Retain the literal AT21 ``A_0^-`` and primed-even polygon conventions."""
    minus = ADELogPairs(QQ).at21("A", 0, variant="A^-")
    assert minus.dynkin_rank() == 0
    assert minus.source_variant() == "short"
    assert minus.base_pair().dynkin_variant() == ("long", "short")
    assert minus.branch_line_bundle().scheme() is minus.scheme()
    assert minus.branch_line_bundle().base_ring() is QQ
    assert minus.branch_line_bundle().associated_divisor() == minus.branch_divisor_class()
    assert {tuple(int(c) for c in vertex) for vertex in minus.base_pair().polygon().vertices()} == {
        (0, 2), (0, 0), (1, 0)
    }

    primed_even = ADELogPairs(QQ).at21("A", 4, variant="'A^-")
    assert primed_even in ToricLogPairs(QQ)
    assert primed_even.base_ring() is QQ
    assert primed_even.log_scheme() is primed_even.base_pair().log_scheme()
    assert primed_even.blue_divisor() is primed_even.base_pair().blue_divisor()
    assert primed_even.complementary_divisor() is primed_even.base_pair().complementary_divisor()
    vertices = {
        tuple(int(c) for c in vertex)
        for vertex in primed_even.base_pair().polygon().vertices()
    }
    assert (3, 0) in vertices
    assert (4, 0) not in vertices
    assert primed_even.branch_line_bundle().scheme() is primed_even.scheme()
    assert primed_even.branch_line_bundle().base_ring() is QQ
    assert primed_even.branch_line_bundle().associated_divisor() == primed_even.branch_divisor_class()
    assert primed_even.scheme().divisor_class(primed_even.branch_divisor_class()) == primed_even.scheme().divisor_class(
        2 * primed_even.complementary_divisor()
    )


def test_at21_public_constructor_accepts_the_default_a_zero_minus_shape() -> None:
    r"""AT21's A_0^- default is normalized before the public rank check."""
    pair = ADELogPairs(QQ).at21("A", 0)
    explicitly_minus = ADELogPairs(QQ).at21("A", 0, variant="A^-")

    assert pair.dynkin_letter() == "A"
    assert pair.dynkin_rank() == 0
    assert pair.source_variant() == "short"
    assert explicitly_minus.dynkin_letter() == "A"
    assert explicitly_minus.dynkin_rank() == 0
    assert explicitly_minus.source_variant() == "short"
    assert explicitly_minus.base_pair().dynkin_variant() == ("long", "short")
    vertices = {
        tuple(int(coordinate) for coordinate in vertex)
        for vertex in explicitly_minus.base_pair().polygon().vertices()
    }
    assert vertices == {(0, 2), (0, 0), (1, 0)}


def test_pure_a_zero_short_shape_is_admitted_by_at21_source_rules() -> None:
    r"""AT21 Table 1 includes the rank-zero pure shape A_0^-."""
    assert _validated_at21_low_level_variant("A", 0, "short", False) == ("long", "short")
    pair = ADELogPairs(QQ)("A", 0)
    assert pair.dynkin_letter() == "A"
    assert pair.dynkin_rank() == 0
    assert _ade_polygon_data("A", 0, ("long", "short"), False) == (
        ((0, 2), (0, 0), (1, 0)),
        (0, 2),
        _polygon_side_decorations(((0, 2), (0, 0), (1, 0)), (0, 2)),
    )


def test_at21_accepts_the_printed_prime_and_minus_a_decorations() -> None:
    r"""AT21's decorated A types have explicit public constructor spellings."""
    primed = ADELogPairs(QQ).at21("A", 3, variant="'A")
    doubly_marked_prime = ADELogPairs(QQ).at21("A", 3, variant="'A'")
    primed_minus = ADELogPairs(QQ).at21("A", 4, variant="'A^-")
    generic_odd_prime = ADELogPairs(QQ).at21("A", 3, variant="prime")
    generic_even_prime = ADELogPairs(QQ).at21("A", 4, variant=("prime",))
    minus = ADELogPairs(QQ).at21("A", 4, variant="^-A")
    superscript_minus = ADELogPairs(QQ).at21("A", 4, variant="A^-")
    unicode_minus = ADELogPairs(QQ).at21("A", 4, variant="A^−")
    unicode_prefix_minus = ADELogPairs(QQ).at21("A", 4, variant="^−A")
    tuple_variant = ADELogPairs(QQ).at21("A", 3, variant=("short", "short"))
    direct_minus = ADELogPairs(QQ)("A", 4, variant="^-A")

    assert primed.source_variant() == "prime-odd"
    assert primed.base_pair().dynkin_rank() == 3
    assert doubly_marked_prime.source_variant() == "prime-odd"
    assert doubly_marked_prime.base_pair().dynkin_rank() == 3
    assert primed_minus.source_variant() == "prime-even"
    assert primed_minus.base_pair().dynkin_rank() == 4
    assert primed_minus.base_pair().dynkin_variant() == ("prime",)
    assert generic_odd_prime.source_variant() == "prime-odd"
    assert generic_even_prime.source_variant() == "prime-even"
    actual_vertices = {
        tuple(int(coordinate) for coordinate in vertex)
        for vertex in primed_minus.base_pair().polygon().vertices()
    }
    assert (3, 0) in actual_vertices
    assert (4, 0) not in actual_vertices
    for rank, variant in ((4, "'A"), (3, "'A^-")):
        try:
            ADELogPairs(QQ).at21("A", rank, variant=variant)
        except ValueError as error:
            assert f"A_{rank}" in str(error)
        else:
            raise AssertionError(
                f"the AT21 source spelling {variant!r} must not admit A_{rank} of the opposite parity"
            )
    try:
        _validated_at21_low_level_variant("A", 4, "prime", False)
    except ValueError as error:
        assert "A_4" in str(error)
    else:
        raise AssertionError("the low-level A validator must not accept an unqualified primed family")
    assert minus.source_variant() == "left-short"
    assert minus.base_pair().dynkin_rank() == 4
    assert minus.base_pair().dynkin_variant() == ("short", "long")
    assert superscript_minus.source_variant() == "short"
    assert unicode_minus.source_variant() == "short"
    assert unicode_prefix_minus.source_variant() == "left-short"
    assert superscript_minus.base_pair().dynkin_rank() == 4

    # Every public spelling denotes the same owned AT21 construction contract:
    # the base ring and category are retained, and enhancement reuses the exact
    # base-pair scheme and boundary divisors rather than rebuilding lookalikes.
    for enhanced in (
        primed,
        doubly_marked_prime,
        primed_minus,
        generic_odd_prime,
        generic_even_prime,
        minus,
        superscript_minus,
        unicode_minus,
        unicode_prefix_minus,
    ):
        assert enhanced in ToricLogPairs(QQ)
        assert enhanced.base_ring() is QQ
        assert enhanced.base_pair() in ADELogPairs(QQ)
        assert enhanced.log_scheme() is enhanced.base_pair().log_scheme()
        assert enhanced.blue_divisor() is enhanced.base_pair().blue_divisor()
        assert enhanced.complementary_divisor() is enhanced.base_pair().complementary_divisor()
        line_bundle = enhanced.branch_line_bundle()
        assert line_bundle.scheme() is enhanced.scheme()
        assert line_bundle.base_ring() is QQ
        assert line_bundle.associated_divisor() == enhanced.branch_divisor_class()
    assert superscript_minus.base_pair().dynkin_variant() == ("long", "short")
    assert tuple_variant.source_variant() == "both-short"
    assert tuple_variant.base_pair().dynkin_rank() == 3
    assert direct_minus.dynkin_variant() == ("short", "long")
    try:
        ADELogPairs(QQ).at21("D", 6, variant="'A^-")
    except ValueError as error:
        assert "type D_6" in str(error)
    else:
        raise AssertionError("an A-specific primed decoration must not normalize as a D-type decoration")


def test_at21_default_variant_matches_the_parity_selected_base_constructor() -> None:
    r"""The default means the canonical AT21 shape for the Dynkin rank."""
    for letter, rank, expected in (("A", 3, "pure"), ("A", 4, "short"), ("D", 5, "short")):
        pair = ADELogPairs(QQ).at21(letter, rank)
        assert pair.source_variant() == expected
        assert pair.base_pair().dynkin_rank() == rank


def test_primed_a_polygon_uses_the_table_four_endpoint() -> None:
    r"""Table 4's 'A_{2n-3} polygon for 'A^-_{2n-2} ends at (2n-3, 0)."""
    parameter = _ade_parameter("A", 4, ("prime",), False)
    vertices, point = _a_family_polygon_data(4, ("prime",), parameter)

    assert parameter == 3
    assert vertices == ((2, 2), (0, 1), (0, 0), (3, 0))
    assert point == (2, 2)


def test_primed_rank_two_a_polygon_uses_the_a_prime_one_endpoint() -> None:
    r"""The first even-rank primed case A^-_2 has polygon A'_1."""
    pair = ADELogPairs(QQ).at21("A", 2, variant="'A^-")
    vertices = {
        tuple(int(coordinate) for coordinate in vertex)
        for vertex in pair.base_pair().polygon().vertices()
    }

    assert pair.base_pair().dynkin_rank() == 2
    assert (1, 0) in vertices
    assert (2, 0) not in vertices


def test_primed_odd_rank_a_polygon_uses_the_a_prime_2n_minus_1_endpoint() -> None:
    r"""The odd-rank primed family A'_{2n-1} ends at the pair rank."""
    pair = ADELogPairs(QQ).at21("A", 3, variant="'A")
    vertices = {
        tuple(int(coordinate) for coordinate in vertex)
        for vertex in pair.base_pair().polygon().vertices()
    }

    assert (3, 0) in vertices
    assert (2, 0) not in vertices
