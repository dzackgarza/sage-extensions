r"""Module quotients of words, with relations computed in their summand modules.

The tensor case distributes over the chosen direct sum, as in Mathlib
LinearAlgebra/DirectSum/TensorProduct, TensorProduct.directSum.  In the
symmetric case the commutativity relations collect equal summand indices;
the component of multiplicity (d_i) is tensor_i Sym^(d_i)(M_i).
Finite support touches only finitely many such exact module computations.
This is a private module realization, not an algebra or a new category.
"""

from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.modules.general_modules import GeneralModules
from sage_extensions.categories.modules.framed.framed_free_modules import FramedFreeModules
from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import _SelectedFinitePresentationModules
from sage_extensions.categories.modules.graded_modules import GradedModules
from sage_extensions.categories.modules.pure.modules import (
    Modules, ModuleSubobjects,
    ModulesWithChosenComponentPresentation, ModulesWithChosenFinitePresentation,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import NN, EnumeratedSets, Sets as OwnedSets
from sage_extensions.logic import conjunction, negation
from sage_extensions.owned_category import _object_of


def _nested_component_label(component, labels):
    labels = tuple(labels)
    match len(labels):
        case 0:
            return 0
        case 1:
            return labels[0]
        case _:
            left = _nested_component_label(component.tensor_factor(0), labels[:-1])
            return component.module_generating_set()(lambda index: left if int(index) == 0 else labels[-1])


def _flatten_nested_label(label, length):
    match length:
        case 0:
            return ()
        case 1:
            return (label,)
        case _:
            left, right = label.component(0), label.component(1)
            return _flatten_nested_label(left, length - 1) + (right,)


def _has_component_presentation(source):
    r"""Whether ``source`` retains the owned component-presentation datum."""
    return source in ModulesWithChosenComponentPresentation(source.base_ring())


class _WordPresentation:
    r"""The selected word cover and its componentwise module quotient."""

    def __init__(self, source_module, flavor):
        assert flavor in ("tensor", "symmetric"), (
            f"cannot build an algebra of words on {source_module}: {flavor!r} is not 'tensor' or 'symmetric'"
        )
        assert (
            _has_component_presentation(source_module)
            or source_module in FramedFreeModules(source_module.base_ring())
            or source_module in ModulesWithChosenFinitePresentation(source_module.base_ring())
        ), (
            f"cannot build the {flavor} algebra of {source_module}: this algorithm needs a free module, "
            f"a finitely presented module with a chosen finite presentation, or a direct sum of such "
            f"modules, but {source_module} is in {source_module.category()}"
        )
        self._source_module = source_module
        self._flavor = flavor
        self._component_cache = {}
        alphabet = source_module.module_generating_set()
        match alphabet:
            case _ if alphabet in EnumeratedSets():
                match flavor:
                    case "tensor":
                        self._labels = alphabet.finite_words()
                    case "symmetric":
                        self._labels = alphabet.finite_multisets()
            case _:
                self._labels = OwnedSets().coproduct(indexed_family(NN, self._degree_set))
        self._cover = self.base_ring().free_module(self._labels)

    def source_module(self):
        return self._source_module

    def flavor(self):
        return self._flavor

    def base_ring(self):
        return self.source_module().base_ring()

    def module_generating_set(self):
        return self._labels

    def cover(self):
        return self._cover

    def _source_has_component_protocol(self):
        return _has_component_presentation(self.source_module())

    def _source_has_relations(self):
        r"""Whether the chosen source framing needs its finite relation quotient."""
        source = self.source_module()
        return (
            source not in FramedFreeModules(self.base_ring())
            and source in ModulesWithChosenFinitePresentation(self.base_ring())
        )

    def _homogeneous_module(self, degree):
        r"""The canonical tensor or symmetric power, with its module relations."""
        source = self.source_module()
        match self.flavor():
            case "tensor":
                return source.tensor_power(int(degree))
            case "symmetric":
                return source.symmetric_power(int(degree))

    def _homogeneous_label(self, label):
        r"""Read a flat word label in the canonical module power's framing."""
        from sage_extensions.categories.modules.tensor_products import _nested_tensor_label

        label = self.module_generating_set()(label)
        degree = int(label.summand_index())
        word = label.summand_element()
        match degree:
            case 0:
                return next(iter(self._homogeneous_module(0).module_generating_set()))
            case _:
                match self.flavor():
                    case "tensor":
                        return _nested_tensor_label(
                            self.source_module(),
                            tuple(word.component(index) for index in word.parent().index_set()),
                        )
                    case "symmetric":
                        match degree:
                            case 1:
                                return next(iter(word.support()))
                            case _:
                                return self._homogeneous_module(degree).module_generating_set().from_multiplicities(
                                    {item: word.multiplicity(item) for item in word.support()}
                                )

    def _label_from_homogeneous(self, degree, label):
        r"""Read the canonical power's framing label in the flat word cover."""
        from sage_extensions.categories.modules.tensor_products import _flatten_tensor_label

        degree = int(degree)
        labels = self.degree_basis(degree)
        match self.flavor():
            case "tensor":
                word = _flatten_tensor_label(label, degree)
                inner = labels(lambda index: word[int(index)])
            case "symmetric":
                match degree:
                    case 0:
                        multiplicities = {}
                    case 1:
                        multiplicities = {label: 1}
                    case _:
                        multiplicities = {item: label.multiplicity(item) for item in label.support()}
                inner = labels.from_multiplicities(multiplicities)
        return self.basis_label(degree, inner)

    def degree_basis(self, degree):
        r"""The exact degree summand of the selected word cover's label set."""
        degree = int(degree)
        if degree < 0:
            raise ValueError(
                f"{self} has no degree-{degree} piece: a degree must be a nonnegative integer"
            )
        return self.module_generating_set().cofactor(NN(degree))

    def _degree_set(self, degree):
        r"""The finite-power set when no enumeration of the alphabet is given."""
        alphabet = self.source_module().module_generating_set()
        match self.flavor():
            case "tensor":
                indices = OwnedSets.Δ[int(degree) - 1]
                return OwnedSets().product(indexed_family(indices, lambda _: alphabet))
            case "symmetric":
                return alphabet.multisets_of_size(degree)

    def basis_label(self, degree, degree_label):
        degree = int(degree)
        return self.module_generating_set()(degree, self.degree_basis(degree)(degree_label))

    def _monomial_component_key(self, basis_label):
        source = self.source_module()
        basis_label = self.module_generating_set()(basis_label)
        inner = basis_label.summand_element()
        if self.flavor() == "tensor":
            return tuple(source.module_component_key(inner.component(position)) for position in inner.parent().index_set())
        multiplicities = {}
        for label in inner.support():
            key = source.module_component_key(label)
            multiplicities[key] = multiplicities.get(key, 0) + inner.multiplicity(label)
        return frozenset(multiplicities.items())

    def _component_items(self, key):
        return tuple(sorted(key, key=lambda item: repr(item[0])))

    def _component_module(self, key):
        cached = self._component_cache.get(key)
        if cached is not None:
            return cached

        source = self.source_module()
        if self.flavor() == "tensor":
            factors = tuple(source.module_component(source_key) for source_key in key)
        else:
            factors = tuple(
                source.module_component(source_key).symmetric_power(multiplicity)
                for source_key, multiplicity in self._component_items(key)
            )

        if not factors:
            component = self.base_ring().regular_module()
        else:
            component = factors[0]
            if len(factors) > 1:
                modules = Modules(self.base_ring())
                for factor in factors[1:]:
                    component = modules.tensor_product((component, factor))
        self._component_cache[key] = component
        return component

    def _component_generator_label(self, basis_label):
        source = self.source_module()
        basis_label = self.module_generating_set()(basis_label)
        inner = basis_label.summand_element()
        if self.flavor() == "tensor":
            return _nested_component_label(
                self._component_module(self._monomial_component_key(basis_label)),
                (source.module_component_generator_label(inner.component(position)) for position in inner.parent().index_set()),
            )

        grouped = {}
        for source_label in inner.support():
            exponent = inner.multiplicity(source_label)
            key = source.module_component_key(source_label)
            component_label = source.module_component_generator_label(source_label)
            counts = grouped.setdefault(key, {})
            counts[component_label] = counts.get(component_label, 0) + int(exponent)

        factor_labels = []
        for key, multiplicity in self._component_items(self._monomial_component_key(basis_label)):
            counts = grouped[key]
            source_component = source.module_component(key)
            if multiplicity == 1:
                factor_labels.append(next(iter(counts)))
            else:
                factor = source_component.symmetric_power(multiplicity)
                factor_labels.append(factor.module_generating_set().from_multiplicities(counts))
        return _nested_component_label(self._component_module(self._monomial_component_key(basis_label)), factor_labels)

    def _basis_label_from_component(self, key, component_label):
        source = self.source_module()
        if self.flavor() == "tensor":
            component_labels = _flatten_nested_label(component_label, len(key))
            degree = len(key)
            inner = self.degree_basis(degree)(
                lambda position: source.module_label_from_component(
                    key[int(position)],
                    component_labels[int(position)],
                )
            )
            return self.basis_label(degree, inner)

        items = self._component_items(key)
        factor_labels = _flatten_nested_label(component_label, len(items))
        counts = {}
        for (source_key, multiplicity), factor_label in zip(items, factor_labels, strict=True):
            if multiplicity == 1:
                labelled_factors = ((factor_label, 1),)
            else:
                labelled_factors = (
                    (label, factor_label.multiplicity(label))
                    for label in factor_label.support()
                )
            for source_component_label, exponent in labelled_factors:
                exponent = int(exponent)
                if not exponent:
                    continue
                source_label = source.module_label_from_component(source_key, source_component_label)
                counts[source_label] = counts.get(source_label, 0) + exponent
        degree = sum(counts.values())
        inner = self.degree_basis(degree).from_multiplicities(counts)
        return self.basis_label(degree, inner)

    def _normalize_component_relations(self, representative):
        grouped = {}
        ring = self.base_ring()
        for basis_label in representative.support().domain():
            coefficient = ring(representative(basis_label))
            basis_label = self.module_generating_set()(basis_label)
            if not coefficient:
                continue
            key = self.component_key(basis_label)
            component_label = self.component_label(basis_label)
            component_coefficients = grouped.setdefault(key, {})
            component_coefficients[component_label] = component_coefficients.get(component_label, ring.zero()) + coefficient

        normalized = {}
        for key, component_coefficients in grouped.items():
            component = self.component_module(key)
            element = component.linear_combination(component_coefficients)

            if component in _SelectedFinitePresentationModules(self.base_ring()):
                element = component._smith_representative(element)
            lifted = component.framing_morphism().lift(element)
            for component_label in lifted.support().domain():
                basis_label = self.label_from_component(key, component_label)
                normalized[basis_label] = normalized.get(basis_label, ring.zero()) + ring(lifted(component_label))
        return {label: coefficient for label, coefficient in normalized.items() if coefficient}


    def normalize(self, representative):
        representative = self.cover()(representative)
        match self._source_has_component_protocol() or self._source_has_relations():
            case False:
                return representative
            case True:
                return self.cover().linear_combination(self._normalize_component_relations(representative))

    def component_key(self, label):
        match self._source_has_component_protocol():
            case True:
                return self._monomial_component_key(label)
            case False:
                match self._source_has_relations():
                    case True:
                        return self.module_generating_set()(label).summand_index()
                    case False:
                        return self.module_generating_set()(label)

    def component_module(self, key):
        match self._source_has_component_protocol():
            case True:
                return self._component_module(key)
            case False:
                match self._source_has_relations():
                    case True:
                        return self._homogeneous_module(key)
                    case False:
                        return self.base_ring().regular_module()

    def component_label(self, label):
        match self._source_has_component_protocol():
            case True:
                return self._component_generator_label(label)
            case False:
                match self._source_has_relations():
                    case True:
                        return self._homogeneous_label(label)
                    case False:
                        return 0

    def label_from_component(self, key, label):
        match self._source_has_component_protocol():
            case True:
                return self._basis_label_from_component(key, label)
            case False:
                match self._source_has_relations():
                    case True:
                        return self._label_from_homogeneous(key, label)
                    case False:
                        assert label == 0, (
                            f"the summand of {self} indexed by the word {key} is free of rank one, "
                            f"so its only generator is 0, not {label}"
                        )
                        return self.module_generating_set()(key)


class _WordClass:
    r"""A class in the word cover modulo the source's module relations."""

    def __init__(self, parent, representative):
        self._representative = parent.presentation().normalize(representative)
        super().__init__(parent)

    def _richcmp_(self, other, op):
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if element_parent(other) is not self.parent():
            return op == op_NE
        presentation = self.parent().presentation()
        difference = presentation.normalize(self._representative - other._representative)
        equal = conjunction(difference(label) == presentation.base_ring().zero() for label in difference.support().domain())
        return equal if op == op_EQ else negation(equal)

    __hash__ = None

    def _repr_(self):
        return repr(self._representative)


class _WordClasses:
    def __init__(self, word_presentation, **rest):
        self._word_presentation = word_presentation
        super().__init__(**rest)

    def presentation(self):
        return self._word_presentation

    def __call__(self, value):
        if element_parent(value) is self:
            return value
        return self.element_class(self, self.presentation().cover()(value))

    def __contains__(self, value):
        return element_parent(value) is self

    def zero(self):
        return self(self.presentation().cover().zero())

    an_element = zero

    def add(self, left, right):
        return self(self(left)._representative + self(right)._representative)

    def negate(self, element):
        return self(-self(element)._representative)

    def scale(self, scalar, element):
        return self(self.presentation().cover().scalar_multiple(scalar, self(element)._representative))


@cached_function(key=id)
def _word_class_set(presentation):
    return _object_of(OwnedSets(), _engine=(OwnedSets(), _WordClasses, _WordClass), word_presentation=presentation)


class _WordModuleElement:
    def homogeneous_components(self):
        degrees = {
            int(label.summand_index())
            for label in self.parent().framing_morphism().lift(self).support().domain()
        }
        return {degree: self.parent().homogeneous_component(self, degree) for degree in degrees}

    def homogeneous_component(self, degree):
        return self.parent().homogeneous_component(self, degree)


class _WordModule:
    r"""The framed module quotient; addition and scalars belong to GeneralModules."""

    def __init__(self, word_presentation, **rest):
        self._word_presentation = word_presentation
        classes = _word_class_set(word_presentation)
        cover = word_presentation.cover()
        super().__init__(
            underlying_set=classes, addition=classes.add, zero=classes.zero(),
            negation=classes.negate, scalar_action=classes.scale,
            module_generating_set=cover.module_generating_set(),
            module_generator_function=lambda label: self(classes(cover.module_generator(label))),
            framing_source=cover,
            **rest,
        )

    def generating_module(self):
        r"""The module whose letters generate this word-module construction."""
        return self._word_presentation.source_module()

    def word_flavor(self):
        return self._word_presentation.flavor()

    def _module_with_structure(self, categories, construction_data):
        return _word_module(self._word_presentation, extra_categories=categories, construction_data=construction_data)

    def _element_constructor_(self, value):
        match value:
            case dict():
                value = self.underlying_set()(self._word_presentation.cover().linear_combination(value))
            case _:
                pass
        return super()._element_constructor_(value)

    def _selected_module_coefficients(self, element):
        return self(element).underlying_element()._representative

    def degree_basis(self, degree):
        return self._word_presentation.degree_basis(degree)

    def basis_label(self, degree, label):
        return self._word_presentation.basis_label(degree, label)

    def module_component_key(self, label):
        return self._word_presentation.component_key(label)

    def module_component(self, key):
        return self._word_presentation.component_module(key)

    def module_component_generator_label(self, label):
        return self._word_presentation.component_label(label)

    def module_label_from_component(self, key, label):
        return self._word_presentation.label_from_component(key, label)

    @cached_method
    def graded_piece(self, degree):
        degree = int(degree)
        match degree:
            case value if value < 0:
                return self.base_ring().free_module(0)
            case 0:
                return self.base_ring().regular_module()
            case 1:
                return self.generating_module()
            case _:
                return _word_degree_module(_module_on_word_quotient(self.generating_module(), self.word_flavor()), degree)

    def from_component(self, degree, component):
        degree = int(degree)
        piece = self.graded_piece(degree)
        component = piece(component)
        if degree < 0:
            return self.zero()
        if degree > 1:
            return self(component.underlying_element())
        coordinates = piece.framing_morphism().lift(component)
        labels = self.degree_basis(degree)
        match (degree, self.word_flavor()):
            case (0, "tensor"):
                return self({self.basis_label(0, labels(lambda _: None)): coordinates(0)})
            case (0, "symmetric"):
                return self({self.basis_label(0, labels.from_multiplicities({})): coordinates(0)})
            case (1, "tensor"):
                return self({self.basis_label(1, labels(lambda _, label=label: label)): coordinates(label) for label in coordinates.support().domain()})
            case (1, "symmetric"):
                return self({self.basis_label(1, labels.from_multiplicities({label: 1})): coordinates(label) for label in coordinates.support().domain()})

    from_graded_piece = from_component

    def homogeneous_component(self, element, degree):
        degree = int(degree)
        coordinates = self._framing_lift(self(element))
        selected = {label: coordinates(label) for label in coordinates.support().domain() if int(label.summand_index()) == degree}
        piece = self.graded_piece(degree)
        match degree:
            case value if value < 0:
                return piece.zero()
            case 0:
                return piece.scalar_multiple(sum(selected.values(), self.base_ring().zero()), piece.module_generator(0))
            case 1:
                def source_label(label):
                    inner = label.summand_element()
                    return inner.component(0) if self.word_flavor() == "tensor" else next(iter(inner.support()))
                return piece.linear_combination({source_label(label): value for label, value in selected.items()})
            case _:
                return piece(self(selected).underlying_element())

    def homogeneous_components(self, element):
        degrees = finite_ordered_set(
            tuple(
                self.grading_monoid()(int(label.summand_index()))
                for label in self._framing_lift(self(element)).support().domain()
            )
        )
        return finite_indexed_family(
            degrees,
            lambda degree: self.homogeneous_component(element, degree),
            name="Nonzero homogeneous word components",
        )

    def from_components(self, components):
        return sum((self.from_component(degree, component) for degree, component in components.items()), self.zero())

    def homogeneous_degree(self, element):
        degrees = {
            int(label.summand_index())
            for label in self._framing_lift(self(element)).support().domain()
        }
        if len(degrees) != 1:
            raise ValueError(
                f"{element} has no degree in {self}: it is not a nonzero homogeneous element, since its "
                f"components lie in degrees {sorted(degrees)}"
            )
        return self.grading_monoid()(next(iter(degrees)))

    def degree_on_module_generator(self, element):
        degrees = {
            int(label.summand_index())
            for label in self._framing_lift(self(element)).support().domain()
        }
        assert len(degrees) == 1, (
            f"{element} is not a generator of {self}: a generator is a single word and has one "
            f"degree, but its components lie in degrees {sorted(degrees)}"
        )
        return self.grading_monoid()(next(iter(degrees)))

    def degree_index_set(self):
        return self.grading_monoid()

    def _repr_(self):
        return f"Module of {self.word_flavor()} words on {self.generating_module()}"


class _WordDegreeModule:
    def __init__(self, word_module, word_degree, **rest):
        self._word_module = word_module
        self._word_degree = word_degree
        classes = word_module.underlying_set()
        subset = OwnedSets().condition_set(classes, lambda value: all(
            int(label.summand_index()) == word_degree
            for label in value._representative.support().domain()
        ))
        cover = word_module.base_ring().free_module(word_module.degree_basis(word_degree))
        super().__init__(
            underlying_set=subset, addition=classes.add, zero=classes.zero(),
            negation=classes.negate, scalar_action=classes.scale,
            module_generating_set=cover.module_generating_set(),
            module_generator_function=lambda label: self(
                word_module.module_generator(
                    word_module.basis_label(word_degree, label)
                ).underlying_element()
            ),
            framing_source=cover,
            **rest,
        )

    def degree(self):
        return self._word_degree

    def _element_constructor_(self, value):
        match value:
            case dict():
                return self.linear_combination(value)
            case _:
                return super()._element_constructor_(value)

    def _selected_module_coefficients(self, element):
        coordinates = self._word_module.framing_morphism().lift(self(element).underlying_element())
        return {label.summand_element(): coordinates(label) for label in coordinates.support().domain()}

    def _repr_(self):
        return f"Degree-{self._word_degree} words on {self._word_module.generating_module()}"


@cached_function(key=lambda module, degree: (id(module), degree))
def _word_degree_module(module, degree):
    r"""The homogeneous submodule of an already constructed word module."""
    ring = module.base_ring()
    placements = (
        GeneralModules(ring),
        ModuleSubobjects(ring),
        Modules(ring).Subobjects(module),
    )
    match module.generating_module() in FramedFreeModules(ring):
        case True:
            placements = (*placements, FramedFreeModules(ring))
        case False:
            pass
    category = Cat().meet(placements)
    return _object_of(
        category,
        _engine=(category, _WordDegreeModule, None),
        base_ring=ring, word_module=module, word_degree=degree,
        subobject_ambient=module,
        subobject_inclusion_factory=lambda piece: Modules(ring).Mono(piece, module)._subobject_inclusion(
            lambda label: module.module_generator(module.basis_label(degree, label)),
            lift=lambda element: piece(module(element).underlying_element()),
        ),
    )


def _word_module(presentation, *, extra_categories=(), construction_data=None):
    r"""Construct the module quotient, optionally in a specialized native realization.

    A stronger construction can supply the same private `_engine` datum used
    by `_object_of`; its engine must still construct this quotient module.
    The word presentation and its cover are retained unchanged.
    """
    ring = presentation.base_ring()
    data = dict(construction_data or {})
    category = Cat().meet((
        GeneralModules(ring),
        GradedModules(ring),
        ModulesWithChosenComponentPresentation(ring),
        *extra_categories,
    ))
    engine = data.pop("_engine", (category, _WordModule, _WordModuleElement))
    return _object_of(category, _engine=engine, base_ring=ring, word_presentation=presentation, **data)


@cached_function(key=lambda source, flavor: (id(source), flavor))
def _module_on_word_quotient(source, flavor):
    return _word_module(_WordPresentation(source, flavor))
