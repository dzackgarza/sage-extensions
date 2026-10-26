"""Linear maps between represented modules."""

import logging
from functools import reduce
from inspect import Parameter, isfunction, ismethod, signature
from itertools import product

from sage.categories.map import Map
from sage.categories.morphism import Morphism, SetMorphism

from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoricalArrow,
    _refuse_foreign_arrow,
)
from sage.misc.cachefunc import cached_method
from sage.structure.element import parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    CategoricalIsomorphism,
    _distinct_supercategories,
    _precomposable,
)
from sage.misc.lazy_attribute import lazy_attribute

from sage_extensions.categories.abstract_categories.arrow_categories import CoreMor, _CoreCategory
from sage_extensions.categories.group.magmas import AdditiveGroups
from sage_extensions.categories.rings.ring_foundation import _engine_element, _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    LocalizationRings,
    LocalRings,
    PrincipalIdealDomains,
    OwnedCategoryOverBaseRing,
    OwnedFields,
    OwnedRings,
    _engine_ring,
    _linear_algebra_ring,
    _linear_algebra_element,
    _enumerated_ring_elements,
    _owned_ring,
)
from sage_extensions.categories.sets.cardinals import Cardinalities, aleph0
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    finite_indexed_family,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import (
    EnumeratedSets,
    FiniteSets,
    Sets,
)
from sage_extensions.logic import AtomicProposition, conjunction, negation
from sage_extensions.validation import validator

_LOGGER = logging.getLogger(__name__)


def _has_finite_free_framing(module) -> bool:
    r"""Whether ``module`` is framed, free and finitely generated: an endpoint of a coordinate matrix."""
    from sage_extensions.categories.modules.pure.modules import (
        _coordinate_framed_free_module,
    )

    return _coordinate_framed_free_module(module, module.base_ring())


def _finite_generating_elements(module):
    r"""A finite generating set of ``module``, or ``None`` when none is supplied.

    Used only by module-morphism comparison. Relations are unnecessary for
    comparing already admitted linear maps: linearity extends equality from
    a generating set. Pure tensors of generators generate a tensor product
    by bilinearity (Mathlib TensorProduct.ext). Adding structure preserves
    the supplied unformed module's generating set through its existing coercion.
    No infinite set or point sample is used to infer equality.
    """
    from sage_extensions.categories.modules.pure.modules import TensorProductModules

    ring = module.base_ring()
    match module:
        case _ if module.has_selected_module_resolution() and Cardinalities().lt(
            module.module_generating_set().cardinality(), aleph0
        ) is True:
            return iter(module.module_generators())
        case _ if module in TensorProductModules(ring) and module.tensor_factors().cardinality() == 2:
            left = _finite_generating_elements(module.tensor_factor(0))
            right = _finite_generating_elements(module.tensor_factor(1))
            if left is None or right is None:
                return None
            return (module.pure_tensor(x, y) for x, y in product(left, right))
        case _ if module.unformed_module() is not module:
            elements = _finite_generating_elements(module.unformed_module())
            return None if elements is None else map(module, elements)
        case _:
            return None


def _integral_preimage_solver(morphism, ring):
    r"""Factor a finite free morphism once and return its exact preimage solver.

    For ``f: F(S) -> F(T)`` the solver takes the coordinates of ``t`` in
    ``F(T)`` and returns ``x`` in ``F(S)`` with ``f(x) = t``, or ``None``
    when ``t`` is not in the image: the Smith form ``D = U f V`` reduces
    the equation to ``d_i y_i = (U t)_i``, solvable exactly when each
    ``d_i`` divides its right-hand side, and then ``x = V y``.

    Over an exact field, use maintained matrix rank and linear solving
    directly. Equality of the coefficient and augmented ranks decides
    consistency. No solver exception is interpreted as inconsistency;
    undecided exact scalar operations propagate. Represented RR uses RR
    coefficients during elimination, retaining its equality protocol.
    """

    from sage_extensions.categories.modules.pure.modules import MatrixSpaces

    assert ring in OwnedRings(), f"cannot solve a linear system integrally over {ring}: the coefficients must lie in a ring, but {ring} is not a ring"
    assert morphism.parent() in MatrixSpaces(ring), f"cannot solve f(x) = t integrally for f = {morphism} over {ring}: f must be a map of finite free {ring}-modules with chosen bases, but it lies in {morphism.parent()}"

    if ring in OwnedFields() and ring.is_exact() is True:
        from sage_extensions.rings.real import RR

        if ring is RR:
            return _represented_real_preimage_solver(morphism)
        from sage.modules.free_module_element import vector
        from sage_extensions.categories.modules.pure.modules import _engine_matrix

        backend = _engine_matrix(morphism).change_ring(_linear_algebra_ring(ring))
        field = backend.base_ring()
        rank = backend.rank()
        source_labels = tuple(morphism.domain().module_generating_set())

        def solve_field(target):
            values = tuple(ring(value) for value in target)
            assert len(values) == backend.nrows(), (
                "a linear-system target must have one coordinate per codomain basis vector"
            )
            right_hand_side = vector(field, tuple(_linear_algebra_element(ring, value) for value in values))
            if backend.augment(right_hand_side).rank() != rank:
                return None
            solution = backend.solve_right(right_hand_side)
            return morphism.domain().linear_combination({
                label: _owned_engine_element(ring, coefficient)
                for label, coefficient in zip(source_labels, solution, strict=True)
            })

        return solve_field

    smith_data = morphism.smith_form()
    smith = smith_data["diagonal"]
    left = smith_data["left_change"]
    right = smith_data["right_change"]
    # smith_form() names the two maps by the sides of the presentation
    # square: left is the codomain change applied to the target, while
    # right is the inverse domain change applied after diagonal solving.
    target_labels = left.domain().module_generating_set()
    shifted_labels = left.codomain().module_generating_set()
    diagonal_rows = smith.codomain().module_generating_set()
    diagonal_columns = smith.domain().module_generating_set()
    width = int(diagonal_columns.cardinality())

    def solve(target):
        target_values = tuple(ring(value) for value in target)
        assert len(target_values) == int(target_labels.cardinality()), (
            f"cannot solve f(x) = t for t = {target}: t must have {target_labels.cardinality()} entries, "
            f"one per generator of the codomain of f, but it has {len(target_values)}"
        )
        target_vector = left.domain().linear_combination({label: target_values[position] for position, label in enumerate(target_labels) if target_values[position]})
        shifted_vector = left(target_vector)
        shifted_coordinates = shifted_vector.to_vector()

        solution = [ring.zero()] * width
        for index, shifted_label in enumerate(shifted_labels):
            value = shifted_coordinates(shifted_label)
            divisor = smith.matrix_entry(diagonal_rows[index], diagonal_columns[index]) if index < min(int(shifted_labels.cardinality()), width) else ring.zero()
            if divisor == 0:
                if value != 0:
                    return None
                continue
            if value not in ring.ideal(divisor):
                return None
            solution[index] = ring(value / divisor)

        normalized_solution = right.domain().linear_combination(
            {label: solution[position] for position, label in enumerate(right.domain().module_generating_set()) if solution[position]}
        )
        return right(normalized_solution)

    return solve


def _represented_real_preimage_solver(morphism):
    r"""Solve a finite real linear system with only decided nonzero pivots.

    Row operations retain owned real coefficients, including an undecided
    zero coefficient in the right-hand side. An unresolved pivot or
    consistency equation is a computational frontier, not nonmembership.
    """
    ring = morphism.domain().base_ring()
    from sage_extensions.categories.modules.pure.modules import _represented_real_rref

    source_labels = tuple(morphism.domain().module_generating_set())
    target_labels = tuple(morphism.codomain().module_generating_set())
    coefficients = tuple(
        tuple(morphism.matrix_entry(row, column) for column in source_labels)
        for row in target_labels
    )

    def solve(target):
        values = tuple(ring(value) for value in target)
        assert len(values) == len(target_labels), (
            "a linear-system target must have one coordinate per codomain basis vector"
        )
        rows, pivots = _represented_real_rref(
            tuple(tuple(row) + (value,) for row, value in zip(coefficients, values, strict=True)),
            len(source_labels),
            ring,
        )
        for row in rows[len(pivots):]:
            status = row[-1] == ring.zero()
            assert status is True or status is False, (
                "the real linear-system consistency equation is undecided"
            )
            if status is False:
                return None
        solution = [ring.zero()] * len(source_labels)
        for row, column in enumerate(pivots):
            solution[column] = rows[row][-1]
        return morphism.domain().linear_combination(
            dict(zip(source_labels, solution, strict=True))
        )

    return solve


def _integral_preimage_positional_solver(morphism, ring):
    r"""Factor ``f`` once and return its positional integral preimage solver."""
    element_solver = _integral_preimage_solver(morphism, ring)

    def solve(target):
        original_solution = element_solver(target)
        if original_solution is None:
            return None
        coordinates = original_solution.to_vector()
        return tuple(
            coordinates(label)
            for label in original_solution.parent().module_generating_set()
        )

    return solve


def _solve_preimage_integrally(morphism, target, ring):
    r"""Return the coordinates of ``x`` with ``f(x) = t`` over a PID, or ``None``."""
    return _integral_preimage_positional_solver(morphism, ring)(target)


def _scalar_linearity_generating_scalars(ring):
    r"""Return scalars whose linearity decides linearity over all of ``ring``.

    Let ``f`` be additive.  The scalars ``r`` with ``f(rx)=rf(x)`` for every
    ``x`` contain ``1`` and are closed under sums, negatives and products, so
    they form a subring of ``R``.  Checking a generating set of ``R`` as a ring
    therefore decides scalar-linearity over the whole of ``R``, and additivity
    already supplies the image of ``ZZ``.

    A finite ring is its own generating set.  A framed algebra over a finite
    ring is generated by that ring together with its chosen algebra generators,
    which is what decides an infinite ring such as ``GF(q)[x]``.  Returns
    ``None`` where neither presentation is represented.
    """
    elements = _enumerated_ring_elements(ring)
    if elements is not None:
        return elements

    base = ring.base_ring()
    if base is ring or not ring.is_framed_algebra():
        return None
    base_elements = _enumerated_ring_elements(base)
    if base_elements is None:
        return None
    labels = ring.algebra_generating_set()
    if not labels.cardinality().is_finite():
        return None
    return tuple(ring(scalar) for scalar in base_elements) + tuple(ring.algebra_generator(label) for label in labels)


