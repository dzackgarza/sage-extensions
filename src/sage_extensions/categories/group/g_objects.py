r"""Internal group objects and external abstract-group actions.

For a category ``C`` with represented finite products, ``Grp(C)`` is the
category of internal group objects: an object ``G`` of ``C`` with multiplication,
unit, and inverse morphisms satisfying the group diagrams.  Actions of such an
internal group are morphisms ``G x X -> X`` satisfying the action diagrams.

This is distinct from an action of an external abstract group:

For a group ``G`` and a category ``C``, a ``G``-action on an object ``X`` of
``C`` is a functor ``BG -> C`` selecting ``X``; equivalently a group morphism
``G -> Aut_C(X)`` (lean-categories FOUNDATIONS, Definition 34.1).  A morphism
of ``G``-objects is a morphism of ``C`` commuting with the two actions, so
``Mor_G(X, Y)`` is the fixed locus of ``G`` acting on ``Mor_C(X, Y)`` by
conjugation.  The forgetful functor to ``C`` is evaluation at the one object
of ``BG``.

The category of ``G``-sets is ``GObjects(G, Sets())``.  ``Modules(R[G])`` is
equivalent to ``GObjects(G, Modules(R))``, and an ``R[G]``-module is not an
object of it by inheritance: ``Modules(R[G]).restriction_along_group_inclusion()``
sends an ``R[G]``-module to its action ``G -> Aut_R(M)``,
``Modules(R[G]).linearization()`` extends a ``G``-action ``R``-linearly, and
``Modules(R[G]).linearization_equivalence()`` is the adjunction between them.
The generic constructor takes the actual functor ``BG -> C``.  Represented
specializations may retain their concrete underlying object, but expose that
same functor through ``action_functor()``; their private elementwise action
data are only a realization of the categorical action.
"""

from sage.categories.category import Category
from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.classcall_metaclass import typecall
from sage.misc.unknown import Unknown
from sage.structure.dynamic_class import DynamicMetaclass
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    CategoryPacketMethods,
    MorCategoryConstruction,
    _category_mor_parent,
)
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.group.groups import (
    GroupsWithChosenFinitePresentation,
    OwnedFiniteGroups,
    OwnedGroups,
    _owned_group,
)
from sage_extensions.categories.sets.set_categories import EnumeratedSets, FiniteSets, Sets
from sage_extensions.logic import AtomicProposition, Predicate, conjunction, negation
from sage_extensions.owned_category import _object_of, owned_category_join
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.refine import RealizationHook
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level

if "ProperlyDiscontinuous" not in all_axioms:
    all_axioms.add("ProperlyDiscontinuous")


@cached_function(key=lambda cls, group, category: (cls, id(group), id(category)))
def _g_objects_category(cls, group, category):
    r"""Construct the category selected by these exact mathematical parameters."""
    return typecall(cls, group, category)

def _verify_relators(action, group, endomorphisms) -> None:
    r"""Check the represented action law without manufacturing presentation data.

    An action is a left action: ``rho(s_1 s_2) = rho(s_1) rho(s_2)``, the
    product of the matrices acting on an ordered basis.  A function on the
    generators extends to a group morphism exactly when every defining
    relator, composed in that order, is the identity.  When no presentation
    has been selected but the group is finite, the same claim is decided
    directly on all pairs.  Finite presentability alone never triggers a
    presentation search.  It is the body of the action validators
    (``OWN-22``), so a failed law raises ``ValueError``.
    """
    if group in GroupsWithChosenFinitePresentation():
        identity = endomorphisms.identity()
        presentation_projection = group.selected_group_resolution().augmentation()
        for relator in group.defining_relations():
            composite = identity
            for letter in relator.parent().reduced_word(relator):
                composite = composite * action(presentation_projection(letter))
            if (composite == identity) is not True:
                raise ValueError(
                    f"the generator images do not satisfy the relator {relator}, "
                    f"so they define no left action of {group}"
                )
        return
    if group in OwnedFiniteGroups():
        for left in group:
            for right in group:
                if (action(left * right) == action(left) * action(right)) is not True:
                    raise ValueError(
                        f"the given automorphisms do not define a left action of {group}: "
                        f"rho({left} * {right}) differs from rho({left}) rho({right})"
                    )


def _product_projections(construction):
    return tuple(
        construction.structure_morphism(index)
        for index in construction.diagram().domain().objects()
    )


def _factor_selected_product(construction, source, legs):
    legs = tuple(legs)
    diagram = construction.diagram()
    cone = diagram.ProductCones().cone(
        source,
        lambda index: legs[int(index.value())],
    )
    return construction.factor(cone).apex_map()


def _terminal_map(category, source):
    return _factor_selected_product(
        category.product_construction(()),
        source,
        (),
    )


class InternalGroupObjectMorphism(CategoricalMor.ElementMethods):
    r"""Methods for a generated morphism of internal group objects."""

    def __init__(self, parent, arrow) -> None:
        Morphism.__init__(self, parent)
        self._arrow = arrow

    def underlying_arrow(self):
        return self._arrow

    def __mul__(self, other):
        if other.codomain() is not self.domain():
            return NotImplemented
        return self.parent().mor_family().Of(
            other.domain(),
            self.codomain(),
        )(
            self.underlying_arrow() * other.underlying_arrow()
        )

    def _repr_(self):
        return f"Internal-group morphism induced by {self.underlying_arrow()}"


class InternalGroupObjectMor(CategoricalMor):
    r"""Morphisms in the category of internal group objects."""

    ElementMethods = InternalGroupObjectMorphism

    def underlying_mor(self):
        category = self.domain().underlying_category()
        return category.Mor(
            self.domain().underlying_object(),
            self.codomain().underlying_object(),
        )

    def _element_constructor_(self, arrow):
        source = self.domain()
        target = self.codomain()
        arrow = self.underlying_mor()(arrow)

        source_square = source.square_construction()
        target_square = target.square_construction()
        first, second = _product_projections(source_square)
        arrow_times_arrow = _factor_selected_product(
            target_square,
            source_square.object(),
            (arrow * first, arrow * second),
        )
        if (
            arrow * source.multiplication()
            != target.multiplication() * arrow_times_arrow
        ):
            raise ValueError(
                f"{arrow} is not a morphism of group objects from {source} to {target}: "
                f"it does not commute with the multiplications"
            )
        if arrow * source.unit_morphism() != target.unit_morphism():
            raise ValueError(
                f"{arrow} is not a morphism of group objects from {source} to {target}: "
                f"it does not send the unit of {source} to the unit of {target}"
            )
        if (
            arrow * source.inverse_morphism()
            != target.inverse_morphism() * arrow
        ):
            raise ValueError(
                f"{arrow} is not a morphism of group objects from {source} to {target}: "
                f"it does not commute with the inverse maps"
            )
        return self.element_class(self, arrow)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"no identity morphism from {self.domain()} to {self.codomain()}: "
                f"they are different group objects"
            )
        return self(self.underlying_mor().identity())


class InternalGroupObjectMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return InternalGroupObjectMor


class InternalGroupObjects(CategoryPacketMethods, OwnedCategory):
    r"""Internal group objects in a category with represented finite products.

    The data are an object G of C and owned C-morphisms m:GxG->G,
    e:1->G, and i:G->G satisfying the group diagrams.  This is distinct
    from GObjects: an action of an external abstract group is a functor BG->C.
    """

    @staticmethod
    def __classcall__(cls, category):
        return Category.__classcall__(cls, category)

    def __init__(self, category) -> None:
        self._underlying_category = category
        OwnedCategory.__init__(self)

    def underlying_category(self):
        return self._underlying_category

    def super_categories(self):
        return [Objects()]

    def _repr_object_names(self):
        return f"internal group objects in {self.underlying_category()}"

    _MorCategory = InternalGroupObjectMorCategoryConstruction

    def _call_(self, underlying_object, multiplication, unit, inverse):
        return _object_of(
            self,
            _engine=(self, _InternalGroupObjectEngine, None),
            underlying_object=underlying_object,
            multiplication=multiplication,
            unit=unit,
            inverse=inverse,
        )

    def an_object(self):
        category = self.underlying_category()
        terminal = category.product_construction(())
        underlying = terminal.object()
        square = category.product_construction((underlying, underlying))
        multiplication = _terminal_map(category, square.object())
        identity = category.Mor(underlying, underlying).identity()
        return self(underlying, multiplication, identity, identity)


