r"""A finitely generated free algebra supplies the chosen presentation it has.

``A = Free(S)`` on a finite set ``S`` is presented by ``S`` and no relations:
its framing ``Free(S) -> A`` is an isomorphism, so the presentation ring is
``A`` itself and nothing is imposed on the generators.  Every object of
``AlgebrasWithChosenFinitePresentation`` answers ``selected_algebra_presentation()``
with one chosen finite presentation, and the presentation ring, the relation
family, the quotient map and the lift are read off that presentation instead of
being stated beside it.

Derivation: a map out of a free algebra is any map on ``S`` (the universal
property), so no relation holds of its generators; the quotient map of the
presentation by no relations is therefore the identity, and an element lifts to
itself.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_polynomial_ring_supplies_its_frame_and_no_relations() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    presentation = plane.selected_algebra_presentation()

    assert plane in FreeAlgebras(QQ).FinitelyGeneratedAsAlgebra()
    assert presentation.truncation() == 1
    assert presentation.level(0) is plane
    assert presentation.generating_set() is plane.algebra_generating_set()
    assert presentation.relations().index_set().cardinality() == 0
    assert plane.selected_algebra_resolution() is presentation

    assert plane.presentation_ring() is presentation.level(0)
    assert plane.relations() is presentation.relations()
    assert plane.algebra_presentation_morphism() is presentation.augmentation()
    assert plane.algebra_presentation_morphism()(x) == x
    assert plane.algebra_presentation_morphism()(x * y) == x * y
    assert plane.lift_to_presentation(x * y) == x * y


def test_the_free_semigroup_algebra_supplies_its_frame_and_no_relations() -> None:
    algebra = AffineSemigroupAlgebras(QQ)(((1, 0), (0, 1)), names=("x", "y"))
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    presentation = algebra.selected_algebra_presentation()

    assert presentation.truncation() == 1
    assert presentation.level(0) is algebra
    assert presentation.generating_set() is algebra.algebra_generating_set()
    assert presentation.relations().index_set().cardinality() == 0
    assert algebra.presentation_ring() is presentation.level(0)
    assert algebra.relations() is presentation.relations()
    assert algebra.algebra_presentation_morphism()(x * y) == x * y
    assert algebra.lift_to_presentation(x * y) == x * y


def test_a_free_algebra_is_built_with_its_frame_and_presents_it_on_request() -> None:
    r"""A free algebra is constructed with its frame, not with a presentation.

    ``Free(S) -> A`` is a length-zero free resolution (``CAT-29``): construction
    fixes that frame and nothing finer.  The chosen finite presentation is the
    same datum read the other way -- ``A`` presented on itself by ``S`` with no
    relations -- so it is realized from the frame when it is asked for, and the
    algebra then carries it as its selected resolution.
    """
    algebra = QQ["s549, t549"]
    frame = algebra.selected_algebra_resolution()

    assert frame.truncation() == 0
    assert frame.level(0) is algebra
    assert frame.generating_set() is algebra.algebra_generating_set()

    presentation = algebra.selected_algebra_presentation()

    assert presentation.truncation() == 1
    assert algebra.selected_algebra_resolution() is presentation
    assert presentation.generating_set() is frame.generating_set()
    assert presentation.relations().index_set().cardinality() == 0


def test_the_tensor_algebra_supplies_its_frame_and_no_relations() -> None:
    r"""The free associative algebra presents on itself, not on a commutative model."""
    algebra = Modules(QQ).free_module(("a", "b")).tensor_algebra()
    a = algebra.algebra_generator("a")
    b = algebra.algebra_generator("b")
    presentation = algebra.selected_algebra_presentation()

    assert presentation.truncation() == 1
    assert presentation.level(0) is algebra
    assert presentation.relations().index_set().cardinality() == 0
    assert algebra.presentation_ring() is algebra
    assert algebra.algebra_presentation_morphism()(a * b) == a * b
    assert algebra.algebra_presentation_morphism()(a * b) != b * a
    assert algebra.lift_to_presentation(b * a) == b * a