class ModuleMorphismMethods:
    r"""The linear extension of a function on a chosen module framing.

    Construction data: the images of the framing of the domain, or an exact
    elementwise map when the domain is unframed or the map is stated on
    elements; optionally a selected lift through the map; and, for a map
    ``S tensor_R f`` constructed by scalar extension along ``R -> S``, the
    morphism ``f`` and the scalar-extension functor it is the image under.

    An arrow built by an operation of its Mor module (a pointwise sum,
    negative or scalar multiple, a composite, the zero map, a multiple of
    the identity, the universal arrows of products and equalizers) also
    takes ``linearity_premises``: the family of linear maps from which the
    operation builds it.  ``Hom_R(M, N)`` is closed under these operations,
    so the arrow is linear when every premise is, and the empty family
    means the module axioms alone make it linear.  Only those operations
    supply the family; the public constructors take none.
    """

    _scalar_extension_of = None
    _scalar_extension_functor = None
    _lift_function = None
    _linearity_premises = None

    def _initialize_lower_arrow(self, parent) -> None:
        domain = parent.domain()
        ring = domain.base_ring()
        match ring.is_commutative():
            case True:
                # The scalar map is a ring homomorphism, so its identity lives in
                # ``Mor_Ring``.  The strongest Mor of ``ring`` can have arrows that
                # build module maps again (algebra maps of ``QQ``), which regresses.
                scalar_map = ring.Mor(ring, category=OwnedRings()).identity()
                super().__init__(
                    parent,
                    scalar_map,
                    evaluator=self._call_,
                )
            case _:
                super().__init__(parent, self._call_)

    def _elementwise_linearity_derivation(self):
        r"""Return the construction-derived linearity decision, or ``None``.

        A linear map read into another Mor with the same endpoints keeps the
        decision of that map.  Ordinary elementwise callables have no
        derivation.  No caller selects a derivation with a string or boolean
        flag.
        """
        source_morphism = self._source_module_morphism
        if source_morphism is not None:
            return source_morphism.linearity_decision()
        return None

    def _generator_image_linearity_derivation(self):
        r"""The linearity decision of a map given by images of a chosen generating set.

        Its linear extension is linear by construction once the images kill
        the selected relations of the domain, so those relations are checked.
        """
        return self._check_selected_domain_relations()

    def _selected_lift_derivation(self):
        r"""Return whether a supplied lift is exact by construction, or ``None``.

        A caller-supplied Python function is not evidence that ``None`` means
        an element lies outside the image.  Constructor-owned subobject maps
        override this hook when their selected lift is part of the subobject
        datum itself.
        """
        return None

    def __init__(
        self,
        parent,
        images,
        *,
        elementwise=False,
        scalar_extension_of=None,
        scalar_extension_functor=None,
        lift=None,
        linearity_premises=None,
    ) -> None:
        self._initialize_lower_arrow(parent)
        assert (scalar_extension_of is None) == (scalar_extension_functor is None), (
            f"cannot construct the base change {scalar_extension_of} along {scalar_extension_functor}: "
            "a map S tensor_R f must be given together with both f and the scalar-extension functor"
        )
        self._scalar_extension_of = scalar_extension_of
        self._scalar_extension_functor = scalar_extension_functor
        self._lift_function = lift
        self._linearity_premises = linearity_premises
        self._source_module_morphism = None
        self._element_function = None
        domain = self.domain()
        codomain = self.codomain()
        match images:
            case ModuleMorphismMethods() if (
                not elementwise
                and images.domain() is domain
                and images.codomain() is codomain
                and images.has_module_generator_images()
            ):
                # A linear map is its generator images: keep them rather than
                # re-evaluating the map on every element (``OWN-22``).
                images = images.module_generator_morphism()
            case Morphism() | CategoricalArrow() if images.domain() is domain and images.codomain() is codomain:
                source_morphism = images
                if isinstance(source_morphism, ModuleMorphismMethods):
                    self._source_module_morphism = source_morphism
                images = lambda element: source_morphism(element)
                elementwise = True
            case _:
                pass
        if elementwise or not domain.has_selected_module_resolution():
            if not callable(images):
                raise TypeError(f"cannot define a linear map {domain} -> {codomain} from {images!r}: {domain} has no chosen generators, so the map must be given as a function on elements")
            self._element_function = images
            self._generator_image = None
            self._generator_morphism = None
            return
        labels = self.domain().module_generating_set()
        set_mor = Sets().Mor(labels, self.codomain())
        if isinstance(images, (SetMorphism, CategoricalArrow)):
            if images.domain() is not labels or images.codomain() is not self.codomain():
                raise ValueError(f"cannot define a linear map {domain} -> {codomain} from the generator images {images}: they must be a map {labels} -> {codomain}, but they are a map {images.domain()} -> {images.codomain()}")
            self._generator_images = indexed_family(
                labels,
                images,
                name="Generator images",
            )
            self._generator_image = self._generator_images.value
            self._generator_morphism = images
        elif isinstance(images, IndexedFamily):
            source_indices = images.index_set()

            def image_at(label):
                return images[source_indices(label)]

            self._generator_images = indexed_family(
                labels,
                image_at,
                name="Generator images",
            )
            self._generator_image = self._generator_images.value
            self._generator_morphism = set_mor(self._generator_image)
        elif isinstance(images, dict):
            size = labels.cardinality()
            if not size.is_finite():
                raise TypeError(f"cannot define a linear map {domain} -> {codomain} by a dictionary of generator images: {domain} has infinitely many generators {labels}; give the images as a function or an indexed family")

            def generator_label(key):
                # A key is a label of the generating set S, or the module
                # generator it names: the image of that label under S -> M.
                match element_parent(key) is domain:
                    case True:
                        named = [label for label in labels if domain.module_generator(label) == key]
                        assert named and all(label == named[0] for label in named), (
                            f"cannot define a linear map {domain} -> {codomain}: {key} is not exactly one "
                            f"of the module generators of {domain}, so it names no generator image"
                        )
                        return named[0]
                    case False:
                        return labels(key)

            if labels in EnumeratedSets():
                ranking = labels.ranking_map()
                missing_value = object()
                normalized_values = [missing_value] * int(size.finite_value())
                for label, value in images.items():
                    normalized_label = generator_label(label)
                    normalized_values[int(ranking(normalized_label))] = value
                missing = [
                    label
                    for position, label in enumerate(labels)
                    if normalized_values[position] is missing_value
                ]
                if missing:
                    raise ValueError(f"cannot define a linear map {domain} -> {codomain}: the images of the generators {missing} of {domain} are not given")
                self._generator_images = indexed_family(
                    labels,
                    lambda label: normalized_values[int(ranking(label))],
                    name="Generator images",
                )
            else:
                normalized_images = {}
                for label, value in images.items():
                    normalized_label = generator_label(label)
                    normalized_images[normalized_label] = value
                missing = [label for label in labels if label not in normalized_images]
                if missing:
                    raise ValueError(f"cannot define a linear map {domain} -> {codomain}: the images of the generators {missing} of {domain} are not given")
                self._generator_images = indexed_family(
                    labels,
                    normalized_images.__getitem__,
                    name="Generator images",
                )
            self._generator_image = self._generator_images.value
            self._generator_morphism = set_mor(self._generator_image)
        elif isinstance(images, (tuple, list)):
            values = tuple(images)
            size = labels.cardinality()
            if not size.is_finite():
                raise TypeError(f"cannot define a linear map {domain} -> {codomain} by a list of generator images: {domain} has infinitely many generators {labels}; give the images as a function or an indexed family")
            if len(values) != int(size.finite_value()):
                raise ValueError(f"cannot define a linear map {domain} -> {codomain}: {domain} has {size} generators, but {len(values)} images were given")
            if labels not in EnumeratedSets():
                raise TypeError(f"cannot define a linear map {domain} -> {codomain} by a list of generator images: the generators {labels} of {domain} have no enumeration order, so give the images as a dictionary")
            self._generator_images = indexed_family(
                labels,
                lambda label: values[int(labels.ranking_map()(label))],
                name="Generator images",
            )
            self._generator_image = self._generator_images.value
            self._generator_morphism = set_mor(self._generator_image)
        elif callable(images):
            self._generator_images = indexed_family(
                labels,
                images,
                name="Generator images",
            )
            self._generator_image = self._generator_images.value
            self._generator_morphism = set_mor(self._generator_image)
        else:
            raise TypeError(f"cannot define a linear map {domain} -> {codomain} from {images!r}: give the images of the generators of {domain} as a dictionary, list, indexed family or function")

    @validator
    def validate_linearity(self) -> None:
        r"""Raise ``ValueError`` unless this map is known to be linear (``OWN-22``).

        A map given by generator images is linear exactly when it sends the
        relations of the chosen presentation to zero; a map given on elements
        is decided in the regimes :meth:`linearity_decision` names.
        """
        decision = self.linearity_decision()
        if decision is not True:
            raise ValueError(
                f"the map {self.domain()} -> {self.codomain()} is not known to be "
                f"{self.domain().base_ring()}-linear (its linearity decision is {decision})"
            )

    @validator
    def validate_lift(self) -> None:
        r"""Raise ``ValueError`` when the selected lift is witnessed not to be a section (``OWN-22``)."""
        match self._lift_function:
            case None:
                return
            case _:
                if self._selected_lift_derivation() is False:
                    raise ValueError(
                        f"the given lift through {self.domain()} -> {self.codomain()} is not a section of it: "
                        f"its own construction shows it fails f(lift(y)) = y"
                    )
                self._refute_invalid_selected_lift_when_decidable()

    def _refute_invalid_selected_lift_when_decidable(self) -> None:
        r"""Reject witnessed section-equation failures of a selected lift.

        This is a refutation pass, not a proof that an arbitrary lift callback
        is exact.  On a represented finite codomain every returned candidate is
        checked; otherwise zero is still a sound probe.  A callback that passes
        these checks remains unresolved unless its constructor supplies a lift
        derivation.
        """
        custom = self._lift_function
        if custom is None:
            return
        codomain = self.codomain()
        ring = codomain.base_ring()
        targets = None
        if codomain in FiniteSets():
            from sage_extensions.categories.modules.pure.modules import Modules

            if codomain in EnumeratedSets() or codomain in Modules(ring).FinitelyPresented().Torsion():
                targets = tuple(codomain)
        if targets is None:
            probes = [codomain.zero()]
            generators = _finite_generating_elements(codomain)
            if generators is not None:
                probes.extend(generators)
            targets = tuple(probes)
        for target in targets:
            candidate = custom(target)
            if candidate is None:
                continue
            candidate = self.domain()(candidate)
            section_equation = self(candidate) == target
            if section_equation is False:
                raise ValueError(f"the given lift through {self.domain()} -> {codomain} is not a section: for y = {target} it returns x = {candidate}, but f(x) != y")

    @cached_method
    def linearity_decision(self):
        r"""Return ``True`` when linearity is established, otherwise the proposition ``is_linear(f)``.

        Computed on the first request, not at construction (``OWN-22``).  A
        computation that refutes linearity raises ``ValueError`` naming the
        witness (a relation not sent to zero, or elements ``x, y`` with
        ``f(x + y) != f(x) + f(y)``).
        Generator-image maps are linear extensions after their source
        relations are checked.  Elementwise maps are either decided in an
        effective regime, derived by a named universal construction, or retain
        the unresolved hypothesis explicitly.  An arrow built by a Mor
        operation from a family of linear maps has a sufficient construction
        proof when every premise is established.  Undecided or refuted
        premises do not decide the resulting map's linearity: its own
        generator relations or elementwise diagnostic are used instead.
        """
        match self._linearity_premises:
            case None:
                pass
            case premises:
                try:
                    construction_decision = _combined_linearity_decision(premises)
                except ValueError:
                    # A refuted input law does not refute the output law.
                    pass
                else:
                    if construction_decision is True:
                        return True
        match self._element_function:
            case None:
                return self._generator_image_linearity_derivation()
            case _:
                derivation = self._elementwise_linearity_derivation()
                match derivation:
                    case None:
                        return self._verify_elementwise_linearity_when_decidable()
                    case _:
                        return derivation

    def _require_established_linearity(self, operation: str) -> None:
        r"""Require that this map is known to be linear, as ``operation`` needs."""
        if self.linearity_decision() is not True:
            raise ValueError(
                f"{operation} requires a linear map, but the map {self.domain()} -> {self.codomain()} was given as a "
                f"function on elements and is not known to be {self.domain().base_ring()}-linear"
            )

    def _verify_elementwise_linearity_when_decidable(self):
        r"""Check an elementwise callable exactly in represented decidable regimes.

        A Python callable does not carry a proof of linearity.  When the source
        module is finite and enumerable, additivity is decidable by exhaustive
        verification, and the scalars an additive map commutes with form a
        subring, so a ring generating set decides scalar-linearity over all of
        ``R``.  Over ``ZZ`` that generating set is empty: every additive-group
        map is automatically ``ZZ``-linear.  Outside such regimes the linearity decision is the
        proposition ``is_linear(f)``; a DEBUG diagnostic records that no
        exhaustive verification was available.

        A map given by images of a framing is not reached here at all.  Its
        linear extension is linear by construction, and the relations of the
        chosen presentation are what has to be checked instead.
        """
        from sage_extensions.categories.modules.pure.modules import Modules

        function = self._element_function
        if function is None:
            return True

        domain = self.domain()
        codomain = self.codomain()
        source_elements = self._finite_source_elements_for_verification()
        if source_elements is not None:
            return self._verify_elementwise_on_finite_source(source_elements)

        ring = domain.base_ring()
        match domain:
            case _ if domain.is_finite() is not True:
                self._check_elementwise_zero()
                self._refute_elementwise_linearity_on_selected_generators()
                _LOGGER.debug(
                    "Elementwise module morphism %s -> %s accepted without exhaustive linearity verification; the source is not represented as finite",
                    domain,
                    codomain,
                )
                return AtomicProposition("is_linear", self)
            case _ if domain in EnumeratedSets() or domain in Modules(ring).FinitelyPresented().Torsion():
                return self._verify_elementwise_on_finite_source(tuple(domain))
            case _:
                self._check_elementwise_zero()
                _LOGGER.debug(
                    "Elementwise module morphism %s -> %s accepted without exhaustive linearity verification; finite source has no represented enumeration",
                    domain,
                    codomain,
                )
                return AtomicProposition("is_linear", self)

    def _refute_elementwise_linearity_on_selected_generators(self) -> None:
        r"""Reject witnessed law failures without promoting finite probes to a proof.

        A finite framing does not decide an arbitrary callable on an infinite
        module.  It does, however, supply sound counterexamples when additivity
        already fails on two selected generators, or scalar-linearity fails on
        a represented ring generator and one selected module generator.  Passing
        these probes leaves linearity undecided.
        """
        generators = _finite_generating_elements(self.domain())
        if generators is None:
            return
        generators = tuple(generators)
        function = self._element_function
        for left in generators:
            for right in generators:
                additive = function(left + right) == function(left) + function(right)
                if additive is False:
                    raise ValueError(f"the given map {self.domain()} -> {self.codomain()} is not additive: f(x + y) != f(x) + f(y) for x = {left}, y = {right}")

        scalars = _scalar_linearity_generating_scalars(self.domain().base_ring())
        if scalars is None:
            return
        for scalar in scalars:
            for generator in generators:
                scalar_linear = (
                    function(self.domain().scalar_multiple(scalar, generator))
                    == self.codomain().scalar_multiple(scalar, function(generator))
                )
                if scalar_linear is False:
                    raise ValueError(f"the given map {self.domain()} -> {self.codomain()} is not {self.domain().base_ring()}-linear: f(r x) != r f(x) for r = {scalar}, x = {generator}")

    def _finite_source_elements_for_verification(self):
        r"""Enumerate a finitely generated module over a finite ring via its framing.

        Distinct scalar combinations of the framing of a free module are
        distinct elements; over a quotient of a free module they can coincide
        and are listed once.
        """
        from sage_extensions.categories.modules.framed.framed_free_modules import (
            FramedFreeModules,
        )
        domain = self.domain()
        ring = domain.base_ring()
        if not domain.has_selected_module_resolution():
            return None
        label_set = domain.module_generating_set()
        if not label_set.cardinality().is_finite():
            return None
        labels = tuple(label_set)
        if not labels:
            return (domain.zero(),)
        scalars = _enumerated_ring_elements(ring)
        if scalars is None:
            return None
        combinations = (
            domain.linear_combination({label: coefficient for label, coefficient in zip(labels, coefficients, strict=True) if coefficient != 0})
            for coefficients in product(scalars, repeat=len(labels))
        )
        match domain:
            case _ if domain in FramedFreeModules(ring):
                return tuple(combinations)
            case _:
                elements = []
                for element in combinations:
                    duplicate = False
                    for previous in elements:
                        equal = element == previous
                        if equal is True:
                            duplicate = True
                            break
                        if equal is not False:
                            return None
                    if not duplicate:
                        elements.append(element)
                return tuple(elements)

    def _verify_elementwise_on_finite_source(self, source_elements):
        function = self._element_function
        domain = self.domain()
        codomain = self.codomain()
        ring = domain.base_ring()
        zero = domain.zero()
        undecided = AtomicProposition("is_linear", self)

        decision = True
        zero_holds = function(zero) == codomain.zero()
        if zero_holds is False:
            raise ValueError(f"the given map {domain} -> {codomain} is not linear: it sends 0 to {function(zero)}, not to 0")
        if zero_holds is not True:
            decision = undecided
        for left in source_elements:
            for right in source_elements:
                additive = function(left + right) == function(left) + function(right)
                if additive is False:
                    raise ValueError(f"the given map {domain} -> {codomain} is not additive: f(x + y) != f(x) + f(y) for x = {left}, y = {right}")
                if additive is not True:
                    decision = undecided

        from sage.rings.integer_ring import ZZ as SageZZ

        if _engine_ring(ring) is SageZZ:
            return decision

        scalars = _scalar_linearity_generating_scalars(ring)
        if scalars is None:
            _LOGGER.debug(
                "Elementwise map %s -> %s is exhaustively additive on its finite source, "
                "but %s has no represented ring generating set, so scalar-linearity was "
                "not exhaustively verified",
                domain,
                codomain,
                ring,
            )
            return undecided
        for scalar in scalars:
            for element in source_elements:
                scalar_linear = (
                    function(domain.scalar_multiple(scalar, element))
                    == codomain.scalar_multiple(scalar, function(element))
                )
                if scalar_linear is False:
                    raise ValueError(f"the given map {domain} -> {codomain} is not {ring}-linear: f(r x) != r f(x) for r = {scalar}, x = {element}")
                if scalar_linear is not True:
                    decision = undecided
        return decision

    def _check_elementwise_zero(self) -> None:
        r"""Refute linearity of a map that does not send zero to zero."""
        zero_holds = self._element_function(self.domain().zero()) == self.codomain().zero()
        if zero_holds is False:
            raise ValueError(f"the given map {self.domain()} -> {self.codomain()} is not linear: it does not send 0 to 0")

    def _check_selected_domain_relations(self):
        if self._element_function is not None:
            return self.linearity_decision()
        domain = self.domain()
        from sage_extensions.categories.modules.framed.framed_free_modules import (
            FramedFreeModules,
        )

        if domain in FramedFreeModules(domain.base_ring()):
            return True
        relations = domain._selected_relation_morphism()
        undecided = AtomicProposition("is_linear", self)
        if relations is None:
            return undecided
        zero = self.codomain().zero()
        decision = True
        for relation_label in relations.domain().module_generating_set():
            relation = relations(relations.domain().module_generator(relation_label)).to_vector()
            relation_image = self._linear_combination_of_generator_images(
                domain.framing_source()(relation.parent()._selected_module_coefficients(relation))
            )
            relation_holds = relation_image == zero
            if relation_holds is False:
                raise ValueError(f"the generator images do not define a linear map {domain} -> {self.codomain()}: the relation {relation} of {domain} is sent to {relation_image}, not to 0")
            if relation_holds is not True:
                decision = undecided
        return decision

    def has_module_generator_images(self) -> bool:
        r"""Return whether this map was given by the images of the chosen generators of its domain."""
        return self._generator_morphism is not None

    def module_generator_morphism(self):
        assert self._generator_morphism is not None, (
            f"the map {self.domain()} -> {self.codomain()} has no generator images: it was given as a function on elements, not by images of chosen generators of {self.domain()}"
        )
        return self._generator_morphism

    def module_generator_images(self):
        assert self._generator_morphism is not None and self._generator_images is not None, (
            f"the map {self.domain()} -> {self.codomain()} has no generator images: it was given as a function on elements, not by images of chosen generators of {self.domain()}"
        )
        return self._generator_images

    def _pointwise_mor(self):
        r"""The Mor holding the pointwise sums and negatives of this arrow.

        It is this arrow's own Mor when that Mor is an additive group.  A Mor
        that is not (isometries, embeddings, automorphisms) does not contain
        ``f + g`` or ``-f``; they lie in ``Hom_R(M, N)`` of the endpoints.
        """
        parent = self.parent()
        match parent:
            case _ if parent in AdditiveGroups():
                return parent
            case _:
                domain = self.domain()
                return domain.module_category().Mor(domain, self.codomain())

    def __add__(self, other):
        r"""Return the pointwise sum ``(f + g)(m) = f(m) + g(m)``.

        ``other`` must already be an arrow of the Mor that holds the sum,
        or a scalar of an endomorphism ring. The explicit map constructor
        can admit a new linearity hypothesis; arithmetic does not do so.
        """
        parent = self._pointwise_mor()
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
        return parent.element_class(
            parent,
            lambda element: self(element) + summand(element),
            elementwise=True,
            linearity_premises=(self, summand),
        )

    def __neg__(self):
        r"""Return the pointwise negative ``(-f)(m) = -f(m)``."""
        parent = self._pointwise_mor()
        from sage_extensions.categories.group.additive_mors import _scalar_identity_coefficient

        scalar = _scalar_identity_coefficient(self, parent)
        if scalar is not None:
            return parent._scalar_identity(-scalar)
        return parent.element_class(
            parent,
            lambda element: -self(element),
            elementwise=True,
            linearity_premises=(self,),
        )

    def __sub__(self, other):
        r"""Return the pointwise difference ``f - g = f + (-g)``."""
        parent = self._pointwise_mor()
        if other in parent:
            return self + (-parent(other))
        if parent.domain() is parent.codomain() and other in parent.base_ring():
            return self + parent._scalar_identity(-parent.base_ring()(other))
        return NotImplemented

    def _richcmp_(self, other, op):
        r"""Compare admitted linear maps on an available finite spanning family.

        A missing finite family, an undecided value comparison, or a linearity
        that is not established answers the proposition ``equal(f, g)``;
        neither failed normalization nor a finite sample disproves equality.
        """
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if element_parent(other) is not self.parent():
            return op == op_NE
        if self is other:
            return op == op_EQ
        from sage_extensions.categories.group.additive_mors import _scalar_identity_coefficient

        left, right = _scalar_identity_coefficient(self, self.parent()), _scalar_identity_coefficient(other, self.parent())
        if left is not None and right is not None and (left == right) is True:
            return op == op_EQ
        undecided = AtomicProposition("equal", self, other)
        elements = _finite_generating_elements(self.domain())
        if elements is None:
            return undecided if op == op_EQ else negation(undecided)
        comparisons = tuple(self(element) == other(element) for element in elements)
        established_linear = (
            self.linearity_decision() is True
            and other.linearity_decision() is True
        )
        match (
            any(answer is False for answer in comparisons),
            all(answer is True for answer in comparisons),
            established_linear,
        ):
            case (True, _, _):
                equal = False
            case (_, True, True):
                equal = True
            case _:
                equal = undecided
        return equal if op == op_EQ else negation(equal)

    def __hash__(self) -> int:
        # Equality is decided within one Mor, whatever class realizes each
        # arrow, so equal arrows share the hash of their Mor.
        return hash(id(self.parent()))

    def __rmul__(self, actor):
        # A specialized right operand such as a module embedding gets reflected
        # multiplication before Python tries the less-specialized left
        # ModuleMorphism.__mul__.  In that case the operation is composition,
        # not scalar multiplication.  Delegate to the left morphism so the
        # ordinary endpoint check and composition constructor remain the one
        # owner of the operation.
        if isinstance(actor, (Morphism, CategoricalArrow)) and _precomposable(actor, self):
            return actor.__mul__(self)
        # A scalar can itself be a morphism when the retained coefficient
        # ring is an endomorphism ring. Noncomposable map-valued scalars
        # therefore keep the ordinary scalar-action ingress.
        return self.parent().scalar_multiple(actor, self)

    def _lmul_(self, scalar):
        return self.parent().scalar_multiple(scalar, self)

    def _rmul_(self, scalar):
        return self._lmul_(scalar)

    def _acted_upon_(self, actor, self_on_left):
        r"""Use the canonical pointwise scalar action of the Mor module."""
        _ = self_on_left
        match actor:
            case _ if actor in self.parent().base_ring():
                return self.parent().scalar_multiple(actor, self)
            case _:
                return None

    def _linear_combination_of_generator_images(self, coordinates):
        r"""Evaluate ``sum_s a(s) f(m_s)`` for ``a`` in the framing source ``F_R(S)`` of the domain.

        Owned ring facades deliberately do not require Sage's coercion model
        to identify native coefficient elements with the facade parent.  Raw
        ``scalar * element`` therefore bypasses the module abstraction.  The
        linear extension is intrinsic: apply the codomain's represented scalar
        action directly to each selected generator image and add the results.
        The retained finite coefficient family suffices; evaluating this sum
        does not require deciding which of its coefficients vanish. No
        codomain framing is involved.
        """
        codomain = self.codomain()
        ring = codomain.base_ring()
        coefficients = coordinates.parent()._selected_module_coefficients(coordinates)
        return sum(
            (
                codomain.scalar_multiple(
                    ring(coefficient),
                    self._generator_image(source_label),
                )
                for source_label, coefficient in coefficients.items()
            ),
            codomain.zero(),
        )

    def _call_(self, element):
        if element.parent() is not self.domain():
            element = self.domain()(element)
        if self._element_function is not None:
            image = self._element_function(element)
            return image if image.parent() is self.codomain() else self.codomain()(image)
        return self._linear_combination_of_generator_images(
            self.domain()._framing_lift(element)
        )

    def alternating_extension(self):
        r"""Extend this linear map through the exterior-algebra universal property."""
        from sage_extensions.categories.algebras.power_algebras import (
            _alternating_extension,
        )

        return _alternating_extension(self)

    @cached_method
    def tensor_square_morphism(self):
        r"""Return ``f tensor f: M tensor_R M -> N tensor_R N`` for this R-linear map.

        R is commutative. The exact source and target are the selected module
        tensor products, also used by algebra multiplication classifiers;
        neither module needs an algebra multiplication. The existing tensor
        product map supplies the induced arrow on those endpoints.
        """
        from sage_extensions.categories.modules.pure.modules import Modules
        from sage_extensions.categories.rings.ring_foundation import OwnedRings

        ring = self.domain().base_ring()
        assert ring in OwnedRings().Commutative(), (
            f"the tensor square of {self} as a map of left {ring}-modules needs "
            "commutative coefficients for this tensor construction"
        )
        modules = Modules(ring)
        return self.tensor_product_map(
            self,
            source=modules.tensor_product((self.domain(), self.domain())),
            target=modules.tensor_product((self.codomain(), self.codomain())),
        )

    def tensor_product_map(self, other, *, source=None, target=None):
        r"""Return the induced map ``self tensor other`` on selected tensor products."""
        from sage_extensions.categories.modules.tensor_products import (
            _tensor_product_morphism,
        )

        return _tensor_product_morphism(
            self,
            other,
            source=source,
            target=target,
        )

    def biproduct_map(self, other, *, source=None, target=None):
        r"""Return the induced map ``self direct-sum other`` on selected biproducts."""
        from sage_extensions.categories.modules.pure.modules import (
            _biproduct_morphism,
        )

        return _biproduct_morphism(
            self,
            other,
            source=source,
            target=target,
        )

    def internal_mor_map(
        self,
        target_map,
        *,
        source_internal_mor=None,
        target_internal_mor=None,
    ):
        r"""Return the internal-Mor map induced by pre- and postcomposition."""
        from sage_extensions.categories.modules.internal_mor import (
            _internal_mor_morphism,
        )

        return _internal_mor_morphism(
            self,
            target_map,
            source_internal_mor=source_internal_mor,
            target_internal_mor=target_internal_mor,
        )

    def stack(self, other):
        r"""Return ``(self,other)`` into the biproduct of the codomains."""
        assert other.domain() is self.domain(), (
            f"cannot form the map into the product from f: {self.domain()} -> {self.codomain()} and "
            f"g: {other.domain()} -> {other.codomain()}: f and g must have the same domain"
        )

        from sage_extensions.categories.modules.pure.modules import Modules

        target = Modules(self.codomain().base_ring()).biproduct(
            (self.codomain(), other.codomain())
        )
        return target.to_product(self, other)

    def scalar_extension_of(self):
        r"""Return ``f`` when this morphism was constructed as ``S tensor_R f``, else ``None``."""
        return self._scalar_extension_of

    def scalar_extension_functor(self):
        r"""Return the functor ``S tensor_R -`` this morphism is the image under, else ``None``."""
        return self._scalar_extension_functor

    def _flat_scalar_extension_ring(self):
        r"""Return ``S`` when this morphism is ``S tensor_R f`` along a flat ``R -> S``, else ``None``.

        A localization is flat over its source, and the adic completion of a
        Noetherian ring is flat over it; those are the scalar extensions whose
        images retain their preimage.
        """
        from sage_extensions.categories.rings.commutative_algebra import (
            AdicCompletions,
        )

        functor = self._scalar_extension_functor
        if functor is None:
            return None
        extended_ring = _owned_ring(functor.ring_map().codomain())
        match extended_ring:
            case _ if extended_ring in AdicCompletions():
                assert extended_ring.is_flat_over_source(), (
                    f"cannot use exactness of completion for {self.domain()} -> {self.codomain()}: "
                    f"the completion {extended_ring} must be flat over its source ring, and it is not known to be"
                )
                return extended_ring
            case _ if extended_ring in LocalizationRings():
                return extended_ring
            case _:
                return None

    @cached_method
    def kernel(self):
        r"""Return ``ker(self)`` as a subobject of the domain.

        Scalar extension along a flat ring map ``R -> S`` is exact, so
        ``ker(S tensor f) = S tensor ker(f)`` with the extended inclusion.  A
        map between localizations of modules along one localization of a
        local ring descends to their numerators by clearing denominators.
        Otherwise a representation of an endpoint computes the kernel.
        """
        self._require_established_linearity("kernel construction")
        from sage_extensions.categories.modules.localizations import (
            LocalizedModules,
        )
        from sage_extensions.categories.modules.framed.fraction_field_quotients import (
            FractionFieldQuotients,
        )
        from sage_extensions.categories.modules.pure.modules import (
            InternalMorModules,
            ModuleSubobjects,
            ModulesWithChosenFinitePresentation,
        )
        from sage_extensions.categories.rings.commutative_algebra import (
            AdicCompletions,
        )

        domain = self.domain()
        codomain = self.codomain()
        extended_ring = self._flat_scalar_extension_ring()
        match extended_ring:
            case None:
                pass
            case _ if extended_ring in AdicCompletions():
                source_morphism = self._scalar_extension_of
                extension = self._scalar_extension_functor
                assert extension(source_morphism.domain()) is domain, (
                    f"kernel of {domain} -> {codomain}: {domain} should be the completion of "
                    f"{source_morphism.domain()}, but {extension} sends it elsewhere"
                )
                source_kernel = source_morphism.kernel()
                extension(source_kernel)
                completed_inclusion = extension(source_kernel.inclusion())
                assert completed_inclusion.codomain() is domain, (
                    f"kernel of {domain} -> {codomain}: the completed inclusion of the kernel should land in "
                    f"{domain}, but lands in {completed_inclusion.codomain()}"
                )
                return completed_inclusion.image()
            case _:
                localization_functor = self._scalar_extension_functor
                source_kernel = self._scalar_extension_of.kernel()
                localized_kernel = localization_functor(source_kernel)
                localized_inclusion = localization_functor(source_kernel.inclusion())
                assert localized_inclusion.codomain() is domain, (
                    f"kernel of {domain} -> {codomain}: the localized inclusion of the kernel should land in "
                    f"{domain}, but lands in {localized_inclusion.codomain()}"
                )
                assert localized_kernel in ModuleSubobjects(domain.base_ring()), (
                    f"kernel of {domain} -> {codomain}: the localization {localized_kernel} of the kernel "
                    f"should be a submodule of {domain}, but it is not"
                )
                assert localized_kernel.inclusion() is localized_inclusion, (
                    f"kernel of {domain} -> {codomain}: the inclusion of the submodule {localized_kernel} "
                    f"is not the localization of the inclusion of the kernel"
                )
                return localized_kernel

        ring = domain.base_ring()
        match domain:
            case _ if (
                ring in LocalRings()
                and domain in LocalizedModules(ring)
                and codomain in LocalizedModules(ring)
                and codomain.localization_functor() is domain.localization_functor()
                and _has_finite_free_framing(domain.numerator_module())
            ):
                functor = domain.localization_functor()
                source_domain = domain.numerator_module()
                source_codomain = codomain.numerator_module()
                labels = tuple(source_domain.module_generating_set())
                images = tuple(self(domain.module_generator(label)) for label in labels)
                denominators = tuple(image.denominator() for image in images)

                source_images = {}
                for position, (label, image) in enumerate(zip(labels, images, strict=True)):
                    multiplier = source_domain.base_ring().one()
                    for other_position, denominator in enumerate(denominators):
                        if other_position != position:
                            multiplier *= denominator
                    source_images[label] = source_codomain.scalar_multiple(
                        multiplier,
                        image.numerator(),
                    )

                source_morphism = source_domain.module_category().Mor(source_domain, source_codomain)(source_images)
                source_kernel = source_morphism.kernel()
                localized_kernel = functor(source_kernel)
                localized_inclusion = functor(source_kernel.inclusion())
                assert localized_inclusion.codomain() is domain, (
                    f"kernel of {domain} -> {codomain}: the localized inclusion of the kernel should land in "
                    f"{domain}, but lands in {localized_inclusion.codomain()}"
                )
                return localized_kernel
            case _ if (
                ring in PrincipalIdealDomains()
                and domain in ModulesWithChosenFinitePresentation(ring)
                and codomain in InternalMorModules(ring)
                and codomain.codomain() in FractionFieldQuotients(ring)
                and codomain.domain().module_generating_set().cardinality().is_finite()
            ):
                return self._kernel_through_generator_evaluation()

        represented = NotImplemented
        for owner in (domain, codomain):
            represented = owner._represented_kernel_of_morphism(self)
            if represented is not NotImplemented:
                return represented
        assert represented is not NotImplemented, (
            f"cannot compute the kernel of {domain} -> {codomain}: no algorithm is available for these modules "
            f"(domain in {domain.category()}, codomain in {codomain.category()})"
        )
        return represented

    def _kernel_through_generator_evaluation(self):
        r"""Return ``ker(f)`` for ``f: A -> Mor_R(X, K/aR)`` with ``X`` finitely generated over a PID ``R``.

        A map out of ``X`` is determined by its values on the generators
        ``x_1, ..., x_n`` of ``X``, so evaluation
        ``Mor_R(X, K/aR) -> (K/aR)^n`` is injective and ``ker(f)`` is the
        kernel of ``a |-> (f(a)(x_j))_j``.  The finitely many values
        ``f(a_i)(x_j)`` on the generators ``a_i`` of ``A`` generate a cyclic
        submodule ``S = R s ~= R/(m)`` of ``K/aR``, which
        :meth:`FractionFieldQuotients.ParentMethods.subobject_on` classifies.
        Writing ``f(a_i)(x_j) = c_ij s`` gives the map
        ``g: A -> (R/(m))^n``, ``a_i |-> (c_ij)_j``, and ``S^n -> (K/aR)^n``
        is injective, so ``ker(f) = ker(g)``.  The kernel of ``g``, a map
        between finitely presented modules, is the linear solve over ``R``
        that the presented-module kernel owner performs.
        """
        from sage_extensions.categories.modules.pure.modules import Modules

        domain = self.domain()
        codomain = self.codomain()
        ring = domain.base_ring()
        source = codomain.domain()
        values = codomain.codomain()
        domain_labels = tuple(domain.module_generating_set())
        source_labels = tuple(source.module_generating_set())
        evaluations = {
            (domain_label, source_label): self(domain.module_generator(domain_label))(
                source.module_generator(source_label)
            )
            for domain_label in domain_labels
            for source_label in source_labels
        }
        if all(value == values.zero() for value in evaluations.values()):
            return domain.whole_subobject()
        cyclic = values.subobject_on(tuple(evaluations.values()))
        (cyclic_label,) = tuple(cyclic.module_generating_set())
        order = cyclic.presentation_matrix()[0, 0]
        coefficient = {
            pair: cyclic.framing_morphism().lift(cyclic.inclusion().lift(value))(cyclic_label)
            for pair, value in evaluations.items()
        }
        target = Modules(ring).FinitelyPresented().Torsion().direct_sum_of_cyclics(
            tuple(order for _ in source_labels)
        )
        target_labels = tuple(target.module_generating_set())
        evaluation = domain.module_category().Mor(domain, target)(
            lambda domain_label: target.linear_combination(
                {
                    target_label: coefficient[(domain_label, source_label)]
                    for source_label, target_label in zip(source_labels, target_labels, strict=True)
                }
            )
        )
        return evaluation.kernel()

    def subobject_image_adjunction(self):
        r"""Return ``f_* ⊣ f^{-1}`` on fixed-ambient module subobjects."""
        from sage_extensions.categories.functors.subobject_images import (
            _SubobjectImageAdjunction,
        )

        return _SubobjectImageAdjunction(self)

    @cached_method
    def image(self):
        r"""Return ``im(self)`` as a subobject of the codomain.

        The image of an R-linear map into the canonical left regular module
        of a *commutative* ring R is an ideal. The ideal constructor retains
        an exact finite presentation and the inclusion into R; merely
        spanning these elements as a generic module loses that structure.
        In other codomains, use the ordinary subobject-span constructor.
        """
        self._require_established_linearity("image construction")
        labels = self.domain().module_generating_set()
        assert labels.cardinality().is_finite(), (
            f"cannot compute the image of {self.domain()} -> {self.codomain()}: the image is computed as the span of "
            f"the images of generators of {self.domain()}, which must be finitely generated, but its generating set "
            f"{labels} is infinite"
        )
        codomain = self.codomain()
        generators = finite_indexed_family(
            labels,
            lambda label: self(self.domain().module_generator(label)),
            name="Image spanning family",
        )
        from sage_extensions.categories.rings.ring_foundation import CommutativeRings

        ring = codomain.base_ring()
        if ring in CommutativeRings() and codomain is ring.regular_module():
            # R-linear submodules of {}_R R are exactly ideals, with their
            # unique scalar coefficients read from the selected rank-one
            # framing. Use the existing ideal computation for relations and
            # its structural inclusion; no independent image algorithm.
            (unit_label,) = tuple(codomain.module_generating_set())
            return ring.ideal(*(
                generators.value(label).to_vector()(unit_label)
                for label in labels
            ))
        return codomain.subobject_on(generators)

    @cached_method
    def image_factorization(self):
        r"""The effective image factorization in the ambient module category.

        For ``f:M -> N`` this retains its actual image submodule ``I``,
        the canonical inclusion ``i:I -> N``, and the induced epimorphism
        ``e:M -> I`` with ``i * e = f``. In particular an image ideal in
        the regular module of a commutative ring stays the selected ideal,
        not an independently constructed isomorphic submodule.

        A multiplication-by-two map on ``ZZ`` factors through ``2 ZZ``;
        its inclusion is not the identity of ``ZZ``. The zero map instead
        factors through the zero submodule, with its zero inclusion.
        """
        image = self.image()
        inclusion = image.inclusion()
        return self.factor_through(inclusion), inclusion

    def solution_fibre(self, right_hand_side):
        r"""Return the full affine fibre, its inclusion and its kernel torsor.

        Empty fibres remain represented; selecting ``base_point()`` raises
        ``ValueError`` when the right-hand side is outside the image.
        """
        from sage_extensions.categories.modules.affine_fibres import AffineModuleFibres

        values = self.codomain()
        zero = values.zero_subobject()
        return AffineModuleFibres(self.domain().base_ring())(
            self, zero.inclusion(), -values(right_hand_side)
        )

    def denominator_ideal(self, source, target):
        r"""Return ``{a in ZZ : a*self(source) subset target}``.

        The endpoints are the chosen rational extensions of finite free
        integral modules. In integral bases, a scalar clears the map exactly
        when it clears every matrix entry. Thus this basis-independent ideal
        is the intersection of the principal denominator ideals, computed
        by the ring's lcm. This is the usual localization description of
        ``Hom_ZZ(source,target)`` inside its rational scalar extension.
        """
        from sage.rings.integer_ring import ZZ as SageZZ
        from sage_extensions.categories.modules.pure.modules import Modules, ModulesOverIntegralDomains
        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        ring = source.base_ring()
        if ring is not _owned_integers() or target.base_ring() is not ring:
            raise TypeError("the normalized denominator ideal requires integral modules over ZZ")
        field_map = ring.fraction_field_map()
        if self.domain() is not source.base_change(field_map) or self.codomain() is not target.base_change(field_map):
            raise ValueError("the rational map must join the chosen generic fibres")
        if not _has_finite_free_framing(source) or not _has_finite_free_framing(target):
            raise NotImplementedError("denominator-ideal computation requires finite integral bases")
        restrict = Modules(field_map.codomain()).restriction_of_scalars(field_map)
        restricted = restrict(self) * ModulesOverIntegralDomains(ring)(source).generic_fibre_map()
        framing = self.codomain().framing_morphism()
        denominator = ring.one()
        for vector in source.module_generators():
            coordinates = framing.lift(restricted(vector).underlying_element())
            for coefficient in coordinates.parent()._selected_module_coefficients(coordinates).values():
                denominator = denominator.lcm(coefficient.denominator())
        return ring.ideal(denominator)

    def affine_inverse_image(self, target_inclusion, offset=None):
        r"""Return all parameters ``p`` with ``offset+self(p)`` in the target submodule.

        An integral inclusion into the restriction of the rational codomain
        restricts this map's scalars as well. Its inverse image retains the
        complete rational kernel, including in non-injective cases.
        """
        from sage_extensions.categories.modules.affine_fibres import AffineModuleFibres
        from sage_extensions.categories.modules.pure.modules import Modules

        ring = target_inclusion.domain().base_ring()
        offset = self.codomain().zero() if offset is None else self.codomain()(offset)
        if self.domain().base_ring() is ring:
            linear = self
        else:
            field_map = ring.fraction_field_map()
            if self.domain().base_ring() is not field_map.codomain():
                raise ValueError("the parameter scalar ring must be the integral ring or its fraction field")
            restrict = Modules(field_map.codomain()).restriction_of_scalars(field_map)
            linear = restrict(self)
            offset = linear.codomain()(offset)
        return AffineModuleFibres(ring)(linear, target_inclusion, offset)

    @cached_method
    def _framed_coordinate_morphism(self):
        r"""Realize this linear arrow in the matrix Mor of its selected framings.

        A stronger arrow keeps its own parent under Mor admission. Matrix
        computations instead use this explicit realization, retaining the
        original linear arrow as the construction premise. The selected
        source and target framings, hence the comparison, are fixed.
        Callers are finite-free kernels, integral preimages, the module owner's engine-matrix
        lowering, and the tensor owner's coordinate, pullback and private
        row-action adapters.
        """
        from sage_extensions.categories.modules.pure.modules import MatrixSpaces

        source, target = self.domain(), self.codomain()
        mor = source.module_category().Mor(source, target)
        if mor not in MatrixSpaces(source.base_ring()):
            raise TypeError(f"coordinates of {self} require finite free modules with selected framings")
        if self.parent() is mor:
            return self
        return mor._from_constructed_element_map(self, premises=(self,))

    def preimage(self, element):
        r"""Return one preimage of ``element`` when it lies in the represented image.

        Solve against the images of the domain's selected generators through
        the codomain's presentation.  A basis chosen for the image need not
        have the same labels or vectors as those generators.  The represented
        solver retains the domain coordinates, including when the codomain
        is a restriction of scalars from a fraction field.

        Over exact fields this uses rank and linear solving directly,
        retaining RR comparisons during elimination.

        EXAMPLES::

            sage: from sage_extensions.rings.real import RR
            sage: V = RR ** 2
            sage: e, f = V.module_generators()
            sage: A = V.module_category().Mor(V, V)((RR.pi()*e, V.zero()))
            sage: x = A.preimage(e)
            sage: assert x.parent() is V and A(x) == e
            sage: assert A.is_in_image(f) is False
            sage: Z = RR ** 0
            sage: z = Z.module_category().Mor(Z, V)(())
            sage: assert z.preimage(V.zero()) == Z.zero()
            sage: assert z.is_in_image(f) is False
            sage: M = ZZ ** 1
            sage: u = M.module_generators()[0]
            sage: twice = M.module_category().Mor(M, M)((2*u,))
            sage: assert twice.is_in_image(u) is False
            sage: assert twice.preimage(2*u) == u
            sage: from sage_extensions.categories.sets.set_categories import NN, Sets
            sage: from sage_extensions.categories.rings.ring_foundation import _owned_rationals
            sage: from sage_extensions.logic import Predicate
            sage: Q = _owned_rationals()
            sage: a = Sets().Mor(NN, Q)(lambda n: Q(1)/Q(2)**int(n))
            sage: t = RR.of_cauchy(a)
            sage: B = V.module_category().Mor(V, V)((e, e + f))
            sage: lifted = B.preimage((RR.one() + t)*e + f)
            sage: assert lifted.parent() is V
            sage: labels = tuple(V.module_generating_set())
            sage: assert isinstance(lifted.to_vector()(labels[0]) == RR.zero(), Predicate)
            sage: assert lifted.to_vector()(labels[1]) == RR.one()
        """
        self._require_established_linearity("preimage computation")
        domain = self.domain()
        codomain = self.codomain()
        element = element if element.parent() is codomain else codomain(element)
        if (element == codomain.zero()) is True:
            return domain.zero()
        preimage = self._preimage_or_none(element)
        if preimage is None:
            raise ValueError(f"{element} is outside the image of {self}")
        return preimage

    def is_injective(self) -> bool:
        r"""Return whether ``ker(self)=0`` when the kernel is computable."""
        self._require_established_linearity("injectivity")
        return self.kernel().is_zero()

    def is_surjective(self) -> bool:
        r"""Return whether ``coker(self)=0`` when the cokernel is computable."""
        self._require_established_linearity("surjectivity")
        ring = self.domain().base_ring()
        if (
            ring in OwnedFields()
            and ring.is_exact() is True
            and _has_finite_free_framing(self.domain())
            and _has_finite_free_framing(self.codomain())
        ):
            # A linear map onto a finite free module is surjective exactly
            # when every selected basis vector has a preimage. This uses the
            # field's exact solver, including represented-real coefficients.
            return all(
                self._preimage_or_none(generator) is not None
                for generator in self.codomain().module_generators()
            )
        return self.cokernel().is_zero()

    def residue_morphism(self):
        r"""Return ``f tensor_R k`` for a morphism of finite modules over a local ring."""

        ring = self.domain().base_ring()
        assert self.codomain().base_ring() is ring, (
            f"cannot reduce {self.domain()} -> {self.codomain()} modulo the maximal ideal: both modules must be over "
            f"the same ring, but they are over {ring} and {self.codomain().base_ring()}"
        )
        assert ring in LocalRings(), (
            f"cannot reduce {self.domain()} -> {self.codomain()} modulo the maximal ideal: the base ring must be local, "
            f"but {ring} is not known to be local"
        )
        assert self.domain().is_finitely_generated() and self.codomain().is_finitely_generated(), (
            f"cannot reduce {self.domain()} -> {self.codomain()} modulo the maximal ideal of {ring}: "
            "Nakayama's lemma needs both modules finitely generated, and at least one is not"
        )
        return self.base_change(ring.residue_map())

    reduction_mod_maximal_ideal = residue_morphism

    def is_surjective_mod_maximal_ideal(self) -> bool:
        r"""Return whether ``f tensor_R k`` is surjective."""
        return self.residue_morphism().is_surjective()

    def is_surjective_by_nakayama(self) -> bool:
        r"""Use Nakayama: a map onto a finite local module is surjective iff its residue map is."""
        return self.is_surjective_mod_maximal_ideal()

    def is_primitive(self) -> bool:
        r"""Return whether this monomorphism has torsion-free cokernel."""
        if not self.is_injective():
            return False
        return self.cokernel().is_torsion_free()

    is_saturated = is_primitive

    def saturation(self):
        r"""Return the saturation of the image of an injective morphism.

        For ``i:S -> M`` this is the kernel of
        ``M -> M/S -> (M/S)/Tor(M/S)``.  For finite free ``ZZ``-modules,
        compute the primitive row lattice directly from the Smith form of the
        coordinate matrix instead of constructing the quotient object first.
        """
        assert self.is_injective(), (
            f"cannot saturate the image of {self.domain()} -> {self.codomain()}: saturation is defined for an "
            f"injective map, and this map has nonzero kernel"
        )
        ring = self.domain().base_ring()
        from sage.rings.integer_ring import ZZ as SageZZ
        if _engine_ring(ring) is SageZZ and _has_finite_free_framing(self.domain()) and _has_finite_free_framing(self.codomain()):
            from sage.matrix.constructor import matrix
            from sage.modules.free_module import FreeModule
            source_labels = tuple(self.domain().module_generating_set())
            target_labels = tuple(self.codomain().module_generating_set())
            rows = []
            for source_label in source_labels:
                image = self(self.domain().module_generator(source_label))
                coordinates = image.to_vector()
                rows.append([_engine_element(ring, coordinates(label)) for label in target_labels])
            engine = _engine_ring(ring)
            A = matrix(engine, rows)
            smith, left, right = A.smith_form()
            rank = int(A.rank())
            # D = left * A * right.  The primitive closure of the row lattice of A
            # is spanned by the first ``rank`` rows of right^{-1}.
            primitive_rows = tuple(right.inverse().row(i) for i in range(rank))
            ambient = FreeModule(engine, len(target_labels))
            primitive = ambient.submodule(primitive_rows)
            basis_rows = tuple(tuple(row) for row in primitive.basis_matrix().rows())
            generators = tuple(
                self.codomain().linear_combination({target_labels[j]: _owned_engine_element(ring, value) for j, value in enumerate(row) if value})
                for row in basis_rows
            )
            return self.codomain().subobject_on(generators)
        quotient = self.cokernel()
        projection = quotient.torsion_free_quotient_projection()
        composite = projection * quotient.presentation_projection()
        return composite.kernel()

    def index(self):
        r"""Return the cardinality of the cokernel."""
        return self.cokernel().cardinality()

    def _preimage_or_none(self, element):
        r"""Return a selected preimage, or ``None`` outside the image.

        Protected contract of module morphisms.  Its callers are :meth:`preimage`, :meth:`lift`,
        :meth:`is_in_image` and :meth:`factor_through`.  A lift selected at
        construction is such a function: it returns the preimage of an
        element of the image and ``None`` for any other element.  Otherwise,
        between finite free modules with chosen bases, the coordinates of
        ``element`` are solved against the images of the domain basis over
        the base ring; into a module with a chosen finite presentation, the
        preimage is solved through that presentation; and into a restriction
        of scalars to ``R`` from ``Frac(R)``, through the framing over
        ``Frac(R)``.
        """
        custom = self._lift_function
        if custom is not None:
            candidate = custom(element)
            if candidate is None:
                if self.selected_lift_exactness_decision() is True:
                    return None
                raise ValueError(
                    f"cannot decide whether {element} is in the image of {self.domain()} -> {self.codomain()}: "
                    "the given lift returned no preimage, but that lift is not known to find every preimage"
                )
            candidate = self.domain()(candidate)
            # The selected construction proves both which values have a
            # preimage and that a returned value is its section. Consume
            # that same certificate on a successful lift as on None.
            if self.selected_lift_exactness_decision() is True:
                return candidate
            target = element if element.parent() is self.codomain() else self.codomain()(element)
            section_equation = self(candidate) == target
            if section_equation is False:
                raise ValueError(f"the given lift through {self.domain()} -> {self.codomain()} is not a section: for y = {target} it returns x = {candidate}, but f(x) != y")
            if section_equation is not True:
                raise ValueError(f"cannot verify the given lift through {self.domain()} -> {self.codomain()}: for y = {target} it returns x = {candidate}, and whether f(x) = y cannot be decided")
            return candidate
        self._require_established_linearity("represented preimage computation")
        from sage_extensions.categories.modules.pure.modules import (
            ModulesWithChosenFinitePresentation,
        )

        domain, codomain = self.domain(), self.codomain()
        ring = domain.base_ring()
        assert domain.module_generating_set().cardinality().is_finite(), (
            f"cannot compute a preimage of {element} under {domain} -> {codomain}: the domain must be finitely "
            f"generated, but its generating set {domain.module_generating_set()} is infinite"
        )
        from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
            _singular_presentation_preimage,
        )

        polynomial_preimage = _singular_presentation_preimage(self, element)
        if polynomial_preimage is not NotImplemented:
            return polynomial_preimage
        match codomain:
            case _ if _has_finite_free_framing(domain) and _has_finite_free_framing(codomain):
                pass
            case _ if codomain in ModulesWithChosenFinitePresentation(ring):
                return self._preimage_through_the_codomain_presentation(element)
            case _:
                return self._preimage_through_the_extension_framing(element)
        if element.parent() is not self.codomain():
            element = self.codomain()(element)
        codomain_labels = tuple(self.codomain().module_generating_set())
        coordinates = element.to_vector()
        target = [coordinates(label) for label in codomain_labels]
        coordinate_map = self._framed_coordinate_morphism()
        solution = _solve_preimage_integrally(coordinate_map, target, ring)
        if solution is None:
            return None
        return self.domain().linear_combination({
            label: coefficient
            for label, coefficient in zip(self.domain().module_generating_set(), solution, strict=True)
        })

    def lift(self, element):
        r"""Return a selected preimage of ``element``; reject an element outside the image with ``ValueError``.

        Along the codomain's own framing ``F(S) ->> M`` -- the augmentation of
        its chosen resolution, the identity when ``M`` is its own framing
        source -- the preimage is the one the codomain's construction chose,
        read through its ``_framing_lift`` contract rather than solved for.
        """
        codomain = self.codomain()
        match codomain.has_selected_module_resolution() and self is codomain.framing_morphism():
            case True:
                return codomain._framing_lift(codomain(element))
            case False:
                pass
        preimage = self._preimage_or_none(element)
        if preimage is None:
            raise ValueError(f"{element} is not in the image of {self}")
        return preimage

    def is_in_image(self, element) -> bool:
        r"""Return whether ``element`` has a preimage under this linear map."""
        return self._preimage_or_none(element) is not None

    def has_selected_lift(self) -> bool:
        r"""Return whether this map carries a selected lift callback."""
        return self._lift_function is not None

    @cached_method
    def selected_lift_exactness_decision(self):
        r"""Return whether absence reported by the selected lift is construction-derived.

        ``True`` with no selected lift, or when the lift's own construction
        shows it is a section; otherwise the proposition that states it.
        Asked on the first request (``OWN-22``).
        """
        match self._lift_function:
            case None:
                return True
            case _:
                if self._selected_lift_derivation() is True:
                    return True
                return AtomicProposition("selected_lift_exactness_decision", self)

    def factor_through(self, target_embedding):
        r"""Return the unique factor through a represented module embedding.

        For ``f:A -> X`` and a monomorphism ``j:B -> X`` this constructs the
        commuting-triangle map ``A -> B`` exactly when every selected generator
        image of ``f`` lies in ``j(B)``; otherwise ``ValueError`` states that
        ``f`` does not factor.  The source map need not itself be a
        monomorphism; uniqueness comes from ``j``.
        """
        factor = self.factor_through_or_none(target_embedding)
        if factor is None:
            raise ValueError(f"{self.domain()} -> {self.codomain()} does not factor through {target_embedding.domain()} -> {target_embedding.codomain()}: its image is not contained in the submodule")
        return factor

    def factor_through_or_none(self, target_embedding):
        r"""Return the unique represented factor, or None when containment fails."""
        self._require_established_linearity("factorization through a module subobject")
        assert target_embedding.codomain() is self.codomain(), (
            f"cannot factor {self.domain()} -> {self.codomain()} through {target_embedding.domain()} -> "
            f"{target_embedding.codomain()}: both maps must have the same codomain"
        )
        source = self.domain()
        target = target_embedding.domain()
        generator_images = {
            label: self(source.module_generator(label))
            for label in source.module_generating_set()
        }
        preimages = {
            label: target_embedding._preimage_or_none(image)
            for label, image in generator_images.items()
        }
        if any(preimage is None for preimage in preimages.values()):
            return None
        return self._factor_from_generator_preimages(target_embedding, preimages)

    def _factor_from_generator_preimages(self, target_embedding, preimages):
        r"""Realize the linear factor from the computed generator preimages."""
        source = self.domain()
        return source.module_category().Mor(source, target_embedding.domain())(preimages)

    @cached_method
    def selected_presentation_morphism(self):
        r"""Lift this map to a commuting square of selected presentations.

        For ``f : M -> N`` with selected presentations ``p : F_1 -> F_0``
        and ``q : G_1 -> G_0``, first lift each image of a selected generator of
        ``M`` to the chosen free cover ``G_0``.  This gives ``b : F_0 -> G_0``
        with ``pi_N b = f pi_M``.  Consequently ``b p`` lands in ``ker(pi_N)``;
        the selected presentation identifies that kernel with ``im(q)``, so
        lifting the images of the relation generators through ``q`` gives
        ``a : F_1 -> G_1`` and the commuting square ``q a = b p``.
        """
        self._require_established_linearity("lifting to selected presentations")
        from sage_extensions.categories.modules.pure.modules import (
            ModulesWithChosenFinitePresentation,
        )

        source = self.domain()
        target = self.codomain()
        ring = source.base_ring()
        assert source in ModulesWithChosenFinitePresentation(ring) and target in ModulesWithChosenFinitePresentation(ring), (
            f"cannot lift {source} -> {target} to a map of finite presentations: both modules must have a chosen "
            f"finite presentation, but they are in {source.category()} and {target.category()}"
        )

        source_presentation = source.presentation()
        target_presentation = target.presentation()
        source_cover = source_presentation.codomain()
        target_cover = target_presentation.codomain()

        def lift_target(element):
            coordinates = target.framing_morphism().lift(element)
            return target_cover.linear_combination(coordinates.parent()._selected_module_coefficients(coordinates))

        cover_map = source_cover.module_category().Mor(source_cover, target_cover)({label: lift_target(self(source.module_generator(label))) for label in source_cover.module_generating_set()})
        relation_source = source_presentation.domain()
        relation_target = target_presentation.domain()
        relation_map = relation_source.module_category().Mor(relation_source, relation_target)(
            {
                label: target_presentation.lift(cover_map(source_presentation(source_presentation.domain().module_generator(label))))
                for label in source_presentation.domain().module_generating_set()
            }
        )

        category = ModulesWithChosenFinitePresentation(ring).presentation_category()
        return category.Mor(source.presentation_object(), target.presentation_object())(
            relation_map,
            cover_map,
        )

    def _preimage_through_the_codomain_presentation(self, element):
        r"""Return a preimage of ``element`` through the codomain's chosen presentation, or ``None``.

        Let ``r : F_1 -> F_0`` be the chosen presentation of the codomain
        ``M``, with ``pi : F_0 ->> M``, and let ``p : F(S) ->> D`` be the
        framing of the finitely generated domain.  Lifting ``f p`` on the
        basis of ``F(S)`` gives ``g : F(S) -> F_0`` with ``pi g = f p``.  For
        a lift ``h`` of ``y`` to ``F_0``, ``y = f(x)`` has a solution exactly
        when ``h`` lies in ``im(g) + ker(pi) = im(g) + im(r)``, that is, when
        ``h`` has a preimage under the map ``F(S) + F_1 -> F_0`` with legs
        ``g`` and ``r``.  That map is between finite free modules, so its
        preimage is a coordinate solve.  The ``F(S)``-component ``c`` of a
        solution gives the preimage ``x = p(c)``.  No element of ``D`` is
        enumerated.
        """
        from sage_extensions.categories.modules.pure.modules import Modules

        domain, codomain = self.domain(), self.codomain()
        if element.parent() is not codomain:
            element = codomain(element)
        presentation = codomain.presentation()
        cover = presentation.codomain()
        codomain_framing = codomain.framing_morphism()

        def lift_to_cover(value):
            coordinates = codomain_framing.lift(value)
            return cover.linear_combination(coordinates.parent()._selected_module_coefficients(coordinates))

        domain_framing = domain.framing_morphism()
        generator_cover = domain_framing.domain()
        composite = self * domain_framing
        generator_lift = generator_cover.module_category().Mor(generator_cover, cover)(
            {
                label: lift_to_cover(composite(generator_cover.module_generator(label)))
                for label in generator_cover.module_generating_set()
            }
        )
        cover_sum = Modules(domain.base_ring()).biproduct((generator_cover, presentation.domain()))
        solution = cover_sum.from_summands(generator_lift, presentation)._preimage_or_none(lift_to_cover(element))
        if solution is None:
            return None
        return domain_framing(cover_sum.projection(0)(solution))

    def _preimage_through_the_extension_framing(self, element):
        r"""Return the preimage of ``element`` in a restriction of scalars to ``R``, or ``None``.

        ``Res_f(W)`` along ``f: R -> Frac(R)`` is divisible, so it is not
        finitely generated over ``R`` and carries no framing of its own to
        solve coordinates against.  The image of this morphism is still the
        ``R``-span of the finitely many images of the domain framing, and
        that span is read in the ``Frac(R)``-framing ``W`` does carry: one
        common denominator carries the generator images and the target into
        the free ``R``-module on that framing, without changing which
        ``R``-combinations of the images the target is.  The coordinate lift
        decides there, which is the rational solve of the linear system
        followed by the integrality of its solution.
        """
        from sage_extensions.categories.modules.pure.modules import (
            FinitelyGeneratedModules,
            RestrictedScalarsModules,
        )

        domain, codomain = self.domain(), self.codomain()
        ring = domain.base_ring()
        assert codomain in RestrictedScalarsModules(ring), f"cannot compute a preimage under {domain} -> {codomain}: {codomain} has no chosen generators, and a preimage is computed here only when it is a module over a larger ring restricted to {ring}, which {codomain} is not"
        fractions = codomain.extension_ring()
        assert fractions is ring.fraction_field(), (
            f"cannot compute a preimage under {domain} -> {codomain}: {codomain} must be a module over the fraction field of {ring} restricted to {ring}, but it is a module over {fractions}"
        )
        extension = codomain.module_over_extension()
        assert extension.has_selected_module_resolution() and extension in FinitelyGeneratedModules(fractions), (
            f"cannot compute a preimage under {domain} -> {codomain}: the {fractions}-module {extension} must be finitely generated with chosen generators, but it is in {extension.category()}"
        )

        if not _has_finite_free_framing(extension):
            from sage_extensions.categories.modules.pure.modules import Modules

            # A presentation's generators are not independent coordinates.
            # Over the fraction field its invariant-factor trivialization
            # removes the relations before the integral coordinate solve.
            coordinates = extension.finite_free_trivialization().forward()
            restricted = Modules(fractions).restriction_of_scalars(codomain.ring_map())(coordinates)
            return (restricted * self)._preimage_or_none(restricted(codomain(element)))

        if element.parent() is not codomain:
            element = codomain(element)

        extension_framing, scale, cleared_span = self._integral_extension_coordinate_span()
        target_coordinates = extension_framing.lift(element.underlying_element())
        coefficients = {
            label: scale * coefficient
            for label, coefficient in target_coordinates.parent()._selected_module_coefficients(target_coordinates).items()
        }
        if any(coefficient not in ring for coefficient in coefficients.values()):
            return None
        target = cleared_span.codomain().linear_combination({
            label: ring(coefficient) for label, coefficient in coefficients.items()
        })
        return cleared_span._preimage_or_none(target)

    @cached_method
    def _integral_extension_coordinate_span(self):
        r"""Retain the integral coordinate span used by extension-framing preimages.

        The module morphism owns this private workspace. Its fixed generator
        images determine one denominator and one integral linear system; a
        queried target changes only the right-hand side.
        """
        domain, codomain = self.domain(), self.codomain()
        ring = domain.base_ring()
        extension = codomain.module_over_extension()
        extension_framing = extension.framing_morphism()
        image_coordinates = {
            label: extension_framing.lift(self(domain.module_generator(label)).underlying_element())
            for label in domain.module_generating_set()
        }
        denominator = reduce(
            lambda current, coefficient: current.lcm(coefficient.denominator()),
            tuple(
                coefficient
                for coordinates in image_coordinates.values()
                for coefficient in coordinates.parent()._selected_module_coefficients(coordinates).values()
            ),
            ring.one(),
        )
        scale = codomain.ring_map()(denominator)
        cleared_module = ring._fresh_free_module_on(extension.module_generating_set())

        def cleared(coordinates):
            return cleared_module.linear_combination({
                label: ring(scale * coefficient)
                for label, coefficient in coordinates.parent()._selected_module_coefficients(coordinates).items()
            })

        cleared_span = domain.module_category().Mor(domain, cleared_module)({label: cleared(coordinates) for label, coordinates in image_coordinates.items()})
        return extension_framing, scale, cleared_span

    def orthogonal_complement(self):
        r"""Return ``im(self)^perp`` when the codomain carries a scalar-valued pairing."""
        codomain = self.codomain()
        ring = codomain.base_ring()
        if codomain.value_module() is not ring:
            raise TypeError(f"cannot form the orthogonal complement of the image of {self.domain()} -> {codomain}: the form on {codomain} must take values in {ring}, but it takes values in {codomain.value_module()}")

        source_generators = tuple(self.domain().module_generators())
        labels = Sets.Δ[len(source_generators) - 1]
        from sage_extensions.categories.modules.framed.framed_free_modules import _fresh_free_module_on
        target = _fresh_free_module_on(ring, labels)
        pairing_map = codomain.module_category().Mor(codomain, target)(
            {
                label: target.linear_combination(
                    {
                        labels[position]: coefficient
                        for position, source_generator in enumerate(source_generators)
                        if (
                            coefficient := codomain.b(
                                codomain.module_generator(label),
                                self(source_generator),
                            )
                        )
                        != ring.zero()
                    }
                )
                for label in codomain.module_generating_set()
            }
        )
        return pairing_map.kernel()

    def then(self, other):
        r"""Return ``other ∘ self``."""
        if other.domain() is not self.codomain():
            raise ValueError(f"cannot compose g . f for f: {self.domain()} -> {self.codomain()} and g: {other.domain()} -> {other.codomain()}: the codomain of f must be the domain of g")
        return other * self

    def tor_map(self, other, degree=0, *, argument=1, lift=None):
        r"""Return the map on ``Tor_degree`` induced by this module morphism.

        With ``argument=1``, ``self`` acts on the first Tor variable and
        ``other`` is fixed.  With ``argument=2``, ``other`` is the fixed first
        variable and ``self`` acts on the second.
        """
        from sage_extensions.categories.modules.derived_functors import _tor_map

        return _tor_map(self, other, degree=degree, argument=argument, lift=lift)

    def ext_map(self, other, degree=0, *, argument=1, lift=None):
        r"""Return the map on ``Ext^degree`` induced by this module morphism.

        With ``argument=1`` this is contravariant in ``self``; with
        ``argument=2`` the first module ``other`` is fixed and the induced map
        is covariant in ``self``.
        """
        from sage_extensions.categories.modules.derived_functors import _ext_map

        return _ext_map(self, other, degree=degree, argument=argument, lift=lift)

    def divided_square(self):
        r"""Return ``Gamma^2(self)`` on the divided squares of the endpoints."""
        from sage_extensions.categories.modules.powers import (
            _divided_square_morphism,
        )

        return _divided_square_morphism(self)

    def symmetric_power(self, degree):
        r"""Return ``Sym^degree(self)``."""
        from sage_extensions.categories.modules.powers import (
            _symmetric_power_morphism,
        )

        return _symmetric_power_morphism(self, degree)

    def exterior_power(self, degree):
        r"""Return ``Lambda^degree(self)``."""
        from sage_extensions.categories.modules.powers import (
            _alternating_power_morphism,
        )

        return _alternating_power_morphism(self, degree)

    def divided_power(self, degree):
        r"""Return ``Gamma^degree(self)``."""
        from sage_extensions.categories.modules.powers import (
            _divided_power_morphism,
        )

        return _divided_power_morphism(self, degree)

    def base_change(self, ring_map):
        r"""Extend this represented linear map along ``ring_map : R -> S``.

        The scalar-extension functor owns both object and morphism transport;
        this method is the module-morphism entry to that same action.
        """
        ring = self.domain().base_ring()
        assert self.codomain().base_ring() is ring and ring_map.domain() is ring, (
            f"cannot base change {self.domain()} -> {self.codomain()} along {ring_map}: both modules and the ring map "
            f"must have source ring {ring}, but they have {self.codomain().base_ring()} and {ring_map.domain()}"
        )
        from sage_extensions.categories.modules.pure.modules import Modules

        return Modules(ring).scalar_extension(ring_map)(self)

    def adic_completion(self, ideal, *, precision=20):
        r"""Return ``self tensor_R R_hat`` using one shared completion parent.

        The endpoint objects are the same completed modules returned by their
        module constructors; the scalar-extension functor adopts those exact
        images before transporting this morphism.
        """
        ring = self.domain().base_ring()
        assert self.codomain().base_ring() is ring, (
            f"cannot complete {self.domain()} -> {self.codomain()}: both modules must be over the same ring, "
            f"but they are over {ring} and {self.codomain().base_ring()}"
        )
        assert ideal.ring() is ring, (
            f"cannot complete {self.domain()} -> {self.codomain()} at {ideal}: the ideal must lie in {ring}, "
            f"but it lies in {ideal.ring()}"
        )
        completion = ring.adic_completion(ideal, precision=precision)
        return self.base_change_to_completion(completion)

    def base_change_to_completion(self, completion):
        r"""Return ``self tensor_R R_hat`` for one already selected completion."""
        ring = self.domain().base_ring()
        assert self.codomain().base_ring() is ring, (
            f"cannot complete {self.domain()} -> {self.codomain()}: both modules must be over the same ring, "
            f"but they are over {ring} and {self.codomain().base_ring()}"
        )
        assert completion.completion_source() is ring, (
            f"cannot base change {self.domain()} -> {self.codomain()} to {completion}: it must be a completion of "
            f"{ring}, but it is a completion of {completion.completion_source()}"
        )
        source = self.domain().base_change_to_completion(completion)
        target = self.codomain().base_change_to_completion(completion)

        from sage_extensions.categories.modules.pure.modules import Modules

        extension = Modules(ring).scalar_extension(completion.completion_map())
        completed = extension(self)
        assert completed.domain() is source and completed.codomain() is target, (
            f"completion of {self.domain()} -> {self.codomain()}: the completed map should go {source} -> {target}, "
            f"but goes {completed.domain()} -> {completed.codomain()}"
        )
        return completed

    def completion_cokernel_comparison(self, ideal, *, precision=20):
        r"""Return the isomorphism ``coker(self) tensor R_hat ~= coker(self tensor R_hat)``.

        Completion of a Noetherian ring is flat, and scalar extension is right
        exact, so completing the cokernel commutes with taking it.  Both sides
        use one selected completion parent and are presented on the same
        generators; the isomorphism carries each generator to the generator of
        the same position.  It is an isomorphism of ``Modules(R_hat)``.
        """
        ring = self.domain().base_ring()
        completion = ring.adic_completion(ideal, precision=precision)
        assert completion.is_flat_over_source(), (
            f"cannot identify the completed cokernel of {self.domain()} -> {self.codomain()}: the completion "
            f"{completion} must be flat over {ring}, and it is not known to be"
        )
        completed_morphism = self.base_change_to_completion(completion)
        completed_cokernel = self.cokernel().base_change_to_completion(completion)
        cokernel_after_completion = completed_morphism.cokernel()
        left_labels = completed_cokernel.module_generating_set()
        right_labels = cokernel_after_completion.module_generating_set()
        assert left_labels.cardinality() == right_labels.cardinality(), (
            f"cannot identify the completed cokernel of {self.domain()} -> {self.codomain()}: {completed_cokernel} and "
            f"{cokernel_after_completion} should have equally many generators, but have {left_labels.cardinality()} "
            f"and {right_labels.cardinality()}"
        )

        forward = completed_cokernel.module_category().Mor(completed_cokernel, cokernel_after_completion)(
            {label: cokernel_after_completion.module_generator(right_labels[int(left_labels.ranking_map()(label))]) for label in left_labels}
        )
        inverse = cokernel_after_completion.module_category().Mor(cokernel_after_completion, completed_cokernel)(
            {label: completed_cokernel.module_generator(left_labels[int(right_labels.ranking_map()(label))]) for label in right_labels}
        )
        return completed_cokernel.module_category().Core().Mor(
            completed_cokernel,
            cokernel_after_completion,
        )(forward, inverse)

    def _is_the_identity(self) -> bool:
        r"""Return whether the retained scalar datum establishes the identity."""
        if self.domain() is not self.codomain():
            return False
        from sage_extensions.categories.group.additive_mors import (
            _scalar_identity_coefficient,
        )

        scalar = _scalar_identity_coefficient(self, self.parent())
        return scalar is not None and (scalar == self.parent().base_ring().one()) is True

    def __mul__(self, other):
        r"""Return ``self . other`` for a composable arrow, or ``other * self`` for a scalar."""
        match other:
            case _ if _precomposable(self, other):
                if other.parent() is self.parent() and self.domain() is self.codomain():
                    return self.parent()._compose_endomorphisms(self, other)
                source = other.domain()
                target = self.codomain()
                # The identity is a two-sided unit.  That is a theorem, so the
                # composite is the other factor itself rather than a fresh
                # morphism that would then have to be compared with it.
                if self._is_the_identity() is True:
                    return other
                if other._is_the_identity() is True:
                    return self
                # Keep the Mor theory in which both arrows were admitted.
                # Redispatching Modules(R) from the source's scalar ring can
                # select a stricter chosen-action category on a group algebra,
                # even when this composite is an ordinary R-linear map.
                mor = self.parent().mor_category().Mor(source, target)
                # Composition of linear maps is linear.  Keep that theorem as
                # construction data instead of rebuilding the composite from
                # all selected generator images and rechecking the source
                # relations.
                return mor.element_class(
                    mor,
                    lambda element: self(other(element)),
                    elementwise=True,
                    linearity_premises=(self, other),
                )
            case _ if other in self.parent().base_ring():
                return self.parent().scalar_multiple(other, self)
            case _:
                return NotImplemented

    @cached_method
    def cokernel(self):
        r"""Return the selected quotient ``codomain(self) / image(self)``.

        Scalar extension is right exact, so the cokernel of a completed
        morphism is the completion of the cokernel of its preimage.
        """
        self._require_established_linearity("cokernel construction")
        from sage_extensions.categories.rings.commutative_algebra import (
            AdicCompletions,
        )

        extended_ring = self._flat_scalar_extension_ring()
        match extended_ring:
            case _ if extended_ring is not None and extended_ring in AdicCompletions():
                return self._scalar_extension_functor(self._scalar_extension_of.cokernel())
        quotient = self.codomain()._represented_cokernel_of_morphism(self)
        if quotient is NotImplemented:
            quotient = self.domain()._represented_cokernel_of_morphism(self)
        assert quotient is not NotImplemented, (
            f"cannot compute the cokernel of {self.domain()} -> {self.codomain()}: no algorithm is available for these "
            f"modules (domain in {self.domain().category()}, codomain in {self.codomain().category()})"
        )
        return quotient

    @cached_method
    def cokernel_projection(self):
        r"""Return the quotient map ``q : B -> coker(self)``.

        The cokernel is presented on the generators of the codomain, with the
        images of this morphism added as relations.  So the quotient map sends
        each generator to the generator of the same name, and no second model
        of the quotient is built to state it.
        """
        quotient = self.cokernel()
        codomain = self.codomain()
        return codomain.module_category().Mor(codomain, quotient)(lambda label: quotient.module_generator(label))

    def section(self):
        r"""Return ``s`` with ``self . s`` the identity when the represented codomain is projective.

        A section chooses one preimage of each generator of the codomain.
        Those choices assemble into a morphism exactly when the codomain is
        free on those generators, since then there is no relation for them to
        respect.  A represented finitely presented projective module over a PID
        is first carried through its existing finite-free trivialization; this
        is the same projectivity argument in a basis supplied by the module's
        invariant-factor presentation, rather than an assumption that its
        selected presentation generators are a basis.
        """

        self._require_established_linearity("splitting an epimorphism")
        codomain = self.codomain()
        assert self.is_surjective(), (
            f"{self.domain()} -> {codomain} has no section: a section exists only for a surjective map, and this "
            "map has nonzero cokernel"
        )
        match codomain:
            case _ if _has_finite_free_framing(codomain):
                return codomain.module_category().Mor(codomain, self.domain())(
                    lambda label: self.lift(codomain.module_generator(label))
                )
            case _:
                from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
                    _SelectedFinitePresentationModules,
                )

                represented_presentations = _SelectedFinitePresentationModules(codomain.base_ring())
                assert codomain in represented_presentations and codomain.is_projective(), (
                    f"cannot construct a section of {self.domain()} -> {codomain}: the codomain must carry either "
                    "a chosen finite free basis or a represented finite projective presentation, "
                    f"but {codomain} is in {codomain.category()}"
                )
                trivialization = codomain.finite_free_trivialization()
                transported = trivialization.forward() * self
                return transported.section() * trivialization.forward()

    def retraction(self):
        r"""Return ``r`` with ``r . self`` the identity, for a split monomorphism.

        Splitting ``i : A -> B`` is the same as splitting the quotient
        ``q : B -> B/i(A)``.  Given a section ``s`` of ``q``, each ``b``
        differs from ``s(q(b))`` by an element of ``i(A)``, and ``i`` is
        injective, so ``r(b) = i^{-1}(b - s(q(b)))`` is well defined and
        restricts to the identity on ``A``.  The section exists when the
        cokernel is free, which over a principal ideal domain is exactly when
        this monomorphism splits.
        """

        self._require_established_linearity("splitting a monomorphism")
        assert self.is_injective(), (
            f"{self.domain()} -> {self.codomain()} has no retraction: a retraction exists only for an injective map, "
            "and this map has nonzero kernel"
        )
        quotient_map = self.cokernel_projection()
        splitting = quotient_map.section()
        codomain = self.codomain()

        def image(label):
            generator = codomain.module_generator(label)
            return self.lift(generator - splitting(quotient_map(generator)))

        return codomain.module_category().Mor(codomain, self.domain())(image)

    def inverse(self):
        r"""Return the two-sided inverse in the same module category.

        An inverse of ``f : M -> N`` in ``R``-modules is a morphism
        ``N -> M`` over the same coefficient ring ``R``.  A coordinate matrix
        may be invertible after scalar extension without ``f`` being an
        isomorphism in ``R``-modules; that fraction-field inverse is a different
        construction and is never returned here.
        """
        self._require_established_linearity("module-morphism inversion")
        assert self.is_injective(), (
            f"{self.domain()} -> {self.codomain()} has no inverse: it is not injective"
        )
        assert self.is_surjective(), (
            f"{self.domain()} -> {self.codomain()} has no inverse: it is not surjective"
        )
        codomain = self.codomain()
        inverse_image = self.lift if _has_finite_free_framing(self.domain()) else self.preimage
        return codomain.module_category().Mor(codomain, self.domain())(
            lambda label: inverse_image(codomain.module_generator(label))
        )

    def as_automorphism(self):
        r"""Return this invertible endomorphism as an element of ``Aut_R(M)``.

        An automorphism is not a kind of morphism; it is an element of the
        automorphism group the Mor packet gives the module.  This states the
        endomorphism together with the inverse it constructs, which is what
        that group's elements are.
        """
        from sage_extensions.categories.modules.pure.modules import Modules

        module = self.domain()
        assert self.codomain() is module, (
            f"{module} -> {self.codomain()} is not an automorphism: its domain and codomain must be the same module"
        )
        return Modules(module.base_ring()).Aut(module)._from_inverse_computation(
            self,
            self.inverse,
        )


