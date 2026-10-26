r"""Modules given as an abelian group together with a ring morphism into its endomorphisms.

An ``R``-module is an abelian group ``A`` and a ring morphism
``rho : R -> End(A)``.  This module states that definition directly: the
underlying set, its addition, zero and negation are the abelian group, and
``rho`` is the scalar action.  Nothing here is a second kind of module.  The
object is built through the owned module chain like every other module, so
every operation the module graph owns -- Mor objects, scalar change,
localization, the annihilator as the kernel of ``rho`` -- answers on it
without being restated at this level.
"""

import logging
import operator

from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import ModuleElement, parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedRings,
    _owned_ring,
    _enumerated_ring_elements,
)
from sage_extensions.categories.sets.set_categories import (
    EnumeratedSets,
    FiniteSets,
    Set,
)
from sage_extensions.logic import AtomicProposition
from sage_extensions.owned_category import _object_of
from sage_extensions.validation import validator

_LOGGER = logging.getLogger(__name__)


def _module_element_scalar_action(element, actor, self_on_left):
    """Dispatch the scalar-ring action of an owned module element."""
    _ = self_on_left
    parent = element.parent()
    match actor:
        case _ if actor in parent.base_ring():
            return parent.scalar_multiple(actor, element)
        case _:
            return None


class GeneralModules(OwnedCategoryOverBaseRing):
    r"""Modules presented by an abelian group and a ring morphism ``rho : R -> End(A)``."""

    class ElementMethods(ModuleElement):
        r"""One element of the module, which is one element of the underlying set."""

        def __init__(self, parent, value) -> None:
            ModuleElement.__init__(self, parent)
            self._value = value

        def underlying_element(self):
            r"""Return this element read in the underlying set."""
            return self._value

        value = underlying_element

        def _add_(self, other):
            return self.parent()._add_elements(self, other)

        def _sub_(self, other):
            return self.parent()._add_elements(self, -other)

        def _neg_(self):
            return self.parent()._negate_element(self)

        def _lmul_(self, scalar):
            return self.parent().scalar_multiple(scalar, self)

        def _rmul_(self, scalar):
            return self.parent().scalar_multiple(scalar, self)

        def __rmul__(self, scalar):
            return self.parent().scalar_multiple(scalar, self)

        def _acted_upon_(self, actor, self_on_left):
            return _module_element_scalar_action(self, actor, self_on_left)

        def _richcmp_(self, other, op):
            if other.parent() is not self.parent():
                return NotImplemented
            if op == op_EQ:
                return self.underlying_element() == other.underlying_element()
            if op == op_NE:
                return self.underlying_element() != other.underlying_element()
            return NotImplemented

        def _repr_(self):
            return repr(self.underlying_element())

    def _repr_object_names(self):
        return f"general modules over {self.base_ring()}"

    def an_object(self):
        r"""The zero module, the one-point set with its only additive structure."""
        return self.from_operations(
            Set([0]),
            addition=lambda left, right: 0,
            zero=0,
            negation=lambda value: 0,
            scalar_action=lambda scalar, value: 0,
        )

    def from_operations(
        self,
        underlying_set,
        *,
        addition,
        zero,
        negation,
        scalar_action,
    ):
        r"""Return the module on ``underlying_set`` with the stated operations."""
        return _object_of(
            self,
            base_ring=self.base_ring(),
            underlying_set=underlying_set,
            addition=addition,
            zero=zero,
            negation=negation,
            scalar_action=scalar_action,
        )

    def super_categories(self):
        return [Modules(self.base_ring())]

    class ParentMethods:
        def __init__(
            self,
            base_ring,
            rho=None,
            *,
            underlying_set=None,
            addition=None,
            zero=None,
            negation=None,
            scalar_action=None,
            **rest,
        ) -> None:
            ring = _owned_ring(base_ring)
            if rho is not None:
                assert all(datum is None for datum in (underlying_set, addition, zero, negation, scalar_action)), (
                    f"cannot construct an {ring}-module from {rho}: a ring morphism rho: {ring} -> End(A) "
                    "already determines the additive group A, so no set, addition, zero, negation or "
                    "scalar multiplication may be given alongside it"
                )
                assert rho.parent().mor_category().is_subcategory(OwnedRings()) and rho.domain() is ring, (
                    f"cannot construct an {ring}-module from {rho}: the scalar action must be a ring "
                    f"morphism out of {ring}, but {rho} lies in {rho.parent()}"
                )
                underlying_set = rho.codomain().domain()
                assert rho.codomain().codomain() is underlying_set, (
                    f"cannot construct an {ring}-module from {rho}: the scalar action must take values in "
                    f"the endomorphism ring End(A) of an abelian group A, but its codomain is {rho.codomain()}"
                )
                addition = operator.add
                zero = underlying_set.zero()
                negation = operator.neg
            else:
                assert callable(scalar_action), (
                    f"cannot construct an {ring}-module on {underlying_set}: a scalar multiplication "
                    f"{ring} x A -> A is required, but {scalar_action!r} is not a function"
                )
            assert callable(addition) and callable(negation), (
                f"cannot construct an {ring}-module on {underlying_set}: an addition and a negation are "
                f"required, but got addition {addition!r} and negation {negation!r}"
            )
            self._underlying_set = Set(underlying_set)
            self._addition = addition
            self._negation = negation
            assert self._underlying_set.is_parent_of(zero) is True, (
                f"cannot construct an {ring}-module on {underlying_set}: membership of the zero "
                f"{zero!r} in {underlying_set} is not established"
            )
            self._zero_value = zero
            self._rho = rho
            self._elementwise_scalar_action = scalar_action
            super().__init__(base_ring=ring, **rest)
            self._module_laws_decision = self._verify_module_laws_when_decidable()

        def module_laws_decision(self):
            r"""Return the admission decision for the stated module laws.

            ``True`` means the laws were either supplied by the defining ring
            morphism ``rho : R -> End(A)`` or exhaustively decided on the
            represented finite data.  The proposition
            ``satisfies_module_laws(A)`` means an elementwise operation
            presentation retains the module laws as its defining hypothesis
            because the represented data do not supply an exact decision
            procedure.
            """
            return self._module_laws_decision

        def underlying_set(self):
            r"""Return the set this module is built on."""
            return self._underlying_set

        @cached_method
        def _ring_morphism_defining_module_action(self):
            r"""Return the stated ``rho : R -> End(A)``, or the one the elementwise action defines."""
            match self._rho:
                case None:
                    return super()._ring_morphism_defining_module_action()
                case rho:
                    return rho

        def underlying_additive_group(self):
            match self._rho:
                case None:
                    return self
                case rho:
                    return rho.codomain().domain()

        def _underlying_additive_element(self, element):
            if self.underlying_additive_group() is self:
                return self(element)
            return self(element).underlying_element()

        def _cardinality_decision(self):
            r"""Return the cardinality of the set this module is built on.

            The module adds structure to that set and no elements, so the count
            is the set's and is not computed a second time here.
            """
            return self.underlying_set().cardinality()

        def _finiteness_decision(self):
            r"""Whether the underlying set is placed as finite: ``True``, ``False`` or the proposition ``is_finite``.

            Read from placement rather than from ``cardinality``, which asserts
            where no cardinality of the underlying set is represented.
            """
            from sage_extensions.categories.sets.set_categories import Sets

            underlying = self.underlying_set()
            match underlying:
                case _ if underlying in Sets().Finite():
                    return True
                case _ if underlying in Sets().Infinite():
                    return False
                case _:
                    return AtomicProposition("is_finite", self)

        def _element_constructor_(self, value):
            r"""Read foreign data as an element of the underlying set.

            A value of the underlying set is taken as it is; any other value is
            converted by the underlying set, which rejects what it does not
            contain.
            """
            source = element_parent(value)
            if source is self:
                return value
            if source in Modules(self.base_ring()) and source.unformed_module() is self:
                return source._element_of_unformed_module(value)
            if isinstance(value, self.category().ElementType):
                if value.parent() is self:
                    return value
                value = value.underlying_element()
            return self._element_from_underlying_set(value)

        def _element_from_underlying_set(self, value):
            r"""Construct the module element on a datum of its retained underlying set.

            Protected GeneralModules construction contract (``OWN-05``).
            The element constructor, this owner's arithmetic and iteration,
            and a realization of further structure on this module call it
            with an underlying-set value and receive an element of this
            exact module. Its normalization and element allocation have one
            owner here. Further structure may give coefficient inputs a
            different meaning, so computed additive or scalar-action results
            cannot re-enter through that public input interpretation.
            """
            underlying = self.underlying_set()
            normalized = value if value in underlying else underlying(value)
            assert normalized in underlying, (
                f"{value!r} is not an element of {self}: it is not in the underlying set {underlying}"
            )
            return self.element_class(self, normalized)

        def __call__(self, value):
            r"""Construct an element without Sage coercion discovery.

            The underlying set is an owned set that Sage's coercion graph has
            never heard of, so asking it for a conversion map fails before this
            parent's own constructor is reached.
            """
            return self._element_constructor_(value)

        def __contains__(self, value) -> bool:
            if element_parent(value) is self:
                return True
            if isinstance(value, self.category().ElementType):
                return value.parent() is self
            return value in self.underlying_set()

        def __iter__(self):
            return (self._element_from_underlying_set(value) for value in self.underlying_set())

        def zero(self):
            return self._element_from_underlying_set(self._zero_value)

        def an_element(self):
            r"""The zero element, which every module contains."""
            return self.zero()

        def _add_elements(self, left, right):
            return self._element_from_underlying_set(
                self._addition(
                    self(left).underlying_element(),
                    self(right).underlying_element(),
                )
            )

        def _negate_element(self, element):
            return self._element_from_underlying_set(
                self._negation(self(element).underlying_element())
            )

        def _owned_scalar_multiple(self, scalar, element):
            scalar = self.base_ring()(scalar)
            value = self(element).underlying_element()
            match self._rho:
                case None:
                    return self._element_from_underlying_set(
                        self._elementwise_scalar_action(scalar, value)
                    )
                case rho:
                    return self._element_from_underlying_set(rho(scalar)(value))

        def scalar_action_input(self):
            r"""Return the supplied ``rho`` when the module was given one."""
            assert self._rho is not None, (
                f"{self} has no ring morphism {self.base_ring()} -> End(A): it was constructed from a "
                f"scalar multiplication {self.base_ring()} x A -> A instead"
            )
            return self._rho

        def _represented_annihilator_ideal(self):
            r"""Represent the scalar-action kernel by exhaustive finite enumeration.

            This is a private backend for ``scalar_action().kernel()``.  Outside
            an enumerable finite regime a stronger algebra backend is required.
            """
            assert self.is_finite() is True, (
                f"cannot compute the annihilator of {self}: this algorithm needs a finite underlying set, "
                f"and {self.underlying_set()} is not known to be finite"
            )
            assert self.underlying_set() in EnumeratedSets(), (
                f"cannot compute the annihilator of {self}: finite cardinality alone does not "
                "supply an enumeration of the module elements"
            )
            scalars = _enumerated_ring_elements(self.base_ring())
            assert scalars is not None, (
                f"cannot compute the annihilator of {self}: this algorithm needs a finite scalar ring "
                f"whose elements can be listed, and {self.base_ring()} is not one"
            )
            zero = self.zero()
            annihilating = []
            from sage_extensions.logic import conjunction

            for scalar in scalars:
                equations = (self.scalar_multiple(scalar, element) == zero for element in self)
                decision = conjunction(equations)
                if decision is True:
                    annihilating.append(scalar)
                elif decision is not False:
                    raise ValueError(
                        f"annihilator membership for {scalar} in {self.base_ring()} is undecided; "
                        "finite enumeration does not establish symbolic scalar-action equality"
                    )
            return self.base_ring().ideal(*(annihilating or (self.base_ring().zero(),)))

        def _verify_module_laws_when_decidable(self):
            r"""Check the supplied structure exactly where the check is decidable.

            A supplied ``rho : R -> End(A)`` is the defining module datum, so
            its module laws follow from the ring-morphism and additive-group
            laws already carried by that datum.  For raw operations, a finite
            underlying set decides the additive laws exactly and an enumerable
            finite scalar ring decides the remaining module laws exactly.
            Outside those regimes the decision is the proposition
            ``satisfies_module_laws(A)`` rather than a silent promotion to a
            theorem.
            """
            if self._rho is not None:
                return True
            undecided = AtomicProposition("satisfies_module_laws", self)
            if self.underlying_set() not in FiniteSets():
                _LOGGER.debug(
                    "General module over %s retains its module laws as an undecided proposition",
                    self.base_ring(),
                )
                return undecided
            if self.underlying_set() not in EnumeratedSets():
                _LOGGER.debug(
                    "Finite general module over %s retains its module laws as an undecided proposition; its underlying set has no selected enumeration",
                    self.base_ring(),
                )
                return undecided
            elements = tuple(self)

            zero = self.zero()
            for element in elements:
                assert (element + zero == element) is True and (zero + element == element) is True, (
                    f"{self} is not a module: the given zero {zero} is not an additive identity, "
                    f"since {element} + {zero} != {element}"
                )
                assert (element + (-element) == zero) is True, (
                    f"{self} is not a module: the given negation does not give additive inverses, "
                    f"since {element} + ({-element}) != {zero}"
                )
            for left in elements:
                for right in elements:
                    assert (left + right == right + left) is True, (
                        f"{self} is not a module: its addition is not commutative, "
                        f"since {left} + {right} != {right} + {left}"
                    )
                    for third in elements:
                        assert ((left + right) + third == left + (right + third)) is True, (
                            f"{self} is not a module: its addition is not associative on "
                            f"{left}, {right}, {third}"
                        )

            scalars = _enumerated_ring_elements(self.base_ring())
            if scalars is None:
                _LOGGER.debug(
                    "Additive group laws for the finite set %s were exhaustively checked, but "
                    "scalar-module laws over non-enumerated %s remain an undecided proposition",
                    self.underlying_set(),
                    self.base_ring(),
                )
                return undecided

            one = self.base_ring().one()
            zero_scalar = self.base_ring().zero()
            for element in elements:
                assert (self.scalar_multiple(one, element) == element) is True, (
                    f"{self} is not a module: 1 in {self.base_ring()} does not act as the identity, "
                    f"since 1 * {element} != {element}"
                )
                assert (self.scalar_multiple(zero_scalar, element) == zero) is True, (
                    f"{self} is not a module: 0 in {self.base_ring()} does not act as zero, "
                    f"since 0 * {element} != {zero}"
                )
                for scalar in scalars:
                    for other in elements:
                        assert (self.scalar_multiple(scalar, element + other) == (
                            self.scalar_multiple(scalar, element)
                            + self.scalar_multiple(scalar, other)
                        )) is True, (
                            f"{self} is not a module: scalar multiplication by {scalar} is not additive, "
                            f"since {scalar} * ({element} + {other}) != {scalar} * {element} + {scalar} * {other}"
                        )
                    for second_scalar in scalars:
                        assert (self.scalar_multiple(scalar + second_scalar, element) == (
                            self.scalar_multiple(scalar, element)
                            + self.scalar_multiple(second_scalar, element)
                        )) is True, (
                            f"{self} is not a module: ({scalar} + {second_scalar}) * {element} != "
                            f"{scalar} * {element} + {second_scalar} * {element}"
                        )
                        assert (self.scalar_multiple(
                            scalar * second_scalar, element
                        ) == self.scalar_multiple(
                            scalar, self.scalar_multiple(second_scalar, element)
                        )) is True, (
                            f"{self} is not a module: ({scalar} * {second_scalar}) * {element} != "
                            f"{scalar} * ({second_scalar} * {element})"
                        )
            return True

        def _repr_(self):
            return f"Module over {self.base_ring()} on {self.underlying_set()}"


