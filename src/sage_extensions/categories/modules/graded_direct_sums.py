r"""Finite-support direct sums of a represented family of graded modules."""

from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import ModuleElement, parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.modules.graded_modules import (
    GradedModules,
    _grading_identity,
)
from sage_extensions.categories.sets.set_categories import FiniteSets
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    ModulesWithChosenComponentPresentation,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import finite_indexed_family
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.logic import conjunction, negation
from sage_extensions.owned_category import _object_of


class GradedDirectSumElement(ModuleElement):
    r"""A finite family of homogeneous components."""

    def __init__(self, parent, components) -> None:
        super().__init__(parent)
        normalized = {}
        for degree, component in components.items():
            degree = parent.normalize_degree(degree)
            piece = parent.graded_piece(degree)
            if component.parent() is not piece:
                component = piece(component)
            if (component == piece.zero()) is not True:
                normalized[degree] = component
        self._components = normalized

    def homogeneous_components(self):
        support = finite_ordered_set(tuple(self._components))
        return finite_indexed_family(
            support,
            self._components.__getitem__,
            name="Nonzero homogeneous components",
        )

    def homogeneous_component(self, degree):
        degree = self.parent().normalize_degree(degree)
        return self._components.get(degree, self.parent().graded_piece(degree).zero())

    def is_homogeneous(self) -> bool:
        return len(self._components) <= 1

    def degree(self):
        if not self._components:
            return _grading_identity(self.parent().grading_monoid())
        if len(self._components) != 1:
            raise ValueError(
                f"{self} has no degree: it is not homogeneous, having nonzero components in degrees "
                f"{sorted(self._components, key=str)}"
            )
        return next(iter(self._components))

    def _coefficient_data(self):
        coefficients = {}
        labels = self.parent().module_generating_set()
        for degree, component in self._components.items():
            coordinates = self.parent().graded_piece(degree).framing_morphism().lift(component)
            for label in coordinates.support().domain():
                coefficients[
                    labels(self.parent().degree_index_set()(degree), label)
                ] = coordinates(label)
        return coefficients

    def _add_(self, other):
        degrees = set(self._components) | set(other._components)
        return self.parent().from_components(
            {
                degree: self.homogeneous_component(degree)
                + other.homogeneous_component(degree)
                for degree in degrees
            }
        )

    def _neg_(self):
        return self.parent().from_components(
            {degree: -component for degree, component in self._components.items()}
        )

    def _lmul_(self, scalar):
        return self.parent().scalar_multiple(scalar, self)

    def _rmul_(self, scalar):
        return self.parent().scalar_multiple(scalar, self)

    def __rmul__(self, scalar):
        return self.parent().scalar_multiple(scalar, self)

    def _acted_upon_(self, actor, self_on_left):
        _ = self_on_left
        try:
            scalar = self.parent().base_ring()(actor)
        except (TypeError, ValueError):
            return None
        return self.parent().scalar_multiple(scalar, self)

    def _richcmp_(self, other, op):
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if element_parent(other) is not self.parent():
            return op == op_NE
        equal = conjunction(
            self.homogeneous_component(degree) == other.homogeneous_component(degree)
            for degree in set(self._components) | set(other._components)
        )
        return equal if op == op_EQ else negation(equal)

    def _repr_(self):
        if not self._components:
            return "0"
        return " + ".join(
            f"[{degree}]({component})"
            for degree, component in self._components.items()
        )


__all__ = [
    "GradedDirectSumElement",
]


