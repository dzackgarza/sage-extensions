r"""Functorial transport of Mor/End/Aut category packets."""

from __future__ import annotations

from collections.abc import Callable

from sage.categories.morphism import Morphism

from sage_extensions.categories.abstract_categories.arrow_categories import (
    _isomorphism_from_known_inverse_pair,
)
from sage_extensions.categories.abstract_categories.mor_categories import (
    _DiscreteTwoMorCategoryOf,
)
from sage_extensions.categories.functors.core import Functor


def _arrow_of(mor_category, arrow_object):
    r"""The arrow that an object of a Mor category is.

    The objects of ``Hom_C(A, B)`` are the arrows ``A -> B``; the Mor category
    presents one either as the arrow or as its arrow object.  The
    2-Mor at that object has the object as its source, normalized by the Mor
    category itself, so the arrow is read from there for either presentation.
    ``two_mor`` is the spelling both Mor-category shapes share and that no
    enrichment of the Mor object (a group of automorphisms, say) rebinds.
    """
    return mor_category.two_mor(arrow_object, arrow_object).domain().arrow()


class _InducedMorFunctor(Functor):
    r"""A lift of ``F`` to ``Hom_C(A,B) -> Hom_D(F(A),F(B))``.

    The target's constructor admits the image arrow and gives its selected
    representation: an element of an enriched Mor, or a constructed object
    of an unenriched fixed category.  Raw-arrow membership is not object
    placement in the latter.  The common functor action owns admission and
    caches both objects and 2-arrows, as for End and Aut below.

    For a discrete source Mor the arrow action is forced. Otherwise the
    construction requires ``on_two_morphism``, except for the canonical lift
    of the identity functor. The supplied action must preserve identity and
    vertical composition. It is local to this fixed Mor: an ordinary functor
    does not determine an action on natural transformations, and a local lift
    does not assert the horizontal coherence of a 2-functor. Compare Mathlib,
    ``CategoryTheory.PrelaxFunctor.map₂`` / ``map₂_id`` / ``map₂_comp`` in
    ``Mathlib/CategoryTheory/Bicategory/Functor/Prelax.lean``.
    """

    def __init__(
        self, functor, domain_object, codomain_object, *,
        on_two_morphism: Callable[[Morphism], Morphism] | None = None,
    ) -> None:
        self._functor = functor
        source = functor.domain().category_packet().Mors().Of(
            domain_object,
            codomain_object,
        )
        target = functor.codomain().category_packet().Mors().Of(
            functor.on_object(domain_object),
            functor.on_object(codomain_object),
        )
        Functor.__init__(self, source, target)
        self._initialize_two_morphism_action(on_two_morphism)

    def base_functor(self):
        return self._functor

    def _initialize_two_morphism_action(
        self, action: Callable[[Morphism], Morphism] | None,
    ) -> None:
        r"""Fix the local arrow action at construction, before the lift escapes.

        The private family declaration selects the discrete realization at
        this constructor boundary (OWN-06). No arrow's membership, endpoint
        equality or exposed methods are used as a proof that it is an identity.
        """
        match action:
            case None:
                match self.domain().MorCategory():
                    case _DiscreteTwoMorCategoryOf():
                        self._two_morphism_action = self._discrete_two_morphism_image
                    case _ if self.base_functor().factors().cardinality() == 0:
                        self._two_morphism_action = lambda arrow: arrow
                    case _:
                        raise TypeError(
                            f"the functor induced on Mor-categories by {self.base_functor()} needs its action on "
                            "2-morphisms (on_two_morphism), because the source Mor-categories are not discrete"
                        )
            case _ if callable(action):
                self._two_morphism_action = action
            case _:
                raise TypeError(
                    f"the action on 2-morphisms must be a function, but {action!r} is not callable"
                )

    def _discrete_two_morphism_image(self, morphism: Morphism) -> Morphism:
        r"""Map the identity supplied by the declared discrete source Mor."""
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        return self.codomain().two_mor(source, target).identity()

    def _apply_object(self, arrow_object):
        image = self.base_functor().on_morphism(_arrow_of(self.domain(), arrow_object))
        return self.codomain()(image)

    def _apply_morphism(self, morphism):
        return self._two_morphism_action(morphism)

    def _repr_(self):
        return f"Mor functor induced by {self.base_functor()}"


class _InducedEndFunctor(_InducedMorFunctor):
    r"""The functor ``End_C(A) -> End_D(F(A))`` induced by ``F``."""

    def __init__(
        self, functor, obj, *,
        on_two_morphism: Callable[[Morphism], Morphism] | None = None,
    ) -> None:
        self._functor = functor
        source = functor.domain().category_packet().Ends().Of(obj)
        target = functor.codomain().category_packet().Ends().Of(
            functor.on_object(obj)
        )
        Functor.__init__(self, source, target)
        self._initialize_two_morphism_action(on_two_morphism)

    def _repr_(self):
        return f"End functor induced by {self.base_functor()}"


class _InducedAutFunctor(_InducedMorFunctor):
    r"""The functor ``Aut_C(A) -> Aut_D(F(A))`` induced by ``F``.

    An object of ``Aut_C(A)`` is an isomorphism, the pair of mutually inverse
    arrows; a functor preserves inverses, so the image pair is again one.
    """

    def __init__(
        self, functor, obj, *,
        on_two_morphism: Callable[[Morphism], Morphism] | None = None,
    ) -> None:
        self._functor = functor
        source = functor.domain().category_packet().Auts().Of(obj)
        target = functor.codomain().category_packet().Auts().Of(
            functor.on_object(obj)
        )
        Functor.__init__(self, source, target)
        self._initialize_two_morphism_action(on_two_morphism)

    def _apply_object(self, arrow_object):
        isomorphism = _arrow_of(self.domain(), arrow_object)
        forward = self.base_functor().on_morphism(isomorphism.forward())
        inverse = self.base_functor().on_morphism(isomorphism.inverse().forward())
        return self.codomain()(
            _isomorphism_from_known_inverse_pair(
                forward, inverse, base_category=self.codomain().base_category()
            )
        )

    def _repr_(self):
        return f"Aut functor induced by {self.base_functor()}"