def _combined_linearity_decision(morphisms):
    r"""Conjoin the linearity decisions of the morphisms of ``morphisms``.

    An infinite family answers the proposition that every member is linear.
    """
    match morphisms:
        case IndexedFamily():
            size = morphisms.cardinality()
            if not size.is_finite():
                return AtomicProposition("are_linear", morphisms)
        case _:
            pass
    return conjunction(morphism.linearity_decision() for morphism in morphisms)


class ModuleMorphism(ModuleMorphismMethods, Morphism):
    r"""Compatibility shell for private realizations not yet moved to generated Mor types."""

    def _initialize_lower_arrow(self, parent) -> None:
        Morphism.__init__(self, parent)


class FramingMorphism(ModuleMorphism):
    r"""A constructor-selected generating epimorphism from a free module."""

    def __init__(self, parent, generator_morphism) -> None:
        match generator_morphism.codomain() is parent.codomain():
            case False:
                raise ValueError(
                    f"the generator map inducing {parent.domain()} -> {parent.codomain()} "
                    f"must land in {parent.codomain()}, but it lands in "
                    f"{generator_morphism.codomain()}"
                )
            case True:
                pass
        super().__init__(parent, generator_morphism)

    def lift(self, element):
        r"""The preimage of ``element`` in the free module that the codomain's construction chose.

        On a basis it is the unique preimage, the coordinate vector.  The
        construction that produced the codomain's elements chose it, so it is
        not recombined and compared here.
        """
        codomain = self.codomain()
        return codomain._framing_lift(codomain(element))

    def is_surjective(self) -> bool:
        r"""True: the codomain's framing coefficients supply a preimage in the selected free source."""
        return True