class _DirectSumOfModules:
    r"""Finite-support realization of a direct sum of arbitrary modules.

    The component elements and arithmetic are shared with the framed
    realization; no basis is claimed for the pieces.  The coproduct map is
    the finite sum of the component maps.  Further structure is constructed
    from this family at its module owner.
    """

    def __init__(self, summand_family, **rest) -> None:
        self._summand_family = summand_family
        super().__init__(**rest)

    def degree_index_set(self):
        return self._summand_family.index_set()

    def normalize_degree(self, degree):
        return self.degree_index_set()(degree)

    def graded_piece(self, degree):
        piece = self._summand_family[self.normalize_degree(degree)]
        assert piece in Modules(self.base_ring()), (
            f"{self} is not a direct sum of {self.base_ring()}-modules: its summand {piece} in degree "
            f"{degree} is in {piece.category()}"
        )
        return piece

    def from_components(self, components):
        return self.element_class(self, components)

    def from_component(self, degree, component):
        return self.from_components({self.normalize_degree(degree): component})

    from_graded_piece = from_component

    def _element_constructor_(self, value):
        source = element_parent(value)
        if source is self:
            return value
        if source in Modules(self.base_ring()) and self._built_on_the_same_data(source):
            return self.from_components(value.homogeneous_components())
        if isinstance(value, dict):
            return self.from_components(value)
        raise TypeError(
            f"{value!r} is not an element of {self}: an element of a direct sum is a finite family "
            "of homogeneous components, given as a dict from degrees to elements of the summands"
        )

    def __call__(self, value):
        return self._element_constructor_(value)

    def zero(self):
        return self.from_components({})

    an_element = zero

    def _owned_scalar_multiple(self, scalar, element):
        scalar = self.base_ring()(scalar)
        return self.from_components({
            degree: self.graded_piece(degree).scalar_multiple(scalar, component)
            for degree, component in self(element).homogeneous_components().items()
        })

    @cached_method
    def injection(self, degree):
        degree = self.normalize_degree(degree)
        return Modules(self.base_ring()).Mor(self.graded_piece(degree), self)._from_constructed_element_map(
            lambda element: self.from_component(degree, element)
        )

    @cached_method
    def projection(self, degree):
        degree = self.normalize_degree(degree)
        return Modules(self.base_ring()).Mor(self, self.graded_piece(degree))._from_constructed_element_map(
            lambda element: self(element).homogeneous_component(degree)
        )

    def from_maps(self, codomain, maps):
        r"""The unique linear map whose restrictions to the summands are ``maps``."""
        assert maps.index_set() is self.degree_index_set(), (
            f"cannot induce a map out of {self}: the maps must be indexed by the summand index set "
            f"{self.degree_index_set()}, but they are indexed by {maps.index_set()}"
        )

        for degree in maps.index_set() if maps.index_set().cardinality().is_finite() else ():
            morphism = maps[degree]
            assert morphism.domain() is self.graded_piece(degree) and morphism.codomain() is codomain, (
                f"cannot induce a map {self} -> {codomain}: the map {morphism} in degree {degree} must go "
                f"from the summand {self.graded_piece(degree)} to {codomain}, but it goes from "
                f"{morphism.domain()} to {morphism.codomain()}"
            )
        def evaluate(element):
            return sum(
                (
                    maps[degree](component)
                    for degree, component in self(element).homogeneous_components().items()
                ),
                codomain.zero(),
            )

        return Modules(self.base_ring()).Mor(self, codomain)._from_constructed_element_map(
            evaluate,
            premises=maps,
        )

    def _direct_sum_realization(self):
        r"""The private component engine retained when further structure is supplied."""
        return _DirectSumOfModules, GradedDirectSumElement

    def _module_with_structure(self, categories, construction_data):
        return _direct_sum_of_modules(
            self.base_ring(), self.grading_index_set(), self._summand_family,
            extra_categories=categories, construction_data=construction_data,
            _realization=self._direct_sum_realization(),
        )

    def _repr_(self):
        return f"Direct sum over {self.degree_index_set()}"


@cached_function(key=lambda ring, pieces: (id(ring), id(pieces)))
def _direct_sum_framing_source(ring, pieces):
    r"""The one chosen free source of the summed framings of this family."""
    labels = Sets().coproduct(pieces.map(lambda piece: piece.module_generating_set()))
    return ring.free_module(labels)


class _FramedDirectSumOfModules(_DirectSumOfModules):
    r"""The direct sum of chosen epimorphisms from free modules.

    If F(S_i) -> M_i are the framings, F(disjoint_union S_i) -> direct_sum M_i
    sends the generator (i,s) to the i-th inclusion of its image in M_i.
    Every finite-support element lifts term by term, so this is an epimorphism;
    no independence of the images is assumed.
    """

    def __init__(self, summand_family, **rest) -> None:
        ring = rest["base_ring"]
        source = _direct_sum_framing_source(ring, summand_family)
        super().__init__(
            summand_family=summand_family,
            module_generating_set=source.module_generating_set(),
            module_generator_function=lambda label: self.from_component(
                label.summand_index(),
                self.graded_piece(label.summand_index()).module_generator(label.summand_element()),
            ),
            framing_source=source,
            **rest,
        )

    def _element_constructor_(self, value):
        match value:
            case dict():
                return self.linear_combination(value)
            case _:
                return super()._element_constructor_(value)

    def _module_with_structure(self, categories, construction_data):
        return super()._module_with_structure(categories, construction_data)

    def _direct_sum_realization(self):
        return _FramedDirectSumOfModules, GradedDirectSumElement

    def module_component_key(self, label):
        return self.module_generating_set()(label).summand_index()

    def module_component(self, degree):
        return self.graded_piece(degree)

    def module_component_generator_label(self, label):
        return self.module_generating_set()(label).summand_element()

    def module_label_from_component(self, degree, component_label):
        return self.module_generating_set()(self.normalize_degree(degree), component_label)


def _direct_sum_of_modules(
    ring, grading_monoid, pieces, *, extra_categories=(), construction_data=None,
    _realization=None, componentwise_framing=None,
):
    r"""The direct sum of ``pieces``, graded by ``grading_monoid``.

    It carries the componentwise chosen generators exactly when every piece
    carries chosen generators.  Over an infinite grading set that is not
    decided by visiting the pieces: the caller that supplies framed pieces
    states it with ``componentwise_framing=True``.  Over a finite grading set
    the pieces are asked.
    """
    graded = GradedModules(ring, grading_monoid)
    assert pieces.index_set() is grading_monoid, (
        f"cannot form a direct sum graded by {grading_monoid}: the summands are indexed by "
        f"{pieces.index_set()}, not by the grading monoid"
    )
    category = Cat().meet((graded, *extra_categories))
    match componentwise_framing:
        case None if grading_monoid in FiniteSets():
            framed = all(piece.has_selected_module_resolution() for piece in pieces)
        case None:
            framed = False
        case stated:
            framed = stated
    if framed:
        category = Cat().meet((
            category,
            ModulesWithChosenComponentPresentation(ring),
        ))
    match _realization:
        case None:
            match framed:
                case True:
                    realization = (_FramedDirectSumOfModules, GradedDirectSumElement)
                case False:
                    realization = (_DirectSumOfModules, GradedDirectSumElement)
        case realization:
            pass
    return _object_of(
        category, _engine=(graded, *realization),
        base_ring=ring, summand_family=pieces, **(construction_data or {}),
    )