class _InternalGroupObjectEngine:
    def __init__(self, underlying_object, multiplication, unit, inverse, **rest) -> None:
        category = rest["category"].underlying_category()
        if underlying_object not in category:
            raise TypeError(
                f"cannot form a group object in {category} on {underlying_object}: it is "
                f"not an object of {category}"
            )
        self._underlying_object = underlying_object
        self._square_construction = category.product_construction(
            (underlying_object, underlying_object)
        )
        self._terminal_construction = category.product_construction(())
        self._multiplication = category.Mor(
            self._square_construction.object(),
            underlying_object,
        )(multiplication)
        self._unit = category.Mor(
            self._terminal_construction.object(),
            underlying_object,
        )(unit)
        self._inverse = category.Mor(
            underlying_object,
            underlying_object,
        )(inverse)
        super().__init__(**rest)
        self._verify_group_diagrams()

    def underlying_category(self):
        return self.category().underlying_category()

    def underlying_object(self):
        return self._underlying_object

    def square_construction(self):
        return self._square_construction

    def terminal_construction(self):
        return self._terminal_construction

    def multiplication(self):
        return self._multiplication

    def unit_morphism(self):
        return self._unit

    def inverse_morphism(self):
        return self._inverse

    def _verify_group_diagrams(self):
        category = self.underlying_category()
        group = self.underlying_object()
        multiplication = self.multiplication()
        square = self.square_construction()
        triple = category.product_construction((group, group, group))
        first, second, third = _product_projections(triple)

        first_pair = _factor_selected_product(
            square,
            triple.object(),
            (first, second),
        )
        second_pair = _factor_selected_product(
            square,
            triple.object(),
            (second, third),
        )
        first_product = multiplication * first_pair
        second_product = multiplication * second_pair
        multiply_first = multiplication * _factor_selected_product(
            square,
            triple.object(),
            (first_product, third),
        )
        multiply_second = multiplication * _factor_selected_product(
            square,
            triple.object(),
            (first, second_product),
        )
        if multiply_first != multiply_second:
            raise ValueError(
                f"{multiplication} does not make {group} a group object in {category}: "
                f"the multiplication is not associative"
            )

        identity = category.Mor(group, group).identity()
        unit_on_group = self.unit_morphism() * _terminal_map(category, group)
        left_unit = multiplication * _factor_selected_product(
            square,
            group,
            (unit_on_group, identity),
        )
        right_unit = multiplication * _factor_selected_product(
            square,
            group,
            (identity, unit_on_group),
        )
        if left_unit != identity or right_unit != identity:
            raise ValueError(
                f"{self.unit_morphism()} is not a two-sided unit for {multiplication} on "
                f"{group} in {category}"
            )

        inverse = self.inverse_morphism()
        left_inverse = multiplication * _factor_selected_product(
            square,
            group,
            (inverse, identity),
        )
        right_inverse = multiplication * _factor_selected_product(
            square,
            group,
            (identity, inverse),
        )
        if left_inverse != unit_on_group or right_inverse != unit_on_group:
            raise ValueError(
                f"{inverse} is not a two-sided inverse for {multiplication} on {group} "
                f"in {category}"
            )

    def actions(self):
        return InternalGroupActions(self)

    def Mor(self, target):
        return self.category().Mor(self, target)

    def _repr_(self):
        return f"Internal group object on {self.underlying_object()}"


class InternalGroupActionMorphism(CategoricalMor.ElementMethods):
    r"""Methods for a generated equivariant morphism between internal group actions."""

    def __init__(self, parent, arrow) -> None:
        Morphism.__init__(self, parent)
        self._arrow = arrow

    def underlying_arrow(self):
        return self._arrow

    def __mul__(self, other):
        if other.codomain() is not self.domain():
            return NotImplemented
        return self.parent().mor_family().Of(
            other.domain(),
            self.codomain(),
        )(
            self.underlying_arrow() * other.underlying_arrow()
        )


class InternalGroupActionMor(CategoricalMor):
    ElementMethods = InternalGroupActionMorphism

    def underlying_mor(self):
        category = self.domain().group_object().underlying_category()
        return category.Mor(
            self.domain().underlying_object(),
            self.codomain().underlying_object(),
        )

    def _element_constructor_(self, arrow):
        source = self.domain()
        target = self.codomain()
        arrow = self.underlying_mor()(arrow)
        source_product = source.action_product_construction()
        target_product = target.action_product_construction()
        group_leg, point_leg = _product_projections(source_product)
        identity_times_arrow = _factor_selected_product(
            target_product,
            source_product.object(),
            (group_leg, arrow * point_leg),
        )
        if (
            arrow * source.action_morphism()
            != target.action_morphism() * identity_times_arrow
        ):
            raise ValueError(
                f"{arrow} is not equivariant from {source} to {target}: it does not "
                f"commute with the actions of {source.group_object()}"
            )
        return self.element_class(self, arrow)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"no identity morphism from {self.domain()} to {self.codomain()}: "
                f"they are different objects with an action"
            )
        return self(self.underlying_mor().identity())


class InternalGroupActionMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return InternalGroupActionMor


class InternalGroupActions(CategoryPacketMethods, OwnedCategory):
    r"""Actions of one internal group object by morphisms GxX->X."""

    @staticmethod
    def __classcall__(cls, group_object):
        return Category.__classcall__(cls, group_object)

    def __init__(self, group_object) -> None:
        self._group_object = group_object
        OwnedCategory.__init__(self)

    def group_object(self):
        return self._group_object

    def super_categories(self):
        return [Objects()]

    def _repr_object_names(self):
        return f"objects acted on by {self.group_object()}"

    _MorCategory = InternalGroupActionMorCategoryConstruction

    def _call_(self, underlying_object, action_morphism):
        return _object_of(
            self,
            _engine=(self, _InternalGroupActionEngine, None),
            underlying_object=underlying_object,
            action_morphism=action_morphism,
        )

    def an_object(self):
        category = self.group_object().underlying_category()
        terminal = category.product_construction(()).object()
        action_product = category.product_construction(
            (self.group_object().underlying_object(), terminal)
        )
        _group_projection, point_projection = _product_projections(action_product)
        return self(terminal, point_projection)


class _InternalGroupActionEngine:
    def __init__(self, underlying_object, action_morphism, **rest) -> None:
        group = rest["category"].group_object()
        category = group.underlying_category()
        if underlying_object not in category:
            raise TypeError(
                f"{group} cannot act on {underlying_object}: it is not an object of "
                f"{category}"
            )
        self._underlying_object = underlying_object
        self._action_product_construction = category.product_construction(
            (group.underlying_object(), underlying_object)
        )
        self._action_morphism = category.Mor(
            self._action_product_construction.object(),
            underlying_object,
        )(action_morphism)
        super().__init__(**rest)
        self._verify_action_diagrams()

    def group_object(self):
        return self.category().group_object()

    def underlying_object(self):
        return self._underlying_object

    def action_product_construction(self):
        return self._action_product_construction

    def action_morphism(self):
        return self._action_morphism

    def _verify_action_diagrams(self):
        group = self.group_object()
        category = group.underlying_category()
        group_object = group.underlying_object()
        acted = self.underlying_object()
        action = self.action_morphism()
        group_times_acted = self.action_product_construction()
        triple = category.product_construction((group_object, group_object, acted))
        first, second, point = _product_projections(triple)

        multiplied = group.multiplication() * _factor_selected_product(
            group.square_construction(),
            triple.object(),
            (first, second),
        )
        via_multiplication = action * _factor_selected_product(
            group_times_acted,
            triple.object(),
            (multiplied, point),
        )
        inner_action = action * _factor_selected_product(
            group_times_acted,
            triple.object(),
            (second, point),
        )
        via_action = action * _factor_selected_product(
            group_times_acted,
            triple.object(),
            (first, inner_action),
        )
        if via_multiplication != via_action:
            raise ValueError(
                f"{action} is not an action of {group} on {acted}: acting by a product "
                f"differs from acting by the factors in turn"
            )

        identity = category.Mor(acted, acted).identity()
        unit_on_acted = group.unit_morphism() * _terminal_map(category, acted)
        via_unit = action * _factor_selected_product(
            group_times_acted,
            acted,
            (unit_on_acted, identity),
        )
        if via_unit != identity:
            raise ValueError(
                f"{action} is not an action of {group} on {acted}: the unit does not act "
                f"as the identity"
            )

    def Mor(self, target):
        return self.category().Mor(self, target)


