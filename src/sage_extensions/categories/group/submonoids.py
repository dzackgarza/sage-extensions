"""Submonoids represented as monomorphism subobjects of an ambient monoid."""

from sage.categories.category import Category
from sage.misc.cachefunc import cached_method

from sage_extensions.categories.group.magmas import AdditiveMagmas, AdditiveMonoids, Monoids
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import (
    FiniteSets, NN, Sets, _ConditionSetEngine, _aleph0, cardinal,
)
from sage_extensions.logic import AtomicProposition, Predicate, conjunction
from sage_extensions.owned_category import _object_of, owned_category_join


def _submonoid_generator_containment(inclusion, target_inclusion, generators):
    r"""Decide containment on the exact chosen monoid generating family.

    Protected construction contract under OWN-05. Multiplicative and
    additive submonoid-inclusion suppliers call this with the corresponding
    finite generating family and a target submonoid in the same law. Closure
    proves containment from these generator images; an unknown answer is
    retained and never interpreted as a missing factor.
    """
    target_image = target_inclusion.image()
    return conjunction(
        target_image.is_parent_of(inclusion(generator)) for generator in generators
    )


class _AdditiveSubmonoidEngine(_ConditionSetEngine):
    r"""An additive submonoid with its retained subset and zero/closure premises.

    The condition-set realization owns facade ingress and undecided
    membership. This specialization supplies zero, the additive inclusion,
    and the selected finite-generator algorithm on the literal natural
    numbers. It inherits no multiplicative operation or unit.
    """

    def __init__(
        self, ambient, *, zero, generators=None, predicate=None, description=None, **rest
    ) -> None:
        self._additive_zero = zero
        self._additive_generators = generators
        self._description = description
        self._positive_member = None
        self._zero_generated = generators is not None and all(
            generator is zero or (generator == zero) is True for generator in generators
        )
        self._generator_weights = None
        if generators is not None:
            if ambient is NN:
                self._generator_weights = tuple(int(generator) for generator in generators if int(generator) > 0)
            predicate = self._generated_membership
        else:
            zero_membership = predicate(zero)
            if zero_membership is False:
                raise ValueError(
                    f"the predicate {description or predicate} does not define an additive submonoid "
                    f"of {ambient}: zero does not satisfy it"
                )
            if zero_membership is not True and not isinstance(zero_membership, Predicate):
                raise TypeError("an additive-submonoid predicate must return a Boolean or an owned proposition")
        super().__init__(universe=ambient, predicate=predicate, **rest)
        self._retain_admitted_member(zero)
        if generators is not None:
            for generator in generators:
                self._retain_admitted_member(generator)

    def ambient_additive_monoid(self):
        return self.universe()

    def zero(self):
        return self._additive_zero

    @cached_method
    def inclusion(self):
        return AdditiveMonoids().Mor(self, self.universe())._from_submonoid_inclusion()

    def additive_monoid_generators(self):
        r"""Return the exact finite indexed family chosen by this presentation."""
        assert self._additive_generators is not None, (
            f"{self} is defined by a predicate and has no selected additive generating family"
        )
        return self._additive_generators

    def _selected_representation_kind(self):
        return "predicate" if self._additive_generators is None else "generators"

    def defining_predicate(self):
        assert self._additive_generators is None, (
            f"{self} was defined by additive generators, not by a selected predicate"
        )
        return self.predicate()

    def _generated_membership(self, element):
        if self._generator_weights is not None:
            from sage.combinat.integer_vector_weighted import WeightedIntegerVectors

            # This fixed-weight, fixed-total family is finite. Zero and
            # repeated generators remain in the defining indexed family.
            return next(iter(WeightedIntegerVectors(int(element), self._generator_weights)), None) is not None
        if self._zero_generated:
            return element == self.zero()
        return AtomicProposition("is_parent_of", self, element)

    def _retain_admitted_member(self, element):
        point = super()._retain_admitted_member(element)
        if self.universe() is NN and self._positive_member is None and int(point) > 0:
            self._positive_member = point
        return point

    def _cardinality_decision(self):
        if self._zero_generated:
            return cardinal(1)
        if self.universe() is NN and self._positive_member is not None:
            # For the retained k>0, n |-> n*k embeds NN in this submonoid;
            # its ambient inclusion gives the countable upper bound.
            return _aleph0()
        return super()._cardinality_decision()

    def __iter__(self):
        if self._zero_generated:
            yield self.zero()
            return
        yield from super().__iter__()

    def _repr_(self):
        if self._description is not None:
            return self._description
        return f"Additive submonoid of {self.universe()}"


