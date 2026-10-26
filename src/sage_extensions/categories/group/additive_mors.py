r"""Additive Mor groups and their composition endomorphism rings.

The enrichment is pointwise addition.  An elementwise map is supplied with
additivity as a hypothesis; construction does not decide arbitrary function
identities.  This is the additive specialization of the existing owned Mor
packet, using Sage's ``Mor``, ``Morphism`` and integer multiplication action.
"""

from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.coerce_actions import IntegerMulAction
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategories,
    _compose_operation_preserving_mor,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.group.magmas import AdditiveGroups
from sage_extensions.categories.sets.set_categories import (
    OwnedSetMorphism,
    SetMorCategory,
)
from sage_extensions.logic import AtomicProposition, conjunction, negation
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedRings,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class AdditiveMagmaMorphism:
    r"""A map preserving the selected additive binary operation."""

    def __init__(self, parent, function) -> None:
        if not callable(function):
            raise TypeError(
                f"cannot build a morphism in {parent} from {function}: an additive morphism needs a map on elements"
            )
        self._function = function
        super().__init__(parent, function)

    def _composition(self, right):
        return _compose_operation_preserving_mor(self, right, super()._composition)


def _additive_operation_mor_element(parent, datum):
    if isinstance(datum, Map):
        if datum.domain() is not parent.domain() or datum.codomain() is not parent.codomain():
            raise ValueError(
                f"{datum} is a morphism {datum.domain()} -> {datum.codomain()}, not a morphism "
                f"{parent.domain()} -> {parent.codomain()}"
            )
        if parent._already_parented_arrow(datum):
            return datum
        raise TypeError(f"{datum} is an arrow of another Mor; give its defining additive map")
    if not callable(datum):
        raise TypeError(
            f"an additive morphism {parent.domain()} -> {parent.codomain()} needs a map on elements, "
            f"but got {datum!r}"
        )
    return parent.element_class(parent, datum)


class AdditiveMagmaMor(CategoricalMor):
    ElementMethods = AdditiveMagmaMorphism

    def _element_constructor_(self, datum):
        return _additive_operation_mor_element(self, datum)

    # The identity function preserves addition. Reuse the declared cached
    # descriptor: its constructor uses this Mor's actual element_class.
    identity = SetMorCategory.__dict__["identity"]


class AdditiveMonoidMorphism:
    r"""An additive-monoid morphism; the lower additive map is inherited."""

    def __init__(self, parent, function) -> None:
        super().__init__(parent, function)

    def _factor_through_inclusion(self, target):
        r"""Supply the additive factor between two retained additive inclusions.

        The existing set inclusion owns injectivity, image and finite-set
        factorization. A chosen additive generating family additionally
        supplies containment by the target's addition-closure premise.
        The resulting arrow retains that actual subset inclusion, so its
        range need not re-decide the target's defining predicate.
        """
        from sage_extensions.categories.group.magmas import AdditiveMonoids
        from sage_extensions.categories.group.submonoids import (
            _AdditiveSubmonoidEngine, _submonoid_generator_containment,
        )
        from sage_extensions.categories.sets.set_categories import SetInjection

        if not isinstance(target, AdditiveMonoidMorphism):
            return None
        donor = self._owned_function
        target_donor = target._owned_function
        if not (
            isinstance(donor, SetInjection) and donor._subset_premise
            and isinstance(target_donor, SetInjection) and target_donor._subset_premise
        ):
            return None
        source = self.domain()
        if (
            isinstance(source, _AdditiveSubmonoidEngine)
            and source._selected_representation_kind() == "generators"
        ):
            contained = _submonoid_generator_containment(
                self, target, source.additive_monoid_generators()
            )
            if contained is False:
                return False
            assert contained is True, (
                f"cannot factor {self} through {target}: containment of the chosen additive "
                "generators remains undecided"
            )
            return AdditiveMonoids().Mor(source, target.domain())._from_submonoid_inclusion()
        factor = donor.factor_through_or_none(target_donor)
        if factor is None:
            return False
        return AdditiveMonoids().Mor(source, target.domain())(factor)