class ModuleEmbeddingMethods:
    r"""An injective module morphism: an element of the monomorphisms ``Mono_R(M, N)``.

    Membership states injectivity, so :meth:`is_injective` answers by
    placement; :meth:`validate_injectivity` computes the kernel when asked
    (``OWN-22``).

    An embedding built by a construction of its Mor takes
    ``injectivity_premises``: the family of maps from which the construction
    builds it, so that it is injective when every premise is, the empty
    family meaning the construction alone makes it injective.  It may also
    take ``lift_is_section``: the construction's statement that its selected
    lift returns a preimage exactly on the image.
    """

    _injectivity_premises = None
    _lift_is_section = None

    def __init__(
        self,
        parent,
        images,
        *,
        injectivity_premises=None,
        lift_is_section=None,
        **construction,
    ) -> None:
        self._injectivity_premises = injectivity_premises
        self._lift_is_section = lift_is_section
        super().__init__(parent, images, **construction)

    def _injectivity_derivation(self):
        r"""Return the injectivity decision the construction gives, or ``None``."""
        match self._injectivity_premises:
            case None:
                return None
            case premises:
                return conjunction(premise.is_injective() for premise in premises)

    def _selected_lift_derivation(self):
        r"""Return whether the construction states its selected lift is a section, or ``None``."""
        return self._lift_is_section

    def is_injective(self) -> bool:
        r"""True: an element of ``Mono_R(M, N)`` is injective by its placement."""
        return True

    @validator
    def validate_injectivity(self) -> None:
        r"""Raise ``ValueError`` unless ``ker(f) = 0`` is established.

        A construction that derives injectivity (a subobject inclusion, a
        localization of a monomorphism) answers at once; otherwise the map is
        read in ``Mor_R(M, N)`` and its kernel is computed.
        """
        decision = self._injectivity_derivation()
        match decision:
            case None:
                linear = self.domain().module_category().Mor(self.domain(), self.codomain())(self)
                decision = linear.is_injective()
            case _:
                pass
        if decision is False:
            raise ValueError(f"{self.domain()} -> {self.codomain()} is not an injective linear map: its kernel is nonzero")
        if decision is not True:
            raise ValueError(f"cannot accept {self.domain()} -> {self.codomain()} as an injective linear map: its injectivity cannot be decided")