class _PointwiseValues:
    r"""The map ``a |-> operation(B, f_1(a), ..., f_k(a))`` built by one pointwise module operation.

    Defining function of a map of ``B^A`` assembled by the pointwise law
    (``_pointwise_module_operations``): the sum, negative, scalar multiple
    or zero of maps already in ``B^A``.  Protected contract (``OWN-05``):
    owner, this module's function-module construction, which alone builds
    it; ``operation()`` and ``operands()`` are read by one consumer, the
    formula adapter of ``categories/functions/real_functions.py``, which
    recovers a symbolic formula of the assembled map from the formulas of
    its operands.  The operands are maps of ``Sets().Mor(A, B)``.
    """

    def __init__(self, codomain, operation, operands) -> None:
        self._codomain = codomain
        self._operation = operation
        self._operands = operands

    def operation(self):
        return self._operation

    def operands(self):
        return self._operands

    def __call__(self, point):
        return self._operation(self._codomain, *(operand(point) for operand in self._operands))


class _FunctionModuleElement:
    r"""A map ``A -> B``, as an element of the module ``B^A`` of all such maps."""

    def __call__(self, point):
        r"""The value at ``point``: the element is the map of ``Sets().Mor(A, B)`` it is built on."""
        return self.underlying_element()(point)


class _FunctionModule:
    r"""Private computation class (``OWN-06``) of ``B.function_module(A)``.

    An object of ``GeneralModules(R)`` whose underlying set is
    ``Sets().Mor(A, B)`` and whose operations are the pointwise law; the
    datum this class adds is the codomain module ``B``, whose operations
    the law reads.  ``_function_module`` is the construction route.
    """

    def __init__(self, function_module_codomain, **rest) -> None:
        self._function_module_codomain = function_module_codomain
        super().__init__(**rest)

    def _element_from_underlying_set(self, value):
        r"""An element of this module is already one; any other value is read by ``Sets().Mor(A, B)``."""
        if element_parent(value) is self:
            return value
        return super()._element_from_underlying_set(value)

    def domain(self):
        r"""The set ``A`` the maps start at."""
        return self.underlying_set().domain()

    def codomain(self):
        r"""The module ``B`` the maps take values in."""
        return self._function_module_codomain

    def _repr_(self):
        return f"Module over {self.base_ring()} of maps {self.domain()} -> {self.codomain()}"