class AdditiveMonoidMor(CategoricalMor):
    ElementMethods = AdditiveMonoidMorphism

    def _element_constructor_(self, datum):
        return _additive_operation_mor_element(self, datum)

    @cached_method
    def _from_submonoid_inclusion(self):
        r"""Retain the set inclusion of an additive submonoid as its actual additive arrow.

        Protected construction contract under OWN-05. Additive-submonoid
        construction and its generator-proved containment factor are the
        callers. The exact source is a subset of the exact target, with
        zero and addition inherited there. The existing set-injection datum
        supplies injectivity and the literal image, without evaluating points.
        """
        from sage_extensions.categories.sets.set_categories import Sets

        donor = Sets().Mono(self.domain(), self.codomain())._from_subset_inclusion()
        return self.element_class(self, donor)

    # The identity function preserves both addition and zero. Bind the same
    # cached descriptor to this Mor and its generated additive-monoid arrow.
    identity = SetMorCategory.__dict__["identity"]


class _ScalarIdentityEvaluation:
    r"""Native evaluation of the scalar endomorphism r.id, from its actual r.

    This callable is the defining computation, not an annotation on another
    map. The parent supplies its already constructed pointwise scalar action.
    Within that same retained parent, arithmetic of two such maps is
    arithmetic of the supplied scalars, even when arbitrary endomorphism
    equality cannot be decided.
    """

    def __init__(self, parent, scalar):
        assert parent.domain() is parent.codomain(), (
            f"cannot form the scalar multiple {scalar}·id in {parent}: a multiple of the "
            f"identity is an endomorphism, but {parent.domain()} and {parent.codomain()} "
            f"are different groups"
        )
        self._parent = parent
        self.scalar = parent.base_ring()(scalar)

    def __call__(self, element):
        return self._parent._apply_pointwise_scalar(self.scalar, element)


def _scalar_identity_coefficient(morphism, parent):
    r"""Read a coefficient for the scalar action of this exact diagonal Mor.

    Private shared additive/linear/group map adapter. Its callers are native map
    arithmetic and endomorphism centrality, and supply their actual result or
    comparison parent. A retained scalar evaluation belongs to that parent's
    selected action; even equal coefficient rings do not identify two actions.
    A scalar map for a stronger module theory therefore need not be a scalar
    map in the weaker additive End ring. Foreign action data return ``None``
    so the caller uses its ordinary formula or computation frontier.

    The retained subgroup-inclusion datum with identical endpoints is the
    identity in its owning group Mor, so also supplies the scalar one there.
    Neither case infers a scalar by sampling a map or transporting scalars.
    """
    from sage_extensions.categories.group.groups import GroupMorphism
    from sage_extensions.categories.modules.module_morphisms.module_morphisms import ModuleMorphismMethods

    if (
        parent.domain() is not parent.codomain()
        or morphism.domain() is not parent.domain()
        or morphism.codomain() is not parent.codomain()
    ):
        return None
    match morphism:
        case ModuleMorphismMethods():
            # Its cooperative additive initializer retains the bound _call_
            # wrapper; the actual selected evaluator is _element_function.
            evaluation = morphism._element_function
        case AdditiveMorphism():
            evaluation = morphism._function
        case GroupMorphism() if morphism._subgroup_premise and morphism.parent() is parent:
            return parent.base_ring().one()
        case OwnedSetMorphism():
            evaluation = morphism._owned_function
        case _:
            return None
    if isinstance(evaluation, _ScalarIdentityEvaluation) and evaluation._parent is parent:
        return evaluation.scalar
    return None