class ModuleEmbeddingMor(CategoricalMor):
    r"""The declared monomorphisms between two modules over one scalar ring."""

    ElementMethods = ModuleEmbeddingMethods

    def __init__(self, mor_family, domain, codomain) -> None:
        modules = domain.module_category()
        assert domain in modules and codomain in modules, (
            f"cannot form the injective linear maps {domain} -> {codomain}: both must be modules in {modules}, "
            f"but they are in {domain.category()} and {codomain.category()}"
        )
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def _element_constructor_(self, images, *, lift=None, check=False):
        r"""Construct the monomorphism with these images; ``check=True`` runs its validators (``OWN-22``)."""
        generator_map = (
            isinstance(images, (SetMorphism, CategoricalArrow))
            and self.domain().has_selected_module_resolution()
            and images.domain() is self.domain().module_generating_set()
            and images.codomain() is self.codomain()
        )
        if isinstance(images, (Map, CategoricalArrow)) and not generator_map:
            if images.domain() is not self.domain() or images.codomain() is not self.codomain():
                raise ValueError(f"cannot regard {images.domain()} -> {images.codomain()} as an injective linear map {self.domain()} -> {self.codomain()}: the domains and codomains differ")
            if self._already_parented_arrow(images):
                return images
            _refuse_foreign_arrow(
                self, images, "construct the monomorphism from its generator images, with its selected lift"
            )
        embedding = self.element_class(self, images, lift=lift)
        embedding.validate_linearity(check=check)
        embedding.validate_lift(check=check)
        embedding.validate_injectivity(check=check)
        return embedding

    def _from_constructed_embedding(
        self,
        datum,
        premises=(),
        *,
        elementwise=True,
        lift=None,
        lift_is_section=None,
        scalar_extension_of=None,
        scalar_extension_functor=None,
    ):
        r"""The monomorphism of a construction that makes it linear and injective when the maps of ``premises`` are.

        ``datum`` is a function on elements, or with ``elementwise=False`` the
        images of the domain framing.  The empty family means the construction
        alone makes the map a monomorphism: the inclusion of a subobject, of a
        homogeneous piece into its graded algebra, of a fractional ideal into
        ``Frac(R)``, the free module on an injection of framings.  The
        localization ``S^{-1} f`` of a monomorphism ``f`` has the premise
        ``f``, since localization is exact.  ``lift_is_section`` states that
        the construction's selected lift returns a preimage exactly on the
        image.

        Protected construction contract (``OWN-05``).  Owner: this Mono
        category, ``ModuleEmbeddingMor``.  Purpose: admit the monomorphism
        that a construction defines, with its linearity and injectivity
        carried by the construction (``premises``) rather than computed,
        since the public element constructor admits a map by the caller's
        claim and leaves both to its validators (``OWN-22``).  Input: the
        defining map on elements (or generator images), the premise
        monomorphisms, an optional selected lift.  Output: an element of
        this Mono category with exactly these endpoints.  Invariant: the
        caller's construction makes the map linear and injective whenever
        the premises are.  Permitted callers, each the owner of the
        construction whose structure map it is:

        - ``_subobject_inclusion`` here, the inclusion of a module subobject
          given by generator images;
        - ``Modules.ParentMethods.sub_framing_morphism``
          (``modules/pure/modules.py``), the free functor on an injection of
          framings;
        - the condition-submodule construction ``_condition_submodule_object``
          (``modules/general_modules.py``), the inclusion of
          ``{x in M : P(x)}`` into ``M``, which is the inclusion of a subset
          of the underlying set of ``M`` and so injective;
        - the homogeneous-piece inclusion of ``modules/powers.py``;
        - the fractional-ideal inclusion into ``Frac(R)`` of
          ``modules/fractional_ideals.py``;
        - the nondegenerate correlation of ``modules/hodge.py``;
        - module localization, ``functors/module_localization.py``, with the
          localized monomorphism as premise.

        A new caller is added to this list at the same time, with the
        construction that makes its map a monomorphism.
        """
        return self.element_class(
            self,
            datum,
            elementwise=elementwise,
            lift=lift,
            linearity_premises=premises,
            injectivity_premises=premises,
            lift_is_section=lift_is_section,
            scalar_extension_of=scalar_extension_of,
            scalar_extension_functor=scalar_extension_functor,
        )

    def _subobject_inclusion(self, images, *, lift=None):
        r"""The inclusion carried by an owned module-subobject datum; its selected lift is part of that datum."""
        return self._from_constructed_embedding(
            images,
            elementwise=False,
            lift=lift,
            lift_is_section=True,
        )

    def base_ring(self):
        return self.domain().base_ring()

    def scalar_multiple(self, scalar, morphism):
        r"""Scale an embedding in the underlying linear Mor.

        A scalar multiple of an injective map need not remain injective, so
        this operation deliberately returns through ``Mor_R`` rather than the
        Mono parent.
        """
        source = self.domain()
        target = self.codomain()
        return source.module_category().Mor(source, target).scalar_multiple(
            scalar,
            morphism,
        )

    def super_categories(self):
        packet = self.base_category().category_packet()
        source = self.domain()
        target = self.codomain()
        inherited = [
            superpacket.Monos().Of(source, target)
            for superpacket in packet.super_packets()
            if source in superpacket.C() and target in superpacket.C()
        ]
        return [packet.Mors().Of(source, target), *inherited]

    def _repr_(self):
        return f"Emb({self.domain()}, {self.codomain()})"