@cached_function(key=lambda module, domain: (id(module), id(domain)))
def _function_module(module, domain):
    r"""Construct ``B^A`` on ``Sets().Mor(A, B)``; the route of ``Modules.ParentMethods.function_module``."""
    from sage_extensions.categories.modules.pure.modules import (
        _pointwise_module_operations,
    )
    from sage_extensions.categories.sets.set_categories import Sets

    ring = _owned_ring(module.base_ring())
    assert domain in Sets(), (
        f"the maps into {module} start at a set, but {domain} is not in the category of sets"
    )
    maps = Sets().Mor(domain, module)

    def combine(operation, operands):
        return maps(_PointwiseValues(module, operation, operands))

    category = GeneralModules(ring)
    return _object_of(
        category,
        _engine=(category, _FunctionModule, _FunctionModuleElement),
        base_ring=ring,
        underlying_set=maps,
        function_module_codomain=module,
        **_pointwise_module_operations(combine),
    )


class _ConditionSubmoduleElement:
    r"""An element of ``{x in M : P(x)}``: a point of ``M``, admitted by the construction's hypothesis."""

    @validator
    def validate_condition_membership(self) -> None:
        r"""Raise ``ValueError`` unless ``P(x)`` holds for this element ``x`` (``OWN-22``).

        Construction does not ask ``P``; this validator does, when called by
        hand, with ``check=True`` at the element constructor, or under
        strict checking.
        """
        submodule = self.parent()
        point = self.underlying_element()
        decision = submodule.condition_predicate()(point)
        # The module the condition is stated on is the codomain of the
        # submodule's inclusion; a structured object on the submodule's data
        # reaches the submodule as its unformed module.
        module = submodule.unformed_module().inclusion().codomain()
        if decision is False:
            raise ValueError(
                f"{point} is not in {submodule}: it fails the condition {submodule.condition_predicate()} "
                f"that cuts the submodule out of {module}"
            )
        assert decision is True, (
            f"cannot decide whether {point} satisfies the condition {submodule.condition_predicate()} "
            f"cutting {submodule} out of {module}: the condition answers {decision}"
        )