class AdditiveMorGroups(OwnedCategory):
    r"""Mor groups with the pointwise abelian law of their target.

    This includes additive and linear maps, and group homomorphisms
    ``G -> A`` with abelian target ``A`` written multiplicatively. The
    source need not be abelian; commutativity of the target makes the
    pointwise product of two homomorphisms another homomorphism.
    """

    def an_object(self):
        r"""The additive endomorphism group of the rank-one integer module."""
        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )
        from sage.rings.integer_ring import ZZ as SageZZ

        module = _owned_integers().regular_module()
        return module.Mor(module)

    def super_categories(self):
        return [AdditiveGroups().AdditiveCommutative()]

    class ParentMethods:
        def base_ring(self):
            r"""The scalar ring retained by this Mor's selected enrichment."""
            return self._preamble_base_ring

        def _is_additive(self):
            r"""The notation of the actual target abelian law.

            This is the shared value-operation supplier for pointwise Mor
            arithmetic. It selects a declared mathematical law, without
            deciding equality of target values or inspecting an engine.
            """
            if self.codomain() in AdditiveGroups().AdditiveCommutative():
                return True
            from sage_extensions.categories.group.groups import OwnedGroups

            if self.codomain() not in OwnedGroups().Commutative():
                raise TypeError(f"pointwise abelian arithmetic needs an abelian target, but got {self.codomain()}")
            return False

        def _sum_values(self, left, right):
            return left + right if self._is_additive() else left * right

        def _negative_value(self, value):
            return -value if self._is_additive() else value**-1

        def _identity_value(self):
            return self.codomain().zero() if self._is_additive() else self.codomain().one()

        def zero(self):
            if self.domain() is self.codomain():
                return self._scalar_identity(self.base_ring().zero())
            return self.elementwise(lambda element: self._identity_value())

        def _pointwise_scalar_multiple(self, scalar, morphism):
            r"""Apply the retained scalar action to the values of this arrow.

            The additive, linear and multiplicative-group Mor realizations
            supply ``_apply_pointwise_scalar`` on their actual target.
            This shared formula is called by their scalar-action adapters;
            it does not select a new target action or coerce a weaker map
            into this Mor.
            """
            if morphism not in self:
                raise TypeError(f"pointwise scalar multiplication in {self} needs an arrow already admitted there")
            scalar = self.base_ring()(scalar)
            coefficient = _scalar_identity_coefficient(morphism, self)
            if coefficient is not None:
                return self._scalar_identity(scalar * coefficient)
            return self.elementwise(
                lambda element: self._apply_pointwise_scalar(scalar, morphism(element))
            )

    class ElementMethods:
        def _add_(self, other):
            r"""Pointwise sum of arrows admitted in the same additive Mor.

            The constructor can accept a function supplied as additive data;
            arithmetic instead needs an already declared additive arrow.
            In particular a set map with these endpoints is not enough.
            """
            parent = self._pointwise_mor()
            if other not in parent:
                return NotImplemented
            left, right = _scalar_identity_coefficient(self, parent), _scalar_identity_coefficient(other, parent)
            if left is not None and right is not None:
                return parent._scalar_identity(left + right)
            return parent.elementwise(lambda element: parent._sum_values(self(element), other(element)))

        def __neg__(self):
            parent = self._pointwise_mor()
            scalar = _scalar_identity_coefficient(self, parent)
            if scalar is not None:
                return parent._scalar_identity(-scalar)
            return parent.elementwise(lambda element: parent._negative_value(self(element)))

        def __sub__(self, other):
            if other not in self._pointwise_mor():
                return NotImplemented
            return self + (-other)

        def _composition(self, right):
            r"""``self ∘ right`` in the additive Mor family.

            The root arrow host has checked that ``right`` is a map into
            this morphism's domain; a map outside the additive Mor theory
            composes as a map of sets.  This is a category arrow method, so
            Sage copies it into the generated arrow type and ``super()`` does
            not reach the root host; the set-level composite is named.
            """
            right_mor = right.parent()
            match right_mor:
                case _ if right_mor in MorCategories() and right_mor.mor_category().is_subcategory(
                    self.parent().mor_category()
                ):
                    pass
                case _:
                    return OwnedSetMorphism._composition(self, right)
            if right.parent() is self.parent() and self.domain() is self.codomain():
                return self.parent()._compose_endomorphisms(self, right)
            mor = self.parent().mor_family().Of(right.domain(), self.codomain())
            return mor.elementwise(lambda element: self(right(element)))

        def __rmul__(self, scalar):
            if isinstance(scalar, (Morphism, CategoricalArrow)):
                return scalar.__mul__(self)
            return self._pointwise_mor()._owned_scalar_multiple(scalar, self)