def _initialize_module_mor_parent(
    parent,
    mor_family,
    domain,
    codomain,
    *,
    full_internal_mor=False,
    full_linear_mor=True,
) -> None:
    r"""Install the common enriched ``R``-module Mor parent semantics.

    This is implementation reuse only.  Structured Mor categories such as
    ``Hom_{R[G]}`` must not subclass ``Hom_R`` as Python classes merely because
    they have ``Hom_R`` as a categorical supercategory.

    ``full_linear_mor`` records whether this constructor supplies a
    full-linear-Hom realization. Graded and cochain maps pass ``False``:
    their extra equations may cut down the Hom, so endpoint bases alone
    do not supply a full-Hom basis. This withholds that representation
    claim without deciding inequivalence or proving an arrow law.
    """
    modules = mor_family.base_category()
    ring = modules.base_ring()
    assert domain in modules and codomain in modules, (
        f"cannot form the linear maps {domain} -> {codomain} in {modules}: both must be objects of {modules}, but they are in {domain.category()} and {codomain.category()}"
    )
    placement = domain.module_category()._mor_parent_placement(
        domain,
        codomain,
        full_internal_mor=full_internal_mor,
        full_linear_mor=full_linear_mor,
    )
    from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
        _SelectedFinitePresentationModules,
        _fix_lazy_selected_module_presentation,
    )
    from sage_extensions.categories.modules.pure.modules import (
        MatrixSpaces,
        _fix_selected_module_resolution,
        _matrix_unit,
    )

    # Fix the choice of every selected resolution before the Mor is
    # constructed in its placement.  A represented internal-Hom presentation is
    # endpoint-determined but potentially expensive, so its factory is fixed
    # here and its model is realized only on the first module-data read.
    match placement:
        case _ if ring in OwnedRings().Commutative() and placement.is_subcategory(MatrixSpaces(ring)):
            # ``Hom_R(F_R(S), F_R(T))`` is free on the matrix units ``T x S``.
            labels = codomain.module_generating_set().product_with(domain.module_generating_set())
            _fix_selected_module_resolution(
                parent,
                ring,
                labels,
                lambda label: _matrix_unit(parent, label),
                lambda: ring._fresh_free_module_on(labels),
            )
        case _ if placement.is_subcategory(_SelectedFinitePresentationModules(ring)):
            def selected_presentation_data():
                from sage_extensions.categories.modules.internal_mor import (
                    _internal_mor_model_data_from_endpoints,
                )

                model, _inclusion, presentation = _internal_mor_model_data_from_endpoints(
                    domain,
                    codomain,
                )
                labels = model.module_generating_set()
                generator_morphism = Sets().Mor(labels, parent)(
                    lambda label: parent._morphism_from_internal_model(
                        model.module_generator(label)
                    )
                )
                return presentation, labels, generator_morphism

            _fix_lazy_selected_module_presentation(
                parent,
                ring,
                selected_presentation_data,
            )

    # Hom_R(M, N) is a module over the center of R.  ``Modules.ParentMethods``
    # reads that scalar ring from ``_preamble_base_ring``; the Sage Homset
    # base stays unset.
    parent._preamble_base_ring = ring.ring_center()
    CategoricalMor.__init__(
        parent,
        mor_family,
        domain,
        codomain,
        category=placement,
    )

class _ModuleMorCommonMethods:
    r"""Python implementation shared by module-enriched Mor parents.

    This is not a mathematical Mor category.  Concrete Mor parents remain
    distinct categories and use this class only to share ordinary module-Mor
    operations.
    """

    def base_ring(self):
        r"""The center of ``R``, over which ``Hom_R(M, N)`` is a module.

        ``_initialize_module_mor_parent`` stores it before ``CategoricalMor``
        constructs this Mor in its placement; ``Modules`` reads the same
        datum once that placement is realized.
        """
        return self._preamble_base_ring

    def _from_constructed_element_map(self, function, premises=()):
        r"""The elementwise map of a construction that makes it linear when the maps of ``premises`` are.

        The empty family means the construction alone makes it linear, as
        for a unit or counit given by its defining formula.  The image of a
        linear map ``f`` under a functor has the premise ``f``.
        """
        if not callable(function):
            raise TypeError(
                f"a constructed linear map {self.domain()} -> {self.codomain()} needs a function on elements, "
                f"but got {function!r}"
            )
        return self.element_class(
            self,
            function,
            elementwise=True,
            linearity_premises=premises,
        )

    def _element_constructor_(self, images, *, check=False):
        r"""Construct the linear map with these images; ``check=True`` runs its validators (``OWN-22``).

        The map on the chosen generating set is defining data. A map on the
        whole underlying set is not a linear-map datum (``CON-17``).

        Unverified separating specimen::

            sage: from dzack_research.preamble.all import *
            sage: M = ZZ.free_module(Sets.Δ[1])
            sage: e = M.module_generator(0)
            sage: f = M.End()(lambda label: M.module_generator(label) + e)
            sage: U = Modules(ZZ).underlying_set()
            sage: assert U(f).parent() is Sets().Mor(U(M), U(M))
            sage: assert U(f)(e) == 2*e
            sage: assert M.End()(f) is f
            sage: translation = Sets().Mor(M, M)(lambda v: v + e)
            sage: M.End()(translation)
            Traceback (most recent call last):
            ...
            TypeError: ...
        """
        from sage_extensions.categories.modules.pure.modules import MatrixSpaces

        if (
            self in MatrixSpaces(self.base_ring())
            and isinstance(images, (tuple, list))
            and len(images) == self.nrows()
            and all(isinstance(row, (tuple, list)) for row in images)
        ):
            return self.from_rows(images)
        generator_map = (
            isinstance(images, (SetMorphism, CategoricalArrow))
            and self.domain().has_selected_module_resolution()
            and images.domain() is self.domain().module_generating_set()
            and images.codomain() is self.codomain()
        )
        if isinstance(images, ModuleMorphismMethods):
            if images.domain() is not self.domain() or images.codomain() is not self.codomain():
                raise ValueError(f"cannot regard {images.domain()} -> {images.codomain()} as a linear map {self.domain()} -> {self.codomain()}: the domains and codomains differ")
            if self._already_parented_arrow(images):
                return images
            _refuse_foreign_arrow(
                self, images, "apply the functor changing the module category, or supply the defining generator images"
            )
        elif isinstance(images, (Map, CategoricalArrow)) and not generator_map:
            if images.domain() is not self.domain() or images.codomain() is not self.codomain():
                raise ValueError(f"cannot regard {images.domain()} -> {images.codomain()} as a linear map {self.domain()} -> {self.codomain()}: the domains and codomains differ")
            # A set map, group map or other non-linear arrow of these
            # endpoints: almost none is linear, so it is not read here as one.
            _refuse_foreign_arrow(
                self, images, "a linear map is given by the images of the module generators or by its "
                "function on elements, whose linearity is its validator"
            )
        base_ring = self.base_ring()
        image_data = isinstance(
            images,
            (SetMorphism, IndexedFamily, dict, tuple, list),
        )
        if self.domain() is self.codomain() and not image_data:
            try:
                scalar = base_ring(images)
            except (TypeError, ValueError):
                pass
            else:
                return self.scalar_multiple(scalar, self.identity())
        from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
            _SelectedFinitePresentationModules,
        )

        # Generator images, or a function giving them, store their data and
        # build no model of Hom_R(M, N); the relation check is
        # ``validate_linearity`` (``OWN-22``).  Only an element of the model
        # is read through it.
        if (
            not image_data
            and not callable(images)
            and self in _SelectedFinitePresentationModules(base_ring)
            and images in self._internal_mor_model()
        ):
            return self._morphism_from_internal_model(self._internal_mor_model()(images))
        morphism = self.element_class(self, images)
        morphism.validate_linearity(check=check)
        return morphism

    def _apply_pointwise_scalar(self, scalar, element):
        center = self.base_ring()
        ring = self.codomain().base_ring()
        coefficient = center(scalar)
        match center is ring:
            case True:
                pass
            case False:
                if ring.ring_center() is not center:
                    raise TypeError(
                        f"the scalars of {self} lie in {center}, which is not the selected centre of {ring}"
                    )
                # The enrichment retained this literal ring centre. The
                # general magma/algebra centre may have another realization.
                inclusion = center.inclusion()
                if inclusion.domain() is not center or inclusion.codomain() is not ring:
                    raise TypeError(
                        f"the selected centre inclusion {inclusion} must have endpoints {center} -> {ring}"
                    )
                coefficient = inclusion(coefficient)
        return self.codomain().scalar_multiple(coefficient, element)

    def _scalar_identity(self, scalar):
        r"""The endomorphism ``r . id``, linear by the module axioms."""
        from sage_extensions.categories.group.additive_mors import _ScalarIdentityEvaluation

        return self.element_class(
            self,
            _ScalarIdentityEvaluation(self, scalar),
            elementwise=True,
            linearity_premises=(),
        )

    def _compose_module_endomorphisms(self, left, right):
        r"""Compose two endomorphisms; the composite's linearity decision conjoins theirs."""
        from sage_extensions.categories.group.additive_mors import (
            _scalar_identity_coefficient,
        )

        left_scalar = _scalar_identity_coefficient(left, self)
        right_scalar = _scalar_identity_coefficient(right, self)
        if left_scalar is not None and right_scalar is not None:
            return self._scalar_identity(left_scalar * right_scalar)
        return self.element_class(
            self,
            lambda element: left(right(element)),
            elementwise=True,
            linearity_premises=(left, right),
        )

    def _compose_endomorphisms(self, left, right):
        return self._compose_module_endomorphisms(left, right)

    def _module_scalar_multiple(self, scalar, morphism):
        r"""Realize the pointwise action ``(r f)(m) = r f(m)`` defining this Mor's scalar enrichment."""
        if morphism not in self:
            raise TypeError(
                f"scalar multiplication in {self} needs an arrow already admitted there"
            )
        if morphism.parent() is not self:
            morphism = self(morphism)
        scalar = self.base_ring()(scalar)
        from sage_extensions.categories.group.additive_mors import _scalar_identity_coefficient

        coefficient = _scalar_identity_coefficient(morphism, self)
        if coefficient is not None:
            return self._scalar_identity(scalar * coefficient)
        return self.element_class(
            self,
            lambda element: self._apply_pointwise_scalar(scalar, morphism(element)),
            elementwise=True,
            linearity_premises=(morphism,),
        )

    def _owned_scalar_multiple(self, scalar, morphism):
        return self._module_scalar_multiple(scalar, morphism)

    def elementwise(self, function):
        r"""Construct a declared linear map from its action on arbitrary elements.

        Exact verification is performed when the represented source/scalar
        underlying sets make it decidable (notably finite ones).  Otherwise the
        linearity decision is the proposition ``is_linear(f)`` and a DEBUG
        diagnostic records that no decision procedure was available.  For finitely
        generated/presented objects, prefer the
        generator-assignment constructor when possible: its linear extension
        is linear by construction and presentation relations are checked.
        """
        if isinstance(function, (Map, CategoricalArrow)):
            return self(function)
        if not callable(function):
            raise TypeError(f"cannot define a linear map {self.domain()} -> {self.codomain()} elementwise from {function!r}: it must be a function on elements")
        morphism = self.element_class(
            self,
            function,
            elementwise=True,
        )
        # ``elementwise`` explicitly claims that this callable is a map on
        # arbitrary module elements.  Run the available decision procedure at
        # that boundary so a witnessed law failure is refused immediately.
        # An undecidable law remains the proposition ``is_linear(f)`` carried
        # by the arrow; it is not promoted to a proof or rejected merely for
        # lacking a finite decision procedure.
        morphism.linearity_decision()
        return morphism

    def _product_projection(self, underlying_projection):
        r"""The projection of a product whose module operations are componentwise, linear by that construction."""
        codomain = self.codomain()
        return self.element_class(
            self,
            lambda element: codomain(underlying_projection(element.underlying_element())),
            elementwise=True,
            linearity_premises=(),
        )

    def _product_factor(self, underlying_factor, legs):
        r"""The factor induced by a cone into a componentwise module product; linear when its legs are."""
        codomain = self.codomain()
        return self.element_class(
            self,
            lambda element: codomain(underlying_factor(element)),
            elementwise=True,
            linearity_premises=legs,
        )

    def _equalizer_inclusion(self, underlying_inclusion, parallel_maps):
        r"""The inclusion of the equalizer of ``parallel_maps``; linear when the parallel maps are."""
        codomain = self.codomain()
        return self.element_class(
            self,
            lambda element: codomain(underlying_inclusion(element.underlying_element())),
            elementwise=True,
            linearity_premises=parallel_maps,
        )

    def _equalizer_factor(self, source_leg, *, inclusion=None):
        r"""The unique factor of ``source_leg`` through a represented module equalizer.

        It is ``source_leg`` read in the equalizer, or lifted through
        ``inclusion`` when one is given, and linear when those maps are.
        """
        codomain = self.codomain()
        match inclusion:
            case None:
                return self.element_class(
                    self,
                    lambda element: codomain(source_leg(element)),
                    elementwise=True,
                    linearity_premises=(source_leg,),
                )
            case _:
                return self.element_class(
                    self,
                    lambda element: inclusion.lift(source_leg(element)),
                    elementwise=True,
                    linearity_premises=(source_leg, inclusion),
                )

    def zero(self):
        r"""The zero map ``m -> 0``, linear by the module axioms."""
        if self.domain() is self.codomain():
            return self._scalar_identity(self.base_ring().zero())
        codomain = self.codomain()
        return self.element_class(
            self,
            lambda _element: codomain.zero(),
            elementwise=True,
            linearity_premises=(),
        )

    @cached_method
    def identity(self):
        r"""Return the identity of this endomorphism Mor.

        A Mor object has one identity.  Returning a fresh morphism on each call
        makes it incomparable with itself, since module-morphism equality is
        not decidable without a chosen finite presentation of the source.
        """
        if self.domain() is not self.codomain():
            raise ValueError(f"there is no identity map {self.domain()} -> {self.codomain()}: the domain and codomain are different modules")
        return self._scalar_identity(self.base_ring().one())

    def one(self):
        r"""Return the multiplicative unit when this is an endomorphism ring."""
        return self.identity()


class _AuxiliaryLinearModuleMor(_ModuleMorCommonMethods, CategoricalMor):
    r"""Private linear-Mor parent used while realizing an internal Mor module.

    This parent represents a linear arrow space needed by an algorithm.  It is
    deliberately placed only in ``LinearMorModules(R)`` and therefore cannot
    recursively demand another internal-Mor module presentation.
    """

    ElementMethods = ModuleMorphismMethods

    def __init__(self, domain, codomain) -> None:
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(_owned_ring(domain.base_ring()))
        _initialize_module_mor_parent(
            self,
            modules.MorCategory(),
            domain,
            codomain,
            full_internal_mor=False,
        )

    def __call__(self, images):
        return CategoricalMor.__call__(self, images)


def _auxiliary_linear_module_mor(domain, codomain):
    return _AuxiliaryLinearModuleMor(domain, codomain)


