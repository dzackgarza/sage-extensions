r"""A functor exposes its image, induced Mor packets, endofunctor algebras, spans, and natural isomorphisms."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_functor_image_and_adopted_object_image_retain_the_same_set() -> None:
    identity = Sets().identity_functor()
    points = Sets.Δ[1]
    image_category = identity.Image()
    presented = image_category(points)

    assert identity.adopt_object_image(points, points) is points
    assert presented.preimage() is points
    assert presented.underlying_image() is points
    assert image_category.functor() is identity


def test_identity_functor_induces_mor_end_and_aut_functors() -> None:
    identity = Sets().identity_functor()
    points = Sets.Δ[1]
    swap = Sets().Mor(points, points)(lambda point: points(1 - int(point)))
    isomorphism = Sets().Core().Mor(points, points)(swap, swap)

    assert identity.induced_mor_functor(points, points)(swap) == swap
    assert identity.induced_end_functor(points)(swap) == swap
    assert identity.induced_aut_functor(points)(isomorphism) == isomorphism


def test_identity_endofunctor_algebra_category_retains_identity_structure() -> None:
    identity = Sets().identity_functor()
    points = Sets.Δ[1]
    algebras = identity.algebras()
    structure = Sets().Mor(points, points).identity()
    algebra = algebras.algebra(points, structure)

    assert algebras.endofunctor() is identity
    assert algebra in algebras


def test_two_object_constant_diagram_has_a_span_category_over_it() -> None:
    index = DiscreteCategory(finite_ordered_set((0, 1)))
    diagrams = Cat().Mor(index, Sets())
    diagram = diagrams.constant_functor(Sets.Δ[0])
    spans = diagram.Spans()

    assert spans.diagram() is diagram
    assert spans.target_category() is Sets()


def test_identity_functor_has_identity_natural_isomorphism_to_itself() -> None:
    identity = Sets().identity_functor()
    points = Sets.Δ[1]
    natural_identity = identity.natural_isomorphism_to(
        identity,
        lambda obj: Sets().Mor(obj, obj).identity(),
        lambda obj: Sets().Mor(obj, obj).identity(),
    )

    assert natural_identity.forward().transformation().component(points) == Sets().Mor(
        points,
        points,
    ).identity()
