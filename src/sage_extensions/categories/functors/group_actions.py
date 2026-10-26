r"""The trivial action, invariants and coinvariants as scalar change along the augmentation.

For the augmentation ``epsilon: R[G] -> R`` the adjoint triple
``R tensor_{R[G]} - -| Res_epsilon -| Hom_{R[G]}(R, -)`` is
``(-)_G -| Triv_G -| (-)^G``: restriction along ``epsilon`` equips a module
with the trivial action, scalar extension along it is the coinvariants
``M_G = R tensor_{R[G]} M`` and coextension the invariants
``M^G = Hom_{R[G]}(R, M)`` (Weibel, *An Introduction to Homological
Algebra*, §6.1).  The functors here are the scalar-change functors of
``scalar_change`` specialized to that hypothesis, with the group module's
represented equalizer and coequalizer as the computation.
"""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.algebras.group_algebras import GroupAlgebras
from sage_extensions.categories.functors.core import (
    Functor,
    NaturalTransformation,
)
from sage_extensions.categories.functors.scalar_change import (
    _BaseChangeAdjunction,
    _CoextensionOfScalarsFunctor,
    _RestrictionCoextensionAdjunction,
    _RestrictionOfScalarsFunctor,
    _ScalarExtensionFunctor,
)
from sage_extensions.categories.rings.ring_foundation import OwnedRings, _owned_ring
from sage_extensions.categories.sets.set_categories import Sets


class GroupActionFunctor(Functor):
    r"""An actual action functor ``BG -> C`` on one represented object.

    ``action(g)`` must return the endomorphism of the selected object induced
    by ``g``.  Concrete action owners use this class only after their own
    action datum has been validated; the generic ``GObjects(G,C)`` constructor
    accepts this or any other genuine functor with the same endpoints.
    """

    def __init__(self, group, category, obj, action) -> None:
        self._group = group
        self._category = category
        self._object = obj
        self._action = action
        if obj not in category:
            raise TypeError(f"{obj} is not an object of {category}")
        super().__init__(group.classifying_category(), category)

    def group(self):
        return self._group

    def underlying_object(self):
        return self._object

    def _apply_object(self, obj):
        if obj is not self.domain().an_object():
            raise ValueError(f"the classifying category BG has one object, and {obj} is not it")
        return self.underlying_object()

    def _apply_morphism(self, morphism):
        endomorphisms = self.codomain().Mor(
            self.underlying_object(), self.underlying_object()
        )
        return endomorphisms(self._action(morphism.group_element()))

    def _repr_(self):
        return f"{self.group()}-action functor on {self.underlying_object()}"


def _action_functor_of(acted, group, category):
    r"""Return the unique represented ``BG -> C`` action carried by ``acted``."""
    from sage_extensions.categories.abstract_categories.cat import Cat

    functor_category = Cat().functor_mor(group.classifying_category(), category)
    if acted in functor_category:
        return acted.arrow().functor()
    functor = acted.action_functor()
    if functor.domain() != group.classifying_category() or functor.codomain() != category:
        raise ValueError(
            f"the action of {group} on an object of {category} must be a functor BG -> {category}, but "
            f"{functor} is a functor {functor.domain()} -> {functor.codomain()}"
        )
    return functor


def _underlying_equivariant_arrow(arrow, group, category):
    r"""Forget equivariance from either a natural transformation or a concrete arrow."""
    from sage_extensions.categories.abstract_categories.cat import Cat
    from sage_extensions.categories.group.g_objects import GObjects

    functor_category = Cat().functor_mor(group.classifying_category(), category)
    if arrow.domain() in functor_category and arrow.codomain() in functor_category:
        point = group.classifying_category().an_object()
        return arrow.component(point)
    acted = GObjects(group, category)
    if arrow in acted.Mor(arrow.domain(), arrow.codomain()):
        return arrow.underlying_arrow()
    return category.Mor(arrow.domain(), arrow.codomain())(arrow)


class ForgetGroupActionFunctor(Functor):
    r"""Evaluation at the unique object, ``[BG,C] -> C``."""

    _faithful = True

    def __init__(self, group, category) -> None:
        from sage_extensions.categories.group.g_objects import GObjects

        self._group = group
        self._category = category
        super().__init__(GObjects(group, category), category)

    def group(self):
        return self._group

    def _apply_object(self, acted):
        action = _action_functor_of(acted, self.group(), self.codomain())
        return action(action.domain().an_object())

    def _apply_morphism(self, arrow):
        return _underlying_equivariant_arrow(arrow, self.group(), self.codomain())

    def _repr_(self):
        return f"Forgetful functor from {self.group()}-objects in {self.codomain()}"