class ModuleMor(_ModuleMorCommonMethods, CategoricalMor):
    ElementMethods = ModuleMorphismMethods

    def __init__(self, mor_family, domain, codomain) -> None:
        _initialize_module_mor_parent(
            self,
            mor_family,
            domain,
            codomain,
            full_internal_mor=True,
        )

    def __call__(self, images):
        r"""Construct a module morphism without Sage coercion discovery."""
        return CategoricalMor.__call__(self, images)

    def _from_scalar_extension(self, morphism, datum, functor, *, elementwise=False):
        r"""``S tensor_R f`` for ``f = morphism``, given by its images on the extended framing or on elements.

        Scalar extension is a functor on linear maps, so ``S tensor_R f`` is
        linear exactly when ``f`` is.  A localization ``S^{-1} f`` is the
        scalar extension along ``R -> S^{-1}R``.
        """
        return self.element_class(
            self,
            datum,
            elementwise=elementwise,
            scalar_extension_of=morphism,
            scalar_extension_functor=functor,
            linearity_premises=(morphism,),
        )

    def presentation_matrix(self):
        r"""Return the relation morphism of the presented model of this Mor module as a type-``(1,1)`` tensor."""
        from sage_extensions.tensors.tensor import tensor

        return tensor.from_morphism(self.presentation())

    def presentation(self):
        r"""Return the presentation of the presented model of this Mor module."""
        from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
            _SelectedFinitePresentationModules,
        )

        match self in _SelectedFinitePresentationModules(self.base_ring()):
            case True:
                selected = self.selected_module_resolution()
                return selected.differential(1)
            case False:
                from sage_extensions.categories.modules.internal_mor import (
                    _internal_mor_model_data,
                )

                _model, _inclusion, presentation = _internal_mor_model_data(self)
                return presentation

    def _repr_(self):
        return f"Mor({self.domain()}, {self.codomain()})"


def _framing_morphism(codomain, domain, generator_morphism) -> FramingMorphism:
    from sage_extensions.categories.modules.pure.modules import Modules
    from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing

    # A framing is linear over the scalar ring, not a map required to retain
    # a chosen group action. Its free source need not be in the specialized
    # category Modules(R[G]), although both endpoints are ordinary R[G]-modules.
    modules = OwnedCategoryOverBaseRing.__classcall__(Modules, domain.base_ring())
    mor = modules.Mor(domain, codomain)
    return FramingMorphism(mor, generator_morphism)


class TensorProductModuleMorphismMethods:
    r"""A linear map out of a chosen tensor product, hence a bilinear map.

    A map stated by a two-variable evaluation ``b`` keeps ``b``: its values
    on the selected tensor framing are its generator images, and it answers
    ``f(x, y)`` with ``b(x, y)``.  A Python callable does not establish that
    its values on arbitrary factor elements agree with that bilinear
    extension, so unless the construction supplies it as a premise, the
    linearity decision is the proposition ``is_linear(f)`` once the framing
    values kill the selected tensor relations.
    """

    _bilinear_evaluation = None
    _defining_pairing_tensor = None
    _pullback_form = None
    _pullback_morphism = None
    _defining_pairing_values = None

    def __init__(
        self,
        parent,
        images,
        *,
        elementwise=False,
        scalar_extension_of=None,
        scalar_extension_functor=None,
        lift=None,
        linearity_premises=None,
        bilinear_evaluation=None,
    ) -> None:
        self._bilinear_evaluation = bilinear_evaluation
        super().__init__(
            parent,
            images,
            elementwise=elementwise,
            scalar_extension_of=scalar_extension_of,
            scalar_extension_functor=scalar_extension_functor,
            lift=lift,
            linearity_premises=linearity_premises,
        )

    def _generator_image_linearity_derivation(self):
        decision = super()._generator_image_linearity_derivation()
        match self._bilinear_evaluation:
            case None:
                return decision
            case _:
                return AtomicProposition("is_linear", self)

    @cached_method
    def left_module(self):
        return self.domain().tensor_factor(0)

    @cached_method
    def right_module(self):
        return self.domain().tensor_factor(1)

    @cached_method
    def module(self):
        if self.left_module() is not self.right_module():
            raise TypeError(f"the pairing {self.left_module()} x {self.right_module()} -> {self.codomain()} is not a bilinear form on one module: its two arguments lie in different modules")
        return self.left_module()

    def __call__(self, *arguments):
        if len(arguments) == 1:
            return self._call_(arguments[0])
        if len(arguments) == 2 and self._bilinear_evaluation is not None:
            left, right = arguments
            value = self._bilinear_evaluation(self.left_module()(left), self.right_module()(right))
            return value if element_parent(value) is self.codomain() else self.codomain()(value)
        if len(arguments) == 2 and self._generator_image is not None:
            return self._evaluate_by_bilinearity(*arguments)
        if len(arguments) == 2:
            return self._call_(self.domain().pure_tensor(*arguments))
        raise TypeError(f"the bilinear map on {self.domain()} takes one element of the tensor product or two elements, one from each factor, but was given {len(arguments)} arguments")

    def _evaluate_by_bilinearity(self, left_element, right_element):
        r"""``b(x, y) = sum_{l, r} x_l y_r b(e_l tensor e_r)`` for a map given on the tensor framing.

        The framing of the tensor product is the set of pure tensors
        ``e_l tensor e_r``, so the linear extension of the generator images
        evaluated at ``x tensor y`` is this double sum.  Reading it from the
        images directly leaves the pure tensor, an element of the tensor
        product, unbuilt.
        """
        codomain = self.codomain()
        left_coordinates = self.left_module().framing_morphism().lift(left_element)
        right_coordinates = self.right_module().framing_morphism().lift(right_element)
        left_coefficients = left_coordinates.parent()._selected_module_coefficients(left_coordinates)
        right_coefficients = right_coordinates.parent()._selected_module_coefficients(right_coordinates)
        value = codomain.zero()
        for left_label, left_coefficient in left_coefficients.items():
            for right_label, right_coefficient in right_coefficients.items():
                value = value + codomain.scalar_multiple(
                    left_coefficient * right_coefficient,
                    self._gram_entry(left_label, right_label),
                )
        return value

    def coordinate_values(self):
        if self._defining_pairing_values is not None:
            return self._defining_pairing_values
        labels = self.domain().module_generating_set()
        return indexed_family(
            labels,
            lambda pair: self(
                self.left_module().module_generator(pair.component(0)),
                self.right_module().module_generator(pair.component(1)),
            ),
            name="Bilinear coordinate values",
        )

    @cached_method
    def _as_numerical_tensor(self):
        r"""Read the selected finite coordinate tensor of this bilinear Hom element.

        An admitted type-(0,2) tensor is returned *by identity*.  A Hom
        constructed from a callable retains its morphism as the defining
        datum and only evaluates the generating pairs on this request.  The
        latter finite extraction is cached here, on the Hom element, rather
        than on any formed module or lattice constructed from it.

        An arbitrary ``R``-module ``W`` has no coefficient ring in which to
        construct a scalar tensor; its W-valued coordinate family is the
        corresponding representation.  Both require selected finite
        framings.  This is private because choosing coordinates is not a
        mathematical operation on the underlying Hom object.
        """
        left, right = self.left_module(), self.right_module()
        if not (left.has_selected_module_resolution() and right.has_selected_module_resolution()):
            raise TypeError(
                f"the numerical coordinates of {self} require selected finite generators of both tensor factors"
            )
        left_labels, right_labels = left.module_generating_set(), right.module_generating_set()
        left_size, right_size = left_labels.cardinality(), right_labels.cardinality()
        if not (left_size.is_finite() and right_size.is_finite()):
            raise TypeError(
                f"the numerical coordinates of {self} require finite generator sets, got {left_size} and {right_size}"
            )
        if self._defining_pairing_tensor is not None:
            return self._defining_pairing_tensor
        from sage_extensions.categories.rings.ring_foundation import OwnedRings
        from sage_extensions.tensors.tensor import tensor

        n, m = int(left_size.finite_value()), int(right_size.finite_value())
        if self._pullback_form is not None:
            from sage_extensions.tensors.tensor import Tensor
            from sage_extensions.categories.modules.pure.modules import MatrixSpaces

            original = self._pullback_form._as_numerical_tensor()
            morphism = self._pullback_morphism
            ordinary = morphism.domain().module_category().Mor(morphism.domain(), morphism.codomain())
            if isinstance(original, Tensor) and ordinary in MatrixSpaces(left.base_ring()):
                if morphism.parent() is not ordinary:
                    morphism = ordinary._from_constructed_element_map(morphism, premises=(morphism,))
                return original.pullback(morphism)
        if self.codomain() not in OwnedRings():
            from sage_extensions.categories.modules.pure.modules import RestrictedScalarsModules

            values = self.codomain()
            if values in RestrictedScalarsModules(left.base_ring()):
                scalar_ring = values.module_over_extension()
                if scalar_ring in OwnedRings():
                    # Res_{R -> S}(S)-valued forms carry a selected scalar
                    # extension. Numerical computations use the coefficients
                    # in S, while the Hom itself remains R-linear into W.
                    return tensor(
                        scalar_ring, (), (n, m),
                        (
                            self._gram_entry(left_labels[i], right_labels[j]).underlying_element()
                            for i in range(n)
                            for j in range(m)
                        ),
                    )
            return self.coordinate_values()
        return tensor(
            self.codomain(), (), (n, m),
            (
                self._gram_entry(left_labels[i], right_labels[j])
                for i in range(n)
                for j in range(m)
            ),
        )

    def values_matrix(self):
        r"""Return the pairing values indexed by the two selected framings."""
        from sage_extensions.categories.sets.coordinate_families import (
            _coordinate_family_from_function,
            _finite_framing,
        )

        left_labels = _finite_framing(self.left_module())
        right_labels = _finite_framing(self.right_module())
        return _coordinate_family_from_function(
            left_labels,
            right_labels,
            self.codomain(),
            self._gram_entry,
            name="Pairing values on the selected framings",
        )

    def _gram_entry(self, left_label, right_label):
        r"""``b(e_l, e_r)``, the value of this map at the framing generator ``e_l ⊗ e_r``.

        A map given by its values on the framing of the tensor product reads
        that value; a map given by a function is evaluated.
        """
        # A finite pairing constructed from a covariant coordinate tensor
        # retains exactly that tensor as its generating datum.  Read its
        # components directly instead of recovering them by re-evaluating
        # the classifying morphism on every pair of generators.
        if self._defining_pairing_tensor is not None:
            left_labels = self.left_module().module_generating_set()
            right_labels = self.right_module().module_generating_set()
            value = self._defining_pairing_tensor[
                int(left_labels.ranking_map()(left_label)),
                int(right_labels.ranking_map()(right_label)),
            ]
            return value if element_parent(value) is self.codomain() else self.codomain()(value)
        if self._defining_pairing_values is not None:
            from sage_extensions.categories.modules.pure.modules import _tensor_pair

            labels = self.domain().module_generating_set()
            return self._defining_pairing_values[_tensor_pair(labels, left_label, right_label)]

        from sage_extensions.categories.modules.pure.modules import _tensor_pair

        match self._generator_image:
            case None:
                return self(
                    self.left_module().module_generator(left_label),
                    self.right_module().module_generator(right_label),
                )
            case generator_image:
                labels = self.domain().module_generating_set()
                return generator_image(_tensor_pair(labels, left_label, right_label))

    def norm(self, element):
        if self.left_module() is not self.right_module():
            raise TypeError(f"cannot evaluate b(x, x) for the pairing {self.left_module()} x {self.right_module()} -> {self.codomain()}: its two arguments lie in different modules")
        return self(element, element)

    def pullback(self, morphism):
        if self.left_module() is not self.right_module():
            raise TypeError(f"cannot pull back the pairing {self.left_module()} x {self.right_module()} -> {self.codomain()} along one map: its two arguments lie in different modules")
        if morphism.codomain() is not self.left_module():
            raise ValueError(f"cannot pull back the bilinear form on {self.left_module()} along {morphism.domain()} -> {morphism.codomain()}: the map must land in {self.left_module()}")

        from sage_extensions.categories.modules.pure.modules import Modules

        source = Modules(morphism.domain().base_ring()).tensor_product(
            (morphism.domain(), morphism.domain())
        )
        induced = source.module_category().Mor(source, self.domain())(
            lambda pair: self.domain().pure_tensor(
                morphism(morphism.domain().module_generator(pair.component(0))),
                morphism(morphism.domain().module_generator(pair.component(1))),
            )
        )
        # b o (f tensor f) is the bilinear map with these values on the
        # framing e_i tensor e_j of the source tensor square; constructing it
        # from them makes it an element of that Mor, where a composite whose
        # parent is already that Mor would be returned as a bare composite.
        result = source.module_category().Mor(source, self.codomain())(
            lambda pair: self(induced(source.module_generator(pair)))
        )
        # Retain the defining pullback. A later scalar-coordinate request
        # transports the original tensor instead of expanding nested pure tensors.
        result._pullback_form = self
        result._pullback_morphism = morphism
        return result

    def polar_form(self):
        if self.left_module() is not self.right_module():
            raise TypeError(f"cannot form the polar form of the pairing {self.left_module()} x {self.right_module()} -> {self.codomain()}: its two arguments lie in different modules")
        return self.parent().scalar_multiple(self.domain().base_ring()(2), self)


class TensorProductModuleMorphism(TensorProductModuleMorphismMethods, ModuleMorphism):
    r"""Compatibility shell for private tensor-product arrow realizations."""


class ModuleAutomorphismMethods:
    r"""An invertible module endomorphism, as an element of ``Aut_R(M)``.

    The defining datum is the forward map.  The inverse is computed on the
    first request and cached (``OWN-22``): ``inverse_computation`` is a
    zero-argument callable returning it.
    """

    def __init__(self, parent, forward, inverse_computation) -> None:
        module = parent.domain()
        self._inverse_computation = inverse_computation
        self._forward_module_morphism = module.module_category().Mor(module, module)(forward)
        super().__init__(parent, self._forward_module_morphism)

    @cached_method
    def _inverse_morphism(self):
        r"""The inverse module map, computed once."""
        module = self.domain()
        return module.module_category().Mor(module, module)(self._inverse_computation())

    def forward(self):
        return self._forward_module_morphism

    def as_morphism(self):
        return self.forward()

    def order(self):
        forward = self.forward()
        linear = forward._framed_coordinate_morphism()
        from sage_extensions.categories.modules.pure.modules import MatrixSpaces

        assert linear.parent() in MatrixSpaces(linear.parent().base_ring()), (
            f"cannot compute the order of the automorphism of {forward.domain()}: the order is computed from a matrix, "
            f"so the module must be finitely generated free with a chosen basis, but it is in {forward.domain().category()}"
        )
        return linear.multiplicative_order()

    def _richcmp_(self, other, op):
        r"""Two automorphisms of ``M`` are equal when their forward maps are equal."""
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if self is other:
            return op == op_EQ
        equal = self.forward() == other.forward()
        return equal if op == op_EQ else negation(equal)

    def __hash__(self):
        return hash(id(self.parent()))

    def inverse(self):
        return self.parent()._from_known_inverse_pair(self._inverse_morphism(), self.forward())

    __invert__ = inverse

    def __mul__(self, other):
        r"""The group law ``(g, g^{-1}) (h, h^{-1}) = (gh, h^{-1} g^{-1})``, or ``g . f`` for a module map ``f``."""
        match other:
            case _ if element_parent(other) is self.parent():
                return self.parent()._from_inverse_computation(
                    self.forward() * other.forward(),
                    lambda: other._inverse_morphism() * self._inverse_morphism(),
                )
            case _:
                return self.forward() * other


class ModuleAutomorphism(ModuleAutomorphismMethods, ModuleMorphism):
    r"""Compatibility shell for private module-automorphism realizations."""


def _flag_stabilizer_engine_data(automorphisms, terms):
    r"""Private engine adapter of ``ModuleAutomorphismGroup`` (``OWN-05``, ``OWN-06``).

    Owner: the module automorphism group; only caller:
    ``ModuleAutomorphismGroup.flag_stabilizer``.  It lowers the flag's
    embedded generators to coordinate rows once, asks the tensor package
    for a basis adapted to the chain and for the block ``GL(n_i, R)``
    generators, and raises the results: the automorphism ``P`` of ``M``
    with ``P(e_j) = b_j``, the block sizes, and the block generators as
    elements of ``GL(M)`` in the coordinates of ``e``.  It asserts that
    every step of the flag is saturated in the next.
    """
    from sage_extensions.tensors.tensor import (
        _engine_block_general_linear_row_actions,
        _engine_flag_adapted_rows,
    )

    module = automorphisms.domain()
    ring = module.base_ring()
    engine_ring = _engine_ring(ring)
    labels = module.module_generating_set()

    def row(vector):
        coordinates = vector.to_vector()
        return [_engine_element(ring, coordinates(label)) for label in labels]

    spans = [[row(vector) for vector in term.embedded_module_generators()] for term in terms]
    spans.append([row(module.module_generator(label)) for label in labels])
    rows, sizes, unsaturated = _engine_flag_adapted_rows(spans, engine_ring)
    assert unsaturated is None, (
        f"{terms} is not a flag of saturated submodules of {module}: step {unsaturated} does not contain "
        f"the previous term as a saturated submodule (its quotient has torsion), so no basis of {module} is "
        f"adapted to it"
    )
    generators = tuple(module.module_generators())
    vectors = tuple(
        sum(
            (module.scalar_multiple(_owned_engine_element(ring, coefficient), generator)
             for coefficient, generator in zip(adapted, generators, strict=True) if coefficient),
            module.zero(),
        )
        for adapted in rows
    )
    change = automorphisms(dict(zip(labels, vectors, strict=True)))
    block_generators = tuple(
        automorphisms._from_backend_row_action(action)
        for action in _engine_block_general_linear_row_actions(sizes, engine_ring)
    )
    return change, sizes, block_generators



class _ModuleCore(_CoreCategory):
    r"""The core of ``Modules(R)``: at ``(M, M)`` its Mor is ``Aut_R(M)``, the one module automorphism group."""

    def Mor(self, domain, codomain):
        if domain is codomain:
            return self.base_category().Aut(domain)
        return super().Mor(domain, codomain)


class ModuleAutomorphismGroups(OwnedCategoryOverBaseRing):
    r"""The groups ``Aut_R(M)`` of invertible module endomorphisms."""

    def _repr_object_names(self):
        return f"module automorphism groups over {self.base_ring()}"

    def an_object(self):
        from sage_extensions.categories.modules.pure.modules import Modules

        return Modules(self.base_ring()).an_object().Aut()

    def super_categories(self):
        from sage_extensions.categories.group.groups import OwnedGroups

        return [OwnedGroups()]

    class ParentMethods:
        @cached_method
        def identity(self):
            module = self.domain()
            identity = module.module_category().Mor(module, module).identity()
            return self._from_known_inverse_pair(identity, identity)

        def one(self, *args, **kwargs):
            return self.identity(*args, **kwargs)
        def identity_automorphism(self, *args, **kwargs):
            return self.identity(*args, **kwargs)