def Grp(category):
    r"""Return the category of internal group objects in category."""
    return InternalGroupObjects(category)


class EquivariantMorphismMethods:
    r"""A morphism of ``C`` between two ``G``-objects that commutes with the actions."""

    def __init__(
        self,
        parent,
        arrow,
        *,
        equivariance_decision=None,
        equivariance_premises=None,
    ) -> None:
        arrow = parent.underlying_mor()(arrow)
        self._equivariance_premise = equivariance_decision
        self._equivariance_premises = (
            None if equivariance_premises is None else tuple(equivariance_premises)
        )
        args, options = arrow._transport_initialization_to_mor(parent)
        super().__init__(*args, **options)
        self.validate_equivariance(check=False)

    @cached_method
    def equivariance_decision(self):
        r"""Return whether ``f rho_X(g) = rho_Y(g) f`` for all ``g``, computed on first request.

        A structural construction supplies its law.  A construction from
        equivariant arrows retains those actual arrows: their known laws
        prove the result's law.  An undecided or failed input law supplies
        no such proof, so the parent then decides the result's own equations
        on a determining family of ``G``.  Failed input laws do not imply a
        failed composite law: inverse translations can compose to identity.
        """
        match self._equivariance_premise:
            case None:
                if self._equivariance_premises is not None and all(
                    premise.equivariance_decision() is True
                    for premise in self._equivariance_premises
                ):
                    return True
                return self.parent().is_equivariant(self.underlying_arrow())
            case premise:
                return premise

    @validator
    def validate_equivariance(self) -> None:
        r"""Raise ``ValueError`` unless this arrow is known to be ``G``-equivariant (``OWN-22``)."""
        if self.equivariance_decision() is not True:
            raise ValueError(
                f"{self.underlying_arrow()} is not known to be equivariant from "
                f"{self.domain()} to {self.codomain()}"
            )

    def underlying_arrow(self):
        r"""Return the same morphism read in the underlying category."""
        return self.parent().underlying_mor()(self)

    def natural_transformation(self):
        r"""Return the corresponding natural transformation between action functors.

        Its source and target are the action functors ``BG -> C`` of the
        domain and codomain, and its one component is this arrow read in
        ``C``; :meth:`NaturalTransformation.morphism` gives it as an arrow of
        the functor category.
        """
        from sage_extensions.categories.functors.core import NaturalTransformation

        return NaturalTransformation(
            self.domain().action_functor(),
            self.codomain().action_functor(),
            lambda _obj: self.underlying_arrow(),
        )

    def __mul__(self, other):
        r"""Compose in ``C``, where this arrow is its own underlying arrow.

        The composite is the one the arrow type of ``C`` forms.  When
        ``other`` is equivariant as well, the composite commutes with the
        actions, so it is an arrow of ``Mor_G``; composed with any other arrow
        of ``C`` it stays an arrow of ``C``.
        """
        composite = super().__mul__(other)
        if composite is self or composite is other:
            return composite
        objects = self.parent().mor_family().base_category()
        source = other.domain()
        match other:
            case _ if source in objects and other in objects.Mor(source, self.domain()):
                return objects.Mor(source, self.codomain())._from_equivariant_arrow(
                    composite,
                    equivariance_premises=(self, other),
                )
            case _:
                return composite

    def _repr_(self) -> str:
        return f"Equivariant {super()._repr_()}"


class ExternalInternalActionComparison(SageObject):
    r"""Comparison of an external Set-action with its internal-group action."""

    def __init__(self, external_object, internal_group, internal_action) -> None:
        self._external_object = external_object
        self._internal_group = internal_group
        self._internal_action = internal_action

    def external_object(self):
        return self._external_object

    def internal_group_object(self):
        return self._internal_group

    def internal_action(self):
        return self._internal_action


class GObjectMor(CategoricalMor):
    r"""The represented ``Mor_G(X, Y)``: the equivariant morphisms of ``C``.

    Equivariance is decided on a determining family of the acting group:
    selected generators when present, or every element when the group is
    represented as finite.
    """

    ElementMethods = EquivariantMorphismMethods

    def __init__(self, mor_family, domain, codomain) -> None:
        assert domain.acting_group() is codomain.acting_group(), (
            f"no equivariant morphisms from {domain} to {codomain}: they are acted on by "
            f"different groups, {domain.acting_group()} and {codomain.acting_group()}"
        )
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def underlying_mor(self):
        r"""Return ``Mor_C(U(X), U(Y))``, where equivariant maps live.

        A concrete ``G``-object need not itself be an object of ``C``: an
        ``R[G]``-module, for example, reaches ``Mod_R`` by restriction of
        scalars.  Evaluation of the represented action functor is the common
        forgetful construction for both generic functor-category objects and
        concrete specializations, so use that rather than treating the acted
        wrapper as its own underlying object.
        """
        category = self.mor_family().base_category()
        forget = category.forgetful_functor()
        source = forget(self.domain())
        target = forget(self.codomain())
        return category.underlying_category().Mor(source, target)

    def is_equivariant(self, arrow):
        r"""Decide ``f rho_X(g) = rho_Y(g) f`` on a determining family of ``G``."""
        group = self.domain().acting_group()
        arrow = self.underlying_mor()(arrow)
        match group:
            case _ if (
                group.has_selected_group_resolution()
                and group.group_generating_set().cardinality().is_finite() is True
            ):
                determining = group.group_generators()
            case _ if group.is_finite() is True:
                try:
                    determining = iter(group)
                except (TypeError, NotImplementedError):
                    return AtomicProposition("is_equivariant", self, arrow)
            case _:
                return AtomicProposition("is_equivariant", self, arrow)
        return conjunction(
            arrow * self.domain().action_of(element)
            == self.codomain().action_of(element) * arrow
            for element in determining
        )

    def _from_equivariant_arrow(self, arrow, *, equivariance_premises=()):
        r"""Construct a structural or premise-derived equivariant arrow.

        The empty family is reserved for a construction, such as identity,
        whose formula proves equivariance.  Composition supplies its actual
        input arrows.  Their laws prove equivariance only when each is known;
        otherwise the resulting arrow keeps its own equation diagnostic.
        Arbitrary supplied arrows use the ordinary constructor instead.
        """
        return self.element_class(
            self,
            arrow,
            equivariance_premises=tuple(equivariance_premises),
        )

    def _element_constructor_(self, datum):
        arrow = self.underlying_mor()(datum)
        return self.element_class(self, arrow)

    @object_level
    @cached_method
    def identity(self):
        r"""Return the retained identity of this exact equivariant Mor."""
        assert self.domain() is self.codomain(), (
            f"no identity morphism from {self.domain()} to {self.codomain()}: they are "
            f"different objects"
        )
        return self._from_equivariant_arrow(self.underlying_mor().identity())

    def _repr_(self) -> str:
        return f"Mor_{self.domain().acting_group()}({self.domain()}, {self.codomain()})"


class GObjectMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return GObjectMor


class _GSpaceOnSpace:
    r"""A ``G``-space on a given space ``X``, with the procedure deciding its orbit relation.

    The data are ``X`` and the relation, a function of two points answering
    ``True``, ``False`` or ``Unknown``; the action is the ``GObjects`` datum.
    """

    def __init__(self, space, orbit_relation, **rest) -> None:
        self._space = space
        self._orbit_relation = orbit_relation
        super().__init__(**rest)

    def space(self):
        r"""The space ``X`` acted on, retained as defining data."""
        return self._space

    def __contains__(self, point) -> bool:
        return point in self.space()

    is_parent_of = __contains__

    def __call__(self, point):
        return self._element_constructor_(point)

    def _element_constructor_(self, point):
        return self.space()(point)

    def __iter__(self):
        return iter(self.space())

    def cardinality(self):
        return self.space().cardinality()

    @cached_method
    def ranking_map(self):
        r"""The enumeration of ``X``, whose points are the points of this ``G``-space."""
        ranking = self.space().ranking_map()
        return self._ranking_isomorphism(
            lambda point: int(ranking(point)),
            lambda position: ranking.inverse()(position),
        )

    def _orbit_relation_decision(self, source, target):
        return self._orbit_relation(source, target)

    def _repr_(self) -> str:
        return f"{self.space()} with {self.acting_group()}-action"


