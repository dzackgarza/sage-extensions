r"""Finite coordinates and restriction maps of an absolute Galois group."""

from sage.categories.finite_fields import FiniteFields as SageFiniteFields
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer_ring import ZZ
from sage.structure.element import Element
from sage.structure.element import parent as element_parent
from sage.structure.richcmp import richcmp

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.group.groups import (
    Groups,
    OwnedGroups,
    _fix_selected_group_resolution_data,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedFields,
    RingMorphism,
    _engine_ring,
    _own_ring,
    _owned_engine_element,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of


def _relative_degree(base_field, extension_field):
    r"""Return ``[L:K] = [L:F] / [K:F]`` over the common prime field ``F``.

    Engine adapter: Sage's number fields, the rational field and finite
    fields all answer ``absolute_degree()``, the degree over the prime field.
    """
    base = _engine_ring(base_field)
    extension = _engine_ring(extension_field)
    assert base.characteristic() == extension.characteristic(), (
        f"{extension_field} is not an extension of {base_field}: their characteristics "
        f"{extension.characteristic()} and {base.characteristic()} differ"
    )
    base_degree = ZZ(base.absolute_degree())
    extension_degree = ZZ(extension.absolute_degree())
    assert extension_degree % base_degree == 0, (
        f"{extension_field} is not a finite extension of {base_field}: its absolute "
        f"degree {extension_degree} is not a multiple of {base_degree}"
    )
    return _owned_engine_element(ZZ, extension_degree // base_degree)


class _FiniteGaloisExtensionEngine:
    r"""Computational vocabulary on a finite stage ``K -> L -> Kbar``.

    The stage itself is not this engine.  It is the factorization object in
    ``(K / Fields) / (K -> Kbar)``.  Consequently all four fields/maps below
    are read from that slice object and no copy of the construction datum is
    retained by the realization.
    """

    def _stage_category(self):
        r"""``(K/Fields)/e``, the slice of ``K/Fields`` over ``e: K -> Kbar`` that this stage lies in."""
        factorization = self.arrow()
        return factorization.parent().arrow_category().SliceOver(factorization.codomain())

    def _extension_category(self):
        r"""``K/Fields``, the coslice of field extensions of ``K``."""
        return self._stage_category().base_category()

    def base_field(self):
        return self.base_embedding().domain()

    def field(self):
        return self.base_embedding().codomain()

    def algebraic_closure(self):
        return self._extension_category().arrow(self.arrow().codomain()).codomain()

    def base_embedding(self) -> RingMorphism:
        return self._extension_category().arrow(self)

    def embedding(self) -> RingMorphism:
        return self.arrow().right()

    def degree(self):
        return _relative_degree(self.base_field(), self.field())

    @cached_method
    def automorphisms_over_base_field(self):
        r"""The exact ``K``-automorphisms of ``L``: the self-embeddings of ``L`` fixing ``K``."""
        base_generators = self.base_field().field_generators()
        return finite_ordered_set(
            tuple(
                candidate
                for candidate in self.field().exact_embeddings(self.field())
                if all(
                    candidate(self.base_embedding()(generator))
                    == self.base_embedding()(generator)
                    for generator in base_generators
                )
            )
        )

    def automorphisms(self):
        r"""The elements of ``Gal(L/K)``, as exact field maps; ``L/K`` is Galois."""
        assert self.is_galois(), (
            f"{self.field()} is not represented as a finite Galois extension of {self.base_field()}"
        )
        return self.automorphisms_over_base_field()

    def is_galois(self) -> bool:
        r"""Whether ``L/K`` is Galois: ``|Aut_K(L)| = [L:K]`` (Stacks, Lemma 9.21.2)."""
        return self.automorphisms_over_base_field().cardinality() == cardinal(self.degree())

    def __eq__(self, other) -> bool:
        r"""Equal when the defining data ``K -> L -> Kbar`` agree.

        Membership in this stage's slice ``(K/Fields)/e`` fixes ``K`` and
        ``e: K -> Kbar``; the field is compared by identity and the two exact
        embeddings by their values on field generators.
        """
        stage_category = self._stage_category()
        if other not in stage_category:
            return False
        base_embedding = self._extension_category().arrow(other)
        return (
            base_embedding.codomain() is self.field()
            and base_embedding == self.base_embedding()
            and stage_category.arrow(other).right() == self.embedding()
        )

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(
            (
                id(self.base_field()),
                id(self.field()),
                id(self.algebraic_closure()),
                self.base_embedding(),
                self.embedding(),
            )
        )

    def _repr_(self) -> str:
        return f"Finite separable extension {self.field()} / {self.base_field()} in {self.algebraic_closure()}"


def FiniteGaloisExtension(
    base_field,
    field,
    base_embedding: RingMorphism,
    closure,
    closure_embedding: RingMorphism,
    *,
    extension_object=None,
):
    r"""Construct the finite stage ``K -> L -> Kbar`` as a factorization.

    For the fixed geometric point ``e: K -> Kbar``, a finite stage is exactly
    an object of the slice ``(K / Fields) / e``: its source object is
    ``K -> L`` and its arrow to ``e`` has right edge ``L -> Kbar``.  The
    optional ``extension_object`` is the already-constructed object ``e`` of
    ``K / Fields``; absolute Galois groups supply it so every stage is visibly
    a factorization of that very geometric point.
    """
    base_field = _own_ring(base_field)
    field = _own_ring(field)
    closure = _own_ring(closure)
    assert base_embedding.parent() is base_field.Mor(field), (
        f"the base inclusion K -> L must be a field morphism {base_field} -> {field}, "
        f"but {base_embedding} lies in {base_embedding.parent()}"
    )
    assert closure_embedding.parent() is field.Mor(closure), (
        f"the embedding L -> Kbar must be a field morphism {field} -> {closure}, "
        f"but {closure_embedding} lies in {closure_embedding.parent()}"
    )

    coslice = OwnedFields().CosliceUnder(base_field)
    source_object = coslice(base_embedding)
    composite = closure_embedding * base_embedding
    if extension_object is None:
        extension_object = coslice(composite)
    else:
        assert extension_object in coslice, (
            f"the embedding K -> Kbar {extension_object} is not a field extension of "
            f"{base_field}"
        )
        assert coslice.arrow(extension_object).codomain() is closure, (
            f"the embedding K -> Kbar {extension_object} does not land in the algebraic "
            f"closure {closure}"
        )
        assert coslice.arrow(extension_object) == composite, (
            f"{field} is not an intermediate field of {base_field} -> {closure}: the "
            f"composite {base_field} -> {field} -> {closure} differs from the given "
            f"embedding {coslice.arrow(extension_object)}"
        )

    factorization = coslice.Mor(source_object, extension_object)(closure_embedding)
    stage = coslice.SliceOver(extension_object).object(
        factorization,
        _engine=_FiniteGaloisExtensionEngine,
    )
    compatible_embeddings = finite_ordered_set(
        tuple(
            candidate
            for candidate in field.exact_embeddings(closure)
            if all(
                candidate(base_embedding(generator))
                == closure_embedding(base_embedding(generator))
                for generator in base_field.field_generators()
            )
        )
    )
    assert compatible_embeddings.cardinality() == cardinal(stage.degree()), (
        f"{field} is not separable over {base_field}: it has "
        f"{compatible_embeddings.cardinality()} {base_field}-embeddings into {closure}, "
        f"not [L:K] = {stage.degree()}"
    )
    return stage


def _morphism_signature(morphism: RingMorphism) -> tuple:
    return tuple(
        morphism(generator) for generator in morphism.domain().field_generators()
    )


class FiniteGaloisAutomorphism(Element):
    r"""An exact ``K``-automorphism of a represented finite extension ``L/K``.

    The element implementation of the finite field-automorphism engine:
    an element is its position in the group's enumeration of the
    ``K``-automorphisms of ``L``.
    """

    def __init__(self, parent, index: int) -> None:
        Element.__init__(self, parent)
        self._index = int(index)

    def action(self) -> RingMorphism:
        return self.parent().automorphisms()[self._index]

    as_morphism = action

    def __call__(self, element):
        return self.action()(element)

    def _mul_(self, other):
        r"""``self ∘ other``; Sage's arithmetic calls this with one parent."""
        return self.parent().compose(self, other)

    def __invert__(self):
        return self.inverse()

    def inverse(self):
        return self.parent().inverse(self)

    def multiplicative_order(self):
        identity = self.parent().one()
        value = identity
        for order in range(1, int(self.parent().order()) + 1):
            value = value * self
            if value == identity:
                return _owned_engine_element(ZZ, ZZ(order))
        raise ArithmeticError(
            f"{self} has no power equal to the identity in the finite group {self.parent()}"
        )

    def __pow__(self, exponent):
        exponent = ZZ(exponent)
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = self.parent().one()
        factor = self
        while exponent:
            if exponent & 1:
                result = result * factor
            factor = factor * factor
            exponent >>= 1
        return result

    def _richcmp_(self, other, op):
        r"""Compare by position in the enumeration; Sage calls this with one parent."""
        return richcmp(self._index, other._index, op)

    def __hash__(self) -> int:
        return hash((id(self.parent()), self._index))

    def _repr_(self) -> str:
        return repr(self.action())


class _FiniteFieldAutomorphismEngine:
    r"""The exact finite group Aut_K(L), realized at OwnedGroups().Finite().

    The extension determines the self-embeddings fixing K, their composition
    and inverses.  It is a realization of a finite group, not another
    category of engine outputs.  Normality is required only by the quotient
    entry Gal(L/K), not by Aut_K(L).
    """

    def __init__(self, extension, **rest) -> None:
        self._extension = extension
        super().__init__(**rest)

    def extension_data(self) -> FiniteGaloisExtension:
        return self._extension

    def top_field(self):
        return self._extension.field()

    def base_field(self):
        return self._extension.base_field()

    def automorphisms(self):
        return self._extension.automorphisms_over_base_field()

    @cached_method
    def _signature_positions(self):
        r"""The position of each automorphism, keyed by its values on the generators of ``L``."""
        return {
            _morphism_signature(automorphism): position
            for position, automorphism in enumerate(self.automorphisms())
        }

    def _element_constructor_(self, datum):
        if isinstance(datum, FiniteGaloisAutomorphism):
            if datum.parent() is self:
                return datum
            datum = datum.action()
        if element_parent(datum) is self.top_field().Mor(self.top_field()):
            position = self._signature_positions().get(_morphism_signature(datum))
            if position is None:
                raise ValueError(
                    f"{datum} is not a {self.base_field()}-automorphism of {self.top_field()}"
                )
            return self.element_class(self, position)
        index = int(ZZ(datum))
        if not 0 <= index < int(self.order()):
            raise ValueError(
                f"{self} has {self.order()} elements, so {index} is not an index of one"
            )
        return self.element_class(self, index)

    def __iter__(self):
        return (self.element_class(self, index) for index in range(int(self.order())))

    def one(self):
        identity_signature = tuple(self.top_field().field_generators())
        assert identity_signature in self._signature_positions(), (
            f"the identity of {self.top_field()} is missing from the automorphisms of {self}"
        )
        return self.element_class(self, self._signature_positions()[identity_signature])

    def order(self):
        return _owned_engine_element(
            ZZ,
            ZZ(int(self.automorphisms().cardinality())),
        )

    def _cardinality_decision(self):
        return cardinal(self.order())

    def compose(self, left, right):
        images = tuple(
            left(right(generator)) for generator in self.top_field().field_generators()
        )
        assert images in self._signature_positions(), (
            f"the composite {left} * {right} is missing from the automorphisms of {self}"
        )
        return self.element_class(self, self._signature_positions()[images])

    def inverse(self, element):
        identity = self.one()
        return next(
            candidate
            for candidate in self
            if element * candidate == identity and candidate * element == identity
        )

    def decomposition_group(self, prime_above):
        r"""Return the decomposition subgroup at ``prime_above``."""
        from sage_extensions.categories.group.profinite.galois_decomposition import (
            _finite_decomposition_group,
        )

        return _finite_decomposition_group(self, prime_above)

    def inertia_group(self, prime_above):
        r"""Return the inertia subgroup at ``prime_above``."""
        from sage_extensions.categories.group.profinite.galois_decomposition import (
            _finite_inertia_group,
        )

        return _finite_inertia_group(self, prime_above)

    def frobenius_class(self, base_prime, prime_above):
        r"""Return the unramified Frobenius conjugacy class at ``prime_above``."""
        from sage_extensions.categories.group.profinite.galois_decomposition import (
            _finite_frobenius_class,
        )

        return _finite_frobenius_class(self, base_prime, prime_above)

    def _computed_group_generators(self):
        r"""A generating set: the Frobenius power of order ``[L:K]`` over a finite field, else the nonidentity elements."""
        identity = self.one()
        nonidentity = tuple(element for element in self if element != identity)
        if _engine_ring(self.top_field()) not in SageFiniteFields():
            return finite_ordered_set(nonidentity)
        generators = tuple(
            element
            for element in nonidentity
            if element.multiplicative_order() == self.order()
        )
        assert self.order() == 1 or generators, (
            f"the Galois group {self} of an extension of finite fields must be cyclic, "
            f"but no element has order {self.order()}"
        )
        return finite_ordered_set(generators[:1])

    def _abelianity_decision(self) -> bool:
        return all(left * right == right * left for left in self for right in self)

    def _repr_(self) -> str:
        if self._extension.is_galois():
            return f"Gal({self.top_field()} / {self.base_field()})"
        return f"Aut_{self.base_field()}({self.top_field()})"
    def __call__(self, datum):
        return self._element_constructor_(datum)

    def __contains__(self, datum):
        return isinstance(datum, FiniteGaloisAutomorphism) and datum.parent() is self


@cached_function
def FiniteExtensionAutomorphismGroup(extension):
    r"""Aut_K(L) for the exact extension diagram, using the finite-group entry."""
    group = _object_of(
        OwnedGroups().Finite(),
        _engine=(OwnedGroups(), _FiniteFieldAutomorphismEngine, FiniteGaloisAutomorphism),
        extension=extension,
    )
    generators = group._computed_group_generators()
    source = Groups.Free(index_set=generators)
    generator_morphism = Sets().Mor(generators, group)(lambda generator: generator)
    _fix_selected_group_resolution_data(
        group, source, generators, generator_morphism
    )
    return group


def FiniteGaloisQuotient(extension):
    r"""Gal(L/K): Aut_K(L) when the finite separable extension is normal."""
    assert extension.is_galois(), f"{extension} is not Galois, so it has no Galois group quotient of G_K"
    return FiniteExtensionAutomorphismGroup(extension)




class GaloisRestrictionMap:
    r"""The continuous quotient map (G_K\to\operatorname{Gal}(L/K))."""

    def __init__(self, parent, extension) -> None:
        self._extension = parent.domain().extension_data(extension)
        assert parent.codomain() is parent.domain().finite_quotient(self._extension), (
            f"the restriction map to {self._extension} must land in its Galois group "
            f"{parent.domain().finite_quotient(self._extension)}, but its codomain is "
            f"{parent.codomain()}"
        )
        super().__init__(parent, self._evaluate_restriction)

    def extension(self) -> FiniteGaloisExtension:
        return self._extension

    def _evaluate_restriction(self, element):
        r"""``sigma |-> sigma|_L``: a realized finite coordinate, else the automorphism of ``L`` agreeing with ``sigma`` on its generators."""
        element = self.domain()(element)
        coordinate = element.restriction_coordinate(self.extension())
        if coordinate is not None:
            return self.codomain()(coordinate)
        embedding = self.extension().embedding()
        generators = self.extension().field().field_generators()
        images = tuple(element(embedding(generator)) for generator in generators)
        restriction = next(
            (
                candidate
                for candidate in self.codomain()
                if all(
                    image == embedding(candidate(generator))
                    for generator, image in zip(generators, images, strict=True)
                )
            ),
            None,
        )
        assert restriction is not None, (
            f"{element} does not map {self.extension().field()} into itself, so it has no "
            f"restriction in {self.codomain()}"
        )
        return restriction

    def kernel(self):
        return self.domain().open_subgroup(self.extension())

    def is_surjective(self) -> bool:
        return True

    def is_continuous(self) -> bool:
        return True

    def _repr_(self) -> str:
        return f"Restriction {self.domain()} -> {self.codomain()}"


def _galois_restriction_rule(extension):
    r"""The group-Mor realization rule for restriction to one finite Galois stage."""
    return lambda mor: mor._from_realization_engine(
        GaloisRestrictionMap,
        extension,
    )


class _LiftCosetEngine:
    r"""Private realization of the fiber of a finite Galois restriction map."""

    def __init__(self, restriction_map, element, **rest) -> None:
        self._restriction_map = restriction_map
        self._element = restriction_map.codomain()(element)
        super().__init__(**rest)

    def supergroup(self):
        return self.codomain()

    def ambient(self):
        r"""Return the ambient absolute Galois group containing this coset."""
        return self.supergroup()

    def finite_automorphism(self):
        return self._element

    def extension(self) -> FiniteGaloisExtension:
        return self._restriction_map.extension()

    def restriction_map(self):
        return self._restriction_map

    def kernel(self):
        return self._restriction_map.kernel()

    def representative(self, candidate=None):
        r"""Return a supplied representative, or the canonical finite-field one.

        Over a general field the fiber is a coset but has no distinguished
        element.  Selecting one here would silently reintroduce a global
        extension-choice policy.
        """
        if candidate is not None:
            if candidate not in self:
                raise ValueError(
                    f"{candidate} does not restrict to {self._element} on "
                    f"{self.extension().field()}"
                )
            return candidate
        if self.supergroup()._is_finite_field():
            return self.supergroup().lift(self._element)
        raise ValueError(
            f"the lifts of {self._element} to {self.supergroup()} have no canonical "
            f"representative unless the base field is finite; give one as `candidate`"
        )

    def _repr_(self) -> str:
        return f"Lift coset of {self._element} in {self.supergroup()}"


def LiftCoset(restriction_map: GaloisRestrictionMap, element):
    r"""The actual fiber ``{sigma in G_K : sigma|_L = element}`` as a subset of ``G_K``."""
    target = restriction_map.codomain()(element)
    ambient = restriction_map.domain()
    inclusion = ambient.condition_set(
        lambda candidate: restriction_map(candidate) == target
    ).inclusion()
    return Sets().Subobjects(ambient).object(
        inclusion,
        _engine=_LiftCosetEngine,
        construction_data={
            "restriction_map": restriction_map,
            "element": target,
        },
    )



__all__ = [
    "FiniteExtensionAutomorphismGroup",
    "FiniteGaloisAutomorphism",
    "FiniteGaloisExtension",
    "FiniteGaloisQuotient",
    "LiftCoset",
]