class AdditiveEndomorphismRings(OwnedCategoryOverBaseRing):
    r"""Endomorphism algebras over their selected commutative scalar ring."""

    def parameter_category(self):
        r"""The coefficient datum is a commutative unital ring."""
        return OwnedRings().Commutative()

    def an_object(self):
        r"""The endomorphism ring of the regular rank-one module."""
        assert self.base_ring() in OwnedRings().Commutative(), (
            f"{self} is defined over a commutative ring, but {self.base_ring()} is not known to be commutative"
        )
        module = self.base_ring().regular_module()
        return module.Mor(module)

    def super_categories(self):
        from sage_extensions.categories.algebras.algebras import Algebras

        assert self.base_ring() in OwnedRings().Commutative(), (
            f"endomorphisms of abelian groups form an algebra over {self.base_ring()} only "
            f"when that ring is commutative, but {self.base_ring()} is only known to be in "
            f"{self.base_ring().category()}"
        )
        return [AdditiveMorGroups(), Algebras(self.base_ring()).Associative().Unital()]

    class ParentMethods:
        @abstract_method
        def _compose_endomorphisms(self, left, right):
            r"""The selected composition of two admitted endomorphisms.

            The arrow multiplication and the algebra's bilinear classifier
            call this contract. Additive and group realizations use the
            pointwise computation below; linear and cochain realizations
            retain the premises carried by their own map constructors.
            """

        def _pointwise_endomorphism_composite(self, left, right):
            r"""Realize composition through an admitted elementwise map.

            Only the additive and group Mor suppliers call this shared
            computation. Their maps retain their laws as admitted data;
            module and component realizations keep their richer premises
            through their selected composition supplier instead.
            """
            left_scalar, right_scalar = _scalar_identity_coefficient(left, self), _scalar_identity_coefficient(right, self)
            if left_scalar is not None and right_scalar is not None:
                return self._scalar_identity(left_scalar * right_scalar)
            return self.elementwise(lambda element: left(right(element)))

        @abstract_method
        def _owned_scalar_multiple(self, scalar, morphism):
            r"""Apply the retained scalar action, preserving the map's premises.

            The scalar-action realization and inherited additive arithmetic
            call this contract. The actual Mor supplies its additive,
            linear, group or component constructor; no stronger arrow law
            is inferred from equal endpoints.
            """


class AdditiveMorphism:
    r"""An additive map with a supplied elementwise realization."""

    def __init__(self, parent, function) -> None:
        self._function = function
        super().__init__(parent, function)

    def _pointwise_mor(self):
        r"""The actual Mor holding this arrow's additive arithmetic.

        Protected result-placement contract for AdditiveMorphism and
        AdditiveMorGroups.ElementMethods: sums, negatives, differences and
        scalar actions use it; composition retains its own Mor theory.
        A parent carrying an additive-group law already supplies closure
        and keeps its selected enrichment. Otherwise only the underlying
        additive-map laws are available, so use the canonical additive Mor
        with the same literal endpoints. In particular a ring or rng Mor
        does not acquire a pointwise additive-group law.

        ModuleMorphismMethods already refines this contract to the linear
        Mor, since sums and negatives of linear maps remain linear even
        when their originally selected restricted Mor is not additive.
        """
        parent = self.parent()
        match parent:
            case _ if parent in AdditiveGroups():
                return parent
            case _:
                return AdditiveGroups().AdditiveCommutative().MorCategory().Of(
                    self.domain(), self.codomain()
                )

    def __add__(self, other):
        return AdditiveMorGroups.ElementMethods._add_(self, other)

    def _add_(self, other):
        return AdditiveMorGroups.ElementMethods._add_(self, other)

    def _neg_(self):
        return AdditiveMorGroups.ElementMethods.__neg__(self)

    def __neg__(self):
        return AdditiveMorGroups.ElementMethods.__neg__(self)

    def __sub__(self, other):
        return AdditiveMorGroups.ElementMethods.__sub__(self, other)

    def __rmul__(self, scalar):
        return AdditiveMorGroups.ElementMethods.__rmul__(self, scalar)

    def _lmul_(self, scalar):
        return AdditiveMorGroups.ElementMethods.__rmul__(self, scalar)

    def _rmul_(self, scalar):
        return AdditiveMorGroups.ElementMethods.__rmul__(self, scalar)

    def _acted_upon_(self, actor, self_on_left):
        r"""Scalar action of the Mor's scalar ring; any other actor is not an action here."""
        parent = self._pointwise_mor()
        scalars = parent.base_ring()
        if actor not in scalars:
            return None
        return parent._owned_scalar_multiple(scalars(actor), self)

    def _composition(self, right):
        if right.codomain() is not self.domain():
            return NotImplemented
        return AdditiveMorGroups.ElementMethods._composition(self, right)

    def _richcmp_(self, other, op):
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if self is other:
            return op == op_EQ
        from sage_extensions.categories.sets.set_categories import EnumeratedSets

        if other not in self.parent():
            return op == op_NE
        left, right = _scalar_identity_coefficient(self, self.parent()), _scalar_identity_coefficient(other, self.parent())
        if left is not None and right is not None and (left == right) is True:
            return op == op_EQ
        domain = self.domain()
        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        if domain is _owned_integers():
            # A homomorphism from (ZZ,+) is determined by the image of 1.
            # The target equality may still be an undecided proposition.
            equal = self(domain.one()) == other(domain.one())
        elif domain.is_finite() is not True or domain not in EnumeratedSets():
            equal = AtomicProposition("equal", self, other)
        else:
            equal = conjunction(self(element) == other(element) for element in domain)
        return equal if op == op_EQ else negation(equal)