class _ConditionSubmodule:
    r"""Private computation class (``OWN-06``) of ``M.condition_submodule(P)``.

    The datum is the module ``M``, the predicate ``P`` on its elements, and
    the condition set ``{x in M : P(x)}`` (``Sets().condition_set``), which
    is the underlying set; the operations are ``M``'s, and closure of the
    condition set under them is the construction's hypothesis.  An element
    holds its point of ``M``.  The structured objects built on these data
    (an algebra or a form on the submodule, through
    ``_module_with_structure``) are realized by the same class, so their
    elements are admitted the same way.  ``_condition_submodule`` and
    ``_condition_submodule_object`` are the construction routes.
    """

    def __init__(
        self,
        condition_module,
        condition_predicate,
        condition_categories,
        condition_engine,
        condition_engine_data,
        **rest,
    ) -> None:
        self._condition_module = condition_module
        self._condition_engine_data = condition_engine_data
        self._condition_predicate = condition_predicate
        self._condition_categories = condition_categories
        self._condition_engine = condition_engine
        super().__init__(**rest)

    def condition_predicate(self):
        r"""The predicate ``P`` with ``self = {x in M : P(x)}``."""
        return self._condition_predicate

    def _element_from_underlying_set(self, value):
        r"""Construct the element on a point of ``M``, without asking ``P``.

        Realizes the protected ``GeneralModules`` construction contract for
        a condition submodule.  Its callers are the element constructor and
        this module's arithmetic: a sum or a scalar multiple of elements is
        an element by the closure hypothesis, and an element supplied by the
        caller is admitted by the caller's claim, checked by
        ``validate_condition_membership`` when that is asked (``OWN-22``).
        """
        return self.element_class(self, self._condition_module(value))

    def _element_constructor_(self, value):
        element = super()._element_constructor_(value)
        element.validate_condition_membership(check=False)
        return element

    def __contains__(self, value) -> bool:
        r"""Whether ``value`` lies in this submodule; a point of ``M`` is asked ``P``.

        The argument is arbitrary.  An element of this submodule is in it;
        a point of ``M``, or a value ``M`` contains, is read in ``M`` and
        asked ``P``; nothing else is in it.
        """
        if element_parent(value) is self:
            return True
        if element_parent(value) is not self._condition_module:
            if value not in self._condition_module:
                return False
            value = self._condition_module(value)
        return self.underlying_set().is_parent_of(value)

    def _module_with_structure(self, categories, construction_data):
        r"""Build further structure (an algebra, a form) on the data of this submodule.

        The structured object is realized by the same class on the same
        module ``M``, predicate and condition set, so its elements are
        the points of ``M`` that this submodule's are.  It is not itself a
        subobject: its ``unformed_module()`` is this submodule, which carries
        the inclusion.
        """
        return _condition_submodule_object(
            self._condition_module,
            self._condition_predicate,
            self.underlying_set(),
            engine=self._condition_engine,
            engine_data=self._condition_engine_data,
            categories=(*self._condition_categories, *categories),
            construction_data=construction_data,
            subobject=False,
        )

    def _repr_(self):
        return f"Submodule of {self._condition_module} cut out by {self._condition_predicate}"