def _additive_submonoid(ambient, *, generators=None, predicate=None, description=None):
    r"""Construct the additive subset declared by the AdditiveMonoids owner.

    Protected constructor under OWN-05. The public generated constructor
    supplies a finite indexed family; the predicate constructor supplies its
    zero and addition-closure laws under OWN-22. Ambient commutativity and
    subset finiteness restrict to this object without selecting an enumeration.
    """
    from sage_extensions.categories.abstract_categories.arrow_categories import SubobjectCategory
    from sage_extensions.categories.sets.indexed_families import (
        IndexedFamily, finite_indexed_family_from_values,
    )

    if ambient not in AdditiveMonoids():
        raise TypeError(f"an additive submonoid needs an additive ambient monoid, but got {ambient}")
    if (generators is None) == (predicate is None):
        raise ValueError("give either a finite additive generating family or a defining predicate")
    if predicate is not None and not callable(predicate):
        raise TypeError("an additive-submonoid predicate must be a function on the ambient monoid")
    zero = ambient.zero()
    if generators is not None:
        labels = generators.index_set() if isinstance(generators, IndexedFamily) else None
        supplied = finite_indexed_family_from_values(labels, generators)
        values = tuple(ambient(generator) for generator in supplied)
        generators = finite_indexed_family_from_values(supplied.index_set(), values)
    # The categories of the submonoid as an additive monoid; the subobject
    # placement is added separately, so the ambient category below is
    # selected by name rather than by position.
    property_placements = []
    if ambient in AdditiveMagmas().AdditiveCommutative():
        property_placements.append(AdditiveMonoids().AdditiveCommutative())
    if Sets().is_provably_finite(ambient) or (
        generators is not None
        and all(generator is zero or (generator == zero) is True for generator in generators)
    ):
        property_placements.append(FiniteSets())
    category = owned_category_join(
        (SubobjectCategory(AdditiveMonoids(), ambient), *property_placements)
    )
    # A submonoid is a monoid with an inclusion as additional data: the
    # category of its objects is the additive monoids (ARC-07).
    return _object_of(
        category,
        _ambient=owned_category_join((AdditiveMonoids(), *property_placements)),
        _engine=(category, _AdditiveSubmonoidEngine, None),
        ambient=ambient,
        zero=zero,
        generators=generators,
        predicate=predicate,
        description=description,
    )


