r"""Limits and colimits in $\mathbf{Set}$ over small poset shapes, pullbacks and pushouts.

The limit of the constant diagram with value $S$ over a connected category
is $S$, and so is its colimit; over the discrete category on two objects the
limit is $S \times S$ and the colimit $S \sqcup S$.  For $S = \{0, 1\}$
these have $2, 2, 4, 4$ elements.  The fiber product of
$f : \{0, \dots, 3\} \to \{0, 1\}$, $n \mapsto n \bmod 2$, and
$g : \{0, 1, 2\} \to \{0, 1\}$, $0 \mapsto 0$, $1, 2 \mapsto 1$, is
$\{(a, b) : f(a) = g(b)\}$, with $2 \cdot 1 + 2 \cdot 2 = 6$ elements.  The
pushout of two points glued at one point is the wedge, with $2 + 2 - 1 = 3$
elements.  Each value is the definition of the limit or colimit in
$\mathbf{Set}$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_set_coequalizer_uses_selected_parallel_morphisms() -> None:
    r"""The ordinary set Mor of a finite parallel pair retains its projection."""
    source = Sets.Δ[1]
    target = Sets.Δ[2]
    left = Sets().Mor(source, target)(lambda point: target(point))
    right = Sets().Mor(source, target)(lambda point: target(point + 1))
    construction = Sets().coequalizer_construction(left, right)
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())

    assert construction.object().cardinality() == cardinal(1)
    assert projection(target(0)) == projection(target(2))
    assert projection * left == projection * right


def test_empty_relation_on_infinite_target_has_identity_coequalizer() -> None:
    r"""No identifications on ZZ give ZZ, not opaque symbolic classes."""
    source = Sets.Δ[-1]
    target = Sets()(ZZ)
    left = Sets().Mor(source, target)(lambda _point: target(0))
    right = Sets().Mor(source, target)(lambda _point: target(1))
    construction = Sets().coequalizer_construction(left, right)
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())
    target_leg = Sets().Mor(target, target)(lambda value: target(2 * value))
    cocone = construction.diagram().Cocones().cocone(
        target, lambda index: target_leg * left if index is shape.source() else target_leg
    )
    factor = construction.factor(cocone).apex_map()

    assert construction.object() is target
    assert projection(target(3)) == target(3)
    assert factor(projection(target(3))) == target(6)


def test_identical_parallel_maps_on_infinite_sets_have_identity_coequalizer() -> None:
    r"""The coequalizer of f=f retains the target even for infinite relation data."""
    source = Sets()(ZZ)
    target = Sets()(ZZ)
    arrow = Sets().Mor(source, target)(lambda value: target(value + 2))
    construction = Sets().coequalizer_construction(arrow, arrow)
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())
    target_leg = Sets().Mor(target, target)(lambda value: target(3 * value))
    cocone = construction.diagram().Cocones().cocone(
        target, lambda index: target_leg * arrow if index is shape.source() else target_leg
    )
    factor = construction.factor(cocone).apex_map()

    assert construction.object() is target
    assert projection(target(7)) == target(7)
    assert factor(projection(target(7))) == target(21)


def test_generated_relation_on_infinite_set_knows_its_defining_edge() -> None:
    r"""An enumerated relation source proves its generating identifications."""
    source = Sets.Δ[0]
    target = Sets()(ZZ)
    left = Sets().Mor(source, target)(lambda _point: target(2))
    right = Sets().Mor(source, target)(lambda _point: target(5))
    construction = Sets().coequalizer_construction(left, right)
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())

    assert projection(target(2)) == projection(target(5))
    assert projection(target(5)) == projection(target(2))
    assert projection * left == projection * right


def test_finite_generated_relation_on_infinite_set_closes_paths() -> None:
    r"""Edges 2~5 and 5~9 yield 2~9 without enumerating the target ZZ."""
    source = Sets.Δ[1]
    target = Sets()(ZZ)
    left = Sets().Mor(source, target)(lambda point: target((2, 5)[int(point)]))
    right = Sets().Mor(source, target)(lambda point: target((5, 9)[int(point)]))
    construction = Sets().coequalizer_construction(left, right)
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())

    assert projection(target(2)) == projection(target(9))
    assert projection(target(9)) == projection(target(2))
    assert projection * left == projection * right
    # Decidable equality on this finite relation support also separates
    # components without enumerating the ambient infinite target.
    assert projection(target(2)) != projection(target(11))
    assert projection(target(11)) != projection(target(9))


def test_set_equalizer_uses_selected_parallel_morphisms_and_inclusion() -> None:
    r"""The equalizer of the identity and a transposition fixes one point."""
    source = Sets.Δ[2]
    identity = Sets().Mor(source, source).identity()
    transpose = Sets().Mor(source, source)(
        lambda point: source(1 - point) if point < 2 else source(2)
    )
    construction = Sets().equalizer_construction(identity, transpose)
    shape = construction.diagram().domain()
    inclusion = construction.structure_morphism(shape.source())

    assert construction.object().cardinality() == cardinal(1)
    assert all(inclusion(point) == source(2) for point in construction.object())
    assert identity * inclusion == transpose * inclusion


def _cospan_shape():
    return PosetCategory(Sets()(("a", "b", "c")), le=lambda left, right: left == right or right == "c")


def _span_shape():
    return PosetCategory(Sets()(("a", "b", "c")), le=lambda left, right: left == right or left == "c")


def _discrete_shape():
    return PosetCategory(Sets()(("a", "b")), le=lambda left, right: left == right)


def test_the_constant_diagram_on_the_cospan_shape_has_limit_and_colimit_two_points() -> None:
    shape = _cospan_shape()
    diagram = Cat().Mor(shape, Sets()).constant_functor(Sets.Δ[1])

    assert Sets().Limits(shape).construction(diagram).object().cardinality() == cardinal(2)
    assert Sets().Colimits(shape).construction(diagram).object().cardinality() == cardinal(2)


def test_the_constant_diagram_on_the_span_shape_has_limit_two_points() -> None:
    shape = _span_shape()
    diagram = Cat().Mor(shape, Sets()).constant_functor(Sets.Δ[1])

    assert Sets().Limits(shape).construction(diagram).object().cardinality() == cardinal(2)


def test_the_constant_diagram_on_the_span_shape_has_colimit_two_points() -> None:
    shape = _span_shape()
    diagram = Cat().Mor(shape, Sets()).constant_functor(Sets.Δ[1])

    assert Sets().Colimits(shape).construction(diagram).object().cardinality() == cardinal(2)


def test_the_limit_over_two_discrete_objects_is_the_product() -> None:
    shape = _discrete_shape()
    diagrams = Cat().Mor(shape, Sets())
    diagram = diagrams.constant_functor(Sets.Δ[1])

    assert Sets().Limits(shape).construction(diagram).object().cardinality() == cardinal(4)
    assert Sets().limit_functor(shape)(diagrams(diagram)).cardinality() == cardinal(4)


def test_the_colimit_over_two_discrete_objects_is_the_disjoint_union() -> None:
    shape = _discrete_shape()
    diagrams = Cat().Mor(shape, Sets())
    diagram = diagrams.constant_functor(Sets.Δ[1])

    assert Sets().Colimits(shape).construction(diagram).object().cardinality() == cardinal(4)
    assert Sets().colimit_functor(shape)(diagrams(diagram)).cardinality() == cardinal(4)


def test_the_fiber_product_of_parity_and_a_two_class_map_has_six_elements() -> None:
    parity_source = Sets.Δ[3]
    other_source = Sets.Δ[2]
    bits = Sets.Δ[1]
    parity = Sets().Mor(parity_source, bits)(lambda n: bits(n % 2))
    nonzero = Sets().Mor(other_source, bits)(lambda n: bits(0) if n == 0 else bits(1))

    assert Sets().fiber_product(parity, nonzero).cardinality() == cardinal(6)


def test_two_points_glued_at_a_point_form_a_three_point_wedge() -> None:
    point = Sets.Δ[0]
    two = Sets.Δ[1]
    at_zero = Sets().Mor(point, two)(lambda _p: two(0))
    span = Sets().span(at_zero, at_zero)

    assert span.apex() is point
    assert span.left_leg() == at_zero
    assert Sets().pushout(at_zero, at_zero).cardinality() == cardinal(3)
    assert span.pushout().cardinality() == cardinal(3)
