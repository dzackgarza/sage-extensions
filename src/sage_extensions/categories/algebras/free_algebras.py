"""Free symmetric, tensor, alternating, and divided-power algebra categories."""

from math import prod
from typing import Any, cast

from sage.algebras.free_algebra import FreeAlgebra as _SageFreeAlgebra
from sage.all import (
    LaurentPolynomialRing as _SageLaurentPolynomialRing,
)
from sage.all import (
    PolynomialRing as _SagePolynomialRing,
)
from sage.categories.map import Map
from sage.categories.morphism import SetMorphism
from sage.categories.rings import Rings as SageRings
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.polynomial.multi_polynomial_ring_base import MPolynomialRing_base
from sage.rings.polynomial.polynomial_quotient_ring import PolynomialQuotientRing_generic
from sage.rings.polynomial.polynomial_ring import PolynomialRing_generic
from sage.structure.element import parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _category_mor_parent,
)
from sage_extensions.categories.algebras.algebras import (
    Algebras,
    AlgebrasWithChosenFinitePresentation,
    CommutativeAlgebraCoproducts,
    CommutativeAlgebraPushouts,
    FinitelyPresentedAlgebras,
    MultiplicativeAlgebraMorphism,
    UnitalMultiplicativeAlgebraMor,
    UnitalMultiplicativeAlgebraMorphism,
    _AlgebraMorCommonMethods,
    _OwnedAlgebraParent,
    _algebra_with_structure,
    _fix_selected_algebra_presentation,
)
from sage_extensions.categories.algebras.graded_algebras import GradedAlgebras
from sage_extensions.categories.algebras.power_algebras import _PowerAlgebra, _PowerAlgebraElement
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphismMethods,
)
from sage_extensions.categories.modules.pure.modules import (
    FinitelyGeneratedFreeModules,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    _free_associative_algebra_placements,
    _polynomial_ring_placements,
    LocalizationRings,
    OwnedCategoryOverBaseRing,
    OwnedRings,
    PredicateSubrings,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_ring,
    _set_owned_ring_display,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.finite_families import finite_family
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import FiniteSets, NN, Sets
from sage_extensions.logic import AtomicProposition, conjunction, negation
from sage_extensions.refine import RealizationHook
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


def _polynomial_monomial_exponents(engine, monomial) -> tuple[int, ...]:
    r"""Decode a polynomial monomial key at the private Sage boundary."""
    if isinstance(engine, PolynomialRing_generic):
        return (int(monomial),)
    if isinstance(engine, MPolynomialRing_base):
        return tuple(int(exponent) for exponent in monomial)
    raise TypeError("the selected symmetric-algebra computation uses a polynomial ring")


class _NativeMonomialEvaluation:
    r"""Native word evaluation shared by free algebras and their linear quotients."""

    def _native_word_representative(self, element):
        return self._engine_element(element)

    def _native_word_generator(self, position):
        return self._engine.gen(position)

    def _native_basis_image(self, label):
        r"""Evaluate one canonical graded framing label in the native algebra."""
        inner = label.summand_element()
        labels = self._generating_module.module_generating_set()
        ranking = labels.ranking_map()
        match self._native_free_flavor:
            case "tensor":
                native = prod(
                    (self._native_word_generator(int(ranking(inner.component(position))))
                     for position in inner.parent().index_set()),
                    start=self._engine.one(),
                )
            case "symmetric":
                native = prod(
                    (self._native_word_generator(int(ranking(item))) ** int(inner.multiplicity(item))
                     for item in inner.support()),
                    start=self._engine.one(),
                )
        return self._from_engine_element(native)

    def _native_basis_coefficients(self, element):
        r"""Decode finite native support in the selected word-module frame.

        Univariate polynomial keys are exponents, multivariate keys are
        exponent tuples, and free-algebra keys are free-monoid words.  A
        linear quotient supplies its lift into that native free algebra.
        """
        generating = self._generating_module
        base = generating.base_ring()
        labels = generating.module_generating_set()
        module_labels = self._native_module_basis.source().module_generating_set()
        representative = self._native_word_representative(element)
        engine = representative.parent()
        coefficients = {}
        for monomial, coefficient in representative.monomial_coefficients().items():
            match self._native_free_flavor:
                case "tensor":
                    native_labels = dict(zip(engine.monoid().gens(), labels, strict=True))
                    word = tuple(
                        native_labels[generator]
                        for generator, exponent in monomial
                        for _ in range(int(exponent))
                    )
                    degree = len(word)
                    inner = module_labels.cofactor(NN(degree))(
                        lambda position, word=word: word[int(position)]
                    )
                case "symmetric":
                    exponents = _polynomial_monomial_exponents(engine, monomial)
                    degree = sum(exponents)
                    powers = dict(zip(labels, exponents, strict=True))
                    inner = module_labels.cofactor(NN(degree)).from_multiplicities(powers)
            coefficients[module_labels(NN(degree), inner)] = _owned_engine_element(base,
                _engine_ring(base)(coefficient)
            )
        return coefficients


class _NativeFreeAlgebraParent(_NativeMonomialEvaluation, _OwnedAlgebraParent):
    r"""Native polynomial/word arithmetic on the canonical free module.

    For a free module M, T(M) = direct_sum_d T^d(M) and
    Sym(M) = direct_sum_d Sym^d(M) (Stacks, Tag 00DM).  The module
    construction supplies these exact pieces.  The free module on the
    disjoint union of their word bases supplies their summed framing.
    Its free source is the basis of all words or monomials, not the
    degree-one generating module M.  Native coefficient extraction is the
    inverse of monomial evaluation in that basis.

    This engine adapter supplies that correspondence before the common
    native ring constructor classifies multiplication.  It introduces no
    module arithmetic, framing accessor, or alternative algebra entry.
    """

    def __init__(self, engine, generating_module, flavor, *, categories=(), construction_data=()) -> None:
        from sage_extensions.categories.modules.framed.framed_free_modules import FramedFreeModules
        from sage_extensions.categories.modules.native_modules import _NativeModuleBasis
        from sage_extensions.categories.group.magmas import AdditiveGroups

        base = generating_module.base_ring()
        assert generating_module in FramedFreeModules(base), (
            f"a free algebra is built on a free module, but {generating_module} is not a free module over {base}"
        )
        self._generating_module = generating_module
        self._native_free_flavor = flavor
        labels = generating_module.module_generating_set()
        indeterminates = int(cardinal(labels.cardinality()).finite_value())
        match flavor:
            case "tensor":
                basis = labels.finite_words()
                algebra_category = TensorAlgebras(base)

                def ring_placement():
                    return _free_associative_algebra_placements(base, indeterminates)
            case "symmetric":
                basis = labels.finite_multisets()
                algebra_category = SymmetricAlgebras(base)

                def ring_placement():
                    return _polynomial_ring_placements(base, indeterminates)
            case _:
                raise ValueError(
                    f"a free algebra here is a tensor algebra or a symmetric algebra, but got flavor {flavor!r}"
                )
        module_placement = FramedFreeModules(base)
        match basis.cardinality().is_finite():
            case True:
                module_placement = FinitelyGeneratedFreeModules(base)
            case False:
                pass
        algebra_placements = ()
        match labels.is_finite():
            case True:
                # A finite free tensor algebra has no defining relations;
                # its symmetric quotient has finitely many commutators.
                # This property chooses no presentation data and implies
                # the previous finite algebra generation placement.
                algebra_placements = (
                    (
                        Algebras(base)
                        .Associative()
                        .Unital()
                        .FinitelyPresentedAsAlgebra()
                    ),
                )
            case _:
                pass
        # The selected generating module is free. Its tensor algebra has
        # the associative algebra lifting property. A symmetric realization
        # has that same property when at most one generator is known; no
        # tensor realization or projectivity is inferred for larger or
        # undecided symmetric families.
        if flavor == "tensor" or (
            labels.is_finite() is True
            and (labels.cardinality() <= cardinal(1)) is True
        ):
            algebra_placements += (
                Algebras(base).Associative().Unital().ProjectiveAsAlgebra(),
            )
        self._native_module_basis = _NativeModuleBasis(
            base.free_module(basis),
            self._native_basis_image,
            self._native_basis_coefficients,
        )
        generator_ranking = labels.ranking_map()
        algebra_generators = indexed_family(
            labels,
            lambda label: self._from_engine_element(
                engine.gen(int(generator_ranking(label)))
            ),
            name="Free algebra generators",
        )
        associative_owner = Algebras(base).Associative().Unital()
        framing_owner = (
            associative_owner.Commutative() if flavor == "symmetric" else associative_owner
        )
        super().__init__(
            engine, base, generating_module.module_generating_set(),
            categories=(
                FreeAlgebras(base),
                GradedFreeAlgebras(base),
                AdditiveGroups().AdditiveCommutative(),
                algebra_category,
                module_placement,
                *algebra_placements,
                *categories,
            ),
            construction_data=construction_data,
            law_decisions=(("grading", True),),
            algebra_generating_family=algebra_generators,
            algebra_framing_source=self,
            algebra_framing_owner=framing_owner,
            ring_placement=ring_placement,
        )
        # Algebras.ParentMethods.__init__, entered through the common parent
        # constructor above, installs the selected resolution, native regular
        # module and deferred algebra placement in that order. Reconstructing
        # the module here would attempt to install a second scalar action on
        # the same parent, violating the one-shot Modules owner contract.

    def _specialized_algebra_with_structure(
        self,
        base_ring,
        labels,
        categories,
        construction_data,
    ):
        r"""Preserve this native free-algebra realization under common refinement."""
        if self.base_ring() is not base_ring:
            return None
        selected_labels = (
            self.algebra_generating_set()
            if labels is None
            else finite_ordered_set(labels)
        )
        generating = self.generating_module()
        if selected_labels == self.algebra_generating_set():
            if (
                not construction_data
                and all(self in category for category in categories)
            ):
                return self
        else:
            generating = base_ring.free_module(selected_labels)
        return _native_free_algebra(
            _engine_ring(self),
            generating,
            self._native_free_flavor,
            categories=categories,
            construction_data=construction_data,
        )

@cached_function(key=lambda engine, generating_module, flavor, categories=(), construction_data=(): (
    engine, id(generating_module), flavor, categories, construction_data,
))
def _native_free_algebra(engine, generating_module, flavor, *, categories=(), construction_data=()):
    r"""The native realization of the free functor on this exact module."""
    return _NativeFreeAlgebraParent(
        engine, generating_module, flavor,
        categories=categories, construction_data=construction_data,
    )


def _finite_labels(labels):
    if labels in FiniteOrderedSets():
        return labels
    if isinstance(labels, int):
        return finite_ordered_set(range(labels))
    return finite_ordered_set(labels)


def _variable_names(labels) -> tuple[str, ...]:
    names = []
    used: set[str] = set()
    for index, label in enumerate(labels):
        candidate = str(label)
        if not candidate.isidentifier() or candidate in used:
            candidate = f"x{index}"
        while candidate in used:
            candidate = f"x{index}_{len(used)}"
        names.append(candidate)
        used.add(candidate)
    return tuple(names)


def _polynomial_variables(variables):
    r"""The set of variables a polynomial ring is constructed on.

    A string names its comma-separated variables, ``"x,y"``; a tuple or list
    names its entries in order; an owned set is its own set of variables.
    """
    match variables:
        case str():
            return finite_ordered_set(tuple(name.strip() for name in variables.split(",")))
        case tuple() | list():
            return finite_ordered_set(tuple(variables))
        case _:
            assert variables in Sets(), (
                f"cannot form a polynomial ring in {variables!r}: give the variables as a string, "
                "a tuple of names or a set"
            )
            return variables


def _polynomial_ring(base_ring, variables):
    r"""``R[S] = Sym_R(F_R(S))``, the free commutative ``R``-algebra on the set ``S`` of variables.

    One object for ``(R, S)``: every route (``R.polynomial_ring(S)``,
    ``R[...]``, ``R.free_module(S).symmetric_algebra()``, an engine raised in
    an adapter) reaches :func:`_symmetric_algebra_on` on the same free module
    (``OWN-02``).
    """
    return _symmetric_algebra_on(_owned_ring(base_ring), _polynomial_variables(variables))


def _polynomial_engine(engine_base, names):
    r"""The private Sage realization of a polynomial ring on ``names``, one rule for every route.

    Univariate for one variable, multivariate otherwise; Sage gives a
    multivariate ring in one variable for a one-element tuple of names, so
    the single name is passed alone.  The term order is a computational
    choice and is Sage's default.
    """
    if len(names) == 1:
        return _SagePolynomialRing(engine_base, names[0])
    return _SagePolynomialRing(engine_base, names)


def _laurent_polynomial_ring(base_ring, *args, **kwargs):
    base = _owned_ring(base_ring)
    result = _own_ring(
        _SageLaurentPolynomialRing(_engine_ring(base), *args, **kwargs)
    )
    labels = tuple(_engine_ring(result).variable_names())
    algebra = _algebra_with_structure(result, base, labels)
    _set_owned_ring_display(
        algebra,
        f"{base}[{', '.join(labels)}^±1]",
        kind="laurent_polynomial",
    )

    return algebra


def _symmetric_algebra_on(base_ring, algebra_generating_set, *, source_module=None):
    r"""``Sym_R(F_R(S))`` on the free module ``F_R(S)`` (or the given ``source_module`` on ``S``)."""
    base = _owned_ring(base_ring)
    infinite = algebra_generating_set in Sets() and algebra_generating_set.is_finite() is not True
    labels = algebra_generating_set if infinite else _finite_labels(algebra_generating_set)
    generating = base.free_module(labels) if source_module is None else source_module
    return _symmetric_algebra_of_free_module(generating)


@cached_function
def _symmetric_algebra_of_free_module(generating):
    r"""``Sym_R(F)`` for the free module ``F = F_R(S)``: one object per ``F``, which is the cache key.

    ``F_R(S)`` is one object per ``(R, S)`` (``_owned_free_module_on``), so
    ``R[S]`` is one object per ``(R, S)`` on every route, never keyed on its
    realization.  The realization is selected here, privately: Sage's
    polynomial ring on the names of ``S`` (:func:`_polynomial_engine`), or the
    sparse construction when ``S`` is not finite or ``R`` has no Sage ring
    realization.
    """
    base = generating.base_ring()
    labels = generating.module_generating_set()
    engine_base = _engine_ring(base)
    if labels.is_finite() is not True or engine_base not in SageRings():
        from sage_extensions.categories.algebras.sparse_free_algebras import (
            _sparse_symmetric_algebra_of,
        )

        return _sparse_symmetric_algebra_of(generating)
    names = _variable_names(labels)
    algebra = _native_free_algebra(
        _polynomial_engine(engine_base, names), generating, "symmetric",
    )
    _set_owned_ring_display(algebra, f"{base}[{', '.join(names)}]", kind="polynomial")
    return algebra


def _tensor_algebra_on(base_ring, algebra_generating_set, *, source_module=None):
    base = _owned_ring(base_ring)
    engine_base = _engine_ring(base)
    if (
        algebra_generating_set in Sets()
        and algebra_generating_set.is_finite() is not True
    ) or engine_base not in SageRings():
        from sage_extensions.categories.algebras.sparse_free_algebras import (
            _sparse_tensor_algebra_of,
        )

        return _sparse_tensor_algebra_of(
            base.free_module(algebra_generating_set) if source_module is None else source_module
        )
    labels = _finite_labels(algebra_generating_set)
    names = _variable_names(labels)
    algebra = _SageFreeAlgebra(engine_base, len(labels), names=names)
    generating = base.free_module(labels) if source_module is None else source_module
    return _native_free_algebra(algebra, generating, "tensor")


def _relations_to_ideal(presentation_ring, relations):
    r"""Return the backend ideal and the owned finite relation family.

    A bare iterable supplies an explicitly finite list, normalized by the
    existing positional-family ingress. Owned families and sets must instead
    supply decided finiteness before their values are traversed.
    """
    if not isinstance(relations, (IndexedFamily, tuple, list)) and relations not in Sets():
        relations = tuple(relations)
    engine = _engine_ring(presentation_ring)
    if isinstance(relations, IndexedFamily):
        size = cardinal(relations.cardinality())
        assert size.is_finite() is True, (
            f"the selected finite algebra presentation needs a known finite relation family, "
            f"but the supplied family has cardinality {size}"
        )
        selected_relations = indexed_family(
            relations.index_set(),
            lambda index: presentation_ring(relations.value(index)),
            name="Defining relation family",
        )
    elif isinstance(relations, (tuple, list)):
        by_position = {position: relation for position, relation in enumerate(relations)}
        indices = Sets.Δ[len(by_position) - 1]
        selected_relations = indexed_family(
            indices,
            lambda index: presentation_ring(by_position[int(index)]),
            name="Defining relation family",
        )
    elif relations in Sets():
        assert cardinal(relations.cardinality()).is_finite() is True, (
            f"the selected finite algebra presentation needs a known finite relation set, "
            f"but the supplied set is {relations}"
        )
        selected_relations = indexed_family(
            relations,
            lambda relation: presentation_ring(relation),
            name="Defining relation family",
        )
    else:
        raise TypeError(
            f"the relations of a quotient of {presentation_ring} are given as a finite indexed family, a "
            f"finite set, or a list, but got {relations!r}"
        )

    backend_relations = [
        _engine_element(presentation_ring, selected_relations.value(index))
        for index in selected_relations.index_set()
    ]
    return engine.ideal(backend_relations), selected_relations


def _base_change_commutative_presentation(algebra, ring_map):
    r"""Change coefficients in the selected polynomial relation family."""
    source_base = algebra.base_ring()
    if ring_map.domain() is not source_base:
        raise ValueError(
            f"scalar change of {algebra} along {ring_map} needs a ring map "
            f"starting at its exact coefficient ring {source_base}"
        )
    target_base = _owned_ring(ring_map.codomain())
    ring_map = OwnedRings().Mor(source_base, target_base)(ring_map)
    source_presentation = algebra.presentation_ring()
    assert source_presentation in SymmetricAlgebras(source_base) and isinstance(
        _engine_ring(source_presentation), (PolynomialRing_generic, MPolynomialRing_base)
    ), (
        f"scalar change of {algebra} needs a selected polynomial presentation; "
        f"its retained presentation {source_presentation} needs a different "
        "coefficient-change computation"
    )
    target_presentation_ring = target_base.free_module(algebra.algebra_generating_set()).symmetric_algebra()
    source_engine = _engine_ring(source_base)
    target_base_engine = _engine_ring(target_base)
    target_engine = _engine_ring(target_presentation_ring)

    def map_backend_scalar(scalar):
        owned_scalar = _owned_engine_element(source_base, source_engine(scalar))
        return _engine_element(target_base, ring_map(owned_scalar))

    backend_base_map = SetMorphism(
        source_engine.Hom(target_base_engine),
        map_backend_scalar,
    )
    source_relations = algebra.relations()
    mapped_relations = indexed_family(
        source_relations.index_set(),
        lambda index: _owned_engine_element(target_presentation_ring,
            target_engine(
                _engine_element(source_presentation, source_relations.value(index)).map_coefficients(
                    backend_base_map,
                    new_base_ring=target_base_engine,
                )
            )
        ),
        name=f"Scalar-changed defining relations of {algebra}",
    )
    return target_presentation_ring.quotient_by_relations(mapped_relations)


class _PresentedAlgebraParent(_OwnedAlgebraParent):
    r"""An algebra with one selected finite presentation fixed at construction."""

    def __init__(
        self,
        quotient_engine,
        base,
        labels,
        presentation_ring,
        selected_relations,
        presentation_ideal,
        *,
        extra_categories=(),
        extra_construction_data=None,
        generating_module=None,
        commutative_backend=False,
        finite_free_degree=None,
        presentation_flattening=None,
        generator_values=None,
        presentation_lift=None,
        finite_free_generator=None,
        finite_free_coordinates=None,
        constructing_category=None,
    ) -> None:
        # An auxiliary native polynomial cover retains its actual map from
        # the chosen presentation.  Other realizations have no such cover.
        self._presentation_cover_map = None
        if extra_construction_data is not None:
            for name, value in extra_construction_data:
                setattr(self, name, value)
        if presentation_flattening is not None:
            self._presentation_cover_map = presentation_flattening
        unflatten = (
            None if presentation_flattening is None else presentation_flattening.section()
        )

        def lift_to_presentation(element):
            backend = quotient_engine(self._engine_element(element))
            representative = (
                backend.lift()
                if presentation_lift is None
                else presentation_lift(backend)
            )
            if unflatten is not None:
                representative = unflatten(representative)
            return _owned_engine_element(presentation_ring, representative)

        if generating_module is not None:
            self._generating_module = generating_module

        extra_categories = tuple(extra_categories)
        placement = [
            FinitelyPresentedAlgebras(base),
            AlgebrasWithChosenFinitePresentation(base),
            Algebras(base).Associative().Unital(),
            *extra_categories,
        ]
        match commutative_backend:
            case True:
                placement.append(Algebras(base).Commutative())
        if finite_free_degree is not None:
            from sage_extensions.categories.modules.native_modules import _power_module_basis

            module_primitive = quotient_engine.gen() if finite_free_generator is None else finite_free_generator

            def basis_coordinates(element):
                backend = self._engine_element(self(element))
                return backend if finite_free_coordinates is None else finite_free_coordinates(backend)

            self._native_module_basis = _power_module_basis(
                base,
                finite_free_degree,
                lambda exponent: self._from_engine_element(module_primitive) ** exponent,
                basis_coordinates,
            )
            placement.append(FinitelyGeneratedFreeModules(base))

        selected_generator_values = generator_values
        if presentation_flattening is not None:
            if selected_generator_values is not None:
                raise ValueError(
                    f"the algebra over {base} given by the relations {selected_relations} computes its generator "
                    "values itself, so they cannot also be given"
                )
            presentation_engine = _engine_ring(presentation_ring)
            # The flattened engine lists parameter variables before these
            # outer algebra generators, so positional backend generators no
            # longer represent the selected algebra framing.
            selected_generator_values = tuple(
                quotient_engine(presentation_flattening(presentation_engine.gen(position)))
                for position in range(presentation_engine.ngens())
            )

        law_decisions = ()
        match any(
            category.is_subcategory(GradedAlgebras(base))
            for category in extra_categories
        ):
            case True:
                law_decisions = (("grading", True),)
            case False:
                pass
        _OwnedAlgebraParent.__init__(
            self,
            quotient_engine,
            base,
            labels,
            generator_values=selected_generator_values,
            categories=tuple(placement),
            law_decisions=law_decisions,
            algebra_framing_source=presentation_ring,
            constructing_category=constructing_category,
        )
        _fix_selected_algebra_presentation(
            self,
            presentation_ring,
            selected_relations,
            presentation_ideal,
            lift_to_presentation,
            presentation_cover_map=self._presentation_cover_map,
        )
        self._preamble_commutative_algebra_coproduct_backend = (
            (lambda left, right: _commutative_algebra_coproduct_backend(left, right))
            if commutative_backend
            else None
        )
        self._preamble_commutative_algebra_pushout_backend = (
            (lambda left_map, right_map: _commutative_algebra_pushout_backend(left_map, right_map))
            if commutative_backend
            else None
        )

    def _repr_(self):
        r"""``P/(r_1, ..., r_k)``: the quotient named by its chosen presentation."""
        display = self._preamble_ring_display
        if display is not None:
            return display
        relations = ", ".join(repr(relation) for relation in self.relations())
        return f"{self.presentation_ring()}/({relations})"




class _WordFramedPresentedAlgebra(_NativeMonomialEvaluation, _PresentedAlgebraParent):
    r"""A presented algebra framed as a module by its words.

    The forgetful functor U: Alg_R -> Mod_R carries the algebra framing
    Free_Alg(S) -> A to the module framing Free_Mod(Mon(S)) -> U(A): the
    words in the chosen generators span A.  For relations linear in
    M = F/N, maps from T(F)/(N) to any associative algebra are exactly
    linear maps from F that vanish on N, so the degree-d module is
    M tensor ... tensor M, and Sym^d(M) for commutative targets; the word
    module is then U(A) itself.  For other relations it is the word module
    of the free algebra, and the framing is a surjection, not a basis.
    """

    def __init__(self, engine, base, labels, presentation_ring, relations,
                 presentation_ideal, *, generating_module, relations_are_linear=True, **options):
        from sage_extensions.categories.modules.native_modules import _NativeModuleFrame
        from sage_extensions.categories.modules.word_modules import _module_on_word_quotient

        self._generating_module = generating_module
        match presentation_ring:
            case _ if presentation_ring in TensorAlgebras(base):
                self._native_free_flavor = "tensor"
            case _:
                assert presentation_ring in SymmetricAlgebras(base), (
                    f"a free algebra with linear relations is a quotient of a tensor algebra or a symmetric algebra, "
                    f"but {presentation_ring} is neither"
                )
                self._native_free_flavor = "symmetric"
        # Fix the native images before any lower constructor can evaluate a
        # word. Flattened coefficient variables are not algebra generators.
        match options.get("generator_values"), options.get("presentation_flattening"):
            case (None, None):
                self._native_word_generators = tuple(engine.gen(i) for i in range(int(labels.cardinality())))
            case (None, flattening):
                free_engine = _engine_ring(presentation_ring)
                self._native_word_generators = tuple(
                    engine(flattening(free_engine.gen(i))) for i in range(int(labels.cardinality()))
                )
            case (values, _):
                self._native_word_generators = tuple(values)
        word_module = _module_on_word_quotient(generating_module, self._native_free_flavor)
        self._native_module_basis = _NativeModuleFrame(
            word_module, self._native_basis_image, self._native_basis_coefficients,
            injective=relations_are_linear,
        )
        super().__init__(
            engine, base, labels, presentation_ring, relations, presentation_ideal,
            generating_module=generating_module, **options,
        )

    def _native_word_generator(self, position):
        return self._native_word_generators[position]

    def _native_word_representative(self, element):
        presentation = self.presentation_ring()
        return _engine_element(presentation, self.lift_to_presentation(self(element)))


def _presented_algebra_on_engine(
    engine,
    presentation_ring,
    relations,
    *,
    generator_values=None,
    finite_free_degree=None,
    finite_free_generator=None,
    finite_free_coordinates=None,
    presentation_lift=None,
):
    r"""Represent a chosen polynomial presentation on an authoritative engine.

    This is the crossing for an algebra whose computation parent already exists
    independently of the polynomial presentation (a number field is the first
    consumer).  The returned object keeps ``engine`` as its ring realization;
    ``presentation_ring`` and ``relations`` supply the algebra framing, quotient
    map, scalar-change data, and finite-presentation module structure.
    """
    base = presentation_ring.base_ring()
    if presentation_ring not in SymmetricAlgebras(base):
        raise TypeError(
            f"this algebra must be a quotient of a commutative polynomial ring, but {presentation_ring} is "
            "not a symmetric algebra"
        )
    presentation_ideal, selected_relations = _relations_to_ideal(
        presentation_ring, relations
    )
    return _PresentedAlgebraParent(
        engine,
        base,
        presentation_ring.algebra_generating_set(),
        presentation_ring,
        selected_relations,
        presentation_ideal,
        commutative_backend=True,
        finite_free_degree=finite_free_degree,
        generator_values=generator_values,
        presentation_lift=presentation_lift,
        finite_free_generator=finite_free_generator,
        finite_free_coordinates=finite_free_coordinates,
    )


def _localized_coefficient_presentation_backend(
    presentation_ring,
    selected_relations,
):
    r"""Realize a finite presentation over a finitely generated localization.

    For ``S^{-1}A[x_1,...,x_n]/I`` with a chosen finite generating family for
    ``S``, compute in the standard polynomial presentation

    ``A[x_1,...,x_n,t_1,...,t_r]/(t_i s_i - 1, I~)``.

    The public algebra keeps its selected presentation over ``S^{-1}A``.  This
    helper supplies only the private Sage quotient, the images of the selected
    algebra generators in that quotient, and the exact lift back to the
    selected presentation.  The construction therefore changes no public
    scalar ring or presentation data.
    """

    base = presentation_ring.base_ring()
    if base not in LocalizationRings():
        return None
    if base.localization_submonoid()._structure_data().get("kind") != "finitely_generated":
        return None
    inverted = tuple(base.inverted_elements())
    if not inverted:
        return None

    coefficient_source = base.localization_source()
    presentation_engine = _engine_ring(presentation_ring)
    coefficient_source_engine = _engine_ring(coefficient_source)
    base_engine = _engine_ring(base)
    variable_names = tuple(presentation_engine.variable_names())
    polynomial_bottom = _SagePolynomialRing(
        coefficient_source_engine,
        names=variable_names,
    )
    flattening = polynomial_bottom.flattening_morphism()
    flattened = flattening.codomain()
    unflatten = flattening.section()

    flat_names = tuple(flattened.variable_names())
    occupied = set(flat_names)
    inverse_names = []
    for position in range(len(inverted)):
        candidate = f"localization_inverse_{position}"
        while candidate in occupied:
            candidate = "localization_" + candidate
        occupied.add(candidate)
        inverse_names.append(candidate)
    engine_presentation = _SagePolynomialRing(
        flattened.base_ring(),
        names=(*flat_names, *inverse_names),
    )
    engine_generators = tuple(engine_presentation.gens())
    flattened_generators = engine_generators[: flattened.ngens()]
    inverse_generators = engine_generators[flattened.ngens() :]
    flattened_to_engine = flattened.hom(
        flattened_generators,
        engine_presentation,
    )

    def bottom_polynomial(element):
        represented = presentation_engine(
            _engine_element(presentation_ring, element)
        )
        coefficients = represented.dict()
        common_denominator = coefficient_source_engine.one()
        represented_coefficients = {}
        for exponent, coefficient in coefficients.items():
            represented_coefficient = base_engine(coefficient)
            represented_coefficients[exponent] = represented_coefficient
            common_denominator *= coefficient_source_engine(
                represented_coefficient.denominator()
            )

        cleared = {}
        for exponent, represented_coefficient in represented_coefficients.items():
            denominator = coefficient_source_engine(
                represented_coefficient.denominator()
            )
            multiplier, remainder = common_denominator.quo_rem(denominator)
            if remainder != coefficient_source_engine.zero():
                raise ArithmeticError(
                    f"cannot clear denominators of {element}: the common denominator {common_denominator} is not "
                    f"divisible by {denominator}"
                )
            cleared[exponent] = (
                coefficient_source_engine(represented_coefficient.numerator())
                * multiplier
            )
        return polynomial_bottom(cleared)

    engine_relations = []
    for inverse, inverted_element in zip(
        inverse_generators,
        inverted,
        strict=True,
    ):
        bottom_element = coefficient_source_engine(
            _engine_element(coefficient_source, inverted_element)
        )
        represented = flattened_to_engine(
            flattening(polynomial_bottom(bottom_element))
        )
        engine_relations.append(
            inverse * represented - engine_presentation.one()
        )
    engine_relations.extend(
        flattened_to_engine(flattening(bottom_polynomial(relation)))
        for relation in selected_relations
    )

    quotient_engine = engine_presentation.quotient(
        engine_presentation.ideal(tuple(engine_relations))
    )

    coefficient_generators = tuple(coefficient_source_engine.gens())
    base_generators = tuple(base_engine.gens())
    if len(coefficient_generators) == len(base_generators):
        scalar_images = [
            quotient_engine(
                flattened_to_engine(
                    flattening(polynomial_bottom(generator))
                )
            )
            for generator in coefficient_generators
        ]
        engine_scalar_map = base_engine.hom(
            scalar_images,
            quotient_engine,
        )
        if not quotient_engine.has_coerce_map_from(base_engine):
            # This quotient engine is a private realization of an algebra over
            # ``base``.  Register exactly that represented scalar embedding so
            # Sage's affine-scheme engine sees the same map; no public owned
            # coercion is introduced.
            quotient_engine.register_coercion(engine_scalar_map)

    generator_values = tuple(
        quotient_engine(
            flattened_to_engine(flattening(polynomial_bottom.gen(position)))
        )
        for position in range(polynomial_bottom.ngens())
    )

    reverse_images = [
        presentation_engine(unflatten(generator))
        for generator in flattened.gens()
    ]
    reverse_images.extend(
        presentation_engine(
            base_engine(
                _engine_element(coefficient_source, inverted_element)
            )
            ** -1
        )
        for inverted_element in inverted
    )
    engine_to_presentation = engine_presentation.hom(
        reverse_images,
        presentation_engine,
    )

    def presentation_lift(element):
        return engine_to_presentation(quotient_engine(element).lift())

    return quotient_engine, generator_values, presentation_lift


def _finitely_presented_algebra_from_data(
    presentation_ring,
    relations,
    *,
    _extra_categories=(),
    _extra_construction_data=None,
    _generating_module=None,
    _constructing_category=None,
):
    r"""Return the selected polynomial or associative quotient by relations.

    The literal free presentation and relation indices are retained.  Tensor
    presentations use the selected two-sided normal-form supplier; polynomial
    presentations keep their existing polynomial computations.  A private
    auxiliary polynomial cover, when needed, carries its exact presentation
    map and inverse lift instead of replacing the owned presentation.
    """
    base = presentation_ring.base_ring()
    assert (
        presentation_ring in AlgebrasWithChosenFinitePresentation(base)
        or presentation_ring in SymmetricAlgebras(base)
        or presentation_ring in TensorAlgebras(base)
    ), (
        f"a selected finite algebra presentation needs a tensor or polynomial "
        f"presentation, or a quotient of one, but {presentation_ring} has none selected"
    )
    assert presentation_ring.is_framed_algebra(), (
        f"a finite presentation of {presentation_ring} needs chosen algebra generators"
    )
    labels = presentation_ring.algebra_generating_set()
    assert labels.cardinality().is_finite() is True, (
        f"a finite presentation of {presentation_ring} needs a known finite chosen "
        "algebra-generator family before the presentation computation"
    )
    match relations:
        case IndexedFamily():
            assert relations.cardinality().is_finite() is True, (
                f"a finite presentation of {presentation_ring} needs a known finite "
                "relation family before any traversal"
            )
        case tuple() | list():
            pass
        case _ if relations in Sets():
            assert cardinal(relations.cardinality()).is_finite() is True, (
                f"a finite presentation of {presentation_ring} needs a known finite "
                "owned relation set before any traversal"
            )
        case _:
            # Retain the existing bare finite-iterable ingress also for
            # quotients of quotients, before their relations are lifted.
            relations = tuple(relations)
    presentation_ideal, selected_relations = _relations_to_ideal(
        presentation_ring, relations
    )
    if presentation_ring in AlgebrasWithChosenFinitePresentation(base):
        # A quotient of a quotient is one quotient of the same free
        # presentation: for A = P/I, the algebra A/(J) is P/(I + J~) where J~
        # lifts the new relations to P.  Consolidating here keeps one chosen
        # presentation and one scalar ring, so a second closed embedding into
        # an already presented algebra reaches the same construction as the
        # first rather than needing a tower of quotient objects.
        source = presentation_ring.presentation_ring()
        existing = presentation_ring.relations()
        lifted_relations = selected_relations.map(
            lambda relation: presentation_ring.lift_to_presentation(relation),
            name="Lifted additional algebra relations",
        )
        relation_families = indexed_family(
            Sets.Δ[1],
            lambda index: existing if int(index) == 0 else lifted_relations,
            name="Original and additional relation families",
        )
        relation_indices = Sets().coproduct(
            relation_families.map(lambda family: family.index_set())
        )
        combined_relations = indexed_family(
            relation_indices,
            lambda index: relation_families.value(index.summand_index()).value(
                index.summand_element()
            ),
            name="Original and lifted additional algebra relations",
        )
        return _finitely_presented_algebra_from_data(
            source,
            combined_relations,
            _extra_categories=_extra_categories,
            _extra_construction_data=_extra_construction_data,
            _generating_module=_generating_module,
            _constructing_category=_constructing_category,
        )
    presentation_engine = _engine_ring(presentation_ring)
    commutative_backend = presentation_ring in SymmetricAlgebras(base)
    if presentation_ring in TensorAlgebras(base):
        from sage_extensions.categories.algebras.finitely_presented_algebras import (
            _HomogeneousPresentationTensorIdeal,
        )

        presentation_ideal = _HomogeneousPresentationTensorIdeal(
            presentation_ring, selected_relations
        )
    presentation_flattening = None
    quotient_presentation_engine = presentation_engine
    quotient_ideal = presentation_ideal
    quotient_engine = None
    generator_values = None
    presentation_lift = None
    extra_construction_data = (
        () if _extra_construction_data is None else tuple(_extra_construction_data)
    )
    if isinstance(presentation_engine, PolynomialRing_generic) and (
        len(presentation_ideal.gens()) > 1
        or any(
            relation and relation.leading_coefficient().is_unit() is not True
            for relation in presentation_ideal.gens()
        )
    ):
        # Reuse the one-variable multivariate polynomial computation already
        # selected for Sym_R(M) with a relation such as 2*x over ZZ.  A
        # nonmonic relation need not define a finite free coefficient module.
        auxiliary = _SagePolynomialRing(
            presentation_engine.base_ring(), 1,
            names=presentation_engine.variable_names(),
        )
        to_auxiliary = presentation_engine.hom(auxiliary.gens(), auxiliary)
        from_auxiliary = auxiliary.hom(
            presentation_engine.gens(), presentation_engine
        )
        cover_map = to_auxiliary
        cover_lift = from_auxiliary
        quotient_presentation_engine = auxiliary
        if isinstance(auxiliary.base_ring(), (PolynomialRing_generic, MPolynomialRing_base)):
            # The same canonical flattening as the multivariate branch below
            # also handles, for example, R=QQ[s] and the relation s*t+1.
            flattening = auxiliary.flattening_morphism()
            quotient_presentation_engine = flattening.codomain()
            cover_map = flattening * to_auxiliary
            cover_lift = from_auxiliary * flattening.section()
        quotient_ideal = quotient_presentation_engine.ideal(
            tuple(cover_map(relation) for relation in presentation_ideal.gens())
        )
        quotient_engine = quotient_presentation_engine.quotient(quotient_ideal)
        generator_values = tuple(
            quotient_engine(cover_map(generator))
            for generator in presentation_engine.gens()
        )

        def presentation_lift(element):
            return cover_lift(quotient_engine(element).lift())

        extra_construction_data += (("_presentation_cover_map", cover_map),)
    elif isinstance(presentation_engine, MPolynomialRing_base) and isinstance(
        presentation_engine.base_ring(),
        (PolynomialRing_generic, MPolynomialRing_base),
    ):
        # Sage's multivariate quotient reduction over a polynomial
        # coefficient ring need not have a Gröbner backend.  Keep the owned
        # relative presentation nested, but compute in the canonically
        # flattened polynomial ring where the coefficient variables become
        # ordinary variables over the ultimate coefficient ring.
        presentation_flattening = presentation_engine.flattening_morphism()
        quotient_presentation_engine = presentation_flattening.codomain()
        quotient_ideal = quotient_presentation_engine.ideal(
            [
                presentation_flattening(
                    _engine_element(
                        presentation_ring,
                        selected_relations.value(index)
                    )
                )
                for index in selected_relations.index_set()
            ]
        )
    elif (
        isinstance(presentation_engine, MPolynomialRing_base)
        and base in LocalizationRings()
    ):
        localized_backend = _localized_coefficient_presentation_backend(
            presentation_ring,
            selected_relations,
        )
        if localized_backend is not None:
            quotient_engine, generator_values, presentation_lift = localized_backend

    if quotient_engine is None:
        quotient_engine = quotient_presentation_engine.quotient(quotient_ideal)
        if quotient_engine is quotient_presentation_engine:

            def presentation_lift(element):
                return element

    finite_free_degree = None
    label_size = labels.cardinality()
    if (
        label_size.is_finite() is True
        and int(label_size.finite_value()) == 1
        and isinstance(quotient_engine, PolynomialQuotientRing_generic)
    ):
        modulus = quotient_engine.modulus()
        degree = int(modulus.degree())
        if degree > 0:
            finite_free_degree = degree

    word_frame = {}
    match finite_free_degree:
        case int():
            constructor = _PresentedAlgebraParent
        case None:
            constructor = _WordFramedPresentedAlgebra
            # A caller supplies M = F/N exactly when the relations are linear
            # in the generators; otherwise the words of the free algebra span.
            word_frame["relations_are_linear"] = _generating_module is not None
            if _generating_module is None:
                _generating_module = presentation_ring.generating_module()
    return constructor(
        quotient_engine,
        base,
        labels,
        presentation_ring,
        selected_relations,
        presentation_ideal,
        extra_categories=tuple(_extra_categories),
        extra_construction_data=extra_construction_data,
        generating_module=_generating_module,
        commutative_backend=commutative_backend,
        finite_free_degree=finite_free_degree,
        presentation_flattening=presentation_flattening,
        generator_values=generator_values,
        presentation_lift=presentation_lift,
        constructing_category=_constructing_category,
        **word_frame,
    )


class FreeAlgebras(OwnedCategoryOverBaseRing):
    def an_object(self):
        r"""The free algebra on one generator."""
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(self.base_ring())
        return modules.tensor_algebra()(modules.an_object())

    def _repr_object_names(self):
        return f"free algebras over {self.base_ring()}"

    def super_categories(self):
        return [Algebras(self.base_ring()).Associative().Unital()]

    class ParentMethods:
        def _cardinality_decision(self):
            r"""Return the cardinality of the free algebra from its word basis."""
            from sage_extensions.categories.sets.cardinals import (
                Cardinalities,
                aleph0,
                cardinal,
            )

            scalars = self.base_ring()._cardinality_decision()
            generators = self.algebra_generating_set()._cardinality_decision()
            if scalars is not None and (cardinal(scalars) == Cardinalities().one()) is True:
                return Cardinalities().one()
            if scalars is None or generators is None:
                return None
            scalars = cardinal(scalars)
            generators = cardinal(generators)
            if (generators == Cardinalities().zero()) is True:
                return scalars
            if not scalars.expression().is_normal_form() or not generators.expression().is_normal_form():
                return None
            match generators == Cardinalities().zero(), scalars == Cardinalities().one():
                case True, _:
                    return scalars
                case False, True:
                    return Cardinalities().one()
                case False, False:
                    return Cardinalities().supremum(scalars, generators, aleph0)

        def is_free(self) -> bool:
            return True

        def _algebra_mor_class(self):
            return FramedFreeAlgebraMor



class GradedFreeAlgebras(OwnedCategoryOverBaseRing):
    def an_object(self):
        r"""The polynomial algebra on one generator, graded by degree."""
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(self.base_ring())
        return modules.symmetric_algebra()(modules.an_object())

    def _repr_object_names(self):
        return f"graded free algebras over {self.base_ring()}"

    def super_categories(self):

        return [FreeAlgebras(self.base_ring()), GradedAlgebras(self.base_ring())]

    class ParentMethods:
        def _realize_graded_piece_basis_label(self, degree, label):
            r"""Return the algebra monomial represented by one basis label of ``A_degree``.

            The authoritative basis is the basis of :meth:`graded_piece`; this
            method only realizes that basis element back in the algebra.  It
            does not construct a second monomial system.
            """
            degree = int(degree)
            if degree < 0:
                raise ValueError(f"graded pieces of {self} are in degrees n >= 0, but n = {degree}")
            if degree == 0:
                return self.one()
            if degree == 1:
                return self.algebra_generator(label)

            piece = self.graded_piece(degree)

            if self in AlternatingAlgebras(self.base_ring()) or self in DividedPowerAlgebras(self.base_ring()):
                return self.from_component(degree, piece.module_generator(label))

            ring = self.algebra_base_ring()
            result = self.one()
            if self in TensorAlgebras(ring):
                from sage_extensions.categories.modules.tensor_products import (
                    _flatten_tensor_label,
                )

                for source_label in _flatten_tensor_label(label, degree):
                    result *= self.algebra_generator(source_label)
                return result

            if self in SymmetricAlgebras(ring):
                for source_label in label.support():
                    for _ in range(int(label.multiplicity(source_label))):
                        result *= self.algebra_generator(source_label)
                return result

            raise TypeError(
                f"{self} is neither a tensor algebra nor a symmetric algebra, so the basis element {label} of "
                f"its degree-{degree} piece cannot be computed"
            )

        def from_graded_piece(self, degree, element):
            r"""Include an element of the canonical degree piece into this algebra."""
            degree = int(degree)
            piece = self.graded_piece(degree)
            coordinates = piece.framing_morphism().lift(element)
            return sum(
                (
                    coordinates(label)
                    * self._realize_graded_piece_basis_label(degree, label)
                    for label in coordinates.support().domain()
                ),
                self.zero(),
            )

        def degree_on_module_generator(self, module_generator):
            r"""Return the degree of one represented homogeneous algebra basis element."""
            return self.homogeneous_degree(module_generator)

        def graded_piece_monomials(self, degree):
            r"""Return the selected algebra basis of the canonical degree piece.

            The index set is literally the framing of :meth:`graded_piece`;
            values are those basis generators realized in this algebra.
            """
            degree = int(degree)
            if degree < 0:
                raise ValueError(f"graded pieces of {self} are in degrees n >= 0, but n = {degree}")
            if degree == 0:
                labels = finite_ordered_set((0,))
            else:
                labels = self.graded_piece(degree).module_generating_set()
            return indexed_family(
                labels,
                lambda label: self._realize_graded_piece_basis_label(degree, label),
                name=f"Degree-{degree} algebra monomial basis of {self}",
            )

        def ideal_generators_in_degree(self, relations, degree):
            r"""Return generators of the degree-``degree`` ideal generated in degree one.

            For tensor/symmetric/exterior algebras this is
            ``sum_{i+j=d-1} A_i K A_j``.  For divided powers the divided
            powers of the selected degree-one relations are included as well,
            which is the divided-power ideal rather than an ordinary
            polynomial ideal.
            """
            degree = int(degree)
            if degree < 0:
                raise ValueError(f"graded pieces of {self} are in degrees n >= 0, but n = {degree}")
            selected = tuple(self(relation) for relation in relations)
            if any(self.homogeneous_degree(relation) != 1 for relation in selected):
                raise ValueError(
                    f"the generators of this graded ideal of {self} must lie in degree 1, but {selected} do not all"
                )
            if degree == 0:
                return finite_family((), name=f"Degree-{degree} ideal generators")

            generators = []
            for relation in selected:
                for left_degree in range(degree):
                    right_degree = degree - 1 - left_degree
                    left_basis = self.graded_piece_monomials(left_degree)
                    right_basis = self.graded_piece_monomials(right_degree)
                    for left_label in left_basis.index_set():
                        for right_label in right_basis.index_set():
                            generators.append(
                                left_basis[left_label] * relation * right_basis[right_label]
                            )

            ring = self.algebra_base_ring()
            if self in DividedPowerAlgebras(ring):
                for relation in selected:
                    for divided_degree in range(2, degree + 1):
                        divided = self.divided_power(relation, divided_degree)
                        complementary = self.graded_piece_monomials(
                            degree - divided_degree
                        )
                        for label in complementary.index_set():
                            generators.append(divided * complementary[label])
            return finite_family(
                generators,
                name=f"Degree-{degree} ideal generators",
            )

        def graded_piece(self, degree):
            r"""Return the canonical degree piece of this free construction.

            The flavor, not this common superclass, determines the degree
            piece: ``T^n(M)``, ``Sym^n(M)``, ``Lambda^n(M)``, or
            ``Gamma^n(M)``.  This is one construction path -- the algebra does
            not build a second model of those modules.
            """
            degree = int(degree)
            assert degree >= 0, f"graded pieces of {self} are in degrees n >= 0, but n = {degree}"

            ring = self.algebra_base_ring()
            match self:
                # The represented exterior/divided-power algebras are assembled
                # from their authoritative module-power pieces, in every degree
                # including zero; do not let this generic free-algebra method
                # replace their degree-zero power module with the scalar ring.
                case _ if self in AlternatingAlgebras(ring):
                    return self.generating_module().exterior_power(degree)
                case _ if self in DividedPowerAlgebras(ring):
                    return self.generating_module().divided_power_module(degree)
                # Every flavor uses its authoritative module-power owner in
                # every degree.  In degree zero this is the rank-one scalar
                # module, not the ring parent viewed through an unrelated API.
                case _ if self in TensorAlgebras(ring):
                    return self.generating_module().tensor_power(degree)
                case _ if self in SymmetricAlgebras(ring):
                    return self.generating_module().symmetric_power(degree)
            raise TypeError(
                f"{self} is neither a tensor algebra nor a symmetric algebra, so its degree-{degree} piece "
                "cannot be computed"
            )


class PowerAlgebraMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class_for(self, domain, codomain):
        _ = codomain
        return domain._power_algebra_mor_class()


class TensorAlgebras(OwnedCategoryOverBaseRing):
    r"""Tensor algebras of represented modules."""

    def an_object(self):
        r"""The tensor algebra on the free module of rank one."""
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(self.base_ring())
        return modules.tensor_algebra()(modules.an_object())

    def _repr_object_names(self):
        return f"tensor algebras over {self.base_ring()}"

    def super_categories(self):

        return [GradedAlgebras(self.base_ring())]

    class ParentMethods:
        def homogeneous_degree(self, element):
            r"""Return the degree of a homogeneous tensor-algebra element.

            Sage's free associative algebra stores monomials on free-monoid
            words.  Word length is the tensor grading, and the coefficient
            dictionary is the maintained exact representation of a finite
            algebra element.
            """
            element = self(element)
            if element == self.zero():
                raise ValueError(f"the zero element of {self} has no degree")
            backend = _engine_element(self, element)
            degrees = {
                len(word)
                for word, coefficient in backend.monomial_coefficients().items()
                if coefficient
            }
            if len(degrees) != 1:
                raise ValueError(
                    f"{element} is not homogeneous in {self}: it has components in degrees {sorted(degrees)}"
                )
            return self.grading_monoid()(degrees.pop())

        def from_component(self, degree, component):
            r"""Embed ``T^degree(M)`` through the shared graded-piece inclusion."""
            return self.from_graded_piece(degree, component)

        def homogeneous_component(self, element, degree):
            r"""Project an element onto the authoritative tensor-power piece."""
            degree = int(degree)
            element = self(element)
            piece = self.graded_piece(degree)
            backend = _engine_element(self, element)
            coefficients = backend.monomial_coefficients()
            word_to_label = {}
            for label in piece.module_generating_set():
                monomial = _engine_element(
                    self,
                    self._realize_graded_piece_basis_label(degree, label),
                )
                entries = tuple(monomial.monomial_coefficients().items())
                if len(entries) != 1 or entries[0][1] != 1:
                    raise ArithmeticError(
                        f"the basis element {label} of the degree-{degree} piece of {self} did not compute as one "
                        "monomial"
                    )
                word_to_label[entries[0][0]] = label
            ring = self.algebra_base_ring()
            engine_ring = _engine_ring(ring)
            return piece.linear_combination(
                {
                    word_to_label[word]: _owned_engine_element(ring, engine_ring(coefficient))
                    for word, coefficient in coefficients.items()
                    if coefficient and len(word) == degree
                }
            )

        def homogeneous_components(self, element):
            r"""Return all nonzero tensor-degree components as tensor-power elements."""
            backend = _engine_element(self, self(element))
            degrees = sorted(
                {
                    len(word)
                    for word, coefficient in backend.monomial_coefficients().items()
                    if coefficient
                }
            )
            return {
                degree: self.homogeneous_component(element, degree)
                for degree in degrees
            }

        def generating_module(self):
            r"""The exact input M of this chosen tensor-algebra construction.

            This is the degree-one module, not U(T(M)), the direct sum of
            all tensor powers.  The native and relationful entries supply M
            before constructing the algebra; this accessor never reconstructs
            it from generator labels.
            """
            return self._generating_module

        @cached_method
        def ring_center(self):
            r"""Return the exact center of the represented free tensor algebra.

            On zero or one generator the tensor algebra is commutative.  On at
            least two free module generators, comparison of coefficients in
            the word basis shows that an element commuting with two distinct
            generators has no nonconstant word, so the center is exactly the
            scalar ring. A relationful generating module needs a computation
            using its tensor relations; its generator count alone does not
            establish this word-basis theorem.
            """
            from sage_extensions.categories.modules.framed.framed_free_modules import (
                FramedFreeModules,
            )

            size = self.algebra_generating_set().cardinality()
            if size.is_finite() and int(size.finite_value()) <= 1:
                return self
            assert self.generating_module() in FramedFreeModules(self.algebra_base_ring()), (
                f"the centre of {self} needs a computation with its tensor relations; "
                "the available scalar-centre theorem needs a chosen free module basis"
            )
            return self.algebra_base_ring()

        @RealizationHook
        @cached_method
        def _center_construction(self):
            r"""Supply the inherited magma centre from the tensor word-basis theorem.

            The retained centre and inclusion satisfy Magmas'
            ``_center_construction`` contract. A scalar centre uses the exact
            coefficient ring as endpoint, regardless of any other algebra
            structures that ring itself carries.
            """
            center = self.ring_center()
            if center is self:
                return center, self.Mor(self).identity()
            if center in PredicateSubrings():
                return center, center.inclusion()
            return center, OwnedRings().Mor(center, self)(lambda scalar: self(scalar))


    class ElementMethods:
        def homogeneous_components(self):
            return self.parent().homogeneous_components(self)

        def homogeneous_component(self, degree):
            return self.parent().homogeneous_component(self, degree)


class SymmetricAlgebras(OwnedCategoryOverBaseRing):
    r"""Symmetric algebras of represented modules."""

    def an_object(self):
        r"""The symmetric algebra on the free module of rank one."""
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(self.base_ring())
        return modules.symmetric_algebra()(modules.an_object())

    def _repr_object_names(self):
        return f"symmetric algebras over {self.base_ring()}"

    def super_categories(self):
        return [GradedAlgebras(self.base_ring()).Commutative()]

    class ParentMethods:
        def _normality_decision(self):
            r"""A finite symmetric algebra over a field is a normal domain.

            Its generating module is a vector space, so choosing a basis
            identifies its symmetric algebra with a polynomial algebra.
            The assertion uses the actual coefficient field; it makes no
            normality claim for Sym_R(M) over an arbitrary ring.
            """
            from sage_extensions.categories.rings.ring_foundation import OwnedFields

            if (
                self.algebra_base_ring() in OwnedFields()
                and self.algebra_generating_set() in FiniteSets()
            ):
                return True
            return super()._normality_decision()

        @cached_method
        def _normalization_data(self):
            r"""Supply identity normalization with the actual affine coefficient map."""
            from sage_extensions.categories.rings.ring_foundation import (
                OwnedFields,
                OwnedRings,
            )
            from sage_extensions.categories.rings.commutative_algebra import (
                _identity_affine_normalization_data,
            )
            from sage_extensions.categories.sets.indexed_families import (
                finite_indexed_family,
            )

            if (
                self.algebra_base_ring() not in OwnedFields()
                or self.algebra_generating_set() not in FiniteSets()
            ):
                return None
            identity = OwnedRings().Mor(self, self).identity()
            components = finite_indexed_family(
                finite_ordered_set((0,)),
                lambda index: (self.ideal(self.zero()), self, identity),
            )
            coefficient_map = self.algebra_structure_morphism()
            if coefficient_map.codomain() is not self:
                coefficient_map = coefficient_map.codomain().inclusion() * coefficient_map
            return _identity_affine_normalization_data(self, coefficient_map, components)

        def generating_module(self):
            r"""The exact input M of this chosen symmetric-algebra construction.

            For polynomial syntax the constructor supplies F_R(S) on its
            variables.  For Sym_R(M) it supplies M itself, including its
            relations.  Neither is the full underlying module U(Sym_R(M)).
            """
            return self._generating_module

        def from_component(self, degree, component):
            r"""Embed ``Sym^degree(M)`` through the shared graded-piece inclusion."""
            return self.from_graded_piece(degree, component)

        def homogeneous_component(self, element, degree):
            r"""Project onto the canonical symmetric-power degree piece."""
            degree = int(degree)
            element = self(element)
            piece = self.graded_piece(degree)
            backend = _engine_element(self, element)
            engine = backend.parent()
            coefficients = backend.monomial_coefficients()
            exponent_to_label = {}
            for label in piece.module_generating_set():
                monomial = _engine_element(
                    self,
                    self._realize_graded_piece_basis_label(degree, label),
                )
                entries = tuple(monomial.monomial_coefficients().items())
                if len(entries) != 1 or entries[0][1] != 1:
                    raise ArithmeticError(
                        f"the basis element {label} of the degree-{degree} piece of {self} did not compute as one "
                        "monomial"
                    )
                exponent_to_label[entries[0][0]] = label
            ring = self.algebra_base_ring()
            engine_ring = _engine_ring(ring)
            return piece.linear_combination(
                {
                    exponent_to_label[exponent]: _owned_engine_element(ring,
                        engine_ring(coefficient)
                    )
                    for exponent, coefficient in coefficients.items()
                    if coefficient
                    and sum(_polynomial_monomial_exponents(engine, exponent)) == degree
                }
            )

        def homogeneous_components(self, element):
            r"""Return all nonzero polynomial-degree components."""
            backend = _engine_element(self, self(element))
            engine = backend.parent()
            degrees = sorted(
                {
                    sum(_polynomial_monomial_exponents(engine, exponent))
                    for exponent, coefficient in backend.monomial_coefficients().items()
                    if coefficient
                }
            )
            return {
                degree: self.homogeneous_component(element, degree)
                for degree in degrees
            }

        def _commutative_algebra_coproduct(self, left, right):
            r"""Supply the symmetric-algebra coproduct to the generic algebra owner.

            Protected construction contract: the sole external caller role is
            ``Algebras._categorical_coproduct``. The backend implementation is
            selected here by the symmetric-algebra owner and returns only the
            owned coproduct object and owned maps.
            """
            return _commutative_algebra_coproduct_backend(left, right)

        def _commutative_algebra_pushout(self, left_map, right_map):
            r"""Supply the symmetric-algebra pushout to the generic algebra owner.

            Protected construction contract: the sole external caller role is
            ``Algebras._categorical_pushout``. The specialized computation
            remains in this owner and returns an owned pushout.
            """
            return _commutative_algebra_pushout_backend(left_map, right_map)

    class ElementMethods:
        def homogeneous_components(self):
            return self.parent().homogeneous_components(self)

        def homogeneous_component(self, degree):
            return self.parent().homogeneous_component(self, degree)

        def number_field(self, name):
            r"""The number field ``K[name]/(f)`` of this irreducible polynomial ``f`` over ``QQ`` or a number field ``K``."""
            from sage_extensions.categories.rings.number_fields import (
                _number_field,
            )

            return _number_field(self, name)


class AlternatingAlgebras(OwnedCategoryOverBaseRing):
    r"""Exterior algebras ``Lambda_R(M)`` of modules over a commutative ring.

    The actual module ``M`` is retained, and its image is the degree-one
    summand. The exterior algebra is the quotient of ``T_R(M)`` by all
    ``m tensor m``; hence every odd homogeneous element squares to zero,
    including over rings with 2-torsion. Sign-supercommutativity alone does
    not impose that equation in characteristic two.

    Its construction morphisms are the graded unital algebra maps induced
    by actual linear maps of the retained modules. They act in degree
    ``n`` by ``Lambda^n`` and in degree zero by the identity of ``R``.
    An ordinary, possibly non-graded algebra map is requested in the
    associative-unital algebra category. The construction also supplies
    the canonical augmentation through ``AugmentedAlgebras``.

    See Mathlib ``LinearAlgebra/ExteriorAlgebra/Basic``: the quotient,
    ``ι_sq_zero``, ``lift``, ``map`` and ``algebraMapInv``.
    """

    def parameter_category(self):
        r"""The coefficient datum is a commutative unital ring."""
        return OwnedRings().Commutative()

    def an_object(self):
        r"""The exterior algebra on the free module of rank one."""
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(self.base_ring())
        return modules.exterior_algebra()(modules.an_object())

    def _repr_object_names(self):
        return f"alternating algebras over {self.base_ring()}"

    def super_categories(self):
        return [GradedAlgebras(self.base_ring()).Supercommutative().Alternating()]

    _MorCategory = PowerAlgebraMorCategoryConstruction

    def _call_(self, module):
        from sage_extensions.categories.algebras.power_algebras import _power_algebra_of
        from sage_extensions.categories.modules.pure.modules import Modules

        assert module in Modules(self.base_ring()), (
            f"the exterior algebra over {self.base_ring()} needs an actual "
            f"module over that ring, but received {module}"
        )
        assert module.base_ring() is self.base_ring(), (
            f"the power algebra over {self.base_ring()} needs a module over {self.base_ring()}, but "
            f"{module} is over {module.base_ring()}"
        )
        return _power_algebra_of(module, "alternating")

    class ParentMethods(_PowerAlgebra):
        r"""The exterior power realization of the alternating algebra on ``M``."""

    class ElementMethods(_PowerAlgebraElement):
        pass


def _presentation_data(algebra):
    from sage_extensions.categories.rings.commutative_algebra import QuotientRings

    base = algebra.base_ring()
    match algebra:
        case _ if algebra in AlgebrasWithChosenFinitePresentation(base):
            presentation = algebra.presentation_ring()
            assert presentation in SymmetricAlgebras(base), (
                f"the selected commutative coproduct of {algebra} needs a "
                "polynomial presentation computation for its actual chosen source"
            )
            return presentation, tuple(algebra.relations())
        case _ if algebra in SymmetricAlgebras(base) and algebra.is_framed_algebra():
            return algebra, ()
        case _ if algebra in QuotientRings():
            quotient_source = algebra.quotient_source()
            if quotient_source in SymmetricAlgebras(base):
                return quotient_source, tuple(algebra.defining_ideal().ideal_generators())
    raise TypeError(
        f"{algebra} must be a polynomial algebra or a quotient of one given by finitely many relations"
    )


def _transport_relations(presentation_ring, relations, target, tag):
    if not relations:
        return ()
    transport = presentation_ring.Mor(target)(
        {
            label: target.algebra_generator((tag, label))
            for label in presentation_ring.algebra_generating_set()
        }
    )
    return tuple(transport(relation) for relation in relations)


@cached_function
def _commutative_algebra_coproduct_backend(left, right):
    base = left.base_ring()
    if right.base_ring() is not base:
        raise ValueError(
            f"the coproduct {left} (x) {right} of commutative algebras needs one base ring, but they are "
            f"over {base} and {right.base_ring()}"
        )
    category = Algebras(base).Associative().Unital().Commutative()
    if left not in category or right not in category:
        raise TypeError(
            f"the coproduct {left} (x) {right} needs both factors to be commutative algebras over {base}"
        )
    assert left.is_framed_algebra() and right.is_framed_algebra(), (
        f"the coproduct {left} (x) {right} is computed only when both factors have finitely many "
        "chosen algebra generators"
    )
    left_labels = left.algebra_generating_set()
    right_labels = right.algebra_generating_set()
    assert (
        left_labels.cardinality().is_finite() is True
        and right_labels.cardinality().is_finite() is True
    ), (
        f"the coproduct {left} (x) {right} needs a selected finite-presentation computation; "
        "finiteness of both chosen algebra-generator families must be decided before enumeration"
    )

    left_presentation, left_relations = _presentation_data(left)
    right_presentation, right_relations = _presentation_data(right)
    combined_labels = tuple(
        ("left", label) for label in left_labels
    ) + tuple(("right", label) for label in right_labels)
    presentation = base.free_module(combined_labels).symmetric_algebra()
    relations = _transport_relations(
        left_presentation, left_relations, presentation, "left"
    ) + _transport_relations(
        right_presentation, right_relations, presentation, "right"
    )
    construction_data = (("_preamble_coproduct_factors", (left, right)),)
    if relations:
        return (presentation).quotient_by_relations(relations,
            _extra_categories=(CommutativeAlgebraCoproducts(base),),
            _extra_construction_data=construction_data,
        )
    return _algebra_with_structure(
        presentation,
        base,
        combined_labels,
        FreeAlgebras(base),
        GradedFreeAlgebras(base),
        SymmetricAlgebras(base),
        CommutativeAlgebraCoproducts(base),
        construction_data=construction_data,
    )


def _quotient_by_algebra_elements_backend(
    algebra,
    elements,
    *,
    extra_categories=(),
    extra_construction_data=None,
):
    base = algebra.base_ring()
    match elements:
        case IndexedFamily():
            assert elements.cardinality().is_finite() is True, (
                f"the selected quotient of {algebra} needs a known finite family of algebra elements"
            )
            empty = elements.cardinality() == cardinal(0)
        case tuple() | list():
            empty = not elements
        case _ if elements in Sets():
            assert cardinal(elements.cardinality()).is_finite() is True, (
                f"the selected quotient of {algebra} needs a known finite owned relation set "
                "before traversal"
            )
            empty = cardinal(elements.cardinality()) == cardinal(0)
        case _:
            # This is the established ingress for a supplied finite iterable,
            # not a finiteness test on an owned mathematical set or family.
            elements = tuple(elements)
            empty = not elements
    if empty is True and not extra_categories and not extra_construction_data:
        identity = Algebras(base).Associative().Unital().Mor(algebra, algebra).identity()
        return algebra, identity
    match algebra:
        case _ if (
            algebra in AlgebrasWithChosenFinitePresentation(base)
            or algebra in SymmetricAlgebras(base)
            or algebra in TensorAlgebras(base)
        ):
            pass
        case _:
            assert False, (
                f"the quotient of {algebra} by {elements} needs a selected tensor "
                "or polynomial presentation computation"
            )
    quotient = _finitely_presented_algebra_from_data(algebra, elements,
        _extra_categories=tuple(extra_categories),
        _extra_construction_data=extra_construction_data,
    )
    quotient_map = Algebras(algebra.base_ring()).Associative().Unital().Mor(algebra, quotient)(
        {
            label: quotient.algebra_generator(label)
            for label in algebra.algebra_generating_set()
        }
    )
    return quotient, quotient_map


@cached_function
def _commutative_algebra_pushout_backend(left_map, right_map):
    common = left_map.domain()
    left = left_map.codomain()
    right_common = right_map.domain()
    right = right_map.codomain()
    if common is not right_common:
        raise ValueError(
            f"a pushout needs a span B <- A -> C, but the maps start at {common} and {right_common}"
        )
    base = common.base_ring()
    if left.base_ring() is not base or right.base_ring() is not base:
        raise ValueError(
            f"the pushout of {left} <- {common} -> {right} needs all three over one base ring {base}"
        )
    category = Algebras(base).Associative().Unital().Commutative()
    if common not in category or left not in category or right not in category:
        raise TypeError(
            f"the pushout of {left} <- {common} -> {right} requires commutative "
            f"associative unital algebras over the retained base {base}"
        )
    if (
        left_map not in category.Mor(common, left)
        or right_map not in category.Mor(common, right)
    ):
        raise TypeError(
            f"the pushout maps {left_map} and {right_map} must be algebra morphisms {common} -> {left} and "
            f"{common} -> {right}"
        )
    assert common.is_framed_algebra(), (
        f"the pushout of {left} <- {common} -> {right} is computed only when {common} has finitely many "
        "chosen algebra generators"
    )
    common_labels = common.algebra_generating_set()
    assert common_labels.cardinality().is_finite() is True, (
        f"the pushout of {left} <- {common} -> {right} needs a finite chosen algebra-generator "
        "family for its common source before forming the compatibility relations"
    )

    tensor = _commutative_algebra_coproduct_backend(left, right)
    left_injection, right_injection = tensor.coproduct_injections()
    equalities = tuple(
        left_injection(left_map(common.algebra_generator(label)))
        - right_injection(right_map(common.algebra_generator(label)))
        for label in common_labels
    )
    pushout, _quotient_map = _quotient_by_algebra_elements_backend(
        tensor,
        equalities,
        extra_categories=(CommutativeAlgebraPushouts(base),),
        extra_construction_data=(
            ("_preamble_pushout_span", (left_map, right_map)),
            ("_preamble_pushout_coproduct", tensor),
        ),
    )
    return pushout

class DividedPowerAlgebras(OwnedCategoryOverBaseRing):
    r"""Divided-power algebras ``Gamma(M)`` with their canonical grading."""

    def parameter_category(self):
        r"""The coefficient datum is a commutative unital ring."""
        return OwnedRings().Commutative()

    def an_object(self):
        r"""The divided-power algebra on the standard module witness."""
        from sage_extensions.categories.modules.pure.modules import Modules

        return Modules(self.base_ring()).an_object().divided_power_algebra()

    def _repr_object_names(self):
        return f"divided power algebras over {self.base_ring()}"

    def super_categories(self):
        return [GradedAlgebras(self.base_ring()).Commutative()]

    _MorCategory = PowerAlgebraMorCategoryConstruction

    def _call_(self, module):
        from sage_extensions.categories.algebras.power_algebras import _power_algebra_of

        assert module.base_ring() is self.base_ring(), (
            f"the power algebra over {self.base_ring()} needs a module over {self.base_ring()}, but "
            f"{module} is over {module.base_ring()}"
        )
        return _power_algebra_of(module, "divided")

    class ElementMethods(_PowerAlgebraElement):
        pass

    class ParentMethods(_PowerAlgebra):
        def divided_power(self, value, exponent):
            r"""Return the canonical divided power of a degree-one element.

            For the retained module ``M``, this computes
            ``gamma_n(iota(m))`` in ``Gamma^n(M)``. The equations
            ``gamma_0(x) = 1`` and ``gamma_n(0) = 0`` for positive ``n``
            hold independently of a chosen homogeneous degree for zero.
            A divided power on another element of the augmentation ideal
            needs a further computation; this degree-one supplier does not
            assert that such a divided power is undefined.
            """
            from sage.rings.integer_ring import ZZ as SageZZ

            from sage_extensions.categories.rings.ring_foundation import _engine_numeral

            # This existing numeral boundary admits exact integral input;
            # Python int alone would truncate, for example, 3/2 to 1.
            exponent = int(_engine_numeral(SageZZ, exponent))
            if exponent < 0:
                raise ValueError(f"the divided power x^[n] needs n >= 0, but n = {exponent}")
            value = self(value)
            if exponent == 0:
                return self.one()
            if (value == self.zero()) is True:
                return value
            assert value.is_homogeneous() is True and (value.degree() == 1) is True, (
                f"cannot compute gamma_{exponent}({value}) in {self}: the selected "
                "divided-power computation needs a represented degree-one element "
                "or proved zero; no computation on a general augmentation-ideal "
                "element is selected"
            )
            return self.from_component(
                exponent,
                self.generating_module().divided_power_element(
                    exponent,
                    value.homogeneous_component(1),
                ),
            )

        gamma = divided_power




def _symmetric_generator_images_commute(codomain, images):
    r"""Decide the commuting-image condition for a symmetric extension.

    In an associative target, the tensor lift descends through the
    symmetric relations exactly when the generator images commute. Actual
    commutative placement proves this without inspecting any labels. A
    known finite label family supplies the conjunction of its exact
    commutator equations; otherwise ``None`` leaves the existing algebra
    diagnostic in charge. Finiteness availability does not request an exact
    cardinal, and an undecided coefficient equality remains a proposition.
    """
    if codomain in Algebras(codomain.algebra_base_ring()).Commutative():
        return True
    labels = images.index_set()
    if labels.is_finite() is not True:
        return None
    values = tuple(images[label] for label in labels)
    return conjunction(
        left * right == right * left
        for position, left in enumerate(values)
        for right in values[position + 1:]
    )


class FramedFreeAlgebraMorphism:
    r"""An exact map or a word extension from a framed free algebra.

    An untagged function gives generator images. A map with the literal
    algebra endpoints instead retains its whole elementwise function, with
    its product and unit equations left to the ordinary diagnostics. For
    generator data the free word basis gives a linear extension; tensor
    multiplicativity uses the retained generating-module map, while a
    symmetric source also requires pairwise commuting images.
    """

    # The common composition retains the whole underlying linear map. A
    # generator-only reconstruction would change a supplied nonunital map.
    __mul__ = MultiplicativeAlgebraMorphism.__mul__

    def _multiplicativity_derivation(self):
        derived = super()._multiplicativity_derivation()
        if derived is not None:
            return derived
        if self._source_element_map is not None:
            return None
        linearity = self._generating_module_morphism.linearity_decision()
        if self.domain() in TensorAlgebras(self.domain().algebra_base_ring()):
            return linearity
        commuting = _symmetric_generator_images_commute(self.codomain(), self._images)
        return None if commuting is None else conjunction((linearity, commuting))

    def _unit_preservation_derivation(self):
        derived = super()._unit_preservation_derivation()
        if derived is not None:
            return derived
        return None if self._source_element_map is not None else True

    def __init__(
        self, parent, images, *, _construction_premises=None,
        _transported_morphism=None,
    ) -> None:
        if (
            _transported_morphism is None
            and isinstance(images, UnitalMultiplicativeAlgebraMorphism)
            and images.domain() is parent.domain()
            and images.codomain() is parent.codomain()
        ):
            _transported_morphism = images
        domain = cast(Any, parent.domain())
        codomain = parent.codomain()
        generating = domain.generating_module()
        labels = domain.algebra_generating_set()
        generator_mor = generating.module_category().Mor(generating, codomain)
        self._source_element_map = None
        self._generating_module_morphism = None
        if isinstance(images, Map):
            if images.codomain() is not codomain:
                raise ValueError(
                    f"a map into {codomain} must retain that exact codomain, but {images} "
                    f"ends at {images.codomain()}"
                )
            if images.domain() is domain:
                self._source_element_map = images
                images = indexed_family(
                    labels,
                    lambda label: codomain(self._source_element_map(domain.algebra_generator(label))),
                    name="Generator images",
                )
            elif images.domain() is generating:
                self._generating_module_morphism = (
                    images if images in generator_mor else generator_mor.elementwise(images)
                )
                images = indexed_family(
                    labels,
                    lambda label: self._generating_module_morphism(generating.module_generator(label)),
                    name="Generator images",
                )
            elif images.domain() is not labels:
                raise ValueError(
                    f"a map out of {domain} must be stated on that algebra, its generating "
                    f"module {generating}, or its generator labels {labels}, not on {images.domain()}"
                )
        if isinstance(images, IndexedFamily):
            source_indices = images.index_set()
            self._images = indexed_family(
                labels,
                lambda label: codomain(images[source_indices(label)]),
                name="Generator images",
            )
        elif isinstance(images, dict):
            if not labels.cardinality().is_finite():
                raise TypeError(
                    f"a dictionary of generator images needs finitely many algebra generators of {domain}, but it "
                    f"has {labels.cardinality()}; give a function or an indexed family"
                )
            missing = [label for label in labels if label not in images]
            if missing:
                raise ValueError(
                    f"the images of the algebra generators of {domain} must be given for every generator, but "
                    f"{missing} are missing"
                )
            self._images = indexed_family(
                labels,
                lambda label: codomain(images[label]),
                name="Generator images",
            )
        elif isinstance(images, (tuple, list)):
            size = labels.cardinality()
            if not size.is_finite():
                raise TypeError(
                    f"a list of generator images needs finitely many algebra generators of {domain}, but it has "
                    f"{size}; give a function or an indexed family"
                )
            values = tuple(images)
            if len(values) != int(size.finite_value()):
                raise ValueError(
                    f"{domain} has {size} algebra generators, but {len(values)} images were given"
                )
            self._images = indexed_family(
                labels,
                lambda label: codomain(values[int(labels.ranking_map()(label))]),
                name="Generator images",
            )
        elif callable(images):
            self._images = indexed_family(
                labels,
                lambda label: codomain(images(label)),
                name="Generator images",
            )
        else:
            raise TypeError(
                f"a morphism out of {domain} is given by the images of its algebra generators, but got {images!r}"
            )
        self._engine_morphism = None
        self._preamble_is_identity = False
        linear_mor = domain.module_category().Mor(domain, codomain)
        if self._source_element_map is not None:
            linear = linear_mor.elementwise(self._source_element_map)
        else:
            if self._generating_module_morphism is None:
                self._generating_module_morphism = generator_mor(self._images.value)
            # Ordered words give an R-linear map on this free module basis
            # even when the generator images do not commute. Retain the
            # actual generating-map premise independently of multiplicativity.
            linear = linear_mor._from_constructed_element_map(
                lambda element: self._call_(element),
                premises=(self._generating_module_morphism,),
            )
        super().__init__(
            parent, linear, _construction_premises=_construction_premises,
            _transported_morphism=_transported_morphism,
        )

    def algebra_generator_images(self):
        return self._images

    def algebra_generator_morphism(self):
        return SetMorphism(
            Sets().Mor(self.domain().algebra_generating_set(), self.codomain()),
            self._images.value,
        )

    def _tensor_terms(self, element):
        domain = self.domain()
        if domain in AlgebrasWithChosenFinitePresentation(domain.base_ring()):
            presentation_ring = domain.presentation_ring()
            presented = _engine_element(
                presentation_ring,
                domain.lift_to_presentation(element),
            )
        else:
            presented = _engine_element(domain, element)
        engine = presented.parent()
        labels = self._finite_engine_generator_labels()
        generator_labels = dict(zip(engine.monoid().gens(), labels, strict=True))
        for monomial, coefficient in presented.monomial_coefficients().items():
            word = tuple(
                generator_labels[generator]
                for generator, exponent in monomial
                for _ in range(int(exponent))
            )
            base = domain.base_ring()
            yield word, _owned_engine_element(base, _engine_ring(base)(coefficient))

    def _symmetric_terms(self, element):
        domain = self.domain()
        if domain in AlgebrasWithChosenFinitePresentation(domain.base_ring()):
            presentation_ring = domain.presentation_ring()
            presented = _engine_element(
                presentation_ring,
                domain.lift_to_presentation(element),
            )
        else:
            presented = _engine_element(domain, element)
        engine = presented.parent()
        labels = self._finite_engine_generator_labels()
        for monomial, coefficient in presented.monomial_coefficients().items():
            exponents = _polynomial_monomial_exponents(engine, monomial)
            factors = tuple(
                label
                for label, exponent in zip(labels, exponents, strict=True)
                for _ in range(int(exponent))
            )
            base = domain.base_ring()
            yield factors, _owned_engine_element(base, _engine_ring(base)(coefficient))

    def _finite_engine_generator_labels(self):
        labels = self.domain().algebra_generating_set()
        assert labels.cardinality().is_finite(), (
            f"cannot compute with {self}: its domain {self.domain()} needs finitely many algebra generators, "
            f"but it has {labels.cardinality()}"
        )
        return tuple(labels)

    def _call_(self, element):
        domain = self.domain()
        element = domain(element)
        if self._source_element_map is not None:
            return self.codomain()(self._source_element_map(element))
        terms = (
            self._tensor_terms(element)
            if domain in TensorAlgebras(domain.base_ring())
            else self._symmetric_terms(element)
        )
        # An R-algebra morphism sends a coefficient c of R to its image under
        # the codomain's structure map R -> B.
        codomain = self.codomain()
        return sum(
            (
                codomain(coefficient)
                * prod(
                    (self._images[label] for label in factors),
                    start=self.codomain().one(),
                )
                for factors, coefficient in terms
            ),
            self.codomain().zero(),
        )

    def __call__(self, element):
        return self._call_(element)

    def is_identity(self) -> bool:
        return self._preamble_is_identity

    def _richcmp_(self, other, op):
        r"""Compare selected word extensions on their defining generator images.

        Two such extensions have the same values on every word precisely
        when their generator images agree. An arbitrary retained whole map
        has no such construction theorem: use the existing module comparison,
        which may retain an undecided equality on an infinite word module.
        """
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if other not in self.parent():
            return op == op_NE
        if self is other:
            return op == op_EQ
        if (
            not isinstance(other, FramedFreeAlgebraMorphism)
            or self._source_element_map is not None
            or other._source_element_map is not None
        ):
            # Admission may preserve a stronger arrow's original parent.
            # The faithful forgetful functor retains both functions and
            # their linearity premises in the same actual module Mor.
            forget = Algebras(self.domain().algebra_base_ring()).underlying_module()
            return ModuleMorphismMethods._richcmp_(forget(self), forget(other), op)
        labels = self.domain().algebra_generating_set()
        if labels.is_finite() is not True:
            equal = AtomicProposition("equal", self, other)
        else:
            equal = conjunction(
                self.algebra_generator_images()[label] == other.algebra_generator_images()[label]
                for label in labels
            )
        return equal if op == op_EQ else negation(equal)


class FramedFreeAlgebraMor(_AlgebraMorCommonMethods, UnitalMultiplicativeAlgebraMor):
    ElementMethods = FramedFreeAlgebraMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        CategoricalMor.__init__(
            self,
            mor_family,
            domain,
            codomain,
        )

    def _element_constructor_(self, datum):
        r"""Extend defining generator data through the free-algebra universal property."""
        if isinstance(datum, Map):
            if self._already_parented_arrow(datum):
                return datum
            source = self.domain()
            generating = source.generating_module()
            labels = source.algebra_generating_set()
            generator_mor = generating.module_category().Mor(generating, self.codomain())
            label_mor = Sets().Mor(labels, self.codomain())
            if not (generator_mor.accepts(datum) or label_mor.accepts(datum)):
                raise TypeError(f"{datum} is a whole arrow of another Mor; give the free-generator map")
        return self.element_class(self, datum)

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(A, A), but this is Mor({self.domain()}, {self.codomain()})"
            )
        identity = self(lambda label: self.domain().algebra_generator(label))
        identity._preamble_is_identity = True
        return identity