class TransportGroupActionFunctor(Functor):
    r"""Postcomposition ``[BG,C] -> [BG,D]`` by a functor ``C -> D``."""

    def __init__(self, group, transport) -> None:
        from sage_extensions.categories.group.g_objects import GObjects

        self._group = group
        self._transport = transport
        super().__init__(
            GObjects(group, transport.domain()),
            GObjects(group, transport.codomain()),
        )

    def group(self):
        return self._group

    def transport_functor(self):
        return self._transport

    def _apply_object(self, acted):
        action = _action_functor_of(
            acted,
            self.group(),
            self.transport_functor().domain(),
        )
        return self.codomain()(action.then(self.transport_functor()))

    def _apply_morphism(self, arrow):
        source = self.object_image(arrow.domain())
        target = self.object_image(arrow.codomain())
        component = self.transport_functor()(
            _underlying_equivariant_arrow(
                arrow,
                self.group(),
                self.transport_functor().domain(),
            )
        )
        source_action = _action_functor_of(
            source, self.group(), self.transport_functor().codomain()
        )
        target_action = _action_functor_of(
            target, self.group(), self.transport_functor().codomain()
        )
        return self.codomain().Mor(source, target)(
            NaturalTransformation(
                source_action,
                target_action,
                lambda _obj: component,
            )
        )

    def _repr_(self):
        return f"Transport of {self.group()}-actions through {self.transport_functor()}"


@cached_function(key=lambda algebra: id(algebra))
def _group_algebra_augmentation_ring_map(algebra):
    r"""Return the canonical augmentation with literal ring target ``R``.

    The algebra augmentation ends at the scalar algebra ``S = R`` over
    itself. If its retained carrier differs from the ring ``R``, the module
    defining ``S`` retains the actual ring elements. Reading those elements
    gives the canonical ring isomorphism ``S -> R``, inverse to its identity
    scalar structure. Compose that map with the retained augmentation; never
    identify its two endpoints. This supplier is used by ``Modules._augmentation``
    and the canonical augmentation recognizer below.
    """
    from sage_extensions.categories.algebras.algebras import _scalar_module

    ring = _owned_ring(algebra.base_ring())
    assert algebra in GroupAlgebras(ring), (
        f"the canonical group augmentation requires an actual group algebra over {ring}"
    )
    augmentation = algebra.augmentation()
    if augmentation.codomain() is ring:
        return augmentation
    scalars = _scalar_module(ring)
    assert augmentation.codomain() is scalars, (
        f"the augmentation of {algebra} must retain the scalar algebra of {ring}"
    )
    module = scalars.unformed_module()
    comparison = OwnedRings().Mor(scalars, ring).elementwise(
        lambda element: module(element).underlying_element()
    )
    return comparison * augmentation


def _is_augmentation_of_group_algebra(ring_map) -> bool:
    r"""Recognize either retained form of the canonical group augmentation.

    The augmentation is a canonical construction of the group algebra and is
    cached by that owner. Its algebra target is the scalar algebra of ``R``;
    scalar change also uses its canonical composite to the literal ring ``R``.
    Recognize these actual maps without manufacturing a generating family of
    ``G`` or deciding arbitrary equality of functions. Specializations over
    ``R`` must additionally require that literal target.
    """
    source = _owned_ring(ring_map.domain())
    if source not in GroupAlgebras(source.base_ring()):
        return False
    return (
        ring_map is source.augmentation()
        or ring_map is _group_algebra_augmentation_ring_map(source)
    )


def _augmentation_data(ring_map):
    assert ring_map.is_group_algebra_augmentation(), (
        f"{ring_map} is not the augmentation of a group algebra"
    )
    return _owned_ring(ring_map.domain()).group()


def _invariant_element(group_module, invariant_module, element):
    r"""Read an invariant-module element inside ``group_module``."""
    if group_module.is_trivial_action():
        return group_module(element)
    return group_module(invariant_module.inclusion()(element))


def _lift_to_invariants(group_module, invariant_module, element):
    r"""Lift a known invariant element from ``group_module``."""
    module = group_module.unformed_module()
    if group_module.is_trivial_action():
        return module(element)
    return invariant_module.inclusion().lift(module(element))


def _coinvariant_projection(group_module, coinvariants, element):
    module = group_module.unformed_module()
    if group_module.is_trivial_action():
        return module(element)
    return coinvariants.presentation_projection()(module(element))


