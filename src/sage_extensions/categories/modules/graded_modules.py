"""Modules graded by a monoid."""

from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.infinity import Infinity as _Infinity
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.group.magmas import (
    AdditiveMonoids,
    Monoids,
)
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphismMethods,
    _initialize_module_mor_parent,
    _ModuleMorCommonMethods,
)
from sage_extensions.categories.modules.pure.modules import (
    LinearEndCategoryConstruction,
    Modules,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.lexicon.algebra import MonoidObject
from sage_extensions.lexicon.set_theory import SetObject
from sage_extensions.logic import AtomicProposition, conjunction
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


def _normalize_grading_monoid(monoid: Parent | None) -> SetObject:
    r"""Return the owned grading monoid, defaulting to \(\mathbb{Z},+\)."""
    return _owned_integers() if monoid is None else monoid


def _require_grading_monoid(monoid: Parent | None) -> MonoidObject:
    monoid = _normalize_grading_monoid(monoid)
    if monoid not in Monoids() and monoid not in AdditiveMonoids():
        raise TypeError(
            f"{monoid} cannot grade a module by degrees that add: it is not a monoid, only known to be in {monoid.category()}"
        )
    return monoid


def _grading_identity(monoid: Parent | None):
    r"""Return the identity degree of the selected grading monoid."""
    monoid = _require_grading_monoid(monoid)
    if monoid in AdditiveMonoids():
        return monoid.zero()
    return monoid.one()


class _ParityKey:
    r"""A chosen parity morphism as a category parameter.

    A chosen morphism has identity semantics as a parameter of a categorical
    construction, as a functor does; the key is interned on that identity.
    """

    def __init__(self, morphism) -> None:
        self._morphism = morphism

    def morphism(self):
        return self._morphism


@cached_function(key=lambda parity: id(parity))
def _parity_key(parity):
    return _ParityKey(parity)


@cached_function
def _integer_parity():
    r"""The reduction ``ZZ -> ZZ/2``, the canonical parity of the integer grading."""
    integers = _owned_integers()
    parity_target = integers.quotient_ring(integers.ideal(integers(2)))
    return integers.Mor(parity_target)(parity_target)


@cached_function
def _two_parity():
    r"""The identity of ``ZZ/2``, the canonical parity of a grading by ``ZZ/2``."""
    integers = _owned_integers()
    two = integers.quotient_ring(integers.ideal(integers(2)))
    return two.Mor(two)(lambda degree: degree)


def _grading_parity(grading_monoid, parity=None):
    r"""Return the parity homomorphism ``M -> ZZ/2`` of the grading, or ``None``.

    The parity is part of the grading datum: a monoid admits many
    homomorphisms to ``ZZ/2``, so it is chosen and stated with the monoid.
    ``ZZ`` is graded with reduction mod 2 and ``ZZ/2`` with the identity unless
    another is stated; every other monoid records the parity it is given and
    none otherwise, and a construction that reads the parity (the Koszul sign
    of a supercommutative product) refuses a grading that recorded none.
    """
    integers = _owned_integers()
    parity_target = integers.quotient_ring(integers.ideal(integers(2)))
    if parity is None:
        if grading_monoid is _owned_integers():
            return _integer_parity()
        if grading_monoid is parity_target:
            return _two_parity()
        return None
    assert parity.domain() is grading_monoid, (
        f"{parity} cannot be the parity of a grading by {grading_monoid}: its domain is {parity.domain()}"
    )
    assert parity.codomain() is parity_target, (
        f"{parity} cannot be the parity of a grading by {grading_monoid}: its codomain is "
        f"{parity.codomain()}, not {parity_target}"
    )
    return parity


def _concentrated_graded_module(base_ring, grading_monoid=None):
    r"""Return a rank-one graded module concentrated in the identity degree."""
    monoid = _require_grading_monoid(grading_monoid)
    return base_ring._fresh_free_module_on(
        Sets.Δ[0],
        _extra_categories=(GradedModules(base_ring, monoid),),
        _extra_construction_data={
            "concentrated_degree": _grading_identity(monoid),
        },
    )


def _represented_homogeneous_degree_or_none(element):
    r"""Return the represented homogeneous degree, or ``None`` for the zero element."""
    components = tuple(element.homogeneous_components().items())
    if not components:
        return None
    if len(components) != 1:
        raise ValueError(
            f"{element} is not homogeneous in {element.parent()}, so it has no single degree"
        )
    return components[0][0]


def _selected_homogeneous_degree(element):
    r"""Return one represented homogeneous degree without imposing one element API."""
    degree = _represented_homogeneous_degree_or_none(element)
    assert degree is not None, (
        f"cannot read a degree of {element}: its parent {element.parent()} gives no degrees to its elements"
    )
    return degree


class GradedModuleMorphismMethods:
    r"""A degree-zero morphism of graded modules.

    An arrow built by an operation of its graded Mor takes
    ``degree_preservation_premises``: the family of graded maps it is built
    from.  It preserves degree when every premise does.
    """

    def __init__(
        self,
        parent,
        images,
        *,
        elementwise=False,
        linearity_premises=None,
        degree_preservation=None,
        degree_preservation_premises=None,
    ) -> None:
        super().__init__(
            parent,
            images,
            elementwise=elementwise,
            linearity_premises=linearity_premises,
        )
        self._supplied_degree_preservation_decision = degree_preservation
        self._degree_preservation_premises = degree_preservation_premises

    def _degree_preservation_derivation(self):
        r"""Conjoin the degree-preservation decisions of the premises, or return ``None``."""
        match self._degree_preservation_premises:
            case None:
                return None
            case premises:
                return conjunction(premise.degree_preservation_decision() for premise in premises)

    @cached_method
    def degree_preservation_decision(self):
        r"""Return the decision that this map preserves degree.

        A decision supplied at construction, or one derived from the
        construction, is returned as given; otherwise the decision is computed
        on the selected homogeneous generators on the first request
        (``OWN-22``).
        """
        if self._supplied_degree_preservation_decision is not None:
            return self._supplied_degree_preservation_decision
        derived = self._degree_preservation_derivation()
        return self._decide_degree_preservation() if derived is None else derived

    @validator
    def validate_degree_preservation(self) -> None:
        r"""Raise ``ValueError`` when this map is decided not to preserve degree (``OWN-22``)."""
        if self.degree_preservation_decision() is False:
            raise ValueError(
                f"the map {self.domain()} -> {self.codomain()} does not preserve degree"
            )

    def _decide_degree_preservation(self):
        r"""Decide degree preservation on selected homogeneous generators, else the proposition ``preserves_degree(f)``."""

        domain = self.domain()
        undecided = AtomicProposition("preserves_degree", self)
        if not domain.has_selected_module_resolution():
            return undecided
        labels = domain.module_generating_set()
        if not labels.cardinality().is_finite():
            return undecided
        answer = True
        for label in labels:
            source = domain.module_generator(label)
            source_degree = _represented_homogeneous_degree_or_none(source)
            if source_degree is None:
                answer = undecided
                continue
            image = self(source)
            zero = image == self.codomain().zero()
            if zero is True:
                continue
            if zero is not False:
                answer = undecided
                continue
            target_degree = _represented_homogeneous_degree_or_none(image)
            if target_degree is None:
                return False
            if target_degree != source_degree:
                return False
        return answer

    def _selected_degree_component(self, degree):
        r"""Return a construction-selected component map, or ``None``."""
        return None

    def _validate_degree_component(self, degree, component):
        r"""Validate specialization-specific laws for one selected component."""
        return component

    def component(self, degree):
        r"""Return the linear map on the degree-``degree`` graded pieces."""
        degree = self.domain().grading_index_set()(degree)
        source = self.domain().graded_piece(degree)
        target = self.codomain().graded_piece(degree)
        selected = self._selected_degree_component(degree)
        if selected is None:
            source_inclusion = source.inclusion()
            target_inclusion = target.inclusion()
            component = source.module_category().Mor(
                source, target
            )._from_constructed_element_map(
                lambda element: target_inclusion.lift(
                    self(source_inclusion(source(element)))
                )
            )
        else:
            component = selected
            if component.domain() is not source or component.codomain() is not target:
                raise ValueError(
                    f"the degree-{degree} component of {self} must be a map {source} -> {target}, "
                    f"but it is {component.domain()} -> {component.codomain()}"
                )
        return self._validate_degree_component(degree, component)

    def __add__(self, other):
        r"""Add admitted graded maps, retaining their degree-preservation laws."""
        parent = self._pointwise_mor()
        if not isinstance(parent, GradedModuleMor):
            return super().__add__(other)
        if other in parent:
            summand = parent(other)
        elif parent.domain() is parent.codomain() and other in parent.base_ring():
            summand = parent._scalar_identity(parent.base_ring()(other))
        else:
            return NotImplemented
        from sage_extensions.categories.group.additive_mors import _scalar_identity_coefficient

        left, right = _scalar_identity_coefficient(self, parent), _scalar_identity_coefficient(summand, parent)
        if left is not None and right is not None:
            return parent._scalar_identity(left + right)
        return parent._from_constructed_graded_map(
            lambda element: self(element) + summand(element),
            premises=(self, summand),
        )

    def __neg__(self):
        r"""Negate a graded map using the additive inverse in each degree."""
        parent = self._pointwise_mor()
        if not isinstance(parent, GradedModuleMor):
            return super().__neg__()
        from sage_extensions.categories.group.additive_mors import _scalar_identity_coefficient

        scalar = _scalar_identity_coefficient(self, parent)
        if scalar is not None:
            return parent._scalar_identity(-scalar)
        return parent._from_constructed_graded_map(
            lambda element: -self(element),
            premises=(self,),
        )

    def __mul__(self, other):
        if not isinstance(other, GradedModuleMorphismMethods):
            return super().__mul__(other)
        if other.codomain() is not self.domain():
            return NotImplemented
        if other.parent() is self.parent() and self.domain() is self.codomain():
            return self.parent()._compose_endomorphisms(self, other)
        domain = other.domain()
        indices = domain.grading_index_set()
        mor = GradedModules(domain.base_ring(), indices).Mor(domain, self.codomain())
        return mor._from_constructed_graded_map(
            lambda element: self(other(element)),
            premises=(self, other),
        )


class GradedModuleMor(_ModuleMorCommonMethods, CategoricalMor):
    ElementMethods = GradedModuleMorphismMethods

    def __init__(self, mor_family, domain, codomain) -> None:
        indices = domain.grading_index_set()
        assert indices is codomain.grading_index_set(), (
            f"no graded-module morphisms {domain} -> {codomain}: the domain is graded by {indices} "
            f"but the codomain by {codomain.grading_index_set()}"
        )
        assert indices is mor_family.base_category().grading_index_set(), (
            f"the morphisms {domain} -> {codomain} are graded by {indices}, but were placed in a category "
            f"graded by {mor_family.base_category().grading_index_set()}"
        )
        _initialize_module_mor_parent(
            self, mor_family, domain, codomain, full_linear_mor=False
        )

    def _element_constructor_(self, images, *, check=False):
        r"""Construct the graded map; ``check=True`` runs its validators (``OWN-22``)."""
        if isinstance(images, Map):
            if self._already_parented_arrow(images):
                images.validate_linearity(check=check)
                images.validate_degree_preservation(check=check)
                return images
            raise TypeError(f"{images} belongs to another Mor; apply the functor between the categories")
        morphism = super()._element_constructor_(images, check=check)
        morphism.validate_degree_preservation(check=check)
        return morphism

    def _from_constructed_graded_map(self, function, *, premises=()):
        r"""Retain a formula whose linearity and degree laws follow from its inputs.

        Graded arithmetic and forgetting a stronger graded-map theory call
        this supplier with their actual graded arrows. Zero and scalar
        identity have both laws by the grading's module axioms, so use the
        empty family. Ordinary linear construction does not call this
        supplier and does not acquire a degree-preservation premise.
        """
        if not callable(function):
            raise TypeError(f"a constructed graded map in {self} needs a function on elements")
        premises = tuple(premises)
        return self.element_class(
            self,
            function,
            elementwise=True,
            linearity_premises=premises,
            degree_preservation_premises=premises,
        )

    def _scalar_identity(self, scalar):
        r"""The selected central scalar acts within each homogeneous submodule."""
        from sage_extensions.categories.group.additive_mors import _ScalarIdentityEvaluation

        return self._from_constructed_graded_map(_ScalarIdentityEvaluation(self, scalar))

    def _compose_module_endomorphisms(self, left, right):
        r"""Compose the actual graded arrows used by the endomorphism algebra."""
        if left not in self or right not in self or self.domain() is not self.codomain():
            raise TypeError(f"composition in {self} needs two admitted graded endomorphisms")
        from sage_extensions.categories.group.additive_mors import _scalar_identity_coefficient

        left_scalar, right_scalar = _scalar_identity_coefficient(left, self), _scalar_identity_coefficient(right, self)
        if left_scalar is not None and right_scalar is not None:
            return self._scalar_identity(left_scalar * right_scalar)
        return self._from_constructed_graded_map(
            lambda element: left(right(element)),
            premises=(left, right),
        )

    def _module_scalar_multiple(self, scalar, morphism):
        r"""Apply the retained central scalar within each target degree."""
        if morphism not in self:
            raise TypeError(f"scalar multiplication in {self} needs an admitted graded map")
        morphism = self(morphism)
        scalar = self.base_ring()(scalar)
        from sage_extensions.categories.group.additive_mors import _scalar_identity_coefficient

        coefficient = _scalar_identity_coefficient(morphism, self)
        if coefficient is not None:
            return self._scalar_identity(scalar * coefficient)
        return self._from_constructed_graded_map(
            lambda element: self._apply_pointwise_scalar(scalar, morphism(element)),
            premises=(morphism,),
        )

    def zero(self):
        r"""The zero map preserves every degree, including off the diagonal."""
        if self.domain() is self.codomain():
            return self._scalar_identity(self.base_ring().zero())
        return self._from_constructed_graded_map(lambda _element: self.codomain().zero())


class GradedModuleMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return GradedModuleMor


class GradedModules(OwnedCategoryOverBaseRing):
    r"""Modules with a direct-sum decomposition indexed by a set.

    Mathlib CategoryTheory/GradedObject defines I-graded objects for any type I,
    with componentwise arrows and a total coproduct.  Multiplying degrees
    requires a monoid; shifts and parity require their additional data.
    The default indexing set is the additive group of integers.
    """

    def an_object(self):
        indices = self.grading_index_set()
        match indices:
            case _ if indices in Monoids() or indices in AdditiveMonoids():
                return _concentrated_graded_module(self.base_ring(), indices)
            case _:
                from sage_extensions.categories.sets.indexed_families import indexed_family

                zero = self.base_ring().free_module(0)
                return self(indexed_family(indices, lambda _: zero))

    @staticmethod
    def __classcall__(cls, base_ring, grading_monoid=None, parity=None):
        r"""``GradedModules(R, M, parity)``: the grading is ``M`` with its parity ``M -> ZZ/2``.

        The parity is canonical for ``ZZ`` (reduction) and ``ZZ/2`` (the
        identity) and stated explicitly for any other monoid; see
        :func:`_grading_parity`.
        """
        monoid = _normalize_grading_monoid(grading_monoid)
        assert monoid in Sets(), f"{monoid} cannot index a grading: it is not a set, only known to be in {monoid.category()}"
        selected_parity = _grading_parity(monoid, parity)
        return OwnedCategoryOverBaseRing.__classcall__(
            cls,
            base_ring,
            monoid,
            None if selected_parity is None else _parity_key(selected_parity),
        )

    def __init__(self, base_ring, grading_monoid: Parent, parity_key) -> None:
        self._grading_index_set = grading_monoid
        self._parity_key = parity_key
        super().__init__(base_ring)

    def _call_(self, pieces, *, placements=(), **construction_data):
        r"""The graded direct sum of the supplied family of R-modules."""
        from sage_extensions.categories.modules.graded_direct_sums import _direct_sum_of_modules

        return _direct_sum_of_modules(
            self.base_ring(), self.grading_index_set(), pieces,
            extra_categories=((*placements, IntegerGradedModules(self.base_ring()))
                              if self.grading_index_set() is _owned_integers() else placements),
            construction_data=construction_data,
        )

    def grading_index_set(self) -> SetObject:
        return self._grading_index_set

    def grading_monoid(self) -> MonoidObject:
        return _require_grading_monoid(self.grading_index_set())

    def parity_homomorphism(self):
        r"""Return the stated parity ``M -> ZZ/2`` of the grading."""
        assert self._parity_key is not None, (
            f"{self.grading_index_set()} is an indexing set with no canonical parity "
            f"homomorphism to ZZ/(2); state the parity with the grading"
        )
        return self._parity_key.morphism()

    def _repr_object_names(self) -> str:
        monoid = self.grading_index_set()
        if monoid is _owned_integers():
            names = "graded modules"
        else:
            names = f"modules graded by {monoid}"
        return f"{names} over {self.base()}"

    def _make_named_class_key(self, name):
        return (super()._make_named_class_key(name), self.grading_index_set(), self._parity_key)

    def super_categories(self):

        return [Modules(self.base_ring())]

    _MorCategory = GradedModuleMorCategoryConstruction
    _EndCategory = LinearEndCategoryConstruction

    class ParentMethods:

        @object_level
        def End(self):
            r"""Endomorphisms preserving the chosen degree decomposition."""
            return self._graded_module_placement().End(self)

        @object_level
        def Aut(self):
            r"""Automorphisms preserving the chosen degree decomposition."""
            return self._graded_module_placement().Aut(self)

        def __init__(
            self,
            concentrated_degree=None,
            degree_on_module_generator=None,
            **rest,
        ) -> None:
            self._preamble_concentrated_degree = concentrated_degree
            self._preamble_degree_on_module_generator = degree_on_module_generator
            super().__init__(**rest)

        def is_graded(self) -> bool:
            return True

        def _graded_module_placement(self):
            r"""Return the declared graded-module placement carrying the grading datum."""
            for category in self.category().all_super_categories(proper=False):
                # Sage realizes a category instance in a dynamic subclass; the
                # declared placement is therefore recognized by its category class.
                if isinstance(category, GradedModules):
                    return category
            raise AssertionError(f"{self} is not a graded module: it is only known to be in {self.category()}")

        def grading_index_set(self):
            return self._graded_module_placement().grading_index_set()

        def grading_monoid(self):
            return _require_grading_monoid(self.grading_index_set())

        def parity_homomorphism(self):
            r"""Return the parity ``M -> ZZ/2`` stated with this module's grading."""
            return self._graded_module_placement().parity_homomorphism()

        def combine_degrees(self, left, right):
            r"""The monoid product of two degrees.

            Additive monoids use \(+\); otherwise the monoid operation is
            multiplication.  A set grading alone supplies no such operation.
            """
            monoid = self.grading_monoid()
            left = monoid(left)
            right = monoid(right)
            if monoid in AdditiveMonoids():
                return left + right
            return left * right

        def concentrated_degree(self):
            selected = self._preamble_concentrated_degree
            if selected is None:
                raise TypeError(f"{self} was not constructed as a graded module concentrated in a single degree")
            return selected

        def degree_on_module_generator(self, module_generator):
            r"""Return the selected degree of one homogeneous framing generator.

            A graded object whose grading is read from a framing supplies this
            operation.  Construction-specific parents such as free graded
            algebras override it; a merely category-placed object with no
            represented grading on its framing refuses rather than guessing.
            """
            selected = self._preamble_degree_on_module_generator
            if selected is not None:
                return selected(module_generator)
            concentrated = self._preamble_concentrated_degree
            if concentrated is not None:
                return concentrated
            raise TypeError(
                f"{self} gives no degree to its chosen module generators, so the degree of {module_generator} is unknown"
            )

        def module_generators_of_degree(self, degree):
            r"""Return the selected framing generators lying in ``degree``."""
            if not self.has_selected_module_resolution():
                raise TypeError(
                    f"cannot list the generators of {self} in degree {degree}: {self} has no chosen "
                    f"generating set; it is in {self.category()}"
                )
            labels = self.module_generating_set()
            assert labels.cardinality().is_finite() is True, (
                f"cannot list the generators of {self} in degree {degree}: its chosen generating set {labels} "
                f"is not known to be finite"
            )
            return finite_ordered_set(
                tuple(
                    self.module_generator(label)
                    for label in labels
                    if self.degree_on_module_generator(self.module_generator(label)) == degree
                )
            )

        def graded_piece(self, degree):
            r"""Return the represented degree piece as a subobject of this module.

            This is the generic framing-derived fallback.  Constructions with
            a more intrinsic degree-piece owner, such as tensor or symmetric
            powers, override this method and remain authoritative.
            """
            if not self.has_selected_module_resolution():
                raise TypeError(
                    f"cannot form the degree-{degree} piece of {self}: {self} has no chosen generating set; "
                    f"it is in {self.category()}"
                )
            return self.subobject_on(self.module_generators_of_degree(degree))

        def homogeneous_degree(self, element):
            r"""Return the selected degree of one nonzero homogeneous element."""
            element = self(element)
            degree = _represented_homogeneous_degree_or_none(element)
            if degree is None:
                raise ValueError("zero has no selected homogeneous degree here")
            return self.grading_monoid()(degree)

    class ElementMethods:
        def is_homogeneous(self) -> bool:
            r"""Whether all nonzero framing terms lie in one degree."""
            parent = self.parent()
            degrees = {
                parent.degree_on_module_generator(parent.module_generator(label))
                for label in parent.framing_morphism().lift(self).support().domain()
            }
            return len(degrees) <= 1

        def homogeneous_components(self):
            r"""Return the degree-indexed nonzero homogeneous components."""
            parent = self.parent()
            components = {}
            coordinates = parent.framing_morphism().lift(self)
            for label in coordinates.support().domain():
                generator = parent.module_generator(label)
                degree = parent.degree_on_module_generator(generator)
                component = components.get(degree, parent.zero())
                components[degree] = component + parent.scalar_multiple(
                    coordinates(label), generator
                )
            return components

        def truncate(self, degree):
            r"""Return the sum of homogeneous terms of degree strictly below ``degree``."""
            parent = self.parent()
            if parent.grading_monoid() is not _owned_integers():
                raise TypeError(
                    f"cannot truncate {self} below degree {degree}: its parent {parent} is graded by "
                    f"{parent.grading_monoid()}, and truncation is computed only for gradings by the integers"
                )
            result = parent.zero()
            coordinates = parent.framing_morphism().lift(self)
            for label in coordinates.support().domain():
                generator = parent.module_generator(label)
                if parent.degree_on_module_generator(generator) < degree:
                    result += parent.scalar_multiple(coordinates(label), generator)
            return result
class IntegerGradedModules(OwnedCategoryOverBaseRing):
    r"""Modules graded by the totally ordered additive group of integers."""

    def super_categories(self):
        return [GradedModules(self.base_ring(), _owned_integers())]

    def an_object(self):
        return self(GradedModules(self.base_ring()).an_object())

    def _call_(self, module):
        from sage_extensions.refine import refine

        if module not in GradedModules(self.base_ring(), _owned_integers()):
            raise TypeError("maximum degree requires an integer-graded module")
        return refine(module, self)

    class ElementMethods:
        def degree(self):
            r"""Maximum of the integer degrees of the finite homogeneous support.

            The zero element has degree negative infinity.
            """
            parent = self.parent()
            coordinates = parent.framing_morphism().lift(self)
            return max(
                (parent.degree_on_module_generator(parent.module_generator(label))
                 for label in coordinates.support().domain()),
                default=-_Infinity,
            )