class _SubmonoidEngine:
    r"""A source monoid with its chosen inclusion into an ambient monoid.

    For a predicate presentation, the caller supplies the identity and
    multiplication-closure premises stated by ``Monoids.predicate_submonoid``.
    This realization retains that predicate; it does not require a decision
    algorithm for membership or for those laws.
    """

    def __init__(
        self,
        ambient,
        *,
        generators=None,
        predicate=None,
        description=None,
        structure_data=None,
        **rest,
    ) -> None:
        if ambient not in Monoids():
            raise TypeError(
                f"cannot form a submonoid of {ambient}: it is not a monoid, "
                f"only known to be in {ambient.category()}"
            )
        if generators is None and predicate is None:
            raise ValueError(
                f"cannot form a submonoid of {ambient}: give monoid generators "
                f"or a membership predicate"
            )
        self._ambient_monoid = ambient
        self._defining_predicate = predicate
        self._description = description
        self._submonoid_structure_data = dict(structure_data or {})
        self._monoid_generators = (
            None if generators is None else finite_ordered_set(tuple(generators))
        )
        super().__init__(facade=ambient, **rest)
        if predicate is not None:
            identity_membership = predicate(ambient.one())
            if not isinstance(identity_membership, Predicate) and not bool(identity_membership):
                raise ValueError(
                    f"the predicate {description or predicate} does not define a submonoid of "
                    f"{ambient}: the identity {ambient.one()} does not satisfy it"
                )

    def ambient_monoid(self):
        return self._ambient_monoid

    supermonoid = ambient_monoid

    @cached_method
    def inclusion(self):
        return Monoids().Mor(self, self.ambient_monoid())._from_submonoid_inclusion()

    def _structure_data(self):
        r"""Return private constructor metadata for localization adapters."""
        return dict(self._submonoid_structure_data)

    def _selected_representation_kind(self):
        r"""Return the representation selected when this submonoid was built.

        Protected construction contract for localization adapters.  A
        predicate-presented submonoid has exact membership by that predicate;
        otherwise the constructor retained a chosen finite generating family.
        Consumers use this datum instead of attempting one representation and
        selecting another when it raises.
        """
        if self._defining_predicate is not None:
            return "predicate"
        return "generators"

    def defining_predicate(self):
        assert self._defining_predicate is not None, (
            f"the submonoid {self} was defined by monoid generators, not by a membership "
            f"predicate, so it has no defining predicate"
        )
        return self._defining_predicate

    def monoid_generators(self):
        assert self._monoid_generators is not None, (
            f"the submonoid {self} was defined by a membership predicate, not by monoid "
            f"generators, so it has no chosen generating set"
        )
        return self._monoid_generators


    def one(self):
        return self.ambient_monoid().one()

    def _normalize(self, datum):
        ambient = self.ambient_monoid()
        membership = ambient.is_parent_of(datum)
        if membership is False:
            raise ValueError(
                f"{datum} cannot be an element of the submonoid {self}: it is not an element "
                f"of the monoid {ambient}"
            )
        assert membership is True, (
            f"cannot admit {datum} into the submonoid {self}: membership in its "
            f"ambient monoid {ambient} is undecided"
        )
        return ambient(datum)

    def __contains__(self, datum) -> bool | Predicate:
        r"""Return the membership proposition without forcing its truth value."""
        ambient = self.ambient_monoid()
        match ambient.is_parent_of(datum):
            case False:
                return False
            case True:
                element = ambient(datum)
            case _:
                return AtomicProposition("is_parent_of", self, datum)
        if self._defining_predicate is not None:
            membership = self._defining_predicate(element)
            return membership if isinstance(membership, Predicate) else bool(membership)
        if element == self.one():
            return True
        generators = tuple(self._monoid_generators)
        # For a selected integer multiplication monoid and one generator,
        # Sage's integer factorization decides the full power equation
        # x = g^n (n >= 0), rather than merely recognizing the generator.
        from sage.rings.integer_ring import ZZ as SageZZ
        from sage_extensions.categories.rings.ring_foundation import OwnedRings

        if len(generators) == 1 and ambient in OwnedRings() and ambient._selected_engine_ring() is SageZZ:
            g = SageZZ(int(generators[0]))
            x = SageZZ(int(element))
            if g == 0:
                return x == 0
            if abs(g) == 1:
                return x == g
            if x == 0:
                return False
            factor_g = dict(abs(g).factor())
            factor_x = dict(abs(x).factor())
            if set(factor_g) != set(factor_x):
                return False
            exponents = {factor_x[p] // e for p, e in factor_g.items()}
            if len(exponents) != 1:
                return False
            exponent = exponents.pop()
            return all(factor_x[p] == exponent * e for p, e in factor_g.items()) and (x < 0) == (g < 0 and exponent % 2 == 1)
        is_selected_generator = any(element == generator for generator in generators)
        assert is_selected_generator, (
            f"cannot decide whether {element} lies in the submonoid {self} of {ambient}: "
            f"it is neither the identity nor a monoid generator, and no algorithm for "
            f"membership in a finitely generated submonoid is available"
        )
        return True

    is_parent_of = __contains__

    def _element_constructor_(self, datum):
        element = self._normalize(datum)
        answer = self.is_parent_of(element)
        if answer is False:
            raise ValueError(f"{element} is not in {self}")
        assert answer is True, (
            f"cannot admit {element} into {self}: its membership is undecided"
        )
        return element

    def _repr_(self):
        if self._description is not None:
            return self._description
        return f"Submonoid of {self.ambient_monoid()}"


def _generated_submonoid(ambient, generators, *, description=None, structure_data=None):
    normalized = tuple(ambient(generator) for generator in generators)
    category = Monoids().Subobjects(ambient)
    return _object_of(
        category,
        _ambient=Monoids(),
        _engine=(category, _SubmonoidEngine, None),
        ambient=ambient,
        generators=normalized,
        description=description,
        structure_data=structure_data,
    )

def _predicate_submonoid(
    ambient,
    predicate,
    description,
    *,
    placements=(),
    structure_data=None,
):
    r"""Realize the predicate submonoid declared at the monoid owner.

    Protected constructor under OWN-05. ``Monoids.predicate_submonoid`` is
    the caller. The predicate is defined on this exact ambient monoid and
    its truth set contains one and is multiplicatively closed. Any stronger
    placements are supplied with their mathematical premises by that caller.
    The result is the existing facade submonoid with its actual inclusion;
    an undecided predicate value is retained, not treated as nonmembership.
    """
    subobjects = Monoids().Subobjects(ambient)
    # ``placements`` are categories of the submonoid as a monoid (the unit
    # group passes ``OwnedGroups()`` or ``AbelianGroups()``); a subobject
    # placement would make the inclusion part of its ambient category.
    assert not any(placement.is_subcategory(subobjects) for placement in placements), (
        f"the predicate submonoid of {ambient} takes placements of its objects as monoids, "
        f"but {placements} contains a category of subobjects of {ambient}"
    )
    category = owned_category_join((subobjects, *placements))
    return _object_of(
        category,
        _ambient=owned_category_join((Monoids(), *placements)),
        _engine=(category, _SubmonoidEngine, None),
        ambient=ambient,
        predicate=predicate,
        description=description,
        structure_data=structure_data,
    )