class _TrivialActionFunctor(_RestrictionOfScalarsFunctor):
    r"""``Triv_G : Modules(R) -> Modules(R[G])``, restriction along the augmentation."""

    def __init__(self, ring_map) -> None:
        super().__init__(ring_map)
        self._group = _augmentation_data(ring_map)

    def group(self):
        return self._group

    def _apply_object(self, module):
        r"""``M`` with the action ``G -> Aut_R(M)`` sending every group element to the identity."""
        automorphisms = module.Aut()
        identity = automorphisms.one()
        trivial = Sets().Mor(self.group(), automorphisms)(lambda _group_element: identity)
        return self.codomain()(module, trivial)

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return source.Mor(target)._from_equivariant_images(
            morphism,
        )

    def _repr_(self):
        return f"Trivial {self.group()}-action functor"


class _InvariantsFunctor(_CoextensionOfScalarsFunctor):
    r"""``(-)^G : Modules(R[G]) -> Modules(R)``, coextension along the augmentation."""

    def __init__(self, ring_map) -> None:
        super().__init__(ring_map)
        self._group = _augmentation_data(ring_map)

    def group(self):
        return self._group

    def _apply_object(self, group_module):
        return group_module.module_invariants()

    def _apply_morphism(self, morphism):
        source_invariants = self(morphism.domain())
        target_invariants = self(morphism.codomain())

        def image(label):
            source = _invariant_element(
                morphism.domain(),
                source_invariants,
                source_invariants.module_generator(label),
            )
            return _lift_to_invariants(
                morphism.codomain(),
                target_invariants,
                morphism(source),
            )

        return source_invariants.module_category().Mor(source_invariants, target_invariants)(image)

    def _repr_(self):
        return f"{self.group()}-invariants functor"


class _CoinvariantsFunctor(_ScalarExtensionFunctor):
    r"""``(-)_G : Modules(R[G]) -> Modules(R)``, scalar extension along the augmentation."""

    def __init__(self, ring_map) -> None:
        super().__init__(ring_map)
        self._group = _augmentation_data(ring_map)

    def group(self):
        return self._group

    def _apply_object(self, group_module):
        return group_module.module_coinvariants()

    def _apply_morphism(self, morphism):
        source_coinvariants = self(morphism.domain())
        target_coinvariants = self(morphism.codomain())

        def image(label):
            representative = morphism.domain().module_generator(label)
            return _coinvariant_projection(
                morphism.codomain(),
                target_coinvariants,
                morphism(representative),
            )

        return source_coinvariants.module_category().Mor(source_coinvariants, target_coinvariants)(image)

    def _repr_(self):
        return f"{self.group()}-coinvariants functor"


class _TrivialInvariantsAdjunction(_RestrictionCoextensionAdjunction):
    r"""``Triv_G ⊣ (-)^G``, restriction/coextension along the augmentation."""

    _restriction_functor = _TrivialActionFunctor
    _coextension_functor = _InvariantsFunctor

    def _unit_component(self, module):
        invariants = self.right_adjoint()(self.left_adjoint()(module))
        return module.module_category().Mor(module, invariants)(
            lambda label: invariants.module_generator(label)
        )

    def _counit_component(self, group_module):
        invariants = self.right_adjoint()(group_module)
        trivial = self.left_adjoint()(invariants)
        return trivial.Mor(group_module)(
            lambda label: _invariant_element(
                group_module,
                invariants,
                invariants(trivial.module_generator(label)),
            )
        )

    def _repr_(self):
        return f"Trivial-action/invariants adjunction for {self.left_adjoint().group()}"


class _CoinvariantsTrivialAdjunction(_BaseChangeAdjunction):
    r"""``(-)_G ⊣ Triv_G``, base change along the augmentation."""

    _extension_functor = _CoinvariantsFunctor
    _restriction_functor = _TrivialActionFunctor

    def _unit_component(self, group_module):
        coinvariants = self.left_adjoint()(group_module)
        trivial = self.right_adjoint()(coinvariants)
        return group_module.Mor(trivial)(
            lambda label: trivial(
                _coinvariant_projection(
                    group_module,
                    coinvariants,
                    group_module.module_generator(label),
                )
            )
        )

    def _counit_component(self, module):
        coinvariants = self.left_adjoint()(self.right_adjoint()(module))
        if coinvariants is not module:
            raise ValueError(
                f"the coinvariants of {module} with the trivial action are {coinvariants}, which is not {module} itself"
            )
        return module.module_category().Mor(module, module).identity()

    def _repr_(self):
        return f"Coinvariants/trivial-action adjunction for {self.left_adjoint().group()}"