class GObjects(CategoryPacketMethods, OwnedCategory):
    r"""The category of objects of ``C`` with a chosen ``G``-action.

    A represented two-point `C_2`-set retains its set cardinality, and the
    forgetful functor supplies the exact underlying arrow endpoints::

        sage: from dzack_research.preamble.all import Sets, Groups
        sage: G, X = Groups.C(2), Sets.Δ[1]
        sage: C = GObjects(G, Sets())
        sage: A = C.on_set(X, lambda g, x: X((int(x) + int(g)) % 2))
        sage: A in C and A in Sets()
        True
        sage: C.forgetful_functor()(A).cardinality() == 2
        True
        sage: C._mor_endpoints_in_supercategory(Sets(), A, A)[0] is C.forgetful_functor()(A)
        True
    """

    @staticmethod
    def __classcall__(cls, group, category):
        if isinstance(cls, DynamicMetaclass):
            cls = cls.__base__
        return _g_objects_category(cls, _owned_group(group), category)

    def __init__(self, group, category) -> None:
        self._group = group
        self._category = category
        OwnedCategory.__init__(self)

    def acting_group(self):
        return self._group

    def underlying_category(self):
        r"""Return ``C``, the codomain of the forgetful functor."""
        return self._category

    def super_categories(self):
        return [self.underlying_category()]

    def _mor_endpoints_in_supercategory(self, supercategory, domain, codomain):
        if supercategory is self.underlying_category():
            forget = self.forgetful_functor()
            return forget(domain), forget(codomain)
        return super()._mor_endpoints_in_supercategory(
            supercategory,
            domain,
            codomain,
        )

    def _repr_object_names(self):
        return f"{self.acting_group()}-objects in {self.underlying_category()._repr_object_names()}"

    _MorCategory = GObjectMorCategoryConstruction

    def functor_category(self):
        r"""Return the represented functor category ``[BG,C]``."""
        return Cat().functor_mor(
            self.acting_group().classifying_category(),
            self.underlying_category(),
        )

    def __contains__(self, candidate) -> bool:
        if candidate in self.functor_category():
            return True
        return super().__contains__(candidate)

    def _call_(self, action_functor):
        r"""Construct a ``G``-object from an actual functor ``BG -> C``."""
        return self.functor_category()(action_functor)

    def on_set(self, points, action, *, orbit_relation=None):
        r"""Present a set action through its retained functor ``BG -> Sets``.

        An optional orbit decision realizes the quotient relation. Its
        absence leaves that relation as a proposition, not a negative answer.
        """
        from sage_extensions.categories.group.g_sets import _g_set_on_points

        if self.underlying_category() is not Sets():
            raise ValueError("on_set requires an action in the category of sets")
        group = self.acting_group()
        return _g_set_on_points(
            group, points, action,
            (lambda left, right: Unknown) if orbit_relation is None else orbit_relation,
            lambda point: group.predicate_subgroup(
                lambda element: action(element, point) == point,
                f"stabilizer of {point}",
            ),
        )

    def on_space(self, space, action, *, orbit_relation=None):
        r"""The ``G``-space ``(X, rho)``: ``G`` acting on the space ``X`` by ``action(g, x)``.

        ``rho: G -> Aut_C(X)`` sends ``g`` to the homeomorphism
        ``x |-> action(g, x)``; it is a left action, checked by
        ``validate_action``.  The ``G``-space has the points and the
        topology of ``X``, which is retained as defining data.  An optional
        orbit decision ``orbit_relation(x, y)`` realizes ``y in G . x``; its
        absence leaves that relation a proposition.
        """
        return self._g_space_in(self, space, action, orbit_relation)

    def _g_space_in(self, placement, space, action, orbit_relation):
        r"""The ``G``-space ``(X, rho)`` of :meth:`on_space`, an object of ``placement``.

        ``placement`` is this category or an axiom subcategory of it that the
        caller's construction states, such as :meth:`ProperlyDiscontinuous`.
        """
        from sage_extensions.categories.topological_spaces import TopologicalSpaces

        category = self.underlying_category()
        assert category.is_subcategory(TopologicalSpaces()), (
            f"on_space needs an action in a category of topological spaces, but the "
            f"actions of {self} are in {category}"
        )
        assert space in category, f"{space} is not an object of {category}"
        match space:
            case _ if space in FiniteSets() and space in EnumeratedSets():
                g_spaces = owned_category_join((placement, FiniteSets(), EnumeratedSets()))
            case _:
                g_spaces = placement
        # The G-space is X itself with the action added: its points, topology
        # and every lower structure of X are X's own defining data, and only the
        # acting group and the action are new.
        return space._with_structure(
            (g_spaces,),
            {
                "space": space,
                "orbit_relation": (lambda left, right: Unknown) if orbit_relation is None else orbit_relation,
                "acting_group": self.acting_group(),
                "action": lambda group_element: (lambda point: action(group_element, point)),
                "underlying_category": category,
                "facade": space,
            },
            engine=_GSpaceOnSpace,
        )

    def orbit_generated_submodule(self, action, seed, *, containing=None):
        r"""Construct the least submodule containing the seed and stable under this action."""
        from sage_extensions.categories.modules.orbit_spans import OrbitSpanConstructions
        from sage_extensions.categories.modules.pure.modules import Modules

        ring = seed.domain().base_ring()
        if self.underlying_category() is not Modules(ring) or action.group() is not self.acting_group():
            raise ValueError("the orbit span requires an action in this module category")
        return OrbitSpanConstructions(ring)(action, seed, containing=containing)

    def Mor(self, source, target):
        r"""Equivariant morphisms, as natural transformations on generic actions."""
        functors = self.functor_category()
        if source in functors and target in functors:
            return functors.Mor(source, target)
        return self.MorCategory().Of(source, target)

    def forgetful_functor(self):
        r"""Evaluation at the unique object, ``GObjects(G,C) -> C``."""
        from sage_extensions.categories.functors.group_actions import (
            ForgetGroupActionFunctor,
        )

        return ForgetGroupActionFunctor(self.acting_group(), self.underlying_category())

    def internal_action_comparison(self, acted_object):
        r"""Compare an external action with an internal action when the constant group exists.

        The represented comparison is currently supplied for Set, where an
        abstract group is itself an internal group object on its underlying set.
        Finite products alone do not construct a constant group object in an
        arbitrary category, so no conversion is inferred outside this regime.
        """
        if self.underlying_category() is not Sets():
            raise TypeError(
                f"cannot compare {acted_object} with an action of a group object in "
                f"{self.underlying_category()}: {self.acting_group()} is realized as a "
                f"group object only in the category of sets"
            )
        if acted_object not in self:
            raise TypeError(
                f"{acted_object} is not an object of {self}: it has no action of "
                f"{self.acting_group()}"
            )

        group = self.acting_group()
        product = Sets().product((group, group))
        multiplication = Sets().Mor(product, group)(
            lambda pair: pair[0] * pair[1]
        )
        terminal = Sets().product(())
        unit = Sets().Mor(terminal, group)(lambda _point: group.one())
        inverse = Sets().Mor(group, group)(lambda element: ~element)
        internal_group = Grp(Sets())(
            group,
            multiplication,
            unit,
            inverse,
        )

        underlying = self.forgetful_functor()(acted_object)
        action_product = Sets().product((group, underlying))
        functor = (
            acted_object
            if acted_object in self.functor_category()
            else acted_object.action_functor()
        )
        classifying = functor.domain()
        point = classifying.an_object()
        arrows = classifying.Mor(point, point)
        action = Sets().Mor(action_product, underlying)(
            lambda pair: functor(arrows(pair[0]))(pair[1])
        )
        internal_action = internal_group.actions()(underlying, action)
        return ExternalInternalActionComparison(
            acted_object,
            internal_group,
            internal_action,
        )

    def transport(self, functor):
        r"""Postcompose actions by ``functor: C -> D``."""
        from sage_extensions.categories.functors.group_actions import (
            TransportGroupActionFunctor,
        )

        assert functor.domain() == self.underlying_category(), (
            f"cannot transport {self.acting_group()}-actions along {functor}: its domain "
            f"is {functor.domain()}, not {self.underlying_category()}"
        )
        return TransportGroupActionFunctor(self.acting_group(), functor)

    def restriction(self, group_morphism):
        r"""Return ``phi^*: GObjects(G, C) -> GObjects(H, C)`` for ``phi: H -> G``.

        Restriction along a group morphism is the reindexing functor
        ``BH -> BG -> C``; it is defined for every ``phi``, not only for the
        inclusion of a subgroup.
        """
        from sage_extensions.categories.functors.group_actions import (
            RestrictionOfGroupActionFunctor,
        )

        assert group_morphism.codomain() is self.acting_group(), f"{group_morphism} does not land in {self.acting_group()}, so it restricts no action of that group"
        return RestrictionOfGroupActionFunctor(group_morphism, self.underlying_category())

    def _scheme_action_functor(self, acted):
        r"""Read the retained BG -> Sch_R datum of an admitted scheme action.

        The category API also accepts the existing functor-category object;
        that object remains a functor, while evaluation supplies its exact
        underlying scheme. No scheme placement is added to the functor.
        """
        from sage_extensions.categories.functors.group_actions import (
            _action_functor_of,
        )
        from sage_extensions.categories.schemes.schemes import Schemes

        category = self.underlying_category()
        match category:
            case Schemes():
                pass
            case _:
                raise TypeError(
                    f"global sections and affine scheme quotients require a scheme action, "
                    f"but {self} consists of actions in {category}"
                )
        if acted not in self:
            raise TypeError(f"{acted} is not an action in {self}")
        return _action_functor_of(acted, self.acting_group(), category)

    @cached_method(key=lambda self, acted: id(acted))
    def _affine_invariant_action(self, acted):
        r"""Select the existing affine invariant computation on the same action.

        A generic functor presentation is evaluated before the affine
        constructor is used as its computation supplier. That supplier
        retains the literal coordinate algebra and the supplied pullbacks;
        public maps continue to use the original action's exact carrier.
        """
        from sage_extensions.categories.schemes.schemes import (
            AffineGSchemes,
            Schemes,
        )

        action = self._scheme_action_functor(acted)
        base = self.underlying_category().base_ring()
        affine_actions = AffineGSchemes(self.acting_group(), base)
        carrier = action(action.domain().an_object())
        match acted:
            case _ if acted in affine_actions:
                return acted
            case _ if carrier in Schemes(base).Affine():
                point = action.domain().an_object()
                arrows = action.domain().Mor(point, point)
                return affine_actions(
                    carrier,
                    lambda group_element: action(arrows(group_element)),
                )
            case _:
                raise AssertionError(
                    f"the invariant algebra Gamma({carrier}, O)^{{{self.acting_group()}}} "
                    "and its universal quotient to affine targets are defined, but no "
                    "selected computation of global sections and their invariants for "
                    "this nonaffine scheme is available"
                )

    def global_sections_functor(self):
        r"""Return Gamma(-, O): GSch_R^op -> Modules(R[G]).

        The left section action is g.s = rho(g^-1)^*(s). Affine schemes
        supply their coordinate algebra; other schemes reach the named
        global-section computation frontier of the same functor.
        """
        from sage_extensions.categories.schemes.quotients import (
            _AffineSectionModuleFunctor,
        )
        from sage_extensions.categories.schemes.schemes import Schemes

        category = self.underlying_category()
        match category:
            case Schemes():
                return _AffineSectionModuleFunctor(
                    self.acting_group(), category.base_ring(), source_category=self
                )
            case _:
                raise TypeError(f"global sections require scheme actions, not {self}")

    def invariant_algebra(self, acted):
        r"""Return Gamma(U(acted), O)^G in the selected represented regime.

        This algebra is defined for every scheme action. The finite linear
        affine algorithm is a supplier, not a restriction of the definition.
        """
        return self._affine_invariant_action(acted)._invariant_algebra_data()[0]

    def invariant_algebra_inclusion(self, acted):
        r"""Return the exact inclusion Gamma(U(acted), O)^G -> Gamma(U(acted), O)."""
        return self._affine_invariant_action(acted)._invariant_algebra_data()[1]

    def invariant_algebra_element(self, acted, element):
        r"""Lift an invariant global section through the retained inclusion."""
        return self._affine_invariant_action(acted)._invariant_algebra_element(element)

    @cached_method(key=lambda self, acted: id(acted))
    def affine_quotient(self, acted):
        r"""Return Spec(Gamma(U(acted), O)^G), universal for affine targets.

        This does not assert a quotient universal among all schemes.
        """
        algebra = self.invariant_algebra(acted)
        return algebra.affine_spectrum(base_ring=self.underlying_category().base_ring())

    @cached_method(key=lambda self, acted: id(acted))
    def quotient_morphism(self, acted):
        r"""Return the invariant map from the exact carrier to its affine quotient."""
        from sage_extensions.categories.schemes.schemes import (
            _affine_morphism_from_pullback,
        )

        action = self._scheme_action_functor(acted)
        carrier = action(action.domain().an_object())
        return _affine_morphism_from_pullback(
            carrier,
            self.affine_quotient(acted),
            self.invariant_algebra_inclusion(acted),
        )

    def factor_through_affine_quotient(self, acted, morphism):
        r"""Factor an invariant map U(acted) -> Y uniquely, for affine Y."""
        from sage_extensions.categories.schemes.schemes import (
            Schemes,
            _affine_morphism_from_pullback,
        )

        action = self._scheme_action_functor(acted)
        carrier = action(action.domain().an_object())
        base = self.underlying_category().base_ring()
        if morphism.domain() is not carrier:
            raise ValueError(
                f"a factor through the affine quotient of {acted} needs a map out of "
                f"its exact carrier {carrier}, not {morphism.domain()}"
            )
        target = morphism.codomain()
        if target not in Schemes(base).Affine():
            raise TypeError(f"the affine quotient factors maps to affine {base}-schemes, not {target}")
        if morphism not in Schemes(base).Mor(carrier, target):
            raise TypeError(f"{morphism} is not a morphism over the retained base {base}")
        supplier = self._affine_invariant_action(acted)
        supplied_morphism = (
            morphism
            if supplier is carrier
            else _affine_morphism_from_pullback(
                supplier, target, morphism.coordinate_algebra_morphism()
            )
        )
        return supplier._factor_through_affine_quotient(supplied_morphism)

    def descend_invariant_family(self, acted, family_morphism):
        r"""Descend an invariant map to an affine parameter scheme."""
        return self.factor_through_affine_quotient(acted, family_morphism)

    def quotient_base_change_comparison(self, acted, ring_map):
        r"""Return the canonical comparison for scalar change of the affine quotient."""
        from sage_extensions.categories.schemes.quotients import (
            AffineInvariantQuotientBaseChangeComparison,
        )

        self._scheme_action_functor(acted)
        return AffineInvariantQuotientBaseChangeComparison(
            acted, ring_map, _action_category=self
        )

    def affine_quotient_functor(self):
        r"""Return ``(-)/G: GObjects(G, Sch_R) -> AffSch_R``.

        This is the universal quotient to affine targets, defined from
        invariant global sections. The selected affine invariant algorithm
        supplies the computation; equivariance determines the arrow action.
        """
        from sage_extensions.categories.schemes.quotients import (
            AffineQuotientFunctor,
        )
        from sage_extensions.categories.schemes.schemes import (
            Schemes,
        )

        category = self.underlying_category()
        match category:
            case Schemes():
                return AffineQuotientFunctor(self.acting_group(), category.base_ring())
            case other:
                assert False, f"no affine quotient functor on {self}: quotients by {self.acting_group()} are constructed for schemes, and the underlying category is {other}"

    def an_object(self):
        r"""The trivial action on an object of the underlying category."""
        from sage_extensions.categories.group.g_sets import FiniteGSets
        from sage_extensions.categories.modules.pure.modules import Modules
        from sage_extensions.categories.schemes.schemes import AffineGSchemes, Schemes

        category = self.underlying_category()
        sample = category.an_object()
        match category:
            case _ if category is Sets():
                return FiniteGSets(self.acting_group()).trivial(sample)
            case Schemes():
                return AffineGSchemes(self.acting_group(), category.base_ring()).an_object()
        assert category.is_subcategory(Modules(category.base_ring())), f"cannot build a sample object of {self}: trivial actions of {self.acting_group()} are constructed on sets, schemes and modules, and {category} is none of these"
        ring = category.base_ring()
        group = self.acting_group()
        trivial = Modules(ring).trivial_action(group)(sample)
        return Modules(ring[group]).restriction_along_group_inclusion()(trivial)

    class SubcategoryMethods:
        def ProperlyDiscontinuous(self):
            r"""The axiom: the action of the discrete group ``G`` on ``X`` is properly discontinuous.

            For every compact ``K`` in ``X`` the set
            ``{g in G : gK meets K}`` is finite (Thurston, *The Geometry and
            Topology of Three-Manifolds*, Ch. 13).  A group ``Gamma`` that is
            discrete in a Lie group ``G`` acts properly discontinuously on
            ``G/K`` for ``K`` compact: ``Sp_{2g}(ZZ)`` on
            ``H_g = Sp_{2g}(RR)/U(g)`` and ``O(L)`` on ``HH^n``.  The
            property is stated by the construction of the action, never
            computed.
            """
            return self._with_axiom("ProperlyDiscontinuous")

    class ProperlyDiscontinuous(CategoryWithAxiom):
        r"""``G``-spaces on which ``G`` acts properly discontinuously.

        The orbit space ``G\X`` of such an action on a manifold is an
        orbifold, whose chart at the orbit of ``p`` has the finite
        stabilizer ``G_p`` as its group (Thurston, Ch. 13).
        """

        def on_space(self, space, action, *, orbit_relation=None):
            r"""The ``G``-space ``(X, rho)`` of ``GObjects.on_space``, stated properly discontinuous."""
            return self.base_category()._g_space_in(self, space, action, orbit_relation)

    class ParentMethods:
        def __init__(self, acting_group, action, underlying_category, **rest) -> None:
            self._acting_group = acting_group
            self._action_datum = action
            self._underlying_category = underlying_category
            super().__init__(**rest)

        def acting_group(self):
            return self._acting_group

        def underlying_category(self):
            r"""Return the category in which this object is acted on."""
            return self._underlying_category

        def Mor(self, codomain, category=None):
            r"""Return the equivariant Mor, or an explicitly requested weaker Mor.

            Equivariance is part of being a ``G``-object, independently of
            whether the underlying object is a set, module, scheme, or other
            represented object.  With no explicit category, morphisms are
            therefore the arrows of ``GObjects(G,C)``.  An explicit weaker
            category forgets the actions first and asks that category for the
            Mor of the underlying endpoints.
            """
            acted = GObjects(self.acting_group(), self.underlying_category())
            # ``acted`` is the category whose constructor builds a G-object,
            # so it is the ambient category of ``ARC-07``; a G-object of a
            # category that is not one of sets (schemes) is not reached by
            # the root of ``Sets``, so the rule is stated here.
            if category is None or category.is_subcategory(acted):
                return acted.Mor(self, codomain)
            forget = acted.forgetful_functor()
            return _category_mor_parent(category, forget(self), forget(codomain))

        def invariant_algebra(self):
            r"""Return the invariant global-section algebra of this scheme action."""
            return GObjects(self.acting_group(), self.underlying_category()).invariant_algebra(self)

        def invariant_algebra_inclusion(self):
            r"""Return the retained inclusion of invariant global sections."""
            return GObjects(self.acting_group(), self.underlying_category()).invariant_algebra_inclusion(self)

        def invariant_algebra_element(self, element):
            r"""Lift an invariant section through the retained inclusion."""
            return GObjects(self.acting_group(), self.underlying_category()).invariant_algebra_element(self, element)

        def affine_quotient(self):
            r"""Return the universal quotient of this action to affine targets."""
            return GObjects(self.acting_group(), self.underlying_category()).affine_quotient(self)

        def quotient_morphism(self):
            r"""Return the map from this action's carrier to its affine quotient."""
            return GObjects(self.acting_group(), self.underlying_category()).quotient_morphism(self)

        def factor_through_affine_quotient(self, morphism):
            r"""Factor an invariant map to an affine scheme."""
            return GObjects(self.acting_group(), self.underlying_category()).factor_through_affine_quotient(self, morphism)

        def descend_invariant_family(self, family_morphism):
            r"""Descend an invariant affine-parameter family."""
            return GObjects(self.acting_group(), self.underlying_category()).descend_invariant_family(self, family_morphism)

        def quotient_base_change_comparison(self, ring_map):
            r"""Return the canonical scalar-change comparison of affine quotients."""
            return GObjects(self.acting_group(), self.underlying_category()).quotient_base_change_comparison(self, ring_map)

        @cached_method
        def action_functor(self):
            r"""Return this represented action as the actual functor ``BG -> C``."""
            from sage_extensions.categories.functors.group_actions import (
                GroupActionFunctor,
            )

            endomorphisms = self.underlying_category().Mor(self, self)
            datum = self._action_datum
            return GroupActionFunctor(
                self.acting_group(),
                self.underlying_category(),
                self,
                lambda group_element: endomorphisms(datum(group_element)),
            )

        @validator
        def validate_action(self) -> None:
            r"""Raise ``ValueError`` unless the chosen action is a left action of ``G`` (``OWN-22``).

            The action images must satisfy the group's chosen relators, or,
            on a finite group without chosen relators, the law
            ``rho(s_1 s_2) = rho(s_1) rho(s_2)`` on all pairs.
            """
            endomorphisms = self.underlying_category().Mor(self, self)
            _verify_relators(self.action(), self.acting_group(), endomorphisms)

        @cached_method
        def action(self):
            r"""Return the chosen action as the set morphism ``G -> Mor_C(X, X)``.

            Its values are automorphisms of ``X`` in ``C``, and the action is
            a left action: ``rho(s_1 s_2) = rho(s_1) rho(s_2)``.  The law is
            the validator :meth:`validate_action`.
            """
            endomorphisms = self.underlying_category().Mor(self, self)
            functor = self.action_functor()
            classifying = functor.domain()
            point = classifying.an_object()
            arrows = classifying.Mor(point, point)
            return Sets().Mor(self.acting_group(), endomorphisms)(lambda group_element: functor(arrows(group_element)))

        def action_of(self, group_element):
            r"""Return the automorphism of ``X`` in ``C`` induced by ``group_element``."""
            assert group_element in self.acting_group(), f"{group_element} is not an element of {self.acting_group()}"
            return self.action()(group_element)

        def fixed_locus(self, group_element):
            r"""Equalizer of the selected action and identity in the underlying category."""
            pass

        def fixed_locus_inclusion(self, group_element):
            pass

        def act(self, group_element, element):
            r"""Return ``group_element . element``."""
            assert element in self, f"{element} is not an element of {self}"
            return self.action_of(group_element)(element)

        @RealizationHook
        def _orbit_relation_decision(self, source, target):
            r"""Protected decision of ``target in G . source`` for two points of this object.

            ``in_same_orbit`` is the only caller.  A realization or a more
            specific category whose construction supplies a procedure
            answers ``True`` or ``False``; ``Unknown`` here means that no
            procedure decides the relation.
            """
            return Unknown

        def in_same_orbit(self, source, target) -> bool | Predicate:
            r"""Whether some ``g`` in ``G`` carries ``source`` to ``target``.

            This is the orbit relation: ``x ~ y`` exactly when
            ``y in G . x``.  Its classes are the points of ``X/G``.  It is
            an exact predicate (``DEF-06``): ``True`` or ``False`` where the
            procedure this object's construction supplies decides it, and
            otherwise the proposition ``in_same_orbit(X, x, y)``, whose
            ``ask`` is ``Unknown``.
            """
            assert source in self, f"{source} is not a point of {self}"
            assert target in self, f"{target} is not a point of {self}"
            decision = self._orbit_relation_decision(source, target)
            if decision is Unknown and self.acting_group() in OwnedFiniteGroups():
                return negation(conjunction(
                    negation(self.act(element, source) == target)
                    for element in self.acting_group()
                ))
            match decision:
                case _ if decision is Unknown:
                    return AtomicProposition("in_same_orbit", self, source, target)
                case _:
                    return decision

        @cached_method
        def orbits(self):
            r"""The orbit set ``X/G``, whose points are the orbits ``G . x``.

            ``X/G`` is the coequalizer in ``Sets()`` of the action and the
            projection ``G x X -> X`` (``CON-09``).  Its projection
            ``X -> X/G`` sends a point to its orbit, and two orbits are
            equal exactly when they meet.
            """
            from sage_extensions.categories.group.g_sets import _orbit_set

            category = self.underlying_category()
            match category:
                case _ if category is Sets():
                    return _orbit_set(self)
                case _:
                    assert False, (
                        f"the orbit object of {self} under {self.acting_group()} is a colimit "
                        f"in {category}, and the preamble constructs it only for G-sets"
                    )

        def orbit_space(self):
            r"""The orbit space ``G\X``, the coequalizer in ``TopologicalSpaces()``.

            ``X`` is a topological space and ``G`` acts by homeomorphisms;
            the action ``a: G x X -> X`` and the projection
            ``pr_2: G x X -> X`` are the parallel pair, and ``G\X`` is the
            universal pair ``(G\X, q)`` with ``q a = q pr_2``.  Its underlying
            set is the orbit set ``orbits()`` and its topology is the final
            topology of ``q: X -> G\X``.  For a discrete group ``Gamma``
            acting properly discontinuously on a manifold, which the
            construction of the action states by the axiom
            ``ProperlyDiscontinuous``, ``Gamma\X`` is in general an orbifold,
            not a manifold (Thurston, *The Geometry and Topology of
            Three-Manifolds*, Ch. 13).  It is placed in ``ComplexOrbifolds()``
            for an action on a complex manifold, by biholomorphisms, which
            makes it a normal complex analytic space (H. Cartan, "Quotient
            d'un espace analytique par un groupe d'automorphismes", 1957); in
            ``RiemannianOrbifolds()`` for an action by isometries of a
            Riemannian manifold; in ``Orbifolds()`` for a smooth manifold;
            and in ``TopologicalSpaces()`` otherwise.  The arithmetic
            quotients ``Gamma\HH``, ``Gamma\H_g`` and ``Gamma\HH^n`` are this
            construction on ``GObjects(Gamma, C)`` for ``C`` the category of
            the symmetric space; so is ``G/K`` for the right action of ``K``
            on ``G``, written as the left action ``k . g = g k^{-1}``.
            """
            from sage_extensions.categories.topological_spaces import (
                TopologicalSpaces,
            )

            category = self.underlying_category()
            assert category.is_subcategory(TopologicalSpaces()), (
                f"cannot form the orbit space of {self} under {self.acting_group()}: the "
                f"orbit space is a coequalizer in topological spaces, and {category} is "
                f"not a category of topological spaces"
            )
            return self._orbit_space_construction()[0]

        def orbit_space_projection(self):
            r"""The projection ``q: X -> G\X``, sending a point to its orbit.

            ``q`` is continuous for the final topology, and ``q rho(g) = q``
            for every ``g`` in ``G``.
            """
            return self._orbit_space_construction()[1]

        @cached_method
        def _orbit_space_construction(self):
            r"""The pair ``(G\X, q)``.

            ``G\X`` is the colimit of the action functor ``BG -> Top``.  The
            forgetful functor ``U: Top -> Set`` creates it: its points are the
            orbit set of the ``G``-set ``UX``, the colimit of ``BG -> Set``, and
            its topology is the final topology along ``q`` (Mathlib,
            ``TopCat.colimit_isOpen_iff``: ``V`` is open exactly when
            ``q^{-1}(V)`` is open).  Top has no product ``G x X`` of a group
            with a space, so the parallel pair ``a, pr_2`` is not formed; the
            colimit over ``BG`` is the same universal pair.
            """
            from sage_extensions.categories.topological_spaces import (
                TopologicalSpaces,
                _final_topology_space,
                _OrbitSpaceEngine,
            )

            from sage_extensions.categories.group.g_sets import FiniteGSets

            group = self.acting_group()
            match self:
                case _ if self in FiniteSets():
                    # A finite G-set decides its orbit relation from its
                    # permutation representation G -> Sym(UX).
                    g_set = FiniteGSets(group)(self, self.act)
                    category = TopologicalSpaces()
                case _:
                    g_set = GObjects(group, Sets()).on_set(
                        self, self.act, orbit_relation=self._orbit_relation_decision
                    )
                    category = self._orbit_space_category()
            orbits = g_set.orbits()
            space, projection, _ = _final_topology_space(
                self,
                Sets().Mor(self, orbits)(orbits.orbit_of),
                category=category,
                engine=_OrbitSpaceEngine,
                g_space=self,
            )
            return space, projection

        def _orbit_space_category(self):
            r"""The category the construction of the action places ``G\X`` in; see :meth:`orbit_space`."""
            from sage_extensions.categories.manifolds import (
                ComplexManifolds,
                RiemannianManifolds,
                SmoothManifolds,
            )
            from sage_extensions.categories.orbifolds import (
                ComplexOrbifolds,
                Orbifolds,
                RiemannianOrbifolds,
            )
            from sage_extensions.categories.topological_spaces import (
                TopologicalSpaces,
            )

            category = self.underlying_category()
            match category:
                case _ if self not in GObjects(self.acting_group(), category).ProperlyDiscontinuous():
                    return TopologicalSpaces()
                case _ if category.is_subcategory(ComplexManifolds()):
                    return ComplexOrbifolds()
                case _ if category.is_subcategory(RiemannianManifolds()):
                    return RiemannianOrbifolds()
                case _ if category.is_subcategory(SmoothManifolds()):
                    return Orbifolds()
                case _:
                    return TopologicalSpaces()

        def orbits_presented_by(self, covering):
            r"""The orbit set ``X/G`` presented by a finite set of points meeting every orbit.

            ``covering`` is a finite set of points meeting every orbit, stated
            by the caller's construction.  The result is the coequalizer of the
            action and the projection, with its projection ``X -> X/G`` and a
            section ``X/G -> X`` with image in ``covering``; the orbits are the
            distinct orbits of its points, so this object's orbit relation must
            be decided (``in_same_orbit``).
            """
            from sage_extensions.categories.group.g_sets import _orbit_set_presented_by

            assert self.underlying_category() is Sets(), (
                f"the orbit object of {self} under {self.acting_group()} is a colimit in "
                f"{self.underlying_category()}, and the preamble constructs it only for G-sets"
            )
            return _orbit_set_presented_by(self, covering)

        def restrict_action(self, group_morphism, *, orbit_relation=None):
            r"""Return this object acted on by ``H`` through ``phi: H -> G``.

            Without ``orbit_relation`` this is the image under the restriction
            functor :meth:`GObjects.restriction`.  ``orbit_relation``, when
            supplied, is the procedure deciding the orbit relation of the
            restricted ``H``-set (``y ~_H x``): it is data of that object, so
            the restricted ``H``-set is constructed on the same points with
            the action through ``phi`` and that decision.  The functor stays
            independent of any one object.
            """
            category = GObjects(self.acting_group(), self.underlying_category())
            if orbit_relation is None:
                return category.restriction(group_morphism)(self)
            from sage_extensions.categories.sets.set_categories import Sets

            assert self.underlying_category() is Sets(), (
                f"an orbit-relation decision is data of an H-set; {self} is an object of "
                f"{self.underlying_category()}"
            )
            return GObjects(group_morphism.domain(), Sets()).on_set(
                self,
                lambda group_element, point: self.act(group_morphism(group_element), point),
                orbit_relation=orbit_relation,
            )

        def orbit_representatives(self, points):
            r"""Retain selected representatives together with their orbit projection."""
            from sage_extensions.categories.group.g_sets import OrbitRepresentativeSets

            return OrbitRepresentativeSets(self.acting_group())(self, points)

        @RealizationHook
        def _named_stabilizer(self, point):
            r"""Protected value hook: the stabilizer of ``point`` as the subgroup the action names.

            ``stabilizer`` is the only caller.  A realization whose
            construction names the stabilizer (the centralizer for the
            conjugation action on elements, the normalizer for the
            conjugation action on subgroups) supplies it; ``None`` here
            states that the construction names none.
            """
            return None

        @RealizationHook
        def _stabilizer_generating_morphism(self, point):
            r"""Protected value hook: the stabilizer's free generating morphism, when the action supplies one.

            ``stabilizer`` is the only caller; it passes the value to the
            stabilizer constructor as that subgroup's selected generating
            datum.  The value maps the constructed stabilizer to a group
            morphism from a free group onto it.  A finite action of a group
            with selected generators supplies it by Schreier's lemma on the
            orbit; ``None`` here states that this action supplies none.
            """
            return None

        def stabilizer(self, point):
            r"""The subgroup ``G_point = {g in G : g.point = point}``.

            Where the construction of this object names the stabilizer, it
            is that subgroup, which carries the operations of its own
            category (an open subgroup of a profinite group knows its
            index).  Otherwise it is the predicate subgroup of the acting
            group cut out by the action; membership is exact from the
            represented action and does not require choosing group
            generators for the stabilizer.
            """
            if point not in self:
                raise ValueError(f"{point} is not a point of {self}")
            named = self._named_stabilizer(point)
            if named is not None:
                return named
            from sage_extensions.categories.group.predicate_subgroups import (
                StabilizerSubgroups,
            )

            group = self.acting_group()
            return StabilizerSubgroups(group)(
                point,
                self.action_functor(),
                lambda group_element: self.act(group_element, point) == point,
                description=f"stabilizer of {point} in {self}",
                generating_morphism=self._stabilizer_generating_morphism(point),
            )

        def _cyclic_restriction(self, group_element):
            r"""Return this object acted on by the cyclic subgroup ``<g> <= G``."""

            from sage_extensions.categories.schemes.schemes import Schemes

            match self.underlying_category():
                case Schemes():
                    return self.restrict_action(
                        group_element.cyclic_subgroup().inclusion()
                    )
                case other:
                    assert False, (
                        f"cannot form the fixed locus of {group_element} on {self}: it is "
                        f"constructed only for schemes, and {self} lies in {other}"
                    )

        def fixed_subobject_of(self, group_element):
            r"""Return ``X^g``, the equalizer of ``rho(g)`` and the identity of ``X``.

            A point fixed by ``g`` is fixed by every power of ``g``, so
            ``X^g = X^{<g>}``: the equalizer of one automorphism with the
            identity is the common fixed locus of the cyclic subgroup that
            automorphism generates, and that common fixed locus is what the
            specialization constructs.
            """
            from sage_extensions.categories.schemes.schemes import AffineGSchemes
            from sage_extensions.categories.sets.set_categories import Sets

            underlying = self.underlying_category()
            if underlying.is_subcategory(Sets()):
                return self.point_set().filtered(
                    lambda point: self.act(group_element, point) == point,
                    name=f"fixed points of {group_element} on {self}",
                )
            if self in AffineGSchemes(self.acting_group(), self.base_ring()):
                return self._cyclic_restriction(group_element).fixed_subscheme()
            raise NotImplementedError(
                f"the equalizer of {group_element} on {self} must be constructed in {underlying}"
            )

        def action_is_free(self):
            r"""Decide whether the identity is the only element with a fixed point.

            This is strictly stronger than ``X^G`` being empty.  ``X^G`` is the
            intersection of the ``X^g``, so one element acting without fixed
            points already empties it while other elements keep theirs; the
            quotient is then still not a torsor over its image, and the
            hypotheses of free quotients do not apply.  Freeness asks the
            question of every nonidentity element separately.

            ``X^g`` is empty exactly when its ideal is the unit ideal.  For an
            acting group not decided finite the answer is the proposition
            ``action_is_free(X)``: the question is one condition per element
            and no owned criterion replaces it.
            """
            group = self.acting_group()
            if group.is_finite() is not True:
                return AtomicProposition("action_is_free", self)
            from sage_extensions.categories.schemes.schemes import Schemes
            underlying = self.underlying_category()
            identity = group.one()
            for group_element in group:
                if group_element == identity:
                    continue
                if underlying.is_subcategory(Sets()):
                    if not self.fixed_subobject_of(group_element).is_empty():
                        return False
                    continue
                if not underlying.is_subcategory(Schemes(self.base_ring())):
                    return AtomicProposition("action_is_free", self)
                restricted = self._cyclic_restriction(group_element)
                unit = restricted.coordinate_algebra().one()
                if not restricted.fixed_ideal().contains_ambient_element(unit):
                    return False
            return True

        def is_invariant(self, element):
            r"""Decide ``g . element = element`` on a determining family of the acting group."""
            group = self.acting_group()
            match group:
                case _ if group.has_selected_finite_group_generating_set():
                    determining = group.group_generators()
                case _ if group.is_finite() is True:
                    determining = group
                case _:
                    return AtomicProposition("is_invariant", self, element)
            return conjunction(self.act(group_element, element) == element for group_element in determining)


__all__ = [
    "ExternalInternalActionComparison",
    "GObjectMor",
    "GObjects",
    "Grp",
    "InternalGroupActionMorphism",
    "InternalGroupActions",
    "InternalGroupObjectMorphism",
    "InternalGroupObjects",
]