def _condition_submodule_object(
    module,
    predicate,
    points,
    *,
    engine,
    engine_data=None,
    categories=(),
    construction_data=None,
    subobject=True,
):
    r"""Construct a condition submodule, or a structured object on its data.

    ``points`` is the condition set of ``predicate`` in ``module``;
    ``engine`` is the pair of computation classes realizing the objects and
    elements (this module's, or a specialization of them such as a function
    space), and ``engine_data`` the data those classes add (a regularity,
    an exponent), kept as one dictionary so a structured object built on the
    same data receives them again; ``categories`` are the further placements the caller established.
    With ``subobject`` the object is placed in ``ModuleSubobjects`` with the
    inclusion of ``points``; a structured object on its data is not.
    """
    from sage_extensions.categories.abstract_categories.cat import Cat
    from sage_extensions.categories.modules.pure.modules import ModuleSubobjects

    ring = module.base_ring()
    general = GeneralModules(ring)
    placement = [general, *categories]
    data = {
        "base_ring": ring,
        "underlying_set": points,
        "addition": operator.add,
        "zero": module.zero(),
        "negation": operator.neg,
        "scalar_action": lambda scalar, value: module.scalar_multiple(scalar, value),
        "condition_module": module,
        "condition_predicate": predicate,
        "condition_categories": tuple(categories),
        "condition_engine": engine,
        "condition_engine_data": dict(engine_data or {}),
    }
    if subobject:
        placement.append(ModuleSubobjects(ring))
        data["subobject_inclusion_factory"] = lambda submodule: submodule.Mono(module)._from_constructed_embedding(
            lambda element: module(submodule(element).underlying_element())
        )
    object_engine, element_engine = engine
    return _object_of(
        Cat().meet(tuple(placement)),
        _engine=(general, object_engine, element_engine),
        _ambient=Cat().meet((general, *categories)) if subobject else None,
        **data,
        **(construction_data or {}),
    )


def _condition_submodule(module, predicate, *, engine=None, engine_data=None, categories=()):
    r"""Construct ``M.condition_submodule(P)``; the route of ``Modules.ParentMethods.condition_submodule``.

    Zero satisfies the condition by the submodule hypothesis, so the zero
    of ``M`` is admitted to the condition set without asking ``P`` on it.
    """
    zero = module.zero()

    def condition(point):
        if (point == zero) is True:
            return True
        return predicate(point)

    return _condition_submodule_object(
        module,
        predicate,
        module.condition_set(condition),
        engine=engine or (_ConditionSubmodule, _ConditionSubmoduleElement),
        engine_data=engine_data,
        categories=categories,
    )


__all__ = [
    "GeneralModules",
]