class RestrictionOfGroupActionFunctor(Functor):
    r"""``phi^*: GObjects(G, C) -> GObjects(H, C)`` for a group morphism ``phi: H -> G``.

    A ``G``-object is a group morphism ``rho: G -> Aut_C(X)``; composing with
    ``phi`` gives ``rho phi: H -> Aut_C(X)``, so restriction changes which
    group acts and nothing about the object of ``C`` underneath.  An
    equivariant morphism stays equivariant because both endpoints restrict
    along the same ``phi``.  Nothing here uses injectivity of ``phi``: the
    inclusion of a subgroup is one case, and a surjection onto ``G`` or the
    projection of a semidirect factor is admitted on the same footing.  On
    ``Modules(R[G])`` this is restriction of scalars along ``R[H] -> R[G]``
    (Serre, *Linear Representations of Finite Groups*, §7.1), which
    restriction along a subgroup computes with the
    module presentation in hand.
    """

    def __init__(self, group_morphism, underlying_category) -> None:
        from sage_extensions.categories.group.g_objects import GObjects

        self._group_morphism = group_morphism
        self._underlying_category = underlying_category
        Functor.__init__(
            self,
            GObjects(group_morphism.codomain(), underlying_category),
            GObjects(group_morphism.domain(), underlying_category),
        )

    def group_morphism(self):
        r"""Return ``phi: H -> G``, the morphism the action is restricted along."""
        return self._group_morphism

    def _apply_object(self, acted):
        morphism = self.group_morphism()
        category = self._underlying_category

        # Preserve the represented underlying object when that owner already
        # knows how to equip the restricted action.  The generic fallback is
        # literally precomposition BH -> BG -> C.
        from sage_extensions.categories.sets.set_categories import Sets

        if category is Sets():
            from sage_extensions.categories.group.g_sets import FiniteGSets

            if acted in FiniteGSets(morphism.codomain()):
                return FiniteGSets(morphism.domain())(
                    acted.point_set(),
                    lambda group_element, point: acted.act(morphism(group_element), point),
                )

        # The affine owner retains the coordinate algebra and constructs the
        # restricted action on it, including the resulting fixed-locus data.
        from sage_extensions.categories.schemes.schemes import (
            AffineGSchemes,
            Schemes,
        )

        match category:
            case Schemes():
                base_ring = category.base_ring()
                if acted in Schemes(base_ring).Affine():
                    return AffineGSchemes(morphism.domain(), base_ring)(
                        acted,
                        lambda group_element: acted.action_of(morphism(group_element)),
                    )

        action = _action_functor_of(acted, morphism.codomain(), category)
        from sage_extensions.categories.group.classifying_categories import (
            ClassifyingFunctor,
        )

        return self.codomain()(ClassifyingFunctor(morphism).then(action))

    def _apply_morphism(self, arrow):
        source = self.object_image(arrow.domain())
        target = self.object_image(arrow.codomain())
        category = self._underlying_category
        underlying = _underlying_equivariant_arrow(
            arrow,
            self.group_morphism().codomain(),
            category,
        )
        source_functors = self.codomain().functor_category()
        if source in source_functors and target in source_functors:
            source_action = _action_functor_of(
                source, self.group_morphism().domain(), category
            )
            target_action = _action_functor_of(
                target, self.group_morphism().domain(), category
            )
            return self.codomain().Mor(source, target)(
                NaturalTransformation(
                    source_action,
                    target_action,
                    lambda _obj: underlying,
                )
            )

        from sage_extensions.categories.schemes.schemes import (
            AffineGSchemes,
            Schemes,
            _affine_morphism_from_pullback,
        )

        match category:
            case Schemes():
                affine_actions = AffineGSchemes(
                    self.group_morphism().domain(), category.base_ring()
                )
                if source in affine_actions and target in affine_actions:
                    restricted_mor = self.codomain().Mor(source, target)
                    if arrow._is_the_identity():
                        return restricted_mor.identity()
                    # Restriction keeps both coordinate algebras literally;
                    # the same pullback therefore has these exact endpoints.
                    restricted = _affine_morphism_from_pullback(
                        source, target, underlying.coordinate_algebra_morphism()
                    )
                    return restricted_mor._from_equivariant_arrow(
                        restricted, equivariance_premises=(arrow,)
                    )
        return self.codomain().Mor(source, target)(underlying)

    def _repr_(self):
        morphism = self.group_morphism()
        return (
            f"Restriction of actions along {morphism.domain()} -> {morphism.codomain()}"
        )


__all__ = [
    "ForgetGroupActionFunctor",
    "GroupActionFunctor",
    "RestrictionOfGroupActionFunctor",
    "TransportGroupActionFunctor",
]
