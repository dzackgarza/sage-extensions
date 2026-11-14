r"""The underlying module of an algebra view: the ring, read along its own structure map.

An ``R``-algebra is a module over ``R``, and the forgetful functor
``U: Alg_R -> Mod_R`` changes which operations a map answers to, never the
object: ``U`` of a coefficient view is the view.  That is only useful when the
view is a *represented* ``R``-module, so this file states where that comes from:

* The module the algebra is built on is the ring read along its own structure
  map.  When the ring states a basis for exactly that reading
  (``_module_basis_along``), the module is built through the
  restriction-of-scalars constructor and keeps that basis and its finite
  presentation; when it does not, the bare scalar-action module is built, as
  before.
* The view keeps its own elements and its own algebra presentation, which is a
  different datum from the module presentation and is therefore named
  ``algebra_presentation()``; ``presentation()`` is the module relation
  morphism ``F_1 -> F_0``.
* A framed free module states an *empty* relation family: its chosen framing is
  a basis, so both its ``presentation()`` and the maintained
  ``_relation_morphism`` read must answer the zero morphism ``F(∅) -> M``, and
  never a shadowing generic "relations unknown".
* The cokernel of a map out of a presented module into a framed free one is the
  quotient of that module by the image: ``coker(F_0(M) -> F(N))``.

The kernel of the fat-point projection is stated in
``test_underlying_module_of_an_algebra_morphism.sage``; this file states the
owner facts that carry it.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.algebras.algebras import (
    Algebras,
    AlgebrasWithChosenFinitePresentation,
)
from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
    _relation_morphism,
)
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    ModulesWithChosenFinitePresentation,
    RestrictedScalarsModules,
)


def _fat_point():
    r"""``A = QQ[x]/(x^2)``, its coefficient composite and its ``QQ``-view ``B``."""
    polynomials = QQ["x"]
    x = polynomials.gen()
    algebra = polynomials.quotient_ring(x**2)
    coefficient_composite = (
        algebra.quotient_map() * polynomials.algebra_structure_morphism()
    )
    return polynomials, algebra, coefficient_composite, algebra.as_algebra_over(QQ)


def test_the_view_is_presented_over_its_coefficient_ring_by_the_retained_basis() -> None:
    r"""``QQ[x]/(x^2)`` over ``QQ``: two generators ``1``, ``x``, no relations."""
    polynomials, algebra, coefficient_composite, view = _fat_point()

    assert view in ModulesWithChosenFinitePresentation(QQ)
    assert view.module_generating_set().cardinality() == 2
    assert view.module_rank() == 2

    module = view.unformed_module()
    assert module.module_over_extension() is algebra
    assert module.ring_map() == coefficient_composite

    # The frame is a basis, so the reading states no relations at all: the
    # relation morphism lands in the same frame and has no columns.
    relations = view.presentation()
    assert tuple(relations.codomain().module_generating_set()) == tuple(
        module.framing_source().module_generating_set()
    )
    assert relations.domain().module_generating_set().cardinality() == 0

    images = [
        view(algebra(module.module_generator(label).underlying_element()))
        for label in view.module_generating_set()
    ]
    assert images[0] == view.one()
    assert images[1] == view(polynomials.gen())


def test_the_view_keeps_its_elements_and_states_its_two_presentations_by_name() -> None:
    r"""The algebra presentation is ``algebra_presentation()``; ``presentation()`` is the module's."""
    polynomials, algebra, coefficient_composite, view = _fat_point()
    x = polynomials.gen()

    assert view.one().parent() is view
    assert view(x) ** 2 == view.zero()

    assert view in AlgebrasWithChosenFinitePresentation(QQ)
    assert view.presentation_ring() is polynomials
    assert len(tuple(view.relations())) == 1
    family = view.algebra_presentation()
    assert tuple(family.index_set()) == ("presentation_ring", "relations")
    assert family("presentation_ring") is view.presentation_ring()

    # ``presentation()`` is the module relation morphism, not the family above.
    module_presentation = view.presentation()
    assert module_presentation is not family
    assert module_presentation.domain().module_generating_set().cardinality() == 0