class ModuleAutomorphismGroup(CoreMor):
    r"""``Aut_R(M) = Core(Mod_R)(M, M)``: the unit group of ``End_R(M)``, retaining its actual module maps.

    It is the core Mor of ``Modules(R)`` at ``(M, M)`` (``_ModuleCore``), so
    ``Modules(R).Core().Mor(M, M) is Modules(R).Aut(M)``; its group
    placement comes from ``CoreMor._vertex_group_placement``, refined to
    ``ModuleAutomorphismGroups(R)``, and its elements are the module
    automorphisms of ``ModuleAutomorphismMethods``.

    The inherited Mor containment distinguishes group elements from the
    categorical objects constructed on them. Both retain their construction
    placement; an invertible underlying endomorphism still enters the group
    through its constructor rather than becoming a group element by inspection.
    """

    ElementMethods = ModuleAutomorphismMethods

    def __init__(self, mor_family, module) -> None:
        self._base_ring = _owned_ring(module.base_ring())
        CoreMor.__init__(
            self, mor_family, module, module, category=ModuleAutomorphismGroups(self._base_ring)
        )

    @lazy_attribute
    def element_class(self) -> type:
        r"""The module automorphism arrow type generated from ``ModuleAutomorphismMethods``, not ``CoreMor``'s pair."""
        return self._generated_arrow_type()

    @property
    def ElementType(self) -> type:
        return self._generated_arrow_type()

    def core_category(self):
        return self.domain().module_category().Core()

    def base_ring(self):
        return self._base_ring

    def _from_known_inverse_pair(self, forward, inverse):
        return self.element_class(self, forward, lambda: inverse)

    def _from_inverse_computation(self, forward, inverse_computation):
        r"""The automorphism ``forward``, whose inverse ``inverse_computation()`` is asked on first request."""
        return self.element_class(self, forward, inverse_computation)

    def __call__(self, datum, inverse=None):
        r"""Construct an automorphism-group element rather than preserving a bare Iso arrow.

        As the core Mor it also takes the inverse pair ``(forward, inverse)``
        of module endomorphisms, as ``CoreMor`` does.
        """
        if inverse is not None:
            return self._from_known_inverse_pair(datum, inverse)
        return self._element_constructor_(datum)

    def _element_constructor_(self, datum):
        if isinstance(datum, ModuleAutomorphismMethods):
            if datum.parent() is self:
                return datum
        module = self.domain()
        module_endomorphisms = module.module_category().Mor(module, module)
        if (
            isinstance(datum, ModuleMorphismMethods)
            and datum.parent() is module_endomorphisms
        ):
            # The forward module map is the immediate defining component of
            # an automorphism.  It is admitted only from this exact module
            # endomorphism Mor; arbitrary arrows with the same endpoints do
            # not acquire invertibility by crossing the constructor boundary.
            return self._from_inverse_computation(datum, datum.inverse)
        if isinstance(datum, (Morphism, CategoricalArrow)):
            # An endomorphism of End_R(M), or any other arrow, is not an
            # automorphism: almost none is invertible (``CON-17``).
            _refuse_foreign_arrow(
                self, datum, "an automorphism is given by its generator images, or by the pair (forward, inverse)"
            )
        if isinstance(datum, tuple) and len(datum) == 2 and all(isinstance(part, (Morphism, CategoricalArrow)) for part in datum):
            return self._from_known_inverse_pair(*datum)
        forward = module.module_category().Mor(module, module)(datum)
        return self._from_inverse_computation(forward, forward.inverse)

    def module(self):
        return self.domain()

    # Private engine realization (OWN-06, OWN-24): for a module with a finite
    # selected basis, GL(M) = Aut_R(M) is realized by Sage's GL(n, R) through
    # that basis.  The coordinate convention is crossed once, by the tensor
    # package's row-action lowering and raising.  These are the group
    # realization hooks of OwnedGroups; ordinary callers use subgroup,
    # image, cosets and group_generators.

    def _framed_rank(self):
        from sage_extensions.categories.modules.framed.framed_free_modules import FramedFreeModules

        module = self.domain()
        assert (
            module in FramedFreeModules(module.base_ring())
            and module.module_generating_set().cardinality().is_finite()
        ), (
            f"GL({module}) is realized as a matrix group only for a free module with a finite selected "
            f"basis, but {module} is in {module.category()}"
        )
        return int(module.module_generating_set().cardinality())

    @cached_method
    def _engine_group(self):
        r"""Sage's ``GL(n, R)`` on the selected basis of the module."""
        from sage.groups.matrix_gps.linear import GL

        return GL(self._framed_rank(), _engine_ring(self.domain().base_ring()))

    def _row_action_matrix(self, automorphism):
        from sage_extensions.tensors.tensor import _engine_row_action_matrix

        assert element_parent(automorphism) is self, (
            f"{automorphism} has no matrix in {self}: it lies in {element_parent(automorphism)}"
        )
        return _engine_row_action_matrix(automorphism.forward())

    def _from_backend_row_action(self, row_action_matrix):
        r"""Raise a row-action matrix on the selected basis to an automorphism of the module."""
        from sage_extensions.tensors.tensor import _engine_column_matrix_from_row_action

        module = self.domain()
        ring = module.base_ring()
        generators = tuple(module.module_generators())
        images = tuple(
            sum(
                (
                    module.scalar_multiple(_owned_engine_element(ring, coefficient), generator)
                    for coefficient, generator in zip(column, generators, strict=True)
                    if coefficient
                ),
                module.zero(),
            )
            for column in _engine_column_matrix_from_row_action(row_action_matrix).columns()
        )
        return self(images)

    def _to_engine(self, automorphism):
        return self._engine_group()(self._row_action_matrix(automorphism))

    def _from_engine(self, engine_element):
        return self._from_backend_row_action(self._engine_group()(engine_element).matrix())

    def _engine_subgroup_from_generators(self, generators):
        r"""The matrix group generated by the selected automorphisms, without a presentation of GL."""
        from sage.groups.matrix_gps.finitely_generated import MatrixGroup

        matrices = tuple(self._row_action_matrix(generator) for generator in generators)
        if not matrices:
            return self._engine_group().subgroup(())
        return MatrixGroup(matrices)

    def _to_subgroup_engine(self, automorphism, engine_subgroup):
        return engine_subgroup(self._row_action_matrix(automorphism))

    def _engine_subgroup_contains(self, automorphism, engine_subgroup):
        return self._row_action_matrix(automorphism) in engine_subgroup

    def _from_subgroup_engine(self, engine_element):
        return self._from_backend_row_action(engine_element.matrix())

    def natural_module_action_functor(self):
        r"""The action functor ``B GL(M) -> Mod_R`` on ``M`` itself."""
        from sage_extensions.categories.functors.group_actions import GroupActionFunctor

        module = self.domain()
        modules = module.module_category()
        return GroupActionFunctor(
            self, modules, module, lambda automorphism: modules.Mor(module, module)(automorphism.forward())
        )

    def flag_stabilizer(self, flag):
        r"""``B = {g in GL(M) : g(T_i) = T_i for all i}`` for a chain ``T_1 < ... < T_k`` of saturated submodules.

        ``flag`` is the ordered family of subobjects of ``M``.  In a basis of
        ``M`` adapted to the flag (``P: e_j |-> b_j``, retained as
        ``basis_change()``), ``B`` is block upper triangular; it is generated
        by the block ``GL(n_i, R)`` (Sage's generators) and the elementary
        automorphisms ``b_k |-> b_k + b_j`` for ``j`` in an earlier block
        than ``k`` (Levi decomposition ``B = L U``; unverified: no source was
        opened, recorded in research issue #398, *Generators of parabolic subgroups
        of GL(M) over a PID*; untrusted computation).  The result is the
        stabilizer subgroup of the flag under the natural module action,
        with that generating morphism.
        """
        from sage_extensions.categories.group.predicate_subgroups import StabilizerSubgroups
        from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        from sage_extensions.categories.sets.set_categories import Sets

        module = self.domain()
        match flag:
            case _ if flag in Sets():
                terms = flag
            case _:
                terms = finite_ordered_set(tuple(flag))
        assert all(term.inclusion().codomain() is module for term in terms), (
            f"a flag of {module} is a chain of its subobjects, but {terms} are not all subobjects of {module}"
        )
        change, sizes, block_generators = _flag_stabilizer_engine_data(self, terms)
        labels = module.module_generating_set()
        block_of = dict(zip(labels, (index for index, size in enumerate(sizes) for _ in range(size)), strict=True))
        elementary = tuple(
            self({
                label: module.module_generator(label) + (module.module_generator(j_label) if label == k_label else module.zero())
                for label in labels
            })
            for k_label in labels
            for j_label in labels
            if block_of[j_label] < block_of[k_label]
        )
        generators = finite_ordered_set(tuple(change * generator * ~change for generator in (*block_generators, *elementary)))

        def preserves_flag(automorphism):
            inverse = ~automorphism
            return all(
                term.inclusion().is_in_image(automorphism(vector)) and term.inclusion().is_in_image(inverse(vector))
                for term in terms
                for vector in term.embedded_module_generators()
            )

        return StabilizerSubgroups(self)(
            terms,
            self.natural_module_action_functor(),
            preserves_flag,
            description=f"g preserves the flag {terms} of {module}",
            generating_morphism=self.free_cover(generators),
            basis_change=change,
        )

    def finite_index_left_cosets(self, subgroup, index):
        r"""``G/H`` for ``G = GL(M)``, ``M`` free of rank two over ``ZZ``, and ``H`` of finite index ``index``.

        ``H`` is a subgroup of ``G`` with selected generators; that its index
        in ``G`` is the natural number ``index`` is the caller's stated
        hypothesis (``OWN-22``), which coset enumeration needs: Todd--Coxeter
        terminates exactly when the index is finite.  The enumeration is
        asserted to find that many cosets.  The result is the pointed
        transitive ``G``-set of ``LeftCosetGSets(H)`` on the finite ordinal
        ``{0, ..., index - 1}`` (``0`` the coset ``H``), with the left action
        ``g . Hx = H x g^-1`` and its section through the selected free cover
        of ``G``; ``G.select_left_cosets`` makes it ``G.left_cosets(H)``, so
        double cosets ``H \ G / Q`` are its ``Q``-orbits.  For ``B`` the
        stabilizer of a line, ``H \ G / B`` is the set of cusps of ``H``,
        its orbits on ``P^1(QQ) = B \ G`` (Mathlib ``CuspOrbits``,
        ``Mathlib/NumberTheory/ModularForms/Cusps.lean``; TauCeti
        ``doubleCosetEquivOrbitQuotient``,
        ``TauCeti/GroupTheory/DoubleCoset/Orbits.lean``).
        """
        from sage_extensions.categories.group.g_sets import FiniteGSets
        from sage_extensions.categories.group.groups import GeneratedSubgroups
        from sage_extensions.categories.rings.ring_foundation import _owned_integers
        from sage_extensions.categories.sets.set_categories import NN, finite_ordinal_set
        from sage_extensions.tensors.tensor import _engine_permutation_word_action

        module = self.domain()
        assert module.base_ring() == _owned_integers() and self._framed_rank() == 2, (
            f"cosets of a finite-index subgroup of {self} are enumerated through a presentation of "
            f"GL_2(ZZ), but {module} is not a free ZZ-module of rank two"
        )
        assert subgroup in GeneratedSubgroups(self), (
            f"{subgroup} has no selected generators in {self}: coset enumeration writes each selected "
            f"generator as a word in GL_2(ZZ)"
        )
        assert index in NN, f"the index of {subgroup} in {self} is a natural number, not {index!r}"
        permutations = self._finite_index_coset_permutations(subgroup, NN(index))
        points = finite_ordinal_set(int(NN(index)))
        return FiniteGSets(self).pointed_orbit(
            subgroup,
            points(0),
            lambda automorphism, point: points(
                _engine_permutation_word_action(
                    permutations, self._general_linear_two_word(~automorphism), int(point)
                )
            ),
        )

    @cached_method
    def _finite_index_coset_permutations(self, subgroup, index):
        r"""The right action of ``s_2, s_3, e`` on the cosets of ``subgroup``, computed once per subgroup.

        Private realization for ``finite_index_left_cosets``; the engine work
        is ``tensors.tensor._engine_general_linear_two_coset_permutations``.
        """
        from sage_extensions.tensors.tensor import _engine_general_linear_two_coset_permutations

        return _engine_general_linear_two_coset_permutations(
            tuple(self._row_action_matrix(generator) for generator in subgroup.selected_subgroup_generators()),
            int(index),
        )

    @cached_method
    def _general_linear_two_word(self, automorphism):
        r"""The word of ``automorphism`` in ``s_2, s_3, e``, lowered once per element (``tensors.tensor._engine_general_linear_two_word``)."""
        from sage_extensions.tensors.tensor import _engine_general_linear_two_word

        return _engine_general_linear_two_word(self._row_action_matrix(automorphism))

    def _basis_general_linear_generators(self):
        r"""Generators of ``GL(M)``: Sage's generators of ``GL(n, R)``, raised through the basis."""
        from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

        return finite_ordered_set(tuple(self._from_engine(generator) for generator in self._engine_group().gens()))

    def _finiteness_decision(self):
        r"""A finite module has finitely many automorphisms; otherwise answer the proposition ``is_finite``.

        An infinite module can have a finite automorphism group (``Aut_Z(Z)``
        has two elements), so finiteness of the module is sufficient and not
        necessary.
        """
        match self.module().is_finite():
            case True:
                return True
            case _:
                return AtomicProposition("is_finite", self)

    def super_categories(self):
        packet = self.base_category().category_packet()
        module = self.domain()
        supers = [
            packet.Mors().Of(module, module),
            packet.Monos().Of(module, module),
            packet.Epis().Of(module, module),
        ]
        if self.aut_family() is not None:
            supers.append(packet.Ends().Of(module))
        return _distinct_supercategories(supers)

    def _repr_(self):
        return f"Aut_{self.base_category()}({self.module()})"


class TensorProductModuleMor(ModuleMor):
    r"""The ordinary module Mor with tensor-domain bilinear constructor syntax."""

    ElementMethods = TensorProductModuleMorphismMethods

    @staticmethod
    def _is_two_argument_callable(function) -> bool:
        r"""Whether ``function`` is a Python function of exactly two required positional arguments."""
        match function:
            case _ if isfunction(function) or ismethod(function):
                required = tuple(
                    parameter
                    for parameter in signature(function).parameters.values()
                    if parameter.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
                    and parameter.default is Parameter.empty
                )
                return len(required) == 2
            case _:
                return False

    def _element_constructor_(self, images):
        if not self.domain().has_selected_module_resolution():
            if self._is_two_argument_callable(images):
                return self.domain().from_bilinear_map(self.codomain(), images)
            return super()._element_constructor_(images)
        left = self.domain().tensor_factor(0)
        right = self.domain().tensor_factor(1)
        left_labels = left.module_generating_set()
        right_labels = right.module_generating_set()

        from sage_extensions.tensors.tensor import (
            Tensor,
            _covariant_bilinear_coordinate_rows,
            tensor,
        )

        defining_tensor = None
        defining_values = None
        match images:
            case Tensor():
                rows = _covariant_bilinear_coordinate_rows(
                    images,
                    left_labels.cardinality(),
                    right_labels.cardinality(),
                )
                if self.codomain() in OwnedRings():
                    defining_tensor = (
                        images if images.base_ring() is self.codomain()
                        else tensor(
                            self.codomain(), (),
                            (int(left_labels.cardinality()), int(right_labels.cardinality())),
                            rows,
                        )
                    )
                else:
                    from sage_extensions.categories.modules.pure.modules import RestrictedScalarsModules

                    codomain = self.codomain()
                    if (
                        codomain in RestrictedScalarsModules(self.domain().base_ring())
                        and codomain.module_over_extension() is images.base_ring()
                    ):
                        defining_tensor = images
                images = rows
            case _:
                pass
        if isinstance(images, IndexedFamily):
            source_indices = images.index_set()
            raw_family = images
            domain_labels = self.domain().module_generating_set()
            defining_values = indexed_family(
                domain_labels,
                lambda pair: self.codomain()(raw_family[
                    source_indices(lambda index: pair.component(index))
                ]),
                name="Selected bilinear coordinate tensor",
            )

            def generator_image(pair):
                value = defining_values[pair]
                return value if element_parent(value) is self.codomain() else self.codomain()(value)

            images = generator_image
        elif self._is_two_argument_callable(images):
            return self._from_bilinear_evaluation(images)
        elif isinstance(images, (tuple, list)) and all(isinstance(row, (tuple, list)) for row in images):
            left_size = left_labels.cardinality()
            right_size = right_labels.cardinality()
            if not left_size.is_finite() or not right_size.is_finite():
                raise TypeError(f"cannot define a pairing {left} x {right} -> {self.codomain()} by an array of values: both modules must be finitely generated, but they have {left_size} and {right_size} generators")
            if len(images) != int(left_size.finite_value()) or any(len(row) != int(right_size.finite_value()) for row in images):
                raise ValueError(f"cannot define a pairing {left} x {right} -> {self.codomain()} by the array {images}: it must have {left_size} rows of {right_size} entries")
            # Finite pairing coordinates are the defining tensor of the
            # morphism, not a disposable input subsequently reconstructed by
            # evaluating it on the framing.  The linear extension below reads
            # this same tensor (or its W-valued rectangular coordinate family).
            if defining_tensor is None and self.codomain() in OwnedRings():
                defining_tensor = tensor(
                    self.codomain(), (),
                    (int(left_size.finite_value()), int(right_size.finite_value())),
                    images,
                )
            coordinates = defining_tensor if defining_tensor is not None else tuple(
                tuple(self.codomain()(entry) for entry in row) for row in images
            )
            left_ranking = left_labels.ranking_map()
            right_ranking = right_labels.ranking_map()
            if defining_tensor is None:
                labels = self.domain().module_generating_set()
                defining_values = indexed_family(
                    labels,
                    lambda pair: coordinates[
                        int(left_ranking(pair.component(0)))
                    ][int(right_ranking(pair.component(1)))],
                    name="Selected bilinear coordinate tensor",
                )

            def generator_image(pair):
                row = int(left_ranking(pair.component(0)))
                column = int(right_ranking(pair.component(1)))
                value = coordinates[row, column] if defining_tensor is not None else coordinates[row][column]
                return value if element_parent(value) is self.codomain() else self.codomain()(value)

            images = generator_image

        morphism = super()._element_constructor_(images)
        if defining_tensor is not None:
            morphism._defining_pairing_tensor = defining_tensor
        if defining_values is not None:
            morphism._defining_pairing_values = defining_values
        return morphism

    def _from_bilinear_evaluation(self, evaluation, premises=None):
        r"""Classify a stated bilinear evaluation without proving it from a framing sample.

        The values on pairs of factor generators are the images of the
        selected tensor framing.  A construction whose evaluation is bilinear
        by its own data, such as the product of a ring, supplies the empty
        family of premises.
        """
        match callable(evaluation):
            case True:
                pass
            case False:
                raise TypeError(f"cannot define a bilinear map on {self.domain()} from {evaluation!r}: it must be a function of two arguments")
        source = self.domain()
        left = source.tensor_factor(0)
        right = source.tensor_factor(1)
        codomain = self.codomain()

        def generator_image(pair):
            value = evaluation(
                left.module_generator(pair.component(0)),
                right.module_generator(pair.component(1)),
            )
            return value if element_parent(value) is codomain else codomain(value)

        return self.element_class(
            self,
            generator_image,
            linearity_premises=premises,
            bilinear_evaluation=evaluation,
        )