class AdditiveMor(CategoricalMor):
    r"""The Sage Mor parent realizing the additive Mor enrichment."""

    ElementMethods = AdditiveMorphism

    def __init__(self, family, domain, codomain) -> None:
        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        # The integer scalar ring is the datum ``Modules.ParentMethods`` reads
        # through ``_preamble_base_ring``; that category method precedes this
        # class in the refined MRO, and the Sage Homset base stays unset.
        self._preamble_base_ring = _owned_integers()
        self._integer_action = IntegerMulAction(SageZZ, codomain, m=codomain.zero())
        category = AdditiveEndomorphismRings(self._preamble_base_ring) if domain is codomain else AdditiveMorGroups()
        super().__init__(family, domain, codomain, category=category)

    def base_ring(self):
        r"""The integer scalar ring of this additive Mor group."""
        return self._preamble_base_ring

    @object_level
    @cached_method
    def identity(self):
        r"""The canonical identity in this additive Mor's diagonal."""
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity map {self.domain()} -> {self.codomain()}: "
                "the domain and codomain are different additive groups"
            )
        return self._scalar_identity(self.base_ring().one())

    def _element_constructor_(self, datum):
        if isinstance(datum, Map):
            assert datum.domain() is self.domain() and datum.codomain() is self.codomain(), (
                f"{datum} is a morphism {datum.domain()} -> {datum.codomain()}, not a "
                f"morphism {self.domain()} -> {self.codomain()}"
            )
            raise TypeError(
                f"{datum} is not already represented as an additive morphism "
                f"{self.domain()} -> {self.codomain()}; constructing an additive morphism from "
                "a weaker arrow would assert additivity without supplying it"
            )
        if callable(datum):
            return self.elementwise(datum)
        assert self.domain() is self.codomain(), (
            f"cannot read the scalar {datum} as a morphism {self.domain()} -> "
            f"{self.codomain()}: a scalar is a multiple of the identity, which exists only "
            f"when the domain and codomain are the same group"
        )
        return self._owned_scalar_multiple(self._preamble_base_ring(datum), self.identity())

    def elementwise(self, function):
        r"""Construct the additive map declared by ``function``."""
        if isinstance(function, Map):
            return self(function)
        assert callable(function), (
            f"cannot build a morphism {self.domain()} -> {self.codomain()} from {function}: "
            f"an additive morphism is given by a map on elements, and {function} is not a map"
        )
        return self.element_class(self, function)

    def _apply_pointwise_scalar(self, scalar, element):
        return self._integer_action(int(self._preamble_base_ring(scalar)), element)

    def _scalar_identity(self, scalar):
        return self.elementwise(_ScalarIdentityEvaluation(self, scalar))

    def _compose_endomorphisms(self, left, right):
        return self._pointwise_endomorphism_composite(left, right)

    def _owned_scalar_multiple(self, scalar, morphism):
        r"""Realize the canonical integer action through Sage's additive action."""
        return self._pointwise_scalar_multiple(scalar, morphism)