def test_the_functor_leaves_the_view_in_place_and_reads_its_dimension_from_the_basis() -> None:
    r"""``U(B)`` is ``B``; its dimension is the retained basis cardinality, not a recursion."""
    polynomials, algebra, coefficient_composite, view = _fat_point()

    assert Algebras(QQ).underlying_module()(view) is view
    assert view.module_rank() == 2


def test_a_ring_that_states_no_basis_keeps_the_scalar_action_module() -> None:
    r"""``QQ[x]/(x^2)`` over ``ZZ`` states no basis, so nothing is invented for it."""
    polynomials, algebra, coefficient_composite, view = _fat_point()
    over_integers = algebra.as_algebra_over(ZZ)

    assert over_integers in Modules(ZZ)
    assert over_integers not in ModulesWithChosenFinitePresentation(ZZ)
    assert over_integers.one() == over_integers(1)


def test_the_zero_predicate_of_a_ring_read_over_itself_is_the_zero_ring() -> None:
    r"""``|Res_f(S)| = |S|``, so the reading is zero exactly when the ring is."""
    polynomials, algebra, coefficient_composite, view = _fat_point()
    reading = RestrictedScalarsModules(QQ)(algebra, coefficient_composite)

    assert reading.is_zero() is False

    trivial = ZZ.quotient_ring(ZZ.ideal([ZZ(1)]))
    assert trivial.one() == trivial.zero()
    zero_reading = RestrictedScalarsModules(ZZ)(
        trivial, trivial.algebra_structure_morphism()
    )
    assert zero_reading.is_zero() is True


def test_a_framed_free_module_states_an_empty_relation_family() -> None:
    r"""A basis is a length-zero free resolution: the relations are ``F(∅) -> M``."""
    line = QQ**1
    single = line.presentation()
    assert single.codomain() is line
    assert single.domain().module_generating_set().cardinality() == 0
    assert _relation_morphism(line).domain().module_generating_set().cardinality() == 0

    # ``QQ[x]/(x)`` is realized as a one-dimensional object; its stated
    # presentation is the same empty relation family, read through the
    # maintained accessor rather than through a generic answer for a module
    # that states no presentation.
    polynomials = QQ["x"]
    reduced = polynomials.quotient_ring(polynomials.ideal([polynomials.gen()]))
    reduced_presentation = reduced.presentation()
    assert reduced_presentation.codomain() is reduced
    assert reduced_presentation.domain().module_generating_set().cardinality() == 0
    assert _relation_morphism(reduced).domain().module_generating_set().cardinality() == 0


def test_the_cokernel_into_a_framed_free_module_is_the_quotient_of_its_cover() -> None:
    r"""``coker(M -> N)`` for framed free ``N`` is ``F(N) /`` the lifted image."""
    polynomials, algebra, coefficient_composite, view = _fat_point()
    x = polynomials.gen()
    line = polynomials.quotient_ring(polynomials.ideal([x])).as_algebra_over(QQ)
    projection = view.Mor(line)(
        {label: line.zero() for label in view.algebra_generating_set()}
    )
    underlying = Algebras(QQ).underlying_module()(projection)

    assert underlying.is_surjective() is True
    assert underlying.is_injective() is False
    assert underlying.cokernel().is_zero() is True

    # The zero map onto a line has the whole domain as kernel and the line as
    # cokernel: the quotient is only zero when the image spans the codomain.
    reading = RestrictedScalarsModules(QQ)(algebra, coefficient_composite)
    target = QQ**1
    zero_morphism = Modules(QQ).Mor(reading, target)(
        {label: target.zero() for label in reading.module_generating_set()}
    )
    assert zero_morphism.kernel().module_rank() == 2
    assert zero_morphism.is_surjective() is False
    cokernel = zero_morphism.cokernel()
    assert cokernel.module_rank() == 1
    assert cokernel.is_zero() is False
